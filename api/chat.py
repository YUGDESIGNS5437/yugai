from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-20b"


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            data = json.loads(body)

            message = str(
                data.get("message", "")
            ).strip()

            if not message:
                self.send_json(
                    {"error": "Message is required."},
                    400
                )
                return

            api_key = os.environ.get("GROQ_API_KEY")

            if not api_key:
                self.send_json(
                    {"error": "GROQ_API_KEY is not configured on Vercel."},
                    500
                )
                return

            payload = {
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are YugAI, a helpful and intelligent "
                            "AI assistant created by YugDesigns. "
                            "Give clear, useful and accurate answers."
                        )
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "temperature": 0.7,
                "max_completion_tokens": 2048,
                "stream": False
            }

            request = urllib.request.Request(
                GROQ_API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
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
                result
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )

            if not answer:
                self.send_json(
                    {"error": "Groq returned an empty response."},
                    502
                )
                return

            self.send_json(
                {"response": answer},
                200
            )

        except urllib.error.HTTPError as error:

            try:
                error_body = error.read().decode("utf-8")
            except Exception:
                error_body = ""

            self.send_json(
                {
                    "error": f"Groq returned HTTP {error.code}.",
                    "details": error_body
                },
                502
            )

        except Exception as error:

            self.send_json(
                {
                    "error": "YugAI API error.",
                    "details": str(error)
                },
                500
            )


    def do_OPTIONS(self):

        self.send_response(204)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()


    def send_json(self, data, status_code):

        response = json.dumps(data).encode("utf-8")

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.end_headers()

        self.wfile.write(response)