import os
import json
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler


# ---------------------------------------
# Basic rate limiting
# ---------------------------------------

RATE_LIMIT = 10
RATE_WINDOW = 60

request_history = {}


# ---------------------------------------
# YugAI system instructions
# ---------------------------------------

SYSTEM_PROMPT = (
    "You are YugAI, an intelligent and helpful general-purpose AI assistant. "

    "Understand exactly what the user is asking and respond according "
    "to the user's request. "

    "Follow the user's requested language, format, length, tone, "
    "and level of detail. "

    "If the user asks for a short answer, keep it short. "
    "If the user asks for details, explain thoroughly. "
    "If the user asks for a list, use a list. "
    "If the user asks for code, provide code. "
    "If the user asks for an email, write an email. "
    "If the user asks for a translation, translate it. "

    "If the user does not specify a format, choose the clearest "
    "and most natural format. "

    "Do not add artificial labels such as 'Sentence 1', "
    "'Sentence 2', 'Answer:', or 'Response:' unless the user "
    "specifically requests them. "

    "Give complete, accurate, and useful answers. "
    "Do not intentionally stop in the middle of a sentence. "

    "Be conversational, helpful, and clear."
)


class handler(BaseHTTPRequestHandler):

    # =====================================
    # Main POST endpoint
    # =====================================

    def do_POST(self):

        try:

            # --------------------------------
            # Get client IP
            # --------------------------------

            forwarded_for = self.headers.get(
                "x-forwarded-for",
                ""
            )

            client_ip = (
                forwarded_for
                .split(",")[0]
                .strip()
            )

            if not client_ip:
                client_ip = self.client_address[0]


            # --------------------------------
            # Basic rate limit
            # --------------------------------

            now = time.time()

            previous_requests = request_history.get(
                client_ip,
                []
            )

            previous_requests = [
                request_time
                for request_time in previous_requests
                if now - request_time < RATE_WINDOW
            ]

            if len(previous_requests) >= RATE_LIMIT:

                self.send_json(
                    429,
                    {
                        "response": (
                            "You're sending requests too quickly. "
                            "Please try again in a moment."
                        )
                    }
                )

                return


            previous_requests.append(now)

            request_history[client_ip] = (
                previous_requests
            )


            # --------------------------------
            # Read request
            # --------------------------------

            length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(length)

            data = json.loads(
                body.decode("utf-8")
            )

            message = data.get(
                "message",
                ""
            ).strip()


            if not message:

                self.send_json(
                    400,
                    {
                        "response":
                            "Please enter a message."
                    }
                )

                return


            # --------------------------------
            # API keys
            # --------------------------------

            gemini_key = os.environ.get(
                "GEMINI_API_KEY"
            )

            groq_key = os.environ.get(
                "GROQ_API_KEY"
            )


            if not gemini_key and not groq_key:

                self.send_json(
                    500,
                    {
                        "response":
                            "No AI API key is configured."
                    }
                )

                return


            # =================================
            # TRY GEMINI FIRST
            # =================================

            if gemini_key:

                try:

                    answer = self.call_gemini(
                        gemini_key,
                        message
                    )

                    if answer:

                        self.send_json(
                            200,
                            {
                                "response": answer
                            }
                        )

                        return

                except Exception as gemini_error:

                    print(
                        "Gemini failed:",
                        str(gemini_error)
                    )


            # =================================
            # GEMINI FAILED → TRY GROQ
            # =================================

            if groq_key:

                try:

                    answer = self.call_groq(
                        groq_key,
                        message
                    )

                    if answer:

                        self.send_json(
                            200,
                            {
                                "response": answer
                            }
                        )

                        return

                except Exception as groq_error:

                    print(
                        "Groq fallback failed:",
                        str(groq_error)
                    )


            # =================================
            # BOTH FAILED
            # =================================

            self.send_json(
                503,
                {
                    "response": (
                        "YugAI is temporarily unable "
                        "to generate a response. "
                        "Please try again shortly."
                    )
                }
            )


        except Exception as error:

            self.send_json(
                500,
                {
                    "response": (
                        "YugAI could not generate "
                        "a response."
                    ),
                    "error": str(error)
                }
            )


    # =====================================
    # Gemini
    # =====================================

    def call_gemini(
        self,
        api_key,
        message
    ):

        api_url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/gemini-flash-latest:"
            "generateContent"
        )


        payload = {

            "system_instruction": {

                "parts": [

                    {
                        "text": SYSTEM_PROMPT
                    }

                ]

            },

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

                "maxOutputTokens": 1000,

                "temperature": 0.7

            }

        }


        request = urllib.request.Request(

            api_url,

            data=json.dumps(
                payload
            ).encode("utf-8"),

            headers={

                "x-goog-api-key":
                    api_key,

                "Content-Type":
                    "application/json"

            },

            method="POST"

        )


        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            result = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )


        candidates = result.get(
            "candidates",
            []
        )


        if not candidates:

            raise Exception(
                "Gemini returned no candidates."
            )


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

            raise Exception(
                "Gemini returned an empty response."
            )


        return answer


    # =====================================
    # Groq fallback
    # =====================================

    def call_groq(
        self,
        api_key,
        message
    ):

        api_url = (
            "https://api.groq.com/"
            "openai/v1/chat/completions"
        )


        payload = {

            "model":
                "llama-3.3-70b-versatile",

            "messages": [

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": message
                }

            ],

            "max_tokens": 1000,

            "temperature": 0.7,

            "stream": False

        }


        request = urllib.request.Request(

            api_url,

            data=json.dumps(
                payload
            ).encode("utf-8"),

            headers={

                "Authorization":
                    f"Bearer {api_key}",

                "Content-Type":
                    "application/json"

            },

            method="POST"

        )


        # ---------------------------------
        # Groq request
        # ---------------------------------

        try:

            with urllib.request.urlopen(
                request,
                timeout=60
            ) as response:

                result = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )


        except urllib.error.HTTPError as error:

            try:

                error_body = (
                    error.read()
                    .decode("utf-8")
                )

            except Exception:

                error_body = (
                    "Unknown Groq error."
                )


            # IMPORTANT:
            # This prints the REAL Groq error
            # into Vercel logs.

            print(
                f"Groq HTTP {error.code}: "
                f"{error_body}"
            )


            raise Exception(
                f"Groq HTTP {error.code}: "
                f"{error_body}"
            )


        # ---------------------------------
        # Extract response
        # ---------------------------------

        choices = result.get(
            "choices",
            []
        )


        if not choices:

            raise Exception(
                "Groq returned no choices: "
                + json.dumps(result)
            )


        message_data = (
            choices[0]
            .get("message", {})
        )


        answer = (
            message_data
            .get("content", "")
            .strip()
        )


        if not answer:

            raise Exception(
                "Groq returned an empty response."
            )


        return answer


    # =====================================
    # JSON response
    # =====================================

    def send_json(
        self,
        status,
        data
    ):

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()


        self.wfile.write(
            json.dumps(
                data
            ).encode("utf-8")
        )