version development

import "../src/main/wdl/cloudsql.wdl" as csql

workflow CreateInstanceTest {
    input {
        String projectId
        File? credentials
        String instanceName
        String? region
        String? databaseVersion
        String? tier
        Boolean? enableIpv4
        Boolean? requireSSL
        String? privateNetwork
        String? databaseId
    }

    call csql.CreateInstance as CreateInstanceTestWDL {
        input:
            projectId = projectId,credentials=credentials, 
            instanceName = instanceName, 
            region=region,
            databaseVersion=databaseVersion,
            tier=tier,
            enableIpv4=enableIpv4, 
            requireSSL=requireSSL, 
            privateNetwork=privateNetwork
    }

    call csql.CreateDatabase as CreateDatabaseTestWDL after CreateInstanceTestWDL {
        input:
            projectId = projectId,credentials=credentials, 
            instanceName = instanceName, 
            databaseId=databaseId
    }

    call csql.DeleteDatabase as DeleteDatabaseTestWDL after CreateDatabaseTestWDL {
        input:
            projectId = projectId, credentials=credentials, 
            instanceName = instanceName,
            databaseId=databaseId
    }

    call csql.DeleteInstance as DeleteInstanceTestWDL after DeleteDatabaseTestWDL {
        input:
            projectId = projectId, credentials=credentials, 
            instanceName = instanceName    
    }

    output {
        DatabaseInstance testInstance = CreateInstanceTestWDL.createdInstance    
        Database testDatabase = CreateDatabaseTestWDL.createdDatabase
        String deleteDatabaseResult = DeleteDatabaseTestWDL.deleteDatabase
        String deleteInstanceResult = DeleteInstanceTestWDL.deleteInstance
    }
}