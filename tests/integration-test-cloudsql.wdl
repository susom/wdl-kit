version development

import "../src/main/wdl/cloudsql.wdl" as csql

workflow CreateInstanceTest {
    input {
        String? apiProjectId
        File? credentials
        CreateInstance createInstance
        Database database
        InstancesImportRequest instancesImportRequest
        CsqlConfig createTableQuery
        CsqlConfig rowcountTableQuery
        String? grantBucket
    }

    call csql.CreateDatabaseInstance as CreateInstanceTestWDL {
        input:
            apiProjectId = apiProjectId,
            credentials=credentials, 
            createInstance = createInstance,
            grantBucket = grantBucket
    }

    call csql.CreateDatabase as CreateDatabaseTestWDL after CreateInstanceTestWDL {
        input:
            apiProjectId = apiProjectId,
            credentials=credentials, 
            database = database
    }

    call csql.CsqlQuery as CreateTable after CreateDatabaseTestWDL {
        input:
            apiProjectId = apiProjectId,
            credentials = credentials, 
            queryConfig = createTableQuery
    }

    call csql.ImportFile after CreateTable {
        input:
            apiProjectId = apiProjectId,
            credentials=credentials, 
            instancesImportRequest = instancesImportRequest
    }

    call csql.CsqlQuery as TableRowCount after ImportFile {
        input:
            apiProjectId = apiProjectId,
            credentials = credentials, 
            queryConfig = rowcountTableQuery
    }

    call csql.DeleteDatabase as DeleteDatabaseTestWDL after TableRowCount {
        input:
            apiProjectId = apiProjectId, 
            credentials=credentials, 
            database = database
    }

    call csql.DeleteInstance as DeleteInstanceTestWDL after DeleteDatabaseTestWDL {
        input:
            apiProjectId = apiProjectId, 
            credentials=credentials, 
            databaseInstance = CreateInstanceTestWDL.createdInstance 
    }

    output {
        DatabaseInstance testInstance = CreateInstanceTestWDL.createdInstance    
        Database testDatabase = CreateDatabaseTestWDL.createdDatabase
        File queryOutput = TableRowCount.stdout
        File deleteDatabaseResult = DeleteDatabaseTestWDL.deleteDatabase
        File deleteInstanceResult = DeleteInstanceTestWDL.deleteInstance
    }
}