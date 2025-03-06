version development

import "structs.wdl"

task BackupDataset {
    parameter_meta {
        apiProjectId: { description: "The project ID of the API we will be using (note: can be different than the instance project ID)" }
        credentials: { description: "Optional JSON credential file" }
        backupOptions: { description: "The backup options" }
    }

    input {
        String? apiProjectId
        File? credentials
        BackupOptions backupOptions
        
        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.9.7"
    }

    command {
        wbr ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} backup ~{write_json(backupOptions)}
        if ~{backupOptions.createHeaderFile}
        then
          wbr ${"--project_id=" + apiProjectId} ${"--credentials=" + credentials} header_file ~{write_json(backupOptions)}
        fi
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
