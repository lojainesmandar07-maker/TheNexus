import discord
from typing import Optional

def create_story_embed(title: str, description: str, world: str = "fantasy") -> discord.Embed:
    """
    Primary Embed for story progression, narrative text, and active quests.
    All player-facing text must be Arabic.
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

    embed.set_footer(text=f"أنت الآن في عالم: {world_ar}")
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

    embed.add_field(name="النمط", value=archetype, inline=True)
    embed.add_field(name="المستوى", value=str(level), inline=True)
    embed.add_field(name="الخبرة", value=str(xp), inline=True)

    embed.add_field(name="الثروة", value=f"{gold} 🪙 عملة ذهبية\n{tokens} 🔮 رموز سحرية", inline=False)

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
from domain.models import Item, Quest

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

def create_test_embed(question_text: str, question_index: int, total_questions: int) -> discord.Embed:
    """Embed for the personality test."""
    embed = discord.Embed(
        title="🔮 اختبار تحديد المصير",
        description=question_text,
        color=0x9b59b6
    )
    embed.set_footer(text=f"سؤال {question_index} من {total_questions}")
    return embed

def create_quests_embed(quests: List[Quest]) -> discord.Embed:
    """Embed for the active quests."""
    embed = discord.Embed(
        title="📜 المهام المتاحة",
        description="أكمل هذه المهام للحصول على مكافآت كبرى وسمعة للفصائل.",
        color=0x3498db
    )

    for quest in quests:
        stages_str = "\n".join([f"- {s['stage_ar']}" for s in quest.stages])
        embed.add_field(
            name=quest.title_ar,
            value=f"{quest.desc_ar}\n**المراحل:**\n{stages_str}\n**المكافأة:** {quest.reward_gold} 🪙",
            inline=False
        )

    embed.set_footer(text="اختر مهمة لتبدأ مغامرتك.")
    return embed

def create_achievements_embed(achievements: List[dict]) -> discord.Embed:
    """Embed for achievements display."""
    embed = discord.Embed(
        title="🏆 لوحة الشرف",
        description="إنجازات يمكن تحقيقها لرفع مكانتك بين المغامرين.",
        color=0xf1c40f
    )

    for achv in achievements:
        embed.add_field(
            name=achv["title_ar"],
            value=f"{achv['desc_ar']}\n**المكافأة:** {achv['reward_title']} | {achv['reward_gold']} 🪙",
            inline=False
        )

    embed.set_footer(text="الأساطير لا تُولد، بل تُصنع.")
    return embed
