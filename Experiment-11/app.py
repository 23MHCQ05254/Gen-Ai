
import streamlit as st
from main import summarize_text, check_chain, LCELChainError

st.set_page_config(
    page_title="Experiment 11 | LCEL Chain",
    page_icon="🔗",
    layout="wide"
)

# Colourful interface styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f8f7ff;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.header {
    background: linear-gradient(115deg, #4338ca, #a21caf, #e11d48, #f97316);
    padding: 30px;
    border-radius: 20px;
    color: white;
    margin-bottom: 26px;
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.18);
}

.header h1 {
    color: white;
    font-size: 32px;
    font-weight: 800;
    margin-bottom: 10px;
}

.header p {
    color: #fff1f7;
    margin-bottom: 4px;
}

.section-title {
    font-size: 21px;
    font-weight: 800;
    color: #6d28d9;
    margin-top: 22px;
    margin-bottom: 14px;
}

.workflow-title {
    font-size: 20px;
    font-weight: 800;
    color: #6d28d9;
    margin-bottom: 18px;
}

.workflow-step {
    padding: 16px 8px;
    border-radius: 14px;
    text-align: center;
    color: white;
    font-weight: 700;
    margin-bottom: 8px;
}

.workflow-step small {
    font-weight: 500;
    font-size: 12px;
}

.step-prompt {
    background: linear-gradient(135deg, #0891b2, #06b6d4);
}

.step-model {
    background: linear-gradient(135deg, #ea580c, #fb923c);
}

.step-parser {
    background: linear-gradient(135deg, #9333ea, #c084fc);
}

.workflow-arrow {
    text-align: center;
    font-size: 24px;
    color: #db2777;
    font-weight: 800;
    line-height: 1.4;
}

.stButton button {
    min-height: 45px;
    border-radius: 12px;
    font-weight: 700;
}

footer, #MainMenu {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# Header
st.markdown("""
<div class="header">
    <h1>🔗 LCEL Chain Studio</h1>
    <p>Experiment 11 · Building a Simple LCEL Chain</p>
    <p>Transform lengthy text into a clear, concise summary.</p>
</div>
""", unsafe_allow_html=True)


# Default input
if "exp11_input" not in st.session_state:
    st.session_state.exp11_input = """
Artificial Intelligence (AI) is one of the most important technological
developments in the modern world. It enables computers and machines to
perform tasks that normally require human intelligence, such as learning,
problem-solving, decision-making, language understanding, and recognizing
images. AI is widely used in healthcare to help doctors analyze medical
images, identify diseases, and improve patient care. In education, AI-based
applications provide personalized learning experiences, assist students
with their doubts, and help teachers evaluate student performance. In
transportation, AI supports traffic management, route planning, and the
development of self-driving vehicles. Businesses use AI to understand
customer preferences, automate repetitive tasks, improve productivity,
and make better decisions using large amounts of data. AI-powered virtual
assistants and chatbots help people obtain information and complete tasks
quickly. However, the increasing use of AI also creates challenges related
to data privacy, security, employment, and ethical decision-making.
Therefore, AI systems must be developed and used responsibly. Human
supervision, transparency, and proper regulations are important to ensure
that AI benefits society. When used carefully, Artificial Intelligence can
support innovation, solve complex problems, and improve the quality of
human life in many different fields.
""".strip()

if "exp11_output" not in st.session_state:
    st.session_state.exp11_output = ""

if "exp11_status" not in st.session_state:
    st.session_state.exp11_status = None

if "exp11_test_type" not in st.session_state:
    st.session_state.exp11_test_type = None


# Input section
st.markdown(
    '<div class="section-title">① Input Text</div>',
    unsafe_allow_html=True
)

with st.container(border=True):
    input_col, workflow_col = st.columns([3, 1])

    with input_col:
        st.text_area(
            "Text to summarize",
            key="exp11_input",
            height=240,
            placeholder="Enter the text you want to summarize..."
        )

    # Visual workflow replaces Chain Details
    with workflow_col:
        st.markdown(
            '<div class="workflow-title">⚡ Chain Workflow</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="workflow-step step-prompt">
            📝 PROMPT TEMPLATE<br>
            <small>Prepare instructions</small>
        </div>

        <div class="workflow-arrow">↓</div>

        <div class="workflow-step step-model">
            🤖 OLLAMA LLM<br>
            <small>Generate summary</small>
        </div>

        <div class="workflow-arrow">↓</div>

        <div class="workflow-step step-parser">
            📄 OUTPUT PARSER<br>
            <small>Format the result</small>
        </div>
        """, unsafe_allow_html=True)

        st.caption("Three connected steps · One LCEL chain")


# Action buttons
run_col, test_col, clear_col = st.columns([1.5, 1.5, 1])

with run_col:
    run_clicked = st.button(
        "▶ Run LCEL Chain",
        type="primary",
        use_container_width=True
    )

with test_col:
    test_clicked = st.button(
        "🧪 Test End-to-End",
        use_container_width=True
    )

with clear_col:
    clear_clicked = st.button(
        "✕ Clear",
        use_container_width=True
    )


# Clear input and output
if clear_clicked:
    st.session_state.exp11_input = ""
    st.session_state.exp11_output = ""
    st.session_state.exp11_status = None
    st.session_state.exp11_test_type = None
    st.rerun()


# Run chain with entered text
if run_clicked:
    st.session_state.exp11_test_type = "run"

    if not st.session_state.exp11_input.strip():
        st.session_state.exp11_output = ""
        st.session_state.exp11_status = (
            False,
            "Please enter text before running the chain."
        )
    else:
        try:
            with st.spinner("Executing LCEL chain..."):
                output = summarize_text(
                    st.session_state.exp11_input
                )

            st.session_state.exp11_output = output
            st.session_state.exp11_status = (
                True,
                "LCEL chain executed successfully."
            )

        except Exception as error:
            st.session_state.exp11_output = ""
            st.session_state.exp11_status = (
                False,
                str(error)
            )


# Test the complete chain with sample text
if test_clicked:
    st.session_state.exp11_test_type = "test"

    try:
        with st.spinner(
            "Testing prompt, model, and output parser..."
        ):
            output = check_chain()

        st.session_state.exp11_output = output
        st.session_state.exp11_status = (
            True,
            "PASS — End-to-end LCEL test completed successfully."
        )

    except Exception as error:
        st.session_state.exp11_output = ""
        st.session_state.exp11_status = (
            False,
            f"FAIL — End-to-end test failed: {error}"
        )


# Execution test result
if st.session_state.exp11_status:
    passed, message = st.session_state.exp11_status

    st.markdown(
        '<div class="section-title">② Execution Test Result</div>',
        unsafe_allow_html=True
    )

    with st.container(border=True):
        if passed:
            st.success(message)

            if st.session_state.exp11_test_type == "test":
                st.markdown("**Workflow Verification**")
                st.write("✓ Prompt template processed the input.")
                st.write("✓ Ollama language model generated a response.")
                st.write("✓ Output parser returned readable text.")
                st.write("✓ End-to-end chain execution completed.")
        else:
            st.error(message)


# Generated summary
st.markdown(
    '<div class="section-title">③ Generated Summary</div>',
    unsafe_allow_html=True
)

with st.container(border=True):
    st.markdown("**Model Output**")

    if st.session_state.exp11_output:
        st.write(st.session_state.exp11_output)
    else:
        st.caption(
            "Your generated summary will appear here after execution."
        )


