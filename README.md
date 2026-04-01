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

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and builds.

Create docker image (for use in WDL workflows):

```bash
make docker
```

Install locally for development (creates a `.venv` and installs all dependencies):

```bash
make install
```

Build a distributable wheel/sdist:

```bash
make build
```

You can also install directly from GitHub:

```bash
uv pip install git+https://github.com/susom/wdl-kit
```

Or install directly from PyPI:

```bash
uv pip install stanford-wdl-kit
```

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
      docker: "wdl-kit:1.9.7"
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
Requires Python 3.11 or higher. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) to manage the project environment:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

uv will automatically create and manage a `.venv` virtual environment when you run `uv sync` or `make install`.

## Release process
This package uses `bump2version` to keep version numbers consistent. For example, to bump the minor version number on the dev branch:

```bash
git checkout dev
git pull
uvx bump2version minor
```

This will update the version in `pyproject.toml`, `Dockerfile`, `Makefile`, `cloudbuild.yaml`, and the relevant WDL files. Publish to PyPI with:

```bash
make publish
```
