from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Player:
    id: int
    name: str
    archetype: str
    level: int = 1
    xp: int = 0
    gold: int = 0
    reputation: Dict[str, int] = field(default_factory=dict)
    inventory: List[str] = field(default_factory=list)
    current_quest: Optional[str] = None
    story_progress: Dict[str, str] = field(default_factory=dict) # e.g. "fantasy": "node_05"

@dataclass
class QuestNode:
    id: str
    text_ar: str
    choices: List[Dict[str, str]] # e.g. [{"text_ar": "قاتل الوحش", "next_node": "node_fight", "skill_check": "strength"}]
    reward_xp: int = 0
    reward_gold: int = 0
    required_archetype: Optional[str] = None

@dataclass
class Item:
    id: str
    name_ar: str
    desc_ar: str
    price: int
    rarity: str
    type: str # 'field_kit', 'title', 'special_good', 'token'

@dataclass
class Job:
    id: str
    title_ar: str
    desc_ar: str
    archetype: str
    base_reward_gold: int
    base_reward_xp: int
    rare_drop_chance: float = 0.001 # 0.1% chance

@dataclass
class Faction:
    id: str
    name_ar: str
    desc_ar: str
    leader_name_ar: str
