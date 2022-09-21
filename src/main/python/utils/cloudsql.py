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
import time
from urllib.request import Request

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from pprint import pprint

credentials = GoogleCredentials.get_application_default()

def create_sql_instance(cloudsql, project_id, config):
    return cloudsql.instances().insert(project=project_id, body=config).execute()

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

def main(project_id, config):
    cloudsql = discovery.build('sqladmin', 'v1beta4', credentials=credentials)
    operation = create_sql_instance(cloudsql, project_id, config)
    if(wait_for_operation(cloudsql, project_id, operation["name"])):
        print("SQL Instance creation finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--project_id", help="Your Google Cloud project ID.")
    parser.add_argument("--instance_name", help="Name of the sql instance.")
    parser.add_argument("--region", default="us-west2", help="Region where the instance will be located, default is us-west2.")
    parser.add_argument("--db_version", default="POSTGRES_12", help="Type that the db instance should be, default is POSTGRES_12.")
    parser.add_argument("--tier", default="db-custom-1-3840", help="Specs for the instance that will be created, default is db-custom-1-3840.")

    args = parser.parse_args()

    # config = { "name": "tjt8712test", "region": "us-west2", "databaseVersion": "POSTGRES_14", "settings": {"tier": "db-custom-1-3840", "ipConfiguration": {"ipv4Enabled": False, "requireSsl": False, "privateNetwork": "projects/som-rit-phi-starr-dev/global/networks/default"}}}
    config = { 
        "name": args.instance_name, 
        "region": args.region, 
        "databaseVersion": args.db_version, 
        "settings": {
            "tier": args.tier, 
            "ipConfiguration": {
                "ipv4Enabled": False, 
                "requireSsl": False, 
                "privateNetwork": "projects/som-rit-phi-starr-dev/global/networks/default"
            }
        }
    }

    main(args.project_id, config)