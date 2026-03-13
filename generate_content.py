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
    # Expanded immersive templates incorporating world-building and avoiding repetitiveness.
    fantasy_templates = [
        "تتقدم في أعماق غابة الأرواح المنسية... الأشجار هنا تبدو وكأنها تهمس بأسرار قديمة.\n\nالضباب يلتف حول قدميك كأنه ثعابين حية، والرياح تعزف لحناً حزيناً عبر الفروع المتشابكة. تشعر بثقل غريب في الهواء، وكأن الغابة نفسها تتنفس وتراقب كل خطوة تخطوها.\n\nهل ستتابع تقدمك في هذا الظلام الموحش، أم ستبحث عن مأوى قبل أن يحل الليل بالكامل؟",
        "تصل إلى بحيرة زمردية تتلألأ تحت ضوء القمر، حيث تسبح مخلوقات من ضوء.\n\nسطح الماء هادئ تماماً، يعكس سماءً مرصعة بالنجوم التي تبدو أقرب مما هي عليه في الواقع. زهور متوهجة تنمو على ضفاف البحيرة، تنبعث منها رائحة حلوة تهدئ الأعصاب المتوترة.\n\nتقترب من حافة المياه، وتلاحظ شيئاً يلمع في الأعماق. هل تجرؤ على الغوص لاكتشافه، أم تكتفي بمراقبة هذا الجمال الساحر؟",
        "تواجه كهفاً مظلماً ينبعث منه زئير خافت يرجف له القلب.\n\nالجدران الصخرية مغطاة بطحالب مضيئة تنبض بضوء خافت، مما يكشف عن رسومات قديمة لمعارك طاحنة بين حراس العهد والوحوش السحيقة. رائحة الكبريت تملأ المكان، محذرة من الخطر الكامن في الداخل.\n\nكلما تقدمت، زاد الزئير وضوحاً. هل تستل سلاحك وتستعد لمواجهة المجهول، أم تتراجع وتبحث عن طريق آخر؟",
        "يقطع طريقك ساحر متجول يعرض عليك مبادلة لغز بمعلومة.\n\nيختبئ وجهه تحت قلنسوة ممزقة، وعيناه تلمعان بذكاء ماكر. يحمل عصا خشبية ملتوية تنبعث منها طاقة غريبة، وفي يده الأخرى يحمل كتاباً قديماً مغلقاً بقفل سحري يحمل شعار فرسان النور.\n\nيقول بصوت خشن: 'أيها المسافر، لدي ما تبحث عنه، ولكن المعرفة لها ثمن'. هل تقبل التحدي وتحاول حل لغزه، أم تتجاهله وتكمل طريقك؟",
        "تجد أطلال قلعة طائرة قد سقطت منذ عصور، سحرها لا يزال ينبض ببطء.\n\nالأحجار الضخمة تطفو في الهواء بشكل عشوائي، متجاهلة قوانين الجاذبية. نباتات غريبة ذات ألوان مبهرة نمت بين الأنقاض، متغذية على بقايا الطاقة السحرية المتسربة.\n\nيبدو أن هناك مدخلاً سرياً يؤدي إلى قبو القلعة، ولكن الحجارة الطافية تشكل عقبة خطيرة. هل تحاول العبور بحذر، أم تبحث عن طريقة لتعطيل السحر المتبقي؟",
        "تتعثر في مخيم مهجور تابع لنقابة الظلال.\n\nالخيام الممزقة ترفرف في مهب الريح الباردة، وبقايا نار المخيم لا تزال دافئة، مما يدل على أنهم غادروا المكان مؤخراً وبسرعة. تجد صندوقاً خشبياً صغيراً مقفلاً بإحكام.\n\nهل تحاول كسر القفل لترى ما بداخله، أم تتبع آثار أقدامهم التي تختفي في عمق الغابة؟",
        "تسمع غناءً عذباً يأتي من قلب الوادي المخفي.\n\nتتبع الصوت لتجد مخلوقاً نصف بشري ونصف طير يغني لحناً يسحر الألباب. الطيور الأخرى تتجمع حوله في صمت رهيب.\n\nهل تقترب للتحدث معه ومقاطعة طقسه السحري، أم تستمع في صمت وتدع سحر الأغنية يجدد طاقتك؟",
        "تقف أمام جسر حجري معلق فوق هاوية لا نهاية لها.\n\nيقف في منتصف الجسر فارس متصلب يبدو وكأنه تحول إلى حجر. يحمل في يده درعاً ضخماً عليه شعار قديم لا تعرفه. الرياح تعوي بقوة، مهددة بإسقاط أي شخص يحاول العبور.\n\nهل تحاول العبور متجاهلاً الفارس الحجري، أم تتفحص التمثال بحثاً عن فخ أو آلية سرية؟"
    ]
    past_templates = [
        "غبار الصحراء يغطي بقايا الإمبراطورية العظيمة. تجد أطلالاً تحتوي على نقوش غريبة.\n\nالشمس الحارقة تضرب الرمال الذهبية، مما يجعل الهواء يرتجف من شدة الحرارة. الأعمدة الحجرية الضخمة تقف كشواهد صامتة على مجد غابر، تحمل أسراراً لم تُكشف بعد.\n\nتقترب من أحد الأعمدة وتحاول مسح الغبار عن النقوش. هل تستخدم مهاراتك في فك الرموز، أم تبحث عن مدخل سري بين الأنقاض؟",
        "تقف أمام معبد مهجور، رائحة البخور القديم لا تزال تعبق في الهواء.\n\nالتماثيل الضخمة للآلهة المنسية تحرس المدخل، وعيونها الحجرية تبدو وكأنها تتابع حركاتك. خطواتك يتردد صداها في القاعة الواسعة، محطمة الصمت الذي ساد لقرون.\n\nفي وسط القاعة، يوجد مذبح حجري عليه بقع دماء قديمة. هل تقترب لتفقد المذبح، أم تستكشف الغرف الجانبية المظلمة؟",
        "تكتشف سيفاً صدئاً مغروزة في حجر، وحوله نقوش تحذر من لمسه.\n\nالسيف يبدو عادياً للوهلة الأولى، ولكنك تشعر بقوة غامضة تنبعث منه، تجذبك نحوه كالمغناطيس. النقوش المحيطة به مكتوبة بلغة قديمة جداً، ويبدو أنها تعويذة حماية قوية تابعة لحراس العهد.\n\nهل تتجاهل التحذيرات وتحاول سحب السيف، أم تحاول قراءة التعويذة لفهم طبيعة اللعنة؟",
        "تلتقي بقافلة تجارية من زمن غابر، يعرضون عليك بضائع لم ترها من قبل.\n\nالملابس الغريبة التي يرتدونها والحيوانات العجيبة التي يستخدمونها في النقل تدل على أنهم جاؤوا من مكان بعيد جداً، أو ربما من زمان آخر. يعرضون عليك أقمشة منسوجة من الضوء وجرعات سحرية ذات ألوان غريبة.\n\nهل تحاول التجارة معهم باستخدام ما تملك، أم تستغل الفرصة لمعرفة المزيد عن أصولهم وجهتهم؟",
        "تجد نفسك في ساحة معركة قديمة، بقايا الدروع والأسلحة تتناثر في كل مكان.\n\nالأرض الجرداء لا تزال تحمل ندوب الحرب الطاحنة، والهياكل العظمية للجنود المحطمة تروي قصة شجاعة ويأس. تشعر بحزن عميق يملأ المكان، وكأن أرواح المحاربين لم تجد السلام بعد.\n\nهل تقوم بالبحث بين الأنقاض عن أي شيء ذي قيمة، أم تؤدي طقوساً لتهدئة الأرواح المعذبة؟",
        "تصل إلى واحة مخفية، المياه فيها صافية ولكن هناك هياكل عظمية حولها.\n\nالنخيل العالي يوفر ظلاً نادراً في هذه الصحراء القاحلة. بجانب المياه، تجد رسالة محفورة على صخرة بدم جاف تحذر من شرب الماء في وقت محدد من اليوم.\n\nهل تتجاهل التحذير وتروي عطشك فوراً، أم تنتظر حتى يحل الظلام لتأمين الموقع أولاً؟",
        "تواجه تمثالاً لأبو الهول نصفه مدفون تحت الرمال.\n\nعيناه المفرغتان تبدوان وكأنهما تراقبان روحك. فجأة، يتردد صوت عميق في رأسك يطرح لغزاً قديماً حول ولادة النجوم وموت الملوك.\n\nهل تجيب على اللغز بثقة، أم تبحث عن طريقة لفتح باب مخفي في قاعدة التمثال؟",
        "تكتشف مكتبة قديمة مدفونة تحت الرمال، الكتب فيها مصنوعة من ألواح طينية.\n\nرفوف المكتبة تمتد لمسافات غير مرئية في الظلام. بعض الألواح محطمة، ولكن إحداها يبدو سليماً وينبض بضوء خافت عندما تقترب منه.\n\nهل تأخذ اللوح السليم معك، أم تقضي وقتاً في فك شفرات الرموز المحفورة عليه؟"
    ]
    future_templates = [
        "أضواء النيون تعكس على البرك المائية في مدينة النجوم. أصوات الطائرات تملأ السماء.\n\nالمباني الزجاجية الشاهقة تخترق الغيوم، والشاشات الإعلانية العملاقة تعرض منتجات لم تكن تتخيل وجودها. الزحام الشديد يجعلك تشعر بالضياع في هذا العالم التكنولوجي المعقد.\n\nفي زاوية مظلمة، تلاحظ شخصاً يرتدي معطفاً طويلاً ويراقبك بصمت. هل تقترب منه لمعرفة نواياه، أم تندمج مع الزحام للهروب من نظراته؟",
        "تدخل إلى منشأة مهجورة حيث الروبوتات المعطلة تومض بإنذارات حمراء.\n\nالأسلاك المتدلية من السقف تصدر شرارات كهربائية، ورائحة المعدن المحترق تملأ الهواء. الشاشات المحطمة تعرض رموزاً غير مفهومة، وكأنها تحاول إيصال رسالة أخيرة قبل أن تنطفئ إلى الأبد.\n\nتسمع صوت خطوات معدنية تقترب منك من الممر المظلم. هل تستعد للمواجهة، أم تبحث عن طريقة لتفعيل أنظمة الدفاع في المنشأة؟",
        "تجد شريحة بيانات متوهجة ملقاة في زقاق ضيق ومظلم.\n\nالشريحة تبدو متطورة جداً، وتصدر نبضات ضوئية خافتة كأنها قلب ينبض بالمعلومات. لا شك أن من أسقطها يبحث عنها بشدة، وأنها تحتوي على أسرار خطيرة، ربما تفضح أعمال نقابة الظلال في هذا العصر.\n\nهل تحتفظ بالشريحة وتحاول فك تشفيرها، أم تتركها في مكانها وتتجنب التورط في مشاكل لا حصر لها؟",
        "توقف مركبة طائرة ويخرج منها شخص آلي يطلب مساعدتك في أمر طارئ.\n\nالشخص الآلي يبدو مصاباً بأضرار جسيمة، وصوته يتقطع بشكل مخيف. يخبرك أن هناك هجوماً سيبرانياً وشيكاً سيعطل جميع أنظمة المدينة، وأنه يحتاج إلى مهاراتك لمنع الكارثة.\n\nهل تثق في هذا الآلي وتتعاون معه، أم تشك في نواياه وترفض المساعدة؟",
        "تتجول في سوق للتقنيات الممنوعة، الباعة هنا يعرضون أطرافاً صناعية متطورة.\n\nالجو مليء بالتوتر والشك، والأسلحة تظهر بوضوح تحت معاطف الباعة والزبائن على حد سواء. كل شيء معروض للبيع هنا، من الأسلحة الفتاكة إلى الذكريات المستعارة.\n\nتلاحظ كشكاً صغيراً يعرض أداة تبدو وكأنها مفتاح لفتح أي قفل إلكتروني. هل تحاول التفاوض لشرائها، أم تستخدم مهاراتك لسرقتها دون أن يلاحظ أحد؟",
        "تصل إلى قمة ناطحة سحاب، حيث مهبط للطائرات يعج بالحركة.\n\nتسمع محادثة مشبوهة بين مسؤولين حكوميين حول تدمير قطاع كامل من المدينة لإخفاء أدلة. طائرة سوداء تقترب من المهبط.\n\nهل تحاول اختراق الطائرة لسرقة الأدلة، أم تسجل المحادثة وتختفي في الظلام؟",
        "تكتشف حديقة اصطناعية، النباتات فيها مصنوعة من الألياف الضوئية.\n\nفي منتصف الحديقة، تجد نظاماً مركزياً يتحكم في الطقس، ويبدو أنه قد تم التلاعب به لإنتاج عواصف سامة. شاشة تحكم صغيرة تطلب إدخال كلمة مرور بيومترية.\n\nهل تحاول اختراق النظام البيومتري، أم تبحث عن المسؤول عن هذا التلاعب بين الزوار الآليين للحديقة؟",
        "تجد نفسك في شبكة واقع افتراضي سرية.\n\nالبيئة من حولك تتحول بين شوارع طوكيو القديمة ومناظر فضائية سريالية. واجهة النظام تخبرك بأنك مستهدف من قبل برامج أمنية قاتلة (IC).\n\nهل تشن هجوماً مضاداً لتدمير البرامج الأمنية، أم تبحث عن باب خلفي للخروج من الشبكة بأمان؟"
    ]
    alternate_templates = [
        "العالم يبدو مقلوباً، السماء حمراء والأرض كأنها مرآة تعكس كوابيسك.\n\nلا يوجد أعلى ولا أسفل، والجاذبية تتغير بشكل عشوائي مع كل خطوة تخطوها. الأصوات هنا مشوهة، وتسمع همسات غير مفهومة تأتي من كل اتجاه، وكأن العالم نفسه يحاول التحدث إليك.\n\nترى شكلاً غامضاً يطفو في المسافة، ويبدو أنه يلوح لك بالاقتراب. هل تتبعه في هذا الخراب المرعب، أم تحاول إيجاد طريقة للعودة إلى واقعك؟",
        "تجد نفسك في غرفة بلا أبواب ولا نوافذ، والجاذبية تبدو منعدمة.\n\nالأثاث يطفو بحرية حولك، والأشياء تتصادم ببعضها البعض مصدرة أصواتاً غريبة. لا يوجد مخرج واضح، ولكنك تلاحظ أن الجدران تتنفس وكأنها حية، ويتغير لونها باستمرار.\n\nهل تحاول العثور على نقطة ضعف في الجدران لكسرها، أم تجلس وتنتظر ما سيحدث في هذا الكابوس؟",
        "ترى نسخة منك تتحدث بلغة غير مفهومة وتحاول إرشادك لشيء ما.\n\nالنسخة تبدو مطابقة لك تماماً، ولكن ملامح وجهها مشوهة بشكل مخيف، وتعبيراتها تتغير بسرعة بين الخوف والغضب. تحاول أن تشرح لك شيئاً مهماً، ولكن كلماتها تبدو وكأنها طلاسم.\n\nهل تحاول فهم ما تقوله عبر إيماءاتها، أم تتجاهلها وتكمل طريقك، خائفاً من أن تكون فخاً؟",
        "الأشياء من حولك تذوب وتتشكل من جديد كأنها في حلم لا ينتهي.\n\nالأشجار تتحول إلى وحوش، والصخور تتحول إلى مياه. لا شيء ثابت في هذا العالم المتقلب، وكل ما تعتقد أنك تعرفه يتغير في غمضة عين. تشعر وكأنك تفقد عقلك تدريجياً.\n\nهل تحاول التمسك بما هو حقيقي ومقاومة هذا التغيير، أم تستسلم للتيار وتدع هذا العالم يقودك إلى وجهة مجهولة؟",
        "تمشي في غابة حيث الأشجار تنمو للأسفل والجذور تمتد نحو السماء.\n\nالأوراق تتساقط نحو الأعلى، والأمطار تهطل من الأرض إلى السماء. هذا المكان يتحدى كل قوانين الطبيعة، وتشعر وكأنك تمشي على سقف العالم. كل خطوة تبدو وكأنها قفزة في الفراغ.\n\nتلاحظ أن هناك ضوءاً غريباً ينبعث من جذع إحدى الأشجار المقلوبة. هل تقترب لاستكشاف مصدر الضوء، أم تبتعد خوفاً من أن يكون فخاً من صنع هذا العالم الغريب؟",
        "تدخل مدينة مصنوعة بالكامل من الزجاج الهش.\n\nأي صوت أعلى من الهمس يتسبب في تصدع المباني. ترى مخلوقات شبحية تنزلق داخل الزجاج، تراقبك بعيون فارغة. باب ضخم من الزجاج المعتم يقف في نهاية الشارع.\n\nهل تمشي بهدوء وحذر نحو الباب، أم تحاول التواصل مع المخلوقات الشبحية عبر التخاطر؟",
        "تكتشف ساعة ضخمة تدور عقاربها بالعكس، وكل تكة تعيدك خطوة للوراء.\n\nالمكان مليء بالتروس والمسننات العائمة. مع كل تكة، تشعر بأن ذكرياتك عن عوالمك الأخرى بدأت تتلاشى تدريجياً.\n\nهل تحاول تحطيم الترس الرئيسي لإيقاف الزمن، أم تركز ذهنك للحفاظ على ذكرياتك أثناء المرور؟",
        "ترى نجوماً تتساقط كالمطر، وعندما تلمس الأرض تتحول إلى رماد بارد.\n\nتقف على حافة جرف يطل على فجوة عدمية تبتلع كل شيء. شخص غريب يرتدي عباءة من الضباب يقف على الحافة، يعرض عليك صفقة للنجاة من هذا العالم المنهار.\n\nهل تقبل الصفقة دون معرفة الثمن، أم ترفضها وتبحث عن حل جذري لهذا الانهيار؟"
    ]

    archetypes = ["المستكشف", "الحارس", "العالم", "الخارج عن القانون", "الحرفي", "الرائي", "القائد", "الظل"]

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

            # Create hidden paths randomly
            choice_1 = {"text_ar": c1, "next_node": next_1, "skill_check": "intellect"}
            choice_2 = {"text_ar": c2, "next_node": next_2, "skill_check": "agility"}

            if random.random() < 0.15: # 15% chance to have a hidden path
                arch = random.choice(archetypes)
                choice_3 = {
                    "text_ar": f"استخدم مهاراتك الخفية ({arch}) لفتح مسار سري",
                    "next_node": next_1, # could link to a special node, but next_1 works
                    "required_archetype": arch
                }
                choices = [choice_1, choice_2, choice_3]
            else:
                choices = [choice_1, choice_2]

            nodes[node_id] = {
                "id": node_id,
                "text_ar": desc,
                "choices": choices,
                "reward_xp": random.randint(10, 50)
            }

            # Add explicit part transition to the last node to guarantee safety
            if i == nodes_per_part - 1:
                nodes[node_id]["next_part_id"] = next_part

        save_json({
            "part_id": part,
            "world": world,
            "next_part_id": next_part,
            "nodes": nodes
        }, f"content/story/{world}/{part}.json")

def generate_jobs():
    archetypes = {
        "explorer": "المستكشف",
        "guardian": "الحارس",
        "scholar": "العالم",
        "outlaw": "الخارج عن القانون",
        "artisan": "الحرفي",
        "seer": "الرائي",
        "commander": "القائد",
        "shadow": "الظل"
    }

    jobs_data = []

    # Generate General Jobs
    for i in range(1, 41):
        jobs_data.append({
            "id": f"job_gen_{i:03d}",
            "title_ar": f"مهمة عامة: تنظيف الحدود {i}",
            "desc_ar": "هناك تهديدات مستمرة على حدود المدينة. نحتاج إلى متطوعين لحماية القوافل التجارية من قطاع الطرق.",
            "archetype": "general",
            "base_reward_gold": random.randint(20, 100),
            "base_reward_xp": random.randint(50, 200),
            "rare_drop_chance": 0.001
        })

    save_json({"jobs": jobs_data}, "content/jobs/index.json")
    save_json({"jobs": jobs_data[:20]}, "content/jobs/general_jobs_city.json")
    save_json({"jobs": jobs_data[20:40]}, "content/jobs/general_jobs_frontier.json")

    # Generate Archetype Specific Jobs
    for arch_id, arch_name_ar in archetypes.items():
        arch_jobs = []
        for i in range(1, 21):
            rare_items = ["token_of_mastery", "ancient_relic", "glowing_crystal", "shadow_dagger", "star_map"]
            chosen_rare = random.choice(rare_items)
            arch_jobs.append({
                "id": f"job_{arch_id}_{i:03d}",
                "title_ar": f"مهمة حصرية: إرث {arch_name_ar} {i}",
                "desc_ar": f"وردت تقارير عن تحركات مشبوهة في المنطقة. هذه المهمة تتطلب حدة ذكائك وخبرتك كـ {arch_name_ar}. الفشل ليس خياراً، لأن حياة الأبرياء تعتمد على مهاراتك الفريدة لحل هذا اللغز.",
                "archetype": arch_id,
                "base_reward_gold": random.randint(150, 600),
                "base_reward_xp": random.randint(400, 1200),
                "rare_drop_chance": 0.1, # 10% rare drop chance
                "rare_event": {
                    "event_text_ar": f"في لحظة حاسمة أثناء إنجاز المهمة، اعتمدت على مهاراتك الفائقة كـ {arch_name_ar} وكشفت غرفة سرية مخفية خلف جدار وهمي!",
                    "bonus_item": chosen_rare
                }
            })
        save_json({"jobs": arch_jobs}, f"content/jobs/{arch_id}_jobs.json")

def generate_quests():
    # 1. Daily Quests
    daily_quests = []
    for i in range(1, 21):
        daily_quests.append({
            "id": f"daily_quest_{i:03d}",
            "title_ar": f"الواجب اليومي: مساعدة سكان المدينة {i}",
            "desc_ar": "يطلب منك أحد السكان مساعدته في إتمام بعض الأعمال الروتينية لضمان سلامة الحي.",
            "stages": [
                {"stage_ar": "تأكد من تأمين الأبواب الخارجية.", "xp": 20},
                {"stage_ar": "قم بجمع بعض الأعشاب الطبية من الغابة القريبة.", "xp": 30},
                {"stage_ar": "أوصل الإمدادات للحراس على الأسوار.", "xp": 50}
            ],
            "reward_gold": 100
        })
    save_json({"quests": daily_quests}, "content/quests/shared_daily_quests.json")

    # 2. Investigation Quests
    investigation_quests = []
    for i in range(1, 11):
        investigation_quests.append({
            "id": f"inv_quest_{i:03d}",
            "title_ar": f"تحقيق: سرقة الآثار القديمة الجزء {i}",
            "desc_ar": "لقد اختفت قطع أثرية مهمة من المتحف الكبير. السارق ترك أدلة غامضة يجب تتبعها.",
            "stages": [
                {"stage_ar": "استجوب حارس المتحف في وردية الليل.", "xp": 100},
                {"stage_ar": "ابحث عن بصمات أو آثار أقدام بالقرب من الواجهة المحطمة.", "xp": 150},
                {"stage_ar": "تتبع أثر الساحر الهارب في الأسواق التحتية.", "xp": 300}
            ],
            "reward_gold": 500,
            "next_quest_id": f"inv_quest_{i+1:03d}" if i < 10 else None
        })
    save_json({"quests": investigation_quests}, "content/quests/shared_investigation_quests.json")

    # 3. Archetype Quests (Explorer, Guardian, Scholar, Shadow)
    archetypes = [
        ("explorer", "المستكشف", "رسم خرائط الكهوف المظلمة"),
        ("guardian", "الحارس", "الدفاع عن القافلة الملكية"),
        ("scholar", "العالم", "فك تشفير المخطوطات المحرمة"),
        ("shadow", "الظل", "اغتيال زعيم العصابة")
    ]

    for arch_id, arch_name, quest_theme in archetypes:
        chains = []
        for i in range(1, 11):
            chains.append({
                "id": f"arch_{arch_id}_{i:03d}",
                "title_ar": f"مهمة {arch_name}: {quest_theme} ({i})",
                "desc_ar": f"لقد تم اختيارك لهذه المهمة الصعبة لأنك {arch_name} متمرس. استخدم مهاراتك الخاصة لإنجاز العمل.",
                "required_archetype": arch_id,
                "stages": [
                    {"stage_ar": "التحضير وجمع الموارد المطلوبة.", "xp": 200},
                    {"stage_ar": "الوصول إلى نقطة الهدف متجاوزاً المخاطر.", "xp": 300},
                    {"stage_ar": "إتمام المهمة والعودة بأمان.", "xp": 500}
                ],
                "reward_gold": 1000
            })
        save_json({"quests": chains}, f"content/quests/archetype_{arch_id}_chains.json")

    # 4. Rare Quest Chains
    rare_quests = [
        {
            "id": "rare_001",
            "title_ar": "السلسلة الأسطورية: سيف التنين القديم",
            "desc_ar": "مهمة نادرة جداً تبدأ بالعثور على مقبض سيف مكسور ينبض بالحرارة.",
            "stages": [
                {"stage_ar": "تحدث مع الحداد الأعمى في الجبل البركاني.", "xp": 1000},
                {"stage_ar": "اجمع ثلاثة أحجار نار من عش التنين.", "xp": 2000},
                {"stage_ar": "اعد تشكيل السيف في لهب البركان.", "xp": 5000}
            ],
            "reward_gold": 10000,
            "reward_item": "legendary_dragon_sword"
        }
    ]
    save_json({"quests": rare_quests}, "content/quests/rare_quest_chains.json")

    # 5. Faction Quests
    faction_city = [{"id": f"fac_city_{i:03d}", "title_ar": f"ولاء المدينة {i}", "desc_ar": "عزز سمعتك مع فصائل المدينة.", "stages": [{"stage_ar": "قم بدورية", "xp": 50}], "reward_reputation": {"city_guard": 10}} for i in range(1, 11)]
    faction_archive = [{"id": f"fac_arch_{i:03d}", "title_ar": f"أسرار الأرشيف {i}", "desc_ar": "اكتشف المعرفة المفقودة.", "stages": [{"stage_ar": "ترجم الكتاب", "xp": 50}], "reward_reputation": {"scholars": 10}} for i in range(1, 11)]

    save_json({"quests": faction_city}, "content/quests/faction_city_quests.json")
    save_json({"quests": faction_archive}, "content/quests/faction_archive_quests.json")
    save_json({"index": "quests directory"}, "content/quests/index.json")

def generate_economy():
    # 1. Titles
    titles = []
    for i in range(1, 21):
        titles.append({
            "id": f"title_{i:03d}",
            "name_ar": f"لقب: قاهر الظلام {i}",
            "desc_ar": "لقب فخري يظهر بجانب اسمك، يثبت شجاعتك في المعارك.",
            "price": i * 1000,
            "currency": "gold",
            "type": "title",
            "rarity": "نادر"
        })
    save_json({"items": titles}, "content/economy/shop_titles.json")

    # 2. Field Kits
    kits = []
    for i in range(1, 21):
        kits.append({
            "id": f"kit_{i:03d}",
            "name_ar": f"حقيبة إسعافات ميدانية {i}",
            "desc_ar": "تحتوي على ضمادات وجرعات سحرية لتعويض الصحة والطاقة أثناء المهام الطويلة.",
            "price": 500,
            "currency": "gold",
            "type": "field_kit",
            "rarity": "شائع"
        })
    save_json({"items": kits}, "content/economy/shop_field_kits.json")

    # 3. Tokens
    tokens = []
    for i in range(1, 11):
        tokens.append({
            "id": f"token_{i:03d}",
            "name_ar": f"عملة الفصيل {i}",
            "desc_ar": "عملة خاصة تُستخدم لشراء سلع نادرة من الفصائل المحلية.",
            "price": 2000,
            "currency": "gold",
            "type": "token",
            "rarity": "أسطوري"
        })
    save_json({"items": tokens}, "content/economy/shop_tokens.json")

    # 4. Special Goods
    special = []
    for i in range(1, 11):
        special.append({
            "id": f"special_{i:03d}",
            "name_ar": f"مخطوطة النسيان {i}",
            "desc_ar": "قطعة نادرة جداً تسمح لك بإعادة توزيع نقاط مهاراتك وتغيير نمطك (Archetype).",
            "price": 5, # Requires special layered currency
            "currency": "token",
            "type": "special_good",
            "rarity": "أسطوري"
        })
    save_json({"items": special}, "content/economy/shop_special_goods.json")

    # 5. Index
    save_json({"index": "economy directory"}, "content/economy/shop_index.json")

def generate_characters():
    # 1. Generate Character Definitions
    character_defs = {
        "archetypes": [
            {"id": "explorer", "name_ar": "المستكشف", "desc_ar": "شخص يدفعه الفضول لكشف المجهول. لا يخاف من الغوص في أعماق العوالم المنسية.", "bonus_skill": "agility"},
            {"id": "guardian", "name_ar": "الحارس", "desc_ar": "درع يحمي الضعفاء، يعتمد على القوة والشجاعة للوقوف في وجه الخطر.", "bonus_skill": "strength"},
            {"id": "scholar", "name_ar": "العالم", "desc_ar": "باحث عن المعرفة، يحل الألغاز القديمة بذكائه وحكمته.", "bonus_skill": "intellect"},
            {"id": "outlaw", "name_ar": "الخارج عن القانون", "desc_ar": "يعيش بقواعده الخاصة، ماهر في الهروب والتلاعب.", "bonus_skill": "agility"},
            {"id": "artisan", "name_ar": "الحرفي", "desc_ar": "مبدع يرى في كل مادة خام فرصة لصنع شيء عظيم.", "bonus_skill": "crafting"},
            {"id": "seer", "name_ar": "الرائي", "desc_ar": "متصل بعوالم الروح، يرى ما لا يستطيع الآخرون رؤيته.", "bonus_skill": "magic"},
            {"id": "commander", "name_ar": "القائد", "desc_ar": "صاحب كاريزما ورؤية استراتيجية، يقود الآخرين نحو النصر.", "bonus_skill": "charisma"},
            {"id": "shadow", "name_ar": "الظل", "desc_ar": "يتحرك في الظلام بلا أثر، خبير في التخفي والتسلل.", "bonus_skill": "stealth"}
        ]
    }
    save_json(character_defs, "content/characters/character_defs.json")

    # 2. Generate Personality Test
    questions = [
        {
            "id": "q_1",
            "text_ar": "أثناء رحلتك، وجدت قرية تحترق. ما هو أول رد فعل لك؟",
            "answers": [
                {"text_ar": "أندفع لإنقاذ المحاصرين في النيران.", "archetype_weight": {"الحارس": 5, "القائد": 2}},
                {"text_ar": "أبحث عن مصدر الحريق لإيقافه من الجذور.", "archetype_weight": {"العالم": 4, "الرائي": 3}},
                {"text_ar": "أراقب من بعيد للبحث عن الناهبين وأخذ غنائمهم.", "archetype_weight": {"الخارج عن القانون": 5, "الظل": 3}},
                {"text_ar": "أحاول بناء حاجز سريع لمنع انتشار النيران.", "archetype_weight": {"الحرفي": 5}}
            ]
        },
        {
            "id": "q_2",
            "text_ar": "تجد خريطة قديمة ممزقة تشير إلى كنز مخفي في غابة مميتة. ماذا تفعل؟",
            "answers": [
                {"text_ar": "أجمع المؤن وأتجه للغابة فوراً لاستكشاف المجهول.", "archetype_weight": {"المستكشف": 5}},
                {"text_ar": "أقوم بتحليل الخريطة ورموزها لتجنب الفخاخ.", "archetype_weight": {"العالم": 5}},
                {"text_ar": "أجمع فريقاً من المقاتلين لقيادتهم نحو الكنز.", "archetype_weight": {"القائد": 5}},
                {"text_ar": "أستخدم حدسي وأرواح الغابة لإرشادي.", "archetype_weight": {"الرائي": 5}}
            ]
        }
    ]

    # Generate remaining questions to hit 20 deep questions
    for i in range(3, 21):
        questions.append({
            "id": f"q_{i}",
            "text_ar": f"تواجه عقبة غامضة في طريقك تتطلب حلاً سريعاً. (سؤال {i})",
            "answers": [
                {"text_ar": "أواجه العقبة بشجاعة وقوة بدنية.", "archetype_weight": {"الحارس": 4, "القائد": 2}},
                {"text_ar": "أتسلل من حول العقبة دون أن يلاحظني أحد.", "archetype_weight": {"الظل": 4, "الخارج عن القانون": 2}},
                {"text_ar": "أدرس طبيعة العقبة وأبتكر حلاً ذكياً.", "archetype_weight": {"العالم": 4, "الحرفي": 2}},
                {"text_ar": "أستكشف محيط العقبة للعثور على مسار بديل.", "archetype_weight": {"المستكشف": 4, "الرائي": 2}}
            ]
        })
    save_json({"questions": questions}, "content/characters/character_test_questions.json")

def generate_achievements():
    def create_achvs(category_ar, count):
        return [
            {
                "id": f"achv_{category_ar}_{i:03d}",
                "title_ar": f"إنجاز {category_ar}: مستوى {i}",
                "desc_ar": f"لقد أثبت جدارتك في مجال {category_ar}. واصل التقدم لفتح المزيد من الأسرار والمكافآت.",
                "reward_title": f"خبير {category_ar}",
                "reward_gold": i * 500
            } for i in range(1, count + 1)
        ]

    save_json({"achievements": create_achvs("الهوية", 10)}, "content/achievements/identity_achievements.json")
    save_json({"achievements": create_achvs("الاقتصاد", 10)}, "content/achievements/economy_achievements.json")
    save_json({"achievements": create_achvs("السمعة", 10)}, "content/achievements/reputation_achievements.json")
    save_json({"achievements": create_achvs("الإنجازات الكبرى", 10)}, "content/achievements/milestone_achievements.json")
    save_json({"achievements": create_achvs("الاكتشاف", 10)}, "content/achievements/discovery_achievements.json")
    save_json({"index": "achievements directory"}, "content/achievements/index.json")

def generate_world_data():
    factions = [
        {"id": "f_1", "name_ar": "حراس العهد", "desc_ar": "تنظيم قديم يحمي الأسرار التاريخية العظيمة من الوقوع في الأيدي الخطأ. يُقال إن قادتهم يمتلكون أعماراً طويلة تتجاوز البشر الطبيعيين بفضل معرفتهم العميقة.", "leader_name_ar": "إلياس الحكيم"},
        {"id": "f_2", "name_ar": "نقابة الظلال", "desc_ar": "مجموعة سرية من القتلة واللصوص يتحكمون في الأسواق السوداء وشبكات المعلومات التحتية. لكل شيء ثمن لديهم، ولا يتدخلون إلا إذا كانت الأرباح طائلة.", "leader_name_ar": "طارق الصامت"},
        {"id": "f_3", "name_ar": "فرسان النور", "desc_ar": "نظام عسكري صارم يحافظ على النظام العام ويحارب الفوضى بكل أشكالها. يمتلكون جيشاً منظماً ولكنهم يُعرفون بقسوتهم في تطبيق العدالة.", "leader_name_ar": "سيران قائدة الجيوش"},
        {"id": "f_4", "name_ar": "باحثو الفراغ", "desc_ar": "طائفة مهووسة بدراسة العوالم الموازية وبوابات الأبعاد. الكثير منهم فقدوا عقولهم إثر رؤيتهم حقائق لا يتحملها الإدراك البشري.", "leader_name_ar": "أوريان المستبصر"}
    ]
    save_json({"factions": factions}, "content/world/factions.json")

    npcs = [
        {"id": "npc_001", "name_ar": "التاجر المجهول", "role": "تاجر سلع نادرة", "location": "الأسواق التحتية", "dialogue_ar": "لدي بضائع لم ترها من قبل، قطع جُمعت من عوالم منسية... ولكن، هل تملك الثمن الذي أطلبه؟ تذكر، الذهب ليس العملة الوحيدة هنا."},
        {"id": "npc_002", "name_ar": "العرافة العمياء", "role": "موجهة مهام روحية", "location": "غابة الأرواح", "dialogue_ar": "عيناي لا تريان النور المادي، ولكني أرى مسارات مصيرك بوضوح تام... هناك ظلال تتجمع حولك أيها المسافر، احذر من الخيارات التي تبدو سهلة."},
        {"id": "npc_003", "name_ar": "الحداد الأسطوري", "role": "صانع أسلحة ودروع", "location": "الجبل البركاني", "dialogue_ar": "الفولاذ يجب أن يطرق وهو ساخن، تماماً كشخصيتك. أحضر لي المعادن النادرة من أعماق الكهوف، وسأصنع لك درعاً يتحمل نيران التنانين."},
        {"id": "npc_004", "name_ar": "الرحالة الغامض", "role": "حامل أخبار", "location": "بوابات المدينة", "dialogue_ar": "لقد جُبت العوالم الأربعة، ورأيت نجوماً تموت وحضارات تولد. أنت فقط في بداية رحلتك. ابحث عن الآثار القديمة، فهي تحمل مفاتيح لأسئلة لم تطرحها بعد."}
    ]
    save_json({"npcs": npcs}, "content/world/npcs.json")

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

    generate_world_data()
    print("Generated World Data")

    print("Epic Arabic Discord RPG content generation complete!")

if __name__ == "__main__":
    main()
