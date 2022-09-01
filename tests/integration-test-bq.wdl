version development
#
# WDL wrapper for WDL-kit integration test for bigquery.wdl
#
import "../src/main/wdl/bigquery.wdl" as bq
import "resources/.test_tables.yaml.wdl" as yaml 

# Used by YAML SQL query files
struct Query {
  String? description
  String sql
  Array[TableFieldSchema]+ fields
}


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

workflow IntegrationTestBq {
   
    input {
        File? testCredentials
        String testProjectId
        Array[AccessEntry]? testAccessEntries
        String? prefix
        String suffix
        String release = "~{prefix}~{suffix}"
        String releaseGroup
        File? sourceFile
        String destinationUri
        String ExtractFileName = "integrationtest_file.csv"
        String CostLabel = "~{prefix}~{suffix}"
    }


    # Create test dataset
    call bq.CreateDataset as TestDataset {
        input:
            credentials = testCredentials, projectId = testProjectId,
            drop = true,
            dataset = object {
                description: "Dataset for integration-test",
                datasetReference: { "projectId": "~{testProjectId}", "datasetId": "~{prefix}~{suffix}" },
                labels: { "release_name": "~{release}", "release_group": "~{releaseGroup}", "archive" : "all" },
                access: testAccessEntries
            }
    }
       
    if (defined(TestDataset.createdDataset.datasetReference)) {
        Boolean TEST_CREATE_DATASET = true
    }

    call yaml.GetYaml
    Map[String, Query] queries = read_json(GetYaml.yaml)

    # LINK ./resources/test_tables.yaml#bq_test_table
    Query bqTestQuery = queries["bq_test_table"]
    call bq.Query as CreateTestDestTable after TestDataset {
        input:
            credentials = testCredentials, projectId = testProjectId,
            query = bqTestQuery.sql,
            destination = object {
                tableReference: { "tableId": "bq_test_table", "projectId": TestDataset.createdDataset.datasetReference.projectId, "datasetId": TestDataset.createdDataset.datasetReference.datasetId },
                description: bqTestQuery.description, 
                schema: { "fields": bqTestQuery.fields } 
            },
            drop = true,
            labels = {"calculatecost": CostLabel}
    }

    if (defined(CreateTestDestTable.table)) {
        Boolean TEST_CREATE_TABLE = true
    }
    
  
    if (defined(sourceFile)) {
        # LINK ./resources/test_tables.yaml#bq_test_source_table
        Query bqSourceTableQuery = queries["bq_test_source_table"]
        call bq.Query as CreateTestSourceTable after CreateTestDestTable {
            input:
                credentials = testCredentials, projectId = testProjectId,
                query = bqSourceTableQuery.sql,
                destination = object {
                    tableReference: { "tableId": "bq_test_source_table", "projectId": TestDataset.createdDataset.datasetReference.projectId, "datasetId": TestDataset.createdDataset.datasetReference.datasetId },
                    description: bqSourceTableQuery.description, 
                    schema: { "fields": bqTestQuery.fields } 
                },
                drop = true,
                labels = {"calculatecost": CostLabel}
        }

        call bq.LoadTable as LoadCSVData after CreateTestSourceTable {
            input:
                credentials = testCredentials, projectId = testProjectId,
                sourceFile = sourceFile,
                format = "CSV",
                destination = object {
                    projectId: TestDataset.createdDataset.datasetReference.projectId,
                    datasetId: TestDataset.createdDataset.datasetReference.datasetId,
                    tableId: "bq_test_source_table" 
                },
                skipLeadingRows = 1,
                writeDisposition = "WRITE_TRUNCATE"                
        }

        if (defined(LoadCSVData.table)) {
            Boolean TEST_LOAD_TABLE = true
        }

        call bq.CopyTable as CopyToDestTable after LoadCSVData {
            input:
                credentials = testCredentials, projectId = testProjectId,
                sources = [LoadCSVData.table],
                destination =  CreateTestDestTable.table,
                writeDisposition = "WRITE_TRUNCATE"
        }

        if (defined(CopyToDestTable.destinationTable)) {
            Boolean TEST_COPY_TABLE = true
        }
 

         # extract table data to bucket. 
        if (defined(destinationUri)) {
            Boolean emptyUri = if destinationUri == "" then true else false
            if(!emptyUri)
            {
                call bq.ExtractTable as ExtractDestTable after CopyToDestTable {
                    input:
                        credentials = testCredentials, projectId = testProjectId,
                        sourceTable = CreateTestDestTable.table,
                        destinationUri = destinationUri,
                        fileFormat = "CSV",
                        fileName = ExtractFileName
                }

                if (defined(ExtractDestTable.job)) {
                    Boolean TEST_EXTRACT_TABLE = true
                }
            }
        }

        # validate original data with copied over data
        call GetFileContent as ShowSourceFile after CopyToDestTable {
            input:
                sourceFile = sourceFile
        }

        # LINK ./resources/test_tables.yaml#destination_table_data
        Query bqDestOutputQuery = queries["destination_table_data"]
        call bq.Query as ShowTestDestTable after ShowSourceFile {
            input:
                credentials = testCredentials, projectId = testProjectId,
                query = bqDestOutputQuery.sql,
                dependencies = { 
                    "bq_test_table": CreateTestDestTable.table
                },
                format = "csv",
                labels = {"calculatecost": CostLabel}
        }

        call GetFileContent as ShowTestDestTableData after ShowTestDestTable {
            input:
                sourceFile = ShowTestDestTable.results
        }

    
        call bq.DeleteDataset as DeleteDatasetWithData after ShowTestDestTableData {
            input:
                credentials = testCredentials, projectId = testProjectId,
                datasetRef = TestDataset.createdDataset.datasetReference
        }

        if (defined(DeleteDatasetWithData.deletedDatasetRef)) {
            Boolean TEST_DELETE_DATASET= true
        }
            
    }

     output {
        # DatasetReference testDataset = TestDataset.createdDataset.datasetReference      
        # String? testCreateDataset = if defined(TEST_CREATE_DATASET) then 'Passed' else 'Not Done'
        # String? testCreateTable = if defined(TEST_CREATE_TABLE) then 'Passed' else 'Not Done'
        # String? testLoadTable = if defined(TEST_LOAD_TABLE) then 'Passed' else 'Not Done'
        # String? testCopyTable = if defined(TEST_COPY_TABLE) then 'Passed' else 'Not Done'
        # String? testExtractTable = if defined(TEST_EXTRACT_TABLE) then 'Passed' else 'Not Done'
        # String? testDeleteDataset = if defined(TEST_DELETE_DATASET) then 'Passed' else 'Not Done'
        String? finalResult = if ShowSourceFile.fileContent==ShowTestDestTableData.fileContent then ">>>>>>>>>>>>>>>>>>>>>>>>>>>> Integration Test Successful" else ">>>>>>>>>>>>>>>>>>>>>>>>>>>> Integration Test Failed"
    }
}

