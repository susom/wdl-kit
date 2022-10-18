version development

# WDL Wrapper for the CloudSQL Python utility
import "structs.wdl"

task CreateInstance {
    parameter_meta {
        apiProjectId: { description: "The project ID of the API we will be using (note: can be different than the instance project ID)" }
        credentials: { description: "Optional JSON credential file" }
        instanceProjectId: { description: "The project ID for where the instance will be created."}
        instanceName: { description: "Name of the database instance to create" }
        region: { description: "Region in GCP that the instance should be created in" }
        databaseVersion: { description: "The type of database instance to create" }
        tier: { description: "Specifications for the machine that the instance will be hosted on" }
        enableIpv4: { description: "Setting this to true will give the instance a public IP address" }
        requireSSL: { description: "This will require an SSL connection to connect to the db istance" }
        privateNetwork: { description: "The private network that is used when allocating the instance a private IP address" }
    }

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

        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.3.0"
    }

    IpConfiguration ipConfig = object {
        ipv4Enabled: enableIpv4,
        requireSsl: requireSSL,
        privateNetwork: privateNetwork
    }

    Settings settings = object {
        tier: tier,
        ipConfiguration: ipConfig
    }

    DatabaseInstance toCreate = object {
        project: instanceProjectId,
        name: instanceName,
        region: region,
        databaseVersion: databaseVersion,
        settings: settings
    }

    command {
        csql ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} insert ~{write_json(toCreate)}
    }

    output {
      DatabaseInstance createdInstance = read_json("instance.json")
      File results = stdout()
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}