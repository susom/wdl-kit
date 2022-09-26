version development
#
# WDL wrapper for WDL-kit wbq
#
import "structs.wdl"

struct QueryConfig {
  # Should be identical to Query.input
  String query
  Map[String, String]? replacements
  Map[String, Table]? dependencies
  DatasetReference? defaultDataset
  Table? destination
  String? format
  Map[String, String]? labels
  Boolean drop
  Array[String]? schemaUpdateOptions
  ScriptOptions? scriptOptions
  Int? maximumBytesBilled
  EncryptionConfiguration? destinationEncryptionConfiguration
  String createDisposition
  String writeDisposition
  String queryPriority
  Boolean useQueryCache
  String delimiter
  Boolean header
}

# Runs a Query saving result to another table (which is dropped beforehand, by default)
task Query {

    parameter_meta {
      credentials: { description: "Optional JSON credential file" }
      projectId: { description: "Default project to use for API requests" }
      query: { description: "Standard SQL query" }
      replacements: { description: "Map containing SQL template replacement values {placeholder}" }
      dependencies: { description: "Map containing tables used in query (key->full table id)" }
      defaultDataset: { description: "Default dataset to use for unqualified table names" }
      destination: { description: "Optional, query outputs to table" }
      format: { description: "One of (csv,json,html): saves row data to results output" }
      labels: { description: "Map containing labels for the BigQuery job" }
      schemaUpdateOptions: { description: "String array containing a mix of ALLOW_FIELD_ADDITION and ALLOW_FIELD_RELAXATION" }
      scriptOptions: { description: "Options controlling the execution of scripts." }
      maximumBytesBilled: { description: "Maximum bytes allowed to bill for this job" }
      destinationEncryptionConfiguration: { description: "Custom encryption configuration (e.g., Cloud KMS keys)" }
      drop: { description: "Drop any existing destination table before executing query (default)" }
      createDisposition: { description: "One of [ (CREATE_IF_NEEDED), CREATE_NEVER ]" }
      writeDisposition: { description: "One of [ WRITE_APPEND, WRITE_TRUNCATE, (WRITE_EMPTY) ]" }
      queryPriority: { description: "Query priority [ INTERACTIVE, (BATCH) ]" }
      useQueryCache: { description: "Use BigQuery query cache if possible (default: no)" }
      delimiter: { description: "What should be the column delimitter for the CSV (default: comma)" }
      header: { description: "Should there be a header row in the CSV (default: true)" }
    }

    input {
      File? credentials
      String projectId
      String query
      Map[String, String]? replacements
      Map[String, Table]? dependencies
      DatasetReference? defaultDataset
      Table? destination
      String? format
      Map[String, String]? labels
      Boolean drop = false
      Array[String]? schemaUpdateOptions
      ScriptOptions? scriptOptions
      Int? maximumBytesBilled
      EncryptionConfiguration? destinationEncryptionConfiguration
      String createDisposition = "CREATE_IF_NEEDED"
      String writeDisposition = "WRITE_EMPTY"
      String queryPriority = "BATCH"
      Boolean useQueryCache = true
      String delimiter = ","
      Boolean header = true

      Int cpu = 1
      String memory = "128 MB"
      String dockerImage = "wdl-kit:1.2.2"
    }

    QueryConfig config = object {
      query: query,
      replacements: replacements,
      dependencies: dependencies,
      defaultDataset: defaultDataset,
      destination: destination,
      format: format,
      labels: labels,
      drop: drop,
      schemaUpdateOptions: schemaUpdateOptions,
      scriptOptions: scriptOptions,
      maximumBytesBilled: maximumBytesBilled,
      destinationEncryptionConfiguration: destinationEncryptionConfiguration,
      createDisposition: createDisposition,
      writeDisposition: writeDisposition,
      queryPriority: queryPriority,
      useQueryCache: useQueryCache, 
      delimiter: delimiter, 
      header: header
    }

    command {
      wbq ${"--project_id=" + projectId} ${"--credentials=" + credentials} query ~{write_json(config)}
    }

    output {
      Table table = read_json("table.json")
      File job = "job.json"
      File results = stdout()
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}

struct CreateTableConfig {
  Table table
  Boolean drop
}

# Creates a table (Table)
task CreateTable {

    parameter_meta {
      credentials: { description: "Optional JSON credential file" }
      projectId: { description: "Default project to use for API requests" }
      table: { description: "Table to create" }
      drop: { description: "Drop any existing table and contents" }
    }

    input {
      File? credentials
      String projectId
      Table table
      Boolean drop = false

      Int cpu = 1
      String memory = "128 MB"
      String dockerImage = "wdl-kit:1.2.2"
    }

    CreateTableConfig config = object {
      table: table,
      drop: drop
    }

    command {
      wbq ${"--project_id=" + projectId} ${"--credentials=" + credentials} create_table ~{write_json(config)}
    }

    output {
      Table createdTable = read_json("table.json")
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}

struct CopyTableConfig {
  Array[Table]+ sources
  Table destination
  String createDisposition
  String writeDisposition
}

task CopyTable {
    
    parameter_meta {
      credentials: { description: "Optional JSON credential file" }
      projectId: { description: "Default project to use for API requests" }
      sources: { description: "Tables to copy from" }
      destination: { description: "Table to copy to" }
      createDisposition: { description: "One of [ (CREATE_IF_NEEDED), CREATE_NEVER ]" }
      writeDisposition: { description: "One of [ WRITE_APPEND, WRITE_TRUNCATE, (WRITE_EMPTY) ]" }
    }

    input {
      File? credentials
      String projectId
      Array[Table]+ sources
      Table destination
      String createDisposition = "CREATE_IF_NEEDED"
      String writeDisposition = "WRITE_EMPTY"

      Int cpu = 1
      String memory = "128 MB"
      String dockerImage = "wdl-kit:1.2.2"
    }

    CopyTableConfig config = object {
      sources: sources,
      destination: destination,
      createDisposition: createDisposition,
      writeDisposition: writeDisposition
    }

    command {
      wbq ${"--project_id=" + projectId} ${"--credentials=" + credentials} copy_table ~{write_json(config)}
    }

    output {
      Table destinationTable = read_json("table.json")
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}

struct ExtractTableConfig {
  Table sourceTable
  String destinationUri
  String fileName
  String fileFormat
  String location
}

task ExtractTable {
  parameter_meta {
    credentials: { description: "Optional JSON credential file" }
    projectId: { description: "Default project to use for API requests" }
    sourceTable: { description: "The table that data will be extracted from." }
    destinationUri: { description: "The storage container URI that the extract will be placed." }
    fileName: { description: "The name to give the extract file once generated. Ex: 'notes-*.csv'" }
    fileFormat: { description: "The option for how the file should be delimited and formatted. Ex: CSV, NEWLINE_DELIMITED_JSON, PARQUET, etc. Defaults to CSV."}
    location: { description: "The location of the source table to be extracted, used to prevent cross country extractions. Defaults to US."}
  }
  
  input {
    File? credentials
    String projectId
    Table sourceTable
    String destinationUri
    String fileName
    String fileFormat
    String location = "US"

    Int cpu = 1
    String memory = "128 MB"
    String dockerImage = "wdl-kit:1.2.2"
  }

  ExtractTableConfig config = object {
    sourceTable: sourceTable,
    destinationUri: destinationUri,
    fileName: fileName,
    fileFormat: fileFormat,
    location: location
  }

  command {
    wbq ${"--project_id=" + projectId} ${"--credentials=" + credentials} extract_table ~{write_json(config)}
  }

  output {
    File job = "job.json"
  }

  runtime {
    docker: dockerImage
    cpu: cpu
    memory: memory
  }
}


struct LoadTableConfig {
  File? sourceFile
  String? sourceUris
  String? sourceBucket
  String? sourcePrefix
  String? sourceDelimiter
  TableReference destination
  Array[TableFieldSchema]? schemaFields
  String format 
  Int skipLeadingRows
  String createDisposition
  String writeDisposition
  Boolean autodetect
  String location
}

task LoadTable {

  parameter_meta {
    credentials: { description: "Optional JSON credential file" }
    projectId: { description: "Default project to use for API requests" }
    sourceFile: { description: "Local file containing data to load" }
    sourceUris: { description: "Uri containing data to load" }
    sourceBucket: { description: "Bucket containing data to load" }
    sourcePrefix: { description: "Bucket prefix containing data to load" }
    sourceDelimiter: { description: "Bucket delimiter containing data to load" }
    destination: { description: "TableReference destination" }
    schemaFields: { description: "Array of TableFieldSchema for destination table" }
    format: { description: "Format of source data, defaults to CSV"}
    skipLeadingRows: { description: "Skip n rows from beginning of source file (eg. CSV headers)"}
    fieldDelimiter: { description: "CSV field delimiter (defaults to comma)"}
    quoteCharacter: { description: "CSV quoting character (defaults to double-quote)"}
    createDisposition: { description: "One of [ (CREATE_IF_NEEDED), CREATE_NEVER ]" }
    writeDisposition: { description: "One of [ WRITE_APPEND, WRITE_TRUNCATE, (WRITE_EMPTY) ]" }
    autodetect:  { description: "Autodetect schema of source file (defaults no)" }
    location: { description: "Location of load job, must match destination table location" }
  }
  
  input {
    File? credentials
    String projectId
    File? sourceFile
    String? sourceUris
    String? sourceBucket
    String? sourcePrefix
    String? sourceDelimiter
    TableReference destination
    Array[TableFieldSchema]? schemaFields
    String format
    Int skipLeadingRows = 0
    String createDisposition = "CREATE_IF_NEEDED"
    String writeDisposition = "WRITE_EMPTY"
    Boolean autodetect = false
    String location = "US"
    String dockerImage
    Int cpu = 1
    String memory = "128 MB"
  }

  LoadTableConfig config = object {
    sourceFile: sourceFile,
    sourceUris: sourceUris,
    sourceBucket: sourceBucket,
    sourcePrefix: sourcePrefix,
    sourceDelimiter: sourceDelimiter,
    destination: destination, 
    schemaFields: schemaFields,
    format: format,
    skipLeadingRows: skipLeadingRows, 
    createDisposition: createDisposition,
    writeDisposition: writeDisposition,
    autodetect: autodetect, 
    location: location
  }

  command {
    wbq ${"--project_id=" + projectId} ${"--credentials=" + credentials} load_table ~{write_json(config)}
  }

  output {
    File job = "job.json"
    Table table = read_json("table.json")
  }

  runtime {
    docker: dockerImage
    cpu: cpu
    memory: memory
  }
}



struct CreateDatasetConfig {
  Dataset dataset
  Boolean drop
  Array[String]? fields
}

# Creates a dataset (Dataset)
task CreateDataset {

    parameter_meta {
      credentials: { description: "Optional JSON credential file" }
      projectId: { description: "Default project to use for API requests" }
      dataset: { description: "Dataset to create" }
      drop: { description: "Drop any existing dataset and contents" }
      fields: { description: "List of fields to update if dataset already exists" }
    }

    input {
      File? credentials
      String projectId
      Dataset dataset
      Boolean drop = false
      Array[String]? fields

      Int cpu = 1
      String memory = "128 MB"
      String dockerImage = "wdl-kit:1.2.2"
    }

    CreateDatasetConfig config = object {
      dataset: dataset,
      drop: drop,
      fields: fields
    }

    command {
      wbq ${"--project_id=" + projectId} ${"--credentials=" + credentials} create_dataset ~{write_json(config)}
    }

    output {
      Dataset createdDataset = read_json("dataset.json")
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}

struct DeleteDatasetConfig {
  DatasetReference datasetRef
  Boolean deleteContents
  Boolean notFoundOk
}

# Deletes a dataset (DatasetReference)
task DeleteDataset {

    parameter_meta {
      credentials: { description: "Optional JSON credential file" }
      projectId: { description: "Default project to use for API requests" }
      datasetRef: { description: "DatasetReference to delete" }
      deleteContents: { description: "Drop dataset contents if not empty" }
      notFoundOk: { description: "Do not return error if dataset does not exist" }
    }

    input {
      File? credentials
      String projectId
      DatasetReference datasetRef
      Boolean deleteContents = true
      Boolean notFoundOk = false

      Int cpu = 1
      String memory = "128 MB"
      String dockerImage = "wdl-kit:1.2.2"
    }

    DeleteDatasetConfig config = object {
      datasetRef: datasetRef,
      notFoundOk: notFoundOk,
      deleteContents: deleteContents
    }

    command {
      wbq ${"--project_id=" + projectId} ${"--credentials=" + credentials} delete_dataset ~{write_json(config)}
    }

    output {
      DatasetReference deletedDatasetRef = datasetRef
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}
