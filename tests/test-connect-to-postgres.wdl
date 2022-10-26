version development

import "../src/main/wdl/cloudsql.wdl" as csql
import "../src/main/wdl/structs.wdl"

workflow connectToPostgres {
    input {
        String? apiProjectId
        File? credentials
        CsqlConfig queryConfig
    }

    call csql.CsqlQuery as CsqlQuery {
        input:
            apiProjectId = apiProjectId,
            credentials = credentials, 
            queryConfig = queryConfig
    }

}