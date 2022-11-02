version development
#
# WDL wrapper for WDL-kit integration test for gcs.wdl
#
import "../src/main/wdl/gcs.wdl" as gcs

# task GetBucketFileContent {
#     input {
#         String sourceFile
#     }

#     command <<<
#         gsutil cat "~{sourceFile}" | sed "s/\"//g" | sed 's/\\//g'
#     >>>

#     output {
#         String fileContent = read_lines(stdout())
#     }

# }

task GetFileContent {
    input {
        File? sourceFile
    }

    command <<<
        cat "~{sourceFile}" | sed "s/\"//g" | sed 's/\\//g'
    >>>

    output {
        String fileContent = read_lines(stdout())
    }

}

workflow IntegrationTestGcs {
   
    input {
        File? testCredentials
        String testProjectId
      
        String gcsDestination
        String gcsSourcePrefix
        String gcsDownloadSourceBucket
        String gcsDownloadSourcePrefix

        String gcsUploadSourceBucket
        String gcsUploadSourcePrefix
        File gcsUploadFile
    }

    call gcs.Compose as gcsCompose {
        input:
                credentials = testCredentials, projectId = testProjectId,
                destination = gcsDestination,
                sourcePrefix = gcsSourcePrefix
    }

    if (defined(gcsCompose.blob)) {
        Boolean TEST_GCS_COMPOSE = true
    }

    call gcs.Download as gcsDownload after gcsCompose {
        input:
                credentials = testCredentials, projectId = testProjectId,
                sourceBucket = gcsDownloadSourceBucket,
                sourcePrefix = gcsDownloadSourcePrefix
    } 

    if (defined(gcsDownload.files)) {
        Boolean TEST_GCS_DOWNLOAD = true
    }

    call gcs.Upload as gcsUpload {
        input:
                credentials = testCredentials, projectId = testProjectId,
                sourceFile = gcsUploadFile,
                sourceBucket = gcsUploadSourceBucket,
                sourcePrefix = gcsUploadSourcePrefix
    } 

    if (defined(gcsUpload.blob)) {
        Boolean TEST_GCS_UPLOAD = true
    }

    call GetFileContent as ShowSourceFile {
            input:
                sourceFile = gcsDownload.files[0]
    }

    if(defined(TEST_GCS_COMPOSE)){
        if(defined(TEST_GCS_DOWNLOAD)){
            String? finalResult = ">>>>>>>>>>>>>>>>>>>> Integration Test Successful"
        }
    }

    output {
        String? testGcsCompose = if defined(TEST_GCS_COMPOSE) then 'Passed' else 'Failed'
        String? testGcsDownload = if defined(TEST_GCS_DOWNLOAD) then 'Passed' else 'Failed'  
        String? testGcsUpload = if defined(TEST_GCS_UPLOAD) then 'Passed' else 'Failed'
        String? finalTestResult = finalResult
        # String? downloadFile = ShowSourceFile.fileContent        
    }
}

