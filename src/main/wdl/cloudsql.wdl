version development

# WDL Wrapper for the CloudSQL Python utility
import "structs.wdl"

task CreateInstance {
    parameter_meta {
        projectId: { description: "Project to create the instance in" }
        credentials: { description: "Optional JSON credential file" }
        instanceName: { description: "Name of the database instance to create" }
        region: { description: "Region in GCP that the instance should be created in" }
        databaseVersion: { description: "The type of database instance to create" }
        tier: { description: "Specifications for the machine that the instance will be hosted on" }
        enableIpv4: { description: "Setting this to true will give the instance a public IP address" }
        requireSSL: { description: "This will require an SSL connection to connect to the db istance" }
        privateNetwork: { description: "The private network that is used when allocating the instance a private IP address" }
    }

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

        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.3.2-dev"
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
        name: instanceName,
        region: region,
        databaseVersion: databaseVersion,
        settings: settings
    }

    File configFile = write_json(toCreate)

    command {
        csql ${"--project_id=" + projectId} ${"--credentials=" + credentials} ${"--config=" + configFile} instance_insert
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

task DeleteInstance {
    parameter_meta {
        projectId: { description: "Project to delete the instance in" }
        credentials: { description: "Optional JSON credential file" }
        instanceName: { description: "Name of the database instance to delete" }
    }

    input {
        String projectId
        File? credentials
        String instanceName


        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.3.2-dev"
    }

    command {
        csql ${"--project_id=" + projectId} ${"--credentials=" + credentials} ${"--instance=" + instanceName} instance_delete
    }

    output {
      String deleteInstance = read_string("delete_instance.json")
      File results = stdout()
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}


task CreateDatabase {
    parameter_meta {
        projectId: { description: "Project to create the database in" }
        credentials: { description: "Optional JSON credential file" }
        instanceName: { description: "Instance to create the database in" }
        databaseId: { description: "Name of the database to create" }
        kind: { description: "This is always sql#database" }
        charset: { description: "The Cloud SQL charset value" }
        collation: { description: "he Cloud SQL collation value" }
        compatibilityLevel: { description: "The version of SQL Server with which the database is to be made compatible" }
        recoveryModel: { description: "The recovery model of a SQL Server database" }
    }

    input {
        String projectId
        File? credentials
        String instanceName
        String? databaseId
        String kind = "sql#database"
        String charset = "UTF8"
        String collation = "en_US.UTF8"
        String? compatibilityLevel
        String? recoveryModel
      
        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.3.2-dev"
    }
    

    SqlserverDatabaseDetails sqlserverDatabaseDetails = object {
        compatibilityLevel: compatibilityLevel,
        recoveryModel: recoveryModel
    }

    Database toCreate = object {
        kind: kind,
        charset: charset,
        collation: collation,
        name: databaseId,
        instance: instanceName,
        project: projectId,
        sqlserverDatabaseDetails: sqlserverDatabaseDetails
    }

    File configFile = write_json(toCreate)

    command {
        csql ${"--project_id=" + projectId} ${"--credentials=" + credentials} ${"--instance=" + instanceName} ${"--database=" + databaseId} ${"--config=" + configFile} database_insert
    }

    output {
      Database createdDatabase = read_json("database.json")
      File results = stdout()
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}

task DeleteDatabase {
    parameter_meta {
        projectId: { description: "Project to delete the instance in" }
        credentials: { description: "Optional JSON credential file" }
        instanceName: { description: "Instance to delete the database in" }
        databaseId: { description: "Name of the database to delete" }
    }

    input {
        String projectId
        File? credentials
        String instanceName
        String? databaseId

        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.3.2-dev"
    }

    command {
        csql ${"--project_id=" + projectId} ${"--credentials=" + credentials} ${"--instance=" + instanceName} ${"--database=" + databaseId} database_delete
    }

    output {
      String deleteDatabase = read_string("delete_database.json")
      File results = stdout()
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}
