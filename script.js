// ==========================================
// YugAI V2.1 — Web Frontend
// Real Ollama API Connection
// ==========================================


// ---------- DOM ELEMENTS ----------

const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const chatBox = document.getElementById("chatBox");
const welcome = document.getElementById("welcome");
const pageContent = document.getElementById("pageContent");


// ---------- STORAGE ----------

const STORAGE_KEY = "yugai_v21_messages";

let messages = loadMessages();
let isGenerating = false;


// ---------- LOAD SAVED MESSAGES ----------

function loadMessages() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);

        if (!saved) {
            return [];
        }

        return JSON.parse(saved);
    } catch (error) {
        console.error("Could not load messages:", error);
        return [];
    }
}


// ---------- SAVE MESSAGES ----------

function saveMessages() {
    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(messages)
    );
}


// ---------- INITIALIZE ----------

document.addEventListener("DOMContentLoaded", () => {

    renderMessages();

    if (messageInput) {
        messageInput.focus();

        messageInput.addEventListener("keydown", (event) => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();

                if (!isGenerating) {
                    sendMessage();
                }
            }
        });
    }
});


// ---------- RENDER MESSAGES ----------

function renderMessages() {

    if (!chatBox) {
        return;
    }

    chatBox.innerHTML = "";

    if (messages.length === 0) {

        if (welcome) {
            welcome.style.display = "flex";
        }

        return;
    }

    if (welcome) {
        welcome.style.display = "none";
    }

    messages.forEach((message) => {

        if (message.role === "user") {
            addUserMessage(message.content, false);
        }

        if (message.role === "assistant") {
            addAIMessage(message.content, false);
        }
    });

    scrollToBottom();
}


// ---------- SEND MESSAGE ----------

async function sendMessage() {

    if (isGenerating) {
        return;
    }

    if (!messageInput) {
        return;
    }

    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    messageInput.value = "";

    hideWelcome();

    // Add user message
    messages.push({
        role: "user",
        content: message
    });

    saveMessages();

    addUserMessage(message, true);

    await generateAIResponse(message);
}


// ---------- REAL AI RESPONSE ----------

async function generateAIResponse(userMessage) {

    isGenerating = true;

    setSendButtonState(true);

    const thinkingElement = addThinkingMessage();

    try {

        const response = await getAIResponse(userMessage);

        removeThinkingMessage(thinkingElement);

        messages.push({
            role: "assistant",
            content: response
        });

        saveMessages();

        addAIMessage(response, true);

    } catch (error) {

        console.error("YugAI API Error:", error);

        removeThinkingMessage(thinkingElement);

        const errorMessage =
            "Sorry, YugAI couldn't connect to the AI service.\n\n" +
            "Please make sure Ollama and the YugAI API server are running.";

        messages.push({
            role: "assistant",
            content: errorMessage
        });

        saveMessages();

        addAIMessage(errorMessage, true);

    } finally {

        isGenerating = false;

        setSendButtonState(false);

        if (messageInput) {
            messageInput.focus();
        }
    }
}


// ==========================================
// REAL YUGAI API
// ==========================================

async function getAIResponse(message) {

    const response = await fetch(
        "http://127.0.0.1:5000/api/chat",
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


    if (!response.ok) {

        throw new Error(
            "YugAI API request failed."
        );
    }


    const data = await response.json();


    if (data.error) {

        throw new Error(
            data.error
        );
    }


    return data.response || "Sorry, I didn't receive a response.";
}


// ---------- ADD USER MESSAGE ----------

function addUserMessage(text, save = true) {

    if (!chatBox) {
        return;
    }

    const messageElement =
        document.createElement("div");

    messageElement.className =
        "message user-message";


    const content =
        document.createElement("div");

    content.className =
        "message-content";


    content.textContent = text;


    messageElement.appendChild(content);

    chatBox.appendChild(messageElement);

    scrollToBottom();
}


// ---------- ADD AI MESSAGE ----------

function addAIMessage(text, save = true) {

    if (!chatBox) {
        return;
    }

    const messageElement =
        document.createElement("div");

    messageElement.className =
        "message ai-message";


    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.textContent = "Y";


    const content =
        document.createElement("div");

    content.className =
        "message-content";


    content.textContent = text;


    messageElement.appendChild(avatar);

    messageElement.appendChild(content);

    chatBox.appendChild(messageElement);

    scrollToBottom();
}


// ---------- THINKING MESSAGE ----------

function addThinkingMessage() {

    if (!chatBox) {
        return null;
    }

    const messageElement =
        document.createElement("div");

    messageElement.className =
        "message ai-message thinking-message";


    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.textContent = "Y";


    const content =
        document.createElement("div");

    content.className =
        "message-content";


    content.innerHTML =
        "<span class='thinking-dots'>" +
        "<span></span>" +
        "<span></span>" +
        "<span></span>" +
        "</span>";


    messageElement.appendChild(avatar);

    messageElement.appendChild(content);

    chatBox.appendChild(messageElement);

    scrollToBottom();

    return messageElement;
}


// ---------- REMOVE THINKING MESSAGE ----------

function removeThinkingMessage(element) {

    if (element && element.parentNode) {
        element.parentNode.removeChild(element);
    }
}


// ---------- HIDE WELCOME ----------

function hideWelcome() {

    if (welcome) {
        welcome.style.display = "none";
    }
}


// ---------- SEND BUTTON STATE ----------

function setSendButtonState(disabled) {

    if (!sendButton) {
        return;
    }

    sendButton.disabled = disabled;

    if (disabled) {
        sendButton.style.opacity = "0.5";
        sendButton.style.cursor = "not-allowed";
    } else {
        sendButton.style.opacity = "1";
        sendButton.style.cursor = "pointer";
    }
}


// ---------- SCROLL ----------

function scrollToBottom() {

    if (!chatBox) {
        return;
    }

    setTimeout(() => {

        chatBox.scrollTop =
            chatBox.scrollHeight;

    }, 50);
}


// ==========================================
// PROMPT CARDS
// ==========================================

function usePrompt(prompt) {

    if (!messageInput) {
        return;
    }

    messageInput.value = prompt;

    messageInput.focus();

    sendMessage();
}


// ==========================================
// NEW CHAT
// ==========================================

function newChat() {

    messages = [];

    localStorage.removeItem(STORAGE_KEY);

    if (chatBox) {
        chatBox.innerHTML = "";
    }

    if (pageContent) {
        pageContent.innerHTML = "";
    }

    if (welcome) {
        welcome.style.display = "flex";
    }

    showChat();

    if (messageInput) {
        messageInput.value = "";
        messageInput.focus();
    }
}


// ==========================================
// CHAT PAGE
// ==========================================

function showChat() {

    setActiveWorkspace("Chat");

    if (pageContent) {
        pageContent.innerHTML = "";
        pageContent.style.display = "none";
    }

    if (chatBox) {
        chatBox.style.display = "flex";
    }

    if (welcome && messages.length === 0) {
        welcome.style.display = "flex";
    }

    if (messageInput) {
        messageInput.focus();
    }
}


// ==========================================
// HISTORY PAGE
// ==========================================

function showHistory() {

    setActiveWorkspace("History");

    if (welcome) {
        welcome.style.display = "none";
    }

    if (chatBox) {
        chatBox.style.display = "none";
    }

    if (!pageContent) {
        return;
    }

    pageContent.style.display = "block";

    pageContent.innerHTML = `
        <div class="page-header">
            <h2>History</h2>
            <p>Your recent YugAI conversations.</p>
        </div>

        <div class="history-card">

            ${
                messages.length === 0

                ? `
                    <div class="empty-state">
                        <div class="empty-icon">○</div>
                        <h3>No conversations yet</h3>
                        <p>Start chatting with YugAI to see your history here.</p>
                    </div>
                `

                : `
                    <div class="history-list">

                        ${messages.map((message, index) => `

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
                                            message.content.substring(0, 100)
                                        )}
                                    </span>

                                </div>

                            </div>

                        `).join("")}

                    </div>
                `
            }

        </div>
    `;
}


// ==========================================
// SETTINGS PAGE
// ==========================================

function showSettings() {

    setActiveWorkspace("Settings");

    if (welcome) {
        welcome.style.display = "none";
    }

    if (chatBox) {
        chatBox.style.display = "none";
    }

    if (!pageContent) {
        return;
    }

    pageContent.style.display = "block";

    pageContent.innerHTML = `

        <div class="page-header">

            <h2>Settings</h2>

            <p>
                Manage your YugAI experience.
            </p>

        </div>


        <div class="settings-card">

            <div class="settings-row">

                <div>
                    <strong>AI Model</strong>

                    <span>
                        Llama 3.2 · 3B
                    </span>
                </div>

                <span class="settings-badge">
                    Local
                </span>

            </div>


            <div class="settings-row">

                <div>
                    <strong>AI Engine</strong>

                    <span>
                        Ollama
                    </span>
                </div>

                <span class="settings-badge">
                    Connected
                </span>

            </div>


            <div class="settings-row">

                <div>
                    <strong>Version</strong>

                    <span>
                        YugAI v2.1
                    </span>
                </div>

            </div>

        </div>


        <div class="settings-card">

            <div class="settings-section">

                <h3>About YugAI</h3>

                <p>
                    YugAI is an intelligent AI assistant
                    created by YugPatel.
                </p>

                <p>
                    Powered locally through Ollama
                    and the Llama 3.2 · 3B model.
                </p>

            </div>

        </div>


        <div class="settings-card danger-card">

            <div class="settings-section">

                <h3>Conversation Data</h3>

                <p>
                    Clear the conversations stored
                    in this browser.
                </p>

                <button
                    class="clear-button"
                    onclick="clearConversation()"
                >
                    Clear Conversation
                </button>

            </div>

        </div>

    `;
}


// ==========================================
// CLEAR CONVERSATION
// ==========================================

function clearConversation() {

    messages = [];

    localStorage.removeItem(STORAGE_KEY);

    showChat();

    if (chatBox) {
        chatBox.innerHTML = "";
    }

    if (welcome) {
        welcome.style.display = "flex";
    }
}


// ==========================================
// ACTIVE NAVIGATION
// ==========================================

function setActiveWorkspace(name) {

    const buttons =
        document.querySelectorAll(
            ".workspace-item"
        );

    buttons.forEach((button) => {

        const text =
            button.textContent.trim();

        button.classList.toggle(
            "active",
            text.includes(name)
        );

    });
}


// ==========================================
// HTML ESCAPE
// ==========================================

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


// ==========================================
// RESPONSIVE KEYBOARD BEHAVIOR
// ==========================================

window.addEventListener("resize", () => {

    if (chatBox) {
        scrollToBottom();
    }

});


// ==========================================
// GLOBAL FUNCTIONS
// ==========================================

window.sendMessage = sendMessage;
window.newChat = newChat;
window.showChat = showChat;
window.showHistory = showHistory;
window.showSettings = showSettings;
window.usePrompt = usePrompt;
window.clearConversation = clearConversation;