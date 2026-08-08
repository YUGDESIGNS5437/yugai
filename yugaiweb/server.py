from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"


@app.route("/api/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json()

        message = data.get("message", "").strip()

        if not message:
            return jsonify({
                "response": "Please enter a message."
            }), 400

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": message,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        answer = result.get(
            "response",
            "Sorry, I couldn't generate a response."
        ).strip()

        return jsonify({
            "response": answer
        })

    except requests.exceptions.ConnectionError:

        return jsonify({
            "response": "YugAI AI engine is unavailable. Please make sure Ollama is running."
        }), 503

    except requests.exceptions.Timeout:

        return jsonify({
            "response": "YugAI took too long to respond. Please try again."
        }), 504

    except Exception as error:

        return jsonify({
            "response": f"Server error: {error}"
        }), 500


if __name__ == "__main__":

    print("================================")
    print("        YugAI SERVER")
    print("================================")
    print("Website: http://127.0.0.1:5000")
    print("AI: Ollama")
    print("Model:", MODEL)
    print("================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )