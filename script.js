const chatBox = document.getElementById("chatBox");
const welcome = document.getElementById("welcome");
const pageContent = document.getElementById("pageContent");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");

const STORAGE_KEY = "yugai_v21_messages";

let messages = JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];


/* =========================
   INITIAL LOAD
========================= */

document.addEventListener("DOMContentLoaded", () => {
    renderMessages();

    messageInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
});


/* =========================
   CHAT RENDERING
========================= */

function renderMessages() {
    chatBox.innerHTML = "";

    if (messages.length === 0) {
        welcome.style.display = "flex";
        chatBox.style.display = "none";
        return;
    }

    welcome.style.display = "none";
    chatBox.style.display = "flex";

    messages.forEach((message) => {
        addMessageToUI(message.role, message.content);
    });

    scrollToBottom();
}


function addMessageToUI(role, content) {
    const messageWrapper = document.createElement("div");

    messageWrapper.className =
        role === "user"
            ? "message user-message"
            : "message ai-message";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";

    avatar.textContent =
        role === "user"
            ? "Y"
            : "Y";

    const contentWrapper = document.createElement("div");
    contentWrapper.className = "message-content";

    const name = document.createElement("div");
    name.className = "message-name";

    name.textContent =
        role === "user"
            ? "You"
            : "YugAI";

    const text = document.createElement("div");
    text.className = "message-text";

    /*
        textContent is intentionally used here
        so AI responses cannot inject HTML/JavaScript.
    */
    text.textContent = content;

    contentWrapper.appendChild(name);
    contentWrapper.appendChild(text);

    messageWrapper.appendChild(avatar);
    messageWrapper.appendChild(contentWrapper);

    chatBox.appendChild(messageWrapper);
}


function scrollToBottom() {
    requestAnimationFrame(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}


/* =========================
   SEND MESSAGE
========================= */

async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    messageInput.value = "";

    pageContent.innerHTML = "";

    addMessageToUI("user", message);

    messages.push({
        role: "user",
        content: message
    });

    saveMessages();

    welcome.style.display = "none";
    chatBox.style.display = "flex";

    showThinking();

    sendButton.disabled = true;
    messageInput.disabled = true;

    try {
        const response = await getAIResponse(message);

        removeThinking();

        addMessageToUI("assistant", response);

        messages.push({
            role: "assistant",
            content: response
        });

        saveMessages();

    } catch (error) {
        removeThinking();

        const errorMessage =
            "Sorry, YugAI couldn't connect to the AI service. Please try again.";

        addMessageToUI("assistant", errorMessage);

        messages.push({
            role: "assistant",
            content: errorMessage
        });

        saveMessages();

        console.error("YugAI API error:", error);

    } finally {
        sendButton.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();

        scrollToBottom();
    }
}


/* =========================
   PUBLIC VERCEL AI API
========================= */

async function getAIResponse(message) {

    /*
        IMPORTANT:
        This uses the Vercel API route.

        DO NOT use:
        http://127.0.0.1:5000/api/chat

        The public website must use:
        /api/chat
    */

    const response = await fetch("/api/chat", {
        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            message: message
        })
    });


    let data;

    try {
        data = await response.json();
    } catch (error) {
        throw new Error(
            "The server returned an invalid response."
        );
    }


    if (!response.ok) {
        console.error("YugAI server response:", data);

        throw new Error(
            data.error ||
            "YugAI API request failed."
        );
    }


    if (!data.response) {
        throw new Error(
            "The AI service returned an empty response."
        );
    }


    return data.response.trim();
}


/* =========================
   THINKING INDICATOR
========================= */

function showThinking() {

    removeThinking();

    const thinking = document.createElement("div");

    thinking.id = "thinkingMessage";
    thinking.className = "message ai-message thinking-message";

    const avatar = document.createElement("div");

    avatar.className = "message-avatar";
    avatar.textContent = "Y";

    const content = document.createElement("div");

    content.className = "message-content";

    const name = document.createElement("div");

    name.className = "message-name";
    name.textContent = "YugAI";

    const text = document.createElement("div");

    text.className = "message-text";
    text.textContent = "Thinking...";

    content.appendChild(name);
    content.appendChild(text);

    thinking.appendChild(avatar);
    thinking.appendChild(content);

    chatBox.appendChild(thinking);

    scrollToBottom();
}


function removeThinking() {
    const thinking = document.getElementById("thinkingMessage");

    if (thinking) {
        thinking.remove();
    }
}


/* =========================
   PROMPT CARDS
========================= */

function usePrompt(prompt) {

    showChat();

    messageInput.value = prompt;

    messageInput.focus();
}


/* =========================
   NEW CHAT
========================= */

function newChat() {

    messages = [];

    localStorage.removeItem(STORAGE_KEY);

    chatBox.innerHTML = "";

    pageContent.innerHTML = "";

    chatBox.style.display = "none";

    welcome.style.display = "flex";

    messageInput.value = "";

    messageInput.focus();

    setActiveWorkspace("Chat");
}


/* =========================
   SAVE CHAT
========================= */

function saveMessages() {

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(messages)
    );
}


/* =========================
   CHAT PAGE
========================= */

function showChat() {

    setActiveWorkspace("Chat");

    pageContent.innerHTML = "";

    welcome.style.display =
        messages.length === 0 ? "flex" : "none";

    chatBox.style.display =
        messages.length === 0 ? "none" : "flex";

    messageInput.disabled = false;
    sendButton.disabled = false;

    messageInput.focus();

    scrollToBottom();
}


/* =========================
   HISTORY PAGE
========================= */

function showHistory() {

    setActiveWorkspace("History");

    welcome.style.display = "none";
    chatBox.style.display = "none";

    pageContent.innerHTML = `
        <div class="content-page">
            <div class="content-header">
                <span class="content-label">YugAI</span>
                <h2>Conversation History</h2>
                <p>Your conversations are stored locally in this browser.</p>
            </div>

            <div class="history-card">

                ${
                    messages.length === 0
                        ? `
                            <div class="empty-state">
                                <div class="empty-icon">○</div>
                                <h3>No conversations yet</h3>
                                <p>Start chatting with YugAI to create your first conversation.</p>
                            </div>
                          `
                        : `
                            <div class="history-summary">
                                <strong>${messages.length}</strong>
                                <span>messages in this conversation</span>
                            </div>

                            <div class="history-list">

                                ${messages
                                    .map(
                                        (message, index) => `
                                            <div class="history-item">
                                                <div class="history-number">
                                                    ${index + 1}
                                                </div>

                                                <div class="history-text">
                                                    <strong>
                                                        ${
                                                            message.role === "user"
                                                                ? "You"
                                                                : "YugAI"
                                                        }
                                                    </strong>

                                                    <span>
                                                        ${escapeHTML(
                                                            message.content
                                                        )}
                                                    </span>
                                                </div>
                                            </div>
                                        `
                                    )
                                    .join("")}

                            </div>
                          `
                }

            </div>
        </div>
    `;

    messageInput.disabled = true;
    sendButton.disabled = true;
}


/* =========================
   SETTINGS PAGE
========================= */

function showSettings() {

    setActiveWorkspace("Settings");

    welcome.style.display = "none";
    chatBox.style.display = "none";

    pageContent.innerHTML = `
        <div class="content-page">

            <div class="content-header">
                <span class="content-label">YugAI</span>
                <h2>Settings</h2>
                <p>Manage your YugAI experience.</p>
            </div>


            <div class="settings-grid">

                <div class="settings-card">

                    <div class="settings-card-title">
                        <span>AI Model</span>
                    </div>

                    <div class="settings-row">
                        <span>Model</span>
                        <strong>GPT-OSS 20B</strong>
                    </div>

                    <div class="settings-row">
                        <span>Provider</span>
                        <strong>Groq</strong>
                    </div>

                    <div class="settings-row">
                        <span>Status</span>
                        <strong class="online-text">
                            ● Online
                        </strong>
                    </div>

                </div>


                <div class="settings-card">

                    <div class="settings-card-title">
                        <span>Conversation</span>
                    </div>

                    <div class="settings-row">
                        <span>Local messages</span>
                        <strong>
                            ${messages.length}
                        </strong>
                    </div>

                    <button
                        class="danger-button"
                        onclick="clearConversation()"
                    >
                        Clear Conversation
                    </button>

                </div>


                <div class="settings-card">

                    <div class="settings-card-title">
                        <span>About YugAI</span>
                    </div>

                    <p class="settings-description">
                        YugAI is an intelligent AI assistant created
                        by YugDesigns.
                    </p>

                    <div class="settings-row">
                        <span>Version</span>
                        <strong>v2.1</strong>
                    </div>

                    <div class="settings-row">
                        <span>Creator</span>
                        <strong>YugPatel</strong>
                    </div>

                </div>

            </div>

        </div>
    `;

    messageInput.disabled = true;
    sendButton.disabled = true;
}


/* =========================
   CLEAR CONVERSATION
========================= */

function clearConversation() {

    const confirmed = confirm(
        "Are you sure you want to clear this conversation?"
    );

    if (!confirmed) {
        return;
    }

    messages = [];

    localStorage.removeItem(STORAGE_KEY);

    chatBox.innerHTML = "";

    pageContent.innerHTML = "";

    showChat();
}


/* =========================
   ACTIVE NAVIGATION
========================= */

function setActiveWorkspace(name) {

    const buttons =
        document.querySelectorAll(".workspace-item");

    buttons.forEach((button) => {

        const text =
            button.querySelector("span:last-child");

        if (!text) {
            return;
        }

        if (text.textContent.trim() === name) {
            button.classList.add("active");
        } else {
            button.classList.remove("active");
        }
    });
}


/* =========================
   HTML ESCAPING
========================= */

function escapeHTML(value) {

    const div = document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}


/* =========================
   GLOBAL FUNCTIONS
========================= */

window.sendMessage = sendMessage;
window.newChat = newChat;
window.showChat = showChat;
window.showHistory = showHistory;
window.showSettings = showSettings;
window.usePrompt = usePrompt;
window.clearConversation = clearConversation;