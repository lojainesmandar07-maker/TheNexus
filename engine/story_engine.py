import json
import os
from typing import Dict, Any, Optional


class StoryEngine:
    def __init__(self, content_dir: str = "content"):
        self.content_dir = content_dir
        self.worlds = ["fantasy", "past", "future", "alternate"]
        self.story_cache: Dict[str, Dict[str, Any]] = {}
        self.endings_cache: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.archetype_id_to_name: Dict[str, str] = {}
        self.archetype_name_to_id: Dict[str, str] = {}
        self.load_archetypes()
        self.load_stories()

    def load_archetypes(self):
        """Load archetype id/name mapping so locks work with ID or Arabic name."""
        self.archetype_id_to_name = {}
        self.archetype_name_to_id = {}
        defs_path = os.path.join(self.content_dir, "characters", "character_defs.json")
        if not os.path.exists(defs_path):
            return

        try:
            with open(defs_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for a in data.get("archetypes", []):
                archetype_id = a.get("id")
                name_ar = a.get("name_ar")
                if isinstance(archetype_id, str) and isinstance(name_ar, str):
                    self.archetype_id_to_name[archetype_id] = name_ar
                    self.archetype_name_to_id[name_ar] = archetype_id
        except Exception as e:
            print(f"Error loading archetypes {defs_path}: {e}")

    def archetype_matches(self, required: str, player_archetype: str) -> bool:
        """Allow comparing archetypes by either ID or Arabic display name."""
        if not required or not player_archetype:
            return False
        if required == player_archetype:
            return True

        req_id = self.archetype_name_to_id.get(required, required)
        ply_id = self.archetype_name_to_id.get(player_archetype, player_archetype)
        if req_id == ply_id:
            return True

        req_name = self.archetype_id_to_name.get(required, required)
        ply_name = self.archetype_id_to_name.get(player_archetype, player_archetype)
        return req_name == ply_name

    def load_stories(self):
        """Loads JSON story files into memory for quick access."""
        for world in self.worlds:
            world_path = os.path.join(self.content_dir, "story", world)
            if not os.path.exists(world_path):
                continue

            for filename in os.listdir(world_path):
                if filename.endswith(".json"):
                    filepath = os.path.join(world_path, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            # Assuming structure like {"nodes": {"node1": {...}, ...}}
                            if "nodes" in data:
                                if world not in self.story_cache:
                                    self.story_cache[world] = {}
                                self.story_cache[world].update(data["nodes"])
                    except Exception as e:
                        print(f"Error loading {filepath}: {e}")

    def get_node(self, world: str, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific node from a world's story."""
        if world in self.story_cache and node_id in self.story_cache[world]:
            return self.story_cache[world][node_id]
        return None

    def get_start_node(self, world: str) -> Optional[Dict[str, Any]]:
        """Return the first node of a world."""
        return self.get_node(world, "p01_a_node_000")

    def process_choice(
        self,
        world: str,
        current_node_id: str,
        choice_index: int,
        player_archetype: str,
        player_stats: Dict[str, int]
    ) -> Dict[str, Any]:
        """Determine the next node based on a player's choice, handling locks and skill checks."""
        node = self.get_node(world, current_node_id)
        if not node or "choices" not in node:
            return {"success": False, "message": "العقدة الحالية غير صالحة."}

        choices = node["choices"]
        if choice_index < 0 or choice_index >= len(choices):
            return {"success": False, "message": "اختيار غير صالح."}

        choice = choices[choice_index]

        # 1. Check Archetype Lock (Hidden Paths)
        req_archetype = choice.get("required_archetype")
        if req_archetype and not self.archetype_matches(req_archetype, player_archetype):
            return {"success": False, "message": "هذا المسار مغلق. يتطلب نمط شخصية مختلف."}

        # 2. Evaluate Skill Check (if any)
        req_skill = choice.get("skill_check")
        if req_skill:
            # Baseline difficulty
            difficulty = 15
            if not self.evaluate_skill_check(player_stats, req_skill, difficulty):
                fail_node_id = choice.get("fail_next_node") or current_node_id
                fail_node = self.get_node(world, fail_node_id)
                if fail_node:
                    return {
                        "success": True,
                        "next_node": fail_node,
                        "reward_xp": max(1, node.get("reward_xp", 10) // 3),
                        "check_failed": True,
                        "outcome_message": "أخفقت في اختبار المهارة، فتعثرت خطتك وتبدّل مسارك.",
                    }
                return {"success": False, "message": "أخفقت في اختبار المهارة ولم يتم العثور على مسار الفشل."}

        ending_id = choice.get("ending_id")
        if ending_id:
            ending = self.get_ending(world, ending_id)
            if not ending:
                return {"success": False, "message": "لم يتم العثور على النهاية المطلوبة."}
            return {
                "success": True,
                "is_ending": True,
                "ending": ending,
                "reward_xp": node.get("reward_xp", 10),
            }

        next_node_id = choice.get("next_node")
        next_node = self.get_node(world, next_node_id)

        if next_node:
            return {"success": True, "next_node": next_node, "reward_xp": node.get("reward_xp", 10)}
        else:
            return {"success": False, "message": "لم يتم العثور على المسار التالي."}

    def evaluate_skill_check(self, player_stats: Dict[str, int], required_skill: str, difficulty: int) -> bool:
        """Simulate a skill check for a story choice (D20 system + modifiers)."""
        import random
        base_roll = random.randint(1, 20)
        skill_modifier = player_stats.get(required_skill, 0) // 2  # Simplified D&D style modifier
        total = base_roll + skill_modifier
        return total >= difficulty