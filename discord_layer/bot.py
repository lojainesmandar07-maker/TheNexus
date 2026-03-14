import discord
from discord import app_commands
from discord.ext import commands
from discord_layer.embeds import create_story_embed, create_story_profile_embed
from engine.story_engine import StoryEngine
from domain.models import Player
import json
from typing import Union

# In a real app, use a DB. Here we use an in-memory dictionary.
players = {}
story_engine = StoryEngine()

# Admin / System Settings
bot_settings = {
    "maintenance_mode": False,
    "story_rooms": set(),
    "closed_worlds": set(),
}

def is_maintenance() -> bool:
    return bot_settings["maintenance_mode"]

# Dummy Data for tests
def get_or_create_player(user: Union[discord.User, discord.Member]) -> Player:
    if user.id not in players:
        players[user.id] = Player(
            id=user.id,
            name=user.display_name,
            unlocked_worlds=["fantasy"]
        )
    return players[user.id]

class StoryChoiceView(discord.ui.View):
    def __init__(self, bot, user_id: int, world: str, node_id: str):
        super().__init__(timeout=None)  # Persistent
        self.bot = bot
        self.user_id = user_id
        self.world = world
        self.node_id = node_id

        node = story_engine.get_node(world, node_id)
        if node and "choices" in node:
            for idx, choice in enumerate(node["choices"]):
                label = choice["text_ar"][:80]
                if choice.get("required_flag"):
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
            result = story_engine.process_choice(
                self.world,
                self.node_id,
                idx,
                player.story_flags
            )

            if result["success"]:
                if result.get("is_ending"):
                    ending = result["ending"]
                    player.completed_endings.append(ending.get("id"))

                    next_part = result.get("next_part_id")
                    if next_part:
                        # Extract the world from the next part (e.g. past_p01_a -> past)
                        next_world = next_part.split("_")[0]
                        if next_world not in player.unlocked_worlds:
                            player.unlocked_worlds.append(next_world)
                        player.story_progress[next_world] = f"{next_part}_node_000"
                        del player.story_progress[self.world]
                    else:
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
        if is_maintenance():
            await interaction.response.send_message("البوت حالياً في وضع الصيانة.", ephemeral=True)
            return

        if interaction.channel_id and bot_settings["story_rooms"] and interaction.channel_id not in bot_settings["story_rooms"]:
            await interaction.response.send_message("يجب استخدام هذا الأمر في غرف القصة المخصصة.", ephemeral=True)
            return

        if world in bot_settings["closed_worlds"]:
            await interaction.response.send_message(f"العالم '{world}' مغلق حالياً.", ephemeral=True)
            return

        if world not in story_engine.worlds:
            await interaction.response.send_message(
                f"العالم '{world}' غير موجود. العوالم المتاحة: fantasy, past, future, alternate",
                ephemeral=True
            )
            return

        player = get_or_create_player(interaction.user)
        if world not in player.unlocked_worlds:
            await interaction.response.send_message("هذا العالم مغلق بالنسبة لك. يجب اكتشافه أولاً.", ephemeral=True)
            return

        current_node_id = player.story_progress.get(world)

        if not current_node_id:
            start_node = story_engine.get_start_node(world)
            if not start_node:
                await interaction.response.send_message("تعذر العثور على بداية القصة لهذا العالم.", ephemeral=True)
                return
            current_node_id = start_node["id"]
            player.story_progress[world] = current_node_id

        node = story_engine.get_node(world, current_node_id)
        if not node:
             await interaction.response.send_message("مسار القصة تالف أو محذوف.", ephemeral=True)
             return

        embed = create_story_embed(
            title="قصتك",
            description=node["text_ar"],
            world=world
        )

        view = StoryChoiceView(bot, interaction.user.id, world, current_node_id)
        await interaction.response.send_message(embed=embed, view=view)

    @bot.tree.command(name="حالة_القصة", description="يعرض حالة اللاعب، العوالم المفتوحة والنهايات التي اكتشفها")
    async def story_status(interaction: discord.Interaction):
        if is_maintenance():
            await interaction.response.send_message("البوت حالياً في وضع الصيانة.", ephemeral=True)
            return
        player = get_or_create_player(interaction.user)
        active_world = list(player.story_progress.keys())[-1] if player.story_progress else None

        embed = create_story_profile_embed(
            player_name=player.name,
            active_world=active_world,
            unlocked_worlds=player.unlocked_worlds,
            endings=player.completed_endings
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="استمر", description="يكمل مغامرتك في آخر عالم كنت فيه")
    async def continue_story(interaction: discord.Interaction):
        if is_maintenance():
            await interaction.response.send_message("البوت حالياً في وضع الصيانة.", ephemeral=True)
            return

        if interaction.channel_id and bot_settings["story_rooms"] and interaction.channel_id not in bot_settings["story_rooms"]:
            await interaction.response.send_message("يجب استخدام هذا الأمر في غرف القصة المخصصة.", ephemeral=True)
            return

        player = get_or_create_player(interaction.user)
        last_world = None
        current_node_id = None
        for world, node_id in player.story_progress.items():
            last_world = world
            current_node_id = node_id

        if not last_world or not current_node_id:
            await interaction.response.send_message("لم تبدأ أي مغامرة بعد! استخدم `/ابدأ` لاختيار عالم.", ephemeral=True)
            return

        node = story_engine.get_node(last_world, current_node_id)
        if not node:
            await interaction.response.send_message("تعذر العثور على موقعك الحالي. حاول البدء من جديد.", ephemeral=True)
            return

        embed = create_story_embed(
            title="مغامرة مستمرة",
            description=node["text_ar"],
            world=last_world
        )

        view = StoryChoiceView(bot, interaction.user.id, last_world, current_node_id)
        await interaction.response.send_message(embed=embed, view=view)

    # ---------------- ADMIN COMMANDS ----------------

    @bot.tree.command(name="تعيين_روم_قصة", description="[أدمن] يعين هذه الروم للقصة")
    @app_commands.default_permissions(administrator=True)
    async def set_story_room(interaction: discord.Interaction):
        if interaction.channel_id:
            bot_settings["story_rooms"].add(interaction.channel_id)
            await interaction.response.send_message("تم تعيين هذه الروم كغرفة قصة بنجاح.", ephemeral=True)
        else:
            await interaction.response.send_message("حدث خطأ في تحديد الروم.", ephemeral=True)

    @bot.tree.command(name="إصلاح_جلسة", description="[أدمن] يقوم بإصلاح مسار لاعب علق في قصة أو عقدة محذوفة")
    @app_commands.describe(user="اللاعب المستهدف", world="العالم (اختياري)")
    @app_commands.default_permissions(administrator=True)
    async def repair_session(interaction: discord.Interaction, user: discord.Member, world: str = None):
        player = get_or_create_player(user)
        if world and world in player.story_progress:
            player.story_progress[world] = f"p01_a_node_000"
            await interaction.response.send_message(f"تم إعادة مسار {user.display_name} في عالم {world} للبداية.", ephemeral=True)
        else:
            player.story_progress.clear()
            await interaction.response.send_message(f"تم مسح كافة الجلسات النشطة لـ {user.display_name}. يمكنه البدء من جديد بأمان.", ephemeral=True)

    @bot.tree.command(name="نقل_لاعب", description="[أدمن] ينقل اللاعب إلى مسار قصة محدد")
    @app_commands.describe(user="اللاعب المستهدف", world="العالم", node_id="المعرف للمسار")
    @app_commands.default_permissions(administrator=True)
    async def move_player_story_state(interaction: discord.Interaction, user: discord.Member, world: str, node_id: str):
        player = get_or_create_player(user)
        player.story_progress[world] = node_id
        if world not in player.unlocked_worlds:
            player.unlocked_worlds.append(world)
        await interaction.response.send_message(f"تم نقل اللاعب {user.display_name} إلى المسار {node_id} في عالم {world}.", ephemeral=True)

    @bot.tree.command(name="إعادة_تحميل", description="[أدمن] يعيد تحميل ملفات القصة من جديد")
    @app_commands.default_permissions(administrator=True)
    async def reload_content(interaction: discord.Interaction):
        story_engine.load_stories()
        story_engine.load_endings()
        await interaction.response.send_message("تمت إعادة تحميل نصوص القصة والنهايات بنجاح.", ephemeral=True)

    @bot.tree.command(name="ارسال_رسالة", description="[أدمن] يرسل رسالة باسم البوت للروم الحالية")
    @app_commands.describe(message="محتوى الرسالة")
    @app_commands.default_permissions(administrator=True)
    async def send_message(interaction: discord.Interaction, message: str):
        await interaction.response.send_message("تم الإرسال.", ephemeral=True)
        await interaction.channel.send(message)

    @bot.tree.command(name="صيانة", description="[أدمن] يدخل البوت في وضع الصيانة")
    @app_commands.default_permissions(administrator=True)
    async def maintenance_mode(interaction: discord.Interaction):
        bot_settings["maintenance_mode"] = True
        await interaction.response.send_message("تم تفعيل وضع الصيانة. البوت لن يقبل أوامر جديدة.", ephemeral=False)

    @bot.tree.command(name="رفع_الصيانة", description="[أدمن] ينهي وضع الصيانة")
    @app_commands.default_permissions(administrator=True)
    async def end_maintenance(interaction: discord.Interaction):
        bot_settings["maintenance_mode"] = False
        await interaction.response.send_message("تم رفع وضع الصيانة.", ephemeral=False)

    @bot.tree.command(name="إعادة_تعيين_قصة", description="[أدمن] يمسح مسارات اللاعب بالكامل ويبدأ من جديد")
    @app_commands.describe(user="اللاعب المستهدف")
    @app_commands.default_permissions(administrator=True)
    async def reset_story(interaction: discord.Interaction, user: discord.Member):
        if user.id in players:
            del players[user.id]
        await interaction.response.send_message(f"تم تصفير قصة اللاعب {user.display_name} بالكامل.", ephemeral=True)
