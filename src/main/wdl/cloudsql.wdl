version development

# WDL Wrapper for the CloudSQL Python utility
import "structs.wdl"

task CreateInstance {
    parameter_meta {
        apiProjectId: { description: "The project ID of the API we will be using (note: can be different than the instance project ID)" }
        credentials: { description: "Optional JSON credential file" }
        databaseInstance: { description: "The database instance to create" }
    }

    input {
        String? apiProjectId
        File? credentials
        DatabaseInstance databaseInstance
        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.3.0"
    }

    command {
        csql ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} instance_insert ~{write_json(databaseInstance)}
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
        apiProjectId: { description: "The project ID of the API we will be using (note: can be different than the instance project ID)" }
        credentials: { description: "Optional JSON credential file" }
        databaseInstance: { description: "The database instance to delete" }
    }

    input {
        String? apiProjectId
        File? credentials
        DatabaseInstance databaseInstance

        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.3.0"
    }

    command {
        csql ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} instance_delete  ~{write_json(databaseInstance)}
    }

    output {
      File deleteInstance = "delete_instance.json"
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
        apiProjectId: { description: "The project ID of the API we will be using (note: can be different than the instance project ID)" }
        credentials: { description: "Optional JSON credential file" }
        database: { description: "The database to create" }
    }

    input {
        String? apiProjectId
        File? credentials
        Database database
      
        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.3.0"
    }
    
    command {
        csql ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} database_insert  ~{write_json(database)}
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
        apiProjectId: { description: "The project ID of the API we will be using (note: can be different than the instance project ID)" }
        credentials: { description: "Optional JSON credential file" }
        database: { description: "The database to delete" }
    }

    input {
        String? apiProjectId
        File? credentials
        Database database

        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.3.0-slimaye14"
    }

    command {
        csql ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} database_delete  ~{write_json(database)}
    }

    output {
      File deleteDatabase = "delete_database.json"
      File results = stdout()
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}

task CsqlQuery { 
    parameter_meta {
        apiProjectId: { description: "The project ID of the API we will be using (note: can be different than the instance project ID)" }
        credentials: { description: "Optional JSON credential file" }
        queryConfig: { description: "CsqlConfig object containing database connection details and query" }
    }
    input {
        String? apiProjectId
        File? credentials
        CsqlConfig queryConfig

        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.3.0-slimaye15"
    }


    command {
        csql ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} query ~{write_json(queryConfig)}
    }

    output {
        File stdout = stdout()
        File stderr = stderr()
    }

    runtime {
        docker: dockerImage
        cpu: cpu
        memory: memory
    }
}

