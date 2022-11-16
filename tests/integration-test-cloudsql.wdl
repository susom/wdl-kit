version development

import "../src/main/wdl/cloudsql.wdl" as csql
import "../src/main/wdl/structs.wdl"

workflow CreateInstanceTest {
    input {
        String? apiProjectId
        File? credentials
        CreateInstance createInstance
        Database database
        CsqlConfig queryConfig
    }

    call csql.CreateDatabaseInstance as CreateDatabaseInstanceTestWDL {
        input:
            apiProjectId = apiProjectId,
            credentials=credentials, 
            createInstance = createInstance
    }

    call csql.CreateDatabase as CreateDatabaseTestWDL after CreateDatabaseInstanceTestWDL {
        input:
            apiProjectId = apiProjectId,
            credentials=credentials, 
            database = database
    }

    call csql.CsqlQuery as CsqlQueryWDL after CreateDatabaseTestWDL{
        input:
            apiProjectId = apiProjectId,
            credentials = credentials, 
            queryConfig = queryConfig
    }

    call csql.DeleteDatabase as DeleteDatabaseTestWDL after CsqlQueryWDL {
        input:
            apiProjectId = apiProjectId, 
            credentials=credentials, 
            database = database
    }

    call csql.DeleteInstance as DeleteInstanceTestWDL after DeleteDatabaseTestWDL {
        input:
            apiProjectId = apiProjectId, 
            credentials=credentials, 
            databaseInstance = createInstance.databaseInstance
    }

    output {
        DatabaseInstance testInstance = CreateDatabaseInstanceTestWDL.createdInstance    
        Database testDatabase = CreateDatabaseTestWDL.createdDatabase
        File queryOutput = CsqlQueryWDL.stdout
        File deleteDatabaseResult = DeleteDatabaseTestWDL.deleteDatabase
        File deleteInstanceResult = DeleteInstanceTestWDL.deleteInstance
    }
}