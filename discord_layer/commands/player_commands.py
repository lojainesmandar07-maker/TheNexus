import discord
from discord.app_commands import command, describe

class PlayerCommands(discord.app_commands.Group):
    """أوامر اللاعب الأساسية"""

    @command(name="ابدأ", description="بدء القصة أو الجزء الحالي في الروم الصحيح")
    async def start(self, interaction: discord.Interaction):
        await interaction.response.send_message("جاري بدء القصة...", ephemeral=True)

    @command(name="استمر", description="استكمال جلسة القصة الحالية")
    async def continue_story(self, interaction: discord.Interaction):
        await interaction.response.send_message("جاري استكمال القصة...", ephemeral=True)

    @command(name="ملفي", description="عرض البروفايل الكامل")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.send_message("جاري عرض الملف الشخصي...", ephemeral=True)

    @command(name="اختبار_الشخصية", description="بدء أو إعادة عرض اختبار الشخصية إذا لم يكتمل")
    async def character_test(self, interaction: discord.Interaction):
        await interaction.response.send_message("بدء اختبار الشخصية...", ephemeral=True)

    @command(name="شخصيتي", description="عرض الشخصية الحالية ووصفها")
    async def my_character(self, interaction: discord.Interaction):
        await interaction.response.send_message("جاري عرض تفاصيل شخصيتك...", ephemeral=True)

    @command(name="عمل", description="تنفيذ دورة العمل اليومية أو الحالية")
    async def work(self, interaction: discord.Interaction):
        await interaction.response.send_message("جاري تنفيذ العمل...", ephemeral=True)

    @command(name="مهمة", description="الحصول على مهمة جانبية أو عرض المهمة الحالية")
    async def quest(self, interaction: discord.Interaction):
        await interaction.response.send_message("جاري جلب المهمة...", ephemeral=True)

    @command(name="متجر", description="فتح المتجر")
    async def shop(self, interaction: discord.Interaction):
        await interaction.response.send_message("جاري فتح المتجر...", ephemeral=True)

    @command(name="شراء", description="شراء عنصر من المتجر")
    @describe(item_id="معرف العنصر المراد شراؤه")
    async def buy(self, interaction: discord.Interaction, item_id: str):
        await interaction.response.send_message(f"جاري شراء {item_id}...", ephemeral=True)

    @command(name="بيع", description="بيع عنصر أو مورد إذا كان النظام يدعم ذلك")
    @describe(item_id="معرف العنصر المراد بيعه")
    async def sell(self, interaction: discord.Interaction, item_id: str):
        await interaction.response.send_message(f"جاري بيع {item_id}...", ephemeral=True)

    @command(name="إنجازاتي", description="عرض الإنجازات المفتوحة أو البارزة")
    async def achievements(self, interaction: discord.Interaction):
        await interaction.response.send_message("جاري عرض الإنجازات...", ephemeral=True)

async def setup(bot):
    bot.tree.add_command(PlayerCommands(name="لاعب", description="أوامر اللاعب"))
