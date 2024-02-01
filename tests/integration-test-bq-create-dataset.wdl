version development
#
# WDL wrapper for WDL-kit integration test for bigquery.wdl
#
import "../src/main/wdl/bigquery.wdl" as bq

workflow IntegrationTestBqCreateDataset {
   
    input {
        File? testCredentials
        String testProjectId
        Array[Map[String, String]]? testAcls
    }

    # update test dataset acl
    call bq.CreateDataset as TEST_CREATE_DATASET {
        input:
            credentials = testCredentials, projectId = testProjectId,
            dataset = object {
                description: "Dataset for integration-test",
                datasetReference: { "projectId": "~{testProjectId}", "datasetId": "xxxx_testing_dataset" }
            },
            acls = testAcls
    }

    output {    
        String? testUpdateACL = if defined(TEST_CREATE_DATASET.createdDataset) then 'Passed' else 'Not Done'
    }
}

