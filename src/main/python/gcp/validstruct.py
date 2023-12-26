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
import json
import sys

struct_object = """
{
  "Dataset": [
    "kind",
    "etag",
    "id",
    "selfLink",
    "datasetReference",
    "friendlyName",
    "description",
    "defaultTableExpirationMs",
    "defaultPartitionExpirationMs",
    "labels",
    "access",
    "creationTime",
    "lastModifiedTime",
    "location",
    "defaultEncryptionConfiguration",
    "satisfiesPzs",
    "type",
    "maxTimeTravelHours",
    "isCaseInsensitive"
  ],

  "Table": [
    "kind",
    "etag",
    "id",
    "selfLink",
    "friendlyName",
    "tableReference",
    "description",
    "labels",
    "schema",
    "numBytes",
    "numLongTermBytes",
    "numRows",
    "numActiveLogicalBytes",
    "numActivePhysicalBytes",
    "numLongTermLogicalBytes",
    "numLongTermPhysicalBytes",
    "numTotalLogicalBytes",
    "numTotalPhysicalBytes",
    "numTimeTravelPhysicalBytes",
    "creationTime",
    "expirationTime",
    "lastModifiedTime",
    "type",
    "location"
  ],
  
  "DatabaseInstance": [
    "kind",
    "state",
    "databaseVersion",
    "settings",
    "etag",
    "failoverReplica",
    "masterInstanceName",
    "replicaNames",
    "maxDiskSize",
    "currentDiskSize",
    "ipAddresses",
    "serverCaCert",
    "instanceType",
    "project",
    "ipv6Address",
    "serviceAccountEmailAddress",
    "onPremisesConfiguration",
    "replicaConfiguration",
    "backendType",
    "selfLink",
    "suspensionReason",
    "connectionName",
    "name",
    "region",
    "gceZone",
    "secondaryGceZone",
    "diskEncryptionConfiguration",
    "diskEncryptionStatus",
    "rootPassword",
    "scheduledMaintenance",
    "satisfiesPzs",
    "databaseInstalledVersion",
    "createTime",
    "outOfDiskReport",
    "maintenanceVersion"
  ],

  "Database": [
    "kind",
    "charset",
    "collation",
    "etag",
    "name",
    "instance",
    "selfLink",
    "project",
    "sqlserverDatabaseDetails"
  ]
}
"""

def delete_keys_from_dict(dict_del, lst_keys):
    """
    Delete the keys present in lst_keys from the dictionary.
    Loops recursively but comment out the code for nested dictionaries.
    """
    dict_foo = dict_del.copy()  
    for field in dict_foo.keys():
        if field not in lst_keys:
            del dict_del[field]
        # if isinstance(dict_foo[field], dict):
        #     delete_keys_from_dict(dict_del[field], lst_keys)
    return dict_del

def valid_object(input_file_path: str, valid_object: str):
    if valid_object is not None and input_file_path is not None:
        
        valid_struct_json = json.loads(struct_object)

        with open(input_file_path) as jfile: 
            input_file = json.load(jfile)

        modifiedJson = delete_keys_from_dict(input_file, valid_struct_json[valid_object])
        return modifiedJson

def main(args=None):
    parser = argparse.ArgumentParser(description="JSON GCS utilities")

    parser.add_argument('--valid-object', metavar='valid_object', type=str,
                        help='The selected object in struct file to be validated')

    parser.add_argument('--input-json', metavar='input_json', type=str,
                        help='JSON credentials file to be validated')
    args = parser.parse_args()

    if args.valid_object is not None and args.input_json is not None:
        modifiedJson = valid_object(args.input_json, args.valid_object)
        with open('modified_file.json', 'w') as modified_file:
            json.dump(modifiedJson, modified_file, indent=2, sort_keys=True)

    if args.input_json and args.valid_object is None:
        parser.error("--input-json requires --valid-object")
 
    # d1 = {'a': 1, 'b': 2, 'c': 3, 'n': {'n1': 99, 'n2': 100}}
    # d2 = {'b': 2, 'c': 4, 'd': 5, 'n': {'n1': 99, 'n2': 100}}

    # intersection_keys = d1.keys() & d2.keys()
    # print(intersection_keys)


if __name__ == '__main__':
    sys.exit(main())
