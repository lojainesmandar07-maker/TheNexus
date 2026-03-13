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


## Web-only resolution (no local setup required)

If you cannot use Git locally, you can resolve directly in GitHub UI:

1. Open the PR page and click **Resolve conflicts**.
2. For each conflicted file below, keep the branch version that contains the hardening changes, then remove conflict blocks and save:
   - `engine/story_engine.py`
   - `discord_layer/bot.py`
   - `content/story/endings.json`
3. Click **Mark as resolved** for each file, then **Commit merge**.
4. Wait for the `content-validation` check to run.
5. If checks pass, click **Merge pull request**.

### What to keep (quick checklist)
- In `engine/story_engine.py`: keep `load_endings`, `get_ending`, `ending_id` handling, and skill-check failure consequence return payload.
- In `discord_layer/bot.py`: keep `is_ending` embed path and `check_failed` message prefix.
- In `content/story/endings.json`: keep all 8 ending IDs with world-specific Arabic text.
