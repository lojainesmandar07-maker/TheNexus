import json
import pathlib
import re
import sys
from collections import Counter

root = pathlib.Path("content")
json_files = list(root.rglob("*.json"))

errors = []

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

# 4) archetype quest coverage
archetypes = {a.get("id") for a in parsed[root / "characters" / "character_defs.json"].get("archetypes", [])}
chains = {p.name.replace("archetype_", "").replace("_chains.json", "") for p in (root / "quests").glob("archetype_*_chains.json")}
missing = sorted([a for a in archetypes if a and a not in chains])
if missing:
    errors.append(f"Missing archetype quest chains for: {missing}")

# 5) duplicate ids per domain
for category, key in [("jobs", "jobs"), ("quests", "quests"), ("economy", "items"), ("achievements", "achievements"), ("contracts", "weekly_contracts")]:
    c = Counter()
    for f in (root / category).glob("*.json"):
        for obj in parsed[f].get(key, []):
            if isinstance(obj, dict) and isinstance(obj.get("id"), str):
                c[obj["id"]] += 1
    dups = [k for k, v in c.items() if v > 1]
    if dups:
        errors.append(f"Duplicate IDs in {category}: {dups[:10]}")

if errors:
    print("❌ Content validation failed:")
    for e in errors:
        print("-", e)
    sys.exit(1)

print(f"✅ Content validation passed ({len(json_files)} JSON files)")
