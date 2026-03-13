import discord
from discord import app_commands
from discord.ext import commands
from discord_layer.embeds import (
    create_story_embed, create_status_embed, create_shop_embed,
    create_job_embed, create_test_embed, create_quests_embed, create_achievements_embed
)
from engine.story_engine import StoryEngine
from engine.game_engine import GameEngine
from services.logic import complete_job, buy_item, complete_quest
from domain.models import Player
import json
from typing import Union

# In a real app, use a DB. Here we use an in-memory dictionary.
players = {}
story_engine = StoryEngine()
game_engine = GameEngine()

# Dummy Data for tests
def get_or_create_player(user: Union[discord.User, discord.Member]) -> Player:
    if user.id not in players:
        players[user.id] = Player(
            id=user.id,
            name=user.display_name,
            archetype="مبتدئ" # Starts as beginner until they take !test
        )
    return players[user.id]

class TestView(discord.ui.View):
    def __init__(self, bot, user_id: int, question_index: int = 0, scores: dict = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.question_index = question_index
        self.scores = scores if scores is not None else {}

        questions = game_engine.character_questions_cache

        if self.question_index < len(questions):
            q = questions[self.question_index]
            for idx, ans in enumerate(q["answers"]):
                button = discord.ui.Button(
                    label=ans["text_ar"][:80],
                    style=discord.ButtonStyle.primary,
                    custom_id=f"test_ans_{self.question_index}_{idx}"
                )

                async def answer_callback(interaction: discord.Interaction, b=button, a=ans):
                    if interaction.user.id != self.user_id:
                        await interaction.response.send_message("هذا الاختبار ليس لك!", ephemeral=True)
                        return

                    # Tally scores
                    for arch, weight in a["archetype_weight"].items():
                        self.scores[arch] = self.scores.get(arch, 0) + weight

                    next_idx = self.question_index + 1
                    qs = game_engine.character_questions_cache

                    if next_idx < len(qs):
                        next_q = qs[next_idx]
                        embed = create_test_embed(next_q["text_ar"], next_idx + 1, len(qs))
                        view = TestView(self.bot, self.user_id, next_idx, self.scores)
                        await interaction.response.edit_message(embed=embed, view=view)
                    else:
                        # Determine winning archetype
                        best_arch = max(self.scores, key=self.scores.get)
                        player = get_or_create_player(interaction.user)
                        player.archetype = best_arch

                        result_embed = discord.Embed(
                            title="🎉 اكتمل الاختبار",
                            description=f"لقد تحدد مصيرك! نمطك هو: **{best_arch}**.\nانطلق الآن واكتشف العالم بهذا النمط.",
                            color=0x2ecc71
                        )
                        await interaction.response.edit_message(embed=result_embed, view=None)

                button.callback = answer_callback
                self.add_item(button)


class StoryChoiceView(discord.ui.View):
    def __init__(self, bot, user_id: int, world: str, node_id: str):
        super().__init__(timeout=None) # Persistent
        self.bot = bot
        self.user_id = user_id
        self.world = world
        self.node_id = node_id

        node = story_engine.get_node(world, node_id)
        if node and "choices" in node:
            for idx, choice in enumerate(node["choices"]):
                # Truncate label if it's too long
                label = choice["text_ar"][:80]
                if choice.get("required_archetype"):
                    label = f"✨ {label}"

                button = discord.ui.Button(
                    label=label,
                    style=discord.ButtonStyle.primary,
                    custom_id=f"story_{world}_{node_id}_{idx}"
                )
                button.callback = self.create_callback(idx)
                self.add_item(button)

    def create_callback(self, idx: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("هذه القصة ليست لك!", ephemeral=True)
                return

            player = get_or_create_player(interaction.user)
            result = story_engine.process_choice(self.world, self.node_id, idx, player.archetype, player.stats)

            if result["success"]:
                next_node = result["next_node"]
                player.story_progress[self.world] = next_node["id"]
                player.xp += result.get("reward_xp", 10)

                embed = create_story_embed(
                    title="مغامرة مستمرة",
                    description=next_node["text_ar"],
                    world=self.world
                )
                view = StoryChoiceView(self.bot, self.user_id, self.world, next_node["id"])
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                await interaction.response.send_message(result["message"], ephemeral=True)
        return callback


def setup_bot(bot: commands.Bot):

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")
        print("Syncing slash commands...")
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
        print("Bot is ready for EPIC ARABIC ADVENTURES!")

    @bot.tree.command(name="ابدأ", description="يبدأ أو يكمل مغامرتك في عالم معين")
    @app_commands.describe(world="اختر العالم: fantasy, past, future, alternate")
    async def start(interaction: discord.Interaction, world: str = "fantasy"):
        if world not in story_engine.worlds:
            await interaction.response.send_message(f"العالم '{world}' غير موجود. العوالم المتاحة: fantasy, past, future, alternate", ephemeral=True)
            return

        player = get_or_create_player(interaction.user)
        current_node_id = player.story_progress.get(world)

        if not current_node_id:
            start_node = story_engine.get_start_node(world)
            if not start_node:
                await interaction.response.send_message("تعذر العثور على بداية القصة لهذا العالم.", ephemeral=True)
                return
            current_node_id = start_node["id"]
            player.story_progress[world] = current_node_id

        node = story_engine.get_node(world, current_node_id)

        embed = create_story_embed(
            title="قصتك",
            description=node["text_ar"],
            world=world
        )

        view = StoryChoiceView(bot, interaction.user.id, world, current_node_id)
        await interaction.response.send_message(embed=embed, view=view)

    @bot.tree.command(name="ملفي", description="يعرض ملفك الشخصي وإنجازاتك")
    async def profile(interaction: discord.Interaction):
        player = get_or_create_player(interaction.user)
        embed = create_status_embed(
            player_name=player.name,
            archetype=player.archetype,
            level=player.level,
            xp=player.xp,
            gold=player.gold,
            tokens=player.tokens,
            active_title=player.active_title
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="المهام", description="يعرض المهام المتاحة لنمطك")
    async def jobs(interaction: discord.Interaction):
        player = get_or_create_player(interaction.user)
        available_jobs = game_engine.get_available_jobs(player.archetype, 3)

        if not available_jobs:
            await interaction.response.send_message("لا توجد مهام متاحة لك في الوقت الحالي.", ephemeral=True)
            return

        embed = create_job_embed("لوحة المهام المفتوحة", "اختر إحدى المهام أدناه لإنجازها وجمع الغنائم.")
        view = discord.ui.View()

        for job in available_jobs:
            embed.add_field(
                name=job.title_ar,
                value=f"{job.desc_ar}\n**المكافأة:** {job.base_reward_gold} 🪙 | {job.base_reward_xp} XP",
                inline=False
            )

            button = discord.ui.Button(
                label=f"قبول: {job.title_ar[:50]}",
                style=discord.ButtonStyle.success,
                custom_id=f"job_accept_{job.id}"
            )

            async def button_callback(inter: discord.Interaction, btn=button, j=job, v=view):
                if inter.user.id != interaction.user.id:
                    await inter.response.send_message("هذه المهمة ليست لك!", ephemeral=True)
                    return

                btn.disabled = True
                await inter.response.edit_message(view=v)

                result = complete_job(player, j)
                msg = f"لقد أنجزت {j.title_ar}!\nحصلت على {result['gold_earned']} 🪙 و {result['xp_earned']} نقطة خبرة."

                if result.get("leveled_up"):
                    msg += f"\n🎉 **لقد ارتفع مستواك إلى {player.level}!**"
                if result.get("dropped_rare"):
                    msg += f"\n🌟 **حدث نادر:** {result['rare_event_text']}"

                await inter.followup.send(msg, ephemeral=False)

            button.callback = button_callback
            view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

    @bot.tree.command(name="اختبار", description="يبدأ اختبار تحديد المصير (النمط)")
    async def test(interaction: discord.Interaction):
        questions = game_engine.character_questions_cache
        if not questions:
            await interaction.response.send_message("الاختبار غير متوفر حالياً.", ephemeral=True)
            return

        embed = create_test_embed(questions[0]["text_ar"], 1, len(questions))
        view = TestView(bot, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @bot.tree.command(name="مهمات_كبرى", description="يعرض المهام الطويلة المتاحة")
    async def quests(interaction: discord.Interaction):
        player = get_or_create_player(interaction.user)
        available_quests = game_engine.get_available_quests(player.archetype, 2)

        if not available_quests:
            await interaction.response.send_message("لا توجد مهام كبرى متاحة لك.", ephemeral=True)
            return

        embed = create_quests_embed(available_quests)
        view = discord.ui.View()

        for quest in available_quests:
            button = discord.ui.Button(
                label=f"ابدأ المهمة: {quest.title_ar[:50]}",
                style=discord.ButtonStyle.success,
                custom_id=f"quest_start_{quest.id}"
            )

            async def quest_callback(inter: discord.Interaction, btn=button, q=quest, v=view):
                if inter.user.id != interaction.user.id:
                    await inter.response.send_message("هذه المهمة لغيرك!", ephemeral=True)
                    return

                btn.disabled = True
                await inter.response.edit_message(view=v)

                result = complete_quest(player, q)
                msg = f"لقد أكملت المهمة {q.title_ar}!\nحصلت على {result['gold_earned']} 🪙 و {result['xp_earned']} نقطة خبرة."
                if result.get("item_gained"):
                    msg += f"\n🎁 **حصلت على أداة:** {result['item_gained']}"

                await inter.followup.send(msg, ephemeral=False)

            button.callback = quest_callback
            view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

    @bot.tree.command(name="انجازات", description="يعرض لوحة الإنجازات")
    async def achievements(interaction: discord.Interaction):
        import random
        achv_list = game_engine.achievements_cache
        if not achv_list:
            await interaction.response.send_message("لا توجد إنجازات مسجلة.", ephemeral=True)
            return

        sample = random.sample(achv_list, min(len(achv_list), 5))
        embed = create_achievements_embed(sample)
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="متجر", description="يعرض متجر اللعبة")
    async def shop(interaction: discord.Interaction):
        player = get_or_create_player(interaction.user)
        shop_items = game_engine.get_shop_items(5)

        if not shop_items:
            await interaction.response.send_message("المتجر مغلق حالياً.", ephemeral=True)
            return

        embed = create_shop_embed(shop_items)
        view = discord.ui.View()

        for item in shop_items:
            currency_icon = "🪙" if item.currency == "gold" else "🔮"
            button = discord.ui.Button(
                label=f"شراء: {item.name_ar[:50]} ({item.price} {currency_icon})",
                style=discord.ButtonStyle.primary,
                custom_id=f"shop_buy_{item.id}"
            )

            async def shop_callback(inter: discord.Interaction, btn=button, i=item, v=view):
                if inter.user.id != interaction.user.id:
                    await inter.response.send_message("تحدث مع التاجر من حسابك الخاص!", ephemeral=True)
                    return

                result = buy_item(player, i)

                if result["success"]:
                    btn.disabled = True
                    await inter.response.edit_message(view=v)
                    await inter.followup.send(result["message"], ephemeral=False)
                else:
                    await inter.response.send_message(result["message"], ephemeral=True)

            button.callback = shop_callback
            view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)
