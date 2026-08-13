import os
import json
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler


# =====================================
# RATE LIMIT SETTINGS
# =====================================

RATE_LIMIT = 10
RATE_WINDOW = 60

request_history = {}


# =====================================
# BASIC USAGE ANALYTICS
# Note: This is temporary/in-memory data.
# Vercel may reset it when functions restart.
# =====================================

analytics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "gemini_success": 0,
    "gemini_failed": 0,
    "gemini_429": 0,
    "groq_attempts": 0,
    "groq_success": 0,
    "groq_failed": 0,
    "rate_limited": 0,
    "unique_ips": set()
}


# =====================================
# YUGAI SYSTEM PROMPT
# =====================================

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
    # MAIN POST ENDPOINT
    # =====================================

    def do_POST(self):

        try:

            # ---------------------------------
            # Get client IP
            # ---------------------------------

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


            # ---------------------------------
            # Track request and unique visitor
            # ---------------------------------

            analytics["total_requests"] += 1

            analytics["unique_ips"].add(
                client_ip
            )


            # ---------------------------------
            # Rate limiting
            # ---------------------------------

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

                analytics["rate_limited"] += 1

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


            # ---------------------------------
            # Read request
            # ---------------------------------

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


            # ---------------------------------
            # Get API keys
            # ---------------------------------

            gemini_key = os.environ.get(
                "GEMINI_API_KEY"
            )

            groq_key = os.environ.get(
                "GROQ_API_KEY"
            )


            if not gemini_key and not groq_key:

                analytics["failed_requests"] += 1

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

                        analytics["gemini_success"] += 1

                        analytics[
                            "successful_requests"
                        ] += 1


                        self.send_json(
                            200,
                            {
                                "response": answer
                            }
                        )

                        return


                except Exception as gemini_error:

                    analytics["gemini_failed"] += 1

                    error_text = str(
                        gemini_error
                    )

                    if (
                        "429" in error_text
                        or "Too Many Requests"
                        in error_text
                    ):

                        analytics["gemini_429"] += 1


                    print(
                        "Gemini failed:",
                        error_text
                    )


            # =================================
            # GEMINI FAILED -> TRY GROQ
            # =================================

            if groq_key:

                analytics["groq_attempts"] += 1


                try:

                    answer = self.call_groq(
                        groq_key,
                        message
                    )


                    if answer:

                        analytics["groq_success"] += 1

                        analytics[
                            "successful_requests"
                        ] += 1


                        self.send_json(
                            200,
                            {
                                "response": answer
                            }
                        )

                        return


                except Exception as groq_error:

                    analytics["groq_failed"] += 1

                    print(
                        "Groq fallback failed:",
                        str(groq_error)
                    )


            # =================================
            # BOTH PROVIDERS FAILED
            # =================================

            analytics["failed_requests"] += 1


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

            analytics["failed_requests"] += 1


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
    # GET ANALYTICS
    # Temporary endpoint:
    # /api/chat
    # =====================================

    def do_GET(self):

        try:

            stats = {
                "total_requests":
                    analytics["total_requests"],

                "successful_requests":
                    analytics["successful_requests"],

                "failed_requests":
                    analytics["failed_requests"],

                "gemini_success":
                    analytics["gemini_success"],

                "gemini_failed":
                    analytics["gemini_failed"],

                "gemini_429":
                    analytics["gemini_429"],

                "groq_attempts":
                    analytics["groq_attempts"],

                "groq_success":
                    analytics["groq_success"],

                "groq_failed":
                    analytics["groq_failed"],

                "rate_limited":
                    analytics["rate_limited"],

                "unique_visitors":
                    len(
                        analytics["unique_ips"]
                    )
            }


            self.send_json(
                200,
                stats
            )


        except Exception as error:

            self.send_json(
                500,
                {
                    "error": str(error)
                }
            )


    # =====================================
    # GEMINI FUNCTION
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
    # GROQ FALLBACK
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


            print(
                f"Groq HTTP {error.code}: "
                f"{error_body}"
            )


            raise Exception(
                f"Groq HTTP {error.code}: "
                f"{error_body}"
            )


        choices = result.get(
            "choices",
            []
        )


        if not choices:

            raise Exception(
                "Groq returned no choices: "
                + json.dumps(result)
            )


        answer = (
            choices[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )


        if not answer:

            raise Exception(
                "Groq returned an empty response."
            )


        return answer


    # =====================================
    # SEND JSON RESPONSE
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