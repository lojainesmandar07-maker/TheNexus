import json
import os
from typing import Dict, Any, List, Optional
from domain.models import Job, Item, Quest

class GameEngine:
    def __init__(self, content_dir: str = "content"):
        self.content_dir = content_dir
        self.jobs_cache: List[Job] = []
        self.shop_items_cache: List[Item] = []
        self.quests_cache: List[Quest] = []
        self.achievements_cache: List[Dict[str, Any]] = []
        self.character_questions_cache: List[Dict[str, Any]] = []

        self.load_jobs()
        self.load_shop()
        self.load_quests()
        self.load_achievements()
        self.load_character_test()

    def load_jobs(self):
        """Loads JSON job files into memory."""
        jobs_path = os.path.join(self.content_dir, "jobs")
        if not os.path.exists(jobs_path):
            return

        for filename in os.listdir(jobs_path):
            if filename.endswith(".json"):
                filepath = os.path.join(jobs_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "jobs" in data:
                            for j in data["jobs"]:
                                job = Job(
                                    id=j["id"],
                                    title_ar=j["title_ar"],
                                    desc_ar=j["desc_ar"],
                                    archetype=j.get("archetype", "general"),
                                    base_reward_gold=j.get("base_reward_gold", 0),
                                    base_reward_xp=j.get("base_reward_xp", 0),
                                    rare_drop_chance=j.get("rare_drop_chance", 0.0),
                                    rare_event=j.get("rare_event")
                                )
                                self.jobs_cache.append(job)
                except Exception as e:
                    print(f"Error loading jobs {filepath}: {e}")

    def load_shop(self):
        """Loads JSON economy shop items into memory."""
        shop_path = os.path.join(self.content_dir, "economy")
        if not os.path.exists(shop_path):
            return

        for filename in os.listdir(shop_path):
            if filename.endswith(".json"):
                filepath = os.path.join(shop_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "items" in data:
                            for i in data["items"]:
                                item = Item(
                                    id=i["id"],
                                    name_ar=i["name_ar"],
                                    desc_ar=i.get("desc_ar", ""),
                                    price=i.get("price", 0),
                                    currency=i.get("currency", "gold"),
                                    rarity=i.get("rarity", "شائع"),
                                    type=i.get("type", "field_kit")
                                )
                                self.shop_items_cache.append(item)
                except Exception as e:
                    print(f"Error loading shop {filepath}: {e}")

    def load_quests(self):
        """Loads JSON quest files into memory."""
        quests_path = os.path.join(self.content_dir, "quests")
        if not os.path.exists(quests_path):
            return

        for filename in os.listdir(quests_path):
            if filename.endswith(".json"):
                filepath = os.path.join(quests_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "quests" in data:
                            for q in data["quests"]:
                                quest = Quest(
                                    id=q["id"],
                                    title_ar=q["title_ar"],
                                    desc_ar=q.get("desc_ar", ""),
                                    stages=q.get("stages", []),
                                    reward_gold=q.get("reward_gold", 0),
                                    next_quest_id=q.get("next_quest_id"),
                                    required_archetype=q.get("required_archetype"),
                                    reward_reputation=q.get("reward_reputation"),
                                    reward_item=q.get("reward_item")
                                )
                                self.quests_cache.append(quest)
                except Exception as e:
                    print(f"Error loading quests {filepath}: {e}")

    def load_achievements(self):
        """Loads achievements into memory."""
        achv_path = os.path.join(self.content_dir, "achievements")
        if not os.path.exists(achv_path):
            return

        for filename in os.listdir(achv_path):
            if filename.endswith(".json"):
                filepath = os.path.join(achv_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "achievements" in data:
                            self.achievements_cache.extend(data["achievements"])
                except Exception as e:
                    print(f"Error loading achievements {filepath}: {e}")

    def load_character_test(self):
        """Loads character test questions into memory."""
        filepath = os.path.join(self.content_dir, "characters", "character_test_questions.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "questions" in data:
                        self.character_questions_cache = data["questions"]
            except Exception as e:
                print(f"Error loading character test: {e}")

    def get_available_jobs(self, archetype: str, count: int = 3) -> List[Job]:
        """Returns a random selection of jobs matching the archetype or general jobs."""
        import random
        valid_jobs = [j for j in self.jobs_cache if j.archetype == archetype or j.archetype == "general"]
        if not valid_jobs:
            return []
        # Return a random sample up to 'count'
        return random.sample(valid_jobs, min(len(valid_jobs), count))

    def get_shop_items(self, count: int = 5) -> List[Item]:
        """Returns a selection of items available in the shop."""
        import random
        if not self.shop_items_cache:
            return []
        return random.sample(self.shop_items_cache, min(len(self.shop_items_cache), count))

    def get_available_quests(self, archetype: str, count: int = 3) -> List[Quest]:
        """Returns a selection of quests available to the player."""
        import random
        valid_quests = [q for q in self.quests_cache if not q.required_archetype or q.required_archetype == archetype]
        if not valid_quests:
            return []
        return random.sample(valid_quests, min(len(valid_quests), count))

    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        for j in self.jobs_cache:
            if j.id == job_id:
                return j
        return None

    def get_item_by_id(self, item_id: str) -> Optional[Item]:
        for i in self.shop_items_cache:
            if i.id == item_id:
                return i
        return None
