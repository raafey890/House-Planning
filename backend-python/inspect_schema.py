from app.models.provider_schema import GeminiLayoutData
import json

schema = GeminiLayoutData.model_json_schema()

def find_unsupported_keys(schema_node, path=""):
    unsupported = []
    if isinstance(schema_node, dict):
        if "additionalProperties" in schema_node:
            unsupported.append(f"{path}: additionalProperties")
        for k, v in schema_node.items():
            unsupported.extend(find_unsupported_keys(v, f"{path}.{k}"))
    elif isinstance(schema_node, list):
        for i, item in enumerate(schema_node):
            unsupported.extend(find_unsupported_keys(item, f"{path}[{i}]"))
    return unsupported

unsupported = find_unsupported_keys(schema, "root")
print("Unsupported keys found:", unsupported)
