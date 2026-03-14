from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class Player:
    id: int
    name: str
    story_progress: Dict[str, str] = field(default_factory=dict) # e.g. "fantasy": "p01_a_node_000"
    completed_endings: List[str] = field(default_factory=list)
    unlocked_worlds: List[str] = field(default_factory=list)
    story_flags: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StoryNode:
    id: str
    text_ar: str
    choices: List[Dict[str, str]]
    next_part_id: Optional[str] = None

@dataclass
class Faction:
    id: str
    name_ar: str
    desc_ar: str
    leader_name_ar: str
