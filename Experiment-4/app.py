
import streamlit as st
import pandas as pd

from main import (
    check_connection,
    generate_response,
    diagnose_and_refine,
    extract_corrected_prompt,
    compare_responses,
    OllamaError,
)

st.set_page_config(
    page_title="Experiment 4 - Prompt Debugging Lab",
    page_icon="🔍",
    layout="wide",
)

# -------------------- CSS --------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg, #f4f0ff 0%, #edf6ff 55%, #f8f5ff 100%
        );
        color: #172033;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }

    .hero {
        background: linear-gradient(120deg, #e5ddff, #dceeff);
        padding: 26px;
        border-radius: 18px;
        border: 1px solid #d4dafa;
        margin-bottom: 22px;
    }

    .hero h1 {
        color: #30245f;
        font-size: 30px;
        margin-bottom: 8px;
    }

    .hero p {
        color: #4a5070;
        font-size: 16px;
        margin-bottom: 0;
    }

    .panel {
        background: #ffffff;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #dce2f1;
        margin: 10px 0;
        color: #172033;
    }

    h2, h3 {
        color: #382c72 !important;
    }

    label, .stMarkdown, p, li {
        color: #24304a;
    }

    textarea {
        background-color: #ffffff !important;
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
        caret-color: #4338ca !important;
        border: 1px solid #a8b2d1 !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        line-height: 1.7 !important;
        opacity: 1 !important;
    }

    textarea:disabled {
        background-color: #ffffff !important;
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
        opacity: 1 !important;
    }

    div.stButton > button {
        background: linear-gradient(100deg, #7662d9, #5595db);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 18px;
        font-weight: 600;
    }

    div.stButton > button:hover {
        border: 1px solid #7662d9;
        color: white;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
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

    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- DEFAULT PROMPT --------------------
DEFAULT_PROMPT = (
    "Explain machine learning in exactly 50 words with a very detailed explanation covering every important concept. Put the answer in a paragraph and a table."
)

# -------------------- SESSION STATE --------------------
if "prompt_input" not in st.session_state:
    st.session_state.prompt_input = DEFAULT_PROMPT

state_keys = [
    "analysis_result",
    "corrected_prompt",
    "original_response",
    "corrected_response",
    "comparison_result",
]

for key in state_keys:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "comparison_result" else {}

# -------------------- HEADER --------------------
st.markdown(
    """
    <div class="hero">
        <h1>🔍 EXPERIMENT 4 · PROMPT DEBUGGING LAB</h1>
        <p>
            Detect prompt errors • Explain failure modes •
            Refine instructions • Compare results
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## 📝 1. Enter the Original Prompt")
prompt = st.text_area(
    "Original prompt",
    key="prompt_input",
    height=160,
    help="You can edit the default travel prompt before running the experiment.",
)

# -------------------- MAIN ACTION --------------------
if st.button(
    "🚀 ANALYZE & COMPARE ALL",
    use_container_width=True,
):
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        try:
            with st.spinner("Checking the model connection..."):
                check_connection()

            with st.spinner("Diagnosing prompt failures and refining the prompt..."):
                analysis = diagnose_and_refine(prompt)
                corrected_prompt = extract_corrected_prompt(analysis)

                if not corrected_prompt.strip():
                    raise ValueError(
                        "The model did not return a corrected prompt. "
                        "Please try again."
                    )

            st.session_state.analysis_result = analysis
            st.session_state.corrected_prompt = corrected_prompt

            with st.spinner("Generating the original response..."):
                original_response = generate_response(prompt)

            with st.spinner("Generating the corrected response..."):
                corrected_response = generate_response(corrected_prompt)

            st.session_state.original_response = original_response
            st.session_state.corrected_response = corrected_response
            st.session_state.comparison_result = compare_responses(
                original_response,
                corrected_response,
            )

            st.success("Experiment completed successfully!")

        except OllamaError as error:
            st.error(f"Model connection error: {error}")
            st.info(
                "Make sure Ollama is running and the model configured "
                "in main.py is installed."
            )
        except Exception as error:
            st.error(f"Something went wrong: {error}")

# -------------------- DIAGNOSIS --------------------
if st.session_state.analysis_result:
    st.markdown("---")
    st.markdown("## 🧩 2. Prompt Failure Diagnosis")

    analysis_text = st.session_state.analysis_result
    marker = "CORRECTED PROMPT:"
    marker_position = analysis_text.lower().find(marker.lower())

    if marker_position >= 0:
        diagnosis_text = analysis_text[:marker_position].strip()
    else:
        diagnosis_text = analysis_text.strip()

    st.markdown(
        f'<div class="panel">{diagnosis_text}</div>',
        unsafe_allow_html=True,
    )

# -------------------- CORRECTED PROMPT --------------------
if st.session_state.corrected_prompt:
    st.markdown("## 🛠️ 3. AI-Generated Corrected Prompt")

    st.text_area(
        "Refined prompt",
        value=st.session_state.corrected_prompt,
        height=180,
        disabled=True,
        key="corrected_prompt_display",
    )

# -------------------- RESPONSE COMPARISON --------------------
if (
    st.session_state.original_response
    and st.session_state.corrected_response
):
    st.markdown("---")
    st.markdown("## 📊 4. Original vs Corrected Response")

    left, right = st.columns(2)

    with left:
        st.markdown("### 🔴 Original Response")
        st.text_area(
            "Response before refinement",
            value=st.session_state.original_response,
            height=300,
            disabled=True,
            key="original_response_display",
        )

    with right:
        st.markdown("### 🟢 Corrected Response")
        st.text_area(
            "Response after refinement",
            value=st.session_state.corrected_response,
            height=300,
            disabled=True,
            key="corrected_response_display",
        )

    # -------------------- DASHBOARD --------------------
    st.markdown("---")
    st.markdown("## 📈 5. Response Comparison Dashboard")

    original = st.session_state.original_response
    corrected = st.session_state.corrected_response

    original_words = len(original.split())
    corrected_words = len(corrected.split())
    changed = original.strip() != corrected.strip()

    col1, col2, col3 = st.columns(3)

    col1.metric("Original Word Count", original_words)
    col2.metric("Corrected Word Count", corrected_words)
    col3.metric("Response Changed", "Yes" if changed else "No")

    comparison_rows = [
        {
            "Comparison Factor": "Prompt clarity",
            "Original Prompt": "Contains conflicting instructions",
            "Corrected Prompt": "Instructions clarified",
        },
        {
            "Comparison Factor": "Missing context",
            "Original Prompt": "Destination, dates and group size missing",
            "Corrected Prompt": "Requests necessary details or states assumptions",
        },
        {
            "Comparison Factor": "Budget requirements",
            "Original Prompt": "Budget conflicts with luxury requirements",
            "Corrected Prompt": "Budget and travel choices made consistent",
        },
        {
            "Comparison Factor": "Output format",
            "Original Prompt": "Bullet points and table requested together",
            "Corrected Prompt": "Output format clearly specified",
        },
        {
            "Comparison Factor": "Length requirements",
            "Original Prompt": "Detailed answer under 30 words",
            "Corrected Prompt": "Length requirement made realistic",
        },
        {
            "Comparison Factor": "Actual response",
            "Original Prompt": f"{original_words} words",
            "Corrected Prompt": f"{corrected_words} words",
        },
    ]

    st.dataframe(
        pd.DataFrame(comparison_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Note: The dashboard summarizes the original prompt's known issues "
        "and the intended corrections. The generated responses may vary "
        "depending on the local model."
    )

# -------------------- RESET --------------------
st.markdown("---")


def reset_app():
    keys_to_clear = [
        "prompt_input",
        "analysis_result",
        "corrected_prompt",
        "original_response",
        "corrected_response",
        "comparison_result",
        "corrected_prompt_display",
        "original_response_display",
        "corrected_response_display",
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)


st.button(
    "🧹 CLEAR & RESET",
    on_click=reset_app,
    use_container_width=True,
)
