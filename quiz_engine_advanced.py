from config import bot


def letters_to_indices(letters_str):
    """
    Excel-дегі әріптерді (A, C) Телеграм түсінетін индекске (0, 2) айналдырады.
    """
    # Егер Excel-де кириллица (А, Б, В) қолдансаңыз, төмендегіні ауыстырыңыз:
    # mapping = {'А': 0, 'Б': 1, 'В': 2, 'Г': 3, 'Д': 4, 'Е': 5}
    mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5}

    indices = []
    # Бос орындарды алып тастап, әріптерді бөлеміз
    parts = [p.strip().upper() for p in letters_str.split(',')]

    for p in parts:
        if p in mapping:
            indices.append(mapping[p])
    return indices


def send_advanced_question(user_id, state):
    """
    Көп жауапты және бір жауапты сұрақтарды анықтап, сауалнама жібереді.
    """
    q = state['questions'][state['current']]

    # 1. Excel-дегі варианттарды жинау (A, B, C, D, E, F бағандары)
    # Ескерту: Excel бағандарыңызда 'A', 'B' деген атаулар бар деп есептедім.
    # Егер бағандарыңыз басқаша аталса (мысалы 1, 2, 3), соны жазыңыз.
    options = []
    for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
        if q.get(letter) and str(q[letter]).strip():
            options.append(str(q[letter]))

    # 2. Дұрыс жауапты (мысалы "A, C") индекске айналдыру
    correct_raw = str(q.get('Дұрыс', ''))
    correct_indices = letters_to_indices(correct_raw)

    # 3. Көп жауапты ма, жоқ па?
    is_multiple = len(correct_indices) > 1

    # 4. Telegram-ға жіберу
    if is_multiple:
        # Көп жауапты болса 'regular'
        poll = bot.send_poll(
            chat_id=user_id,
            question=q['Сұрақ'],
            options=options,
            type='regular',
            allows_multiple_answers=True,  # Осы параметр көп жауапты етеді
            is_anonymous=False
        )
    else:
        # Бір жауапты болса 'quiz'
        poll = bot.send_poll(
            chat_id=user_id,
            question=q['Сұрақ'],
            options=options,
            type='quiz',
            correct_option_id=correct_indices[0] if correct_indices else 0,
            is_anonymous=False
        )

    state['msg_ids'].append(poll.message_id)
    state['current_options'] = options  # Тексеру үшін сақтап қоямыз