
import streamlit as st
import pandas as pd

from main import compare_prompts, OllamaError

st.set_page_config(
    page_title="PromptLab | Experiment 5",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------- DESIGN --------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f3f0ff, #edf6ff, #ffffff);
    color: #172033;
}

.block-container {
    max-width: 1300px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    background: linear-gradient(120deg, #e5ddff, #dceeff);
    padding: 28px 32px;
    border-radius: 18px;
    margin-bottom: 25px;
    border: 1px solid #d5dcf1;
}

.hero h1 {
    color: #30245f !important;
    font-size: 32px;
    margin-bottom: 8px;
}

.hero p {
    color: #414b70 !important;
    margin-bottom: 0;
}

.section-label {
    color: #5363b8 !important;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.3px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border: 1px solid #dce2f1;
    border-radius: 14px;
}

div.stButton > button {
    min-height: 43px;
    border-radius: 9px;
    font-weight: 600;
    border: 1px solid #cbd5e1;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #7662d9, #5595db);
    color: white;
    border: none;
}

div.stButton > button[kind="primary"]:hover {
    background: #5d55c7;
    color: white;
}

.stTextArea textarea {
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
    background-color: #ffffff !important;
    opacity: 1 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 9px !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
}

.stTextArea textarea:disabled {
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
    background-color: #ffffff !important;
    opacity: 1 !important;
}

.stTextArea label,
.stMarkdown,
p,
li {
    color: #172033;
}

div[data-testid="stExpander"] {
    background: white;
    border: 1px solid #e4e8f1;
    border-radius: 10px;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #dce2f1;
    border-radius: 12px;
    padding: 14px;
}

[data-testid="stMetricLabel"] {
    color: #4b5270 !important;
}

[data-testid="stMetricValue"] {
    color: #30245f !important;
}

hr {
    border-color: #dce2f1;
}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown("""
<div class="hero">
    <h1>🧪 EXPERIMENT 05 | FEW-SHOT VS ZERO-SHOT PROMPTING</h1>
    <p style="margin-top:12px;">
        Explore how examples influence a model's response using Ollama.
    </p>
</div>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
defaults = {
    "question_input": "Explain the difference between a stack and a queue.",
    "zero_result": "",
    "few_result": "",
    "zero_prompt": "",
    "few_prompt": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------- INPUT --------------------
st.markdown(
    '<div class="section-label">01 — INPUT CONFIGURATION</div>',
    unsafe_allow_html=True
)
question = st.text_area(
    "Enter Your question",
    height=100,
    key="question_input",
    placeholder="Example: Explain binary search."
)

st.caption(
    "Zero-shot uses instructions without examples. "
    "Few-shot provides academic examples before the question."
)

button_col1, button_col2 = st.columns([3, 1])

with button_col1:
    generate = st.button(
        "✨ Generate & Compare",
        type="primary",
        use_container_width=True
    )

with button_col2:
    clear = st.button(
        "↻ Clear & Reset",
        use_container_width=True
    )

# -------------------- RESET --------------------
if clear:
    for key in defaults:
        st.session_state.pop(key, None)

    st.rerun()

# -------------------- GENERATE --------------------
if generate:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner(
                "Ollama is generating both responses. Please wait..."
            ):
                zero, few, zero_prompt, few_prompt = compare_prompts(
                    question.strip()
                )

            st.session_state["zero_result"] = zero
            st.session_state["few_result"] = few
            st.session_state["zero_prompt"] = zero_prompt
            st.session_state["few_prompt"] = few_prompt

            st.success("Both responses generated successfully!")

        except OllamaError as error:
            st.error(str(error))

        except Exception as error:
            st.error(f"Unable to generate responses: {error}")

# -------------------- RESULTS --------------------
if (
    st.session_state["zero_result"]
    and st.session_state["few_result"]
):
    st.divider()

    st.markdown(
        '<div class="section-label">02 — RESPONSE COMPARISON</div>',
        unsafe_allow_html=True
    )
    zero_col, few_col = st.columns(2, gap="large")

    with zero_col:
        with st.container(border=True):
            st.markdown("### 🔵 Zero-Shot")
            st.caption("Instructions only · No examples")

            st.text_area(
                "Zero-Shot Response",
                value=st.session_state["zero_result"],
                height=280,
                disabled=True,
                key="zero_output"
            )
    with few_col:
        with st.container(border=True):
            st.markdown("### 🟣 Few-Shot")
            st.caption("Examples included · Pattern guidance")

            st.text_area(
                "Few-Shot Response",
                value=st.session_state["few_result"],
                height=280,
                disabled=True,
                key="few_output"
            )
    # -------------------- DASHBOARD --------------------
    st.divider()

    st.markdown(
        '<div class="section-label">03 — COMPARISON DASHBOARD</div>',
        unsafe_allow_html=True
    )

    zero_response = st.session_state["zero_result"]
    few_response = st.session_state["few_result"]

    zero_words = len(zero_response.split())
    few_words = len(few_response.split())

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric("Zero-Shot Word Count", zero_words)
    metric2.metric("Few-Shot Word Count", few_words)
    metric3.metric(
        "Responses Different",
        "Yes" if zero_response.strip() != few_response.strip() else "No"
    )

    comparison_data = pd.DataFrame({
        "Feature": [
            "Examples provided",
            "Prompt structure",
            "Response guidance",
            "Typical use",
            "Generated response length"
        ],
        "Zero-Shot": [
            "No",
            "Direct instructions",
            "Instructions guide the model",
            "Direct questions",
            f"{zero_words} words"
        ],
        "Few-Shot": [
            "Yes",
            "Instructions plus examples",
            "Examples demonstrate a pattern",
            "Specific formats and tasks",
            f"{few_words} words"
        ]
    })

    st.dataframe(
        comparison_data,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### 💡 Key Takeaway")

    st.success(
        "Zero-shot prompting relies on instructions alone, whereas "
        "few-shot prompting provides examples to demonstrate the "
        "expected answer style. Actual results depend on the model "
        "and the question."
    )



