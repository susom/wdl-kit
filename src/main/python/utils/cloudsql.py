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
from pyparsing import Optional

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

def insert_instance(config):
    credentials = GoogleCredentials.get_application_default()
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)
    print(config)
    instanceConig = json.loads(config)
    operation = cloudsql.instances().insert(project=instanceConig['project'], body=instanceConig).execute()
    result = wait_for_operation(cloudsql, instanceConig['project'], operation["name"])
    if "error" in result:
        raise Exception(result["error"])
    
    instanceName = result["targetId"]
    projectId = result["targetProject"]

    with open('instance.json', 'w') as instance_file:
        json.dump(cloudsql.instances().get(project=projectId, instance=instanceName).execute(), instance_file, indent=2, sort_keys=True)

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

    instanceConfig = json.loads(config)

    if instance_get(instanceConfig['project'], instanceConfig['name']):
        operation = cloudsql.instances().delete(project=instanceConfig['project'], instance=instanceConfig['name']).execute()
        result = wait_for_operation(cloudsql, instanceConfig['project'], operation["name"])
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
    databaseConfig = json.loads(config)
    operation = cloudsql.databases().insert(project=databaseConfig['project'], instance=databaseConfig['instance'], body=databaseConfig).execute()
    result = wait_for_operation(cloudsql, databaseConfig['project'], operation["name"])
    if "error" in result:
        raise Exception(result["error"])
    
    instanceName = result["targetId"]
    projectId = result["targetProject"]

    with open('database.json', 'w') as database_file:
        json.dump(cloudsql.databases().get(project=projectId, instance=instanceName, database=databaseConfig['name']).execute(), database_file, indent=2, sort_keys=True)

def delete_database(config):
    credentials = GoogleCredentials.get_application_default()
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)
    databaseConfig = json.loads(config)
    if database_get(databaseConfig['project'], databaseConfig['instance'], databaseConfig['name']):
        operation = cloudsql.databases().delete(project=databaseConfig['project'], instance=databaseConfig['instance'], database=databaseConfig['name']).execute()
        result = wait_for_operation(cloudsql, databaseConfig['project'], operation["name"])
        if "error" in result:
            raise Exception(result["error"])

        with open('delete_database.json', 'w') as delete_database_file:
            json.dump(result, delete_database_file, indent=2, sort_keys=True)
    else:
        print("Database Not Found")

def main():
    parser = argparse.ArgumentParser(description="Google CloudSql utility")

    parser.add_argument("--project_id", required=False, help="Your Google Cloud project ID.")
    parser.add_argument('--credentials', required=False, help='Specify path to a GCP JSON credentials file')
    
    parser.add_argument('command', choices=['instance_insert', 'instance_delete', 'database_insert', 'database_delete'], type=str.lower, help='command to execute')
    parser.add_argument('config', help='JSON configuration file for command')

    args = parser.parse_args()

    if args.credentials is not None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credentials

    if args.project_id is not None:
        os.environ['GCLOUD_PROJECT'] = args.project_id
    

    if args.command == "instance_insert" and args.config is not None:
        config = Path(args.config).read_text()
        insert_instance(config)

    if args.command == "instance_delete" and args.config is not None:
        config = Path(args.config).read_text()
        delete_instance(config)

    if args.command == "database_insert" and args.config is not None:
        config = Path(args.config).read_text()
        insert_database(config)

    if args.command == "database_delete" and args.config is not None:
        config = Path(args.config).read_text()
        delete_database(config)


if __name__ == '__main__':
    sys.exit(main())