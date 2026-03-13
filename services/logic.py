from domain.models import Player, Job, QuestNode, Item

def calculate_level_up(player: Player) -> bool:
    """Check if the player has enough XP to level up."""
    required_xp = player.level * 1000
    if player.xp >= required_xp:
        player.level += 1
        player.xp -= required_xp
        return True
    return False

def complete_job(player: Player, job: Job) -> dict:
    """Handle the logic of completing a job."""
    # Simplified simulation
    player.gold += job.base_reward_gold
    player.xp += job.base_reward_xp

    leveled_up = calculate_level_up(player)

    import random
    dropped_rare = False
    if random.random() < job.rare_drop_chance:
        player.inventory.append("rare_item_drop")
        dropped_rare = True

    return {
        "success": True,
        "gold_earned": job.base_reward_gold,
        "xp_earned": job.base_reward_xp,
        "leveled_up": leveled_up,
        "dropped_rare": dropped_rare
    }

def buy_item(player: Player, item: Item) -> bool:
    """Handle shop logic."""
    if player.gold >= item.price:
        player.gold -= item.price
        player.inventory.append(item.id)
        return True
    return False
