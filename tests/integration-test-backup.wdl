version development
import "../src/main/wdl/bigquery.wdl" as bq
import "resources/.test_tables.yaml.wdl" as yaml 
import "../src/main/wdl/backup.wdl" as backup
import "../src/main/wdl/restore.wdl" as restore

# Used by YAML SQL query files
struct Query {
    String? description
    String sql
    Array[TableFieldSchema]+ fields
}

workflow BackupUtilTest{
    input {
        String apiProjectId
        File credentials
        Array[AccessEntry]? testAccessEntries
        String? prefix
        String suffix
        String release = "~{prefix}~{suffix}"
        String releaseGroup
        File? sourceFile

        BackupOptions? backupOptions
        RestoreOptions? restoreOptions
    }

     # Create test dataset
    call bq.CreateDataset as TestDataset {
        input:
            credentials = credentials, projectId = apiProjectId,
            drop = true,
            dataset = object {
                description: "Dataset for integration-test",
                datasetReference: { "projectId": "~{apiProjectId}", "datasetId": "~{prefix}~{suffix}" },
                labels: { "release_name": "~{release}", "release_group": "~{releaseGroup}", "archive" : "all" },
                access: testAccessEntries
            }
    }
    

    call yaml.GetYaml
    Map[String, Query] queries = read_json(GetYaml.yaml)

    # LINK ./resources/test_tables.yaml#bq_test_table
    Query bqTestQuery = queries["bq_test_table"]
    call bq.Query as CreateTestDestTable after TestDataset {
        input:
            credentials = credentials, projectId = apiProjectId,
            query = bqTestQuery.sql,
            destination = object {
                tableReference: { "tableId": "bq_test_table", "projectId": TestDataset.createdDataset.datasetReference.projectId, "datasetId": TestDataset.createdDataset.datasetReference.datasetId },
                description: bqTestQuery.description, 
                schema: { "fields": bqTestQuery.fields } 
            },
            drop = true
    }

    Query bqSourceTableQuery = queries["bq_test_source_table"]
    call bq.Query as CreateTestSourceTable after CreateTestDestTable {
        input:
            credentials = credentials, projectId = apiProjectId,
            query = bqSourceTableQuery.sql,
            destination = object {
                tableReference: { "tableId": "bq_test_source_table", "projectId": TestDataset.createdDataset.datasetReference.projectId, "datasetId": TestDataset.createdDataset.datasetReference.datasetId },
                description: bqSourceTableQuery.description, 
                schema: { "fields": bqTestQuery.fields } 
            },
            drop = true
    }

    call bq.LoadTable as LoadCSVData after CreateTestSourceTable {
        input:
            credentials = credentials, projectId = apiProjectId,
            sourceFile = sourceFile,
            format = "CSV",
            destination = object {
                projectId: TestDataset.createdDataset.datasetReference.projectId,
                datasetId: TestDataset.createdDataset.datasetReference.datasetId,
                tableId: "bq_test_source_table" 
            },
            skipLeadingRows = 1,
            writeDisposition = "WRITE_TRUNCATE",
            dockerImage = "us-west1-docker.pkg.dev/som-rit-infrastructure-prod/starr/wdl-kit:1.4.0"                
    }

    call backup.BackupDataset as Backup after LoadCSVData {
        input:
            apiProjectId = apiProjectId,
            credentials = credentials, 
            backupOptions = select_first([backupOptions])
    }

    call restore.RestoreDataset as Restore after Backup {
        input:
            apiProjectId = apiProjectId,
            credentials = credentials, 
            restoreOptions = select_first([restoreOptions])
    }

    String testProjectId = select_first([backupOptions]).quotaProject
    String testDatasetId = select_first([backupOptions]).datasetName
    call bq.Query as BqRowCount after Restore {
        input:
            credentials = credentials, projectId = apiProjectId,
            format = "csv",
            query = "select count(*) from `~{testProjectId}.~{testDatasetId}.bq_test_source_table`;",
            drop=true
    }

    String testProjectId1 = select_first([restoreOptions]).quotaProject
    String testDatasetId1 = select_first([restoreOptions]).datasetName
    call bq.Query as BqRowCountRestore after Restore {
        input:
            credentials = credentials, projectId = apiProjectId,
            format = "csv",
            query = "select count(*) from `~{testProjectId1}.~{testDatasetId1}.bq_test_source_table`;",
            drop=true
    }

    call GetRowcount as GetRowcountBackup {
        input:
            logfile = BqRowCount.results
    }

    call GetRowcount as GetRowcountRestore {
        input:
            logfile = BqRowCountRestore.results
    }

    DatasetReference datasetReference = object {
        projectId: testProjectId,
        datasetId: testDatasetId
    }
    call bq.DeleteDataset as DeleteDatasetBackup after GetRowcountRestore {
        input:
            credentials = credentials, projectId = apiProjectId,
            datasetRef = datasetReference
    }

    DatasetReference datasetReference1 = object {
        projectId: testProjectId1,
        datasetId: testDatasetId1
    }
    call bq.DeleteDataset as DeleteDatasetRestore after GetRowcountRestore {
        input:
            credentials = credentials, projectId = apiProjectId,
            datasetRef = datasetReference1
    }

    output {
        String? rowcountResultBackup = GetRowcountBackup.rowNumber
        String? rowcountResultRestore = GetRowcountRestore.rowNumber
    }
}

task GetRowcount {
    input {
        File? logfile 
        String dockerImage = "us-west1-docker.pkg.dev/som-rit-infrastructure-prod/starr/wdl-kit:1.4.0"
    }

    command <<<
        tail -1 "~{logfile}"
    >>>

    runtime {
        docker: dockerImage
    }

    output {
        String rowNumber = read_string(stdout())
    }
}