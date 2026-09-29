from flask import Flask, request, jsonify
from flask_cors import CORS

import sys
import os

# Allow Python to find ai.py in the parent D:\YugAI folder
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from ai import get_response


app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return "YugAI API is running!"


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No JSON data received."
            }), 400

        message = data.get("message", "").strip()

        if not message:
            return jsonify({
                "error": "Message is required."
            }), 400

        response = get_response(message)

        return jsonify({
            "response": response
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


if __name__ == "__main__":
    print("================================")
    print("        YugAI API Server")
    print("================================")
    print("API: http://127.0.0.1:5000")
    print("Chat: http://127.0.0.1:5000/api/chat")
    print("================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )