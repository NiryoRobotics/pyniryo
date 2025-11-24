#!/usr/bin/env python3
"""
AsyncAPI to Pydantic Models Generator

This script generates Pydantic models from AsyncAPI YAML specifications.
It handles $ref resolution (both local files and nested references) and
generates models following the project's conventions.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml


class RefResolver:
    """Resolves $ref references in AsyncAPI/JSON Schema documents."""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._resolution_stack: List[str] = []

    def resolve_ref(self, ref_path: str, current_file_path: Path) -> Any:
        """
        Resolve a $ref reference.
        
        Args:
            ref_path: The $ref value (e.g., './user.yaml#/components/schemas/User')
            current_file_path: Path to the file containing this $ref
            
        Returns:
            The resolved schema
        """
        # Check if it's an internal reference
        if ref_path.startswith('#/'):
            # Internal reference - need to resolve from root document
            cache_key = f"{current_file_path}::{ref_path}"
            if cache_key in self._cache:
                return self._cache[cache_key]

            # Load the current file and navigate to the reference
            with open(current_file_path, 'r') as f:
                document = yaml.safe_load(f)

            resolved = self._navigate_path(document, ref_path[2:])
            self._cache[cache_key] = resolved
            return resolved

        # External reference
        if '#' in ref_path:
            file_path, json_path = ref_path.split('#', 1)
            json_path = json_path.lstrip('/')
        else:
            file_path = ref_path
            json_path = ''

        # Resolve file path relative to current file
        if file_path:
            target_file = (current_file_path.parent / file_path).resolve()
        else:
            target_file = current_file_path

        # Check for circular references
        ref_id = f"{target_file}::{json_path}"
        if ref_id in self._resolution_stack:
            raise ValueError(f"Circular reference detected: {ref_id}")

        # Check cache
        if ref_id in self._cache:
            return self._cache[ref_id]

        # Load and resolve
        self._resolution_stack.append(ref_id)
        try:
            with open(target_file, 'r') as f:
                document = yaml.safe_load(f)

            if json_path:
                resolved = self._navigate_path(document, json_path)
            else:
                resolved = document

            # Recursively resolve any nested $refs
            resolved = self.resolve_all_refs(resolved, target_file)

            self._cache[ref_id] = resolved
            return resolved
        finally:
            self._resolution_stack.pop()

    def resolve_all_refs(self, schema: Any, current_file_path: Path) -> Any:
        """
        Recursively resolve all $ref in a schema.
        
        Args:
            schema: The schema to resolve
            current_file_path: Path to the file containing this schema
            
        Returns:
            The schema with all $refs resolved
        """
        if isinstance(schema, dict):
            if '$ref' in schema:
                return self.resolve_ref(schema['$ref'], current_file_path)

            return {key: self.resolve_all_refs(value, current_file_path) for key, value in schema.items()}
        elif isinstance(schema, list):
            return [self.resolve_all_refs(item, current_file_path) for item in schema]
        else:
            return schema

    @staticmethod
    def _navigate_path(document: Dict[str, Any], path: str) -> Any:
        """Navigate a JSON pointer path in a document."""
        parts = path.split('/')
        current = document

        for part in parts:
            if not part:
                continue
            if isinstance(current, dict):
                current = current[part]
            elif isinstance(current, list):
                current = current[int(part)]
            else:
                raise ValueError(f"Cannot navigate to {path}")

        return current


class SchemaParser:
    """Parse AsyncAPI 3.0 specifications and extract schemas."""

    def __init__(self, file_path: Path, resolver: RefResolver):
        self.file_path = file_path
        self.resolver = resolver
        self.asyncapi_spec: Dict[str, Any] = {}

    def parse(self) -> None:
        """Parse the AsyncAPI file."""
        with open(self.file_path, 'r') as f:
            self.asyncapi_spec = yaml.safe_load(f)

        # Validate AsyncAPI version
        version = self.asyncapi_spec.get('asyncapi', '')
        if not version.startswith('3.'):
            print(f"Warning: This script supports AsyncAPI 3.0. Found version: {version}", file=sys.stderr)

    def get_all_schemas(self) -> Dict[str, Any]:
        """
        Extract all schemas from AsyncAPI 3.0 spec.
        
        Returns:
            Dictionary mapping schema names to their definitions
        """
        schemas = {}
        schema_refs: Dict[str, Path] = {}  # Track schema names to their file paths

        # Extract from components/schemas (direct schema definitions)
        if 'components' in self.asyncapi_spec and 'schemas' in self.asyncapi_spec['components']:
            for name, schema in self.asyncapi_spec['components']['schemas'].items():
                resolved_schema = self.resolver.resolve_all_refs(schema, self.file_path)
                schemas[name] = resolved_schema

        # Extract from components/messages (AsyncAPI 3.0)
        # Messages in AsyncAPI 3.0 can be external files with payload refs
        if 'components' in self.asyncapi_spec and 'messages' in self.asyncapi_spec['components']:
            for msg_name, message_ref in self.asyncapi_spec['components']['messages'].items():
                # Messages are typically external refs in AsyncAPI 3.0
                if isinstance(message_ref, dict) and '$ref' in message_ref:
                    # Resolve the message file
                    message = self.resolver.resolve_ref(message_ref['$ref'], self.file_path)
                    # Get the message file path for relative resolution
                    message_file_path = self._get_ref_file_path(message_ref['$ref'], self.file_path)

                    if isinstance(message, dict) and 'payload' in message:
                        payload = message['payload']
                        # Payload can be a $ref or inline schema
                        if isinstance(payload, dict):
                            if '$ref' in payload:
                                # Track the schema file for nested ref extraction
                                schema_file = self._get_ref_file_path(payload['$ref'], message_file_path)
                                # Resolve payload ref relative to the message file (without resolving nested refs yet)
                                schema = self.resolver.resolve_ref(payload['$ref'], message_file_path)

                                # Extract schema name from file path or message
                                schema_name = message.get('name', msg_name)
                                if schema_name not in schemas:
                                    schema_refs[schema_name] = schema_file
                                    # Store the unresolved schema temporarily
                                    schemas[schema_name] = schema
                            else:
                                # Inline payload schema
                                schema = self.resolver.resolve_all_refs(payload, message_file_path)
                                schema_name = message.get('name', msg_name)
                                if schema_name not in schemas:
                                    schemas[schema_name] = schema
                elif isinstance(message_ref, dict):
                    # Inline message definition
                    if 'payload' in message_ref:
                        payload = self.resolver.resolve_all_refs(message_ref['payload'], self.file_path)
                        if isinstance(payload, dict) and ('properties' in payload or 'type' in payload):
                            schemas[msg_name] = payload

        # Extract nested schema references
        # Go through all schemas and find $refs to external schema files
        self._extract_nested_schemas(schemas, schema_refs)

        # Now resolve all refs in all schemas
        for name, schema in list(schemas.items()):
            if name in schema_refs:
                schemas[name] = self.resolver.resolve_all_refs(schema, schema_refs[name])
            else:
                schemas[name] = self.resolver.resolve_all_refs(schema, self.file_path)

        return schemas

    def _extract_nested_schemas(self, schemas: Dict[str, Any], schema_refs: Dict[str, Path]) -> None:
        """Extract schemas that are referenced from within other schemas."""
        processed_files: Set[str] = set()

        def extract_refs_from_schema(schema: Any, current_file: Path) -> None:
            """Recursively extract schema references."""
            if isinstance(schema, dict):
                if '$ref' in schema:
                    ref = schema['$ref']
                    if not ref.startswith('#'):
                        # External file reference
                        ref_file = self._get_ref_file_path(ref, current_file)
                        ref_file_str = str(ref_file)

                        if ref_file_str not in processed_files:
                            processed_files.add(ref_file_str)
                            # Load the referenced schema
                            try:
                                with open(ref_file, 'r') as f:
                                    ref_schema = yaml.safe_load(f)

                                # Extract schema name from file name
                                schema_name = ref_file.stem  # e.g., 'Point' from 'Point.yaml'

                                if schema_name not in schemas:
                                    schemas[schema_name] = ref_schema
                                    schema_refs[schema_name] = ref_file

                                # Recursively process this schema for more refs
                                extract_refs_from_schema(ref_schema, ref_file)
                            except Exception:
                                # If we can't load the file, skip it
                                pass
                else:
                    # Recursively check nested structures
                    for value in schema.values():
                        extract_refs_from_schema(value, current_file)
            elif isinstance(schema, list):
                for item in schema:
                    extract_refs_from_schema(item, current_file)

        # Extract refs from all currently known schemas
        for name, schema in list(schemas.items()):
            current_file = schema_refs.get(name, self.file_path)
            extract_refs_from_schema(schema, current_file)

    def _get_ref_file_path(self, ref: str, current_file: Path) -> Path:
        """Get the file path that a $ref points to."""
        if ref.startswith('#'):
            return current_file

        if '#' in ref:
            file_path, _ = ref.split('#', 1)
        else:
            file_path = ref

        if file_path:
            return (current_file.parent / file_path).resolve()


class TypeMapper:
    """Map JSON Schema types to Python types."""

    def __init__(self):
        self.custom_types: Set[str] = set()
        self.import_types: Set[str] = set()

    def map_type(self, schema: Dict[str, Any], name: Optional[str] = None) -> str:
        """
        Map a JSON Schema type to Python type.
        
        Args:
            schema: The JSON Schema definition
            name: Optional name for nested type generation
            
        Returns:
            Python type string
        """
        if not isinstance(schema, dict):
            return 'Any'

        # Handle enums
        if 'enum' in schema:
            return 'str'  # Will be generated as separate Enum class

        schema_type = schema.get('type', 'object')
        format_type = schema.get('format')

        # Handle arrays
        if schema_type == 'array':
            items = schema.get('items', {})
            item_type = self.map_type(items)
            self.import_types.add('List')
            return f'List[{item_type}]'

        # Handle objects
        if schema_type == 'object':
            if 'properties' in schema or 'additionalProperties' in schema:
                # Will be generated as separate model
                if name:
                    return name
                return 'Dict[str, Any]'
            else:
                self.import_types.add('Dict')
                return 'Dict[str, Any]'

        # Handle basic types
        type_map = {
            'string': self._map_string_type(format_type),
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'null': 'None',
        }

        python_type = type_map.get(schema_type, 'Any')

        # Track imports
        if python_type == 'datetime':
            self.import_types.add('datetime')
        elif python_type == 'UUID':
            self.import_types.add('UUID')
        elif python_type == 'EmailStr':
            self.import_types.add('EmailStr')

        return python_type

    def _map_string_type(self, format_type: Optional[str]) -> str:
        """Map string format to Python type."""
        if format_type == 'date-time':
            return 'datetime'
        elif format_type == 'uuid':
            return 'UUID'
        elif format_type == 'email':
            return 'EmailStr'
        elif format_type == 'byte':
            return 'bytes'
        return 'str'


class PydanticGenerator:
    """Generate Pydantic models from schemas."""

    def __init__(self, schemas: Dict[str, Any]):
        self.schemas = schemas
        self.type_mapper = TypeMapper()
        self.generated_models: List[str] = []
        self.generated_enums: List[str] = []
        self.enum_names: Set[str] = set()
        self.model_names: Set[str] = set()
        self._generation_order: List[str] = []

    def generate(self) -> str:
        """Generate all Pydantic models."""
        # First pass: identify all enums and models
        # Create a copy of items to avoid RuntimeError when dict is modified during iteration
        for name, schema in list(self.schemas.items()):
            self._collect_types(name, schema)

        # Determine generation order (dependencies first)
        self._determine_order()

        # Generate enums first
        for name, schema in self.schemas.items():
            if 'enum' in schema:
                self.generated_enums.append(self._generate_enum(name, schema))

        # Generate models in dependency order
        for name in self._generation_order:
            if name in self.schemas and 'enum' not in self.schemas[name]:
                model_code = self._generate_model(name, self.schemas[name])
                if model_code:
                    self.generated_models.append(model_code)

        return self._format_output()

    def _collect_types(self, name: str, schema: Dict[str, Any]) -> None:
        """Collect all type names that will be generated."""
        if 'enum' in schema and 'properties' not in schema:
            self.enum_names.add(name)
        elif 'type' in schema or 'properties' in schema:
            self.model_names.add(name)

        # Recursively collect nested types
        if 'properties' in schema:
            for prop_name, prop_schema in schema['properties'].items():
                if isinstance(prop_schema, dict) and 'enum' in prop_schema:
                    # Generate enum name from property name
                    enum_name = self._to_pascal_case(prop_name)
                    self.enum_names.add(enum_name)
                    # Store the enum schema for later generation
                    if enum_name not in self.schemas:
                        self.schemas[enum_name] = prop_schema

    def _determine_order(self) -> None:
        """Determine the order to generate models (dependencies first)."""
        dependencies: Dict[str, Set[str]] = {}

        # Build dependency graph
        for name, schema in self.schemas.items():
            if 'enum' in schema:
                continue
            deps = self._find_dependencies(schema)
            dependencies[name] = deps

        # Topological sort
        visited: Set[str] = set()
        temp_mark: Set[str] = set()

        def visit(node: str) -> None:
            if node in temp_mark:
                # Circular dependency - just add it
                return
            if node in visited:
                return

            temp_mark.add(node)
            if node in dependencies:
                for dep in dependencies[node]:
                    if dep in dependencies:
                        visit(dep)
            temp_mark.remove(node)
            visited.add(node)
            if node not in self._generation_order:
                self._generation_order.append(node)

        for name in dependencies:
            visit(name)

    def _find_dependencies(self, schema: Dict[str, Any]) -> Set[str]:
        """Find model dependencies in a schema."""
        deps: Set[str] = set()

        def find_refs(obj: Any, current_deps: Set[str]) -> None:
            """Recursively find schema references."""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == 'properties' and isinstance(value, dict):
                        for prop_name, prop_schema in value.items():
                            # Check if property type matches a known schema
                            if isinstance(prop_schema, dict):
                                if 'enum' in prop_schema:
                                    # It references an enum
                                    enum_name = self._to_pascal_case(prop_name)
                                    if enum_name in self.enum_names:
                                        current_deps.add(enum_name)
                            find_refs(prop_schema, current_deps)
                    elif key == 'items' and isinstance(value, dict):
                        # Check if array items reference a schema
                        find_refs(value, current_deps)
                    else:
                        find_refs(value, current_deps)
            elif isinstance(obj, list):
                for item in obj:
                    find_refs(item, current_deps)

        find_refs(schema, deps)
        return deps

    def _generate_enum(self, name: str, schema: Dict[str, Any]) -> str:
        """Generate an Enum class."""
        enum_values = schema['enum']
        description = schema.get('description', '')

        lines = []
        if description:
            lines.append(f'class {name}(Enum):')
            lines.append(f'    """{description}"""')
        else:
            lines.append(f'class {name}(Enum):')

        for value in enum_values:
            # Create a valid Python identifier from the value
            member_name = self._to_enum_member_name(value)
            lines.append(f"    {member_name} = '{value}'")

        return '\n'.join(lines)

    def _generate_model(self, name: str, schema: Dict[str, Any]) -> str:
        """Generate a Pydantic model class."""
        if not isinstance(schema, dict):
            return ''

        # Check if it's a RootModel (array at top level)
        if schema.get('type') == 'array' and 'items' in schema:
            return self._generate_root_model(name, schema)

        # Check if it's a simple type with no properties
        if 'properties' not in schema and schema.get('type') != 'object':
            return ''

        description = schema.get('description', '')
        properties = schema.get('properties', {})
        required = set(schema.get('required', []))

        lines = []
        lines.append(f'class {name}(BaseModel):')

        if description:
            lines.append(f'    """{description}"""')

        if not properties:
            lines.append('    pass')
            return '\n'.join(lines)

        # Generate fields
        for prop_name, prop_schema in properties.items():
            field_code = self._generate_field(prop_name, prop_schema, prop_name in required)
            lines.append(f'    {field_code}')

        return '\n'.join(lines)

    def _generate_root_model(self, name: str, schema: Dict[str, Any]) -> str:
        """Generate a RootModel for array types."""
        items = schema.get('items', {})
        item_type = self.type_mapper.map_type(items)
        description = schema.get('description', '')

        lines = []
        lines.append(f'class {name}(RootModel[List[{item_type}]]):')

        if description:
            lines.append(f'    """{description}"""')

        field_args = [f'List[{item_type}]']
        field_kwargs = []

        if description:
            field_kwargs.append(f"description='{description}'")

        if 'examples' in schema:
            examples = schema['examples']
            field_kwargs.append(f"examples={examples!r}")

        kwargs_str = ', '.join(field_kwargs)
        if kwargs_str:
            lines.append(f'    root: List[{item_type}] = Field(..., {kwargs_str})')
        else:
            lines.append(f'    root: List[{item_type}]')

        return '\n'.join(lines)

    def _generate_field(self, name: str, schema: Dict[str, Any], is_required: bool) -> str:
        """Generate a field definition."""
        if not isinstance(schema, dict):
            field_type = 'Any'
        elif 'enum' in schema:
            # Use the enum class name
            field_type = self._to_pascal_case(name)
        elif schema.get('type') == 'array' and 'items' in schema:
            # Handle arrays with potential model references
            items = schema['items']
            if isinstance(items, dict) and 'properties' in items:
                # Items define an inline object - check if it matches a known schema
                item_type = self._find_matching_schema(items)
                if item_type:
                    field_type = f'List[{item_type}]'
                else:
                    field_type = self.type_mapper.map_type(schema, self._to_pascal_case(name))
            else:
                field_type = self.type_mapper.map_type(schema, self._to_pascal_case(name))
            self.type_mapper.import_types.add('List')
        elif 'properties' in schema:
            # Inline object - check if it matches a known schema
            matched_type = self._find_matching_schema(schema)
            if matched_type:
                field_type = matched_type
            else:
                field_type = 'Dict[str, Any]'
                self.type_mapper.import_types.add('Dict')
        else:
            field_type = self.type_mapper.map_type(schema, self._to_pascal_case(name))

        # Add Optional if not required
        if not is_required:
            self.type_mapper.import_types.add('Optional')
            field_type = f'Optional[{field_type}]'

        # Build Field() arguments
        field_args = []
        field_kwargs = []

        # Default value
        if is_required:
            if 'default' in schema:
                field_args.append(repr(schema['default']))
            else:
                field_args.append('...')
        else:
            if 'default' in schema:
                field_args.append(repr(schema['default']))
            else:
                field_args.append('None')

        # Description
        if 'description' in schema:
            desc = schema['description'].replace("'", "\\'").replace('\n', '\\n')
            field_kwargs.append(f"description='{desc}'")

        # Examples
        if 'examples' in schema:
            field_kwargs.append(f"examples={schema['examples']!r}")

        # Build final field definition
        args_str = ', '.join(field_args)
        if field_kwargs:
            kwargs_str = ', '.join(field_kwargs)
            return f'{name}: {field_type} = Field({args_str}, {kwargs_str})'
        elif field_args and field_args[0] != 'None':
            return f'{name}: {field_type} = Field({args_str})'
        else:
            return f'{name}: {field_type} = {field_args[0]}'

    @staticmethod
    def _to_pascal_case(name: str) -> str:
        """Convert a name to PascalCase."""
        # Handle snake_case and kebab-case
        parts = name.replace('-', '_').split('_')
        return ''.join(word.capitalize() for word in parts if word)

    def _find_matching_schema(self, schema: Dict[str, Any]) -> Optional[str]:
        """Find if a schema matches any known schema definition."""
        if not isinstance(schema, dict) or 'properties' not in schema:
            return None

        schema_props = set(schema.get('properties', {}).keys())

        # Check against all known schemas
        for schema_name, known_schema in self.schemas.items():
            if isinstance(known_schema, dict) and 'properties' in known_schema:
                known_props = set(known_schema.get('properties', {}).keys())
                # If properties match, it's likely the same schema
                if schema_props == known_props:
                    return schema_name

        return None

    @staticmethod
    def _to_enum_member_name(value: str) -> str:
        """Convert an enum value to a valid Python identifier."""
        # Replace special characters
        member = value.replace('.', '_').replace('-', '_').replace('*', '_').replace(' ', '_')
        # Remove invalid characters
        member = ''.join(c if c.isalnum() or c == '_' else '_' for c in member)
        # Ensure it doesn't start with a number
        if member and member[0].isdigit():
            member = '_' + member
        # Convert to uppercase for enum convention
        return member.upper() if member else 'UNKNOWN'

    def _format_output(self) -> str:
        """Format the final output with imports and models."""
        lines = [
            f'# generated by {sys.argv[0]}',
            f'#   timestamp: {datetime.now().isoformat()}',
            '',
            'from __future__ import annotations',
            '',
        ]

        # Standard library imports
        std_imports = []
        if 'datetime' in self.type_mapper.import_types:
            std_imports.append('from datetime import datetime')
        std_imports.append('from enum import Enum')
        if 'Dict' in self.type_mapper.import_types or 'List' in self.type_mapper.import_types or 'Optional' in self.type_mapper.import_types:
            imports = []
            # Always include Any if we're using Dict
            if 'Dict' in self.type_mapper.import_types:
                imports.append('Any')
                imports.append('Dict')
            if 'List' in self.type_mapper.import_types:
                imports.append('List')
            if 'Optional' in self.type_mapper.import_types:
                imports.append('Optional')
            std_imports.append(f"from typing import {', '.join(sorted(imports))}")
        if 'UUID' in self.type_mapper.import_types:
            std_imports.append('from uuid import UUID')

        lines.extend(std_imports)
        lines.append('')

        # Pydantic imports
        pydantic_imports = ['BaseModel', 'Field']
        if any('RootModel' in model for model in self.generated_models):
            pydantic_imports.append('RootModel')
        if 'EmailStr' in self.type_mapper.import_types:
            pydantic_imports.append('EmailStr')

        lines.append(f"from pydantic import {', '.join(sorted(pydantic_imports))}")
        lines.append('')
        lines.append('')

        # Enums
        if self.generated_enums:
            lines.extend(enum + '\n\n' for enum in self.generated_enums)
            lines.append('')
            lines.append('')

        # Models
        lines.extend([model + '\n\n' for model in self.generated_models])

        return '\n'.join(lines).rstrip() + '\n'


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Generate Pydantic models from AsyncAPI YAML specifications')
    parser.add_argument('input', type=Path, help='Path to the AsyncAPI YAML file')
    parser.add_argument('-o', '--output', type=Path, help='Output file path (default: stdout)')

    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        print(f"Error: Input file '{args.input}' does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        # Initialize components
        resolver = RefResolver()
        parser = SchemaParser(args.input, resolver)

        # Parse AsyncAPI file
        parser.parse()

        # Extract schemas
        schemas = parser.get_all_schemas()

        if not schemas:
            print("Warning: No schemas found in AsyncAPI file", file=sys.stderr)
            sys.exit(0)

        # Generate models
        generator = PydanticGenerator(schemas)
        output = generator.generate()

        # Write output
        if args.output:
            args.output.write_text(output)
            print(f"Generated models written to {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
