const input = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const chatBox = document.getElementById("chatBox");
const welcome = document.getElementById("welcome");


function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


function addMessage(sender, message, type) {

    const messageElement =
        document.createElement("div");

    messageElement.className =
        `message ${type}`;

    messageElement.innerHTML = `
        <div class="message-name">
            ${escapeHtml(sender)}
        </div>

        <div class="message-content">
            ${escapeHtml(message)}
        </div>
    `;

    chatBox.appendChild(messageElement);

    chatBox.scrollTop =
        chatBox.scrollHeight;
}


function showThinking() {

    const thinking =
        document.createElement("div");

    thinking.id = "thinking";

    thinking.className =
        "message assistant";

    thinking.innerHTML = `
        <div class="message-name">
            YugAI
        </div>

        <div class="message-content">
            Thinking...
        </div>
    `;

    chatBox.appendChild(thinking);

    chatBox.scrollTop =
        chatBox.scrollHeight;
}


function removeThinking() {

    const thinking =
        document.getElementById("thinking");

    if (thinking) {
        thinking.remove();
    }
}


async function sendMessage() {

    const message =
        input.value.trim();

    if (!message) {
        return;
    }


    welcome.style.display = "none";


    addMessage(
        "You",
        message,
        "user"
    );


    input.value = "";

    input.disabled = true;
    sendButton.disabled = true;


    showThinking();


    try {

        const response = await fetch(
            "/api/chat",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    message: message
                })
            }
        );


        const data = await response.json();


        removeThinking();


        if (!response.ok) {

            addMessage(
                "YugAI",
                data.response ||
                "Sorry, something went wrong.",
                "assistant"
            );

        } else {

            addMessage(
                "YugAI",
                data.response ||
                "Sorry, I couldn't generate a response.",
                "assistant"
            );

        }


    } catch (error) {

        removeThinking();


        addMessage(
            "YugAI",
            "Unable to connect to the YugAI server. Please make sure the server is running.",
            "assistant"
        );

        console.error(error);

    }


    input.disabled = false;
    sendButton.disabled = false;

    input.focus();
}


function newChat() {

    chatBox.innerHTML = "";

    welcome.style.display = "block";

    input.value = "";

    input.focus();
}


input.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);