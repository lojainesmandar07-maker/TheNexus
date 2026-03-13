# AI Review Report — Epic Arabic Discord RPG Bot

## Scope
This review validated JSON integrity, structural consistency, and cross-system links for:
- stories
- quests
- jobs
- economy
- achievements
- factions/NPCs
- contracts
- character identity content

## Method
The audit used local static checks over `content/**/*.json` to verify:
1. JSON parse validity and empty structures.
2. Required fields in key gameplay entities.
3. Reference consistency (`next_node`, `next_quest_id`, archetypes, factions, reward items).
4. Arabic-language quality rules for player-facing fields (`*_ar`) and narrative constraints.
5. Content volume for gameplay sufficiency.

## High-Level Result
- ✅ All JSON files are valid and parse successfully.
- ✅ No top-level empty JSON arrays or objects were found.
- ✅ Story graph node references are internally valid per world (no broken `next_node` references detected).
- ⚠️ Several data consistency gaps exist across systems (details below).
- ⚠️ Arabic narrative constraints are only partially satisfied.

## Content Volume Snapshot
- Story: 4 worlds × 10 parts × 100 nodes = **4000 nodes** with >8500 choices total.
- Quests: **91** quests.
- Jobs: **240** jobs.
- Economy shop items: **60** items.
- Achievements: **50** achievements.
- Weekly contracts: **2** contracts.
- Character test questions: **20** questions.

## Detected Issues

### 1) Job ID collisions (logic risk)
`general_jobs_city.json` and `general_jobs_frontier.json` reuse the same job IDs (`job_gen_001` ... `job_gen_040`).

Why this matters:
- `GameEngine.get_job_by_id()` returns the first match in memory, so duplicate IDs create ambiguous lookups.

Recommendation:
- Make all job IDs globally unique (example: `job_city_gen_001`, `job_frontier_gen_001`) and update any references.

### 2) Quest-to-item reference break
`rare_001` uses `reward_item: "legendary_dragon_sword"`, but this item does not exist in economy item catalogs.

Why this matters:
- Reward claims can fail or create inconsistent player states.

Recommendation:
- Either add this item to a shop/item file or change `reward_item` to an existing valid item ID.

### 3) Faction reputation keys do not match faction IDs
Faction quest files reward reputation to keys like `"scholars"` and `"city_guard"`, while canonical faction IDs are `f_1`..`f_4`.

Why this matters:
- Reputation progression cannot reliably map to the faction system.

Recommendation:
- Normalize `reward_reputation` keys to canonical faction IDs from `content/world/factions.json`.

### 4) Arabic-only policy violation in player-facing text
`content/economy/shop_special_goods.json` contains English text `(Archetype)` inside `desc_ar` values.

Why this matters:
- Violates the project rule: no English in player-facing narrative/UI content.

Recommendation:
- Replace with an Arabic term such as `(النمط)` or `(الطراز)`.

### 5) “Address player as أنت” rule is not consistently followed
A large majority of story node narrations do not include the explicit pronoun `"أنت"`.

Why this matters:
- The current narrative style is descriptive, but it does not consistently enforce the requested direct-address voice.

Recommendation:
- Add a narrative style pass to enforce second-person phrasing in node templates.

### 6) Weekly contract depth is currently thin
Only 2 weekly contracts exist.

Why this matters:
- Rotational replayability may feel limited for an “epic-scale” persistent RPG.

Recommendation:
- Expand weekly contract sets (at least 8–12 rotating entries with varied objectives and faction ties).

### 7) Archetype coverage mismatch vs target design
Current archetypes are 8 (`explorer`, `guardian`, `scholar`, `outlaw`, `artisan`, `seer`, `commander`, `shadow`), while the design description mentions classes like `merchant`, `hunter`, `mage`, `diplomat`.

Why this matters:
- Product description and shipped content may diverge, causing expectation gaps.

Recommendation:
- Either add missing archetypes and linked content, or update project docs to match implemented archetypes.

## Overall Assessment
The project has strong content scale and good base structural integrity. The most urgent fixes are cross-system key normalization (jobs/factions/items) and strict Arabic presentation compliance. Once these are corrected, the content architecture is well-positioned for expansion.
