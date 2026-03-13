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
    fantasy_templates = [
        "تتقدم في أعماق غابة الأرواح المنسية... الأشجار هنا تبدو وكأنها تهمس بأسرار قديمة.",
        "تصل إلى بحيرة زمردية تتلألأ تحت ضوء القمر، حيث تسبح مخلوقات من ضوء.",
        "تواجه كهفاً مظلماً ينبعث منه زئير خافت يرجف له القلب.",
        "يقطع طريقك ساحر متجول يعرض عليك مبادلة لغز بمعلومة.",
        "تجد أطلال قلعة طائرة قد سقطت منذ عصور، سحرها لا يزال ينبض ببطء.",
        "تصادف قرية صغيرة يسكنها أقزام يطلبون مساعدتك في التخلص من وحش يهدد محاصيلهم.",
        "شجرة عملاقة ذات أوراق ذهبية تقف شامخة، جذوعها تخفي مدخلاً سرياً.",
        "تلتقي بجنية صغيرة تعدك بمكافأة إذا ساعدتها في العثور على زهرتها المفقودة.",
        "جسر معلق يتمايل فوق وادٍ عميق، ويبدو أن هناك مخلوقاً يحرس العبور.",
        "تكتشف دائرة من الحجارة السحرية تنبعث منها طاقة دافئة تشفي جراحك.",
        "تسمع صدى موسيقى غامضة تقودك إلى حقل من الزهور المتوهجة.",
        "تواجه نمراً سيفياً ذا فرو فضي، ينظر إليك وكأنه ينتظر إشارة منك.",
        "تجد بئراً قديمة، كلما اقتربت منها تسمع أصواتاً تهمس باسمك.",
        "يظهر أمامك شبح محارب قديم يطلب منك استعادة شرفه المفقود.",
        "تلاحظ آثار أقدام ضخمة محترقة تقود إلى أعلى الجبل القريب.",
        "سحابة كثيفة من الضباب الأرجواني تغطي الطريق، وتشعر بوجود أعين تراقبك.",
        "تلتقي بتاجر عفريت يبيع جرعات سحرية غريبة، بعضها يبدو مشبوهاً.",
        "تصل إلى وادٍ مليء بالبلورات الضخمة التي تعكس صوراً من عوالم أخرى.",
        "تواجه باباً حجرياً ضخماً مقفلاً بأحجية تعتمد على حركة النجوم.",
        "تجد تمثالاً لآلهة منسية يبكي دماءً فضية، وتشعر بطاقة هائلة تنبعث منه."
    ]
    past_templates = [
        "غبار الصحراء يغطي بقايا الإمبراطورية العظيمة. تجد أطلالاً تحتوي على نقوش غريبة.",
        "تقف أمام معبد مهجور، رائحة البخور القديم لا تزال تعبق في الهواء.",
        "تكتشف سيفاً صدئاً مغروزة في حجر، وحوله نقوش تحذر من لمسه.",
        "تلتقي بقافلة تجارية من زمن غابر، يعرضون عليك بضائع لم ترها من قبل.",
        "تجد نفسك في ساحة معركة قديمة، بقايا الدروع والأسلحة تتناثر في كل مكان.",
        "تستكشف مقبرة فرعونية، الفخاخ لا تزال نشطة والظلام دامس.",
        "تسمع أصوات حوافر خيول تقترب، وتدرك أنك في وسط معركة تاريخية.",
        "تصل إلى مدينة مبنية بالكامل من الطين، ويبدو أن سكانها اختفوا فجأة.",
        "تجد لوحة جدارية تروي قصة حضارة زالت بسبب غضب الآلهة.",
        "تواجه حارساً حجرياً عملاقاً يبدو أنه استيقظ من سباته الطويل.",
        "تكتشف مكتبة قديمة مدفونة تحت الرمال، الكتب فيها مصنوعة من ألواح طينية.",
        "ترى برجاً خشبياً محترقاً، ودخان يتصاعد منه رغم مرور قرون.",
        "تجد قناعاً ذهبياً ملقى على الأرض، وما إن تلمسه حتى تسمع أصوات الماضي.",
        "تصل إلى واحة مخفية، المياه فيها صافية ولكن هناك هياكل عظمية حولها.",
        "تواجه متاهة تحت الأرض صُممت لاختبار ذكاء الملوك القدامى.",
        "تلتقي بحكيم أعمى يجلس تحت شجرة زيتون معمرة، يبدو أنه كان ينتظرك.",
        "تكتشف نقوداً ذهبية تحمل صور ملوك لم يذكرهم التاريخ.",
        "ترى نقشاً يصف سلاحاً أسطورياً مخبأً في جبل مجاور.",
        "تصل إلى أطلال قصر فخم، وتتخيل الحفلات التي كانت تقام هنا.",
        "تجد جداراً مليئاً بالثقوب، ويبدو أن سهاماً قديمة لا تزال عالقة فيه."
    ]
    future_templates = [
        "أضواء النيون تعكس على البرك المائية في مدينة النجوم. أصوات الطائرات تملأ السماء.",
        "تدخل إلى منشأة مهجورة حيث الروبوتات المعطلة تومض بإنذارات حمراء.",
        "تجد شريحة بيانات متوهجة ملقاة في زقاق ضيق ومظلم.",
        "توقف مركبة طائرة ويخرج منها شخص آلي يطلب مساعدتك في أمر طارئ.",
        "تتجول في سوق للتقنيات الممنوعة، الباعة هنا يعرضون أطرافاً صناعية متطورة.",
        "تصل إلى برج اتصالات ضخم يخترق الغيوم، ويبدو أنه يبث رسائل مشفرة.",
        "تواجه طائرة بدون طيار تراقب تحركاتك وتبدأ في إصدار أصوات تحذيرية.",
        "تكتشف مختبراً سرياً تُجرى فيه تجارب لدمج البشر مع الآلات.",
        "ترى شاشة إعلانات ثلاثية الأبعاد تعرض أخباراً عن انهيار مجري وشيك.",
        "تجد مركبة فضائية محطمة، ويبدو أن هناك كائناً فضائياً محاصراً بداخلها.",
        "تصل إلى منطقة صناعية ينبعث منها دخان سام، والعمال هنا روبوتات بالكامل.",
        "تواجه عصابة من القراصنة السيبرانيين يطالبونك بتسليم بياناتك الشخصية.",
        "تكتشف حديقة اصطناعية، النباتات فيها مصنوعة من الألياف الضوئية.",
        "تسمع صوت ذكاء اصطناعي يوجهك نحو مخرج آمن من هذه المتاهة المعدنية.",
        "تجد سلاحاً يعمل بالبلازما، لكن طاقته توشك على النفاذ.",
        "تصل إلى محطة قطار مغناطيسي تعمل بسرعة تفوق سرعة الصوت.",
        "ترى أشخاصاً موصولين بشبكات الواقع الافتراضي، غائبين تماماً عن العالم الحقيقي.",
        "تكتشف قاعدة عسكرية مهجورة، والأسلحة فيها لا تزال جاهزة للإطلاق.",
        "تواجه حاجزاً ليزرياً يمنع تقدمك، وتحتاج إلى بطاقة مرور لاختراقه.",
        "تجد كبسولة زمنية مقفلة برقم سري معقد."
    ]
    alternate_templates = [
        "العالم يبدو مقلوباً، السماء حمراء والأرض كأنها مرآة تعكس كوابيسك.",
        "تجد نفسك في غرفة بلا أبواب ولا نوافذ، والجاذبية تبدو منعدمة.",
        "ترى نسخة منك تتحدث بلغة غير مفهومة وتحاول إرشادك لشيء ما.",
        "الأشياء من حولك تذوب وتتشكل من جديد كأنها في حلم لا ينتهي.",
        "تمشي في غابة حيث الأشجار تنمو للأسفل والجذور تمتد نحو السماء.",
        "تصل إلى مدينة مبنية من الزجاج الهش، والهمس هنا قد يحطم المباني.",
        "تواجه ظلاً يتحرك بشكل مستقل عن صاحبه، ويبدو أنه يحمل رسالة.",
        "تكتشف ساعة ضخمة تدور عقاربها بالعكس، وكل تكة تعيدك خطوة للوراء.",
        "ترى نجوماً تتساقط كالمطر، وعندما تلمس الأرض تتحول إلى رماد بارد.",
        "تجد بحراً من الكلمات المكتوبة، وعليك السباحة فيها لتفهم المعنى.",
        "تصل إلى باب يفتح على ذكريات لم تعشها أبداً.",
        "تواجه كائناً مصنوعاً من الدخان الأبيض، يحاول سرقة أفكارك.",
        "تكتشف سلماً يمتد إلى ما لا نهاية، وكل درجة تغير لون العالم.",
        "ترى وجوهاً تظهر وتختفي في جدران الكهف المحيط بك.",
        "تجد نفسك في لعبة شطرنج عملاقة، وأنت أحد البيادق.",
        "تصل إلى حديقة حيث الأزهار تصرخ عندما تقطفها.",
        "تواجه مرآة لا تعكس صورتك، بل تعكس ما تخافه أكثر.",
        "تكتشف مكتبة حيث الكتب فارغة حتى تقرأها بصوت عالٍ.",
        "ترى شمساً زرقاء تبعث برودة قاسية بدلاً من الدفء.",
        "تجد صندوقاً موسيقياً يعزف لحناً يجعلك تنسى من أنت."
    ]

    for part_idx, part in enumerate(parts):
        nodes = {}
        # Determine the next part for inter-part connections
        next_part = parts[part_idx + 1] if part_idx + 1 < len(parts) else parts[0]

        for i in range(nodes_per_part):
            node_id = f"{part}_node_{i:03d}"

            # Ensure proper connections: always have a valid next node or edge logic
            # If it's the last node of a part, make one of the choices link to the next part
            if i == nodes_per_part - 1:
                next_1 = f"{next_part}_node_000"
                next_2 = f"{part}_node_{random.randint(0, nodes_per_part - 1):03d}"
            else:
                next_1_index = i + 1
                next_2_index = random.randint(0, nodes_per_part - 1)
                next_1 = f"{part}_node_{next_1_index:03d}"
                next_2 = f"{part}_node_{next_2_index:03d}"

            # Text based on world
            if world == "fantasy":
                desc = random.choice(fantasy_templates)
                c1 = "استخدم السحر لإضاءة الطريق أو المواجهة"
                c2 = "امشِ بحذر وتجنب الخطر"
            elif world == "past":
                desc = random.choice(past_templates)
                c1 = "حاول قراءة النقوش وفهم التاريخ"
                c2 = "ابحث عن مدخل سري أو طريق بديل"
            elif world == "future":
                desc = random.choice(future_templates)
                c1 = "اختراق النظام الأمني للوصول للمعلومات"
                c2 = "الاندماج مع الزحام والتخفي"
            else:
                desc = random.choice(alternate_templates)
                c1 = "واجه انعكاسك وتحدى الواقع"
                c2 = "حاول إيجاد بوابة للهروب من هذا الكابوس"

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

    # Generate large story files for 4 worlds, 10 parts each, 100 nodes per part (1000 nodes per world, 4000 total)
    parts = [
        "p01_a", "p01_b",
        "p02_a", "p02_b",
        "p03_a", "p03_b",
        "p04_a", "p04_b",
        "p05_a", "p05_b"
    ]
    for w in ["fantasy", "past", "future", "alternate"]:
        generate_story(w, parts, 100)
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
