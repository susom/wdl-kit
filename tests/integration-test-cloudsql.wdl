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

    output {
        DatabaseInstance testInstance = CreateInstanceTestWDL.createdInstance
    }
}