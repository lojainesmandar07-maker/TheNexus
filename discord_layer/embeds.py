import discord
from typing import Optional

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

def create_status_embed(player_name: str, archetype: str, level: int, xp: int, gold: int, tokens: int = 0, active_title: Optional[str] = None) -> discord.Embed:
    """
    Secondary Embed for profile, stats, and achievements.
    All player-facing text must be Arabic.
    """
    title_str = f"👤 ملف اللاعب: {player_name}"
    if active_title:
        title_str += f" | {active_title}"

    embed = discord.Embed(
        title=title_str,
        color=0xf1c40f
    )

    embed.add_field(name="النمط (Archetype)", value=archetype, inline=True)
    embed.add_field(name="المستوى", value=str(level), inline=True)
    embed.add_field(name="الخبرة (XP)", value=str(xp), inline=True)

    embed.add_field(name="الثروة", value=f"{gold} 🪙 ذهب\n{tokens} 🔮 توكنز", inline=False)

    embed.set_footer(text="استمر في إنجاز المهام واستكشاف العوالم لترقية مستواك.")
    return embed

def create_job_embed(title: str, desc: str) -> discord.Embed:
    """Embed for listing jobs."""
    embed = discord.Embed(
        title=f"📋 لوحة المهام: {title}",
        description=desc,
        color=0x2ecc71
    )
    embed.set_footer(text="أنجز المهام للحصول على مكافآت نادرة.")
    return embed

from typing import Optional, List
from domain.models import Item

def create_shop_embed(items: List[Item]) -> discord.Embed:
    """Embed for the shop loaded from live JSON data."""
    embed = discord.Embed(
        title="🛒 متجر المغامرين",
        description="استبدل ذهبك والتوكنز التي حصلت عليها بأدوات نادرة، ألقاب فخرية، ومخطوطات.",
        color=0xe67e22
    )

    for item in items:
        currency_icon = "🪙" if item.currency == "gold" else "🔮"
        embed.add_field(
            name=f"{item.name_ar} - {item.price} {currency_icon}",
            value=f"{item.desc_ar}\n*الندرة: {item.rarity}*",
            inline=False
        )

    embed.set_footer(text="الأسعار قابلة للتغيير. البضائع المباعة لا ترد ولا تستبدل.")
    return embed
