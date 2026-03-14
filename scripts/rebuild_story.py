import json
import os
import random

worlds = ["fantasy", "past", "future", "alternate"]
parts = ["p01_a", "p01_b", "p02_a", "p02_b", "p03_a", "p03_b", "p04_a", "p04_b", "p05_a", "p05_b"]
archetypes = ["المستكشف", "الحارس", "العالم", "الخارج عن القانون", "الحرفي", "الرائي", "القائد", "الظل"]
skills = ["agility", "strength", "intellect", "magic", "stealth", "crafting", "charisma"]

endings_mapping = {
    "fantasy": ["fantasy_ending_light", "fantasy_ending_shadow"],
    "past": ["past_ending_light", "past_ending_shadow"],
    "future": ["future_ending_light", "future_ending_shadow"],
    "alternate": ["alternate_ending_light", "alternate_ending_shadow"]
}

# Thematic texts for each world to construct paragraphs
themes = {
    "fantasy": {
        "intros": [
            "في قلب الغابة البلورية، حيث تتراقص الأضواء السحرية بين الأشجار القديمة، تقف أمام بوابة منسية تنبعث منها طاقة غامضة.",
            "على قمة الجبل الشاهق الذي يعانق السحاب، تهب رياح باردة محملة بأصوات من الماضي السحيق، محذرة من الخطر القادم.",
            "أمام بحيرة النسيان الهادئة، حيث تعكس المياه سماء مرصعة بنجوم لا تُحصى، تشعر بوجود كائن خفي يراقب تحركاتك.",
            "في أطلال القلعة المفقودة، حيث ينمو الطحلب المتوهج على الجدران المتصدعة، تسمع همسات أرواح سقطت في معارك قديمة."
        ],
        "events": [
            "تكتشف تمثالاً حجرياً يتغير شكله كلما اقتربت منه، وتنبثق منه هالة من الضوء الساحر.",
            "يظهر أمامك ذئب أثيري يحمل في عينيه حكمة العصور، ويبدو أنه يحاول إيصال رسالة لك.",
            "تجد لفيفة قديمة مغطاة بتعويذات متوهجة، وبمجرد لمسها تشعر بتيار من الطاقة يسري في جسدك.",
            "تسمع صدى ضحكات خافتة تتردد بين الأشجار، وتدرك أن الجنيات تلعب في الجوار، ولكن نواياهن غير معروفة."
        ],
        "choices": [
            "اقترب بحذر واستخدم قوتك لكشف الأسرار الخفية.",
            "حاول التواصل مع الكائنات الروحية باستخدام سحرك.",
            "تراجع وابحث عن طريق بديل لتجنب المواجهة المباشرة.",
            "استخدم ذكائك لفك الرموز الغامضة وفهم طبيعة المكان."
        ]
    },
    "past": {
        "intros": [
            "بين أروقة القصر الإمبراطوري العتيق، حيث تفوح رائحة البخور العتيق والمؤامرات، تقف أمام باب مغلق يخفي أسراراً عظيمة.",
            "في قلب السوق المزدحم، حيث يختلط ضجيج التجار بصليل السيوف، تلتقط عيناك شخصاً غامضاً يراقبك من بعيد.",
            "في قبو المكتبة الكبرى، حيث تتكدس المخطوطات القديمة المغبرة، تكتشف خريطة ممزقة تشير إلى موقع مجهول.",
            "أمام ساحة الإعدام الصامتة، حيث تركت الرياح أثرها على المشانق القديمة، تشعر بثقل التاريخ والظلم الذي شهده هذا المكان."
        ],
        "events": [
            "تجد رسالة سرية مشفرة بختم الملك المفقود، تحمل تحذيراً من خيانة وشيكة.",
            "تلتقي بمحارب مخضرم يحمل سيفاً مكسوراً، يروي لك حكاية عن معركة ملحمية لم تُسجل في كتب التاريخ.",
            "تكتشف باباً خفياً خلف رف الكتب، يؤدي إلى ممر مظلم مليء بالفخاخ القاتلة.",
            "تسمع همسات مؤامرة تحاك في الظلام، وتدرك أن حياتك قد تكون في خطر إذا لم تتصرف بسرعة."
        ],
        "choices": [
            "واجه المخاطر بشجاعة واقتحم الممر المظلم.",
            "حاول فك الشفرة واستخراج المعلومات السرية من الرسالة.",
            "استخدم براعتك في التخفي للتسلل خلف الأعداء.",
            "استعن بخبرتك في القتال للتغلب على المحارب المخضرم."
        ]
    },
    "future": {
        "intros": [
            "في شوارع المدينة السايبربانكية المضيئة بالنيون، حيث تتداخل أصوات الآلات مع زخات المطر الحمضي، تقف أمام ناطحة سحاب تخفي أسرار الشركات الكبرى.",
            "داخل المختبر المهجور المليء بالأسلاك المقطوعة والشاشات المحطمة، تكتشف مشروعاً سرياً قد يغير مسار البشرية.",
            "في قلب شبكة البيانات المركزية، حيث تتدفق المعلومات كتيار لا نهائي، تواجه ذكاءً اصطناعياً متمرداً يهدد بالسيطرة على العالم.",
            "على متن المحطة الفضائية المهجورة، حيث يسود الصمت القاتل، تشعر بوجود كائن فضائي يختبئ في الظلام."
        ],
        "events": [
            "تجد رقاقة ذاكرة مشفرة تحتوي على بيانات حساسة للغاية، وبمجرد توصيلها بجهازك تبدأ الأنظمة في الانهيار.",
            "تلتقي بقرصان إلكتروني يعرض عليك المساعدة في اختراق دفاعات الشركة، لكن نواياه غير واضحة.",
            "تكتشف سلاحاً تجريبياً يطلق أشعة طاقة مدمرة، لكنه غير مستقر وقد ينفجر في أي لحظة.",
            "تسمع صوتاً آلياً ينذرك بأنك تجاوزت حدودك، وتدرك أن الأمن على وشك اكتشاف أمرك."
        ],
        "choices": [
            "حاول اختراق النظام باستخدام مهاراتك التقنية.",
            "استخدم السلاح التجريبي لتدمير العقبات التي تعترض طريقك.",
            "ابحث عن طريقة للهروب من المحطة الفضائية قبل فوات الأوان.",
            "تفاوض مع القرصان الإلكتروني للحصول على مساعدته."
        ]
    },
    "alternate": {
        "intros": [
            "في الأراضي القاحلة التي تفصل بين الأبعاد المتعددة، حيث تتلاشى قوانين الفيزياء وتتشوه الألوان، تقف أمام صدع زمني يتوهج بطاقة غريبة.",
            "داخل المتاهة البلورية التي تغير شكلها باستمرار، تجد نفسك محاصراً بين انعكاسات متعددة لشخصيتك.",
            "في قلعة الزمن المتوقفة، حيث تتدلى الساعات من السقف بلا حركة، تكتشف آلة غامضة قد تكون مفتاحاً لعودتك إلى عالمك.",
            "على حافة الهاوية التي تطل على فراغ لا نهائي، تشعر بقوة سحب هائلة تحاول ابتلاعك."
        ],
        "events": [
            "تجد قطعة من الكريستال المتوهج، وبمجرد لمسها تنتقل إلى واقع بديل يختلف تماماً عن واقعك.",
            "تلتقي بنسخة أخرى منك تحمل ذكريات ومشاعر مختلفة، وتحاول إقناعك بتغيير مسارك.",
            "تكتشف أن الآلة الغامضة تتطلب طاقة حيوية لتشغيلها، وتدرك أنك قد تضطر إلى التضحية بجزء من نفسك.",
            "تسمع صوتاً يهمس لك بأسرار الكون، وتدرك أن عقلك قد لا يتحمل كل هذه المعرفة."
        ],
        "choices": [
            "استخدم الكريستال المتوهج للانتقال إلى واقع آخر.",
            "حاول فهم النسخة الأخرى منك واستخلاص المعرفة منها.",
            "شغل الآلة الغامضة باستخدام طاقتك الحيوية.",
            "استخدم قواك العقلية للسيطرة على الصدع الزمني."
        ]
    }
}

def generate_node_id(part_id, index):
    return f"{part_id}_node_{index:03d}"

def generate_choices(world, num_choices=2, current_node=None, next_node=None):
    choices = []
    available_skills = random.sample(skills, min(num_choices, len(skills)))

    for i in range(num_choices):
        text = random.choice(themes[world]["choices"])
        choice = {
            "text_ar": text,
            "next_node": next_node,
            "skill_check": available_skills[i],
            "difficulty": random.randint(10, 20)
        }
        # Add fail node randomly
        if random.random() < 0.3:
            choice["fail_next_node"] = current_node

        choices.append(choice)

    # 15% chance for hidden path
    if random.random() < 0.15:
        arch = random.choice(archetypes)
        choices.append({
            "text_ar": f"استخدم حدسك ({arch}) لاكتشاف ممر خفي.",
            "next_node": next_node,
            "required_archetype": arch
        })

    return choices

def build_story():
    for world in worlds:
        world_dir = f"content/story/{world}"
        os.makedirs(world_dir, exist_ok=True)

        for p_idx, part in enumerate(parts):
            next_part = parts[p_idx + 1] if p_idx + 1 < len(parts) else None

            nodes = {}
            num_nodes = 10

            for n_idx in range(num_nodes):
                node_id = generate_node_id(part, n_idx)
                next_node_id = generate_node_id(part, n_idx + 1) if n_idx + 1 < num_nodes else None

                intro = random.choice(themes[world]["intros"])
                event = random.choice(themes[world]["events"])
                text = f"{intro}\n\n{event}"

                node = {
                    "id": node_id,
                    "text_ar": text,
                    "reward_xp": random.randint(10, 50)
                }

                if next_node_id:
                    node["choices"] = generate_choices(world, random.randint(2, 3), node_id, next_node_id)
                elif next_part:
                    node["next_part_id"] = next_part
                    node["choices"] = generate_choices(world, random.randint(2, 3), node_id, generate_node_id(next_part, 0))
                else: # Final part, endings
                    endings = endings_mapping[world]
                    node["choices"] = [
                        {
                            "text_ar": "اختر مسار النور والحكمة.",
                            "ending_id": endings[0]
                        },
                        {
                            "text_ar": "اختر مسار القوة المظلمة.",
                            "ending_id": endings[1]
                        }
                    ]

                nodes[node_id] = node

            part_data = {
                "part_id": part,
                "world": world,
                "nodes": nodes
            }
            if next_part:
                part_data["next_part_id"] = next_part

            with open(f"{world_dir}/{part}.json", "w", encoding="utf-8") as f:
                json.dump(part_data, f, ensure_ascii=False, indent=2)

def main():
    build_story()
    print("Story rebuild complete.")

if __name__ == "__main__":
    main()
