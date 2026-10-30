
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

# -------------------- UI THEME --------------------
st.markdown(
    """
    <style>
    .stApp {
        background: #f3f4ef;
        color: #17251e;
    }

    .block-container {
        max-width: 1180px;
        padding: 2rem 1.5rem 4rem;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 36px 40px;
        margin-bottom: 22px;
        border: 1px solid #263d31;
        border-radius: 24px;
        background:
            radial-gradient(ellipse at 92% 10%, #35523c 0, transparent 36%),
            linear-gradient(120deg, #14221b 0%, #1c3025 100%);
        box-shadow: 0 18px 44px rgba(20, 34, 27, 0.13);
    }

    .hero h1 {
        color: #f7f8f2;
        font-size: clamp(30px, 4vw, 42px);
        font-weight: 750;
        letter-spacing: -1.7px;
        line-height: 1.08;
        margin: 12px 0 10px;
    }

    .hero p {
        max-width: 620px;
        color: #c1cdc3;
        font-size: 15px;
        line-height: 1.65;
        margin: 0;
    }

    .hero-kicker, .section-kicker {
        color: #b6e878;
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .workflow {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 0 0 30px;
    }

    .workflow-step {
        display: flex;
        align-items: center;
        gap: 9px;
        padding: 10px 14px;
        border: 1px solid #e0e4dc;
        border-radius: 999px;
        background: #fbfcf8;
        color: #536057;
        font-size: 12px;
        font-weight: 650;
    }

    .workflow-step span {
        display: grid;
        width: 21px;
        height: 21px;
        place-items: center;
        border-radius: 50%;
        background: #e7f2db;
        color: #315329;
        font-size: 11px;
        font-weight: 750;
    }

    h2 {
        color: #19291f !important;
        font-size: 22px !important;
        font-weight: 720 !important;
        letter-spacing: -0.5px;
        margin: 1.25rem 0 0.25rem !important;
    }

    h3 {
        color: #24372b !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }

    label, .stMarkdown, p, li {
        color: #46534a;
    }

    [data-testid="stWidgetLabel"] p {
        color: #39483e !important;
        font-size: 13px !important;
        font-weight: 650 !important;
    }

    textarea {
        background-color: #fbfcf8 !important;
        color: #1d2b22 !important;
        -webkit-text-fill-color: #1d2b22 !important;
        caret-color: #537a3b !important;
        border: 1px solid #d9dfd6 !important;
        border-radius: 14px !important;
        font-size: 14px !important;
        line-height: 1.75 !important;
        opacity: 1 !important;
        padding: 14px 16px !important;
    }

    textarea:disabled {
        background-color: #f8f9f5 !important;
        color: #27372d !important;
        -webkit-text-fill-color: #27372d !important;
        opacity: 1 !important;
    }

    div.stButton > button {
        min-height: 48px;
        background: #c9ef81;
        color: #1b2b1f;
        border: none;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 750;
        transition: background 150ms ease, transform 150ms ease;
    }

    div.stButton > button:hover {
        background: #b7e76a;
        border: none;
        color: #17251e;
        transform: translateY(-1px);
    }

    [data-testid="stMetric"] {
        min-height: 118px;
        padding: 20px;
        border: 1px solid #e0e5dc;
        border-radius: 16px;
        background: #fbfcf8;
        box-shadow: 0 5px 16px rgba(26, 42, 31, 0.035);
    }

    [data-testid="stMetricLabel"] {
        color: #627066 !important;
        font-size: 12px !important;
        font-weight: 650 !important;
    }

    [data-testid="stMetricValue"] {
        color: #203529 !important;
        font-size: 29px !important;
        font-weight: 750 !important;
    }

    [data-testid="stDataFrame"] {
        overflow: hidden;
        border: 1px solid #e0e5dc;
        border-radius: 14px;
        background: #fbfcf8;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    hr {
        border-color: #e1e5de !important;
        margin: 2rem 0 !important;
    }

    .panel {
        padding: 20px 22px;
        margin: 12px 0 20px;
        border: 1px solid #e0e5dc;
        border-left: 4px solid #a9d86c;
        border-radius: 14px;
        background: #fbfcf8;
        color: #34443a;
        line-height: 1.8;
        white-space: pre-wrap;
    }

    .stCaption {
        color: #758077 !important;
    }

    @media (max-width: 640px) {
        .block-container {
            padding: 1rem 1rem 2rem;
        }

        .hero {
            padding: 26px 23px;
            border-radius: 18px;
        }

        .workflow {
            gap: 7px;
        }

        .workflow-step {
            padding: 8px 11px;
            font-size: 11px;
        }
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
        <div class="hero-kicker">Experiment 04 &nbsp; / &nbsp; Local AI studio</div>
        <h1>Make every prompt<br>work harder.</h1>
        <p>
            Find the friction in your instructions, refine them with AI,
            and compare both responses side by side.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="workflow">
        <div class="workflow-step"><span>1</span> Write</div>
        <div class="workflow-step"><span>2</span> Diagnose</div>
        <div class="workflow-step"><span>3</span> Refine</div>
        <div class="workflow-step"><span>4</span> Compare</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## Start with your prompt")
st.caption("Paste an instruction below. The lab will diagnose it, create a clearer version, and compare the model's responses.")
prompt = st.text_area(
    "Original prompt",
    key="prompt_input",
    height=160,
    help="Edit the example or write your own prompt before running the experiment.",
)

# -------------------- MAIN ACTION --------------------
if st.button(
    "ANALYZE PROMPT  ·  REFINE  ·  COMPARE",
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
    st.markdown("## Prompt diagnosis")
    st.caption("What could make the original instruction harder for a model to follow?")

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
    st.markdown("## Refined prompt")
    st.caption("A clearer version that preserves your original intent.")

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
    st.markdown("## Response comparison")
    st.caption("See how the model responds to the original and refined instructions.")

    left, right = st.columns(2)

    with left:
        st.markdown("### Original")
        st.text_area(
            "Response before refinement",
            value=st.session_state.original_response,
            height=300,
            disabled=True,
            key="original_response_display",
        )

    with right:
        st.markdown("### Refined")
        st.text_area(
            "Response after refinement",
            value=st.session_state.corrected_response,
            height=300,
            disabled=True,
            key="corrected_response_display",
        )

    # -------------------- DASHBOARD --------------------
    st.markdown("---")
    st.markdown("## At a glance")
    st.caption("A quick read on response length and how much the output changed.")

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
    "CLEAR WORKSPACE",
    on_click=reset_app,
    use_container_width=True,
)
