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

        const response =
            await fetch(
                "/api/admin-login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            username:
                                usernameInput.value.trim(),

                            password:
                                passwordInput.value
                        })
                }
            );


        const data =
            await response.json();


        if (
            response.ok &&
            data.success
        ) {

            sessionStorage.setItem(
                "yugai_admin",
                "authenticated"
            );


            window.location.href =
                "dashboard.html";

            return;
        }


        errorMessage.textContent =
            data.error ||
            "Invalid username or password.";

    }

    catch (error) {

        errorMessage.textContent =
            "Unable to connect to YugAI.";

    }

    finally {

        loginButton.disabled =
            false;

        loginButton.textContent =
            "Login to Dashboard";

    }

}
```

);
