version development

import "../src/main/wdl/cloudsql.wdl" as csql

workflow CreateInstanceTest {
    input {
        String? apiProjectId
        File? credentials
        String instanceProjectId
        String instanceName
        String? region
        String? databaseVersion
        String? tier
        Boolean? enableIpv4
        Boolean? requireSSL
        String? privateNetwork
        String databaseId
    }

    call csql.CreateInstance as CreateInstanceTestWDL {
        input:
            apiProjectId = apiProjectId,
            credentials=credentials, 
            instanceProjectId = instanceProjectId,
            instanceName = instanceName, 
            region=region,
            databaseVersion=databaseVersion,
            tier=tier,
            enableIpv4=enableIpv4, 
            requireSSL=requireSSL, 
            privateNetwork=privateNetwork
    }

    call csql.CreateDatabase as CreateDatabaseTestWDL {
        input:
            apiProjectId = apiProjectId,
            credentials=credentials, 
            instanceProjectId = instanceProjectId,
            instanceName = CreateInstanceTestWDL.createdInstance.name, 
            databaseId=databaseId
    }

    call csql.DeleteDatabase as DeleteDatabaseTestWDL {
        input:
            apiProjectId = apiProjectId, 
            credentials=credentials, 
            instanceProjectId = instanceProjectId,
            instanceName = instanceName,
            databaseId=CreateDatabaseTestWDL.createdDatabase.name
    }

    call csql.DeleteInstance as DeleteInstanceTestWDL after DeleteDatabaseTestWDL {
        input:
            apiProjectId = apiProjectId, 
            credentials=credentials, 
            instanceProjectId = instanceProjectId,
            instanceName = CreateDatabaseTestWDL.createdDatabase.instance    
    }

    output {
        DatabaseInstance testInstance = CreateInstanceTestWDL.createdInstance    
        Database testDatabase = CreateDatabaseTestWDL.createdDatabase
        String deleteDatabaseResult = DeleteDatabaseTestWDL.deleteDatabase
        String deleteInstanceResult = DeleteInstanceTestWDL.deleteInstance
    }
}