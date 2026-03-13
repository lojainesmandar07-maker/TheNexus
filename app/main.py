import os
import discord
from discord.ext import commands
from discord_layer.bot import setup_bot

def main():
    # Load environment variables or config
    token = os.getenv("DISCORD_BOT_TOKEN", "YOUR_TOKEN_HERE")

    # Initialize bot
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    # Setup bot layers
    setup_bot(bot)

    # Run bot
    bot.run(token)

if __name__ == "__main__":
    main()
