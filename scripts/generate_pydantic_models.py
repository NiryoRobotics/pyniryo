import yaml
import argparse
from pathlib import Path
from typing import Any, Dict, Set

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


def json_schema_to_pydantic(
    name: str,
    schema: Dict[str, Any],
    model_store: Dict[str, str],
    known_models: Set[str],
) -> str:
    """Generate Pydantic model from schema and store any sub-models."""
    name = pascalcase(name)
    if name in known_models:
        return name
    known_models.add(name)

    lines = []

    if schema.get("type") == "array":
        lines.append(f'class {name}(RootModel):')
        lines.append(f'    root = List[{schema["items"]}]')
        properties = schema.get('items', {}).get('properties', {})
    elif schema.get("type") == "object":
        lines.append(f'class {name}(BaseModel):')
        properties = schema.get("properties", {})
    else:
        raise ValueError(f"Unsupported schema type for {name}: {schema.get('type')}")

    if not properties:
        lines.append("    pass")
        model_store[name] = "\n".join(lines)
        return name

    for prop_name, prop_schema in properties.items():
        if "$ref" in prop_schema:
            # Should already be resolved in bundle_yaml
            raise ValueError("Unresolved $ref found in schema")

        prop_type_hint = prop_schema.get("type", "Any")

        # Nested object
        if prop_type_hint == "object":
            nested_name = pascalcase(prop_name)
            json_schema_to_pydantic(nested_name, prop_schema, model_store, known_models)
            prop_type = nested_name
        # Array of objects
        elif prop_type_hint == "array":
            print(f"Processing array for property '{prop_name}' with schema: {prop_schema}")
            items = prop_schema.get("items", {})
            item_type = items.get("type", "Any")

            if item_type == "object":
                nested_name = pascalcase(prop_name)
                json_schema_to_pydantic(nested_name, items, model_store, known_models)
                prop_type = f"List[{nested_name}]"
            else:
                base_type = map_type(item_type)
                prop_type = f"List[{base_type}]"
        else:
            prop_type = map_type(prop_type_hint)

        lines.append(f"    {prop_name}: {prop_type}")

    model_store[name] = "\n".join(lines)
    return name


def generate_models(parsed_yaml: Dict[str, Any]) -> str:
    from collections import OrderedDict

    components = parsed_yaml.get("components", {})
    messages = components.get("messages", {})

    output = [
        "from pydantic import BaseModel, RootModel",
        "from typing import Any, List, Dict, Optional\n",
    ]

    model_store = OrderedDict()
    known_models = set()

    for msg_name, msg_def in messages.items():
        payload = msg_def.get("payload", {})
        json_schema_to_pydantic(msg_name, payload, model_store, known_models)

    output.extend(model_store.values())
    return "\n\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Generate Pydantic models from AsyncAPI YAML.")
    parser.add_argument("yaml_file", type=Path, help="Path to asyncapi.yaml")
    parser.add_argument("-o", "--output", default="models.py", help="Output Python file")
    args = parser.parse_args()

    parsed = bundle_yaml(args.yaml_file)
    model_code = generate_models(parsed)

    Path(args.output).write_text(model_code)
    print(f"✅ Models written to {args.output}")


if __name__ == "__main__":
    main()
