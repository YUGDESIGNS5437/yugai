import os
import requests
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def do_POST(self):

        try:

            length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(length)

            import json

            data = json.loads(
                body.decode("utf-8")
            )

            message = data.get(
                "message",
                ""
            ).strip()

            if not message:

                self.send_response(400)

                self.send_header(
                    "Content-Type",
                    "application/json"
                )

                self.end_headers()

                self.wfile.write(
                    json.dumps({
                        "response":
                        "Please enter a message."
                    }).encode()
                )

                return


            token = os.environ.get(
                "HF_TOKEN"
            )


            if not token:

                raise Exception(
                    "HF_TOKEN is not configured."
                )


            API_URL = (
                "https://router.huggingface.co/"
                "v1/chat/completions"
            )


            headers = {

                "Authorization":
                f"Bearer {token}",

                "Content-Type":
                "application/json"

            }


            payload = {

                "model":
                "meta-llama/"
                "Llama-3.2-3B-Instruct",

                "messages": [

                    {
                        "role": "user",
                        "content": message
                    }

                ],

                "max_tokens": 500,

                "temperature": 0.7

            }


            response = requests.post(

                API_URL,

                headers=headers,

                json=payload,

                timeout=60

            )


            response.raise_for_status()


            result = response.json()


            answer = (
                result["choices"][0]
                ["message"]["content"]
                .strip()
            )


            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()


            self.wfile.write(
                json.dumps({
                    "response": answer
                }).encode()
            )


        except Exception as error:

            import json

            self.send_response(500)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps({
                    "response":
                    "YugAI could not generate a response.",
                    "error":
                    str(error)
                }).encode()
            )