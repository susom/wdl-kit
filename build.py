from pybuilder.core import Author, use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.flake8")
#use_plugin("python.coverage")
use_plugin("python.distutils")


name = "wdl-kit"
default_task = "publish"
summary = "A WDL toolkit with a focus on ETL and Cloud integration"
version = "1.2.0"
description = "# WDL-kit\n## A WDL toolkit with a focus on ETL and Cloud integration\nWDL-kit is a collection of dockerized utilities to simplify the creation of ETL-like workflows in the Workflow Definition Language. "
url = "https://github.com/susom/wdl-kit"
authors = [Author("Darren Guan", "dguan@stanford.edu"),   
           Author("Joe Mesterhazy","jmesterh@stanford.edu"),
           Author("SHC Research IT Team Sapphire","rit-oss-admin@stanford.edu"),
           Author("Tyler Tollefson", "ttollefson45@gmail.com")
          ]
maintainers = [Author("SHC Research IT Team Sapphire","rit-oss-admin@stanford.edu")]
license = "Apache License, Version 2.0"

@init
def initialize(project):
    project.set_property('distutils_console_scripts', [
        "wbq = gcp.bigquery:main",
        "wgcs = gcp.gcs:main",
        "yaml2wdl = utils.yaml2wdl:main",
        "slacker = utils.slacker:main",
        "mailer = utils.mailer:main"
    ])
    # TODO: Find a different way to do this
    project.set_property("distutils_description_overwrite", True)
    project.depends_on_requirements("requirements.txt")