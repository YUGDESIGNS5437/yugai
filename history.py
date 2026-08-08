import json
import os


HISTORY_FOLDER = "history"


def get_history_file(username):
    os.makedirs(HISTORY_FOLDER, exist_ok=True)

    safe_username = "".join(
        character for character in username
        if character.isalnum() or character in "_-"
    )

    return os.path.join(
        HISTORY_FOLDER,
        f"{safe_username}.json"
    )


def load_history(username):
    """Load history belonging to one user."""

    history_file = get_history_file(username)

    if not os.path.exists(history_file):
        return []

    try:
        with open(
            history_file,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_chat(username, messages):
    """Save a conversation for a specific user."""

    if not messages:
        return

    history = load_history(username)

    history.append({
        "messages": messages
    })

    history_file = get_history_file(username)

    with open(
        history_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            history,
            file,
            indent=4,
            ensure_ascii=False
        )


def clear_history(username):
    """Delete history for one user."""

    history_file = get_history_file(username)

    if os.path.exists(history_file):
        os.remove(history_file)