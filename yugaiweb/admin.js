const loginForm =
document.getElementById("loginForm");

const usernameInput =
document.getElementById("username");

const passwordInput =
document.getElementById("password");

const loginButton =
document.getElementById("loginButton");

const errorMessage =
document.getElementById("errorMessage");

loginForm.addEventListener(
"submit",
async function (event) {

```
    event.preventDefault();

    errorMessage.textContent = "";

    loginButton.disabled = true;

    loginButton.textContent =
        "Logging in...";

    try {

        const response = await fetch(
            "/api/admin_login",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    username:
                        usernameInput.value.trim(),

                    password:
                        passwordInput.value
                })
            }
        );


        const responseText =
            await response.text();

        console.log(
            "Login status:",
            response.status
        );

        console.log(
            "Login response:",
            responseText
        );


        let data = {};

        try {

            data =
                JSON.parse(responseText);

        }

        catch (jsonError) {

            throw new Error(
                "Server returned: " +
                responseText
            );

        }


        if (
            response.ok &&
            data.success === true
        ) {

            sessionStorage.setItem(
                "yugai_admin",
                "authenticated"
            );

            window.location.href =
                "/dashboard.html";

            return;

        }


        errorMessage.textContent =
            data.error ||
            "Login failed. Status: " +
            response.status;

    }

    catch (error) {

        console.error(
            "Login error:",
            error
        );

        errorMessage.textContent =
            "Login error: " +
            error.message;

    }

    finally {

        loginButton.disabled = false;

        loginButton.textContent =
            "Login to Dashboard";

    }

}
```

);
