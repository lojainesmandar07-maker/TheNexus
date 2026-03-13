import random
from domain.models import Player, Job, Quest, Item

def calculate_level_up(player: Player) -> bool:
    """Check if the player has enough XP to level up. XP scales exponentially."""
    required_xp = player.level * 1000 + (player.level ** 2 * 100)
    if player.xp >= required_xp:
        player.level += 1
        player.xp -= required_xp
        # Slight stat boost on level up
        for stat in player.stats:
            player.stats[stat] += random.randint(0, 2)
        return True
    return False

def complete_job(player: Player, job: Job) -> dict:
    """Handle the logic of completing a job based on archetype matching and rare events."""
    bonus_multiplier = 1.0

    # Archetype synergy bonus
    if player.archetype == job.archetype or job.archetype == "general":
        bonus_multiplier = 1.5

    earned_gold = int(job.base_reward_gold * bonus_multiplier)
    earned_xp = int(job.base_reward_xp * bonus_multiplier)

    player.gold += earned_gold
    player.xp += earned_xp

    leveled_up = calculate_level_up(player)

    dropped_rare = False
    rare_item = None
    rare_event_text = None

    # Rare Drop Logic (~0.1% to 5% chance depending on job setup)
    if random.random() < job.rare_drop_chance:
        dropped_rare = True
        if job.rare_event:
            rare_event_text = job.rare_event.get("event_text_ar")
            rare_item = job.rare_event.get("bonus_item")
            if rare_item:
                player.inventory.append(rare_item)
                if rare_item == "token_of_mastery" or rare_item == "token":
                    player.tokens += 1
        else:
            player.inventory.append("rare_mystery_item")
            rare_item = "rare_mystery_item"

    return {
        "success": True,
        "gold_earned": earned_gold,
        "xp_earned": earned_xp,
        "leveled_up": leveled_up,
        "dropped_rare": dropped_rare,
        "rare_event_text": rare_event_text,
        "rare_item": rare_item
    }

def buy_item(player: Player, item: Item) -> dict:
    """Handle shop logic with multi-currency support (gold vs tokens)."""
    currency_balance = player.gold if item.currency == 'gold' else player.tokens

    if currency_balance >= item.price:
        if item.currency == 'gold':
            player.gold -= item.price
        else:
            player.tokens -= item.price

        if item.type == 'title':
            player.titles.append(item.name_ar)
            player.active_title = item.name_ar
        else:
            player.inventory.append(item.id)

        return {"success": True, "message": f"تم شراء {item.name_ar} بنجاح!"}

    return {"success": False, "message": "لا تملك رصيداً كافياً."}

def complete_quest(player: Player, quest: Quest) -> dict:
    """Handle quest completion, reputation rewards, and multi-stage tracking."""
    # Assuming the player has completed all stages
    total_xp = sum(stage.get("xp", 0) for stage in quest.stages)
    player.xp += total_xp
    player.gold += quest.reward_gold

    leveled_up = calculate_level_up(player)

    if quest.reward_reputation:
        for faction, amount in quest.reward_reputation.items():
            player.reputation[faction] = player.reputation.get(faction, 0) + amount

    if quest.reward_item:
        player.inventory.append(quest.reward_item)

    return {
        "success": True,
        "xp_earned": total_xp,
        "gold_earned": quest.reward_gold,
        "leveled_up": leveled_up,
        "reputation_gained": quest.reward_reputation,
        "item_gained": quest.reward_item,
        "next_quest_unlocked": quest.next_quest_id
    }
