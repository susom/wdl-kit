#   -*- coding: utf-8 -*-
import os
from pybuilder.core import use_plugin, init, task

use_plugin("python.core")
use_plugin("python.flake8")
# use_plugin("python.unittest")
# use_plugin("python.coverage")
use_plugin("python.distutils")

name = "wdl-kit"
default_task = "publish"
description = "A WDL toolkit with a focus on ETL and Cloud integration"
version = "1.0.0"


@init
def initialize(project):
    project.set_property('distutils_console_scripts', [
        "wbq = gcp.bigquery:main",
        "wgcs = gcp.gcs:main",
        "yaml2wdl = utils.yaml2wdl:main",
        "slacker = utils.slacker:main",
        "mailer = utils.mailer:main"
    ])

    # -- In case resources are ever needed, this is how to include them
    # -- use_plugin("copy_resources")
    # project.get_property("copy_resources_glob").append(
    #     "src/main/resources/*.txt")
    # project.set_property("copy_resources_target", "$dir_dist")
    # # In docker this is /usr/local/share/wdl-kit
    # project.install_file("share/wdl-kit", "src/main/resources/example.txt")
