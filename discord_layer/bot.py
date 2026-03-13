import discord
from discord.ext import commands
from discord_layer.embeds import create_story_embed, create_status_embed, create_shop_embed, create_job_embed
from engine.story_engine import StoryEngine
from domain.models import Player
import json

# In a real app, use a DB. Here we use an in-memory dictionary.
players = {}
story_engine = StoryEngine()

# Dummy Data for tests
def get_or_create_player(user: discord.User) -> Player:
    if user.id not in players:
        players[user.id] = Player(
            id=user.id,
            name=user.display_name,
            archetype="explorer" # Default to explorer for now
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
        """يعرض المهام المتاحة (محاكاة)"""
        # In a real app we'd load these from the generator output
        embed = create_job_embed("مهام الفصيل", "تتوفر مهام جديدة لنمطك الخاص. تفقدها الآن للحصول على موارد نادرة وتوكنز.")
        # Mock view
        view = discord.ui.View()
        button_accept = discord.ui.Button(label="قبول المهمة العشوائية", style=discord.ButtonStyle.success, custom_id="job_accept")
        view.add_item(button_accept)
        await ctx.send(embed=embed, view=view)

    @bot.command()
    async def shop(ctx):
        """يعرض متجر اللعبة"""
        embed = create_shop_embed()
        await ctx.send(embed=embed)
