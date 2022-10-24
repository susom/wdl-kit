version development

import "../src/main/wdl/cloudsql.wdl" as csql
import "../src/main/wdl/structs.wdl"

workflow connectToPostgres {
     input {
        CsqlConfig queryConfig
    }

    call csql.CsqlQuery as CsqlQuery {
        input:
            queryConfig
    }

}