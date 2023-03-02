# Copyright 2022 The Board of Trustees of The Leland Stanford Junior University.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
from pathlib import Path
import time
import sys
import json
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
# from pyparsing import Optional
from typing import Optional
import pg8000
import sqlalchemy
from sqlalchemy import insert
from google.cloud.sql.connector import Connector, IPTypes
import pandas as pd
from google.cloud import storage

class CsqlConfig:
    project: str
    name: str
    instance: str
    ipType: str
    user: str
    password: str
    query: str
    format: Optional[str] = None

    def __init__(self, project, region, instance, ipType, name, user, password, query, format):
        self.project = project
        self.name = name
        self.instance = instance
        self.ipType = ipType
        self.region = region
        self.user = user
        self.password = password
        self.query= query
        self.format = format
    
    def getconn(self):
        with Connector() as connector:
            conn = connector.connect(
                f'{self.project}:{self.region}:{self.instance}', # Cloud SQL Instance Connection Name
                "pg8000",
                db=self.name,
                user=self.user,
                password=self.password,
                ip_type=self.ipType 
            )
                
        return conn

    def getconn_iam(self):
        with Connector() as connector:
            # print(f'Came_here to connect with {self.user} and {self.ipType}')
            conn = connector.connect(
                f'{self.project}:{self.region}:{self.instance}', # Cloud SQL Instance Connection Name
                "pg8000",
                db=self.name,
                user=self.user,
                password=None,
                ip_type=self.ipType,
                enable_iam_auth=True
            )
                
        return conn

    def queryDb(self):
        
        engine = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=self.getconn if self.password is not None else self.getconn_iam
        )
        
        with engine.connect(self) as db_conn:

            # query database
            result = db_conn.execute(sqlalchemy.text(self.query))

            if self.format == "csv":
                df = pd.DataFrame(result.fetchall())
                df.to_csv(sys.stdout, index=False)
            if self.format == "json":
                df = pd.DataFrame(result.fetchall())
                df.to_json(sys.stdout, orient="records")
            if self.format == "html":
                df = pd.DataFrame(result.fetchall())
                df.to_html(sys.stdout)                
     
            # close connection
            db_conn.close()

def wait_for_operation(cloudsql, project, operation):
    operation_complete = False
    while not operation_complete:
        result = (
            cloudsql.operations()
            .get(project=project, operation=operation)
            .execute()
        )

        if result["status"] == "DONE":
            return result

        time.sleep(1)
    return result

def insert_instance(config, grantBucket: str = None):
    credentials = GoogleCredentials.get_application_default()
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)

    json_config = json.loads(config)
    instance_config = json_config["databaseInstance"]

    operation = cloudsql.instances().insert(project=instance_config["project"], body=instance_config).execute()
    result = wait_for_operation(cloudsql, instance_config["project"], operation["name"])
    if "error" in result:
       raise Exception(result["error"])

    instanceName = result["targetId"]
    projectId = result["targetProject"]    

    if "databaseUser" in json_config and json_config["databaseUser"] is not None :
        add_user(instanceName, instance_config, json_config["databaseUser"])

    with open('instance.json', 'w') as instance_file:
        json.dump(cloudsql.instances().get(project=projectId, instance=instanceName).execute(), instance_file, indent=2, sort_keys=True)

    if grantBucket is not None:
        instanceProfile = open('instance.json', 'r')
        instance_config = json.load(instanceProfile)
        grantBucket = grantBucket.replace("gs://","")
        add_bucket_iam_member(grantBucket, "serviceAccount:"+instance_config["serviceAccountEmailAddress"])

def add_bucket_iam_member(bucket_name, member, role="roles/storage.objectViewer"):
    # bucket_name = "your-bucket-name"
    # role = "IAM role, e.g., roles/storage.objectViewer"
    # member = "IAM identity, e.g., user: name@example.com"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    policy = bucket.get_iam_policy(requested_policy_version=3)

    policy.bindings.append({"role": role, "members": {member}})

    bucket.set_iam_policy(policy)

def add_user(instanceName, instance_config, user_config):
    credentials = GoogleCredentials.get_application_default()
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)
    projectId = instance_config["project"] 

    operation = cloudsql.users().insert(project=projectId, instance=instanceName, body=user_config).execute()
    result = wait_for_operation(cloudsql, instance_config["project"], operation["name"])
    if "error" in result:
        delete_instance(instance_config)
        raise Exception(result["error"])

def instance_get(project_id, instance_name):
    credentials = GoogleCredentials.get_application_default()
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)
    try:
        cloudsql.instances().get(project=project_id, instance=instance_name).execute()
    except:
        return False 
    return True

def delete_instance(config):
    credentials = GoogleCredentials.get_application_default()
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)

    json_config = json.loads(config)
    if instance_get(json_config["project"], json_config["name"]):
        operation = cloudsql.instances().delete(project=json_config["project"], instance=json_config["name"]).execute()
        result = wait_for_operation(cloudsql, json_config["project"], operation["name"])
        if "error" in result:
            raise Exception(result["error"])

        with open('delete_instance.json', 'w') as delete_instance_file:
            json.dump(result, delete_instance_file, indent=2, sort_keys=True)
    else:
        print("Instance Not Found")


def database_get(project_id, instance_name, database_id):
    credentials = GoogleCredentials.get_application_default()
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)
    try:
        cloudsql.databases().get(project=project_id, instance=instance_name, database=database_id).execute()
    except:
        return False 
    return True

def insert_database(config):
    credentials = GoogleCredentials.get_application_default()
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)

    json_config = json.loads(config)
    operation = cloudsql.databases().insert(project=json_config["project"], instance=json_config["instance"], body=json_config).execute()
    result = wait_for_operation(cloudsql, json_config["project"], operation["name"])
    if "error" in result:
        raise Exception(result["error"])
    
    instanceName = result["targetId"]
    projectId = result["targetProject"]

    with open('database.json', 'w') as database_file:
        json.dump(cloudsql.databases().get(project=projectId, instance=instanceName, database=json_config["name"]).execute(), database_file, indent=2, sort_keys=True)


def delete_database(config):
    credentials = GoogleCredentials.get_application_default()
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)

    json_config = json.loads(config)
    if database_get(json_config["project"], json_config["instance"], json_config["name"]):
        operation = cloudsql.databases().delete(project=json_config["project"], instance=json_config["instance"], database=json_config["name"]).execute()
        result = wait_for_operation(cloudsql, json_config["project"], operation["name"])
        if "error" in result:
            raise Exception(result["error"])

        with open('delete_database.json', 'w') as delete_database_file:
            json.dump(result, delete_database_file, indent=2, sort_keys=True)
    else:
        print("Database Not Found")

def import_file(config):
    credentials = GoogleCredentials.get_application_default()
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)

    json_config = json.loads(config)
    operation = cloudsql.instances().import_(project=json_config["importContext"]["project"], instance=json_config["importContext"]["instance"], body=json_config).execute()
    result = wait_for_operation(cloudsql, json_config["importContext"]["project"], operation["name"])
    if "error" in result:
        raise Exception(result["error"])
    
    instanceName = result["targetId"]
    projectId = result["targetProject"]

    with open('import_file.json', 'w') as instance_file:
        json.dump(cloudsql.instances().get(project=projectId, instance=instanceName).execute(), instance_file, indent=2, sort_keys=True)

# https://cloud.google.com/storage/docs/access-control/using-iam-permissions#storage-add-bucket-iam-python
def add_bucket_iam_member(bucket_name, member, role="roles/storage.objectViewer"):
    # bucket_name = "your-bucket-name"
    # role = "IAM role, e.g., roles/storage.objectViewer"
    # member = "IAM identity, e.g., user: name@example.com"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    policy = bucket.get_iam_policy(requested_policy_version=3)

    policy.bindings.append({"role": role, "members": {member}})

    bucket.set_iam_policy(policy)

def modify_csv_file (config):
    try:
        json_config = json.loads(config)
        data = pd.read_csv(json_config["csvfile"], dtype=str)
        data.drop(data.columns[json_config["dropColIndex"]], inplace=True, axis=1)
        data.to_csv(json_config["newFileName"], header=(not json_config["removeHeader"]), index=False)
    except:
        return False
    finally:
        return True

def main():
    parser = argparse.ArgumentParser(description="Google CloudSql utility")

    parser.add_argument("--project_id", required=False, help="Your Google Cloud project ID.")
    parser.add_argument('--credentials', required=False, help='Specify path to a GCP JSON credentials file')
    parser.add_argument('--grant_bucket', required=False, help='Specify bucket to grant to service account')
    parser.add_argument('command', choices=['instance_insert', 'instance_delete', 'database_insert', 'database_delete', 'query', 'import_file', 'csv_update'], type=str.lower, help='command to execute')
    parser.add_argument('config', help='JSON configuration file for command')
    
    args = parser.parse_args()
    config = Path(args.config).read_text()

    if args.credentials is not None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credentials

    if args.project_id is not None:
        os.environ['GCLOUD_PROJECT'] = args.project_id
    
    if args.command == "instance_insert" and args.config is not None:
        insert_instance(config, args.grant_bucket)

    if args.command == "instance_delete" and args.config is not None:
        delete_instance(config)

    if args.command == "database_insert" and args.config is not None:
        insert_database(config)

    if args.command == "database_delete" and args.config is not None:
        delete_database(config)

    if args.command == "import_file" and args.config is not None:
        import_file(config)

    if args.command == "csv_update" and args.config is not None:
        modify_csv_file(config)
        
    if args.command == "query":
        json_config = json.loads(config)    
        json_database=json_config["database"]

        # check if password is supplied, if not, chop off anything after .iam in the username 
        user = json_config["user"]
        password = None
        if "password" in json_config and json_config["password"] is not None :
            password = json_config["password"]
        else:
            head, sep, tail = user.partition('.iam')
            user = f'{head}.iam'

        ipType=IPTypes.PRIVATE
        if "ipType" in json_config and json_config["ipType"] is not None and json_config["ipType"].lower() != "private" :
            ipType=IPTypes.PUBLIC
        
        csqlConfig = CsqlConfig( json_database["project"],json_config["region"], json_database["instance"], ipType, 
            json_database["name"], user, password, json_config["query"], json_config["format"])
        csqlConfig.queryDb() 

if __name__ == '__main__':
    sys.exit(main())
