import argparse
import json
import os
import sys
from pandas import DataFrame
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from dataclasses_json import dataclass_json
from google.cloud import bigquery, exceptions
from google.cloud.bigquery import DEFAULT_RETRY


@dataclass_json
@dataclass
class CreateTableConfig():
    # https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets#resource-dataset
    table: dict
    # If dataset already exists, drop it (including contents)
    drop: bool = False
    # If table already exists, don't return an error
    existsOk: bool = True


def create_table(config: CreateTableConfig):
    """
    Creates a table -> table.json
    """
    client = bigquery.Client()
    table = bigquery.Table.from_api_repr(config.table)
    if config.drop:
        client.delete_table(table, not_found_ok=True)
    table = client.create_table(table, exists_ok=config.existsOk, timeout=30)

    with open('table.json', 'w') as table_file:
        json.dump(table.to_api_repr(), table_file, indent=2, sort_keys=True)


@dataclass_json
@dataclass
class CopyTableConfig():
    # https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html#google.cloud.bigquery.client.Client.copy_table
    # the table(s) to copy from
    sources: List[dict]
    # the table to copy to
    destination: dict
    # Extra configuration options for the job.
    createDisposition: str = "CREATE_IF_NEEDED"
    writeDisposition: str = "WRITE_EMPTY"


def copy_table(config: CopyTableConfig):
    client = bigquery.Client()
    source_tables = list(
        map(lambda d: bigquery.Table.from_api_repr(d), config.sources))
    dest_table = bigquery.Table.from_api_repr(config.destination)

    job_config = bigquery.CopyJobConfig(
        create_disposition=config.createDisposition,
        write_disposition=config.writeDisposition
    )

    job = client.copy_table(source_tables, dest_table, job_config=job_config)
    job.result()
    table = client.get_table(dest_table)

    with open('table.json', 'w') as table_file:
        json.dump(table.to_api_repr(), table_file, indent=2, sort_keys=True)


@dataclass_json
@dataclass
class CreateDatasetConfig():
    # https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets#resource-dataset
    dataset: dict
    # Fields to update if dataset already exists, and is not being dropped
    fields: Optional[List[str]]
    # If dataset already exists, drop it (including contents)
    drop: bool = False
    # If dataset already exists, don't return an error
    existsOk: bool = True


def create_dataset(config: CreateDatasetConfig):
    """
    Creates a dataset -> dataset.json
    If there is a dataset already of the same name it can be deleted or have specified fields updated with new values
    """
    client = bigquery.Client()
    dataset = bigquery.Dataset.from_api_repr(config.dataset)
    try:
        existing_dataset = client.get_dataset(dataset.reference)
        if config.fields is not None:
            modified_dataset = client.update_dataset(
                dataset, fields=config.fields, timeout=30)
            return modified_dataset.to_api_repr()
        if config.drop:
            client.delete_dataset(
                existing_dataset, not_found_ok=True, delete_contents=True)
    except exceptions.NotFound:
        pass
    dataset = client.create_dataset(
        dataset, exists_ok=config.existsOk, timeout=30)

    with open('dataset.json', 'w') as dataset_file:
        json.dump(dataset.to_api_repr(), dataset_file,
                  indent=2, sort_keys=True)


@dataclass_json
@dataclass
class DeleteDatasetConfig():
    # https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets#DatasetReference
    datasetRef: dict
    # Delete contents if dataset is not already empty
    deleteContents: bool = False
    # Do not throw error if dataset does not exist
    notFoundOk: bool = False


def delete_dataset(config: DeleteDatasetConfig):
    """
    Deletes a dataset
    """
    client = bigquery.Client()
    dataset_ref = bigquery.DatasetReference.from_api_repr(config.datasetRef)
    client.delete_dataset(dataset_ref, timeout=30, not_found_ok=config.notFoundOk,
                          delete_contents=config.deleteContents)


@dataclass_json
@dataclass
class QueryConfig():
    # Query string
    query: str
    # Map of replacement values for query
    replacements: Optional[dict]
    # Map of tables used in query, replacements are {key} -> full_table_id
    dependencies: Optional[dict]
    # https://cloud.google.com/bigquery/docs/reference/rest/v2/tables#resource:-table
    destination: Optional[dict] = None
    # Set to one of csv, json, html to print the row data to stdout
    format: Optional[str] = None
    # Drop any existing table with the same name (ensures table is a completely new version)
    drop: bool = False
    defaultDataset: Optional[dict] = None
    labels: Optional[dict] = None
    schemaUpdateOptions: Optional[List[str]] = None
    scriptOptions: Optional[dict] = None
    maximumBytesBilled: Optional[str] = None
    destinationEncryptionConfiguration: Optional[dict] = None
    createDisposition: str = "CREATE_IF_NEEDED"
    writeDisposition: str = "WRITE_EMPTY"
    queryPriority: str = "INTERACTIVE"
    useQueryCache: bool = True


def query(config: QueryConfig):
    """
    Executes a query, optionally retrieving row data to stdout. 
    Writes Table to table.json and Job to job.json
    """
    client = bigquery.Client()

    job_config = bigquery.QueryJobConfig(
        destination_encryption_configuration=bigquery.EncryptionConfiguration.from_api_repr(
            config.destinationEncryptionConfiguration) if config.destinationEncryptionConfiguration is not None else None,
        priority=config.queryPriority,
        script_options=bigquery.ScriptOptions.from_api_repr(
            config.scriptOptions),
        use_legacy_sql=False,
        use_query_cache=config.useQueryCache
    )

    if config.defaultDataset is not None:
        job_config.default_dataset = bigquery.DatasetReference.from_api_repr(
            config.defaultDataset)

    if config.labels is not None:
        job_config.labels = config.labels

    if config.destination:
        destination_table = bigquery.Table.from_api_repr(config.destination)
        job_config.destination = destination_table
        job_config.write_disposition = config.writeDisposition
        job_config.create_disposition = config.createDisposition

        if config.drop:
            client.delete_table(destination_table, not_found_ok=True)
            # We create the table ourself, otherwise constraints are seemingly ignored
            if config.createDisposition == "CREATE_IF_NEEDED":
                client.create_table(destination_table, exists_ok=True)
                job_config.write_disposition = "WRITE_APPEND"  # or constraints are lost
            if config.writeDisposition == "WRITE_APPEND" and config.schemaUpdateOptions:
                job_config.schema_update_options = config.schemaUpdateOptions

    if config.maximumBytesBilled:
        job_config.maximum_bytes_billed = config.maximumBytesBilled

    # Format the query with replacement values (will NOT error if a replacement found has no value mapped to it)
    query = config.query
    if config.replacements is not None:
        for key, value in config.replacements.items():
            query = query.replace("{"+key+"}", value)

    if config.dependencies is not None:
        for key, value in config.dependencies.items():
            ref = bigquery.TableReference.from_api_repr(
                value["tableReference"])
            query = query.replace(
                "{"+key+"}", "{}.{}.{}".format(ref.project, ref.dataset_id, ref.table_id))

    # Start the query
    query_job = client.query(query, job_config)

    # Wait for query to complete
    result = query_job.result()

    final_result = {}
    # Optionally print the row data to stdout
    if config.format is not None:
        df: DataFrame = result.to_dataframe()
        if config.format == "csv":
            df.to_csv(sys.stdout, index=False)
        if config.format == "json":
            df.to_json(sys.stdout, orient="records")
        if config.format == "html":
            df.to_html(sys.stdout)

    # Call the Job REST API, as query_job.to_api_repr() is missing statistics
    extra_params = {"projection": "full"}
    path = "/projects/{}/jobs/{}".format(query_job.project, query_job.job_id)
    span_attributes = {
        "path": path, "job_id": query_job.job_id, "location": query_job.location}
    job_result = client._call_api(retry=DEFAULT_RETRY, span_name="BigQuery.getJob",
                                  span_attributes=span_attributes, method="GET", path=path, query_params=extra_params)

    # Write job information to job.json
    with open('job.json', 'w') as job_result_file:
        json.dump(job_result, job_result_file, indent=2, sort_keys=True)

    # Write the updated destination table to table.json
    with open('table.json', 'w') as dest_table_file:
        # If no destination, this will be a BQ temp table
        table_ref = job_result.get('configuration').get(
            'query').get('destinationTable')
        if table_ref is not None:
            table_info = client.get_table(
                bigquery.TableReference.from_api_repr(table_ref))
            json.dump(table_info.to_api_repr(),
                      dest_table_file, indent=2, sort_keys=True)


def main(args=None):
    parser = argparse.ArgumentParser(description="jGCP BigQuery utility")

    parser.add_argument('--project_id', metavar='PROJECT_ID', type=str,
                        help='Project ID when creating a new client (default: infer from environment)')

    parser.add_argument('--credentials', metavar='KEY.JSON', type=str,
                        help='JSON credentials file (default: infer from environment)')

    parser.add_argument('command', choices=['query', 'create_table', 'copy_table', 'create_dataset',
                                            'delete_dataset'], type=str.lower, help='command to execute')

    parser.add_argument('config', help='JSON configuration file for command')
    args = parser.parse_args()

    config = Path(args.config).read_text()

    if args.project_id is not None:
        os.environ['GCP_PROJECT'] = args.project_id
    if args.credentials is not None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credentials

    if args.command == "create_dataset":
        create_dataset(config=CreateDatasetConfig.from_json(config))

    if args.command == "delete_dataset":
        delete_dataset(config=DeleteDatasetConfig.from_json(config))

    if args.command == "create_table":
        create_table(config=CreateTableConfig.from_json(config))

    if args.command == "copy_table":
        copy_table(config=CopyTableConfig.from_json(config))

    if args.command == "query":
        query(config=QueryConfig.from_json(config))


if __name__ == '__main__':
    sys.exit(main())
