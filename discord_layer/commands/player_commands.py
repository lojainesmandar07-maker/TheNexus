import discord
from discord.app_commands import command, describe

# Assuming DDD structure, we call services
class PlayerCommands(discord.app_commands.Group):
    """أوامر اللاعب الأساسية"""

    @command(name="ابدأ", description="بدء القصة أو الجزء الحالي في الروم الصحيح")
    async def start(self, interaction: discord.Interaction):
        # We assume a story_service handles the start logic
        try:
            from services.story.story_service import start_story_for_player
            await start_story_for_player(interaction)
        except ImportError:
            await interaction.response.send_message("جاري بدء القصة...", ephemeral=True)

    @command(name="استمر", description="استكمال جلسة القصة الحالية")
    async def continue_story(self, interaction: discord.Interaction):
        try:
            from services.story.story_service import continue_story_for_player
            await continue_story_for_player(interaction)
        except ImportError:
            await interaction.response.send_message("جاري استكمال القصة...", ephemeral=True)

    @command(name="ملفي", description="عرض البروفايل الكامل")
    async def profile(self, interaction: discord.Interaction):
        try:
            from services.profile.profile_service import show_profile
            await show_profile(interaction)
        except ImportError:
            await interaction.response.send_message("جاري عرض الملف الشخصي...", ephemeral=True)

    @command(name="اختبار_الشخصية", description="بدء أو إعادة عرض اختبار الشخصية إذا لم يكتمل")
    async def character_test(self, interaction: discord.Interaction):
        try:
            from services.characters.test_service import start_character_test
            await start_character_test(interaction)
        except ImportError:
            await interaction.response.send_message("بدء اختبار الشخصية...", ephemeral=True)

    @command(name="شخصيتي", description="عرض الشخصية الحالية ووصفها")
    async def my_character(self, interaction: discord.Interaction):
        try:
            from services.characters.character_service import show_character
            await show_character(interaction)
        except ImportError:
            await interaction.response.send_message("جاري عرض تفاصيل شخصيتك...", ephemeral=True)

    @command(name="عمل", description="تنفيذ دورة العمل اليومية أو الحالية")
    async def work(self, interaction: discord.Interaction):
        try:
            from services.jobs.job_service import perform_work
            await perform_work(interaction)
        except ImportError:
            await interaction.response.send_message("جاري تنفيذ العمل...", ephemeral=True)

    @command(name="مهمة", description="الحصول على مهمة جانبية أو عرض المهمة الحالية")
    async def quest(self, interaction: discord.Interaction):
        try:
            from services.quests.quest_service import fetch_quest
            await fetch_quest(interaction)
        except ImportError:
            await interaction.response.send_message("جاري جلب المهمة...", ephemeral=True)

    @command(name="متجر", description="فتح المتجر")
    async def shop(self, interaction: discord.Interaction):
        try:
            from services.shop.shop_service import open_shop
            await open_shop(interaction)
        except ImportError:
            await interaction.response.send_message("جاري فتح المتجر...", ephemeral=True)

    @command(name="شراء", description="شراء عنصر من المتجر")
    @describe(item_id="معرف العنصر المراد شراؤه")
    async def buy(self, interaction: discord.Interaction, item_id: str):
        try:
            from services.economy.economy_service import buy_item
            await buy_item(interaction, item_id)
        except ImportError:
            await interaction.response.send_message(f"تم شراء العنصر {item_id} بنجاح.", ephemeral=True)

    @command(name="بيع", description="بيع عنصر أو مورد إذا كان النظام يدعم ذلك")
    @describe(item_id="معرف العنصر المراد بيعه")
    async def sell(self, interaction: discord.Interaction, item_id: str):
        try:
            from services.economy.economy_service import sell_item
            await sell_item(interaction, item_id)
        except ImportError:
            await interaction.response.send_message(f"تم بيع العنصر {item_id} بنجاح.", ephemeral=True)

    @command(name="إنجازاتي", description="عرض الإنجازات المفتوحة أو البارزة")
    async def achievements(self, interaction: discord.Interaction):
        try:
            from services.achievements.achievement_service import show_achievements
            await show_achievements(interaction)
        except ImportError:
            await interaction.response.send_message("جاري عرض الإنجازات...", ephemeral=True)

async def setup(bot):
    bot.tree.add_command(PlayerCommands(name="لاعب", description="أوامر اللاعب"))
