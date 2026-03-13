from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class Player:
    id: int
    name: str
    archetype: str
    level: int = 1
    xp: int = 0
    gold: int = 0
    tokens: int = 0
    reputation: Dict[str, int] = field(default_factory=dict)
    inventory: List[str] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)
    active_title: Optional[str] = None
    current_quest: Optional[str] = None
    story_progress: Dict[str, str] = field(default_factory=dict) # e.g. "fantasy": "p01_a_node_000"
    stats: Dict[str, int] = field(default_factory=lambda: {"agility": 10, "strength": 10, "intellect": 10, "magic": 10, "stealth": 10, "crafting": 10, "charisma": 10})

@dataclass
class QuestNode:
    id: str
    text_ar: str
    choices: List[Dict[str, str]]
    reward_xp: int = 0
    reward_gold: int = 0

@dataclass
class Item:
    id: str
    name_ar: str
    desc_ar: str
    price: int
    currency: str # 'gold', 'token'
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
    rare_drop_chance: float = 0.001
    rare_event: Optional[Dict[str, str]] = None

@dataclass
class Quest:
    id: str
    title_ar: str
    desc_ar: str
    stages: List[Dict[str, Any]]
    reward_gold: int = 0
    next_quest_id: Optional[str] = None
    required_archetype: Optional[str] = None
    reward_reputation: Optional[Dict[str, int]] = None
    reward_item: Optional[str] = None

@dataclass
class Faction:
    id: str
    name_ar: str
    desc_ar: str
    leader_name_ar: str
