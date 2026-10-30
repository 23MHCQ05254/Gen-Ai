
import html
import re
import streamlit as st

from main import run_refinement, OllamaError, check_connection


# -------------------- PAGE CONFIGURATION --------------------
st.set_page_config(
    page_title="Experiment 7 - Iterative Refinement",
    page_icon="🔄",
    layout="wide"
)


# -------------------- CSS DESIGN --------------------
st.markdown("""
<style>
.stApp {
    background: #f4f6fb;
    color: #172033;
}

.main .block-container {
    max-width: 1500px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.main-title {
    text-align: center;
    font-size: 29px;
    font-weight: 750;
    color: #293b78;
}

.subtitle {
    text-align: center;
    color: #555f72;
    margin-bottom: 25px;
}

.section-heading {
    color: #293b78;
    font-size: 20px;
    font-weight: 700;
    margin: 14px 0;
}

.response-title {
    color: #293b78;
    font-weight: 700;
    font-size: 16px;
    margin-bottom: 8px;
    min-height: 25px;
}

.response-box {
    box-sizing: border-box;
    height: 360px;
    overflow-y: auto;
    overflow-x: hidden;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
    padding: 14px;
    border: 1px solid #d5dbe7;
    border-radius: 9px;
    background: #ffffff;
    color: #111111;
    font-size: 14px;
    line-height: 1.65;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background-color: white !important;
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    opacity: 1 !important;
}

div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label {
    color: #172033 !important;
    font-weight: 600 !important;
}

.stMarkdown p,
.stMarkdown li {
    color: #172033;
}

div.stButton > button {
    min-height: 42px;
    border-radius: 8px;
    font-weight: 600;
}

div.stButton > button[kind="primary"] {
    background: #5268c9;
    color: white;
    border: none;
}

div.stButton > button[kind="primary"]:hover {
    background: #3d50ac;
    color: white;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #d5dbe7;
    border-radius: 10px;
    padding: 12px;
}

hr {
    border-color: #d5dbe7;
}
</style>
""", unsafe_allow_html=True)


# -------------------- HELPER FUNCTIONS --------------------
def count_words(text):
    return len(re.findall(r"\b[\w'-]+\b", text))


def count_bullets(text):
    return sum(
        1 for line in text.splitlines()
        if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line)
    )


def find_repeated_sentences(first, second):
    def sentences(text):
        return {
            sentence.strip().lower()
            for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
            if len(sentence.strip()) > 15
        }

    return sentences(first) & sentences(second)


def evaluate_response(stage, response, previous=""):
    checks = []
    response = response or ""

    words = count_words(response)
    bullets = count_bullets(response)

    checks.append(("Response is not empty", bool(response.strip())))
    checks.append((f"Word count recorded: {words}", True))

    if stage in (1, 2):
        checks.append((
            f"Word count is 80–120 (actual: {words})",
            80 <= words <= 120
        ))
        checks.append((
            f"Exactly 5 bullet points (actual: {bullets})",
            bullets == 5
        ))

    if stage == 2:
        lower = response.lower()

        definition_found = any(term in lower for term in [
            "definition", "means", "refers to", "is a",
            "is the process", "can be defined"
        ])

        example_found = any(term in lower for term in [
            "example", "for example", "for instance",
            "such as", "e.g."
        ])

        checks.append((
            "Definition or meaning included",
            definition_found
        ))
        checks.append(("Example included", example_found))
        checks.append((
            "No exact repeated sentences from Refinement 1",
            not find_repeated_sentences(previous, response)
        ))

    return checks


def show_response(title, response):
    safe_title = html.escape(title)
    safe_response = html.escape(response or "")

    st.markdown(
        f'<div class="response-title">{safe_title}</div>'
        f'<div class="response-box">{safe_response}</div>',
        unsafe_allow_html=True
    )


def show_evaluation(title, checks):
    st.markdown(f"**{title}**")

    for description, passed in checks:
        icon = "✅" if passed else "❌"
        st.write(f"{icon} {description}")


# -------------------- SESSION STATE --------------------
defaults = {
    "topic": "Normalization in DBMS",
    "source_text": "",
    "refinement_results": None,
    "refinement_error": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------- HEADER --------------------
st.markdown(
    '<div class="main-title">'
    'Constraint Specification & Iterative Refinement'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Experiment 7 | Improve an initial response through two refinement stages'
    '</div>',
    unsafe_allow_html=True
)


# -------------------- INPUT --------------------
st.markdown(
    '<div class="section-heading">1. Enter Your Input</div>',
    unsafe_allow_html=True
)

topic = st.text_input(
    "Topic",
    placeholder="Example: Normalization in DBMS",
    key="topic"
)

source_text = st.text_area(
    "Optional Source Text",
    placeholder="Paste additional reference information here (optional)...",
    height=120,
    key="source_text"
)

st.caption(
    "Enter a topic, or provide source text. A source text is optional."
)


# -------------------- BUTTONS --------------------
left, right = st.columns(2)

with left:
    generate_clicked = st.button(
        "🔄 Generate & Refine",
        type="primary",
        use_container_width=True
    )

with right:
    clear_clicked = st.button(
        "🧹 Clear All",
        use_container_width=True
    )


# -------------------- CLEAR --------------------
if clear_clicked:
    for key in defaults:
        st.session_state.pop(key, None)

    st.rerun()


# -------------------- GENERATION --------------------
if generate_clicked:
    st.session_state["refinement_results"] = None
    st.session_state["refinement_error"] = ""

    if not topic.strip() and not source_text.strip():
        st.warning("Please enter a topic or source text.")
    else:
        try:
            with st.spinner("Connecting to Ollama..."):
                check_connection()

            with st.spinner(
                "Ollama is generating the initial response "
                "and performing two refinement stages..."
            ):
                results = run_refinement(
                    topic.strip() or "Text summary",
                    source_text.strip()
                )

            required_keys = [
                "initial_response",
                "refinement_1_response",
                "refinement_2_response",
                "initial_prompt",
                "refinement_1_prompt",
                "refinement_2_prompt"
            ]

            missing = [
                key for key in required_keys
                if key not in results
            ]

            if missing:
                raise ValueError(
                    "Missing result fields: " + ", ".join(missing)
                )

            st.session_state["refinement_results"] = results

        except (OllamaError, ValueError) as error:
            st.session_state["refinement_error"] = str(error)

        except Exception as error:
            st.session_state["refinement_error"] = str(error)


# -------------------- ERROR DISPLAY --------------------
if st.session_state["refinement_error"]:
    st.error("Generation failed.")

    with st.expander("View error details"):
        st.code(st.session_state["refinement_error"])


# -------------------- RESPONSE COMPARISON --------------------
results = st.session_state["refinement_results"]

if results:
    initial = results["initial_response"]
    refined1 = results["refinement_1_response"]
    refined2 = results["refinement_2_response"]

    st.divider()

    st.markdown(
        '<div class="section-heading">2. Response Comparison</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        show_response("Initial Response", initial)

    with col2:
        show_response("Refinement 1", refined1)

    with col3:
        show_response("Refinement 2", refined2)

    # -------------------- METRICS --------------------
    st.markdown(
        '<div class="section-heading">3. Response Metrics</div>',
        unsafe_allow_html=True
    )

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "Initial Word Count",
        count_words(initial)
    )

    metric2.metric(
        "Refinement 1 Words",
        count_words(refined1)
    )

    metric3.metric(
        "Refinement 2 Words",
        count_words(refined2)
    )

    # -------------------- EVALUATION --------------------
    st.markdown(
        '<div class="section-heading">'
        '4. Detailed Constraints Evaluation'
        '</div>',
        unsafe_allow_html=True
    )

    e1, e2, e3 = st.columns(3, gap="medium")

    with e1:
        with st.container(border=True):
            show_evaluation(
                "Initial Response",
                evaluate_response(0, initial)
            )

    with e2:
        with st.container(border=True):
            show_evaluation(
                "Refinement 1",
                evaluate_response(1, refined1)
            )

    with e3:
        with st.container(border=True):
            show_evaluation(
                "Refinement 2",
                evaluate_response(2, refined2, refined1)
            )

    st.caption(
        "These are rule-based checks. They verify word counts, bullet "
        "counts, selected keywords and repeated sentences; they cannot "
        "guarantee factual accuracy or complete semantic correctness."
    )


   


