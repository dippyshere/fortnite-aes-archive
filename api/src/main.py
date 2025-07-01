import re
import json
import os

file_path = "./archive/readme.md"
dynamic_dir = "./archive/dynamic"
output_dir = "api/archive"

os.makedirs(output_dir, exist_ok=True)

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

pattern = re.compile(
    r'\|\s*(?:\[[\s]*([\d]+\.[\d]+(?:\.[\d]+)?)\][^\|]*|\s*([\d]+\.[\d]+(?:\.[\d]+)?)?)\s*\|\s*(0x[a-zA-Z0-9]{64})\s*\|'
)

matches = pattern.findall(content)

for match in matches:
    version = match[0] if match[0] else match[1]
    key = match[2]

    json_data = {
        "mainKey": key
    }

    dynamic_path = os.path.join(dynamic_dir, f"{version}.md")
    if os.path.isfile(dynamic_path):
        with open(dynamic_path, "r", encoding="utf-8") as df:
            dynamic_content = df.read()

        dynamic_keys = []
        seen_guids = set()

        row_pattern = re.compile(r'\|\s*([^\|\n]+?)\s*\|\s*(.*?)\s*(?:\|\s*(.*?)\s*)?\|')
        for row in row_pattern.findall(dynamic_content):
            if len(row) < 2:
                continue

            name = row[0]
            key_guid_cell = row[1]

            if name.strip().startswith("##") or key_guid_cell.strip().startswith("##"):
                continue

            if "name" in name.lower() or set(name.strip()) <= {"-", "*"}:
                continue

            name_clean = name.strip("* ").strip()

            parts = re.split(r'<br\s*/?>|</br>|<br>|\\n|\n', key_guid_cell)
            parts = [p.strip() for p in parts if p.strip()]

            key = next((p for p in parts if p.startswith("0x")), None)
            guid = next((p for p in parts if not p.startswith("0x")), parts[0] if parts else None)

            if not guid or guid in seen_guids:
                continue
            seen_guids.add(guid)

            dynamic_keys.append({
                "name": name_clean,
                "guid": guid,
                **({"key": key} if key else {})
            })

        row_pattern_2col = re.compile(r'\|\s*([^\|\n]+?)\s*\|\s*([^\|]+?)\s*\|')
        for row in row_pattern_2col.findall(dynamic_content):
            name, key_guid_cell = row

            if name.strip().startswith("##") or key_guid_cell.strip().startswith("##"):
                continue

            if "name" in name.lower() or set(name.strip()) <= {"-", "*"}:
                continue

            name_clean = name.strip("* ").strip()

            if any(d.get("name") == name_clean for d in dynamic_keys):
                continue

            parts = re.split(r'<br\s*/?>|</br>|<br>|\\n|\n', key_guid_cell)
            parts = [p.strip() for p in parts if p.strip()]

            key = next((p for p in parts if p.startswith("0x")), None)
            guid = next((p for p in parts if not p.startswith("0x")), parts[0] if parts else None)

            if not guid or guid in seen_guids:
                continue
            seen_guids.add(guid)

            dynamic_keys.append({
                "name": name_clean,
                "guid": guid,
                **({"key": key} if key else {})
            })

        if dynamic_keys:
            json_data["dynamicKeys"] = dynamic_keys

    output_path = os.path.join(output_dir, f"{version}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    print(f"Wrote {output_path}")
