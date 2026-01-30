import random

def get_questions(chat_data: dict, category: str, questions: list, count: int) -> list:
    """
    Rotating shuffle per chat, per category.
    No repeats until the list is exhausted.
    """

    if "shuffle_state" not in chat_data:
        chat_data["shuffle_state"] = {}

    state = chat_data["shuffle_state"]

    if category not in state or state[category]["index"] >= len(state[category]["queue"]):
        shuffled = questions.copy()
        random.shuffle(shuffled)
        state[category] = {
            "queue": shuffled,
            "index": 0
        }

    start = state[category]["index"]
    end = start + count

    selected = state[category]["queue"][start:end]
    state[category]["index"] = end

    return selected
