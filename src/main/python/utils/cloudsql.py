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
from numpy import insert
from oauth2client.client import GoogleCredentials

def wait_for_operation(cloudsql, project, operation):
    print("Waiting for operation to finish...")
    operation_complete = False
    while not operation_complete:
        result = (
            cloudsql.operations()
            .get(project=project, operation=operation)
            .execute()
        )

        if result["status"] == "DONE":
            print("done.")
            operation_complete = True
            if "error" in result:
                raise Exception(result["error"])
            return result

        time.sleep(1)
    return operation_complete

def insert_instance(project_id, config):
    credentials = GoogleCredentials.get_application_default()
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)

    operation = cloudsql.instances().insert(project=project_id, body=config).execute()
    if(wait_for_operation(cloudsql, project_id, operation["name"])):
        print("SQL Instance creation finished.")
    
    with open('instance.json', 'w') as instance_file:
        json.dump(operation.get(), instance_file, indent=2, sort_keys=True)

def main():
    parser = argparse.ArgumentParser(description="Google CloudSql utility")

    parser.add_argument("--project_id", required=False, help="Your Google Cloud project ID.")
    parser.add_argument('--credentials', required=False, help='Specify path to a GCP JSON credentials file')
    parser.add_argument('command', choices=['insert'], type=str.lower, help='command to execute')
    parser.add_argument('config', help='JSON configuration file for command')
    args = parser.parse_args()

    if args.credentials is not None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credentials

    if args.project_id is not None:
        os.environ['GCLOUD_PROJECT'] = args.project_id

    if args.command == "insert":
        insert_instance(args.project_id, args.config)


if __name__ == '__main__':
    sys.exit(main())