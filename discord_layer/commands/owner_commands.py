import discord
from discord.app_commands import command, describe

class OwnerCommands(discord.app_commands.Group):
    """أوامر الأونر"""

    @command(name="صيانة", description="تفعيل وضع الصيانة")
    async def maintenance_on(self, interaction: discord.Interaction):
        await interaction.response.send_message("تم تفعيل وضع الصيانة.", ephemeral=True)

    @command(name="رفع_الصيانة", description="رفع وضع الصيانة")
    async def maintenance_off(self, interaction: discord.Interaction):
        await interaction.response.send_message("تم رفع وضع الصيانة.", ephemeral=True)

    @command(name="إعادة_تحميل", description="إعادة تحميل الأنظمة أو المحتوى")
    async def reload_system(self, interaction: discord.Interaction):
        await interaction.response.send_message("تم إعادة تحميل النظام بنجاح.", ephemeral=True)

    @command(name="نسخ_احتياطي", description="أخذ نسخة احتياطية للبيانات")
    async def backup(self, interaction: discord.Interaction):
        await interaction.response.send_message("تم أخذ نسخة احتياطية.", ephemeral=True)

    @command(name="استرجاع_نسخة", description="استرجاع نسخة احتياطية")
    @describe(backup_id="معرف النسخة")
    async def restore_backup(self, interaction: discord.Interaction, backup_id: str):
        await interaction.response.send_message(f"تم استرجاع النسخة {backup_id}.", ephemeral=True)

    @command(name="تصفير_لاعب", description="تصفير بيانات لاعب بالكامل")
    @describe(player_id="معرف اللاعب")
    async def wipe_player(self, interaction: discord.Interaction, player_id: str):
        await interaction.response.send_message(f"تم تصفير اللاعب {player_id}.", ephemeral=True)

    @command(name="تصفير_اقتصاد", description="تصفير اقتصاد السيرفر بالكامل")
    async def wipe_economy(self, interaction: discord.Interaction):
        await interaction.response.send_message("تم تصفير الاقتصاد.", ephemeral=True)

async def setup(bot):
    bot.tree.add_command(OwnerCommands(name="أونر", description="أوامر الأونر"))
