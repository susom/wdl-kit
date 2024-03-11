from pybuilder.core import Author, use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.flake8")
# use_plugin("python.coverage")
use_plugin("python.distutils")

name = "stanford-wdl-kit"
default_task = "publish"
summary = "A WDL toolkit with a focus on ETL and Cloud integration"
version = "1.8.0"
url = "https://github.com/susom/wdl-kit"
authors = [Author("Darren Guan", "dguan2@stanford.edu"),
           Author("Joe Mesterhazy", "jmesterh@stanford.edu"),
           Author("Tyler Tollefson", "tjt8712@stanford.edu"),
           Author("Smita Limaye", "slimaye@stanford.edu"),
           Author("Jay Chen", "jchen313@stanford.edu")
        ]
maintainers = [Author(
    "Research IT: Technology & Digital Solutions, Stanford Medicine", "rit-oss-admin@stanford.edu")]
license = "Apache License, Version 2.0"

@init
def initialize(project):
    project.set_property('distutils_console_scripts', [
        "wbq = gcp.bigquery:main",
        "wgcs = gcp.gcs:main",
        "csql = gcp.cloudsql:main",
        "wbr = utils.backup:main",
        "yaml2wdl = utils.yaml2wdl:main",
        "slacker = utils.slacker:main",
        "mailer = utils.mailer:main"
    ])
    project.set_property("distutils_readme_file", "SUMMARY.md")
    project.set_property("distutils_readme_description", True)
    project.set_property("distutils_description_overwrite", True)
    project.depends_on_requirements("requirements.txt")
    project.set_property("distutils_classifiers", [
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License"])
