import json
import os
from config import USERS_FILE


def load_db():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_db(db):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)


# Бұл жерде тарауды және қатені қабылдау үшін параметрлерді қостық
def update_stats(user_id, correct, total, chapter_name=None, mistakes_count=0):
    db = load_db()
    uid = str(user_id)
    if uid in db:
        db[uid]["correct"] = db[uid].get("correct", 0) + correct
        db[uid]["total"] = db[uid].get("total", 0) + total

        # Егер тарау аты берілсе және қате болса, оны сақтаймыз
        if chapter_name and mistakes_count > 0:
            if "chapter_mistakes" not in db[uid]:
                db[uid]["chapter_mistakes"] = {}
            # Тараудағы қателер санын қосамыз
            db[uid]["chapter_mistakes"][chapter_name] = db[uid]["chapter_mistakes"].get(chapter_name,
                                                                                        0) + mistakes_count

        save_db(db)


def get_top_10():
    db = load_db()
    users_list = []
    for uid, user_data in db.items():
        user_data['user_id'] = uid
        users_list.append(user_data)
    sorted_users = sorted(users_list, key=lambda x: x.get('correct', 0), reverse=True)
    return sorted_users[:10]


# --- ЖАҢА ФУНКЦИЯЛАР ---

def get_user_rank(user_id):
    db = load_db()
    uid = str(user_id)
    if uid not in db:
        return "Белгісіз"

    # Оқушыларды дұрыс жауап саны бойынша сұрыптау
    sorted_users = sorted(db.items(), key=lambda x: x[1].get('correct', 0), reverse=True)
    for index, (u, data) in enumerate(sorted_users, start=1):
        if u == uid:
            return index
    return "Белгісіз"


def get_hardest_chapter(user_id):
    db = load_db()
    uid = str(user_id)
    if uid not in db or 'chapter_mistakes' not in db[uid]:
        return "Әлі анықталмаған"

    mistakes = db[uid].get('chapter_mistakes', {})
    if not mistakes:
        return "Әлі анықталмаған"

    # Ең көп қате жіберілген тарауды табу
    hardest = max(mistakes, key=mistakes.get)
    return hardest