import pandas as pd
import json
import os

INDEX_FILE = "last_index.json"


def get_motivation(time_of_day):
    # Қай қатарға келгенін тексеру
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r') as f:
            data = json.load(f)
            index = data.get("index", 0)
    else:
        index = 0

    df = pd.read_excel("motivation.xlsx")

    # Егер файл соңына жетсе, басына қайту
    if index >= len(df):
        index = 0

    # Мәтінді алу
    text = df.iloc[index][time_of_day]

    # Индексті жаңарту
    with open(INDEX_FILE, 'w') as f:
        json.dump({"index": index + 1}, f)

    return text