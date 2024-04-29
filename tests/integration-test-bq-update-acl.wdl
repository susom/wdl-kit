version development
#
# WDL wrapper for WDL-kit integration test for bigquery.wdl
#
import "../src/main/wdl/bigquery.wdl" as bq

workflow IntegrationTestBqUpdateAcl {
   
    input {
        File? testCredentials
        String testProjectId
        String testDataset_id
        Array[AccessEntry] testAcls
        Boolean? testAppend
    }

    # update test dataset acl
    call bq.UpdateACL as TEST_UPDATE_ACL {
        input:
            credentials = testCredentials, projectId = testProjectId,
            dataset_id = testDataset_id,
            acls = testAcls,
            append = testAppend
    }

    output {    
        String? testUpdateACL = if defined(TEST_UPDATE_ACL.updateAclDatasetRef) then 'Passed' else 'Not Done'
    }
}

