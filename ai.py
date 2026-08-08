import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

# Current conversation memory
conversation = []


def get_response(message):
    """Send the conversation to Ollama and return the AI response."""

    try:
        conversation.append({
            "role": "user",
            "content": message
        })

        prompt = ""

        for item in conversation:
            if item["role"] == "user":
                prompt += f"User: {item['content']}\n"
            else:
                prompt += f"YugAI: {item['content']}\n"

        prompt += "YugAI:"

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get(
            "response",
            "Sorry, I couldn't generate a response."
        ).strip()

        conversation.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except requests.exceptions.ConnectionError:
        return (
            "YugAI cannot connect to Ollama. "
            "Please make sure Ollama is running."
        )

    except requests.exceptions.Timeout:
        return (
            "YugAI took too long to respond. "
            "Please try again."
        )

    except Exception as error:
        return f"Sorry, an error occurred:\n{error}"


def get_conversation():
    """Return a copy of the current conversation."""
    return conversation.copy()


def clear_conversation():
    """Clear current conversation memory."""
    conversation.clear()