
import html
import pandas as pd
import streamlit as st

from main import evaluate_prompts, OllamaError

st.set_page_config(
    page_title="Prompt Studio | Experiment 6",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------- DESIGN --------------------

st.markdown("""
<style>
.stApp {
    background: #101827;
    color: #F3F6FC;
}

.block-container {
    max-width: 1350px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4, p, label {
    color: #F3F6FC !important;
}

.hero {
    background: linear-gradient(120deg, #123A50, #126E75);
    padding: 25px;
    border-radius: 16px;
    margin-bottom: 24px;
    border: 1px solid #287D85;
}

.hero h1 {
    color: white !important;
    margin: 0 0 8px 0;
}

.hero p {
    color: #E0FFFC !important;
    margin-bottom: 0;
}

.section-label {
    color: #5EEAD4 !important;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}

.stTextArea textarea,
.stTextInput input {
    background: #FFFFFF !important;
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    opacity: 1 !important;
    border-radius: 8px !important;
    border: 1px solid #CBD5E1 !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
}

div.stButton > button {
    background: #16A6A1;
    color: white;
    border: none;
    border-radius: 9px;
    min-height: 44px;
    font-weight: 600;
}

div.stButton > button:hover {
    background: #12857F;
    color: white;
    border: none;
}

.response-title {
    color: #FFFFFF !important;
    font-size: 19px;
    font-weight: 700;
    margin-top: 8px;
    margin-bottom: 5px;
}

.response-subtitle {
    color: #B7C4D8 !important;
    font-size: 13px;
    margin-bottom: 10px;
}

.response-card {
    background: #FFFFFF !important;
    color: #111827 !important;
    height: 340px;
    overflow-y: auto;
    overflow-x: hidden;
    box-sizing: border-box;
    padding: 17px;
    border: 1px solid #CBD5E1;
    border-radius: 12px;
    font-size: 15px;
    line-height: 1.7;
    overflow-wrap: anywhere;
    white-space: normal;
    scrollbar-width: thin;
    scrollbar-color: #94A3B8 #F1F5F9;
}

.response-card,
.response-card * {
    color: #111827 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #334155;
    border-radius: 12px;
    background: #172235;
}

[data-testid="stMetric"] {
    background: #172235;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 14px;
}

[data-testid="stMetricLabel"] {
    color: #CBD5E1 !important;
}

[data-testid="stMetricValue"] {
    color: #5EEAD4 !important;
}

div[data-testid="stExpander"] {
    background: #172235;
    border: 1px solid #334155;
    border-radius: 10px;
}

hr {
    border-color: #334155;
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
    <h1>🎭 Prompt Studio</h1>
    <p>EXPERIMENT 06 · ROLE-BASED & NEGATIVE PROMPTING</p>
    <p style="margin-top:12px;">
        Explore how roles and restrictions influence AI-generated answers.
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


