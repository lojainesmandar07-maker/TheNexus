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
from keep_alive import keep_alive

def main():
    # Start the background web server for Render health checks
    keep_alive()

    # Load environment variables or config
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token or token == "YOUR_TOKEN_HERE":
        print("Error: DISCORD_BOT_TOKEN environment variable is missing.")
        return

    # Initialize bot
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    # Prefix is still set but mostly unused now since we migrated to slash commands
    bot = commands.Bot(command_prefix="/", intents=intents)

    # Setup bot layers
    setup_bot(bot)

    # Run bot
    bot.run(token)

if __name__ == "__main__":
    main()
