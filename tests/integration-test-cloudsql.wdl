version development

import "../src/main/wdl/cloudsql.wdl" as csql
import "../src/main/wdl/structs.wdl"

workflow CreateInstanceTest {
    input {
        String? apiProjectId
        File? credentials
        DatabaseInstance databaseInstance
        Database database
    }

    call csql.CreateInstance as CreateInstanceTestWDL {
        input:
            apiProjectId = apiProjectId,
            credentials=credentials, 
            databaseInstance = databaseInstance
    }

    call csql.CreateDatabase as CreateDatabaseTestWDL after CreateInstanceTestWDL {
        input:
            apiProjectId = apiProjectId,
            credentials=credentials, 
            database = database
    }

    call csql.DeleteDatabase as DeleteDatabaseTestWDL after CreateDatabaseTestWDL {
        input:
            apiProjectId = apiProjectId, 
            credentials=credentials, 
            database = database
    }

    call csql.DeleteInstance as DeleteInstanceTestWDL after DeleteDatabaseTestWDL {
        input:
            apiProjectId = apiProjectId, 
            credentials=credentials, 
            databaseInstance = databaseInstance
    }

    output {
        DatabaseInstance testInstance = CreateInstanceTestWDL.createdInstance    
        Database testDatabase = CreateDatabaseTestWDL.createdDatabase
        File deleteDatabaseResult = DeleteDatabaseTestWDL.deleteDatabase
        File deleteInstanceResult = DeleteInstanceTestWDL.deleteInstance
    }
}