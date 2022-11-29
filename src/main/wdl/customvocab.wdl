version development

task CleanupCustomVocabulary {
    parameter_meta {
        infile: { description: "The cvs file containing custom vocabulary mappings before cleanup" }
    }

    input {
        File? infile
        Int cpu = 1
        String memory = "128 MB"
        String dockerImage = "wdl-kit:1.5.0"
    }

    command {
        vocabcleaner ~{infile}
    }

    output {
      File cleanFile = "outfile"
    }

    runtime {
      docker: dockerImage
      cpu: cpu
      memory: memory
    }
}