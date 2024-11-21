# WDL-kit
## A WDL toolkit with a focus on ETL and Cloud integration

WDL-kit is a collection of dockerized utilities to simplify the creation of ETL-like workflows in the Workflow Definition Language. 

## Features

* YAML-to-WDL
  
  Converts .yaml files into .wdl tasks. This is primarily a workaround for the WDL language not supporting multi-line strings, which is problematic for SQL ETL workflows. 

* Google Cloud

  Wrappers for BigQuery, Google Cloud Storage, etc. 

* Slack

  Wrapper for sending Slack messages

* MailGun

  Wrapper for sending mail via MailGun


## Building WDL-kit

Create docker image (for use in WDL workflows):

`make docker`

Install into local pip: (installs yaml2wdl, etc.)

`make install`

You can also build & install directly from GitHub:

`pip3 install git+https://github.com/susom/wdl-kit`

Or install directly from PyPi:

`pip3 install stanford-wdl-kit`

---
## Background
We needed a method of calling GCP API's via WDL. Most WDL workflow engines require commands to be dockerized, so the natural inclination
would be to write WDL tasks that call the command line utilities from the `google/cloud-sdk` docker image. 

### Cloud-SDK Docker Example
If we wanted a task to create datasets in BigQuery (using the Google cloud-sdk docker image) this would be a 
natural implementation:

```WDL
task CreateDataset {
    input {
      File credentials
      String projectId
      String dataset
      String description = ""
    }
    command {
      gcloud auth activate-service-account --key-file=~{credentials}
      bq --project_id=~{projectId} mk --description="~{description}" ~{dataset}
    }
    runtime {
      docker: "google/cloud-sdk:367.0.0"
    }
}
```

This is a good start, however the `bq mk` command has over 70(!) different flags. If we wanted to support all possible
options, the task above would be incredibly long and complex. Even then, some functionality would still not be available.
What if you wanted to specify the ACL's for the dataset that is being created? The GCP API supports this, but the `bq mk` command does not. 

Other disadvantages:
* You need an input String for every new field or feature added to the task. That list will quickly grow. 
* What is the return value for this task? The `bq mk` command will tell you if the dataset was created successfully (or not) but that's it. Ideally
WDL tasks should return either data or a data reference (in this case). We could return the dataset name again as an output String, but that's about it.
* The task is dependent on the arguments for `bq mk`. Future versions of the `bq` command may break the task. 
* All parameters need to be sensitive to shell escaping rules

### WDL-kit Example

Here is an example of the same task, this time using WDL-kit:

```WDL
task CreateDataset {
    input {
      File? credentials
      String projectId
      Dataset dataset
    }
    CreateDatasetConfig config = object {
      credentials: credentials,
      projectId: projectId,
      dataset: dataset
    }
    command {
      wbq create_dataset ~{write_json(config)}
    }
    output {
      Dataset createdDataset = read_json(stdout())
    }
    runtime {
      docker: "wdl-kit:1.9.6"
    }
}
```

Advantages
* The task supports **every** feature of the [datasets.insert method](https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets/insert) using only three inputs.
* Input and output are valid GCP [Dataset resources](https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets).
    * The caller has access to all fields of the created resource, eg. `CreateDataset.createdDataset.selfLink`
* The Input and Output are Structs, not Strings containing JSON. The fields are typed and less prone to error.  

WDL Dataset struct:

```WDL
# https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets
struct Dataset {
  String? kind
  String? etag
  String? id
  String? selfLink
  DatasetReference datasetReference
  String? friendlyName
  String? description
  String? defaultTableExpirationMs
  String? defaultPartitionExpirationMs
  Map[String, String]? labels
  Array[AccessEntry]? access
  String? creationTime
  String? lastModifiedTime
  String? location
  EncryptionConfiguration? defaultEncryptionConfiguration
  Boolean? satisfiesPzs
  String? type
}
```

Note that DatasetReference is another Struct, just like the actual GCP [Dataset](https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets) resource.

#### Python code
Here is the entirety of the `create_dataset` method in wdl-kit:

```python
def create_dataset(config: CreateDatasetConfig) -> dict:
    """
    Creates a dataset (Dataset), if there is a dataset already of the same name it can be deleted
    or have specified fields updated with new values
    """
    client = bigquery.Client(project=config.projectId)
    dataset = bigquery.Dataset.from_api_repr(config.dataset)
    new_dataset = client.create_dataset(dataset, exists_ok=config.existsOk, timeout=30)
    return new_dataset.to_api_repr()
```

The method is 4 lines of code(!):
* Authenticate to BigQuery
* Create a Dataset object from the input JSON (WDL Dataset Struct serialized as JSON)
* Materialize the Dataset object by calling the create_dataset method. 
* Return the created Dataset resource (which WDL Serializes back to a Dataset Struct)

The GCP Python `from_api_repr` and `to_api_repr` methods do all the heavy lifting for us.
---
#### Notes
If your terminal in VSCode has "venv" in front of it do the following:
* Upgrade to python 3.9.9 via pyenv
* Add the following into your .bashrc
```shell
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if command -v pyenv 1>/dev/null 2>&1; then
 eval "$(pyenv init -)"
fi
export PATH=$(pyenv root)/shims:$PATH
```

## Release process
This package uses 'bumpversion' to keep version numbers consistent. For example, to bump the minor version number on the dev branch (say after a new release version)... 
```bash
git checkout dev
git pull
bumpversion minor
```
and you will see the changed versions reflected locally in git:
```bash
	modified:   .bumpversion.cfg
	modified:   Dockerfile
	modified:   Makefile
	modified:   README.md
	modified:   build.py
	modified:   cloudbuild.yaml
	modified:   src/main/wdl/bigquery.wdl
	modified:   src/main/wdl/common.wdl
	modified:   src/main/wdl/gcs.wdl
	modified:   src/main/wdl/structs.wdl
```
