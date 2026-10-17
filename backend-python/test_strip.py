def strip_unsupported_keys(schema_node):
    if isinstance(schema_node, dict):
        # Remove unsupported keys
        for key in ['title', 'default', 'additionalProperties']:
            schema_node.pop(key, None)
            
        # Fix anyOf for Optional fields
        if 'anyOf' in schema_node:
            # Pydantic Optional[T] generates anyOf: [{'type': 'T'}, {'type': 'null'}]
            types = []
            for sub in schema_node['anyOf']:
                if 'type' in sub and sub['type'] != 'null':
                    types.append(sub['type'])
            if types:
                schema_node['type'] = types[0]
            del schema_node['anyOf']
            
        for k, v in schema_node.items():
            strip_unsupported_keys(v)
            
    elif isinstance(schema_node, list):
        for item in schema_node:
            strip_unsupported_keys(item)
            
    return schema_node

from app.models.provider_schema import GeminiLayoutData
import json

schema = GeminiLayoutData.model_json_schema()
stripped_schema = strip_unsupported_keys(schema)
print(json.dumps(stripped_schema))
