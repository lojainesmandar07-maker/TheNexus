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

    def process_choice(self, world: str, current_node_id: str, choice_index: int) -> Optional[Dict[str, Any]]:
        """Determine the next node based on a player's choice."""
        node = self.get_node(world, current_node_id)
        if node and "choices" in node:
            choices = node["choices"]
            if 0 <= choice_index < len(choices):
                choice = choices[choice_index]
                next_node_id = choice.get("next_node")
                return self.get_node(world, next_node_id)
        return None

    def evaluate_skill_check(self, player_stats: Dict[str, int], required_skill: str, difficulty: int) -> bool:
        """Simulate a skill check for a story choice."""
        import random
        base_roll = random.randint(1, 20)
        skill_modifier = player_stats.get(required_skill, 0)
        return (base_roll + skill_modifier) >= difficulty
