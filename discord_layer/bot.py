import discord
from discord.ext import commands
from discord_layer.embeds import create_story_embed, create_status_embed, create_shop_embed, create_job_embed
from engine.story_engine import StoryEngine
from engine.game_engine import GameEngine
from services.logic import complete_job, buy_item
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
            archetype="المستكشف" # Default to Arabic equivalent to match JSON locks
        )
    return players[user.id]

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
                player.xp += result.get("reward_xp", 10)

                if result.get("is_ending"):
                    ending = result["ending"]
                    player.story_progress[self.world] = "p01_a_node_000"
                    embed = create_story_embed(
                        title=ending.get("title_ar", "نهاية الرحلة"),
                        description=ending.get("text_ar", "وصلت إلى نهاية هذا المسار."),
                        world=self.world
                    )
                    await interaction.response.edit_message(embed=embed, view=None)
                    return

                next_node = result["next_node"]
                player.story_progress[self.world] = next_node["id"]
                description = next_node["text_ar"]
                if result.get("check_failed") and result.get("outcome_message"):
                    description = f"⚠️ {result['outcome_message']}\n\n{description}"
                embed = create_story_embed(
                    title="مغامرة مستمرة",
                    description=description,
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
            async def button_callback(interaction: discord.Interaction, j=job):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("هذه المهمة ليست لك!", ephemeral=True)
                    return

                result = complete_job(player, j)
                msg = f"لقد أنجزت {j.title_ar}!\nحصلت على {result['gold_earned']} 🪙 و {result['xp_earned']} XP."

                if result.get("leveled_up"):
                    msg += f"\n🎉 **لقد ارتفع مستواك إلى {player.level}!**"
                if result.get("dropped_rare"):
                    msg += f"\n🌟 **حدث نادر:** {result['rare_event_text']}"

                await interaction.response.send_message(msg, ephemeral=False)

            button.callback = button_callback
            view.add_item(button)

        await ctx.send(embed=embed, view=view)

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

            async def shop_callback(interaction: discord.Interaction, i=item):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("تحدث مع التاجر من حسابك الخاص!", ephemeral=True)
                    return

                result = buy_item(player, i)
                await interaction.response.send_message(result["message"], ephemeral=not result["success"])

            button.callback = shop_callback
            view.add_item(button)

        await ctx.send(embed=embed, view=view)
