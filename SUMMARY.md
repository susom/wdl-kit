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