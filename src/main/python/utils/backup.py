#
# Copyright (c) 2020 The Board of Trustees of The Leland Stanford Junior University.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#
import array as arr
import gzip
import io
import json
import logging
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from datetime import timezone
from urllib import parse
import argparse
from pathlib import Path

import requests
from google.cloud import bigquery
from google.cloud import storage
from google.cloud.storage import Client
from google.cloud.exceptions import GoogleCloudError
from google.cloud.exceptions import NotFound
from google.cloud.storage.blob import Blob
from google.oauth2 import service_account
from google.cloud.exceptions import NotFound, Conflict
import uuid

"""
BigQuery backup / restore utility
"""

logger = logging.getLogger(__name__)


class Table:
    """
    Helper class for manipulating Tables
    """

    def __init__(self, client: bigquery.Client, table=None):
        # If a restored table was provided, remove the etag, id and selfLinks
        if type(table) is dict:
            self.scrub(table)
            self.table = bigquery.Table.from_api_repr(table)

        if type(table) is bigquery.TableReference:
            self.table = bigquery.Table(table)

        self.client = client

    def scrub(self, d: dict):
        """Removes the identity keys from a dataset created from a restored API representation"""
        for k, v in d.copy().items():
            if isinstance(v, dict):
                self.scrub(v)
            else:
                if k == "etag" or k == "selfLink" or k == "id" or k == "__len__":
                    d.pop(k, None)

    def get(self):
        """Retrieves table from BigQuery"""
        self.table = self.client.get_table(self.table)

    def create(self, drop=False):
        """Creates table in BigQuery, dropping it if it already exists (option)"""
        try:
            if self.table.table_type == "VIEW":
                self.table.schema = None
            self.table = self.client.create_table(table=self.table, exists_ok=False)
        except Conflict as ex:
            if drop:
                self.client.delete_table(self.table)
                logger.warning("Dropped %s %s:%s.%s", self.table.table_type, self.table.project,
                               self.table.dataset_id,
                               self.table.table_id)
                self.table = self.client.create_table(table=self.table, exists_ok=False)
            else:
                logger.error("%s %s:%s.%s already exists, use --drop-table to overwrite existing tables",
                             self.table.project, self.table.dataset_id, self.table.table_id,
                             self.table.full_table_id)
                raise ex
        logger.info("Created %s %s", self.table.table_type, self.table.full_table_id)

    def load(self, extract_job: dict, drop=False):
        """Loads a table resulted from a BigQuery extract job, using datetime conversion if needed
        :param extract_job: BigQuery extract job to use for loading information
        :param drop: Drop table if it exists
        """

        self.create(drop)

        # Check if this table needs string to datetime conversion fixes, if so load into a temporary staging table
        if extract_job['configuration']['extract']['destinationFormat'] == "AVRO" \
                and any(field.field_type == "DATETIME" for field in self.table.schema):
            load_table = bigquery.Table.from_string(
                "{}.{}.{}_{}".format(self.table.project, self.table.dataset_id, self.table.table_id,
                                     uuid.uuid4().hex[0:6]))
        else:
            load_table = self.table

        logger.debug("%s %s:%s.%s", "Staging" if load_table is not self.table else "Loading",
                     load_table.project, load_table.dataset_id, load_table.table_id)

        job_config = bigquery.job.LoadJobConfig()
        job_config.source_format = extract_job['configuration']['extract']['destinationFormat']
        if 'useAvroLogicalTypes' in extract_job['configuration']['extract']:
            job_config.use_avro_logical_types = extract_job['configuration']['extract']['useAvroLogicalTypes']
        if job_config.source_format == "CSV" and extract_job['configuration']['extract'].get('printHeader'):
            job_config.skip_leading_rows = 1
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
        self.client.load_table_from_uri(
            source_uris=extract_job['configuration']['extract']['destinationUris'],
            destination=load_table,
            location=load_table.location,
            job_config=job_config
        ).result()

        # If the table was loaded into a staging table, use SQL query to cast STRINGS back to DATETIME
        if load_table is not self.table:

            logger.debug("Casting %s:%s.%s to %s:%s.%s",
                         load_table.project, load_table.dataset_id, load_table.table_id,
                         self.table.project, self.table.dataset_id, self.table.table_id
                         )

            # Cast STRING datetime fields in staging table to DATETIME fields in destination table
            query_job_config = bigquery.job.QueryJobConfig()
            query_job_config.destination = self.table
            query_job_config.use_legacy_sql = False
            query_job_config.use_query_cache = False

            # Do NOT use truncate here, or the table will lose schema constraints!
            query_job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

            columns = []
            for field in self.table.schema:
                if field.field_type == "DATETIME":
                    columns.append("CAST({} AS DATETIME) AS {}".format(field.name, field.name))
                else:
                    columns.append(field.name)
            query = "SELECT {} FROM `{}.{}`.{}".format(",".join(columns), load_table.project, load_table.dataset_id,
                                                       load_table.table_id)
            logger.debug(query)
            self.client.query(query=query, job_config=query_job_config).result()

            logger.debug("Deleting staging table %s:%s.%s", load_table.project, load_table.dataset_id,
                         load_table.table_id)
            self.client.delete_table(load_table)

        logger.info("Loaded %s", self.table.full_table_id)

    def extract_metadata(self):
        """Convenience function that returns a table and a None job definition"""
        self.get()
        return self.table, None

    def extract(self, destination_uri, compression, dest_format, print_header, merge_csv):
        """Extract a BigQuery table to a GCS storage bucket path """
        if not self.table.full_table_id:
            self.get()

        if self.table.table_type == "VIEW" or not self.table.schema:
            return self.table, None

        job_config = bigquery.job.ExtractJobConfig()

        split_required = self.table.num_bytes > 1000000000

        if dest_format == bigquery.DestinationFormat.CSV:
            if print_header:
                if split_required and merge_csv:
                    # If the output is going to be split into multiple files, and they are to be merged, disable headers
                    job_config.print_header = False
                else:
                    job_config.print_header = True
            else:
                job_config.print_header = False

        job_config.compression = compression
        if dest_format == bigquery.DestinationFormat.AVRO:
            job_config.use_avro_logical_types = True
        job_config.destination_format = dest_format

        final_uri = "{}/{}.{}.{}{}".format(destination_uri,
                                           self.table.project, self.table.dataset_id, self.table.table_id,
                                           "-*" if split_required else "")

        if dest_format == bigquery.DestinationFormat.AVRO:
            final_uri += ".avro"
        if dest_format == bigquery.DestinationFormat.CSV:
            final_uri += ".csv"
        if dest_format == bigquery.DestinationFormat.NEWLINE_DELIMITED_JSON:
            final_uri += ".json"
        if compression == bigquery.Compression.GZIP:
            final_uri += ".gz"

        logger.info("Extracting %s to %s", self.table.full_table_id, final_uri)

        return self.table, self.client.extract_table(source=self.table, destination_uris=final_uri,
                                                     location=self.table.location,
                                                     job_config=job_config).result()

    def delete(self):
        self.client.delete_table(table=self.table)


class Dataset:

    def __init__(self, client: bigquery.Client, dataset: dict = None):
        self.client = client

        # If a restored dataset was provided, remove the etag, id and selfLinks
        if dataset is not None:
            self.scrub(dataset)
            self.dataset = bigquery.Dataset.from_api_repr(dataset)

    def scrub(self, d: dict):
        """Removes the identity keys from a dataset created from a restored API representation"""
        for k, v in d.copy().items():
            if isinstance(v, dict):
                self.scrub(v)
            else:
                if k == "etag" or k == "selfLink" or k == "id" or k == "__len__":
                    d.pop(k, None)

    def get(self, project, dataset_id):
        self.dataset = self.client.get_dataset(bigquery.DatasetReference(project, dataset_id))

    def create(self, drop=False):
        try:
            existing = self.client.get_dataset(self.dataset)
            if not drop:
                # Update mandatory fields
                logger.warning("Dataset %s already exists, metadata will not be updated", existing.dataset_id)
                self.client.update_dataset(self.dataset,
                                           fields=["default_table_expiration_ms", "default_table_expiration_ms"])
            else:
                logger.warning("Deleting dataset %s and all contents", existing.dataset_id)
                self.client.delete_dataset(self.dataset, delete_contents=True)
                self.client.create_dataset(dataset=self.dataset, exists_ok=False)
        except NotFound:
            self.client.create_dataset(dataset=self.dataset, exists_ok=False)
            logger.info("Created dataset %s", self.dataset.dataset_id)

    def delete(self):
        self.client.delete_dataset(self.dataset, delete_contents=True)


class BackupException(Exception):
    """Exceptions raised by this class"""


def backup(credentials, quota_project, dataset_expr, backup_uri, compression=bigquery.Compression.SNAPPY,
           destination_format=bigquery.DestinationFormat.AVRO, threads=25, print_header=False,
           metadata_only=False, merge_csv=False) -> str:
    project, dataset_id, table_expr = __parse_dataset_expr(dataset_expr)

    # Defaults from None
    if compression is None:
        compression = bigquery.Compression.SNAPPY
    if destination_format is None:
        destination_format = bigquery.DestinationFormat.AVRO

    # Default pool size is too small so we create a custom HTTP adapter with a bigger pool
    bq_client = bigquery.Client(project=quota_project, credentials=credentials)
    adapter = requests.adapters.HTTPAdapter(pool_connections=128, pool_maxsize=128, max_retries=5)
    bq_client._http.mount("https://", adapter)
    bq_client._http._auth_request.session.mount("https://", adapter)

    gcs_client = Client(project=quota_project, credentials=credentials)

    # Backup
    dataset = Dataset(bq_client)
    dataset.get(project, dataset_id)
    start_time = datetime.now(timezone.utc)
    archive = {
        'dataset': dataset.dataset.to_api_repr()
    }
    try:
        archive['tables'] = __extract_dataset(bq_client, dataset.dataset, backup_uri, table_expr, compression,
                                              destination_format, print_header, merge_csv, metadata_only,
                                              threads)

        # If the final output is to be merged CSV, enumerate all of the jobs that resulted in multiple output files
        if merge_csv:
            for table_job in archive['tables']:
                if "job" in table_job:
                    dest_uri = table_job['job']['configuration']['extract']['destinationUri']
                    if "-*" in dest_uri:
                        fields = [field['name'] for field in
                                  table_job['table']['schema']['fields']] if print_header else None
                        bucket_name = parse.urlparse(dest_uri).netloc
                        prefix = parse.urlparse(dest_uri).path[1:].partition("*")[0]
                        merged = __merge_csv(gcs_client, bucket_name, prefix, fields)
                        merged_uri = "gs://{}/{}".format(merged.bucket.name, merged.name)
                        table_job.update({
                            'merge': {
                                'destinationUri': merged_uri
                            }
                        })
                        logger.info("Merged %s to %s", dest_uri, merged_uri)

        complete_time = datetime.now(timezone.utc)
        archive['start_date'] = start_time.isoformat(timespec='seconds')
        archive['finish_date'] = complete_time.isoformat(timespec='seconds')
        archive['seconds_elapsed'] = (complete_time - start_time).seconds

        table_bytes = 0
        for table in archive['tables']:
            table_bytes += int(table['table']['numBytes'])
        archive['table_bytes'] = table_bytes

        if not metadata_only:
            gcs_bytes = 0
            for table in archive['tables']:
                if 'job' not in table:
                    continue
                job_uri = table['job']['configuration']['extract']['destinationUri']
                blobs = gcs_client.list_blobs(bucket_or_name=parse.urlparse(job_uri).hostname,
                                              prefix=parse.urlparse(job_uri).path[1:].partition("*")[0])
                for blob in blobs:
                    gcs_bytes += blob.size
            archive['gcs_bytes'] = gcs_bytes
            if table_bytes > 0 and gcs_bytes > 0:
                archive['compression_ratio'] = round(table_bytes / gcs_bytes, 2)

        if not backup_uri.endswith(".json") and not backup_uri.endswith(".json.gz"):
            # Create backup URI in format gs://backup_uri/project.dataset_id.json
            uri = "{}{}.{}.json".format(backup_uri, dataset.dataset.project, dataset.dataset.dataset_id)
        else:
            # Otherwise use URI exactly as provided
            uri = backup_uri
        if uri.endswith(".gz"):
            Blob.from_string(uri, gcs_client).upload_from_string(__gzip_str(json.dumps(archive, indent=2)))
        else:
            Blob.from_string(uri, gcs_client).upload_from_string(json.dumps(archive, indent=2))
        logger.info("Backup complete, wrote %s %s", uri, "(metadata only)" if metadata_only else "")
        return json.dumps({
            "dataset": dataset.dataset.to_api_repr()['datasetReference'],
            "backup_uri": uri
        })
    except GoogleCloudError as error:
        logger.error(error.message)
        raise BackupException
    except TimeoutError:
        logger.error("Connection timeout error!")
        raise BackupException


def __parse_dataset_expr(dataset_expr):
    pattern = '^(.*?):(.*?)(?:\\.(.*))?$'
    search = re.search(pattern, dataset_expr)
    project = search.group(1)
    dataset_id = search.group(2)
    table_re = search.group(3)
    if table_re is None:
        table_re = ".*"
    return project, dataset_id, table_re


def __merge_csv(client: Client, bucket_name: str, prefix: str, fields = None) -> storage.blob:
    if fields is None:
        fields = []

    bucket = client.get_bucket(bucket_name)
    segments = list(client.list_blobs(bucket, prefix=prefix))

    # Create header file
    header_file = None
    blobs = []
    if fields:
        header_file = Blob(prefix + "header.csv", bucket)
        header_file.upload_from_string(",".join(fields) + "\n")
        blobs.append(header_file)
    blobs.extend(segments)

    # Merge using object composition
    destination = bucket.blob(prefix[:-1] + ".csv")
    destination.content_type = "text/plain"
    if len(blobs) <= 32:
        destination.compose(blobs)
        # Delete the temporary header file
        if header_file:
            header_file.delete()
        return destination
    else:
        # Requires iterative composition
        compositions = []
        windex = 0
        for i, b in enumerate(blobs):
            if i != 0 and i % 32 == 0:
                next_blob = Blob("{}-tmp-{:02d}-{:02d}.csv".format(prefix[:-1], windex, i - 1), bucket)
                next_blob.content_type = "text/plain"
                next_blob.compose(blobs[windex:i])
                compositions.append(next_blob)
                logger.debug("Composed from %s-%s -> %s", windex, i - 1, next_blob.name)
                windex = i
        if windex < len(blobs):
            next_blob = Blob("{}-tmp-{:02d}-{:02d}.csv".format(prefix[:-1], windex, len(blobs)), bucket)
            next_blob.content_type = "text/plain"
            next_blob.compose(blobs[windex:len(blobs)])
            compositions.append(next_blob)
            logger.debug("Composed from %s-%s -> %s (final)", windex, len(blobs), next_blob.name)
        # Create aggregate composition
        destination.compose(compositions)
        # Delete intermediate compositions
        for blob in compositions:
            blob.delete()
        # Delete the temporary header file
        if header_file:
            header_file.delete()
        return destination


def restore(credentials, quota_project, dataset_expr, backup_uri, threads, keep_expiration=False, metadata_only=False,
            drop_dataset=False, drop_tables=False, default_table_expiration=None,
            default_partition_expiration=None) -> str:
    # Get the destination (new) dataset project, dataset_id, table regex
    project, dataset_id, table_expr = __parse_dataset_expr(dataset_expr)

    # Default pool size is too small so we create a custom HTTP adapter with a bigger pool
    bq_client = bigquery.Client(project=quota_project, credentials=credentials)
    adapter = requests.adapters.HTTPAdapter(pool_connections=128, pool_maxsize=128, max_retries=5)
    bq_client._http.mount("https://", adapter)
    bq_client._http._auth_request.session.mount("https://", adapter)

    gcs_client = Client(project=quota_project, credentials=credentials)

    start_time = datetime.now(timezone.utc)
    try:
        if str(backup_uri).endswith(".gz"):
            archive = json.loads(
                gzip.decompress(Blob.from_string(backup_uri, gcs_client).download_as_bytes()))
        else:
            archive = json.loads(Blob.from_string(str(backup_uri), gcs_client).download_as_text())
    except NotFound:
        logger.error("Could not find %s!", backup_uri)
        raise BackupException

        # Replace the project and dataset in the backup with our new destination project and dataset
    source_project = archive['dataset']['datasetReference']['projectId']
    source_dataset = archive['dataset']['datasetReference']['datasetId']
    archive['dataset']['datasetReference']['projectId'] = project
    archive['dataset']['datasetReference']['datasetId'] = dataset_id
    if default_table_expiration is not None:
        archive['dataset']['defaultTableExpirationMs'] = str(default_table_expiration)
    if default_partition_expiration is not None:
        archive['dataset']['defaultPartitionExpirationMs'] = str(default_partition_expiration)

    logger.info("Restoring backup of %s:%s to %s:%s for all tables matching %s %s", source_project, source_dataset,
                project, dataset_id, table_expr, "(metadata only)" if metadata_only else "")

    dataset = Dataset(bq_client, archive['dataset'])
    try:
        dataset.create(drop=drop_dataset)
        __load_dataset(bq_client, dataset, archive['tables'], table_expr, keep_expiration, metadata_only, threads,
                       drop_tables)
    except GoogleCloudError as ex:
        logger.error("Error during restore: %s", ex.message)
        raise BackupException
    except TimeoutError:
        logger.error("Connection timeout error!")
        raise BackupException

    complete_time = datetime.now(timezone.utc)

    logger.info("Restore of dataset %s%s:%s completed in %s seconds", "metadata " if metadata_only else "",
                dataset.dataset.project, dataset.dataset.dataset_id, (complete_time - start_time).seconds)

    return json.dumps(dataset.dataset.to_api_repr()['datasetReference'])


def __load_dataset(client: bigquery.Client, dataset, tables: dict, table_expr: str,
                   keep_expiration, metadata_only, threads, drop_tables):
    futures = []
    with ThreadPoolExecutor(max_workers=threads, thread_name_prefix="LoadJob") as executor:
        # Submit jobs to load in parallel
        for table in tables:
            # Replace project and dataset in backup with new destination project and dataset
            table['table']['tableReference']['projectId'] = dataset.dataset.project
            table['table']['tableReference']['datasetId'] = dataset.dataset.dataset_id
            if 'expirationTime' in table['table'] and (not keep_expiration or
                                                       int(table['table']['expirationTime']) >=
                                                       datetime.now(timezone.utc).microsecond * 1000):
                del table['table']['expirationTime']

            dest_table = Table(client, table['table'])
            try:
                # Only restore tables that match the given regex
                if re.match("^" + table_expr + "$", dest_table.table.table_id, re.IGNORECASE):
                    if metadata_only or 'job' not in table:
                        futures.append(executor.submit(dest_table.create, drop_tables))
                    else:
                        futures.append(executor.submit(dest_table.load, table['job'], drop_tables))
                else:
                    logger.info("Skipping %s %s, it does not match pattern %s", dest_table.table.table_type,
                                dest_table.table.table_id, table_expr)
            except re.error as ex:
                logger.error("Table regular expression parsing error: %s at position %s of \"%s\"", ex.msg, ex.pos,
                             ex.pattern)
                raise BackupException

    for future in as_completed(futures):
        future.result()


def __extract_dataset(client: bigquery.Client, dataset: bigquery.Dataset, backup_uri, table_expr: str, compression,
                      destination_format, print_header, merge_csv, metadata_only, threads):
    tables = []
    futures = []
    with ThreadPoolExecutor(max_workers=threads, thread_name_prefix="ExtractJob") as executor:
        # Submit extract jobs in parallel
        for item in client.list_tables(dataset):
            table_ref = item.reference
            if re.match('^' + table_expr + "$", table_ref.table_id, re.IGNORECASE):
                table = Table(client, table_ref)
                if metadata_only:
                    futures.append(executor.submit(table.extract_metadata))
                else:
                    futures.append(
                        executor.submit(table.extract, os.path.dirname(backup_uri), compression, destination_format,
                                        print_header, merge_csv))
            else:
                logger.info("Skipping %s, it does not match pattern %s", table_ref.table_id, table_expr)

        for future in as_completed(futures):
            table, job = future.result()
            if job is not None:
                if job.error_result is not None:
                    logger.error("Failed to extract %:%s.%s: %s", job.source.project, job.source.dataset_id,
                                 job.source.table_id, job.error_result)
                else:
                    logger.debug("Extracted %s:%s.%s", job.source.project, job.source.dataset_id, job.source.table_id)
                tables.append({"table": table.to_api_repr(), "job": job.to_api_repr()})
            else:
                tables.append({"table": table.to_api_repr()})
    return tables


def __gzip_str(string_: str) -> bytes:
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode='w') as fo:
        fo.write(string_.encode())
    return out.getvalue()

def header_file(credentials, quota_project, dataset_id: str, backup_uri):
    client = bigquery.Client()
    # dataset_id = 'your-project.your_dataset'
    # table_id = 'your-project.your_dataset.your_table'

    tables = client.list_tables(dataset_id)  

    for table in tables:
        tableOb = client.get_table("{}.{}.{}".format(table.project, table.dataset_id, table.table_id))
        result = ["{}".format(schema.name) for schema in tableOb.schema]
       
        fileName = '{}.{}.{}_header.csv'.format(quota_project, table.dataset_id, table.table_id)
        csvfile = open(fileName,'w')
        csvfile.write(','.join(result)) 
        csvfile.close()

        sClient = storage.Client(credentials=credentials, project=quota_project)

        uri = str(backup_uri)+fileName
        bucketName = uri.split("/")[2]
        objectName = "/".join(uri.split("/")[3:])

        bucket = sClient.get_bucket(bucketName)
        blob = bucket.blob(objectName)
        blob.upload_from_filename(fileName)



def main():
    parser = argparse.ArgumentParser(description="GCP Dataset Backup/Restore Utility")
    parser.add_argument("--project_id", required=False, help="Your Google Cloud project ID.")
    parser.add_argument('--credentials', required=False, help='Specify path to a GCP JSON credentials file')
    parser.add_argument('command', choices=['backup', 'restore', 'header_file'], type=str.lower, help='command to execute')
    parser.add_argument('config', help='JSON configuration file for command')
    
    args = parser.parse_args()
    config = Path(args.config).read_text()

    if args.credentials is not None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credentials

    if args.project_id is not None:
        os.environ['GCLOUD_PROJECT'] = args.project_id
    
    json_options = json.loads(config)    
    
    if json_options["logLevel"] != "NONE":
        logging.basicConfig(format='%(asctime)s %(threadName)-13s %(levelname)-8s %(message)s', level=json_options["logLevel"])
    logger = logging.getLogger(__name__)

    _credentials = None
    if args.credentials is not None:
        _credentials = service_account.Credentials.from_service_account_file(
            args.credentials, scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

    try:
        datasetExpr = "{}:{}".format(json_options["quotaProject"],json_options["datasetName"])

        if args.command == "backup" and args.config is not None:
            if not json_options["backupUri"].endswith('/'):
                json_options["backupUri"] += "/", 
            result = backup(credentials=_credentials, quota_project=json_options["quotaProject"],
                                dataset_expr=datasetExpr, backup_uri=json_options["backupUri"], threads=json_options["threads"],
                                compression=json_options["compression"], destination_format=json_options["destinationFormat"],
                                print_header=json_options["printHeader"], metadata_only=json_options["metadataOnly"],
                                merge_csv=json_options["mergeCsv"])
            if json_options["json"]:
                print(result)
            sys.exit(0)

        elif args.command == "restore" and args.config is not None:
            result = restore(credentials=_credentials, quota_project=json_options["quotaProject"],
                                dataset_expr=datasetExpr, backup_uri=json_options["backupRestoreJsonUri"], threads=json_options["threads"],
                                keep_expiration=json_options["keepExpiration"], metadata_only=json_options["metadataOnly"],
                                drop_dataset=json_options["dropDataset"], drop_tables=json_options["dropTables"],
                                default_table_expiration=json_options["defaultTableExpiration"],
                                default_partition_expiration=json_options["defaultPartitionExpiration"])
            if json_options["json"]:
                print(result)
            sys.exit(0)

        elif args.command == "header_file" and args.config is not None:
            header_file(credentials=_credentials, quota_project=json_options["quotaProject"],
                            dataset_id = "{}.{}".format(json_options["quotaProject"], json_options["datasetName"]), backup_uri=json_options["backupUri"])

    except BackupException:
        logger.error("Backup or restore failed, exiting.")

        # Trouble if we got this far
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
