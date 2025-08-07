import argparse
from pathlib import Path

import yaml
from caseconverter import pascalcase


def get_yaml_from_path(yaml_content, path: str):
    parts = path.split("/")
    current = yaml_content
    for part in parts:
        current = current[part]
    return current


def bundle_yaml(file_path: Path):
    yaml_root = yaml.safe_load(file_path.read_text())

    def resolve(yaml_data, ref_dir: Path):
        if isinstance(yaml_data, dict):
            if '$ref' in yaml_data:
                ref = yaml_data['$ref']
                if ref.startswith('#/'):
                    return resolve(get_yaml_from_path(yaml_root, ref[2:]), ref_dir)
                elif (ref_path := ref_dir.joinpath(ref)).is_file():
                    return resolve(yaml.safe_load(ref_path.read_text()), ref_path.parent)
                else:
                    raise ValueError(f"Unsupported reference format: {ref}")
            else:
                return {key: resolve(value, ref_dir) for key, value in yaml_data.items()}
        elif isinstance(yaml_data, list):
            return [resolve(item, ref_dir) for item in yaml_data]
        else:
            return yaml_data

    return resolve(yaml_root, file_path.parent)


def map_type(json_type: str) -> str:
    return {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "List",
        "object": "Dict",
    }.get(json_type, "Any")


def parse(name: str, schema: dict, model_store: dict, known_models: set) -> str:
    """Generate Pydantic model from schema and store any sub-models."""
    schema_type = schema.get('type')
    if schema_type == 'object':
        parse_object(name, schema, model_store, known_models)
    elif schema_type == 'array':
        parse_array(name, schema, model_store, known_models)


def parse_object(obj_name: str, obj_spec: dict, model_store: dict, known_models: set):
    lines = [f'class {obj_name}(BaseModel):']
    for prop_name, prop_spec in obj_spec.get('properties', {}).items():
        prop_type = map_type(prop_spec.get('type'))
        if prop_type == 'object':
            sub_model_name = parse_object(pascalcase(prop_name), prop_spec, model_store, known_models)
            lines.append(f'    {prop_name}: Optional[{sub_model_name}] = None')
        else:
            lines.append(f'    {prop_name}: Optional[{prop_type}] = None')


def parse_array(arr_name: str, arr_spec: dict, model_store: dict, known_models: set):
    ...


def main():
    parser = argparse.ArgumentParser(description="Generate Pydantic models from AsyncAPI YAML.")
    parser.add_argument("yaml_file", type=Path, help="Path to asyncapi.yaml")
    parser.add_argument("-o", "--output", default="models.py", type=Path, help="Output Python file")
    args = parser.parse_args()

    model_store = {}
    known_models = set()
    asyncapi_spec = bundle_yaml(args.yaml_file)
    for message in asyncapi_spec['components']['messages'].values():
        name = message.get('name')
        if name in known_models:
            continue
        payload = message.get('payload')

        if not isinstance(payload, dict):
            raise ValueError(f"Message with non-dict payload: {message['name']}")

        payload_type = payload.get('type')
        if payload_type == 'object':
            parse_object(name, payload, model_store, known_models)
        elif payload_type == 'array':
            print(f"Message with array payload: {message['name']}")
        else:
            print(f"Message with unknown payload type: {message['name']}")

        known_models.add(name)
