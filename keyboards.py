from telebot import types
from config import CHAPTERS

def course_reply():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Иә, смарттамын")
    btn2 = types.KeyboardButton("Иә, джуниордамын")
    btn3 = types.KeyboardButton("Басқа курс")
    btn4 = types.KeyboardButton("Жоқ")
    btn5 = types.KeyboardButton("Оқушы емеспін")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

# --- АСТЫҢҒЫ МӘЗІР КЛАВИАТУРАЛАРЫ ---
def default_reply():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🏠 Басты мәзір")
    return markup

def test_reply():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🏁 Тестті аяқтау")
    return markup

# ------------------------------------

def back_button(callback_data):
    return types.InlineKeyboardButton("⬅️ Артқа қайту", callback_data=callback_data)


def main_menu():
    markup = types.InlineKeyboardMarkup()

    # 1-жол: Екі батырма қатар тұрады
    btn1 = types.InlineKeyboardButton("🎓 ҰБТ-ға дайындық", callback_data="prep_menu")
    markup.row(btn1)
    btn2 = types.InlineKeyboardButton("📂 Материалдар", callback_data="materials_menu")
    markup.row(btn2)
    btn3 = types.InlineKeyboardButton("🏆 ТОП-10 қолданушы", callback_data="stats")
    markup.row(btn3)
    btn_stats = types.InlineKeyboardButton("📊 Жеке статистика", callback_data="personal_stats")
    # Оны markup-қа қосамыз (басқа батырмалармен бірге)
    markup.add(btn_stats)
    btn4 = types.InlineKeyboardButton("👨‍🏫 Нурба ағаймен байланыс", callback_data="contact")
    markup.row(btn4)
    markup.add(types.InlineKeyboardButton("👑 Жазылымдар", callback_data="pay_course"))

    return markup

def prep_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📚 Сынып бойынша тесттер", callback_data="grades_menu"),
        types.InlineKeyboardButton("📝 Нұсқа тапсыру", callback_data="nuskalar"),
        types.InlineKeyboardButton("🏆 Джуниор", callback_data="junior_menu"),
        back_button("main_menu")
    )
    return markup

def materials_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📝 Авторлық база", callback_data="author_base"),
        types.InlineKeyboardButton("📜 Чек-листтер", callback_data="checklists"),
        types.InlineKeyboardButton("📖 Кітаптар", callback_data="books"),
        back_button("main_menu")
    )
    return markup

def grades_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("7-сынып", callback_data="grade_7"),
        types.InlineKeyboardButton("8-сынып", callback_data="grade_8"),
        types.InlineKeyboardButton("9-сынып", callback_data="grade_9"),
        types.InlineKeyboardButton("10-сынып", callback_data="grade_10"),
        types.InlineKeyboardButton("11-сынып", callback_data="grade_11"),
        back_button("prep_menu")
    )
    return markup

def nusqalar_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("1-нұсқа", callback_data="nusqa_1"),
        types.InlineKeyboardButton("2-нұсқа", callback_data="nusqa_2"),
        types.InlineKeyboardButton("3-нұсқа", callback_data="nusqa_3"),
        types.InlineKeyboardButton("4-нұсқа", callback_data="nusqa_4"),
        types.InlineKeyboardButton("5-нұсқа", callback_data="nusqa_5"),
        types.InlineKeyboardButton("6-нұсқа", callback_data="nusqa_6"),
        back_button("prep_menu")
    )
    return markup

def junior_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("шілде", callback_data="month_шілде"),
        types.InlineKeyboardButton("тамыз", callback_data="month_тамыз"),
        types.InlineKeyboardButton("қыркүйек", callback_data="month_қыркүйек"),
        types.InlineKeyboardButton("қазан", callback_data="month_қазан"),
        back_button("prep_menu")
    )
    return markup

def ailar_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("1-ай", callback_data="month_1"),
        types.InlineKeyboardButton("2-ай", callback_data="month_2"),
        types.InlineKeyboardButton("3-ай", callback_data="month_3"),
        types.InlineKeyboardButton("4-ай", callback_data="month_4"),
        types.InlineKeyboardButton("5-ай", callback_data="month_5"),
        back_button("junior_menu")
    )
    return markup

def aptalar_1_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("1-ай 1-апта", callback_data="1_1"),
        types.InlineKeyboardButton("1-ай 2-апта", callback_data="1_2"),
        types.InlineKeyboardButton("1-ай 3-апта", callback_data="1_3"),
        types.InlineKeyboardButton("1-ай 4-апта", callback_data="1_4"),
        back_button("junior_menu")
    )
    return markup

def aptalar_2_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("2-ай 1-апта", callback_data="2_1"),
        types.InlineKeyboardButton("2-ай 2-апта", callback_data="2_2"),
        types.InlineKeyboardButton("2-ай 3-апта", callback_data="2_3"),
        types.InlineKeyboardButton("2-ай 4-апта", callback_data="2_4"),
        back_button("junior_menu")
    )
    return markup

def aptalar_3_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("3-ай 1-апта", callback_data="3_1"),
        types.InlineKeyboardButton("3-ай 2-апта", callback_data="3_2"),
        types.InlineKeyboardButton("3-ай 3-апта", callback_data="3_3"),
        types.InlineKeyboardButton("3-ай 4-апта", callback_data="3_4"),
        back_button("junior_menu")
    )
    return markup

def aptalar_4_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("4-ай 1-апта", callback_data="4_1"),
        types.InlineKeyboardButton("4-ай 2-апта", callback_data="4_2"),
        types.InlineKeyboardButton("4-ай 3-апта", callback_data="4_3"),
        types.InlineKeyboardButton("4-ай 4-апта", callback_data="4_4"),
        back_button("junior_menu")
    )
    return markup

def aptalar_5_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("5-ай 1-апта", callback_data="5_1"),
        types.InlineKeyboardButton("5-ай 2-апта", callback_data="5_2"),
        types.InlineKeyboardButton("5-ай 3-апта", callback_data="5_3"),
        types.InlineKeyboardButton("5-ай 4-апта", callback_data="5_4"),
        back_button("junior_menu")
    )
    return markup



def author_base_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("7-сынып базасы", callback_data="base_7"),
        types.InlineKeyboardButton("8-сынып базасы", callback_data="base_8"),
        types.InlineKeyboardButton("9-сынып базасы", callback_data="base_9"),
        back_button("materials_menu")
    )
    return markup

def chapters_menu(grade):
    markup = types.InlineKeyboardMarkup(row_width=1)
    chapter_list = CHAPTERS.get(str(grade), [])

    for chapter in chapter_list:
        markup.add(types.InlineKeyboardButton(chapter, callback_data=f"start_{grade}_{chapter}"))

    markup.add(back_button("grades_menu"))
    return markup