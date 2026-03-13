import discord
from discord.ext import commands
from discord_layer.embeds import create_story_embed, create_status_embed

def setup_bot(bot: commands.Bot):

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")
        print("Bot is ready for EPIC ARABIC ADVENTURES!")

    @bot.command()
    async def start(ctx):
        """يبدأ مغامرتك"""
        embed = create_story_embed(
            title="بداية الرحلة",
            description="أهلاً بك أيها المسافر في عوالمنا المتعددة. هل أنت مستعد لاكتشاف المجهول؟\n\nستكون رحلة مليئة بالمخاطر، الألغاز، والانتصارات العظيمة. كل قرار تتخذه سيؤثر على مصيرك ومصير هذه العوالم.",
            world="fantasy"
        )
        # Create a view with some persistent buttons
        view = discord.ui.View()
        button_yes = discord.ui.Button(label="نعم، أنا مستعد", style=discord.ButtonStyle.success, custom_id="start_yes")
        button_no = discord.ui.Button(label="أحتاج لبعض الوقت", style=discord.ButtonStyle.secondary, custom_id="start_no")
        view.add_item(button_yes)
        view.add_item(button_no)

        await ctx.send(embed=embed, view=view)

    @bot.command()
    async def profile(ctx):
        """يعرض ملفك الشخصي وإنجازاتك"""
        # In a real app, we'd fetch user data from DB or JSON
        embed = create_status_embed(
            player_name=ctx.author.display_name,
            archetype="المستكشف (Explorer)",
            level=5,
            xp=1250,
            gold=300
        )
        await ctx.send(embed=embed)
