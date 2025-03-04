version development

import "structs.wdl"

task RestoreDataset {
    parameter_meta {
        apiProjectId: { description: "The project ID of the API we will be using (note: can be different than the instance project ID)" }
        credentials: { description: "Optional JSON credential file" }
        restoreOptions: { description: "The restore options" }
    }

    input {
        String? apiProjectId
        File? credentials
        RestoreOptions restoreOptions
        
        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.9.7"
    }

    command {
        wbr ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} restore ~{write_json(restoreOptions)}
    }

    output {
      File results = stdout()
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}
