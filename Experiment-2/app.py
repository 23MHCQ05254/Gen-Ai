
import streamlit as st
import re
from main import compare_responses, check_connection

st.set_page_config(
   page_title="Prompt Lab · Experiment 02",
   page_icon="✳",
    layout="wide"
)

# ---------- Prompt Lab Design System ----------
st.markdown("""
<style>
:root {
   --ink: #17283b;
   --muted: #718096;
   --line: #e4e9ef;
   --paper: #f5f7f9;
   --teal: #087f75;
   --teal-dark: #06675f;
   --violet: #7658d6;
   --blue: #3478c8;
}

.stApp {
   background:
       radial-gradient(ellipse at 82% 0%, rgba(201, 230, 225, .32), transparent 30rem),
       var(--paper);
   color: var(--ink);
   font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.block-container {
   max-width: 1320px;
   padding: 2rem 2.5rem 3rem;
}

[data-testid="stAppSkipLink"],
a[data-testid="stAppSkipLink"],
[data-testid="stHeader"],
[data-testid="stToolbar"] {
   display: none !important;
}

h1, h2, h3, p, label, .stMarkdown {
   color: var(--ink);
}

h1 {
   font-size: 2.15rem !important;
   font-weight: 750 !important;
   letter-spacing: -.045em;
}

h2 {
   font-size: 1.45rem !important;
   font-weight: 720 !important;
   letter-spacing: -.025em;
}

h3 {
   font-size: 1rem !important;
   font-weight: 700 !important;
}

[data-testid="stSidebar"] {
   background: #142438;
   border-right: 1px solid #263a50;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
   color: #e5edf5;
}

[data-testid="stSidebar"] h2 {
   font-size: 1.05rem !important;
   letter-spacing: .04em;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
   color: #9eb0c3;
}

[data-testid="stSidebar"] hr {
   border-color: #30445a;
}

[data-testid="stSidebar"] [data-testid="stCode"] {
   background: #1d334a;
   border: 1px solid #38516a;
   border-radius: 9px;
}

.hero {
   position: relative;
   overflow: hidden;
   padding: 2rem 2.2rem;
   margin: .25rem 0 1.8rem;
   border: 1px solid #254159;
   border-radius: 20px;
   background: linear-gradient(115deg, #142a40 0%, #1b3c52 60%, #23534f 120%);
   box-shadow: 0 16px 38px rgba(27, 49, 68, .12);
}

.hero:after {
   content: "";
   position: absolute;
   width: 240px;
   height: 240px;
   right: -54px;
   top: -115px;
   border: 1px solid rgba(202, 241, 226, .18);
   border-radius: 50%;
   box-shadow: 0 0 0 28px rgba(202, 241, 226, .035), 0 0 0 58px rgba(202, 241, 226, .025);
}

.hero-eyebrow {
   margin-bottom: .65rem;
   color: #a9ddd0;
   font-size: .72rem;
   font-weight: 750;
   letter-spacing: .16em;
   text-transform: uppercase;
}

.hero-title {
   margin: 0;
   color: #f7fbff;
   font-size: clamp(1.75rem, 3vw, 2.6rem);
   font-weight: 760;
   letter-spacing: -.05em;
   line-height: 1.12;
}

.hero-copy {
   max-width: 660px;
   margin: .8rem 0 0;
   color: #c6d5e0;
   font-size: .98rem;
   line-height: 1.65;
}

.hero-tags {
   display: flex;
   flex-wrap: wrap;
   gap: .55rem;
   margin-top: 1.2rem;
}

.hero-tag {
   padding: .36rem .68rem;
   border: 1px solid rgba(219, 239, 236, .19);
   border-radius: 999px;
   background: rgba(235, 250, 247, .08);
   color: #e4f3ef;
   font-size: .72rem;
   font-weight: 650;
}

.section-kicker {
   margin-bottom: .3rem;
   color: var(--teal);
   font-size: .7rem;
   font-weight: 800;
   letter-spacing: .14em;
   text-transform: uppercase;
}

.section-intro {
   margin-bottom: 1rem;
   color: var(--muted);
   font-size: .9rem;
}

div[data-testid="column"]:has([data-testid="stTextArea"]) {
   padding: 1.2rem 1.25rem 1rem;
   border: 1px solid var(--line);
   border-radius: 16px;
   background: rgba(255, 255, 255, .86);
   box-shadow: 0 5px 18px rgba(32, 54, 75, .045);
}

div[data-testid="column"]:has([data-testid="stTextArea"]) h3 {
   margin-top: .1rem;
   margin-bottom: .2rem;
}

div[data-testid="column"]:has([data-testid="stTextArea"]) [data-testid="stCaptionContainer"] {
   color: var(--muted);
   font-size: .8rem;
}

.stTextArea textarea {
   background: #fbfcfd !important;
   color: var(--ink) !important;
   -webkit-text-fill-color: var(--ink) !important;
   border: 1px solid #dce3e9 !important;
   border-radius: 11px !important;
   padding: 13px 14px !important;
   font-size: .91rem !important;
   line-height: 1.6 !important;
   transition: border-color .16s ease, box-shadow .16s ease;
}

.stTextArea textarea:focus {
   border-color: #55a69c !important;
   box-shadow: 0 0 0 3px rgba(8, 127, 117, .12) !important;
}

.stTextArea textarea:disabled {
   background: #f7f9fb !important;
   color: #35485b !important;
   -webkit-text-fill-color: #35485b !important;
   opacity: 1 !important;
}

.stButton button {
   min-height: 42px;
   border: 1px solid #dce3e9;
   border-radius: 10px;
   background: #fff;
   color: #42566a;
   font-size: .84rem;
   font-weight: 680;
   transition: transform .16s ease, box-shadow .16s ease, background .16s ease;
}

.stButton button:hover {
   border-color: #9fc9c3;
   background: #f4fbf9;
   color: var(--teal-dark);
   box-shadow: 0 4px 12px rgba(25, 73, 78, .08);
   transform: translateY(-1px);
}

.stButton button[kind="primary"] {
   min-height: 52px;
   border: 1px solid var(--teal);
   background: var(--teal);
   color: #fff;
   font-size: .95rem;
   box-shadow: 0 8px 18px rgba(8, 127, 117, .18);
}

.stButton button[kind="primary"]:hover {
   border-color: var(--teal-dark);
   background: var(--teal-dark);
   color: #fff;
   box-shadow: 0 10px 22px rgba(8, 127, 117, .23);
}

div[data-testid="stAlert"] {
   border-radius: 12px;
}

[data-testid="stMetric"] {
   padding: 1rem 1.1rem;
   border: 1px solid var(--line);
   border-radius: 14px;
   background: #fff;
}

[data-testid="stMetricLabel"] {
   color: var(--muted) !important;
}

[data-testid="stMetricValue"] {
   color: var(--ink) !important;
   font-weight: 750;
}

[data-testid="stTable"] {
   overflow: hidden;
   border: 1px solid var(--line);
   border-radius: 13px;
   background: #fff;
}

[data-testid="stTable"] thead tr th {
   background: #edf4f4;
   color: #31485b;
   font-weight: 700;
}

hr {
   margin: 1.6rem 0 !important;
   border-color: var(--line);
}

@media (max-width: 720px) {
   .block-container {
       padding: 1rem 1rem 2rem;
   }

   .hero {
       padding: 1.5rem;
       border-radius: 15px;
   }
}
</style>
""", unsafe_allow_html=True)


# ---------- Default Prompts ----------
BASELINE_DEFAULT = "Explain Artificial Intelligence."

ENHANCED_DEFAULT = (
    "Explain Artificial Intelligence in simple English. "
    "Give exactly 5 numbered points. Each point must have "
    "a heading and a short explanation. Include one real-world "
    "example and finish with a one-sentence conclusion."
)


# ---------- Session State ----------
defaults = {
    "baseline_input": BASELINE_DEFAULT,
    "enhanced_input": ENHANCED_DEFAULT,
    "baseline_output": "",
    "enhanced_output": "",
    "comparison_done": False,
    "a_relevant": False,
    "a_clear": False,
    "a_complete": False,
    "b_relevant": False,
    "b_clear": False,
    "b_structure": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- Clear Functions ----------
def clear_baseline():
    st.session_state.baseline_input = ""
    st.session_state.baseline_output = ""
    st.session_state.comparison_done = False


def clear_enhanced():
    st.session_state.enhanced_input = ""
    st.session_state.enhanced_output = ""
    st.session_state.comparison_done = False


def clear_all():
    st.session_state.baseline_input = ""
    st.session_state.enhanced_input = ""
    st.session_state.baseline_output = ""
    st.session_state.enhanced_output = ""
    st.session_state.comparison_done = False

    for key in [
        "a_relevant", "a_clear", "a_complete",
        "b_relevant", "b_clear", "b_structure"
    ]:
        st.session_state[key] = False


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## ✳ PROMPT LAB")
    st.caption("GENERATIVE AI  /  EXPERIMENT 02")
    st.divider()

    st.markdown("### The experiment")
    st.write(
        "Study how prompt instructions affect the structure, "
        "clarity and completeness of AI-generated answers."
    )

    st.markdown("### Local model")
    st.code("llama3.2:1b", language="text")
    st.caption("Runtime: Local Ollama")

    if st.button("Test Connection", use_container_width=True):
        connected, message = check_connection()

        if connected:
            st.success(message)
        else:
            st.error(message)

    st.divider()

    st.button(
        "Reset All Panels",
        on_click=clear_all,
        use_container_width=True
    )


# ---------- Experiment Header ----------
st.markdown("""
<section class="hero">
    <div class="hero-eyebrow">Generative AI · Experiment 02</div>
    <h1 class="hero-title">A better prompt changes the answer.</h1>
    <p class="hero-copy">
        Run the same idea through two prompts, then compare how clear,
        complete, and well-structured each response becomes.
    </p>
    <div class="hero-tags">
        <span class="hero-tag">01 &nbsp; Control prompt</span>
        <span class="hero-tag">02 &nbsp; Enhanced prompt</span>
        <span class="hero-tag">Local inference</span>
    </div>
</section>
""", unsafe_allow_html=True)

# ---------- Prompt Input Panels ----------
st.markdown('<div class="section-kicker">01 / Compose</div>', unsafe_allow_html=True)
st.markdown("## Set up your prompts")
st.markdown(
    '<p class="section-intro">Keep the topic consistent. Change the instructions.</p>',
    unsafe_allow_html=True
)

left, right = st.columns(2, gap="large")

with left:
    st.markdown("### 01 &nbsp; Baseline")
    st.caption("A simple instruction — your control.")

    st.text_area(
        "Baseline prompt",
        key="baseline_input",
        height=145,
        label_visibility="collapsed",
        placeholder="Enter your baseline prompt..."
    )

    st.button(
        "✕ Clear Baseline",
        key="clear_a",
        on_click=clear_baseline,
        use_container_width=True
    )


with right:
    st.markdown("### 02 &nbsp; Enhanced")
    st.caption("More guidance — your experiment.")

    st.text_area(
        "Enhanced prompt",
        key="enhanced_input",
        height=145,
        label_visibility="collapsed",
        placeholder="Enter your enhanced prompt..."
    )

    st.button(
        "✕ Clear Enhanced",
        key="clear_b",
        on_click=clear_enhanced,
        use_container_width=True
    )


# ---------- Generate and Compare ----------
st.markdown("---")

_, compare_col, _ = st.columns([1, 2, 1])

with compare_col:
    compare_clicked = st.button(
        "Generate both responses  →",
        key="generate_compare",
        use_container_width=True,
        type="primary"
    )


if compare_clicked:
    baseline = st.session_state.baseline_input.strip()
    enhanced = st.session_state.enhanced_input.strip()

    if not baseline or not enhanced:
        st.warning(
            "Please fill in both prompt areas before generating."
        )
    else:
        try:
            with st.spinner(
                "Generating baseline and enhanced responses..."
            ):
                baseline_answer, enhanced_answer = compare_responses(
                    baseline,
                    enhanced
                )

            st.session_state.baseline_output = baseline_answer
            st.session_state.enhanced_output = enhanced_answer
            st.session_state.comparison_done = True

            st.success(
                "Both responses generated successfully!"
            )

        except Exception as error:
            st.error(f"Generation failed: {error}")


# ---------- Output Panels ----------
st.markdown("---")
st.markdown('<div class="section-kicker">02 / Review</div>', unsafe_allow_html=True)
st.markdown("## Generated responses")
st.markdown(
    '<p class="section-intro">Read the outputs side by side before comparing their quality.</p>',
    unsafe_allow_html=True
)

out_a, out_b = st.columns(2, gap="large")

with out_a:
    st.markdown("### Baseline response")

    st.text_area(
        "Baseline result",
        key="baseline_output",
        height=290,
        placeholder="Baseline response will appear here...",
        disabled=True,
        label_visibility="collapsed"
    )

with out_b:
    st.markdown("### Enhanced response")

    st.text_area(
        "Enhanced result",
        key="enhanced_output",
        height=290,
        placeholder="Enhanced response will appear here...",
        disabled=True,
        label_visibility="collapsed"
    )
    
# ---------- Response Comparison ----------
if st.session_state.comparison_done:
    st.markdown("---")
    st.markdown('<div class="section-kicker">03 / Compare</div>', unsafe_allow_html=True)
    st.markdown("## How did the prompts perform?")

    st.caption(
        "Compare both responses based on relevance, "
        "completeness, and writing style."
    )

    baseline_answer = st.session_state.baseline_output
    enhanced_answer = st.session_state.enhanced_output

    def evaluate_response(answer, prompt, is_enhanced=False):
        text = answer.strip()
        words = text.split()
        sentences = [
            s for s in re.split(r'[.!?]+', text) if s.strip()
        ]

        # Relevance: check for overlap between prompt keywords
        # and the generated response.
        stop_words = {
            "the", "a", "an", "is", "are", "in", "on", "of",
            "to", "and", "or", "for", "with", "give", "explain",
            "include", "finish", "each", "must", "have", "one",
            "short", "simple", "english", "exactly"
        }

        keywords = {
            word.lower().strip(".,!?():;")
            for word in prompt.split()
            if word.lower().strip(".,!?():;") not in stop_words
            and len(word.strip(".,!?():;")) > 2
        }

        answer_words = {
            word.lower().strip(".,!?():;")
            for word in text.split()
        }

        overlap = (
            len(keywords & answer_words) / len(keywords)
            if keywords else 0
        )

        relevance = (
            "High" if overlap >= 0.5
            else "Medium" if overlap >= 0.25
            else "Low"
        )

        # Completeness: heuristic based on response detail.
        if len(words) >= 80 and len(sentences) >= 4:
            completeness = "High"
        elif len(words) >= 35 and len(sentences) >= 2:
            completeness = "Medium"
        else:
            completeness = "Low"

        # Style: check structure and readability.
        numbered_points = len(
            re.findall(r'(?m)^\s*\d+[\.\)]\s+', text)
        )
        has_headings = bool(
            re.search(r'(?m)^\s*#{1,6}\s+', text)
            or re.search(r'(?m)^\s*\d+[\.\)]\s+\S+', text)
        )

        if is_enhanced:
            if numbered_points >= 5 and has_headings:
                style = "High"
            elif numbered_points >= 2 or has_headings:
                style = "Medium"
            else:
                style = "Low"
        else:
            if has_headings or numbered_points >= 2:
                style = "High"
            elif len(sentences) >= 3:
                style = "Medium"
            else:
                style = "Low"

        return relevance, completeness, style

    baseline_scores = evaluate_response(
        baseline_answer,
        st.session_state.baseline_input
    )

    enhanced_scores = evaluate_response(
        enhanced_answer,
        st.session_state.enhanced_input,
        is_enhanced=True
    )

    st.markdown("### Evaluation breakdown")

    st.table({
        "Evaluation Criteria": [
            "Relevance",
            "Completeness",
            "Style"
        ],
        "Baseline Response": list(baseline_scores),
        "Enhanced Response": list(enhanced_scores)
    })

    # Summary of the comparison
    score_values = {"Low": 1, "Medium": 2, "High": 3}

    baseline_total = sum(
        score_values[score] for score in baseline_scores
    )
    enhanced_total = sum(
        score_values[score] for score in enhanced_scores
    )

    st.markdown("### Overall score")

    col_a, col_b = st.columns(2)

    with col_a:
        st.metric(
            "Baseline Score",
            f"{baseline_total}/9"
        )

    with col_b:
        st.metric(
            "Enhanced Score",
            f"{enhanced_total}/9",
            delta=enhanced_total - baseline_total
        )

    if enhanced_total > baseline_total:
        st.success(
            "The enhanced response scored higher using these "
            "automatic text-based checks."
        )
    elif enhanced_total < baseline_total:
        st.info(
            "The baseline response scored higher using these "
            "automatic text-based checks."
        )
    else:
        st.info(
            "Both responses received the same score using these "
            "automatic text-based checks."
        )

    st.caption(
        "Note: These are approximate, rule-based scores based on "
        "keyword overlap, response length, and formatting. They "
        "do not fully measure meaning or factual correctness."
    )





# ---------- Footer ----------
st.divider()
st.caption("GENERATIVE AI LAB  •  EXPERIMENT 02")
