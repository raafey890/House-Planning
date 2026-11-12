import json, re

with open(r'frontend/src/data/exteriorCatalog.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'export const EXTERIOR_DESIGNS = (\[.*?\]);', content, re.DOTALL)
if m:
    designs = json.loads(m.group(1))
    print(f'Total designs: {len(designs)}')
    for d in designs:
        print(f"{d['id']}: {d['name']} [{d['category']}] -> {d['image_path']}")
