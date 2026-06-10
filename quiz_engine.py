import random
from telebot import types
from config import bot, user_states
import database
import keyboards


def send_question(user_id):
    state = user_states.get(user_id)
    if not state: return

    if state['current'] < len(state['questions']):
        q = state['questions'][state['current']]
        options = [str(q['А']), str(q['Б']), str(q['В']), str(q['Г'])]
        correct_answer = str(q['Дұрыс'])

        random.shuffle(options)
        state['current_options'] = options

        poll = bot.send_poll(
            chat_id=user_id,
            question=q['Сұрақ'],
            options=options,
            type='quiz',
            correct_option_id=options.index(correct_answer),
            is_anonymous=False
        )
        state['msg_ids'].append(poll.message_id)
    else:
        finish_quiz(user_id)


def finish_quiz(user_id):
    # Тізімнен пайдаланушыны тауып аламыз
    state = user_states.get(user_id)
    if not state:
        return

    score = state.get('score', 0)
    current_idx = state.get('current', 0)

    # Сұрақтар санын анықтаймыз (нешеуіне жауап берілді)
    total = current_idx if current_idx > 0 else 1
    percent = (score / total * 100)

    # Тарау аты мен қателер санын аламыз
    # Дұрыс нұсқа:
    chapter_name = state.get('chapter_name') or state.get('month_week') or state.get('search_term') or "Белгісіз"
    mistakes_count = len(state.get('mistakes', []))
    # 1. ЖІБЕРІЛГЕН ТЕСТТЕРДІ (POLLS) ТЕЗ АРАДА ӨШІРУ
    if 'msg_ids' in state:
        for m_id in state['msg_ids']:
            try:
                bot.delete_message(user_id, m_id)
            except:
                pass
        state['msg_ids'] = []  # Өшірген соң тізімді тазалаймыз

    # 2. НӘТИЖЕНІ ДАЙЫНДАУ
    msg = f"🏁 **ТЕСТ АЯҚТАЛДЫ!**\n\n👤 Нәтижеңіз: {score} / {current_idx}\n📊 Көрсеткіш: {percent:.1f}%"

    # 3. СТАТИСТИКАНЫ БАЗАҒА САҚТАУ (Осы жер дұрысталды)
    database.update_stats(
        user_id=user_id,
        correct=score,
        total=current_idx,
        chapter_name=chapter_name,
        mistakes_count=mistakes_count
    )

    # 4. БІРДЕН НӘТИЖЕНІ ЖІБЕРУ
    markup = types.InlineKeyboardMarkup()
    if state.get('mistakes'):
        markup.add(types.InlineKeyboardButton("❌ Қатемен жұмыс", callback_data="fix_mistakes"))

    bot.send_message(user_id, msg, parse_mode="Markdown")

    if state.get('mistakes'):
        bot.send_message(user_id, "Төмендегі батырмамен қателеріңізді қайта тапсыра аласыз:", reply_markup=markup)

    # Егер қатемен жұмыс істегісі келмесе, state-ті тек осы жерде өшіруге болады
    # Бірақ біз оны fix_mistakes үшін уақытша қалдырамыз