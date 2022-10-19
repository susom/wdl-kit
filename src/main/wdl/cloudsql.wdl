version development

# WDL Wrapper for the CloudSQL Python utility
import "structs.wdl"

task CreateInstance {
    parameter_meta {
        apiProjectId: { description: "Project for GCloud API" }
        credentials: { description: "Optional JSON credential file" }
        instanceProjectId: { description: "Project to create the instance in" }
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
        project: instanceProjectId,
        name: instanceName,
        region: region,
        databaseVersion: databaseVersion,
        settings: settings
    }

    command {
        csql ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} instance_insert ~{write_json(toCreate)}
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
        apiProjectId: { description: "Project for GCloud API" }
        credentials: { description: "Optional JSON credential file" }
        instanceProjectId: { description: "Project to delete the instance in" }     
        instanceName: { description: "Name of the database instance to delete" }
    }

    input {
        String apiProjectId
        File? credentials
        String instanceProjectId
        String? instanceName

        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.3.2-dev"
    }

    DatabaseInstance toDelete = object {
        project: instanceProjectId,
        name: instanceName
    }

    File configFile = write_json(toDelete)

    command {
        csql ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} instance_delete  ~{write_json(toDelete)}
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
        apiProjectId: { description: "Project for GCloud API" }
        credentials: { description: "Optional JSON credential file" }
        instanceProjectId: { description: "Project to create the database in" }    
        instanceName: { description: "Instance to create the database in" }
        databaseId: { description: "Name of the database to create" }
        kind: { description: "This is always sql#database" }
        charset: { description: "The Cloud SQL charset value" }
        collation: { description: "he Cloud SQL collation value" }
        compatibilityLevel: { description: "The version of SQL Server with which the database is to be made compatible" }
        recoveryModel: { description: "The recovery model of a SQL Server database" }
    }

    input {
        String apiProjectId
        File? credentials
        String instanceProjectId
        String? instanceName
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
        project: instanceProjectId,
        sqlserverDatabaseDetails: sqlserverDatabaseDetails
    }

    File configFile = write_json(toCreate)

    command {
        csql ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} database_insert  ~{write_json(toCreate)}
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
        apiProjectId: { description: "Project for GCloud API" }
        credentials: { description: "Optional JSON credential file" }
        instanceProjectId: { description: "Project to create the database in" }  
        instanceName: { description: "Instance to delete the database in" }
        databaseId: { description: "Name of the database to delete" }
    }

    input {
        String apiProjectId
        File? credentials
        String instanceProjectId
        String? instanceName
        String? databaseId

        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.3.2-dev"
    }

    Database toDelete = object {
        name: databaseId,
        instance: instanceName,
        project: instanceProjectId,
    }

    command {
        csql ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} database_delete  ~{write_json(toDelete)}
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
