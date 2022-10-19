version development

import "../src/main/wdl/cloudsql.wdl" as csql

workflow CreateInstanceTest {
    input {
        String apiProjectId
        File? credentials
        String instanceProjectId
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

    output {
        DatabaseInstance testInstance = CreateInstanceTestWDL.createdInstance
    }
}