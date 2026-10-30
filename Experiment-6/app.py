
import html
import pandas as pd
import streamlit as st

from main import evaluate_prompts, OllamaError

st.set_page_config(
    page_title="Prompt Lab | Experiment 6",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------- DESIGN --------------------

st.markdown("""
<style>
.stApp {
    background: #f5f6f8;
    color: #18212f;
}

.block-container {
    max-width: 1280px;
    padding-top: 2.25rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] {
    color: #18212f;
}

.hero {
    position: relative;
    overflow: hidden;
    background: #ffffff;
    padding: 38px 42px;
    border-radius: 24px;
    margin-bottom: 34px;
    border: 1px solid #e6e9ef;
    box-shadow: 0 12px 36px rgba(27, 39, 61, 0.045);
}

.hero:after {
    content: "";
    position: absolute;
    width: 220px;
    height: 220px;
    right: -54px;
    top: -105px;
    border-radius: 50%;
    background: #f0edff;
    box-shadow: 0 0 0 34px #f8f7ff;
}

.eyebrow {
    position: relative;
    z-index: 1;
    color: #6b55d9;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.8px;
    margin-bottom: 12px;
}

.hero h1 {
    position: relative;
    z-index: 1;
    color: #18212f !important;
    font-size: clamp(32px, 4vw, 46px);
    letter-spacing: -1.8px;
    line-height: 1.08;
    margin: 0 0 12px 0;
}

.hero p {
    position: relative;
    z-index: 1;
    color: #697386 !important;
    max-width: 650px;
    line-height: 1.65;
    margin-bottom: 0;
}

.section-label {
    color: #6b55d9 !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.7px;
    margin: 10px 0 15px;
}

.stTextArea textarea,
.stTextInput input {
    background: #ffffff !important;
    color: #18212f !important;
    -webkit-text-fill-color: #18212f !important;
    opacity: 1 !important;
    border-radius: 12px !important;
    border: 1px solid #dfe3eb !important;
    font-size: 14px !important;
    line-height: 1.65 !important;
    transition: border-color 150ms ease, box-shadow 150ms ease;
}

.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: #8876e8 !important;
    box-shadow: 0 0 0 3px rgba(107, 85, 217, 0.12) !important;
}

[data-testid="stWidgetLabel"] p {
    color: #303b4d !important;
    font-size: 13px;
    font-weight: 650;
}

div.stButton > button {
    background: #6b55d9;
    color: #ffffff;
    border: none;
    border-radius: 11px;
    min-height: 48px;
    font-weight: 700;
    transition: background 150ms ease, transform 150ms ease;
}

div.stButton > button:hover {
    background: #5943c6;
    color: #ffffff;
    border: none;
    transform: translateY(-1px);
}

div.stButton > button:focus {
    box-shadow: 0 0 0 3px rgba(107, 85, 217, 0.2) !important;
}

.response-title {
    color: #202a3a !important;
    font-size: 16px;
    font-weight: 700;
    margin-top: 8px;
    margin-bottom: 6px;
}

.response-subtitle {
    color: #7a8495 !important;
    font-size: 13px;
    margin-bottom: 12px;
}

.response-card {
    background: #ffffff !important;
    color: #283346 !important;
    min-height: 300px;
    max-height: 380px;
    overflow-y: auto;
    overflow-x: hidden;
    box-sizing: border-box;
    padding: 20px;
    border: 1px solid #e4e7ee;
    border-radius: 15px;
    font-size: 14px;
    line-height: 1.7;
    overflow-wrap: anywhere;
    white-space: normal;
    scrollbar-width: thin;
    scrollbar-color: #c3bddf #f5f4fa;
    box-shadow: 0 5px 16px rgba(27, 39, 61, 0.035);
}

.response-card,
.response-card * {
    color: #283346 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #e6e9ef;
    border-radius: 16px;
    background: #ffffff;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e6e9ef;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 5px 16px rgba(27, 39, 61, 0.035);
}

[data-testid="stMetricLabel"] {
    color: #707b8e !important;
}

[data-testid="stMetricValue"] {
    color: #6b55d9 !important;
}

div[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #e6e9ef;
    border-radius: 12px;
}

[data-testid="stDataFrame"] {
    background: #ffffff;
    border: 1px solid #e6e9ef;
    border-radius: 14px;
    overflow: hidden;
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

[data-testid="stCaptionContainer"] {
    color: #7a8495;
}

hr {
    border-color: #e3e6ed;
    margin: 2rem 0;
}

@media (max-width: 700px) {
    .block-container {
        padding: 1.25rem 1rem 2.5rem;
    }

    .hero {
        padding: 28px 24px;
        border-radius: 18px;
    }

    .hero:after {
        opacity: 0.55;
        right: -140px;
    }
}
</style>
""", unsafe_allow_html=True)


# -------------------- SESSION STATE --------------------

defaults = {
    "question": "Explain how a student can manage a monthly budget.",
    "role_instruction": (
        "You are a helpful financial advisor. "
        "Explain the answer clearly in simple language."
    ),
    "negative_instruction": (
        "Do not mention any brand names. "
        "Avoid unnecessary technical terms."
    ),
    "experiment_results": None,
    "experiment_error": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------- HEADER --------------------

st.markdown("""
<div class="hero">
    <div class="eyebrow">· PROMPT DESIGN</div>
    <h1>Prompt Lab</h1>
    <p>
        See how a role and clear boundaries shape an AI response.
        Run three prompt styles side by side and compare the results.
    </p>
</div>
""", unsafe_allow_html=True)


# -------------------- INPUT --------------------

st.markdown(
    '<div class="section-label">01 / DEFINE YOUR TASK</div>',
    unsafe_allow_html=True
)

question = st.text_area(
    "Academic or general question",
    key="question",
    height=100,
    placeholder="Enter the question you want the model to answer..."
)

role_col, negative_col = st.columns(2, gap="large")

with role_col:
    st.markdown(
        '<div class="response-title">🟢 Role-Based Instruction</div>',
        unsafe_allow_html=True
    )

    role = st.text_area(
        "Define the AI role and response style",
        key="role_instruction",
        height=130,
        help="Example: You are a college teacher. Explain in simple English."
    )

with negative_col:
    st.markdown(
        '<div class="response-title">🟣 Negative Instructions</div>',
        unsafe_allow_html=True
    )

    negative_instruction = st.text_area(
        "What should the AI avoid?",
        key="negative_instruction",
        height=130,
        help="Example: Do not use difficult words or irrelevant details."
    )

st.caption(
    "The normal response uses only your question. The other two responses "
    "add the role and then the negative instructions."
)


# -------------------- BUTTONS --------------------

generate_col, clear_col = st.columns([3, 1])

with generate_col:
    generate = st.button(
        "⚡ Generate Responses",
        use_container_width=True
    )

with clear_col:
    clear = st.button(
        "↻ Clear & Reset",
        use_container_width=True
    )


# -------------------- CLEAR --------------------

if clear:
    for key in defaults:
        st.session_state.pop(key, None)

    st.rerun()


# -------------------- GENERATE --------------------

if generate:
    if not question.strip():
        st.warning("Please enter a question.")
    elif not role.strip():
        st.warning("Please enter a role-based instruction.")
    elif not negative_instruction.strip():
        st.warning("Please enter a negative instruction.")
    else:
        try:
            with st.spinner(
                "Ollama is generating three responses. Please wait..."
            ):
                results = evaluate_prompts(
                    question,
                    role,
                    negative_instruction
                )

            st.session_state["experiment_results"] = results
            st.session_state["experiment_error"] = ""
            st.success("All three responses generated successfully!")

        except (OllamaError, ValueError) as error:
            st.session_state["experiment_error"] = str(error)
            st.session_state["experiment_results"] = None

        except Exception as error:
            st.session_state["experiment_error"] = str(error)
            st.session_state["experiment_results"] = None


# -------------------- ERROR --------------------

if st.session_state["experiment_error"]:
    st.error(st.session_state["experiment_error"])


# -------------------- RESULTS --------------------

results = st.session_state["experiment_results"]

if results:
    st.divider()

    st.markdown(
        '<div class="section-label">02 / GENERATED RESPONSES</div>',
        unsafe_allow_html=True
    )

    response_columns = st.columns(3, gap="medium")

    response_items = [
        (
            "⚪ Normal Response",
            "Question only",
            "normal_response"
        ),
        (
            "🟢 Role-Based Response",
            "Role + question",
            "role_response"
        ),
        (
            "🟣 Controlled Response",
            "Role + restrictions",
            "controlled_response"
        )
    ]

    for column, item in zip(response_columns, response_items):
        title, subtitle, result_key = item
        response = results[result_key]

        with column:
            st.markdown(
                f'<div class="response-title">{title}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="response-subtitle">{subtitle}</div>',
                unsafe_allow_html=True
            )

            safe_response = html.escape(response).replace("\n", "<br>")

            st.markdown(
                f'<div class="response-card">{safe_response}</div>',
                unsafe_allow_html=True
            )

            st.caption(f"Word count: {len(response.split())}")

    # -------------------- PROMPT DETAILS --------------------

    st.divider()

    st.markdown(
        '<div class="section-label">03 / PROMPT DETAILS</div>',
        unsafe_allow_html=True
    )

    prompt_columns = st.columns(3, gap="medium")

    prompt_items = [
        ("Normal Prompt", "normal_prompt"),
        ("Role-Based Prompt", "role_prompt"),
        ("Controlled Prompt", "controlled_prompt")
    ]

    for column, item in zip(prompt_columns, prompt_items):
        title, prompt_key = item

        with column:
            with st.expander(title):
                st.code(results[prompt_key], language="text")

    # -------------------- COMPARISON DASHBOARD --------------------

    st.divider()

    st.markdown(
        '<div class="section-label">04 / COMPARISON DASHBOARD</div>',
        unsafe_allow_html=True
    )

    normal_words = len(results["normal_response"].split())
    role_words = len(results["role_response"].split())
    controlled_words = len(results["controlled_response"].split())

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric("Normal Words", normal_words)
    metric2.metric("Role-Based Words", role_words)
    metric3.metric("Controlled Words", controlled_words)

    comparison_data = pd.DataFrame({
        "Feature": [
            "Question included",
            "Role instruction",
            "Negative instruction",
            "Generated response length"
        ],
        "Normal": [
            "Yes",
            "No",
            "No",
            f"{normal_words} words"
        ],
        "Role-Based": [
            "Yes",
            "Yes",
            "No",
            f"{role_words} words"
        ],
        "Role + Negative": [
            "Yes",
            "Yes",
            "Yes",
            f"{controlled_words} words"
        ]
    })

    st.dataframe(
        comparison_data,
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Observation: Role instructions guide the model's perspective "
        "and style. Negative instructions tell the model what to avoid. "
        "The actual effect depends on the question and the model."
    )

