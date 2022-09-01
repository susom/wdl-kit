version development

# Struct containing common config passed around to all workflows
struct GcpConfig {
    # Optional credentials JSON file for API calls
    File? credentials
    # Optional default project ID associated with API calls
    String apiProjectId
}

struct SlackConfig {
  String tokenUri
  String channel
  String message
}

struct MailerConfig {
  String apiUrl
  String apiUri
  String mailTo
  String message
  String subject
  String sender
}

task StringReplace {
    input {
        String toReplace
        File? replacements
        String dockerImage = "wdl-kit:1.2.2"
    }

    command <<<
        python3 <<CODE
        import json
        strToReplace = "~{toReplace}"
        with open("~{replacements}") as replacements_file:
            replacements = json.load(replacements_file)
            for key, value in replacements.items():
                strToReplace = strToReplace.replace("{"+key+"}", value)
        print(strToReplace)
        CODE
    >>>

    runtime {
        docker: dockerImage
    }

    output {
        String replacedString = read_string(stdout())
    }
}

task Slacker {
    input {
        SlackConfig? slackConfig
        String replacedMessage
        String dockerImage = "wdl-kit:1.2.2"
    }

    parameter_meta {
        slackConfig: {description: "The config for slack including the token uri, channel and message, specififed in the input.json file"}
        config: {description: "Specify the GCP config to use to acquire the slack API token", category: "required"}
    }

    command <<<
        slacker ~{"--slack_uri=" + select_first([slackConfig]).tokenUri} ~{"--channel=" + select_first([slackConfig]).channel} ~{"--message=" + "\"" + replacedMessage + "\""}
    >>>
    
    runtime {
        docker: dockerImage
    }
}

task Mailer {
    input {
        MailerConfig? mailerConfig
        String replacedMessage
        String dockerImage = "wdl-kit:1.2.2"
    } 

    command <<<
        mailer ~{"--mailgun_api_url=" + select_first([mailerConfig]).apiUrl} ~{"--mailgun_api_uri=" + select_first([mailerConfig]).apiUri} ~{"--mailto=" + "\"" + select_first([mailerConfig]).mailTo + "\"" }  ~{"--message=" + "\"" + replacedMessage + "\""} ~{"--subject=" + "\"" + select_first([mailerConfig]).subject + "\""} ~{"--sender=" + select_first([mailerConfig]).sender}
    >>>

    runtime {
        docker: dockerImage
    }
}

task ZipCompress {
    input {
        Array[File] sourceFiles
        String destinationFile
        Int cpu = 1
        String memory = "1024MB"
        String dockerImage = "wdl-kit:1.2.2"
    }

    command {
        set -e -o pipefail
        mkdir -p "$(dirname ~{destinationFile})"
        zip -j ~{destinationFile} ~{sep(' ',sourceFiles)}
    }

    output {
        File zipFile = destinationFile
    }

    runtime {
        docker: dockerImage
        cpu: cpu
        memory: memory
    }
}

# Simple S3 single file uploader
task S3Upload {
    input {
        # AWS credentials
        String awsAccessKey
        String awsSecretAccessKey
        # Source file to upload
        File source
        # Bucket destination
        String bucket
        # Destination name for object in bucket
        String key
    }

    String uri = "s3://~{bucket}/~{key}"

    command {
        export AWS_ACCESS_KEY_ID=~{awsAccessKey}
        export AWS_SECRET_ACCESS_KEY=~{awsSecretAccessKey}
        set -e -o pipefail
        aws s3 --quiet cp ~{source} ~{uri} && aws s3api head-object --bucket ~{bucket} --key ~{key} --output json
    }

    output {
        File metadata = stdout()
    }

    runtime {
        docker: "amazon/aws-cli:2.7.7"
    }
}