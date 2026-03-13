import json
import os
from typing import Dict, Any, Optional


class StoryEngine:
    def __init__(self, content_dir: str = "content"):
        self.content_dir = content_dir
        self.worlds = ["fantasy", "past", "future", "alternate"]
        self.story_cache: Dict[str, Dict[str, Any]] = {}
        self.endings_cache: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.load_stories()
        self.load_endings()

    def load_stories(self):
        """Load all story nodes across all parts for each world."""
        self.story_cache = {}
        for world in self.worlds:
            world_path = os.path.join(self.content_dir, "story", world)
            if not os.path.exists(world_path):
                continue

            for filename in sorted(os.listdir(world_path)):
                if not filename.endswith(".json"):
                    continue

                filepath = os.path.join(world_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    nodes = data.get("nodes")
                    if isinstance(nodes, dict):
                        self.story_cache.setdefault(world, {}).update(nodes)
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")

    def load_endings(self):
        """Load configured narrative endings per world."""
        self.endings_cache = {world: {} for world in self.worlds}
        endings_path = os.path.join(self.content_dir, "story", "endings.json")
        if not os.path.exists(endings_path):
            return

        try:
            with open(endings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            endings = data.get("endings", [])
            if isinstance(endings, list):
                for ending in endings:
                    world = ending.get("world")
                    ending_id = ending.get("id")
                    if world in self.endings_cache and isinstance(ending_id, str):
                        self.endings_cache[world][ending_id] = ending
        except Exception as e:
            print(f"Error loading endings {endings_path}: {e}")

    def get_node(self, world: str, node_id: str) -> Optional[Dict[str, Any]]:
        if world in self.story_cache and node_id in self.story_cache[world]:
            return self.story_cache[world][node_id]
        return None

    def get_ending(self, world: str, ending_id: str) -> Optional[Dict[str, Any]]:
        if world in self.endings_cache:
            return self.endings_cache[world].get(ending_id)
        return None

    def get_start_node(self, world: str) -> Optional[Dict[str, Any]]:
        return self.get_node(world, "p01_a_node_000")

    def process_choice(
        self,
        world: str,
        current_node_id: str,
        choice_index: int,
        player_archetype: str,
        player_stats: Dict[str, int],
    ) -> Dict[str, Any]:
        """Resolve choice destination, including multi-endings."""
        node = self.get_node(world, current_node_id)
        if not node or "choices" not in node:
            return {"success": False, "message": "العقدة الحالية غير صالحة."}

        choices = node["choices"]
        if choice_index < 0 or choice_index >= len(choices):
            return {"success": False, "message": "اختيار غير صالح."}

        choice = choices[choice_index]

        req_archetype = choice.get("required_archetype")
        if req_archetype and req_archetype != player_archetype:
            return {"success": False, "message": "هذا المسار مغلق. يتطلب نمط شخصية مختلف."}

        req_skill = choice.get("skill_check")
        if req_skill:
            difficulty = int(choice.get("difficulty", 15))
            if not self.evaluate_skill_check(player_stats, req_skill, difficulty):
 main
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
=======
                # On failure, prevent progression and return an explicit failure state
                return {
                    "success": False,
                    "message": "لقد فشلت في اجتياز اختبار المهارة المطلوب (D20). حاول اختيار مسار آخر أو ترقية مستواك."
                }
 arabic-rpg-bot-init-5663612515060521641

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
        next_node = self.get_node(world, next_node_id) if next_node_id else None
        if next_node:
            return {"success": True, "next_node": next_node, "reward_xp": node.get("reward_xp", 10)}

        return {"success": False, "message": "لم يتم العثور على المسار التالي."}

    def evaluate_skill_check(self, player_stats: Dict[str, int], required_skill: str, difficulty: int) -> bool:
        import random

        base_roll = random.randint(1, 20)
        skill_modifier = player_stats.get(required_skill, 0) // 2
        total = base_roll + skill_modifier
        return total >= difficulty
