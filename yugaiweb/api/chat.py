import os
import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            data = json.loads(body.decode("utf-8"))
            message = data.get("message", "").strip()

            if not message:
                self.send_json(
                    400,
                    {"response": "Please enter a message."}
                )
                return

            token = os.environ.get("HF_TOKEN")

            if not token:
                self.send_json(
                    500,
                    {"response": "HF_TOKEN is not configured."}
                )
                return

            api_url = (
                "https://router.huggingface.co/"
                "v1/chat/completions"
            )

            payload = {
                "model": "meta-llama/Llama-3.2-3B-Instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }

            request = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )

            with urllib.request.urlopen(
                request,
                timeout=60
            ) as response:

                result = json.loads(
                    response.read().decode("utf-8")
                )

            answer = (
                result["choices"][0]
                ["message"]["content"]
                .strip()
            )

            self.send_json(
                200,
                {"response": answer}
            )

        except urllib.error.HTTPError as error:
            try:
                error_body = error.read().decode("utf-8")
            except Exception:
                error_body = "Unknown Hugging Face error."

            self.send_json(
                500,
                {
                    "response": "Hugging Face API request failed.",
                    "error": error_body
                }
            )

        except Exception as error:
            self.send_json(
                500,
                {
                    "response": "YugAI could not generate a response.",
                    "error": str(error)
                }
            )

    def send_json(self, status, data):
        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json"
        )
        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )
        self.end_headers()

        self.wfile.write(
            json.dumps(data).encode("utf-8")
        )