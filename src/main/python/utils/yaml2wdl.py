# Copyright 2022 The Board of Trustees of The Leland Stanford Junior University.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import yaml
import json
import sys
import re

template = """version {version}

task GetYaml {{{inputs}
  command {{}}
  output {{
    File yaml = write_lines([{yaml}])
  }}
}}"""


def main(args=None):
    """
    A simple YAML to WDL pre-processor. Creates a .wdl file from .yaml input, containing
    a single task 'GetYaml' which returns an output File 'yaml' which contains the YAML
    converted JSON. Use this for embedding large input files in your WDL workflows which
    you want as part of the workflow code (not as workflow inputs).

    Supports simple string substitution. If the input yaml has ~{foo} then the GetYaml
    task will have an input variable called "foo" available for substition.

    This exists to address two limitations of WDL:
    * WDL can only import .wdl files
    * WDL doesn't support multi-line strings (especially painful for SQL ETL code)

    """
    parser = argparse.ArgumentParser(description="YAML to WDL pre-processor")

    parser.add_argument('--version', type=str, default='development',
                        help='WDL document version (default: development)')
    parser.add_argument('yaml_in', type=argparse.FileType(
        'r'), help='Input YAML file')
    parser.add_argument('wdl_out', type=argparse.FileType(
        'w'), help='Output WDL file')

    args = parser.parse_args()

    input_clause = ""
    input_vars = []
    with args.yaml_in as yaml_in:
        with args.wdl_out as wdl_out:
            data = yaml.load(yaml_in, Loader=yaml.FullLoader)
            jsons = json.dumps(data)

            # Look for simple WDL string replacement expressions
            inputs = re.findall(r'~{[a-zA-Z]+[a-zA-Z0-9_]*}', jsons)
            for input in inputs:
                input_vars.append("  String {0}".format(input[2:-1]))

            if len(input_vars) > 0:
                input_clause = "\n  input {{\n  {vars}\n  }}".format(
                    vars="\n  ".join(sorted(set(input_vars))))

            wdl_out.write(template.format(
                version=args.version, yaml=json.dumps(jsons), inputs=input_clause))


if __name__ == '__main__':
    sys.exit(main())
