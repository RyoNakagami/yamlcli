import sys
import yaml
import json
import argparse


class RegmonkeyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(RegmonkeyDumper, self).increase_indent(flow, False)


def yaml_to_json(file_path, indent):
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)

    if indent <= 0:
        print(json.dumps(data))
    else:
        print(json.dumps(data, indent=indent))


def json_to_yaml(file_path, indent):
    with open(file_path, "r") as f:
        data = json.load(f)

    if indent <= 0:
        print(yaml.safe_dump(data, sort_keys=False))
    else:
        # Dump YAML with 2-space indentation for lists
        print(
            yaml.dump(
                data,
                Dumper=RegmonkeyDumper,
                sort_keys=False,
                default_flow_style=False,
                indent=indent,
            )
        )


def main():
    parser = argparse.ArgumentParser(description="Convert YAML ↔ JSON")
    parser.add_argument("file", help="Input file path")
    parser.add_argument("--to-json", action="store_true", help="Convert YAML to JSON")
    parser.add_argument("--to-yaml", action="store_true", help="Convert JSON to YAML")
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentation level for JSON output (default: 2)",
    )
    args = parser.parse_args()

    if args.to_json == args.to_yaml:
        print("Error: Specify exactly one of --to-json or --to-yaml", file=sys.stderr)
        sys.exit(1)

    try:
        if args.to_yaml:
            json_to_yaml(args.file, args.indent)
        else:
            yaml_to_json(args.file, args.indent)
    except FileNotFoundError:
        print(f"Error: File not found - {args.file}", file=sys.stderr)
        sys.exit(1)
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        print(f"Error: Parsing failed - {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
