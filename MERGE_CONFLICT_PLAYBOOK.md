# Merge Conflict Playbook (for this branch)

When GitHub shows conflicts in:
- `content/story/endings.json`
- `discord_layer/bot.py`
- `engine/story_engine.py`

use this exact sequence locally:

```bash
git fetch origin
git checkout work
git merge origin/main
```

If conflict appears, keep the hardening logic from this branch and re-run validator:

```bash
# After editing conflict blocks manually
git add content/story/endings.json discord_layer/bot.py engine/story_engine.py
python scripts/validate_content.py
git commit -m "Resolve merge conflicts in endings and story runtime files"
git push origin work
```

## What must be preserved

1. `engine/story_engine.py`
   - `load_endings()`
   - `get_ending()`
   - `process_choice()` handling for:
     - `ending_id`
     - skill-check failure consequence (`check_failed`, fallback node)

2. `discord_layer/bot.py`
   - ending embed flow (`is_ending` branch)
   - failure outcome message prefix in normal progression

3. `content/story/endings.json`
   - all 8 ending IDs
   - world-specific Arabic ending text

## Safety net

CI now fails if unresolved conflict markers exist (merge conflict separators).
This is enforced by `scripts/validate_content.py` and workflow `.github/workflows/content-validation.yml`.
