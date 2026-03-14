import discord
from typing import Optional, List

def create_story_embed(title: str, description: str, world: str = "fantasy", lore: Optional[str] = None) -> discord.Embed:
    """
    Primary Embed for story progression, narrative text, and world flavor.
    """
    world_translations = {
        "fantasy": "الخيال",
        "past": "الماضي السحيق",
        "future": "المستقبل المظلم",
        "alternate": "العالم الموازي"
    }

    colors = {
        "fantasy": 0x3498db,
        "past": 0xe67e22,
        "future": 0x9b59b6,
        "alternate": 0x2ecc71
    }

    color = colors.get(world.lower(), 0xffffff)
    world_ar = world_translations.get(world.lower(), "المجهول")

    embed = discord.Embed(
        title=f"📜 {title}",
        description=description,
        color=color
    )

    if lore:
        embed.add_field(name="مقتطفات من الذاكرة", value=f"*{lore}*", inline=False)

    embed.set_footer(text=f"أنت الآن في عالم: {world_ar}")
    return embed

def create_story_profile_embed(player_name: str, active_world: Optional[str], unlocked_worlds: List[str], endings: List[str]) -> discord.Embed:
    """
    Secondary Embed for tracking player story state, flags, and progression.
    """
    embed = discord.Embed(
        title=f"👤 مسار اللاعب: {player_name}",
        color=0xf1c40f
    )

    world_str = active_world if active_world else "لا يوجد عالم نشط"
    embed.add_field(name="العالم الحالي", value=world_str, inline=True)

    unlocked_str = ", ".join(unlocked_worlds) if unlocked_worlds else "لا يوجد"
    embed.add_field(name="العوالم المفتوحة", value=unlocked_str, inline=True)

    if endings:
        ending_str = "\n".join([f"✨ {e}" for e in endings])
        embed.add_field(name="النهايات المكتشفة", value=ending_str, inline=False)

    embed.set_footer(text="الأقدار تُكتب بخياراتك.")
    return embed
