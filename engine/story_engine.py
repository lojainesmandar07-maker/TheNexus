import json
import os
from typing import Dict, Any, Optional

class StoryEngine:
    def __init__(self, content_dir: str = "content"):
        self.content_dir = content_dir
        self.worlds = ["fantasy", "past", "future", "alternate"]
        self.story_cache: Dict[str, Dict[str, Any]] = {}
        self.load_stories()

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
                        with open(filepath, 'r', encoding='utf-8') as f:
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

    def process_choice(self, world: str, current_node_id: str, choice_index: int, player_archetype: str, player_stats: Dict[str, int]) -> Dict[str, Any]:
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
        if req_archetype and req_archetype != player_archetype:
            return {"success": False, "message": "هذا المسار مغلق. يتطلب نمط شخصية مختلف."}

        # 2. Evaluate Skill Check (if any)
        req_skill = choice.get("skill_check")
        if req_skill:
            # Baseline difficulty
            difficulty = 15
            if not self.evaluate_skill_check(player_stats, req_skill, difficulty):
                # On failure, maybe route them to a random node instead of the intended one, or apply a penalty.
                # For this epic implementation, let's say they take a minor setback but still progress, or stay on the node.
                # We'll just pass them through with a warning string for now.
                pass

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
        skill_modifier = player_stats.get(required_skill, 0) // 2 # Simplified D&D style modifier
        total = base_roll + skill_modifier
        return total >= difficulty
