        from __future__ import annotations

        import discord
        from discord import app_commands
        from discord.ext import commands

        from src.domain.enums import ArchetypeName, JobStatus, WorldName
        from src.discord_layer.embeds import StoryEmbeds, world_name_to_arabic
        from src.discord_layer.guards import StoryChannelGuard
        from src.discord_layer.views import PersistentStoryView
        from src.services.admin_service import AdminService
        from src.services.achievement_service import AchievementService
        from src.services.character_service import CharacterService
        from src.services.discord_access_service import DiscordAccessService
        from src.services.economy_service import EconomyService
        from src.services.faction_service import FactionService
        from src.services.guild_config_service import GuildConfigService
        from src.services.job_service import JobService
        from src.services.npc_service import NpcService
        from src.services.profile_service import ProfileService
        from src.services.quest_service import QuestService
        from src.services.shop_service import ShopService
        from src.services.story_service import StoryService
        from src.services.weekly_contract_service import WeeklyContractService
        from src.services.world_service import WorldService


        class StoryCommands(commands.Cog):
            def __init__(self, bot: commands.Bot, story_service: StoryService, profile_service: ProfileService, world_service: WorldService, channel_guard: StoryChannelGuard) -> None:
                self.bot = bot
                self._story_service = story_service
                self._profile_service = profile_service
                self._world_service = world_service
                self._channel_guard = channel_guard

            @app_commands.command(name="ابدأ_قصة", description="ابدأ رحلتك في أحد العوالم")
            async def start_story(self, interaction: discord.Interaction, world: str) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                try:
                    world_name = WorldName(world)
                except ValueError:
                    await interaction.response.send_message("العالم المطلوب غير صالح.", ephemeral=True)
                    return
                allowed_channel, channel_error = self._channel_guard.ensure_story_channel(interaction.guild_id, interaction.channel_id, world_name)
                if not allowed_channel:
                    await interaction.response.send_message(channel_error or "روم غير صالح.", ephemeral=True)
                    return
                profile = self._profile_service.build_profile(interaction.guild_id, interaction.user.id)
                dummy_player = type("PlayerShape", (), {"guild_id": interaction.guild_id, "unlocked_worlds": set(), "__dict__": profile})
                allowed_world, world_error = self._world_service.is_world_available_to_player(dummy_player, world_name)  # type: ignore[arg-type]
                if not allowed_world:
                    await interaction.response.send_message(world_error or "العالم غير متاح.", ephemeral=True)
                    return
                render_result = self._story_service.start_story(interaction.guild_id, interaction.user.id, world_name)
                embed = StoryEmbeds.build_story_node_embed(world_name_to_arabic(world_name), render_result)
                view = PersistentStoryView.build_from_render_result(world_name=world_name, user_id=interaction.user.id, render_result=render_result)
                await interaction.response.send_message(embed=embed, view=view)
                message = await interaction.original_response()
                self.bot.add_view(view, message_id=message.id)
                self._story_service.bind_active_message(interaction.guild_id, interaction.user.id, message.id)

            @app_commands.command(name="اكمل_القصة", description="استرجع جلستك القصصية الحالية")
            async def resume_story(self, interaction: discord.Interaction) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                session = self._story_service.get_active_session(interaction.guild_id, interaction.user.id)
                if session is None:
                    await interaction.response.send_message("لا توجد لك جلسة قصة نشطة حاليًا.", ephemeral=True)
                    return
                allowed_channel, channel_error = self._channel_guard.ensure_story_channel(interaction.guild_id, interaction.channel_id, session.pointer.world_name)
                if not allowed_channel:
                    await interaction.response.send_message(channel_error or "روم غير صالح.", ephemeral=True)
                    return
                render_result = self._story_service.resume_story(interaction.guild_id, interaction.user.id)
                embed = StoryEmbeds.build_story_node_embed(world_name_to_arabic(session.pointer.world_name), render_result)
                view = PersistentStoryView.build_from_render_result(world_name=session.pointer.world_name, user_id=interaction.user.id, render_result=render_result)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                message = await interaction.original_response()
                self.bot.add_view(view, message_id=message.id)
                self._story_service.bind_active_message(interaction.guild_id, interaction.user.id, message.id)


        class CharacterCommands(commands.Cog):
            def __init__(self, bot: commands.Bot, character_service: CharacterService, discord_access_service: DiscordAccessService) -> None:
                self.bot = bot
                self._character_service = character_service
                self._discord_access_service = discord_access_service

            @app_commands.command(name="اختبار_الهوية", description="ابدأ اختبار هويتك")
            async def start_test(self, interaction: discord.Interaction) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                session, question = self._character_service.start_or_resume_test(interaction.guild_id, interaction.user.id)
                lines = [f"• `{option['id']}` — {option['text_ar']}" for option in question.get("options", [])]
                embed = discord.Embed(title=question.get("text_ar", "سؤال"), description="
".join(lines), color=discord.Color.blurple())
                embed.set_footer(text=f"Question {session.current_question_index + 1}/{len(session.question_ids)}")
                await interaction.response.send_message(embed=embed, ephemeral=True)

            @app_commands.command(name="أجب_الهوية", description="أجب عن السؤال الحالي في اختبار الهوية")
            async def answer_test(self, interaction: discord.Interaction, option_id: str) -> None:
                if interaction.guild_id is None or interaction.guild is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                session, next_question = self._character_service.answer_current_question(interaction.guild_id, interaction.user.id, option_id)
                if next_question is not None:
                    lines = [f"• `{option['id']}` — {option['text_ar']}" for option in next_question.get("options", [])]
                    embed = discord.Embed(title=next_question.get("text_ar", "سؤال"), description="
".join(lines), color=discord.Color.blurple())
                    embed.set_footer(text=f"Question {session.current_question_index + 1}/{len(session.question_ids)}")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                archetype = self._character_service.finish_test(interaction.guild_id, interaction.user.id, interaction.user.display_name)
                member = interaction.guild.get_member(interaction.user.id)
                granted_channels: list[int] = []
                if member is not None:
                    await self._discord_access_service.assign_archetype_role(member, archetype)
                    granted_channels = await self._discord_access_service.apply_archetype_channel_access(member, archetype)
                embed = discord.Embed(title="اكتمل اختبار هويتك", description=f"تم تحديد نمطك: {archetype.value}", color=discord.Color.green())
                if granted_channels:
                    embed.add_field(name="قنوات فُتحت لك", value="
".join(f"• <#{channel_id}>" for channel_id in granted_channels[:10]), inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)


        class ProfileCommands(commands.Cog):
            def __init__(self, bot: commands.Bot, profile_service: ProfileService) -> None:
                self.bot = bot
                self._profile_service = profile_service

            @app_commands.command(name="ملفي", description="اعرض ملفك الشخصي")
            async def my_profile(self, interaction: discord.Interaction) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                profile = self._profile_service.build_profile(interaction.guild_id, interaction.user.id)
                embed = discord.Embed(title=profile["display_name"], color=discord.Color.gold())
                embed.add_field(name="المستوى", value=str(profile["level"]), inline=True)
                embed.add_field(name="الخبرة", value=str(profile["xp"]), inline=True)
                embed.add_field(name="الذهب", value=str(profile["gold"]), inline=True)
                embed.add_field(name="السمعة", value=str(profile["reputation"]), inline=True)
                embed.add_field(name="النمط", value=str(profile["archetype"]), inline=True)
                embed.add_field(name="السجل الحي", value=profile["live_log"], inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)


        class JobsCommands(commands.Cog):
            def __init__(self, bot: commands.Bot, job_service: JobService) -> None:
                self.bot = bot
                self._job_service = job_service

            @app_commands.command(name="عمل_يومي", description="نفّذ عملك اليومي")
            async def daily_job(self, interaction: discord.Interaction) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                status, cooldown_until = self._job_service.get_status(interaction.guild_id, interaction.user.id)
                if status == JobStatus.ON_COOLDOWN and cooldown_until is not None:
                    await interaction.response.send_message(f"لا يمكنك تنفيذ عمل جديد الآن. الجاهزية التالية: {cooldown_until.isoformat()}", ephemeral=True)
                    return
                result = self._job_service.run_daily_job(interaction.guild_id, interaction.user.id)
                job_def = result["job"]
                reward_bundle = result["reward_bundle"]
                embed = discord.Embed(title=f"العمل اليومي: {job_def.get('name_ar', job_def['id'])}", description=job_def.get("description_ar", "أنجزت عملك اليومي."), color=discord.Color.green())
                embed.add_field(name="الخبرة", value=str(reward_bundle.xp), inline=True)
                embed.add_field(name="الذهب", value=str(reward_bundle.gold), inline=True)
                embed.add_field(name="السمعة", value=str(reward_bundle.reputation), inline=True)
                if result.get("rare_event_text"):
                    embed.add_field(name="حدث نادر", value=result["rare_event_text"], inline=False)
                if result["achievement_result"].unlocked_achievement_ids:
                    embed.add_field(name="إنجازات جديدة", value="
".join(result["achievement_result"].unlocked_achievement_ids[:5]), inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)


        class QuestsCommands(commands.Cog):
            def __init__(self, bot: commands.Bot, quest_service: QuestService) -> None:
                self.bot = bot
                self._quest_service = quest_service

            @app_commands.command(name="مهمة_جانبية", description="استلم مهمة جانبية")
            async def get_side_quest(self, interaction: discord.Interaction) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                result = self._quest_service.assign_quest(interaction.guild_id, interaction.user.id)
                quest_def = result["quest_def"]
                embed = discord.Embed(title=f"مهمة جانبية: {quest_def.get('name_ar', quest_def['id'])}", description=quest_def.get("description_ar", "وصلكت مهمة جانبية جديدة."), color=discord.Color.orange())
                embed.add_field(name="الهدف", value=quest_def.get("objective_ar", "لا يوجد هدف محدد."), inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)

            @app_commands.command(name="إنهاء_مهمة_جانبية", description="أنه المهمة الجانبية النشطة")
            async def complete_side_quest(self, interaction: discord.Interaction) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                result = self._quest_service.complete_active_quest(interaction.guild_id, interaction.user.id)
                reward_bundle = result["reward_bundle"]
                quest_def = result["quest_def"]
                embed = discord.Embed(title=f"أنجزت المهمة: {quest_def.get('name_ar', quest_def['id'])}", description="تم تسجيل التقدم وإضافة المكافآت.", color=discord.Color.gold())
                embed.add_field(name="الخبرة", value=str(reward_bundle.xp), inline=True)
                embed.add_field(name="الذهب", value=str(reward_bundle.gold), inline=True)
                embed.add_field(name="السمعة", value=str(reward_bundle.reputation), inline=True)
                if result.get("next_quest_id"):
                    embed.add_field(name="خيط جديد", value=str(result["next_quest_id"]), inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)


        class ContractsCommands(commands.Cog):
            def __init__(self, bot: commands.Bot, weekly_contract_service: WeeklyContractService) -> None:
                self.bot = bot
                self._weekly_contract_service = weekly_contract_service

            @app_commands.command(name="عقد_أسبوعي", description="استلم أو استعرض عقدك الأسبوعي")
            async def weekly_contract(self, interaction: discord.Interaction) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                result = self._weekly_contract_service.assign_or_resume(interaction.guild_id, interaction.user.id)
                contract = result["contract"]
                embed = discord.Embed(title=f"العقد الأسبوعي: {contract.get('name_ar', contract['id'])}", description=contract.get("description_ar", "وصلك عقد أسبوعي جديد."), color=discord.Color.dark_orange())
                embed.add_field(name="الهدف", value=contract.get("objective_ar", "لا يوجد هدف محدد."), inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)

            @app_commands.command(name="إنهاء_عقد_أسبوعي", description="أنه العقد الأسبوعي النشط")
            async def complete_weekly_contract(self, interaction: discord.Interaction) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                result = self._weekly_contract_service.complete_active(interaction.guild_id, interaction.user.id)
                reward_bundle = result["reward_bundle"]
                contract = result["contract"]
                embed = discord.Embed(title=f"أنجزت العقد: {contract.get('name_ar', contract['id'])}", description="تم احتساب العقد ضمن تقدمك الأسبوعي.", color=discord.Color.dark_gold())
                embed.add_field(name="الخبرة", value=str(reward_bundle.xp), inline=True)
                embed.add_field(name="الذهب", value=str(reward_bundle.gold), inline=True)
                embed.add_field(name="السمعة", value=str(reward_bundle.reputation), inline=True)
                await interaction.response.send_message(embed=embed, ephemeral=True)


        class ShopCommands(commands.Cog):
            def __init__(self, bot: commands.Bot, shop_service: ShopService, economy_service: EconomyService) -> None:
                self.bot = bot
                self._shop_service = shop_service
                self._economy_service = economy_service

            @app_commands.command(name="المتجر", description="اعرض المتجر")
            async def show_shop(self, interaction: discord.Interaction) -> None:
                catalog = self._shop_service.list_catalog()
                if not catalog:
                    await interaction.response.send_message("المتجر فارغ حاليًا.", ephemeral=True)
                    return
                lines = [f"• `{item['id']}` — {item.get('name_ar', item['id'])} — {item.get('price_gold', 0)} ذهب" for item in catalog[:10]]
                embed = discord.Embed(title="المتجر العالمي", description="
".join(lines), color=discord.Color.teal())
                await interaction.response.send_message(embed=embed, ephemeral=True)

            @app_commands.command(name="شراء", description="اشتر عنصرًا من المتجر")
            async def buy_item(self, interaction: discord.Interaction, item_id: str) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                result = self._shop_service.buy_item(interaction.guild_id, interaction.user.id, item_id)
                balance = self._economy_service.get_balance(interaction.guild_id, interaction.user.id)
                embed = discord.Embed(title=f"تم الشراء: {result['item'].get('name_ar', item_id)}", description=f"رصيدك الحالي: {balance['gold']} ذهب", color=discord.Color.blue())
                await interaction.response.send_message(embed=embed, ephemeral=True)


        class AchievementsCommands(commands.Cog):
            def __init__(self, bot: commands.Bot, achievement_service: AchievementService) -> None:
                self.bot = bot
                self._achievement_service = achievement_service

            @app_commands.command(name="إنجازاتي", description="افحص إنجازاتك")
            async def my_achievements(self, interaction: discord.Interaction) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                result = self._achievement_service.evaluate_player(interaction.guild_id, interaction.user.id)
                if not result.unlocked_achievement_ids:
                    await interaction.response.send_message("لا توجد إنجازات جديدة الآن.", ephemeral=True)
                    return
                embed = discord.Embed(title="إنجازاتك الجديدة", description="
".join(f"• {item}" for item in result.unlocked_achievement_ids), color=discord.Color.fuchsia())
                await interaction.response.send_message(embed=embed, ephemeral=True)


        class WorldCommands(commands.Cog):
            def __init__(self, bot: commands.Bot, faction_service: FactionService, npc_service: NpcService) -> None:
                self.bot = bot
                self._faction_service = faction_service
                self._npc_service = npc_service

            @app_commands.command(name="سمعتي", description="اعرض سمعتك مع الفصائل")
            async def my_factions(self, interaction: discord.Interaction) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                reputations = self._faction_service.list_reputations(interaction.guild_id, interaction.user.id)
                if not reputations:
                    await interaction.response.send_message("لا توجد لك سمعة مسجلة مع أي فصيل بعد.", ephemeral=True)
                    return
                lines = [f"• {item.faction_id}: {item.reputation}" for item in reputations]
                embed = discord.Embed(title="سمعتك مع الفصائل", description="
".join(lines), color=discord.Color.brand_green())
                await interaction.response.send_message(embed=embed, ephemeral=True)

            @app_commands.command(name="علاقاتي", description="اعرض علاقاتك مع الشخصيات المؤثرة")
            async def my_bonds(self, interaction: discord.Interaction) -> None:
                if interaction.guild_id is None:
                    await interaction.response.send_message("هذا الأمر يعمل داخل السيرفر فقط.", ephemeral=True)
                    return
                bonds = self._npc_service.list_bonds(interaction.guild_id, interaction.user.id)
                if not bonds:
                    await interaction.response.send_message("لا توجد لك علاقات مسجلة بعد.", ephemeral=True)
                    return
                lines = [f"• {item.npc_id}: ألفة {item.affinity} / ثقة {item.trust}" for item in bonds]
                embed = discord.Embed(title="شبكة علاقاتك", description="
".join(lines), color=discord.Color.blurple())
                await interaction.response.send_message(embed=embed, ephemeral=True)


        class AdminCommands(commands.Cog):
            def __init__(self, bot: commands.Bot, admin_service: AdminService, guild_config_service: GuildConfigService, story_service: StoryService) -> None:
                self.bot = bot
                self._admin_service = admin_service
                self._guild_config_service = guild_config_service
                self._story_service = story_service

            @app_commands.command(name="إغلاق_جلسة", description="إغلاق جلسة قصة يدويًا")
            async def close_session(self, interaction: discord.Interaction, session_id: str) -> None:
                if not interaction.user.guild_permissions.administrator:
                    await interaction.response.send_message("هذا الأمر للإدارة فقط.", ephemeral=True)
                    return
                self._admin_service.force_close_story_session(session_id)
                await interaction.response.send_message("تم إغلاق الجلسة بنجاح.", ephemeral=True)

            @app_commands.command(name="استرجاع_جلسة", description="استرجاع واجهة جلسة قصة نشطة للاعب")
            async def restore_session(self, interaction: discord.Interaction, member: discord.Member) -> None:
                if interaction.guild_id is None or not interaction.user.guild_permissions.administrator:
                    await interaction.response.send_message("هذا الأمر للإدارة فقط.", ephemeral=True)
                    return
                session = self._admin_service.get_player_active_story_session(interaction.guild_id, member.id)
                if session is None:
                    await interaction.response.send_message("لا توجد جلسة قصة نشطة لهذا اللاعب.", ephemeral=True)
                    return
                render_result = self._story_service.resume_story(interaction.guild_id, member.id)
                embed = StoryEmbeds.build_story_node_embed(world_name_to_arabic(session.pointer.world_name), render_result)
                view = PersistentStoryView.build_from_render_result(world_name=session.pointer.world_name, user_id=member.id, render_result=render_result)
                await interaction.response.send_message(content=f"تم استرجاع واجهة جلسة {member.display_name}.", embed=embed, view=view, ephemeral=True)
                message = await interaction.original_response()
                self.bot.add_view(view, message_id=message.id)
                self._story_service.bind_active_message(interaction.guild_id, member.id, message.id)

            @app_commands.command(name="تعيين_روم_قصة", description="تعيين روم القصة لعالم محدد")
            async def set_story_channel(self, interaction: discord.Interaction, world: str, channel: discord.TextChannel) -> None:
                if interaction.guild_id is None or not interaction.user.guild_permissions.administrator:
                    await interaction.response.send_message("هذا الأمر للإدارة فقط.", ephemeral=True)
                    return
                self._guild_config_service.set_story_channel(interaction.guild_id, WorldName(world), channel.id)
                await interaction.response.send_message("تم تعيين روم القصة بنجاح.", ephemeral=True)

            @app_commands.command(name="فتح_عالم", description="فتح عالم على مستوى السيرفر")
            async def open_world(self, interaction: discord.Interaction, world: str) -> None:
                if interaction.guild_id is None or not interaction.user.guild_permissions.administrator:
                    await interaction.response.send_message("هذا الأمر للإدارة فقط.", ephemeral=True)
                    return
                self._guild_config_service.open_world(interaction.guild_id, WorldName(world))
                await interaction.response.send_message("تم فتح العالم بنجاح.", ephemeral=True)

            @app_commands.command(name="تعيين_رتبة_هوية", description="ربط نمط شخصية برتبة ديسكورد")
            async def set_archetype_role(self, interaction: discord.Interaction, archetype: str, role: discord.Role) -> None:
                if interaction.guild_id is None or not interaction.user.guild_permissions.administrator:
                    await interaction.response.send_message("هذا الأمر للإدارة فقط.", ephemeral=True)
                    return
                archetype_name = ArchetypeName(archetype)
                self._guild_config_service.set_archetype_role(interaction.guild_id, f"archetype_{archetype_name.value}", role.id)
                await interaction.response.send_message("تم ربط الرتبة بالنمط بنجاح.", ephemeral=True)

            @app_commands.command(name="تعيين_قنوات_هوية", description="ربط نمط شخصية بقنوات محددة")
            async def set_archetype_channels(self, interaction: discord.Interaction, archetype: str, channel_ids_csv: str) -> None:
                if interaction.guild_id is None or not interaction.user.guild_permissions.administrator:
                    await interaction.response.send_message("هذا الأمر للإدارة فقط.", ephemeral=True)
                    return
                archetype_name = ArchetypeName(archetype)
                channel_ids = [int(item.strip()) for item in channel_ids_csv.split(",") if item.strip()]
                self._guild_config_service.set_archetype_channels(interaction.guild_id, f"archetype_{archetype_name.value}", channel_ids)
                await interaction.response.send_message("تم حفظ قنوات الهوية بنجاح.", ephemeral=True)
