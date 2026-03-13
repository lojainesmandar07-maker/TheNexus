import discord

def create_story_embed(title: str, description: str, world: str = "fantasy") -> discord.Embed:
    """
    Primary Embed for story progression, narrative text, and active quests.
    All player-facing text must be Arabic.
    """
    colors = {
        "fantasy": 0x3498db,
        "past": 0xe67e22,
        "future": 0x9b59b6,
        "alternate": 0x2ecc71
    }

    color = colors.get(world.lower(), 0xffffff)

    embed = discord.Embed(
        title=f"📜 {title}",
        description=description,
        color=color
    )

    embed.set_footer(text=f"أنت الآن في عالم: {world.capitalize()}")
    return embed


def create_status_embed(player_name: str, archetype: str, level: int, xp: int, gold: int) -> discord.Embed:
    """
    Secondary Embed for jobs, shop, achievements, stats, and global updates.
    All player-facing text must be Arabic.
    """
    embed = discord.Embed(
        title=f"👤 ملف اللاعب: {player_name}",
        color=0xf1c40f
    )

    embed.add_field(name="النمط (Archetype)", value=archetype, inline=True)
    embed.add_field(name="المستوى", value=str(level), inline=True)
    embed.add_field(name="الخبرة (XP)", value=str(xp), inline=True)
    embed.add_field(name="الذهب", value=f"{gold} 🪙", inline=True)

    embed.set_footer(text="قم بترقية مستواك عبر إنجاز المهام واكتشاف الأسرار.")
    return embed
