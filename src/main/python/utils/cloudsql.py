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
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from googleapiclient import discovery
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

@dataclass_json
@dataclass
class CreateInstanceConfig():
    # Name of the database instance to create
    instance_name: str
    # Region in GCP that the instance should be created in
    region: str = "us-west2"
    # The type of database instance to create
    database_version: str = "POSTGRES_12"
    # Specifications for the machine that the instance will be hosted on
    tier: str = "db-custom-1-3840"
    # Setting this to true will give the instance a public IP address
    enable_ipv4: bool = False
    # This will require an SSL connection to connect to the db istance
    require_ssl: bool = False
    # The private network that is used when allocating the instance a private IP address
    private_network: str = "projects/som-rit-phi-starr-dev/global/networks/default"

def create_instance(project_id, config: CreateInstanceConfig):
    credentials = GoogleCredentials.get_application_default()
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)
    request_config = {
        "name": config.instance_name, 
        "region": config.region, 
        "databaseVersion": config.database_version, 
        "settings": {
            "tier": config.tier, 
            "ipConfiguration": {
                "ipv4Enabled": config.enable_ipv4, 
                "requireSsl": config.require_ssl, 
                "privateNetwork": config.private_network
            }
        }
    }

    operation = cloudsql.instances().insert(project=project_id, body=request_config).execute()
    if(wait_for_operation(cloudsql, config.project_id, operation["name"])):
        print("SQL Instance creation finished.")

def main():
    parser = argparse.ArgumentParser(description="Google CloudSql utility")

    parser.add_argument("--project_id", required=False, help="Your Google Cloud project ID.")
    parser.add_argument('--credentials', required=False, help='Specify path to a GCP JSON credentials file')
    parser.add_argument('command', choices=['create_instance'], type=str.lower, help='command to execute')
    parser.add_argument('config', help='JSON configuration file for command')
    args = parser.parse_args()
    
    config = Path(args.config).read_text()

    if args.credentials is not None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credentials

    if args.project_id is not None:
        os.environ['GCLOUD_PROJECT'] = args.project_id

    if args.command == "create_instance":
        create_instance(args.project_id, config=CreateInstanceConfig.from_json(config))


if __name__ == '__main__':
    sys.exit(main())