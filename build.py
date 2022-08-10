from pybuilder.core import Author, use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.flake8")
#use_plugin("python.coverage")
use_plugin("python.distutils")


name = "wdl-kit"
default_task = "publish"
summary = "A WDL toolkit with a focus on ETL and Cloud integration"
version = "1.1.0"
url = "https://github.com/susom/wdl-kit"
authors = [Author("SHC Research IT Team Sapphire","rit-oss-admin@stanford.edu"),
           Author("Joe Mesterhazy","jmesterh@stanford.edu"),
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

    project.set_property("distutils_readme_description", True)
    project.set_property("distutils_description_overwrite", True)
    project.depends_on_requirements("requirements.txt")