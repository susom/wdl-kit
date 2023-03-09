version development
#
# WDL wrapper for jgcs Google Cloud Storage functions
#
import "structs.wdl"

struct ComposeConfig {
  # gs:// URI to final composed object
  String destination
  # URI prefix used to find source blobs
  String sourcePrefix
  # Delimiter for prefix, usually /
  String? sourceDelimiter 
  # Deletes source files after successful composition
  Boolean? deleteSources
}

# Quickly composes multiple files (based on a matching prefix) into a single file, using GCS composition
task Compose {

    parameter_meta {
      credentials: { description: "Optional JSON credential file" }
      projectId: { description: "Default project to use for API requests" }
      bucket: { description: "Bucket of source and destination objects" }
      destination: { description: "path/filename of final composed object" }
      sourcePrefix: { description: "prefix to determine what files to compose (note this is NOT a -* syntax)" }
      sourceDelimiter: { description: "(optional) delimiter to use when finding source files, eg /" }
      deleteSources: { description: "delete source files upon successful composition" }
    }

    input {
      File? credentials
      String? projectId
      String destination
      String sourcePrefix
      String? sourceDelimiter
      Boolean deleteSources = false

      Int cpu = 1
      String memory = "128 MB"
      String dockerImage = "wdl-kit:1.5.1"
    }

    ComposeConfig config = object {
      destination: destination,
      sourcePrefix: sourcePrefix,
      sourceDelimiter: sourceDelimiter,
      deleteSources: deleteSources
    }

    command {
      wgcs ${"--project_id=" + projectId} ${"--credentials=" + credentials} compose ~{write_json(config)}
    }

    output {
      Blob blob = read_json(stdout())
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}


struct DownloadConfig {
  # Source bucket
  String sourceBucket
  # prefix used to find source blobs in bucket
  String sourcePrefix
  # Delimiter for prefix, usually /
  String? sourceDelimiter
  # Deletes source files after successful download
  Boolean? deleteSources
  # Keeps the prefix in the destination filename (replaces '/' with '_')
  Boolean? keepPrefix
}

# Downloads files from GCS bucket (sequentially) -- use scatter for parallelism
task Download {

    parameter_meta {
      credentials: { description: "Optional JSON credential file" }
      projectId: { description: "Default project to use for API requests" }
      sourceBucket: { description: "bucket containing source objects" }
      sourcePrefix: { description: "download all object names with this prefix" }
      sourceDelimiter: { description: "(optional) delimiter to use when finding source files, eg /" }
      deleteSources: { description: "delete GCS source objects upon successful composition" }
      keepPrefix: { description: "Include prefix of source objects (replacing / with _)" }
    }

    input {
      File? credentials
      String? projectId
      String sourceBucket
      String sourcePrefix
      String? sourceDelimiter
      Boolean deleteSources = false
      Boolean keepPrefix = false
      Int cpu = 1
      String memory = "128 MB"
      String dockerImage = "wdl-kit:1.5.1"
    }

    DownloadConfig config = object {
      sourceBucket: sourceBucket,
      sourcePrefix: sourcePrefix,
      sourceDelimiter: sourceDelimiter,
      deleteSources: deleteSources,
      keepPrefix: keepPrefix
    }

    command {
      wgcs ${"--project_id=" + projectId} ${"--credentials=" + credentials} download ~{write_json(config)}
    }

    output {
      Array[File] files = read_json(stdout())
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}

struct UploadConfig {
  # Source bucket
  String sourceBucket
  # prefix used to find source blobs in bucket
  String sourcePrefix
  # Source file 
  File sourceFile
}

# Uploads a file to GCS bucket
task Upload {
    parameter_meta {
      credentials: { description: "Optional JSON credential file" }
      projectId: { description: "Default project to use for API requests" }
      sourceBucket: { description: "bucket containing source objects" }
      sourcePrefix: { description: "upload the object name with this prefix" }
      sourceFile: { description: "path location of the file" }
    }

    input {
      File? credentials
      String? projectId
      String sourceBucket
      String sourcePrefix
      File sourceFile
      Int cpu = 1
      String memory = "128 MB"
      String dockerImage = "wdl-kit:1.5.1"
    }

    UploadConfig config = object {
      sourceBucket: sourceBucket,
      sourcePrefix: sourcePrefix,
      sourceFile: sourceFile
    }

    command {
      wgcs ${"--project_id=" + projectId} ${"--credentials=" + credentials} upload ~{write_json(config)}
    }

    output {
      Blob blob = read_json(stdout())
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}
