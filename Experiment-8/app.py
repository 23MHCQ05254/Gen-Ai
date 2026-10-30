
import streamlit as st
import html
from main import run_experiment, check_connection, verify_structure

st.set_page_config(
    page_title="Experiment 8 | Structured Format Prompting",
    page_icon="🌅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- SUNSET THEME ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #fff4e8, #f9e7ef, #eee7ff);
    color: #35233f;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    background: linear-gradient(120deg, #54245f, #9d3f73, #f07854);
    padding: 30px;
    border-radius: 22px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 10px 28px rgba(99,38,91,.18);
}

.hero h1 {
    color: white;
    font-size: 32px;
    font-weight: 800;
}

.hero p {
    color: #fff0f3;
    margin-bottom: 4px;
}

.section-title {
    color: #672d68;
    font-size: 21px;
    font-weight: 700;
    margin-bottom: 14px;
}

.input-card {
    background: rgba(255,255,255,.78);
    border: 1px solid #ead5e8;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 20px;
}

.stTextArea textarea {
    background: #fffaf7 !important;
    color: #38263d !important;
    border: 1px solid #dfb9d5 !important;
    border-radius: 12px !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: #fffaf7;
    border-color: #dfb9d5;
    border-radius: 10px;
}

div.stButton > button {
    border-radius: 12px;
    min-height: 44px;
    font-weight: 600;
    border: none;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #87366f, #e66d58);
    color: white;
}

/* Actual answer boxes */

.result-box {
    background: #fffaf7;
    border: 1px solid #e6c7df;
    border-left: 5px solid #d96569;
    border-radius: 14px;
    padding: 20px;
    min-height: 260px;
    height: auto;
    overflow-wrap: anywhere;
    white-space: normal;
}

.verify-box {
    background: #fbf3fc;
    border: 1px solid #d9b5df;
    border-left: 5px solid #87366f;
    border-radius: 14px;
    padding: 20px;
    min-height: 260px;
    height: auto;
    overflow-wrap: anywhere;
}

.result-box ul,
.result-box ol {
    padding-left: 24px;
}

.result-box table {
    width: 100%;
    border-collapse: collapse;
}

.result-box th,
.result-box td {
    border: 1px solid #dfb9d5;
    padding: 8px;
    text-align: left;
}

.footer {
    text-align: center;
    color: #875e83;
    font-size: 13px;
    padding: 20px 0;
}

#MainMenu, footer, header {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>🌅 Structured Format Prompting</h1>
    <p>Experiment 8 · Generative AI Lab</p>
    <p>Generate structured responses and verify the requested format.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------

if "topic_input" not in st.session_state:
    st.session_state.topic_input = "Benefits of daily exercise"

if "experiment8_result" not in st.session_state:
    st.session_state.experiment8_result = None

if "experiment8_error" not in st.session_state:
    st.session_state.experiment8_error = None

if "experiment8_verified" not in st.session_state:
    st.session_state.experiment8_verified = None

if "experiment8_format" not in st.session_state:
    st.session_state.experiment8_format = "Bullet List"

if "experiment8_count" not in st.session_state:
    st.session_state.experiment8_count = 3


def clear_all():
    st.session_state.topic_input = ""
    st.session_state.experiment8_result = None
    st.session_state.experiment8_error = None
    st.session_state.experiment8_verified = None


# ---------------- INPUT SECTION ----------------

st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown(
    '<div class="section-title">✍️ Enter Your Topic</div>',
    unsafe_allow_html=True
)

left_col, empty_col = st.columns([1, 1.1])

with left_col:
    topic = st.text_area(
        "Enter the topic",
        key="topic_input",
        height=110,
        placeholder="Enter a topic for the AI to explain..."
    )

    output_format = st.selectbox(
        "Select the required output format",
        [
            "Bullet List",
            "Numbered List",
            "Markdown Table",
            "Headings and Points"
        ],
        key="experiment8_format"
    )

    item_count = st.slider(
        "Required number of items",
        min_value=2,
        max_value=10,
        value=3,
        key="experiment8_count"
    )

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BUTTONS ----------------

generate_col, verify_col, clear_col = st.columns(3)

with generate_col:
    generate_clicked = st.button(
        "✨ Generate Answer",
        type="primary",
        use_container_width=True
    )

with verify_col:
    verify_clicked = st.button(
        "✓ Verify Structure",
        use_container_width=True
    )

with clear_col:
    st.button(
        "🗑️ Clear All",
        on_click=clear_all,
        use_container_width=True
    )

# ---------------- GENERATE ----------------

if generate_clicked:
    if not topic.strip():
        st.session_state.experiment8_error = "Please enter a topic first."
        st.session_state.experiment8_result = None
        st.session_state.experiment8_verified = None
    else:
        try:
            with st.spinner("Generating your structured answer..."):
                check_connection()

                result = run_experiment(
                    topic=topic.strip(),
                    output_format=output_format,
                    count=item_count
                )

                if isinstance(result, dict):
                    answer = (
                        result.get("answer")
                        or result.get("output")
                        or result.get("response")
                        or str(result)
                    )
                else:
                    answer = str(result)

                st.session_state.experiment8_result = answer
                st.session_state.experiment8_error = None
                st.session_state.experiment8_verified = None

        except Exception as error:
            st.session_state.experiment8_error = str(error)
            st.session_state.experiment8_result = None
            st.session_state.experiment8_verified = None

# ---------------- VERIFY ----------------

if verify_clicked:
    answer = st.session_state.experiment8_result

    if not answer:
        st.session_state.experiment8_error = (
            "Generate an answer first, then verify its structure."
        )
    else:
        try:
            st.session_state.experiment8_verified = verify_structure(
                answer,
                output_format,
                item_count
            )
            st.session_state.experiment8_error = None
        except Exception as error:
            st.session_state.experiment8_verified = {
                "passed": False,
                "message": str(error)
            }

# ---------------- ERRORS ----------------

if st.session_state.experiment8_error:
    st.error(st.session_state.experiment8_error)

# ---------------- RESULTS SIDE BY SIDE ----------------

answer = st.session_state.experiment8_result

if answer:
    answer_col, verified_col = st.columns(2, gap="large")

    # LEFT: ANSWER IS RENDERED INSIDE ONE HTML BOX
    with answer_col:
        st.markdown(
            '<div class="section-title">📝 Generated Answer</div>',
            unsafe_allow_html=True
        )

        # Escape HTML first so model output cannot break the box.
        # Convert common Markdown structures to readable HTML.
        # Using a single HTML block keeps the response inside the box.
        import re

        safe_answer = html.escape(answer.strip())

        lines = safe_answer.splitlines()
        rendered_lines = []
        in_list = False
        list_type = None

        for line in lines:
            stripped = line.strip()

            bullet_match = re.match(r"^[-*•]\s+(.+)", stripped)
            numbered_match = re.match(r"^\d+[.)]\s+(.+)", stripped)

            if bullet_match or numbered_match:
                current_type = "ul" if bullet_match else "ol"

                if not in_list or current_type != list_type:
                    if in_list:
                        rendered_lines.append(f"</{list_type}>")
                    rendered_lines.append(f"<{current_type}>")
                    in_list = True
                    list_type = current_type

                item = bullet_match.group(1) if bullet_match else numbered_match.group(1)
                rendered_lines.append(f"<li>{item}</li>")
            else:
                if in_list:
                    rendered_lines.append(f"</{list_type}>")
                    in_list = False
                    list_type = None

                if stripped:
                    if stripped.startswith("### "):
                        rendered_lines.append(f"<h4>{stripped[4:]}</h4>")
                    elif stripped.startswith("## "):
                        rendered_lines.append(f"<h3>{stripped[3:]}</h3>")
                    elif stripped.startswith("# "):
                        rendered_lines.append(f"<h3>{stripped[2:]}</h3>")
                    else:
                        rendered_lines.append(f"<p>{stripped}</p>")

        if in_list:
            rendered_lines.append(f"</{list_type}>")

        answer_html = "\n".join(rendered_lines)

        st.markdown(
            f'<div class="result-box">{answer_html}</div>',
            unsafe_allow_html=True
        )

    # RIGHT: VERIFICATION IS INSIDE THE BOX
    with verified_col:
        st.markdown(
            '<div class="section-title">🔍 Verified Structure Response</div>',
            unsafe_allow_html=True
        )

        verification = st.session_state.experiment8_verified

        if verification is None:
            verification_html = (
                "<p>Click <b>Verify Structure</b> to check "
                "the generated answer.</p>"
            )
        else:
            if isinstance(verification, dict):
                passed = verification.get(
                    "passed",
                    verification.get("valid", False)
                )
                details = verification.get(
                    "message",
                    verification.get("details", "")
                )
            elif isinstance(verification, tuple):
                passed = bool(verification[0])
                details = (
                    str(verification[1])
                    if len(verification) > 1
                    else ""
                )
            else:
                passed = bool(verification)
                details = ""

            status = (
                "<h3 style='color:#205c34;'>"
                "✅ Structure Verification Passed</h3>"
                if passed
                else
                "<h3 style='color:#8b3c27;'>"
                "⚠️ Structure Verification Failed</h3>"
            )

            safe_details = html.escape(str(details))
            verification_html = (
                status
                + f"<p><b>Required format:</b> {html.escape(output_format)}</p>"
                + f"<p><b>Required number of items:</b> {item_count}</p>"
                + (f"<p>{safe_details}</p>" if details else "")
            )

        st.markdown(
            f'<div class="verify-box">{verification_html}</div>',
            unsafe_allow_html=True
        )
