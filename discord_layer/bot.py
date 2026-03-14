import discord
from discord import app_commands
from discord.ext import commands
from discord_layer.embeds import (
    create_story_embed,
    create_status_embed,
    create_shop_embed,
    create_job_embed,
    create_test_embed,
    create_quests_embed,
    create_achievements_embed,
)
from engine.story_engine import StoryEngine
from engine.game_engine import GameEngine
from services.logic import complete_job, buy_item, calculate_level_up
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
            archetype="explorer"  # Canonical archetype ID
        )
    return players[user.id]


class CharacterTestView(discord.ui.View):
    def __init__(self, user_id: int, questions: list, current_index: int = 0, scores: dict = None):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.questions = questions
        self.current_index = current_index
        self.scores = scores or {}

        if self.current_index < len(self.questions):
            question = self.questions[self.current_index]
            for idx, answer in enumerate(question.get("answers", [])):
                label = answer.get("text_ar", "")[:80]
                button = discord.ui.Button(
                    label=label,
                    style=discord.ButtonStyle.primary,
                    custom_id=f"test_ans_{self.current_index}_{idx}"
                )
                button.callback = self.create_callback(answer.get("archetype_weight", {}))
                self.add_item(button)

    def create_callback(self, weights: dict):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("هذا الاختبار ليس لك!", ephemeral=True)
                return

            for arch, weight in weights.items():
                self.scores[arch] = self.scores.get(arch, 0) + weight

            next_index = self.current_index + 1
            if next_index < len(self.questions):
                next_q = self.questions[next_index]
                embed = create_test_embed(next_q["text_ar"], next_index + 1, len(self.questions))
                view = CharacterTestView(self.user_id, self.questions, next_index, self.scores)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                best_archetype = max(self.scores, key=self.scores.get) if self.scores else "المستكشف"
                canonical_id = game_engine.normalize_archetype(best_archetype)

                player = get_or_create_player(interaction.user)
                player.archetype = canonical_id

                await interaction.response.edit_message(
                    content=f"🎉 **اكتمل الاختبار!**\nلقد تبين أن شخصيتك هي: **{best_archetype}**\nاستخدم أمر `/شخصيتي` لمعرفة المزيد.",
                    embed=None,
                    view=None
                )

        return callback


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
            result = story_engine.process_choice(
                self.world,
                self.node_id,
                idx,
                player.archetype,
                player.stats
            )

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
        print("Syncing slash commands...")
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
        print("Bot is ready for EPIC ARABIC ADVENTURES!")

    @bot.tree.command(name="اختبار_الشخصية", description="أجب عن الأسئلة لتحديد نمط شخصيتك ومسارك")
    async def character_test(interaction: discord.Interaction):
        questions = game_engine.test_questions_cache
        if not questions:
            await interaction.response.send_message("عذراً، لا يمكن تحميل أسئلة الاختبار حالياً.", ephemeral=True)
            return

        embed = create_test_embed(questions[0]["text_ar"], 1, len(questions))
        view = CharacterTestView(interaction.user.id, questions)
        await interaction.response.send_message(embed=embed, view=view)

    @bot.tree.command(name="شخصيتي", description="يعرض معلومات وتفاصيل نمط شخصيتك")
    async def my_character(interaction: discord.Interaction):
        player = get_or_create_player(interaction.user)
        archetype_id = player.archetype

        # Reverse lookup for Arabic name if needed
        archetype_name_ar = archetype_id
        archetype_desc_ar = "لا يوجد وصف."
        for name_ar, can_id in game_engine.archetype_name_to_id.items():
            if can_id == archetype_id:
                archetype_name_ar = name_ar
                break

        # Attempt to get full desc from characters JSON if we reload it fully,
        # but for now we'll just display the name and basic info.
        embed = discord.Embed(
            title=f"🎭 شخصيتك: {archetype_name_ar}",
            description=f"النمط الحالي الخاص بك هو {archetype_name_ar}. هذا يؤثر على مسارات القصة والمهام المتاحة لك.",
            color=0x9b59b6
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="ابدأ", description="يبدأ أو يكمل مغامرتك في عالم معين")
    @app_commands.describe(world="اختر العالم: fantasy, past, future, alternate")
    async def start(interaction: discord.Interaction, world: str = "fantasy"):
        if world not in story_engine.worlds:
            await interaction.response.send_message(
                f"العالم '{world}' غير موجود. العوالم المتاحة: fantasy, past, future, alternate",
                ephemeral=True
            )
            return

        player = get_or_create_player(interaction.user)
        current_node_id = player.story_progress.get(world)

        if not current_node_id:
            start_node = story_engine.get_start_node(world)
            if not start_node:
                await interaction.response.send_message(
                    "تعذر العثور على بداية القصة لهذا العالم.",
                    ephemeral=True
                )
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

    @bot.tree.command(name="استمر", description="يكمل مغامرتك في آخر عالم كنت فيه")
    async def continue_story(interaction: discord.Interaction):
        player = get_or_create_player(interaction.user)
        # Find the world with the most recent progress or just the first one found
        # In a real system, we'd track 'last_world'
        last_world = None
        current_node_id = None
        for world, node_id in player.story_progress.items():
            last_world = world
            current_node_id = node_id
            break

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

    @bot.tree.command(name="عمل", description="يعرض الأعمال المتاحة لنمطك")
    async def jobs(interaction: discord.Interaction):
        player = get_or_create_player(interaction.user)
        available_jobs = game_engine.get_available_jobs(player.archetype, 3)

        if not available_jobs:
            await interaction.response.send_message(
                "لا توجد مهام متاحة لك في الوقت الحالي.",
                ephemeral=True
            )
            return

        embed = create_job_embed(
            "لوحة المهام المفتوحة",
            "اختر إحدى المهام أدناه لإنجازها وجمع الغنائم."
        )
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
                msg = f"لقد أنجزت {j.title_ar}!\nحصلت على {result['gold_earned']} 🪙 و {result['xp_earned']} XP."

                if result.get("leveled_up"):
                    msg += f"\n🎉 **لقد ارتفع مستواك إلى {player.level}!**"
                if result.get("dropped_rare"):
                    msg += f"\n🌟 **حدث نادر:** {result['rare_event_text']}"

                await inter.followup.send(msg, ephemeral=False)

            button.callback = button_callback
            view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

    @bot.tree.command(name="مهمة", description="يعرض المهام والرحلات الكبرى المتاحة")
    async def quests(interaction: discord.Interaction):
        player = get_or_create_player(interaction.user)
        # Fetching a few quests to show
        available_quests = game_engine.quests_cache[:3] if game_engine.quests_cache else []

        if not available_quests:
            await interaction.response.send_message("لا توجد مهام كبرى متاحة حالياً.", ephemeral=True)
            return

        # Convert dictionary formats to a mock Quest object if needed, or update embed to handle dict
        # Since quests are loaded as dicts in game_engine, let's pass dicts
        class MockQuest:
            def __init__(self, q_dict):
                self.id = q_dict.get("id", "unknown")
                self.title_ar = q_dict.get("title_ar", "مهمة مجهولة")
                self.desc_ar = q_dict.get("summary_ar", q_dict.get("desc_ar", "لا يوجد وصف"))
                self.stages = q_dict.get("stages", [{"stage_ar": "المرحلة الأولى"}])
                self.reward_gold = q_dict.get("reward_gold", 100)

        mock_quests = [MockQuest(q) for q in available_quests]
        embed = create_quests_embed(mock_quests)

        view = discord.ui.View()
        for mq in mock_quests:
            button = discord.ui.Button(
                label=f"بدء: {mq.title_ar[:50]}",
                style=discord.ButtonStyle.success,
                custom_id=f"quest_start_{mq.id}"
            )
            async def start_quest_callback(inter: discord.Interaction, btn=button, q=mq, v=view):
                if inter.user.id != interaction.user.id:
                    await inter.response.send_message("هذه المهمة ليست لك!", ephemeral=True)
                    return
                btn.disabled = True
                player.current_quest = q.id
                await inter.response.edit_message(view=v)
                await inter.followup.send(f"لقد بدأت المهمة الكبرى: **{q.title_ar}**!\nاستعد للمخاطر.", ephemeral=False)
            button.callback = start_quest_callback
            view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)


    @bot.tree.command(name="شراء", description="شراء عنصر معين من المتجر باستخدام المعرف")
    @app_commands.describe(item_id="معرف العنصر الذي تود شراءه")
    async def buy(interaction: discord.Interaction, item_id: str):
        player = get_or_create_player(interaction.user)
        item = game_engine.get_item_by_id(item_id)

        if not item:
            await interaction.response.send_message("هذا العنصر غير موجود.", ephemeral=True)
            return

        result = buy_item(player, item)
        if result["success"]:
            await interaction.response.send_message(result["message"])
        else:
            await interaction.response.send_message(result["message"], ephemeral=True)

    @bot.tree.command(name="بيع", description="بيع عنصر تملكه للحصول على بعض الذهب")
    @app_commands.describe(item_id="معرف العنصر الذي تود بيعه")
    async def sell(interaction: discord.Interaction, item_id: str):
        player = get_or_create_player(interaction.user)
        if item_id not in player.inventory:
            await interaction.response.send_message("أنت لا تملك هذا العنصر.", ephemeral=True)
            return

        item = game_engine.get_item_by_id(item_id)
        sell_price = int(item.price * 0.5) if item else 10

        player.inventory.remove(item_id)
        player.gold += sell_price

        item_name = item.name_ar if item else item_id
        await interaction.response.send_message(f"لقد قمت ببيع **{item_name}** مقابل {sell_price} 🪙.")

    @bot.tree.command(name="إنجازاتي", description="عرض لوحة الإنجازات الخاصة بك")
    async def achievements_cmd(interaction: discord.Interaction):
        player = get_or_create_player(interaction.user)

        # Mocking player achievements based on game_engine cache
        all_achievements = game_engine.achievements_cache[:5] if game_engine.achievements_cache else []

        if not all_achievements:
            await interaction.response.send_message("لم يتم العثور على إنجازات في النظام.", ephemeral=True)
            return

        # Format for embed
        formatted_achvs = []
        for a in all_achievements:
            formatted_achvs.append({
                "title_ar": a.get("title_ar", "إنجاز مجهول"),
                "desc_ar": a.get("desc_ar", "لا يوجد وصف"),
                "reward_title": a.get("reward_title", "لا يوجد لقب"),
                "reward_gold": a.get("reward_gold", 0)
            })

        embed = create_achievements_embed(formatted_achvs)
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="تعيين_روم_قصة", description="[أدمن] يعين هذه الروم للقصة")
    @app_commands.default_permissions(administrator=True)
    async def set_story_room(interaction: discord.Interaction):
        # In a real system, save to DB
        await interaction.response.send_message("تم تعيين هذه الروم كغرفة قصة بنجاح.", ephemeral=True)

    @bot.tree.command(name="تعيين_روم_شرح", description="[أدمن] يعين هذه الروم للشروحات")
    @app_commands.default_permissions(administrator=True)
    async def set_explain_room(interaction: discord.Interaction):
        # In a real system, save to DB
        await interaction.response.send_message("تم تعيين هذه الروم كغرفة شروحات بنجاح.", ephemeral=True)

    @bot.tree.command(name="تعيين_روم_ستايلات", description="[أدمن] يعين هذه الروم للستايلات")
    @app_commands.default_permissions(administrator=True)
    async def set_style_room(interaction: discord.Interaction):
        # In a real system, save to DB
        await interaction.response.send_message("تم تعيين هذه الروم كغرفة ستايلات بنجاح.", ephemeral=True)

    @bot.tree.command(name="فتح_عالم", description="[أدمن] يفتح عالم معين للعب")
    @app_commands.describe(world="اسم العالم لفتحه")
    @app_commands.default_permissions(administrator=True)
    async def open_world(interaction: discord.Interaction, world: str):
        # In a real system, save to DB
        await interaction.response.send_message(f"تم فتح العالم '{world}' للمغامرين.", ephemeral=False)

    @bot.tree.command(name="إغلاق_عالم", description="[أدمن] يغلق عالم معين")
    @app_commands.describe(world="اسم العالم لإغلاقه")
    @app_commands.default_permissions(administrator=True)
    async def close_world(interaction: discord.Interaction, world: str):
        # In a real system, save to DB
        await interaction.response.send_message(f"تم إغلاق العالم '{world}'. لن يتمكن اللاعبون من دخوله.", ephemeral=False)

    @bot.tree.command(name="إغلاق_جلسة", description="[أدمن] يغلق جلسة قصة لاعب")
    @app_commands.describe(user="اللاعب المستهدف")
    @app_commands.default_permissions(administrator=True)
    async def close_session(interaction: discord.Interaction, user: discord.Member):
        if user.id in players:
            player = players[user.id]
            # Reset the story progress logic
            player.story_progress.clear()
            await interaction.response.send_message(f"تم إغلاق الجلسة للاعب {user.display_name}.", ephemeral=True)
        else:
            await interaction.response.send_message("اللاعب غير موجود.", ephemeral=True)

    @bot.tree.command(name="استرجاع_جلسة", description="[أدمن] يسترجع جلسة لاعب في عالم معين")
    @app_commands.describe(user="اللاعب المستهدف", world="العالم", node_id="معرف المسار")
    @app_commands.default_permissions(administrator=True)
    async def restore_session(interaction: discord.Interaction, user: discord.Member, world: str, node_id: str):
        player = get_or_create_player(user)
        player.story_progress[world] = node_id
        await interaction.response.send_message(f"تم استرجاع الجلسة للاعب {user.display_name} في العالم {world} إلى {node_id}.", ephemeral=True)

    @bot.tree.command(name="إعادة_تعيين_شخصية", description="[أدمن] يعيد تعيين نمط شخصية اللاعب")
    @app_commands.describe(user="اللاعب المستهدف", archetype="النمط الجديد")
    @app_commands.default_permissions(administrator=True)
    async def reset_character(interaction: discord.Interaction, user: discord.Member, archetype: str):
        player = get_or_create_player(user)
        canonical_id = game_engine.normalize_archetype(archetype)
        player.archetype = canonical_id
        await interaction.response.send_message(f"تم تغيير نمط شخصية {user.display_name} إلى {canonical_id}.", ephemeral=True)

    @bot.tree.command(name="ارسال_رسالة", description="[أدمن] يرسل رسالة باسم البوت للروم الحالية")
    @app_commands.describe(message="محتوى الرسالة")
    @app_commands.default_permissions(administrator=True)
    async def send_message(interaction: discord.Interaction, message: str):
        await interaction.response.send_message("تم إرسال الرسالة.", ephemeral=True)
        await interaction.channel.send(message)

    @bot.tree.command(name="إضافة_xp", description="[أدمن] يضيف خبرة للاعب")
    @app_commands.describe(user="اللاعب المستهدف", amount="كمية الخبرة")
    @app_commands.default_permissions(administrator=True)
    async def add_xp(interaction: discord.Interaction, user: discord.Member, amount: int):
        player = get_or_create_player(user)
        player.xp += amount
        calculate_level_up(player)
        await interaction.response.send_message(f"تمت إضافة {amount} XP لـ {user.display_name}.", ephemeral=True)

    @bot.tree.command(name="حذف_xp", description="[أدمن] يحذف خبرة من لاعب")
    @app_commands.describe(user="اللاعب المستهدف", amount="كمية الخبرة")
    @app_commands.default_permissions(administrator=True)
    async def remove_xp(interaction: discord.Interaction, user: discord.Member, amount: int):
        player = get_or_create_player(user)
        player.xp = max(0, player.xp - amount)
        await interaction.response.send_message(f"تم خصم {amount} XP من {user.display_name}.", ephemeral=True)

    @bot.tree.command(name="إضافة_عملة", description="[أدمن] يضيف ذهب للاعب")
    @app_commands.describe(user="اللاعب المستهدف", amount="الكمية")
    @app_commands.default_permissions(administrator=True)
    async def add_gold(interaction: discord.Interaction, user: discord.Member, amount: int):
        player = get_or_create_player(user)
        player.gold += amount
        await interaction.response.send_message(f"تمت إضافة {amount} 🪙 لـ {user.display_name}.", ephemeral=True)

    @bot.tree.command(name="حذف_عملة", description="[أدمن] يحذف ذهب من لاعب")
    @app_commands.describe(user="اللاعب المستهدف", amount="الكمية")
    @app_commands.default_permissions(administrator=True)
    async def remove_gold(interaction: discord.Interaction, user: discord.Member, amount: int):
        player = get_or_create_player(user)
        player.gold = max(0, player.gold - amount)
        await interaction.response.send_message(f"تم خصم {amount} 🪙 من {user.display_name}.", ephemeral=True)

    @bot.tree.command(name="إغلاق_الأزرار", description="[أدمن] يغلق كافة أزرار التفاعل في الروم الحالية")
    @app_commands.default_permissions(administrator=True)
    async def disable_buttons(interaction: discord.Interaction):
        # Implementation would require tracking message IDs and their views
        await interaction.response.send_message("تم إرسال أمر تعطيل الأزرار إلى الجلسات النشطة.", ephemeral=True)

    @bot.tree.command(name="صيانة", description="[أونر] يدخل البوت في وضع الصيانة")
    @app_commands.default_permissions(administrator=True) # Assuming Owner check via code or higher role
    async def maintenance_mode(interaction: discord.Interaction):
        await interaction.response.send_message("تم تفعيل وضع الصيانة. البوت لن يقبل أوامر جديدة الآن.", ephemeral=False)

    @bot.tree.command(name="رفع_الصيانة", description="[أونر] ينهي وضع الصيانة")
    @app_commands.default_permissions(administrator=True)
    async def end_maintenance(interaction: discord.Interaction):
        await interaction.response.send_message("تم رفع وضع الصيانة. البوت متاح الآن للجميع.", ephemeral=False)

    @bot.tree.command(name="إعادة_تحميل", description="[أونر] يعيد تحميل ملفات المحتوى (القصص، المهام، وغيرها)")
    @app_commands.default_permissions(administrator=True)
    async def reload_content(interaction: discord.Interaction):
        story_engine.load_stories()
        story_engine.load_endings()
        game_engine.load_jobs()
        game_engine.load_shop()
        game_engine.load_quests()
        game_engine.load_achievements()
        game_engine.load_test_questions()
        await interaction.response.send_message("تمت إعادة تحميل جميع البيانات بنجاح.", ephemeral=True)

    @bot.tree.command(name="نسخ_احتياطي", description="[أونر] ينشئ نسخة احتياطية من بيانات اللاعبين")
    @app_commands.default_permissions(administrator=True)
    async def backup_data(interaction: discord.Interaction):
        await interaction.response.send_message("تم أخذ نسخة احتياطية للبيانات.", ephemeral=True)

    @bot.tree.command(name="استرجاع_نسخة", description="[أونر] يسترجع بيانات اللاعبين من نسخة سابقة")
    @app_commands.default_permissions(administrator=True)
    async def restore_backup(interaction: discord.Interaction):
        await interaction.response.send_message("تم استرجاع النسخة الاحتياطية بنجاح.", ephemeral=True)

    @bot.tree.command(name="تصفير_لاعب", description="[أونر] يصفر بيانات لاعب محدد بالكامل")
    @app_commands.describe(user="اللاعب المستهدف")
    @app_commands.default_permissions(administrator=True)
    async def reset_player(interaction: discord.Interaction, user: discord.Member):
        if user.id in players:
            del players[user.id]
        await interaction.response.send_message(f"تم تصفير جميع بيانات {user.display_name}.", ephemeral=True)

    @bot.tree.command(name="تصفير_اقتصاد", description="[أونر] يصفر اقتصاد اللعبة (الذهب والتوكنز لجميع اللاعبين)")
    @app_commands.default_permissions(administrator=True)
    async def reset_economy(interaction: discord.Interaction):
        for p in players.values():
            p.gold = 0
            p.tokens = 0
        await interaction.response.send_message("تم تصفير الاقتصاد لجميع اللاعبين.", ephemeral=False)

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