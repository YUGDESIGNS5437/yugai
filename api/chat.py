from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error


OPENAI_API_URL = "https://api.openai.com/v1/responses"
MODEL = "gpt-5.6-luna"


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

            api_key = os.environ.get("OPENAI_API_KEY")

            if not api_key:
                self.send_json(
                    {"error": "OPENAI_API_KEY is not configured."},
                    500
                )
                return

            payload = {
                "model": MODEL,
                "instructions": (
                    "You are YugAI, a helpful and intelligent "
                    "AI assistant created by YugDesigns. "
                    "Give clear, useful and accurate answers."
                ),
                "input": message,
                "max_output_tokens": 2048
            }

            request = urllib.request.Request(
                OPENAI_API_URL,
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

            answer = result.get("output_text", "").strip()

            if not answer:
                self.send_json(
                    {"error": "OpenAI returned an empty response."},
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
                    "error": f"OpenAI returned HTTP {error.code}.",
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