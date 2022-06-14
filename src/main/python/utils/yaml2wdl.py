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
