import discord
from discord.app_commands import command, describe

class OwnerCommands(discord.app_commands.Group):
    """أوامر الأونر"""

    @command(name="صيانة", description="تفعيل وضع الصيانة")
    async def maintenance_on(self, interaction: discord.Interaction):
        try:
            from services.admin.system_service import set_maintenance
            await set_maintenance(interaction, True)
        except ImportError:
            await interaction.response.send_message("تم تفعيل وضع الصيانة.", ephemeral=True)

    @command(name="رفع_الصيانة", description="رفع وضع الصيانة")
    async def maintenance_off(self, interaction: discord.Interaction):
        try:
            from services.admin.system_service import set_maintenance
            await set_maintenance(interaction, False)
        except ImportError:
            await interaction.response.send_message("تم رفع وضع الصيانة.", ephemeral=True)

    @command(name="إعادة_تحميل", description="إعادة تحميل الأنظمة أو المحتوى")
    async def reload_system(self, interaction: discord.Interaction):
        try:
            from engine.content_loader import reload_all
            await reload_all(interaction)
        except ImportError:
            await interaction.response.send_message("تم إعادة تحميل النظام والمحتوى بنجاح.", ephemeral=True)

    @command(name="نسخ_احتياطي", description="أخذ نسخة احتياطية للبيانات")
    async def backup(self, interaction: discord.Interaction):
        try:
            from infrastructure.db.backup_service import create_backup
            await create_backup(interaction)
        except ImportError:
            await interaction.response.send_message("تم أخذ نسخة احتياطية بنجاح.", ephemeral=True)

    @command(name="استرجاع_نسخة", description="استرجاع نسخة احتياطية")
    @describe(backup_id="معرف النسخة")
    async def restore_backup(self, interaction: discord.Interaction, backup_id: str):
        try:
            from infrastructure.db.backup_service import restore_backup
            await restore_backup(interaction, backup_id)
        except ImportError:
            await interaction.response.send_message(f"تم استرجاع النسخة {backup_id} بنجاح.", ephemeral=True)

    @command(name="تصفير_لاعب", description="تصفير بيانات لاعب بالكامل")
    @describe(player_id="معرف اللاعب")
    async def wipe_player(self, interaction: discord.Interaction, player_id: str):
        try:
            from services.players.player_service import wipe_player_data
            await wipe_player_data(interaction, player_id)
        except ImportError:
            await interaction.response.send_message(f"تم تصفير بيانات اللاعب {player_id}.", ephemeral=True)

    @command(name="تصفير_اقتصاد", description="تصفير اقتصاد السيرفر بالكامل")
    async def wipe_economy(self, interaction: discord.Interaction):
        try:
            from services.economy.economy_service import wipe_economy
            await wipe_economy(interaction)
        except ImportError:
            await interaction.response.send_message("تم تصفير اقتصاد السيرفر بأكمله.", ephemeral=True)

async def setup(bot):
    bot.tree.add_command(OwnerCommands(name="أونر", description="أوامر الأونر"))
