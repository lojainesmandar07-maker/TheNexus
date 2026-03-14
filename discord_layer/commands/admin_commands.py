import discord
from discord.app_commands import command, describe

class AdminCommands(discord.app_commands.Group):
    """أوامر الإدارة"""

    @command(name="تعيين_روم_قصة", description="تعيين الروم الحالي كروم قصة")
    async def set_story_room(self, interaction: discord.Interaction):
        await interaction.response.send_message("تم تعيين روم القصة.", ephemeral=True)

    @command(name="تعيين_روم_شرح", description="تعيين الروم الحالي كروم شرح")
    async def set_guide_room(self, interaction: discord.Interaction):
        await interaction.response.send_message("تم تعيين روم الشرح.", ephemeral=True)

    @command(name="تعيين_روم_ستايلات", description="تعيين الروم الحالي كروم ستايلات")
    async def set_style_room(self, interaction: discord.Interaction):
        await interaction.response.send_message("تم تعيين روم الستايلات.", ephemeral=True)

    @command(name="فتح_عالم", description="فتح عالم مغلق")
    @describe(world_name="اسم العالم")
    async def open_world(self, interaction: discord.Interaction, world_name: str):
        await interaction.response.send_message(f"تم فتح عالم {world_name}.", ephemeral=True)

    @command(name="إغلاق_عالم", description="إغلاق عالم مفتوح")
    @describe(world_name="اسم العالم")
    async def close_world(self, interaction: discord.Interaction, world_name: str):
        await interaction.response.send_message(f"تم إغلاق عالم {world_name}.", ephemeral=True)

    @command(name="إغلاق_جلسة", description="إغلاق جلسة لاعب")
    @describe(player_id="معرف اللاعب")
    async def close_session(self, interaction: discord.Interaction, player_id: str):
        await interaction.response.send_message(f"تم إغلاق جلسة {player_id}.", ephemeral=True)

    @command(name="استرجاع_جلسة", description="استرجاع جلسة لاعب")
    @describe(player_id="معرف اللاعب")
    async def restore_session(self, interaction: discord.Interaction, player_id: str):
        await interaction.response.send_message(f"تم استرجاع جلسة {player_id}.", ephemeral=True)

    @command(name="إعادة_تعيين_شخصية", description="إعادة تعيين شخصية لاعب")
    @describe(player_id="معرف اللاعب")
    async def reset_character(self, interaction: discord.Interaction, player_id: str):
        await interaction.response.send_message(f"تم إعادة تعيين شخصية {player_id}.", ephemeral=True)

    @command(name="إضافة_xp", description="إضافة XP للاعب")
    @describe(player_id="معرف اللاعب", amount="الكمية")
    async def add_xp(self, interaction: discord.Interaction, player_id: str, amount: int):
        await interaction.response.send_message(f"تم إضافة {amount} XP للاعب {player_id}.", ephemeral=True)

    @command(name="حذف_xp", description="حذف XP من لاعب")
    @describe(player_id="معرف اللاعب", amount="الكمية")
    async def remove_xp(self, interaction: discord.Interaction, player_id: str, amount: int):
        await interaction.response.send_message(f"تم حذف {amount} XP من اللاعب {player_id}.", ephemeral=True)

    @command(name="إضافة_عملة", description="إضافة عملة للاعب")
    @describe(player_id="معرف اللاعب", amount="الكمية", currency="نوع العملة")
    async def add_currency(self, interaction: discord.Interaction, player_id: str, amount: int, currency: str):
        await interaction.response.send_message(f"تم إضافة {amount} {currency} للاعب {player_id}.", ephemeral=True)

    @command(name="حذف_عملة", description="حذف عملة من لاعب")
    @describe(player_id="معرف اللاعب", amount="الكمية", currency="نوع العملة")
    async def remove_currency(self, interaction: discord.Interaction, player_id: str, amount: int, currency: str):
        await interaction.response.send_message(f"تم حذف {amount} {currency} من اللاعب {player_id}.", ephemeral=True)

    @command(name="إغلاق_الأزرار", description="إغلاق أزرار جلسة قديمة")
    async def disable_buttons(self, interaction: discord.Interaction):
        await interaction.response.send_message("تم إغلاق الأزرار.", ephemeral=True)

    @command(name="ارسال_رسالة", description="البوت يرسل الرسالة باسمه داخل الروم المحدد")
    @describe(channel="الروم", message="النص")
    async def send_message(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        await channel.send(message)
        await interaction.response.send_message("تم إرسال الرسالة بنجاح.", ephemeral=True)

async def setup(bot):
    bot.tree.add_command(AdminCommands(name="إدارة", description="أوامر الإدارة"))
