# 🌟 Epic Arabic Discord RPG Bot - User Guide

Welcome to the Epic Arabic Discord RPG Bot! This guide will explain how your project is structured, how to use the generation tools, and what to do with your JSON files.

## ❓ What is `generate_content.py`?

The `generate_content.py` script is the **Heart of the Content Engine**.

Because this is an "Epic-Scale" RPG, manually writing 4,000+ story choices, 100+ jobs, layered economy shops, and branching logic would take months. Instead, this Python script uses programmatic logic, randomization, and rich Arabic narrative templates (`سرد`) to **automatically build the entire game universe in seconds**.

When you run this script, it builds all the folders inside `content/` and creates every single `.json` file required for the game to function.

## 🛠️ How to use `generate_content.py`?

If you want to create a fresh copy of the game's data, or if you make edits to the templates inside `generate_content.py` (like adding new factions, items, or story scenarios), you simply run the script from your terminal:

```bash
python generate_content.py
```

**What happens when you run it?**
1. It reads the templates and logic.
2. It generates exactly 10 parts for all 4 worlds (Fantasy, Past, Future, Alternate).
3. It creates unique Archetype-specific jobs, rare items, quests, economy shops, and NPC dialogue.
4. It saves everything cleanly into the `content/` folder as `.json` files.

## 🗑️ Should I delete the Story JSONs and other JSONs?

**Short Answer:** No, you do not need to manually delete them.

**Detailed Answer:**
You should **not** delete the JSON files inside the `content/` folder if you want to run the bot right now, because the bot (`engine/story_engine.py`) reads directly from those JSONs to run the game!

However, if you want to "refresh" or "update" the game:
1. You can freely edit `generate_content.py`.
2. When you run `python generate_content.py` again, the script will automatically **overwrite** the old JSON files with the new ones. You don't have to delete the old ones first; the script handles it seamlessly!

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
