version development

# version 1.6.1

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
  String? maxTimeTravelHours
  Boolean? isCaseInsensitive
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

struct DatabaseInstance {
  String? kind
  String? state
  String? databaseVersion
  Settings? settings
  String? etag
  FailoverReplica? failoverReplica
  String? masterInstanceName
  Array[String]? replicaNames
  String? maxDiskSize
  String? currentDiskSize
  Array[IpMapping]? ipAddresses
  SslCert? serverCaCert
  String? instanceType
  String? project
  String? ipv6Address
  String? serviceAccountEmailAddress
  OnPremisesConfiguration? onPremisesConfiguration
  ReplicaConfiguration? replicaConfiguration
  String? backendType
  String? selfLink
  Array[String]? suspensionReason
  String? connectionName
  String name
  String? region
  String? gceZone
  String? secondaryGceZone
  DiskEncryptionConfiguration? diskEncryptionConfiguration
  DiskEncryptionStatus? diskEncryptionStatus
  String? rootPassword
  SqlScheduledMaintenance? scheduledMaintenance
  Boolean? satisfiesPzs
  String? databaseInstalledVersion
  String? createTime
  SqlOutOfDiskReport? outOfDiskReport
  String? maintenanceVersion
}

struct InstanceReference {
  String? name
  String? region
  String? project
}

struct SqlOutOfDiskReport {
  String? sqlOutOfDiskState
  Int? sqlMinRecommendedIncreaseSizeGb
}

struct SqlScheduledMaintenance {
  String? startTime
  Boolean? canDefer
  Boolean? canReschedule
  String? scheduleDeadlineTime
}

struct DiskEncryptionStatus {
  String? kmsKeyVersionName
  String? kind
}

struct DiskEncryptionConfiguration {
  String? kmsKeyName
  String? kind
}

struct ReplicaConfiguration {
  String? kind
  MySqlReplicaConfiguration? mysqlReplicaConfiguration
  Boolean? failoverTarget
}

struct MySqlReplicaConfiguration {
  String? dumpFilePath
  String? username
  String? password
  String? connectRetryInterval
  String? masterHeartbeatPeriod
  String? caCertificate
  String? clientCertificate
  String? clientKey
  String? sslCipher
  Boolean? verifyServerCertificate
  String? kind
}

struct OnPremisesConfiguration {
  String? hostPort
  String? kind
  String? username
  String? password
  String? caCertificate
  String? clientCertificate
  String? clientKey
  String? dumpFilePath
  InstanceReference? sourceInstance
}

struct SslCert {
  String? kind
  String? certSerialNumber
  String? cert
  String? createTime
  String? commonName
  String? expirationTime
  String? sha1Fingerprint
  String? instance
  String? selfLink
}

struct FailoverReplica {
  String? name
  Boolean? available
}

struct Settings {
  String? settingsVersion
  Array[String]? authorizedGaeApplications
  String? tier
  String? kind
  Map[String, String]? userLabels
  String? availabilityType
  String? pricingPlan
  String? replicationType
  String? storageAutoResizeLimit
  String? activationPolicy
  IpConfiguration? ipConfiguration
  Boolean? storageAutoResize
  LocationPreference? locationPreference
  Array[DatabaseFlags]? databaseFlags
  String? dataDiskType
  MaintenanceWindow? maintenanceWindow
  BackupConfiguration? backupConfiguration
  Boolean? databaseReplicationEnabled
  Boolean? crashSafeReplicationEnabled
  String? dataDiskSizeGb
  SqlActiveDirectoryConfig? activeDirectoryConfig
  String? collation
  Array[DenyMaintenancePeriod]? denyMaintenancePeriods
  InsightsConfig? insightsConfig
  PasswordValidationPolicy? passwordValidationPolicy
  SqlServerAuditConfig? sqlServerAuditConfig
  String? connectorEnforcement
  Boolean? deletionProtectionEnabled
}

struct SqlServerAuditConfig {
  String? kind
  String? bucket
  String? retentionInterval
  String? uploadInterval
}

struct PasswordValidationPolicy {
  Int? minLength
  String? complexity
  Int? reuseInterval
  Boolean? disallowUsernameSubstring
  String? passwordChangeInterval
  Boolean? enablePasswordPolicy
}

struct InsightsConfig {
  Boolean? queryInsightsEnabled
  Boolean? recordClientAddress
  Boolean? recordApplicationTags
  Int? queryStringLength
  Int? queryPlansPerMinute
}

struct DenyMaintenancePeriod {
  String? startDate
  String? endDate
  String? time
}

struct SqlActiveDirectoryConfig {
  String? kind
  String? domain
}

struct BackupConfiguration {
  String? startTime
  Boolean? enabled
  String? kind
  Boolean? binaryLogEnabled
  Boolean? replicationLogArchivingEnabled
  String? location
  Boolean? pointInTimeRecoveryEnabled
  Int? transactionLogRetentionDays
  BackupRetentionSettings? backupRetentionSettings
}

struct BackupRetentionSettings {
  String? retentionUnit
  Int? retainedBackups
}

struct MaintenanceWindow {
  Int? hour
  Int? day
  String? updateTrack
  String? kind
}

struct DatabaseFlags {
  String? name
  String? value
}

struct LocationPreference {
  String? followGaeApplication
  String? zone
  String? secondaryZone
  String? kind
}

struct IpConfiguration {
  Boolean? ipv4Enabled
  String? privateNetwork
  Boolean? requireSsl
  String? sslMode
  Array[AclEntry]? authorizedNetworks
  String? allocatedIpRange
}

struct AclEntry {
  String? value
  String? expirationTime
  String? name
  String? kind
}

struct IpMapping {
  String? type
  String? ipAddress
  String? timeToRetire
}

struct Database {
  String? kind
  String? charset
  String? collation
  String? etag
  String name
  String instance
  String? selfLink
  String project
  SqlserverDatabaseDetails? sqlserverDatabaseDetails
}

struct SqlserverDatabaseDetails {
  String? compatibilityLevel
  String? recoveryModel
}

struct CsqlConfig {
  Database database
  String region
  String user
  String? password
  String query
  String? ipType
  String? format
}

struct CreateInstance {
  DatabaseInstance databaseInstance
  DatabaseUser? databaseUser
}

struct DatabaseUser {
  String name
  String type
}

struct CreatedDatabaseUser {
  String? operationType
  String? user
  String? status
}

struct InstancesImportRequest {
  ImportContext importContext
}

struct ImportContext {
  String project
  String instance
  String kind
  String uri
  String database
  String fileType
  CsvImportOptions csvImportOptions
  String? importUser
}

struct CsvImportOptions {
  String table
  Array[String]? columns 
}

struct CsvModifyOptions {
  String csvfile
  Array[Int]? dropColIndex
  Boolean removeHeader
  String newFileName
}

struct BackupOptions {
  String quotaProject
  String datasetName
  String backupUri
  Boolean metadataOnly
  Boolean printHeader
  Boolean? createHeaderFile
  String logLevel
  Boolean json
  String destinationFormat
  String compression
  Boolean mergeCsv
  Int threads
}

struct RestoreOptions {
  String quotaProject
  String datasetName
  String backupRestoreJsonUri
  Boolean dropDataset
  Boolean dropTables
  Boolean metadataOnly
  String logLevel
  Boolean json
  Int threads
  Int? defaultTableExpiration
  Int? defaultPartitionExpiration
  Boolean? keepExpiration
}