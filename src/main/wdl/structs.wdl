version development

#
# Datasets
# https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets
#
struct DatasetReference {
  String projectId
  String datasetId
}

struct RoutineReference {
  String projectId
  String datasetId
  String routineId
}

# https://cloud.google.com/bigquery/docs/reference/rest/v2/TableReference
struct TableReference {
  String projectId
  String datasetId
  String tableId
}

struct AccessEntry {
  String role
  String? userByEmail
  String? groupByEmail
  String? domain
  String? specialGroup
  String? iamMember
  TableReference? view
  RoutineReference? routine
}

struct EncryptionConfiguration {
  String kmsKeyName
}

# https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets
struct Dataset {
  String? kind
  String? etag
  String? id
  String? selfLink
  DatasetReference datasetReference
  String? friendlyName
  String? description
  String? defaultTableExpirationMs
  String? defaultPartitionExpirationMs
  Map[String, String]? labels
  Array[AccessEntry]? access
  String? creationTime
  String? lastModifiedTime
  String? location
  EncryptionConfiguration? defaultEncryptionConfiguration
  Boolean? satisfiesPzs
  String? type
}

struct PolicyTags {
  Array[String] names
}

struct TableFieldSchema2 {
  String name
  String type
  String? mode
  #Array[TableFieldSchema3] fields # create if necessary... 
  String? description
  PolicyTags? policyTags
  Int? maxLength
  String? precision
  String? scale
}

struct TableFieldSchema {
  String name
  String type
  String? mode
  Array[TableFieldSchema2]? fields # WDL does not allow circular, only going one-level deep
  String? description
  PolicyTags? policyTags
  Int? maxLength
  String? precision
  String? scale
}

struct TableSchema {
  Array[TableFieldSchema] fields
}

# https://cloud.google.com/bigquery/docs/reference/rest/v2/tables
struct Table {
  String? kind
  String? etag
  String? id
  String? selfLink
  String? friendlyName
  TableReference tableReference
  String? description
  Map[String, String]? labels
  TableSchema? schema
  String? numBytes
  String? numLongTermBytes
  String? numRows
  String? numActiveLogicalBytes
  String? numActivePhysicalBytes
  String? numLongTermLogicalBytes
  String? numLongTermPhysicalBytes
  String? numTotalLogicalBytes
  String? numTotalPhysicalBytes
  String? numTimeTravelPhysicalBytes
  String? creationTime
  String? expirationTime
  String? lastModifiedTime
  String? type
  String? location
}

struct ScriptOptions {
  String statementTimeoutMs
  String statementByteBudget
  String keyResultStatement
}

# Replace all places where these two variables are in the code
struct Config {
  File? credentials
  String gcpProject
  String jgcp
}

struct SlackConfig {
  String tokenUri
  String channel
  String message
}

struct MailerConfig {
  String apiUrl
  String apiUri
  String mailTo
  String message
  String subject
  String sender
}

##
## GCS
## 
struct ProjectTeam {
  String projectNumber
  String team
}

# 
# object access resource
# https://cloud.google.com/storage/docs/json_api/v1/objectAccessControls#resource-representations
#
struct ObjectAccessControl {
  String? kind
  String? id
  String? selfLink
  String bucket
  # This field is named "object" which is a reserved word in WDL.. need a workaround
  String? object_
  String? generation
  String entity
  String role
  String? email
  String? entityId
  String? domain
  ProjectTeam projectTeam
  String? etag
}

struct Owner {
  String entity
  String entityId
}

struct CustomerEncryption {
  String encryptionAlgorithm
  String keySha256
}

#
# object
# https://cloud.google.com/storage/docs/json_api/v1/objects#resource-representations
#
struct Blob {
  String? kind
  String? id
  String? selfLink
  String name
  String bucket
  Int? generation
  Int? metageneration
  String? contentType
  String? timeCreated 
  String? updated 
  String? customTime 
  String? timeDeleted 
  Boolean? temporaryHold
  Boolean? eventBasedHold
  String? retentionExpirationTime
  String? storageClass
  String? timeStorageClassUpdated
  String? size
  String? md5Hash
  String? mediaLink
  String? contentEncoding
  String? contentDisposition
  String? contentLanguage
  String? cacheControl
  Map[String, String]? metadata
  Array[ObjectAccessControl]? acl
  Owner? owner
  String? crc32c
  Int? componentCount
  String? etag
  CustomerEncryption? customerEncryption
  String? kmsKeyName
}
