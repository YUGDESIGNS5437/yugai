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

            api_key = os.environ.get("GEMINI_API_KEY")

            if not api_key:
                self.send_json(
                    500,
                    {"response": "GEMINI_API_KEY is not configured."}
                )
                return

            api_url = (
                "https://generativelanguage.googleapis.com/"
                "v1beta/models/gemini-2.5-flash:generateContent"
            )

            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": message
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500
                }
            }

            request = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "x-goog-api-key": api_key,
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

            candidates = result.get("candidates", [])

            if not candidates:
                self.send_json(
                    500,
                    {
                        "response": "Gemini returned no response.",
                        "error": json.dumps(result)
                    }
                )
                return

            parts = (
                candidates[0]
                .get("content", {})
                .get("parts", [])
            )

            answer = "".join(
                part.get("text", "")
                for part in parts
            ).strip()

            if not answer:
                self.send_json(
                    500,
                    {
                        "response": "Gemini returned an empty response."
                    }
                )
                return

            self.send_json(
                200,
                {"response": answer}
            )

        except urllib.error.HTTPError as error:
            try:
                error_body = error.read().decode("utf-8")
            except Exception:
                error_body = "Unknown Gemini API error."

            self.send_json(
                error.code,
                {
                    "response": "Gemini API request failed.",
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