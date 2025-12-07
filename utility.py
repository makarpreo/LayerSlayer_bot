user_sessions = {}


def get_user_data(user_id):
    """Получает или создает данные пользователя"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'chat_id': user_id
        }
    return user_sessions[user_id]


import json


def add_qa(question: str, answer: str, file: str = "qa.json") -> None:
    with open(file, "r+", encoding="utf-8") as f:
        data = json.load(f)

        data.append({
            "question": question,
            "answer": answer
        })

        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()

def load_qa_dict(file: str = "qa.json") -> dict[str, str]:
    with open(file, encoding="utf-8") as f:
        data = json.load(f)

    return {
        item["question"]: item["answer"]
        for item in data
    }

def delete_qa(question: str, file: str = "qa.json") -> None:
    with open(file, "r+", encoding="utf-8") as f:
        data = json.load(f)

        for i, item in enumerate(data):
            if item["question"] == question:
                del data[i]
                break

        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()

