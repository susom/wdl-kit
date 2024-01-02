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

  "DiskEncryptionConfiguration": [
    "kmsKeyName",
    "kind"
  ],

  "SqlOutOfDiskReport": [
    "sqlOutOfDiskState",
    "sqlMinRecommendedIncreaseSizeGb"
  ],

  "TableSchema": [
    "name",
    "type",
    "mode",
    "fields",
    "description",
    "policyTags",
    "maxLength",
    "precision",
    "scale"
  ],

  "PolicyTags": [
    "names"
  ],

  "TableFieldSchema": [
    "fields"
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

  "InstanceReference": [
    "name",
    "region",
    "project"
  ],

  "SourceInstance": [
    "name",
    "region",
    "project"
  ],

  "SqlScheduledMaintenance": [
    "startTime",
    "canDefer",
    "canReschedule",
    "scheduleDeadlineTime"
  ],

  "DiskEncryptionStatus": [
    "kmsKeyVersionName",
    "kind"
  ],

  "ReplicaConfiguration": [
    "kind",
    "mysqlReplicaConfiguration",
    "failoverTarget"
  ],

  "MySqlReplicaConfiguration": [
    "dumpFilePath",
    "username",
    "password",
    "connectRetryInterval",
    "masterHeartbeatPeriod",
    "caCertificate",
    "clientCertificate",
    "clientKey",
    "sslCipher",
    "verifyServerCertificate",
    "kind"
  ],

  "OnPremisesConfiguration": [
    "hostPort",
    "kind",
    "username",
    "password",
    "caCertificate",
    "clientCertificate",
    "clientCertificate",
    "clientKey",
    "dumpFilePath",
    "sourceInstance"
  ],

  "SslCert": [
    "kind",
    "certSerialNumber",
    "cert",
    "createTime",
    "commonName",
    "expirationTime",
    "sha1Fingerprint",
    "instance",
    "selfLink"
  ],

  "FailoverReplica": [
    "name",
    "available"
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
  ],

  "EncryptionConfiguration": [
    "kmsKeyName"
  ],

  "Settings": [
    "settingsVersion",
    "authorizedGaeApplications",
    "tier",
    "kind",
    "userLabels",
    "availabilityType",
    "pricingPlan",
    "replicationType",
    "storageAutoResizeLimit",
    "activationPolicy",
    "ipConfiguration",
    "storageAutoResize",
    "locationPreference",
    "databaseFlags",
    "dataDiskType",
    "maintenanceWindow",
    "backupConfiguration",
    "databaseReplicationEnabled",
    "crashSafeReplicationEnabled",
    "dataDiskSizeGb",
    "activeDirectoryConfig",
    "collation",
    "denyMaintenancePeriods",
    "insightsConfig",
    "passwordValidationPolicy",
    "sqlServerAuditConfig",
    "connectorEnforcement",
    "deletionProtectionEnabled"
  ],

  "IpConfiguration": [
    "ipv4Enabled",
    "privateNetwork",
    "requireSsl",
    "authorizedNetworks",
    "allocatedIpRange",
    "sslMode"
  ],

  "SqlServerAuditConfig": [
    "kind",
    "bucket",
    "retentionInterval",
    "uploadInterval"
  ],

  "PasswordValidationPolicy": [
    "minLength",
    "complexity",
    "reuseInterval",
    "disallowUsernameSubstring",
    "passwordChangeInterval",
    "enablePasswordPolicy"
  ],

  "InsightsConfig": [
    "queryInsightsEnabled",
    "recordClientAddress",
    "recordApplicationTags",
    "queryStringLength",
    "queryPlansPerMinute"
  ],

  "SqlActiveDirectoryConfig": [
    "kind",
    "domain"
  ],

  "BackupConfiguration": [
    "startTime",
    "enabled",
    "kind",
    "binaryLogEnabled",
    "replicationLogArchivingEnabled",
    "location",
    "pointInTimeRecoveryEnabled",
    "transactionLogRetentionDays",
    "backupRetentionSettings"
  ],

  "BackupRetentionSettings": [
    "retentionUnit",
    "retainedBackups"
  ],

  "MaintenanceWindow": [
    "hour",
    "day",
    "updateTrack",
    "kind"
  ],

  "LocationPreference": [
    "followGaeApplication",
    "zone",
    "secondaryZone",
    "kind"
  ],
  
  "SqlserverDatabaseDetails": [
    "compatibilityLevel",
    "recoveryModel"
  ]

}
"""

def delete_keys_from_dict(dict_del, lst_keys):
    """
    Delete the keys present in lst_keys from the dictionary.
    Loops recursively but comment out the code for nested dictionaries.
    """
    dict_foo = dict_del.copy()  
    for key, value in dict_foo.items():
        if isinstance(value, dict) and struct_exist(key[0].upper() + key[1:]):
            valid_struct_json = json.loads(struct_object)
            nested_keys = valid_struct_json[key[0].upper() + key[1:]]
            delete_keys_from_dict(dict_del[key], nested_keys)
        else:
            if key not in lst_keys:
              del dict_del[key]
    return dict_del

def struct_exist(field_name: str):
    valid_struct_json = json.loads(struct_object)
    if field_name in valid_struct_json:
        return True
    return False

def valid_object(input_file_path: str, valid_object: str):
    if valid_object is not None and input_file_path is not None:
        
        valid_struct_json = json.loads(struct_object)

        with open(input_file_path) as jfile: 
            input_file = json.load(jfile)

        modifiedJson = delete_keys_from_dict(input_file, valid_struct_json[valid_object])
        return modifiedJson

def main(args=None):
    parser = argparse.ArgumentParser(description="JSON Key Fieltering Utilities")

    parser.add_argument('--valid-object', metavar='valid_object', type=str,
                        help='The selected object to be validated')

    parser.add_argument('--input-json', metavar='input_json', type=str,
                        help='JSON credentials file to be validated')
    args = parser.parse_args()

    if args.valid_object is not None and args.input_json is not None:
        modifiedJson = valid_object(args.input_json, args.valid_object)
        with open('modified_file.json', 'w') as modified_file:
            json.dump(modifiedJson, modified_file, indent=2, sort_keys=True)

    if args.input_json and args.valid_object is None:
        parser.error("--input-json requires --valid-object")
 
if __name__ == '__main__':
    sys.exit(main())
