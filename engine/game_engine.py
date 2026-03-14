import json
import os
from typing import Dict, Any, List, Optional
from domain.models import Job, Item


class GameEngine:
    def __init__(self, content_dir: str = "content"):
        self.content_dir = content_dir
        self.jobs_cache: List[Job] = []
        self.jobs_index: Dict[str, Job] = {}
        self.shop_items_cache: List[Item] = []
        self.shop_items_index: Dict[str, Item] = {}
        self.archetype_name_to_id: Dict[str, str] = {}
        self.quests_cache: List[Any] = []
        self.quests_index: Dict[str, Any] = {}
        self.achievements_cache: List[Any] = []
        self.achievements_index: Dict[str, Any] = {}
        self.test_questions_cache: List[Any] = []
        self.load_archetypes()
        self.load_jobs()
        self.load_shop()
        self.load_quests()
        self.load_achievements()
        self.load_test_questions()

    def load_archetypes(self):
        """Load mapping to normalize Arabic archetype names to canonical IDs."""
        defs_path = os.path.join(self.content_dir, "characters", "character_defs.json")
        if not os.path.exists(defs_path):
            return
        try:
            with open(defs_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for a in data.get('archetypes', []):
                archetype_id = a.get('id')
                name_ar = a.get('name_ar')
                if isinstance(archetype_id, str) and isinstance(name_ar, str):
                    self.archetype_name_to_id[name_ar] = archetype_id
        except Exception as e:
            print(f"Error loading archetypes {defs_path}: {e}")

    def normalize_archetype(self, archetype: str) -> str:
        if not isinstance(archetype, str):
            return "general"
        return self.archetype_name_to_id.get(archetype, archetype)

    def load_jobs(self):
        """Loads JSON job files into memory."""
        self.jobs_cache.clear()
        self.jobs_index.clear()
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
                                self.jobs_index[job.id] = job
                except Exception as e:
                    print(f"Error loading jobs {filepath}: {e}")

    def load_shop(self):
        """Loads JSON economy shop items into memory."""
        self.shop_items_cache.clear()
        self.shop_items_index.clear()
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
                                self.shop_items_index[item.id] = item
                except Exception as e:
                    print(f"Error loading shop {filepath}: {e}")

    def load_quests(self):
        """Loads JSON quest files into memory."""
        self.quests_cache.clear()
        self.quests_index.clear()
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
                                self.quests_cache.append(q)
                                self.quests_index[q.get("id")] = q
                except Exception as e:
                    print(f"Error loading quests {filepath}: {e}")

    def load_achievements(self):
        """Loads JSON achievement files into memory."""
        self.achievements_cache.clear()
        self.achievements_index.clear()
        achievements_path = os.path.join(self.content_dir, "achievements")
        if not os.path.exists(achievements_path):
            return

        for filename in os.listdir(achievements_path):
            if filename.endswith(".json"):
                filepath = os.path.join(achievements_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "achievements" in data:
                            for a in data["achievements"]:
                                self.achievements_cache.append(a)
                                self.achievements_index[a.get("id")] = a
                except Exception as e:
                    print(f"Error loading achievements {filepath}: {e}")

    def load_test_questions(self):
        """Loads character test questions into memory."""
        self.test_questions_cache.clear()
        questions_path = os.path.join(self.content_dir, "characters", "character_test_questions.json")
        if not os.path.exists(questions_path):
            return

        try:
            with open(questions_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "questions" in data:
                    self.test_questions_cache = data["questions"]
        except Exception as e:
            print(f"Error loading test questions {questions_path}: {e}")

    def get_available_jobs(self, archetype: str, count: int = 3) -> List[Job]:
        """Returns a random selection of jobs matching the archetype or general jobs."""
        import random
        normalized_archetype = self.normalize_archetype(archetype)
        valid_jobs = [j for j in self.jobs_cache if j.archetype == normalized_archetype or j.archetype == "general"]
        if not valid_jobs:
            return []
        return random.sample(valid_jobs, min(len(valid_jobs), count))

    def get_shop_items(self, count: int = 5) -> List[Item]:
        """Returns a selection of items available in the shop."""
        import random
        if not self.shop_items_cache:
            return []
        return random.sample(self.shop_items_cache, min(len(self.shop_items_cache), count))

    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        return self.jobs_index.get(job_id)

    def get_item_by_id(self, item_id: str) -> Optional[Item]:
        return self.shop_items_index.get(item_id)

    def get_quest_by_id(self, quest_id: str) -> Optional[Any]:
        return self.quests_index.get(quest_id)

    def get_achievement_by_id(self, achievement_id: str) -> Optional[Any]:
        return self.achievements_index.get(achievement_id)
