import json
import pathlib
import re
import sys
from collections import Counter

root = pathlib.Path("content")
json_files = list(root.rglob("*.json"))

errors = []


# 0) unresolved merge marker check (prevents broken merges)
scan_ext = {".py", ".json", ".md", ".yml", ".yaml"}
for f in pathlib.Path('.').rglob('*'):
    if not f.is_file() or f.suffix not in scan_ext:
        continue
    try:
        txt = f.read_text(encoding='utf-8')
    except Exception:
        continue
    if ("<<<"+"<<<<") in txt or ("==="+"====") in txt or (">>>"+">>>>") in txt:
        errors.append(f"Unresolved merge markers found: {f}")

# 1) parse
parsed = {}
for f in json_files:
    try:
        parsed[f] = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"JSON parse failure: {f} :: {e}")

if errors:
    for e in errors:
        print(e)
    sys.exit(1)

# 2) story link + endings refs
story_root = root / "story"
for world_dir in story_root.iterdir():
    if not world_dir.is_dir():
        continue
    world = world_dir.name
    world_nodes = {}
    for sf in world_dir.glob("*.json"):
        world_nodes.update(parsed[sf].get("nodes", {}))

    for sf in world_dir.glob("*.json"):
        for node_id, node in parsed[sf].get("nodes", {}).items():
            for idx, ch in enumerate(node.get("choices", [])):
                nxt = ch.get("next_node")
                if nxt and nxt not in world_nodes:
                    errors.append(f"Broken next_node: {world}/{sf.name}::{node_id}[{idx}] -> {nxt}")

endings = parsed.get(root / "story" / "endings.json", {}).get("endings", [])
ending_ids = {e.get("id") for e in endings if isinstance(e, dict)}
for world_dir in story_root.iterdir():
    if not world_dir.is_dir():
        continue
    for sf in world_dir.glob("*.json"):
        for node_id, node in parsed[sf].get("nodes", {}).items():
            for idx, ch in enumerate(node.get("choices", [])):
                eid = ch.get("ending_id")
                if eid and eid not in ending_ids:
                    errors.append(f"Broken ending_id: {sf}::{node_id}[{idx}] -> {eid}")

# 3) _ar latin token check
lat = re.compile(r"[A-Za-z]")
for f, d in parsed.items():
    def walk(x, path="$"):
        if isinstance(x, dict):
            for k, v in x.items():
                p = f"{path}.{k}"
                if k.endswith("_ar") and isinstance(v, str) and lat.search(v):
                    errors.append(f"Latin chars in _ar field: {f}::{p}")
                walk(v, p)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, f"{path}[{i}]")
    walk(d)


if errors:
    print("❌ Content validation failed:")
    for e in errors:
        print("-", e)
    sys.exit(1)

print(f"✅ Content validation passed ({len(json_files)} JSON files)")
