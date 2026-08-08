import threading
import customtkinter as ctk

from ai import get_response


def create_app():

    # ==========================================
    # MAIN WINDOW
    # ==========================================

    app = ctk.CTk()

    app.title("YugAI")
    app.geometry("1250x780")
    app.minsize(1000, 650)

    # ==========================================
    # PREMIUM ELEGANT COLORS
    # ==========================================

    BG = "#0A0A0A"
    SIDEBAR = "#101010"

    PANEL = "#151515"
    PANEL_2 = "#1B1B1B"

    TEXT = "#F5F1E8"
    SECONDARY = "#9B978E"

    BORDER = "#2A2A2A"

    GOLD = "#C9A86A"
    GOLD_HOVER = "#B89355"

    GREEN = "#7FBF9A"

    app.configure(
        fg_color=BG
    )

    # ==========================================
    # SIDEBAR
    # ==========================================

    sidebar = ctk.CTkFrame(
        app,
        width=250,
        corner_radius=0,
        fg_color=SIDEBAR
    )

    sidebar.pack(
        side="left",
        fill="y"
    )

    sidebar.pack_propagate(False)

    # ==========================================
    # BRAND
    # ==========================================

    brand = ctk.CTkLabel(
        sidebar,
        text="YugAI",
        font=("Arial", 30, "bold"),
        text_color=TEXT
    )

    brand.pack(
        pady=(40, 3)
    )

    brand_subtitle = ctk.CTkLabel(
        sidebar,
        text="INTELLIGENT ASSISTANT",
        font=("Arial", 10, "bold"),
        text_color=SECONDARY
    )

    brand_subtitle.pack(
        pady=(0, 35)
    )

    # ==========================================
    # NEW CHAT
    # ==========================================

    def new_chat():

        chat_box.configure(
            state="normal"
        )

        chat_box.delete(
            "1.0",
            "end"
        )

        chat_box.configure(
            state="disabled"
        )

        welcome_frame.pack(
            pady=(45, 20)
        )

        message_entry.delete(
            0,
            "end"
        )

        message_entry.focus()

    new_chat_button = ctk.CTkButton(
        sidebar,
        text="+   New Chat",
        height=48,
        corner_radius=12,
        fg_color=GOLD,
        hover_color=GOLD_HOVER,
        text_color="#0A0A0A",
        font=("Arial", 14, "bold"),
        command=new_chat
    )

    new_chat_button.pack(
        fill="x",
        padx=20,
        pady=(0, 30)
    )

    # ==========================================
    # SIDEBAR INFORMATION
    # ==========================================

    info_title = ctk.CTkLabel(
        sidebar,
        text="YUGAI",
        font=("Arial", 10, "bold"),
        text_color=SECONDARY
    )

    info_title.pack(
        anchor="w",
        padx=25,
        pady=(10, 8)
    )

    info_text = ctk.CTkLabel(
        sidebar,
        text="Private local AI\n\nPowered by Ollama\nRunning on your device",
        font=("Arial", 12),
        text_color=SECONDARY,
        justify="left"
    )

    info_text.pack(
        anchor="w",
        padx=25
    )

    # ==========================================
    # SIDEBAR DIVIDER
    # ==========================================

    divider = ctk.CTkFrame(
        sidebar,
        height=1,
        fg_color=BORDER
    )

    divider.pack(
        side="bottom",
        fill="x",
        padx=25,
        pady=(0, 15)
    )

    # ==========================================
    # VERSION
    # ==========================================

    version = ctk.CTkLabel(
        sidebar,
        text="YugAI v1.0  •  Local",
        font=("Arial", 10),
        text_color=SECONDARY
    )

    version.pack(
        side="bottom",
        pady=(0, 25)
    )

    # ==========================================
    # MAIN CONTENT
    # ==========================================

    content = ctk.CTkFrame(
        app,
        fg_color=BG,
        corner_radius=0
    )

    content.pack(
        side="right",
        fill="both",
        expand=True
    )

    # ==========================================
    # TOP BAR
    # ==========================================

    topbar = ctk.CTkFrame(
        content,
        height=65,
        fg_color=BG,
        corner_radius=0
    )

    topbar.pack(
        fill="x"
    )

    topbar.pack_propagate(False)

    top_title = ctk.CTkLabel(
        topbar,
        text="YugAI",
        font=("Arial", 19, "bold"),
        text_color=TEXT
    )

    top_title.pack(
        side="left",
        padx=30
    )

    # ==========================================
    # AI STATUS
    # ==========================================

    status_frame = ctk.CTkFrame(
        topbar,
        fg_color="transparent"
    )

    status_frame.pack(
        side="right",
        padx=30
    )

    status_dot = ctk.CTkLabel(
        status_frame,
        text="●",
        font=("Arial", 13),
        text_color=GREEN
    )

    status_dot.pack(
        side="left",
        padx=(0, 5)
    )

    status_text = ctk.CTkLabel(
        status_frame,
        text="AI Online",
        font=("Arial", 12),
        text_color=SECONDARY
    )

    status_text.pack(
        side="left"
    )

    # ==========================================
    # CHAT CONTAINER
    # ==========================================

    chat_container = ctk.CTkFrame(
        content,
        fg_color=BG
    )

    chat_container.pack(
        fill="both",
        expand=True,
        padx=35
    )

    # ==========================================
    # WELCOME
    # ==========================================

    welcome_frame = ctk.CTkFrame(
        chat_container,
        fg_color=BG
    )

    welcome_frame.pack(
        pady=(45, 20)
    )

    welcome_title = ctk.CTkLabel(
        welcome_frame,
        text="How can I help you?",
        font=("Arial", 36, "bold"),
        text_color=TEXT
    )

    welcome_title.pack()

    welcome_subtitle = ctk.CTkLabel(
        welcome_frame,
        text="Ask anything. YugAI is ready.",
        font=("Arial", 15),
        text_color=SECONDARY
    )

    welcome_subtitle.pack(
        pady=(8, 0)
    )

    # ==========================================
    # CHAT BOX
    # ==========================================

    chat_box = ctk.CTkTextbox(
        chat_container,
        corner_radius=18,
        fg_color=PANEL,
        border_width=1,
        border_color=BORDER,
        text_color=TEXT,
        font=("Arial", 15),
        wrap="word"
    )

    chat_box.pack(
        fill="both",
        expand=True
    )

    chat_box.configure(
        state="disabled"
    )

    # ==========================================
    # INPUT OUTER
    # ==========================================

    input_outer = ctk.CTkFrame(
        content,
        fg_color=BG
    )

    input_outer.pack(
        fill="x",
        padx=35,
        pady=(18, 25)
    )

    # ==========================================
    # INPUT BOX
    # ==========================================

    input_box = ctk.CTkFrame(
        input_outer,
        height=64,
        corner_radius=18,
        fg_color=PANEL_2,
        border_width=1,
        border_color=BORDER
    )

    input_box.pack(
        fill="x"
    )

    input_box.pack_propagate(False)

    # ==========================================
    # MESSAGE ENTRY
    # ==========================================

    message_entry = ctk.CTkEntry(
        input_box,
        placeholder_text="Message YugAI...",
        height=50,
        corner_radius=14,
        fg_color="transparent",
        border_width=0,
        text_color=TEXT,
        placeholder_text_color=SECONDARY,
        font=("Arial", 15)
    )

    message_entry.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(18, 5),
        pady=7
    )

    # ==========================================
    # SEND BUTTON
    # ==========================================

    send_button = ctk.CTkButton(
        input_box,
        text="➤",
        width=48,
        height=48,
        corner_radius=14,
        fg_color=GOLD,
        hover_color=GOLD_HOVER,
        text_color="#0A0A0A",
        font=("Arial", 20, "bold")
    )

    send_button.pack(
        side="right",
        padx=8,
        pady=7
    )

    # ==========================================
    # USER MESSAGE
    # ==========================================

    def add_user_message(message):

        chat_box.configure(
            state="normal"
        )

        chat_box.insert(
            "end",
            f"\nYou\n{message}\n\n"
        )

        chat_box.configure(
            state="disabled"
        )

        chat_box.see(
            "end"
        )

    # ==========================================
    # SEND MESSAGE
    # ==========================================

    def send_message():

        message = message_entry.get().strip()

        if not message:
            return

        send_button.configure(
            state="disabled"
        )

        message_entry.configure(
            state="disabled"
        )

        welcome_frame.pack_forget()

        add_user_message(
            message
        )

        # Thinking message

        chat_box.configure(
            state="normal"
        )

        chat_box.insert(
            "end",
            "YugAI\nThinking...\n\n"
        )

        chat_box.configure(
            state="disabled"
        )

        chat_box.see(
            "end"
        )

        message_entry.delete(
            0,
            "end"
        )

        # ======================================
        # AI BACKGROUND THREAD
        # ======================================

        def generate():

            try:

                response = get_response(
                    message
                )

            except Exception as error:

                response = (
                    "Sorry, something went wrong.\n\n"
                    f"{error}"
                )

            app.after(
                0,
                lambda: finish_response(
                    response
                )
            )

        threading.Thread(
            target=generate,
            daemon=True
        ).start()

    # ==========================================
    # FINISH RESPONSE
    # ==========================================

    def finish_response(response):

        chat_box.configure(
            state="normal"
        )

        content_text = chat_box.get(
            "1.0",
            "end"
        )

        thinking_text = (
            "YugAI\n"
            "Thinking...\n\n"
        )

        if thinking_text in content_text:

            content_text = content_text.replace(
                thinking_text,
                "",
                1
            )

            chat_box.delete(
                "1.0",
                "end"
            )

            chat_box.insert(
                "end",
                content_text
            )

        chat_box.insert(
            "end",
            f"YugAI\n{response}\n\n"
        )

        chat_box.configure(
            state="disabled"
        )

        chat_box.see(
            "end"
        )

        send_button.configure(
            state="normal"
        )

        message_entry.configure(
            state="normal"
        )

        message_entry.focus()

    # ==========================================
    # SEND COMMAND
    # ==========================================

    send_button.configure(
        command=send_message
    )

    # ==========================================
    # ENTER KEY
    # ==========================================

    message_entry.bind(
        "<Return>",
        lambda event: send_message()
    )

    message_entry.focus()

    return app