import json
import os
import random

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_json(data, filename):
    ensure_dir(filename)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_story(world, parts, nodes_per_part):
    for part in parts:
        nodes = {}
        for i in range(nodes_per_part):
            node_id = f"node_{i:03d}"
            next_1 = f"node_{random.randint(0, nodes_per_part-1):03d}"
            next_2 = f"node_{random.randint(0, nodes_per_part-1):03d}"

            # Text based on world
            if world == "fantasy":
                desc = f"تتقدم في أعماق غابة الأرواح المنسية... الأشجار هنا تبدو وكأنها تهمس بأسرار قديمة. (العقدة {i})"
                c1 = "استخدم السحر لإضاءة الطريق"
                c2 = "امشِ بحذر في الظلام"
            elif world == "past":
                desc = f"غبار الصحراء يغطي بقايا الإمبراطورية العظيمة. تجد أطلالاً تحتوي على نقوش غريبة. (العقدة {i})"
                c1 = "حاول قراءة النقوش"
                c2 = "ابحث عن مدخل سري"
            elif world == "future":
                desc = f"أضواء النيون تعكس على البرك المائية في مدينة النجوم. أصوات الطائرات تملأ السماء. (العقدة {i})"
                c1 = "اختراق النظام الأمني"
                c2 = "الاندماج مع الزحام"
            else:
                desc = f"العالم يبدو مقلوباً، السماء حمراء والأرض كأنها مرآة تعكس كوابيسك. (العقدة {i})"
                c1 = "واجه انعكاسك"
                c2 = "حاول إيجاد بوابة"

            nodes[node_id] = {
                "id": node_id,
                "text_ar": desc,
                "choices": [
                    {"text_ar": c1, "next_node": next_1, "skill_check": "intellect"},
                    {"text_ar": c2, "next_node": next_2, "skill_check": "agility"}
                ],
                "reward_xp": random.randint(10, 50)
            }

        save_json({"nodes": nodes}, f"content/story/{world}/{part}.json")

def generate_jobs():
    archetypes = ["المستكشف", "الحارس", "العالم", "الخارج عن القانون", "الحرفي", "الرائي", "القائد", "الظل"]
    jobs_data = []

    for i in range(1, 101): # Generate 100 jobs
        arch = random.choice(archetypes)
        job = {
            "id": f"job_{i:03d}",
            "title_ar": f"مهمة: {arch} العظيم {i}",
            "desc_ar": f"هذه مهمة خطيرة تتطلب مهارات {arch}. العوائد ستكون مجزية، لكن المخاطر عالية. ستساعدك هذه المهمة في كسب احترام الفصائل وجمع الموارد النادرة.",
            "archetype": arch,
            "base_reward_gold": random.randint(50, 500),
            "base_reward_xp": random.randint(100, 1000),
            "rare_drop_chance": 0.001
        }
        jobs_data.append(job)

    save_json({"jobs": jobs_data}, "content/jobs/index.json")
    save_json({"jobs": jobs_data[:20]}, "content/jobs/general_jobs_city.json")
    save_json({"jobs": jobs_data[20:40]}, "content/jobs/general_jobs_frontier.json")
    # ... more job divisions would go here

def generate_quests():
    quests = []
    for i in range(1, 51):
        quest = {
            "id": f"quest_{i:03d}",
            "title_ar": f"مهمة جانبية: سر الوديان {i}",
            "desc_ar": "لقد وصلتك رسالة غامضة تدعوك للتحقيق في أحداث غريبة. يجب عليك جمع الأدلة ومواجهة التحديات.",
            "stages": [
                {"stage_ar": "تحدث إلى التاجر", "xp": 50},
                {"stage_ar": "اجمع 5 قطع نادرة", "xp": 100},
                {"stage_ar": "اهزم زعيم اللصوص", "xp": 300}
            ]
        }
        quests.append(quest)

    save_json({"quests": quests}, "content/quests/index.json")
    save_json({"quests": quests[:25]}, "content/quests/shared_daily_quests.json")

def generate_economy():
    items = []
    types = ["field_kit", "title", "special_good", "token"]
    for i in range(1, 101):
        t = random.choice(types)
        item = {
            "id": f"item_{i:03d}",
            "name_ar": f"أداة نادرة {i}",
            "desc_ar": "قطعة فريدة من نوعها ذات خصائص سحرية أو تقنية متطورة. يمكن استخدامها لتعزيز قدراتك أو فتح مسارات جديدة.",
            "price": random.randint(100, 10000),
            "rarity": random.choice(["شائع", "نادر", "أسطوري"]),
            "type": t
        }
        items.append(item)

    save_json({"items": items}, "content/economy/shop_index.json")

def generate_characters():
    questions = []
    for i in range(1, 21):
        questions.append({
            "id": f"q_{i}",
            "text_ar": "إذا واجهت طريقاً مسدوداً، ماذا تفعل؟",
            "answers": [
                {"text_ar": "أحطم الجدار بالقوة", "archetype_weight": {"الحارس": 5, "القائد": 3}},
                {"text_ar": "أبحث عن ممر سري", "archetype_weight": {"الظل": 5, "المستكشف": 3}},
                {"text_ar": "أدرس طبيعة العائق", "archetype_weight": {"العالم": 5, "الرائي": 3}},
                {"text_ar": "أبتكر أداة للعبور", "archetype_weight": {"الحرفي": 5}}
            ]
        })
    save_json({"questions": questions}, "content/characters/character_test_questions.json")

def generate_achievements():
    achievements = []
    for i in range(1, 51):
        achievements.append({
            "id": f"achv_{i}",
            "title_ar": f"إنجاز: المستكشف الأعظم {i}",
            "desc_ar": "اكتشف 100 منطقة جديدة واستكمل المهام المرتبطة بها.",
            "reward_title": f"الرحالة {i}",
            "reward_gold": 1000
        })
    save_json({"achievements": achievements}, "content/achievements/index.json")

def generate_factions():
    factions = [
        {"id": "f_1", "name_ar": "حراس العهد", "desc_ar": "تنظيم قديم يحمي الأسرار.", "leader_name_ar": "إلياس"},
        {"id": "f_2", "name_ar": "نقابة الظلال", "desc_ar": "مجموعة من القتلة واللصوص.", "leader_name_ar": "طارق"}
    ]
    save_json({"factions": factions}, "content/world/factions.json")

def main():
    print("Generating Content...")

    # Generate large story files for 4 worlds, 5 parts each, 500 nodes per part (simulating epic scale)
    parts = ["p01_a", "p02_b", "p03_a", "p04_b", "p05_a"]
    for w in ["fantasy", "past", "future", "alternate"]:
        generate_story(w, parts, 100) # Reduced to 100 nodes per part for generation speed, still 2000 nodes total across parts
        print(f"Generated story for {w}")

    generate_jobs()
    print("Generated Jobs")

    generate_quests()
    print("Generated Quests")

    generate_economy()
    print("Generated Economy")

    generate_characters()
    print("Generated Characters")

    generate_achievements()
    print("Generated Achievements")

    generate_factions()
    print("Generated Factions")

    print("Epic Arabic Discord RPG content generation complete!")

if __name__ == "__main__":
    main()
