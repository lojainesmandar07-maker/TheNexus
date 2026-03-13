import discord
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

# In a real app, use a DB. Here we use an in-memory dictionary.
players = {}
story_engine = StoryEngine()
game_engine = GameEngine()

# Dummy Data for tests
def get_or_create_player(user: discord.User) -> Player:
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
        print("Bot is ready for EPIC ARABIC ADVENTURES!")

    @bot.command()
    async def start(ctx, world: str = "fantasy"):
        """يبدأ أو يكمل مغامرتك في عالم معين"""
        if world not in story_engine.worlds:
            await ctx.send(f"العالم '{world}' غير موجود. العوالم المتاحة: fantasy, past, future, alternate")
            return

        player = get_or_create_player(ctx.author)
        current_node_id = player.story_progress.get(world)

        if not current_node_id:
            start_node = story_engine.get_start_node(world)
            if not start_node:
                await ctx.send("تعذر العثور على بداية القصة لهذا العالم.")
                return
            current_node_id = start_node["id"]
            player.story_progress[world] = current_node_id

        node = story_engine.get_node(world, current_node_id)

        embed = create_story_embed(
            title="قصتك",
            description=node["text_ar"],
            world=world
        )

        view = StoryChoiceView(bot, ctx.author.id, world, current_node_id)
        await ctx.send(embed=embed, view=view)

    @bot.command()
    async def profile(ctx):
        """يعرض ملفك الشخصي وإنجازاتك"""
        player = get_or_create_player(ctx.author)
        embed = create_status_embed(
            player_name=player.name,
            archetype=player.archetype,
            level=player.level,
            xp=player.xp,
            gold=player.gold,
            tokens=player.tokens,
            active_title=player.active_title
        )
        await ctx.send(embed=embed)

    @bot.command()
    async def jobs(ctx):
        """يعرض المهام المتاحة لنمطك من ملفات اللعبة الفعلية"""
        player = get_or_create_player(ctx.author)
        available_jobs = game_engine.get_available_jobs(player.archetype, 3)

        if not available_jobs:
            await ctx.send("لا توجد مهام متاحة لك في الوقت الحالي.")
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

            # Using default args in lambda prevents closure scope issues in loop
            async def button_callback(interaction: discord.Interaction, btn=button, j=job, v=view):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("هذه المهمة ليست لك!", ephemeral=True)
                    return

                # Prevent farming by disabling the button after use
                btn.disabled = True
                await interaction.response.edit_message(view=v)

                result = complete_job(player, j)
                msg = f"لقد أنجزت {j.title_ar}!\nحصلت على {result['gold_earned']} 🪙 و {result['xp_earned']} نقطة خبرة."

                if result.get("leveled_up"):
                    msg += f"\n🎉 **لقد ارتفع مستواك إلى {player.level}!**"
                if result.get("dropped_rare"):
                    msg += f"\n🌟 **حدث نادر:** {result['rare_event_text']}"

                await interaction.followup.send(msg, ephemeral=False)

            button.callback = button_callback
            view.add_item(button)

        await ctx.send(embed=embed, view=view)

    @bot.command()
    async def test(ctx):
        """يبدأ اختبار تحديد المصير (النمط)"""
        questions = game_engine.character_questions_cache
        if not questions:
            await ctx.send("الاختبار غير متوفر حالياً.")
            return

        embed = create_test_embed(questions[0]["text_ar"], 1, len(questions))
        view = TestView(bot, ctx.author.id)
        await ctx.send(embed=embed, view=view)

    @bot.command()
    async def quests(ctx):
        """يعرض المهام الطويلة المتاحة"""
        player = get_or_create_player(ctx.author)
        available_quests = game_engine.get_available_quests(player.archetype, 2)

        if not available_quests:
            await ctx.send("لا توجد مهام كبرى متاحة لك.")
            return

        embed = create_quests_embed(available_quests)
        view = discord.ui.View()

        for quest in available_quests:
            button = discord.ui.Button(
                label=f"ابدأ المهمة: {quest.title_ar[:50]}",
                style=discord.ButtonStyle.success,
                custom_id=f"quest_start_{quest.id}"
            )

            async def quest_callback(interaction: discord.Interaction, btn=button, q=quest, v=view):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("هذه المهمة لغيرك!", ephemeral=True)
                    return

                btn.disabled = True
                await interaction.response.edit_message(view=v)

                result = complete_quest(player, q)
                msg = f"لقد أكملت المهمة {q.title_ar}!\nحصلت على {result['gold_earned']} 🪙 و {result['xp_earned']} نقطة خبرة."
                if result.get("item_gained"):
                    msg += f"\n🎁 **حصلت على أداة:** {result['item_gained']}"

                await interaction.followup.send(msg, ephemeral=False)

            button.callback = quest_callback
            view.add_item(button)

        await ctx.send(embed=embed, view=view)

    @bot.command()
    async def achievements(ctx):
        """يعرض لوحة الإنجازات"""
        import random
        achv_list = game_engine.achievements_cache
        if not achv_list:
            await ctx.send("لا توجد إنجازات مسجلة.")
            return

        sample = random.sample(achv_list, min(len(achv_list), 5))
        embed = create_achievements_embed(sample)
        await ctx.send(embed=embed)

    @bot.command()
    async def shop(ctx):
        """يعرض متجر اللعبة من الملفات الفعلية"""
        player = get_or_create_player(ctx.author)
        shop_items = game_engine.get_shop_items(5)

        if not shop_items:
            await ctx.send("المتجر مغلق حالياً.")
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

            async def shop_callback(interaction: discord.Interaction, btn=button, i=item, v=view):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("تحدث مع التاجر من حسابك الخاص!", ephemeral=True)
                    return

                result = buy_item(player, i)

                # If successful, optionally disable button to prevent double-charging by mistake
                if result["success"]:
                    btn.disabled = True
                    await interaction.response.edit_message(view=v)
                    await interaction.followup.send(result["message"], ephemeral=False)
                else:
                    await interaction.response.send_message(result["message"], ephemeral=True)

            button.callback = shop_callback
            view.add_item(button)

        await ctx.send(embed=embed, view=view)
