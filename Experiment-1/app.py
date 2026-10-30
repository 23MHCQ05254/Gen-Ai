import streamlit as st
from main import generate_response

st.set_page_config(
    page_title="Atelier — Local AI Studio",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #20231f;
        --muted: #777a72;
        --paper: #f7f7f2;
        --panel: #ffffff;
        --line: #e8e9e1;
        --accent: #c6f36b;
        --deep: #20251f;
    }

    html, body, [class*="css"] {
        font-family: 'Aptos', 'Segoe UI', sans-serif;
    }
    .stApp {
        background: var(--paper);
        color: var(--ink);
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    [data-testid="stToolbar"] {
        right: 1.5rem;
    }
    [data-testid="stSidebar"] {
        background: var(--deep);
        border-right: 1px solid #343a32;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 1.55rem 1.1rem 1.2rem;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #b7bdb2;
    }
    [data-testid="stSidebar"] .stButton button {
        color: #d7dcd3;
        background: transparent;
        border: 1px solid transparent;
        border-radius: 10px;
        text-align: left;
        transition: background .18s ease, border-color .18s ease;
    }
    [data-testid="stSidebar"] .stButton button p {
        color: inherit;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        color: white;
        background: #30362e;
        border-color: #3b4338;
    }
    [data-testid="stSidebar"] .stButton button[kind="primary"] {
        color: #20251f;
        background: var(--accent);
        border-color: var(--accent);
        font-weight: 700;
    }
    [data-testid="stSidebar"] .stButton button[kind="primary"] p {
        color: #20251f;
    }
    [data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
        color: #20251f;
        background: #d5fb8b;
        border-color: #d5fb8b;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: .55rem;
    }
    .brand {
        display: flex;
        align-items: center;
        gap: 11px;
        margin: 0 0 2.45rem 4px;
    }
    .brand-mark {
        display: grid;
        place-items: center;
        width: 35px;
        height: 35px;
        border-radius: 11px;
        color: #20251f;
        background: var(--accent);
        font-size: 21px;
        font-weight: 700;
    }
    .brand-name {
        color: #f1f3ed;
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
        font-size: 15px;
        font-weight: 800;
        letter-spacing: .12em;
    }
    .brand-caption, .eyebrow, .mono {
        font-family: 'Consolas', monospace;
        font-size: 10px;
        letter-spacing: .12em;
        text-transform: uppercase;
    }
    .brand-caption {
        margin-top: 2px;
        color: #8d9588;
        letter-spacing: .08em;
    }
    .side-label {
        margin: 0 0 9px 5px;
        color: #7f887b;
        font-family: 'Consolas', monospace;
        font-size: 10px;
        letter-spacing: .13em;
        text-transform: uppercase;
    }
    .side-section {
        margin-top: 1.75rem;
    }
    .runtime-card {
        margin-top: 2rem;
        padding: 14px;
        border: 1px solid #3a4137;
        border-radius: 12px;
        background: #292f27;
    }
    .runtime-heading {
        margin-bottom: 12px;
        color: #8f998b;
        font-family: 'Consolas', monospace;
        font-size: 9px;
        letter-spacing: .13em;
        text-transform: uppercase;
    }
    .runtime-model {
        color: #eff2e9;
        font-size: 13px;
        font-weight: 600;
    }
    .runtime-status {
        display: flex;
        align-items: center;
        gap: 7px;
        margin-top: 8px;
        color: #a7b09f;
        font-size: 11px;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--accent);
        box-shadow: 0 0 10px #c6f36b70;
    }
    .main .block-container {
        max-width: 1120px;
        padding: 3.2rem 4rem 4rem;
    }
    .topline {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2.4rem;
    }
    .eyebrow {
        color: #85887f;
    }
    .privacy-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 7px 11px;
        border: 1px solid #e4e6dc;
        border-radius: 99px;
        background: #fbfcf8;
        color: #5e6558;
        font-size: 11px;
    }
    .privacy-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #8ab83f;
    }
    .hero {
        margin-bottom: 2rem;
    }
    .hero h1 {
        margin: 0 0 10px;
        color: var(--ink);
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
        font-size: clamp(2.2rem, 4vw, 3.2rem);
        font-weight: 700;
        letter-spacing: -.055em;
        line-height: 1.08;
    }
    .hero p {
        margin: 0;
        color: var(--muted);
        font-size: 15px;
    }
    .st-key-prompt_panel, .st-key-response_panel, .welcome-panel {
        padding: 1.45rem 1.55rem;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: var(--panel);
        box-shadow: 0 8px 30px #28321d08;
    }
    .panel-heading {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.1rem;
    }
    .panel-title {
        color: #343831;
        font-size: 13px;
        font-weight: 700;
    }
    .panel-hint {
        color: #989b92;
        font-family: 'Consolas', monospace;
        font-size: 10px;
        letter-spacing: .04em;
    }
    .stTextArea textarea {
        min-height: 125px;
        padding: 14px 15px;
        border: 1px solid #e6e8df;
        border-radius: 10px;
        background: #fbfcf9;
        color: #282c25;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: none;
    }
    .stTextArea textarea:focus {
        border-color: #9ac94b;
        box-shadow: 0 0 0 3px #c6f36b30;
    }
    .stTextArea textarea::placeholder {
        color: #a4a79e;
    }
    .stButton button, .stFormSubmitButton button {
        min-height: 42px;
        border: 1px solid #e5e7df;
        border-radius: 9px;
        background: white;
        color: #4b5047;
        font-size: 13px;
        font-weight: 600;
        transition: all .18s ease;
    }
    .stButton button:hover, .stFormSubmitButton button:hover {
        border-color: #cbd0c2;
        color: #20251f;
        background: #f8faf4;
    }
    .stFormSubmitButton button[kind="primary"] {
        border-color: #20251f;
        background: #20251f;
        color: #f7f9f2;
    }
    .stFormSubmitButton button[kind="primary"] p {
        color: #f7f9f2;
    }
    .stFormSubmitButton button[kind="primary"]:hover {
        border-color: #3e4935;
        background: #3e4935;
        color: white;
    }
    .st-key-response_panel {
        margin-top: 1.35rem;
        padding: 1.45rem 1.55rem 1.65rem;
        border-color: #e4e8d9;
    }
    .st-key-response_panel [data-testid="stMarkdownContainer"] {
        color: #41463d;
        font-size: 14px;
        line-height: 1.8;
    }
    .st-key-response_panel [data-testid="stMarkdownContainer"] p:last-child {
        margin-bottom: 0;
    }
    .welcome-panel {
        display: flex;
        align-items: flex-start;
        gap: 15px;
        margin-top: 1.35rem;
        padding: 1.2rem 1.4rem;
        background: #f0f3e8;
        box-shadow: none;
    }
    .welcome-icon {
        display: grid;
        flex: 0 0 34px;
        place-items: center;
        width: 34px;
        height: 34px;
        border-radius: 10px;
        background: #dff3b9;
        color: #4b642a;
        font-size: 17px;
    }
    .welcome-title {
        margin: 1px 0 4px;
        color: #343a2f;
        font-size: 13px;
        font-weight: 700;
    }
    .welcome-copy {
        color: #777d6f;
        font-size: 12px;
        line-height: 1.6;
    }
    .stAlert {
        border-radius: 10px;
    }
    [data-testid="stSpinner"] {
        color: #596c38;
    }
    @media (max-width: 800px) {
        .main .block-container {
            padding: 2rem 1.15rem 3rem;
        }
        .topline {
            margin-bottom: 1.7rem;
        }
        .st-key-prompt_panel, .st-key-response_panel {
            padding: 1.1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "chats" not in st.session_state:
    st.session_state.chats = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None
if "output" not in st.session_state:
    st.session_state.output = ""
if "history_open" not in st.session_state:
    st.session_state.history_open = False
if "prompt_value" not in st.session_state:
    st.session_state.prompt_value = ""

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">✳</div>
            <div>
                <div class="brand-name">ATELIER</div>
                <div class="brand-caption">Local AI studio</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">Workspace</div>', unsafe_allow_html=True)
    if st.button("＋  New conversation", type="primary", use_container_width=True):
        st.session_state.current_chat = None
        st.session_state.output = ""
        st.session_state.prompt_value = ""
        st.rerun()

    st.markdown('<div class="side-section side-label">Your conversations</div>', unsafe_allow_html=True)
    if st.button(
        "◷  Conversation history",
        use_container_width=True,
    ):
        st.session_state.history_open = not st.session_state.history_open

    if st.session_state.history_open:
        if not st.session_state.chats:
            st.caption("Your conversations will appear here.")
        else:
            for i in range(len(st.session_state.chats) - 1, -1, -1):
                old_chat = st.session_state.chats[i]
                label = old_chat["prompt"].replace("\n", " ").strip()
                if len(label) > 27:
                    label = label[:27].rstrip() + "…"

                if st.button(
                    f"↳  {label or 'Untitled conversation'}",
                    key=f"history_{i}",
                    use_container_width=True,
                ):
                    st.session_state.current_chat = i
                    st.session_state.prompt_value = old_chat["prompt"]
                    st.session_state.output = old_chat["output"]
                    st.rerun()

    st.markdown(
        """
        <div class="runtime-card">
            <div class="runtime-heading">Runtime environment</div>
            <div class="runtime-model">Llama 3.2 · 1B</div>
            <div class="runtime-status"><span class="status-dot"></span>Runs locally with Ollama</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="topline">
        <div class="eyebrow">A thoughtful space to explore ideas</div>
        <div class="privacy-pill"><span class="privacy-dot"></span>Private · on-device</div>
    </div>
    <div class="hero">
        <h1>Make room for<br>good questions.</h1>
        <p>A focused workspace for thinking, creating, and finding your next idea.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True, key="prompt_panel"):
    st.markdown(
        """
        <div class="panel-heading">
            <span class="panel-title">Start with a prompt</span>
            <span class="panel-hint">LOCAL MODEL · LLAMA 3.2</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("prompt_form", clear_on_submit=False):
        prompt = st.text_area(
            "Prompt",
            value=st.session_state.prompt_value,
            height=125,
            placeholder="What would you like to explore today?",
            label_visibility="collapsed",
        )
        generate_col, clear_col, _ = st.columns([2.4, 1, 4])
        with generate_col:
            generate = st.form_submit_button(
                "✳  Generate",
                type="primary",
                use_container_width=True,
            )
        with clear_col:
            clear = st.form_submit_button("Clear", use_container_width=True)

if clear:
    st.session_state.output = ""
    st.session_state.prompt_value = ""
    st.session_state.current_chat = None
    st.rerun()

if generate:
    if not prompt.strip():
        st.warning("Add a prompt to get started.")
    else:
        try:
            with st.spinner("Thinking through your prompt…"):
                answer = generate_response(prompt.strip())

            if not answer or not answer.strip():
                st.error("The model returned an empty response.")
            else:
                answer = answer.strip()
                st.session_state.output = answer
                st.session_state.prompt_value = prompt

                if st.session_state.current_chat is None:
                    st.session_state.chats.append(
                        {"prompt": prompt, "output": answer}
                    )
                    st.session_state.current_chat = len(st.session_state.chats) - 1
                else:
                    st.session_state.chats[st.session_state.current_chat] = {
                        "prompt": prompt,
                        "output": answer,
                    }
        except Exception as error:
            st.error(f"Generation failed: {error}")

if st.session_state.output:
    with st.container(border=True, key="response_panel"):
        st.markdown(
            """
            <div class="panel-heading">
                <span class="panel-title">A response for you</span>
                <span class="panel-hint">GENERATED LOCALLY</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(st.session_state.output)
else:
    st.markdown(
        """
        <div class="welcome-panel">
            <div class="welcome-icon">↗</div>
            <div>
                <div class="welcome-title">Your next idea starts here</div>
                <div class="welcome-copy">
                    Ask a question, draft something new, or bring a tricky idea
                    into focus. Your conversation stays on this device.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
