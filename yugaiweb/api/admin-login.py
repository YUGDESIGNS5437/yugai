import os
import json
import secrets
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):

```
def do_POST(self):

    try:

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


        username = data.get(
            "username",
            ""
        )

        password = data.get(
            "password",
            ""
        )


        admin_username = os.environ.get(
            "ADMIN_USERNAME"
        )

        admin_password = os.environ.get(
            "ADMIN_PASSWORD"
        )


        if not admin_username or not admin_password:

            self.send_json(
                500,
                {
                    "success": False,
                    "error": "Admin credentials are not configured."
                }
            )

            return


        username_correct = secrets.compare_digest(
            username,
            admin_username
        )

        password_correct = secrets.compare_digest(
            password,
            admin_password
        )


        if username_correct and password_correct:

            self.send_json(
                200,
                {
                    "success": True
                }
            )

            return


        self.send_json(
            401,
            {
                "success": False,
                "error": "Invalid username or password."
            }
        )


    except Exception as error:

        self.send_json(
            500,
            {
                "success": False,
                "error": "Login failed."
            }
        )


def send_json(self, status, data):

    self.send_response(status)

    self.send_header(
        "Content-Type",
        "application/json"
    )

    self.send_header(
        "Cache-Control",
        "no-store"
    )

    self.end_headers()

    self.wfile.write(
        json.dumps(data).encode("utf-8")
    )
```
