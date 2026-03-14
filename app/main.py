import os
import sys
from pathlib import Path

# Ensure project root is importable when launched as `python app/main.py`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
