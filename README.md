# 🌟 Epic Arabic Discord RPG Bot - User Guide

Welcome to the Epic Arabic Discord RPG Bot! This guide will explain how your project is structured, how to use the generation tools, and what to do with your JSON files.

## 🎮 Content Engine

This is an "Epic-Scale" RPG featuring over 4,000+ story choices, 100+ jobs, layered economy shops, and complex branching logic.

All of this data is fully baked into static `.json` files located in the `content/` directory.

**You do not need to run any scripts to generate the story.** The bot (`engine/story_engine.py`) reads directly from these richly populated JSON files (containing 100% Arabic narrative `سرد`) to run the game instantly!

If you want to edit the story, add new factions, or adjust the economy, you can safely and directly edit the JSON files inside the `content/` folder. The bot will load the changes automatically upon restart.

## 🚀 How to Run Your Bot

1. Make sure you have your Discord Bot Token from the Discord Developer Portal.
2. Set it as an environment variable in your terminal:
   ```bash
   export DISCORD_BOT_TOKEN="your_token_here"
   ```
3. Run the main bot application:
   ```bash
   python app/main.py
   ```
4. Go to your Discord server and type `!start` to begin your epic Arabic adventure! (Or `!profile`, `!shop`, `!jobs`).

---

*Enjoy your Masterpiece! All player-facing text is in beautiful, immersive Arabic, while the backend code securely powers the logic in English.*
