import yaml  # type: ignore[import-untyped]
import json


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
