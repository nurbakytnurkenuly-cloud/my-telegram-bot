import pandas as pd
import random
from telebot import types
from config import bot, user_states, reg_states, EXCEL_FILE, CHANNEL_ID, CHANNEL_URL
import database, keyboards, quiz_engine
from datetime import datetime
import report_generator
from apscheduler.schedulers.background import BackgroundScheduler
import motivator
import config

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_") or call.data.startswith("reject_"))
def admin_decision(call):
    print(f"DEBUG: Батырма басылды! Келген дерек: {call.data}")  # Бұл консольде шығуы керек

    try:
        action, uid = call.data.split("_")
        print(f"DEBUG: Action: {action}, UID: {uid}")
    except Exception as e:
        print(f"DEBUG: Қателік (split кезінде): {e}")
        return

    if action == "confirm":
        # Дерекқорды жаңарту
        db = database.load_db()
        print(f"DEBUG: База жүктелді. UID бар ма?: {uid in db}")

        if uid in db:
            db[uid]['is_paid'] = True
            database.save_db(db)
            print("DEBUG: База жаңартылды!")

        bot.send_message(uid, "🎉 Төлеміңіз расталды! Енді барлық мүмкіндіктер ашылды.")
        bot.edit_message_caption("✅ Төлем расталды!", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif action == "reject":
        bot.send_message(uid, "❌ Төлеміңіз расталмады.")
        bot.edit_message_caption("❌ Төлем қабылданбады.", chat_id=call.message.chat.id,
                                 message_id=call.message.message_id)


def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception as err:
        print(f"Тексеру қатесі: {err}")
        return False


@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)

#КАНАЛҒА ЖАЗЫЛМАҒАН БОЛСА - ТІРКЕУ
    if not is_subscribed(uid):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Каналға жазылу", url=CHANNEL_URL))
        markup.add(types.InlineKeyboardButton("✅ Жазылдым", callback_data="check_subscription"))
        bot.send_message(uid,
                         "👋 Сәлем! Ботты қолдану үшін алдымен біздің каналға жазылуыңыз қажет.\n\n"
                         "Жазылып болған соң «Жазылдым» батырмасын басыңыз 👇",
                         reply_markup=markup)
        return

#КАНАЛҒА ЖАЗЫЛҒАН БОЛСА - ТІРКЕУ
    db = database.load_db()
    if uid not in db:
        bot.send_message(uid,
                         "Сәлем, Жас түлек! Мен сенің биология пәнінен көмекшіңмін.\n\n"
                         "Бастамас бұрын танысып алайық. Аты-жөнің кім?")
        reg_states[uid] = {"step": "name"}
    else:
        # Астыңғы менюді шығарамыз
        bot.send_message(uid, f"Қайта қош келдің, {db[uid]['name']}!", reply_markup=keyboards.default_reply())
        bot.send_message(uid, "Негізгі мәзір:                                   .", reply_markup=keyboards.main_menu())


#ҚАЛАСЫН ТІРКЕУ
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    uid = str(message.chat.id)
    text = message.text

    # --- ТІРКЕЛУ ПРОЦЕСІ ---
    if uid in reg_states:
        if reg_states[uid]["step"] == "name":
            reg_states[uid]["name"] = text
            reg_states[uid]["step"] = "city"
            bot.send_message(uid, "Қай қаладансың?")

        elif reg_states[uid]["step"] == "city":
            reg_states[uid]["city"] = text  # Қаланы сақтап қаламыз
            reg_states[uid]["step"] = "course"  # КЕЛЕСІ ҚАДАМҒА ӨТКІЗЕМІЗ
            bot.send_message(uid, "Juz40 курсына қатысасың ба?", reply_markup=keyboards.course_reply())

        elif reg_states[uid]["step"] == "course":
            name = reg_states[uid]["name"]
            city = reg_states[uid]["city"]

            raw_text = text
            if raw_text == "Иә, смарттамын":
                course = "Смарт"
            elif raw_text == "Иә, джуниордамын":
                course = "Джуниор"
            elif raw_text == "Басқа курс":
                course = "Басқа курс"
            elif raw_text == "Жоқ":
                course = "Курста емес"
            elif raw_text == "Оқушы емеспін":
                course = "Оқушы емес"
            else:
                course = raw_text

            username = message.from_user.username
            db = database.load_db()

            # Базаға толық сақтаймыз
            db[uid] = {
                "name": name,
                "city": city,
                "course": course,
                "username": username,
                "is_paid": False,  # МІНДЕТТІ ТҮРДЕ ОСЫНЫ ҚОСЫҢЫЗ
                "reg_date": datetime.now().strftime("%d.%m.%Y"),
                "correct": 0,
                "total": 0,
                "chapter_mistakes": {}
            }
            database.save_db(db)
            del reg_states[uid]  # ТЕК ОСЫ ЖЕРДЕ ҒАНА ТІРКЕУДЕН ӨШІРЕМІЗ

            bot.send_message(uid,
                             f"Сәтті тіркелдің, қуаныштымын!\n👤 Аты-жөніңіз: {name}\n🏙 Қала: {city}\n📚 Курс: {course}",
                             reply_markup=keyboards.default_reply())
            bot.send_message(uid, "Ал іске көшейік, бұл менің қызметтерім:", reply_markup=keyboards.main_menu())
        return
    # --- ТІРКЕЛУ ПРОЦЕСІ АЯҚТАЛДЫ ---


#КЛАВИШ АСТЫНДАҒЫ КНОПКАЛАР БАСЫЛҒАНДА
    if text == "🏠 Басты мәзір":
        bot.send_message(uid, "Басты мәзір                                 .", reply_markup=keyboards.main_menu())

    elif text == "🏁 Тестті аяқтау":
        current_uid = uid if uid in user_states else int(uid)
        if current_uid in user_states:
            quiz_engine.finish_quiz(current_uid)
            # Тест аяқталғанда қайтадан "Басты мәзір" клавиатурасы қайтарылады
            bot.send_message(uid, "Төмендегі батырмалар арқылы мәзірге орала аласыз 👇",
                             reply_markup=keyboards.default_reply())
        else:
            bot.send_message(uid, "Белсенді тест табылмады.", reply_markup=keyboards.default_reply())
            bot.send_message(uid, "Басты мәзір                                 .", reply_markup=keyboards.main_menu())




@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = str(call.message.chat.id)
    cid = call.message.chat.id
    mid = call.message.message_id
    data = call.data


    if data == "main_menu":
        bot.edit_message_text("Басты мәзір                                 .", cid, mid, reply_markup=keyboards.main_menu())

    elif data == "prep_menu":
        bot.edit_message_text("ҰБТ-ға дайындық бөлімі:", cid, mid, reply_markup=keyboards.prep_menu())
    elif data == "materials_menu":
        bot.edit_message_text("Керекті материалды таңдаңыз:", cid, mid, reply_markup=keyboards.materials_menu())
    elif data == "author_base":
        bot.edit_message_text("Керекті базаны таңдаңыз:", cid, mid, reply_markup=keyboards.author_base_menu())
    elif data == "nuskalar":
        bot.edit_message_text("Керекті нұсқаны таңдаңыз:", cid, mid, reply_markup=keyboards.nusqalar_menu())
    elif data == "grades_menu":
        bot.edit_message_text("Керекті сыныпты таңдаңыз:", cid, mid, reply_markup=keyboards.grades_menu())
    elif data == "junior_menu":
        bot.edit_message_text("Өзіңіздің потогыңызды таңдаңыз:", cid, mid, reply_markup=keyboards.junior_menu())

    elif data == "month_шілде":
        bot.edit_message_text("Керекті айды таңдаңыз:", cid, mid, reply_markup=keyboards.ailar_menu())
    elif data == "month_тамыз":
        bot.edit_message_text("Керекті айды таңдаңыз:", cid, mid, reply_markup=keyboards.ailar_menu())


    elif data == "month_1":
        bot.edit_message_text("Керекті аптаны таңдаңыз:", cid, mid, reply_markup=keyboards.aptalar_1_menu())
    elif data == "month_2":
        bot.edit_message_text("Керекті аптаны таңдаңыз:", cid, mid, reply_markup=keyboards.aptalar_2_menu())
    elif data == "month_3":
        bot.edit_message_text("Керекті аптаны таңдаңыз:", cid, mid, reply_markup=keyboards.aptalar_3_menu())
    elif data == "month_4":
        bot.edit_message_text("Керекті аптаны таңдаңыз:", cid, mid, reply_markup=keyboards.aptalar_4_menu())
    elif data == "month_5":
        bot.edit_message_text("Керекті аптаны таңдаңыз:", cid, mid, reply_markup=keyboards.aptalar_5_menu())


    elif data == "personal_stats":
        bot.answer_callback_query(call.id)  # Батырманың жүктелуін (часики) тоқтату

        db = database.load_db()
        if uid not in db:
            bot.answer_callback_query(call.id, "Ақпарат табылмады.", show_alert=True)
            return

        user_data = db[uid]
        reg_date = user_data.get("reg_date", "Белгісіз (ескі база)")
        total = user_data.get("total", 0)
        correct = user_data.get("correct", 0)
        incorrect = total - correct

        rank = database.get_user_rank(uid)
        hardest_chapter = database.get_hardest_chapter(uid)

        text_msg = (
            f"📈 <b>{user_data.get('name')}</b>, сенің жеке статистикаң:\n\n"
            f"📅 Тіркелген күні: <b>{reg_date}</b>\n\n"
            f"📝 Барлық сұрақ саны: <b>{total}</b>\n"
            f"✅ Дұрыс жауаптар: <b>{correct}</b>\n"
            f"❌ Қате жауаптар: <b>{incorrect}</b>\n\n"
            f"🏆 Рейтингтегі орны: <b>{rank}-орын</b>\n"
            f"🧠 Ең қиналатын тарауың: <b>{hardest_chapter}</b>"
        )

        # Хабарламаны жаңа мәтінмен өзгертеміз және астына Басты мәзірді қайта қосамыз
        bot.send_message(uid, text_msg, parse_mode="HTML")



    elif data == "pay_course":

        bot.answer_callback_query(call.id)

        db = database.load_db()

        user_info = db.get(uid, {})

        # Оқушы бұрын төлеген бе?

        if user_info.get('is_paid', False):

            bot.send_message(uid, "✅ Сіз курстасыз! Барлық материалдар қолжетімді. Оқуды жалғастырыңыз!")

        else:

            # Төлем нұсқаулығы

            bot.send_message(uid, "👑 <b>Боттың жазылымы</b>\n\n"
                                  "Боттың толық мүмкіндіктерін ашу үшін төлем жасаңыз.\n\n"
                                  "💳 <b>Карта:</b> <a href='#'>4400430370943760</a>\n"
                                  "💰 <b>Бағасы:</b> 990 теңге\n\n"
                                  "Төлем жасаған соң, чекті скриндап осы жерге жіберіңіз, мен растайтын боламын!",
                             parse_mode="HTML")

    #ТОП-10 ШЫҒАРУ
    elif data == "stats":
        bot.answer_callback_query(call.id)
        user_data = database.load_db().get(uid, {})
        top_list = database.get_top_10()

        leaderboard = "<b>🏆 ТОП-10 ҮЗДІК ОҚУШЫ</b>\n__________________________\n\n"
        for i, user in enumerate(top_list, 1):
            correct_answers = user.get('correct', 0)
            total_answers = user.get('total', 0)
            incorrect_answers = total_answers - correct_answers
            user_id = user.get('user_id', '')

            # Егер username болса, жақша ішінде @username шығады, болмаса жақша мүлдем болмайды
            username = user.get('username')
            mention_part = f" (@{username})" if username else ""

            # Аты-жөнін басу арқылы профильге өту
            leaderboard += f"{i}. <a href='tg://user?id={user_id}'>{user.get('name')}</a>, {user.get('city', 'Белгісіз')}{mention_part}\n"
            leaderboard += f"Дұрыс: {correct_answers}  |  Қате: {incorrect_answers}\n\n"

        #Жеке статистика
        personal_correct = user_data.get('correct', 0)
        personal_total = user_data.get('total', 0)
        personal_incorrect = personal_total - personal_correct

        personal = (
            f"📈 <b>СЕНІҢ КӨРСЕТКІШІҢ:</b>\n"
            f"✅ Дұрыс: <b>{personal_correct}</b>\n"
            f"❌ Қате: <b>{personal_incorrect}</b>\n"
            f"🎯 Жалпы: <b>{personal_total}</b>"
        )
        bot.send_message(uid, leaderboard + personal, parse_mode="HTML")


    # БАЗА ЖІБЕРУ
    elif data.startswith("base_"):
        grade = data.split("_")[1]  # "7", "8" немесе "9" аламыз
        file_path = None
        try:
            if grade == "7":
                file_path = "Био 7-кл Толық база.pdf"
            elif grade == "8":
                file_path = "Био 8-кл Толық база.pdf"
            elif grade == "9":
                file_path = "Био 9-кл Толық база.pdf"
            else:
                file_path = None

            if file_path:
                with open(file_path, 'rb') as doc:
                    bot.send_document(uid, doc)
            else:
                bot.send_message(uid, "Кешіріңіз, бұл файл әлі базаға қосылмаған.")
        except FileNotFoundError:
            bot.send_message(uid, f"❌ Қате: Компьютерде '{file_path}' деген файл табылмады. Файлдың атын тексеріңіз.")

    #НУРБА АҒАЙМЕН БАЙЛАНЫС
    elif data == "contact":
        bot.answer_callback_query(call.id)
        contact_text = (
            "<b>Менің әлеуметтік желілерім:</b> \n\n"  # Мұнда </b> деп түзеттік
            "📱 Instagram: <a href='https://instagram.com/nurbakyt_sarsenov'>@nurbakyt_sarsenov</a>\n"
            "📢 Telegram канал: <a href='https://t.me/nurbaagai'>Нурба ағайдың каналы</a>\n"
            "💬 WhatsApp: <a href='https://wa.me/77087473804'>Хабарлама жазу</a>"
        )

        bot.send_message(uid, contact_text, parse_mode="HTML")
        # ---------------------------------------

    # ТАРАУЛАР КНОПКАЛАРЫН ШЫҒАРУ
    elif data.startswith("grade_"):
        grade = data.split("_")[1]
        bot.edit_message_text(
            f"📖 {grade}-сынып тарауларын таңдаңыз:",
            cid, mid,
            reply_markup=keyboards.chapters_menu(grade)
        )

    #КАНАЛҒАН ЖАЗЫЛҒАН, ЖАЗЫЛМАҒАНЫН ТЕКСЕРУ
    elif data == "check_subscription":
        if is_subscribed(uid):
            bot.answer_callback_query(call.id, "Рақмет! Тексеру сәтті өтті ✅")
            bot.delete_message(uid, mid)

            db = database.load_db()
            if uid not in db:
                bot.send_message(uid, "Керемет! Енді танысып алайық. Аты-жөніңіз кім?")
                reg_states[uid] = {"step": "name"}
            else:
                bot.send_message(uid, "Негізгі мәзір ашылды:", reply_markup=keyboards.default_reply())
                bot.send_message(uid, "Таңдау жасаңыз:", reply_markup=keyboards.main_menu())
        else:
            bot.answer_callback_query(call.id, "❌ Сіз әлі жазылмағансыз!", show_alert=True)


    #СЫНЫП БОЙЫНША ТЕСТ БАСТАУ
    elif data.startswith("start_"):
        uid = str(call.message.chat.id)
        db = database.load_db()

        # Тексеру:
        if not db.get(uid, {}).get('is_paid', False):
            bot.answer_callback_query(call.id, "❌ Бұл курс ақылы! Жазылым алуыңыз қажет.", show_alert=True)
            return
        _, grade, chapter = data.split("_")
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=f"{grade}-сынып")
            q_list = df[df['Тарау'].astype(str) == str(chapter)].to_dict('records')

            if not q_list:
                bot.answer_callback_query(call.id, "Сұрақтар жақында қосылады.", show_alert=True)
                return
            random.shuffle(q_list)
            user_states[uid] = {
                'questions': q_list,
                'current': 0,
                'score': 0,
                'mistakes': [],
                'msg_ids': [],
                'chapter_name': chapter  # ЖАҢАДАН ҚОСЫЛДЫ (Тарау атын есте сақтау үшін)
            }

            # Тест басталғанда клавиатура "Тестті аяқтау" деп ауысады
            msg = bot.send_message(uid, f"🚀 {chapter} бойынша тест басталды!", reply_markup=keyboards.test_reply())
            user_states[uid]['msg_ids'].append(msg.message_id)
            quiz_engine.send_question(uid)
        except Exception as err:
            # 1. Өзіңізге (Консольге) қатенің нақты себебін жазасыз (жөндеу үшін)
            print(f"Excel қатесі: {err}")
            # 2. Пайдаланушыға тек түсінікті, сыпайы хабарлама жібересіз
            bot.send_message(uid,
                             "⚠️ Кешіріңіз, тест мәліметтерін оқу кезінде техникалық қате орын алды. Біраз уақыттан соң қайталап көріңіз.")


        #ДЖУНИОР ТЕСТІН БАСТАУ
    elif "_" in data and data.replace("_", "").isdigit():
        month, week = data.split("_")
        sheet_name = f"{month}-ай"  # Мысалы: '1-ай'
        chapter_identifier = f"{month}_{week}"  # Мысалы: '1_1'
        chapter = f"{month}-ай, {week}-апта"

        try:
            # Excel-ден сәйкес листті оқимыз
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)

            # "Тарау" бағаны арқылы сұрақтарды сүзіп аламыз
            q_list = df[df['Тарау'].astype(str) == chapter_identifier].to_dict('records')

            if not q_list:
                bot.answer_callback_query(call.id, "Бұл аптада сұрақтар әлі қосылмаған.", show_alert=True)
                return
            # Тесттің бастапқы күйін орнатамыз
            random.shuffle(q_list)
            user_states[uid] = {
                'questions': q_list,
                'current': 0,
                'score': 0,
                'mistakes': [],
                'msg_ids': [],
                'month_week': chapter  # ЖАҢАДАН ҚОСЫЛДЫ (Тарау атын есте сақтау үшін)
            }
            # Тестті бастау
            msg = bot.edit_message_text(f"🚀 {month}-ай, {week}-апта бойынша тест басталды!", cid, mid)
            user_states[uid]['msg_ids'].append(msg.message_id)
            quiz_engine.send_question(uid)  # Дайын engine-ді қолданамыз

        except Exception as err:
            # 1. Қатені консольге жазыңыз (жөндеу үшін сізге қажет)
            print(f"Excel қатесі: {err}")
            # 2. Пайдаланушыға тек түсінікті нұсқаулық беріңіз
            bot.send_message(uid, "❌ Кешіріңіз, мәліметтерді оқу кезінде қате шықты. "
                                  "Парақ аты (мысалы: '1-ай') дұрыс жазылғанын және файлдың пішімінде мәселе жоқ екенін тексеріп көріңіз.")


    #НҰСҚАЛАР ТЕСТІН БАСТАУ
    elif data.startswith("nusqa_"):
        # Нұсқаның санын аламыз: "nusqa_1" -> "1"
        _, nusqa_id = data.split("_")

        # Іздеу сөзін құрастырамыз: "1" -> "1-нұсқа"
        search_term = f"{nusqa_id}-нұсқа"

        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name="Нұсқа")
            # "Тарау" бағанындағы бос орындарды тазалау
            df['Тарау'] = df['Тарау'].astype(str).str.strip()

            # Дәл сол мәтінді іздеу
            q_list = df[df['Тарау'] == search_term].to_dict('records')

            if not q_list:
                bot.answer_callback_query(call.id, f"'{search_term}' нұсқасы әлі дайын емес.", show_alert=True)
                return
            random.shuffle(q_list)
            user_states[uid] = {

                'questions': q_list,
                'current': 0,
                'score': 0,
                'mistakes': [],
                'msg_ids': [],
                'search_term': search_term  # ЖАҢАДАН ҚОСЫЛДЫ (Тарау атын есте сақтау үшін)

            }
            msg = bot.send_message(uid, f"🚀 {search_term} басталды!", reply_markup=keyboards.test_reply())
            user_states[uid]['msg_ids'].append(msg.message_id)
            quiz_engine.send_question(uid)
        except Exception as err:
            print(f"Excel қатесі: {err}")
            bot.send_message(uid, "Бұл нұсқаны оқу мүмкін болмады.")


    #ҚАТЕМЕН ЖҰМЫС БАСТАУ
    elif data == "fix_mistakes":
        state = user_states.get(uid)
        if state and state.get('mistakes'):
            bot.answer_callback_query(call.id, "Қатемен жұмыс басталуда...")
            state['questions'] = state['mistakes'].copy()
            state['mistakes'] = []
            state['current'] = 0
            state['score'] = 0
            state['msg_ids'] = []

            # Мұнда да тест клавиатурасы беріледі
            msg = bot.send_message(uid, "🛠 **Қатемен жұмыс басталды!**\nТек қате жіберген сұрақтарыңыз беріледі.",
                             reply_markup=keyboards.test_reply(),
                             parse_mode="Markdown")
            user_states[uid]['msg_ids'].append(msg.message_id)
            quiz_engine.send_question(uid)
        else:
            bot.answer_callback_query(call.id, "Қателер табылмады немесе сессия ескірген.", show_alert=True)
            bot.send_message(uid, "Қатемен жұмыс істеу үшін алдымен тестті аяқтап, қате жіберуіңіз керек.")


@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    uid = str(message.chat.id)

    # 1-қадам: Оқушының төлегенін тексеру (егер бұрын төлеген болса, қабылдамау)
    db = database.load_db()
    if db.get(uid, {}).get('is_paid') == True:
        bot.reply_to(message, "✅ Сіз төлеміңізді растап үлгердіңіз. Бәрі дайын!")
        return

    # 2-қадам: Админге жіберу (жоғарыдағы кодтың жалғасы)
    photo_id = message.photo[-1].file_id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Растау", callback_data=f"confirm_{uid}"))
    markup.add(types.InlineKeyboardButton("❌ Қабылдамау", callback_data=f"reject_{uid}"))

    bot.send_photo(config.ADMIN_ID, photo_id,
                   caption=f"💸 Жаңа төлем! \nОқушы: {db.get(uid, {}).get('name', 'Белгісіз')}\nID: {uid}",
                   reply_markup=markup)

    bot.reply_to(message, "✅ Чек қабылданды! Админ тексеріп жатыр, біраз күте тұрыңыз.")




#ОПРОС ТЕСТІН ЖІБЕРУШІ КОМАНДАЛАР
@bot.poll_answer_handler()
def handle_poll_answer(answer):
    uid = str(answer.user.id)

    if uid not in user_states:
        return

    state = user_states[uid]
    current_index = state['current']
    questions = state['questions']

    q = questions[current_index]
    selected_option = state['current_options'][answer.option_ids[0]]

    if str(selected_option) == str(q['Дұрыс']):
        state['score'] += 1
    else:
        state['mistakes'].append(q)

    state['current'] += 1

    if state['current'] < len(questions):
        quiz_engine.send_question(uid)
    else:
        quiz_engine.finish_quiz(uid)
        # Мәтін қостық: "Тест аяқталды! ..."
        bot.send_message(uid, "Тест аяқталды! Аз-аздан үздіксіз!",
                         reply_markup=keyboards.default_reply())


# Мотивация жіберу функциясы
def send_daily_motivation(time_of_day):
    db = database.load_db()
    print(f"DEBUG: Мотивация функциясы іске қосылды: {time_of_day}")  # <--- Осыны қосыңыз
    print(f"DEBUG: Дерекқордағы оқушылар саны: {len(db)}")  # <--- Оқушы бар ма, жоқ па көресіз

    text = motivator.get_motivation(time_of_day)

    for uid in db.keys():
        try:
            bot.send_message(uid, f"✨ {text}")
            print(f"DEBUG: Хабарлама жіберілді: {uid}")  # <--- Сәтті жіберілгенін көресіз
        except Exception as e:
            print(f"DEBUG: Қате орын алды {uid}: {e}")  # <--- Егер қате болса, енді оны көресіз


if __name__ == "__main__":
    # 1. Жоспарлаушыны баптау
    scheduler = BackgroundScheduler()

    # Таңғы 08:00-де жіберу (сағатты қаласаңыз 6:27-ге өзгертіп көріңіз, бірақ 8:00 әлдеқайда дұрыс)
    scheduler.add_job(send_daily_motivation, 'cron', hour=9, minute=00, args=['Morning'])

    # Кешкі 20:00-де жіберу
    scheduler.add_job(send_daily_motivation, 'cron', hour=21, minute=0, args=['Evening'])

    # Жоспарлаушыны міндетті түрде іске қосамыз
    scheduler.start()
    print("✅ Мотивация жоспарлаушысы іске қосылды.")

    # 2. Ботты іске қосу
    report_generator.generate_excel_report()  # Отчет жасау
    print("🚀 Нурба ағайдың боты қосылды...")

    bot.remove_webhook()
    bot.polling(none_stop=True)