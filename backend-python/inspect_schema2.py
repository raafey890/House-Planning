from app.models.provider_schema import GeminiLayoutData
import json

schema = GeminiLayoutData.model_json_schema()
with open('schema_dump.json', 'w') as f:
    json.dump(schema, f, indent=2)
