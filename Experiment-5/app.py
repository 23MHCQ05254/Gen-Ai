import pandas as pd
import streamlit as st

from main import OllamaError, compare_prompts

st.set_page_config(
    page_title="PromptLab | Experiment 05",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --ink: #17251f;
        --muted: #6a786f;
        --paper: #f5f6f1;
        --line: #e2e7df;
        --green: #b9ef75;
        --deep-green: #315d43;
        --violet: #7763d5;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 86% 3%, rgba(185, 239, 117, .15), transparent 28rem),
            var(--paper);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        max-width: 1180px;
        padding: 2rem 2.5rem 3.5rem;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .hero {
        position: relative;
        overflow: hidden;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        gap: 2rem;
        min-height: 255px;
        padding: 2.5rem 3rem;
        margin: 0 0 2rem;
        border-radius: 22px;
        color: #f5f8f2;
        background: #17251f;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 360px;
        height: 360px;
        right: 7%;
        top: -225px;
        border: 1px solid rgba(185, 239, 117, .22);
        border-radius: 50%;
        box-shadow: 0 0 0 35px rgba(185, 239, 117, .035),
                    0 0 0 70px rgba(185, 239, 117, .025);
        pointer-events: none;
    }

    .hero-copy, .hero-index {
        position: relative;
        z-index: 1;
    }

    .hero-kicker, .eyebrow, .hero-index-label {
        font-family: 'DM Mono', monospace;
        font-size: .72rem;
        letter-spacing: .12em;
        text-transform: uppercase;
    }

    .hero-kicker {
        color: var(--green);
        margin-bottom: 1.1rem;
    }

    .hero h1 {
        max-width: 660px;
        margin: 0;
        color: #f5f8f2;
        font: 700 clamp(2.2rem, 5vw, 3.65rem)/1.07 'Manrope', sans-serif;
        letter-spacing: -.055em;
    }

    .hero p {
        margin: .9rem 0 0;
        color: #b7c3ba;
        font-size: 1rem;
    }

    .hero-index {
        flex: 0 0 150px;
        padding: 1rem 0 0 1.2rem;
        border-left: 1px solid rgba(255, 255, 255, .18);
    }

    .hero-index strong {
        display: block;
        margin-top: .5rem;
        color: var(--green);
        font: 700 2.7rem/1 'Manrope', sans-serif;
        letter-spacing: -.07em;
    }

    .hero-index-label {
        color: #a7b3aa;
        line-height: 1.7;
    }

    .eyebrow {
        margin: 0 0 .45rem;
        color: var(--deep-green);
    }

    .section-heading {
        margin: 0 0 .35rem;
        color: var(--ink);
        font: 700 1.35rem 'Manrope', sans-serif;
        letter-spacing: -.035em;
    }

    .section-description {
        margin: 0 0 1.35rem;
        color: var(--muted);
        font-size: .95rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(255, 255, 255, .82);
        box-shadow: 0 8px 26px rgba(35, 54, 41, .035);
    }

    .stTextArea label {
        color: var(--ink) !important;
        font-weight: 600 !important;
    }

    .stTextArea textarea {
        border: 1px solid #dce3da !important;
        border-radius: 12px !important;
        background: #fbfcf9 !important;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: .97rem !important;
        line-height: 1.65 !important;
        transition: border-color .2s, box-shadow .2s;
    }

    .stTextArea textarea:focus {
        border-color: #7eaa71 !important;
        box-shadow: 0 0 0 3px rgba(126, 170, 113, .13) !important;
    }

    .stTextArea textarea:disabled {
        background: #fbfcf9 !important;
        opacity: 1 !important;
    }

    div.stButton > button {
        min-height: 45px;
        border: 1px solid #dce3da;
        border-radius: 11px;
        color: var(--ink);
        background: #fff;
        font-weight: 600;
        transition: transform .15s, border-color .15s, background .15s;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
        border-color: #91ae84;
        color: var(--ink);
    }

    div.stButton > button[kind="primary"] {
        border: 1px solid #17251f;
        color: #17251f;
        background: var(--green);
    }

    div.stButton > button[kind="primary"]:hover {
        border-color: #a5dc63;
        color: #17251f;
        background: #a5dc63;
    }

    .input-meta {
        display: flex;
        align-items: center;
        gap: .55rem;
        margin-top: .25rem;
        color: var(--muted);
        font: .72rem 'DM Mono', monospace;
        letter-spacing: .035em;
    }

    .input-meta-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #7db36f;
    }

    .response-title {
        display: flex;
        align-items: center;
        gap: .65rem;
        margin: 0 0 .3rem;
        color: var(--ink);
        font: 700 1.14rem 'Manrope', sans-serif;
        letter-spacing: -.025em;
    }

    .response-marker {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #58835d;
    }

    .response-marker.few {
        background: var(--violet);
    }

    .response-caption {
        margin: 0 0 1rem;
        color: var(--muted);
        font-size: .85rem;
    }

    [data-testid="stMetric"] {
        min-height: 112px;
        padding: 1.1rem 1.25rem;
        border: 1px solid var(--line);
        border-radius: 15px;
        background: #fff;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-size: .82rem !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--ink) !important;
        font: 700 1.75rem 'Manrope', sans-serif !important;
    }

    [data-testid="stDataFrame"] {
        overflow: hidden;
        border: 1px solid var(--line);
        border-radius: 14px;
    }

    div[data-testid="stAlert"] {
        border-radius: 13px;
    }

    hr {
        margin: 2.25rem 0;
        border-color: var(--line);
    }

    @media (max-width: 700px) {
        .block-container {
            padding: 1.1rem 1rem 2.5rem;
        }

        .hero {
            min-height: auto;
            padding: 1.8rem 1.5rem;
            border-radius: 17px;
        }

        .hero-index {
            display: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <div class="hero-copy">
            <div class="hero-kicker">PromptLab&nbsp; / &nbsp;Prompt study</div>
            <h1>One question.<br>Two ways to prompt.</h1>
            <p>See what examples change in an AI-generated answer.</p>
        </div>
        <div class="hero-index">
            <div class="hero-index-label">Experiment<br>number</div>
            <strong>05</strong>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

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

with st.container(border=True):
    st.markdown(
        """
        <div class="eyebrow">01 &nbsp; / &nbsp; Your experiment</div>
        <h2 class="section-heading">Start with a question</h2>
        <p class="section-description">
            Both approaches receive the same question. Only the prompt changes.
        </p>
        """,
        unsafe_allow_html=True,
    )
    question = st.text_area(
        "Your question",
        height=112,
        key="question_input",
        placeholder="For example: Explain binary search.",
    )
    st.markdown(
        """
        <div class="input-meta">
            <span class="input-meta-dot"></span>
            LOCAL MODEL &nbsp;·&nbsp; LLAMA 3.2 1B
            &nbsp;&nbsp; / &nbsp;&nbsp; ZERO-SHOT + FEW-SHOT
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    button_col1, button_col2 = st.columns([2, 1])
    with button_col1:
        generate = st.button(
            "Run comparison",
            type="primary",
            use_container_width=True,
        )
    with button_col2:
        clear = st.button(
            "Clear and reset",
            use_container_width=True,
        )

if clear:
    for key in defaults:
        st.session_state.pop(key, None)
    st.rerun()

if generate:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Generating both responses with Ollama..."):
                zero, few, zero_prompt, few_prompt = compare_prompts(
                    question.strip()
                )

            st.session_state["zero_result"] = zero
            st.session_state["few_result"] = few
            st.session_state["zero_prompt"] = zero_prompt
            st.session_state["few_prompt"] = few_prompt

            st.success("Both responses generated successfully.")

        except OllamaError as error:
            st.error(str(error))

        except Exception as error:
            st.error(f"Unable to generate responses: {error}")

if st.session_state["zero_result"] and st.session_state["few_result"]:
    st.divider()
    st.markdown(
        """
        <div class="eyebrow">02 &nbsp; / &nbsp; The outputs</div>
        <h2 class="section-heading">Compare the responses</h2>
        <p class="section-description">
            Same model, same question — different prompting strategies.
        </p>
        """,
        unsafe_allow_html=True,
    )

    zero_col, few_col = st.columns(2, gap="large")
    with zero_col:
        with st.container(border=True):
            st.markdown(
                """
                <div class="response-title">
                    <span class="response-marker"></span>Zero-shot
                </div>
                <p class="response-caption">Instructions only · No examples</p>
                """,
                unsafe_allow_html=True,
            )
            st.text_area(
                "Zero-shot response",
                value=st.session_state["zero_result"],
                height=280,
                disabled=True,
                key="zero_output",
            )

    with few_col:
        with st.container(border=True):
            st.markdown(
                """
                <div class="response-title">
                    <span class="response-marker few"></span>Few-shot
                </div>
                <p class="response-caption">Examples included · Pattern guidance</p>
                """,
                unsafe_allow_html=True,
            )
            st.text_area(
                "Few-shot response",
                value=st.session_state["few_result"],
                height=280,
                disabled=True,
                key="few_output",
            )

    st.divider()
    st.markdown(
        """
        <div class="eyebrow">03 &nbsp; / &nbsp; The readout</div>
        <h2 class="section-heading">A closer look</h2>
        <p class="section-description">
            A quick summary of how the two generated answers compare.
        </p>
        """,
        unsafe_allow_html=True,
    )

    zero_response = st.session_state["zero_result"]
    few_response = st.session_state["few_result"]
    zero_words = len(zero_response.split())
    few_words = len(few_response.split())

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Zero-shot words", zero_words)
    metric2.metric("Few-shot words", few_words)
    metric3.metric(
        "Different responses",
        "Yes" if zero_response.strip() != few_response.strip() else "No",
    )

    st.write("")
    comparison_data = pd.DataFrame(
        {
            "Feature": [
                "Examples provided",
                "Prompt structure",
                "Response guidance",
                "Typical use",
                "Generated response length",
            ],
            "Zero-shot": [
                "No",
                "Direct instructions",
                "Instructions guide the model",
                "Direct questions",
                f"{zero_words} words",
            ],
            "Few-shot": [
                "Yes",
                "Instructions plus examples",
                "Examples demonstrate a pattern",
                "Specific formats and tasks",
                f"{few_words} words",
            ],
        }
    )
    st.dataframe(
        comparison_data,
        use_container_width=True,
        hide_index=True,
    )

    st.write("")
    st.markdown(
        """
        <div class="eyebrow">Takeaway</div>
        <h2 class="section-heading">Examples set a pattern</h2>
        <p class="section-description">
            Zero-shot prompting relies on instructions alone, whereas few-shot
            prompting shows examples of the expected answer style. Results vary
            with the model and the question.
        </p>
        """,
        unsafe_allow_html=True,
    )
