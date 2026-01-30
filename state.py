import random

def get_questions(chat_data, category, pool, count):
    key = f"used_{category}"
    used = set(chat_data.get(key, []))

    available = [q for q in pool if q not in used]

    if len(available) < count:
        used.clear()
        available = pool.copy()

    selected = random.sample(available, min(count, len(available)))

    used.update(selected)
    chat_data[key] = list(used)

    return selected

