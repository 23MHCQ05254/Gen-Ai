
import streamlit as st
import ollama
import html

from main import run_agent, MODEL

st.set_page_config(
    page_title="Simple LLM Agent",
    page_icon="🤖",
    layout="wide",
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #F0FDFA, #EFF6FF, #F5F3FF);
}

.block-container {
    max-width: 1000px;
    padding-top: 2rem;
}

.agent-header {
    background: linear-gradient(110deg, #0F766E, #2563EB, #7C3AED);
    padding: 25px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 25px;
    color: white;
}

.agent-header h1,
.agent-header p {
    color: white;
}

.result-box {
    background: #EDE9FE;
    color: #4C1D95;
    border: 1px solid #C4B5FD;
    border-radius: 12px;
    padding: 20px;
    min-height: 150px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    line-height: 1.7;
    font-size: 18px;
}
</style>

<div class="agent-header">
    <h1>🤖 Simple LLM Agent</h1>
    <p>Ask a question and get an intelligent answer</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Agent Settings")
    st.success("Local Ollama Model")
    st.code(MODEL)
    st.write("Registered Tool")
    st.code("calculator(operation, a, b)")
    st.caption("Runs locally using Ollama.")

if "agent_answer" not in st.session_state:
    st.session_state.agent_answer = ""

st.subheader("💬 Ask Your Agent")

examples = [
    "Calculate 5 multiplied by 3.",
    "Calculate 125 multiplied by 24.",
    "What is 945 divided by 9?",
    "Add 456 and 789.",
    "Explain what an LLM agent is.",
]

example = st.selectbox(
    "Choose an example",
    ["Select an example..."] + examples,
)

question = st.text_area(
    "Your question",
    value="" if example == "Select an example..." else example,
    height=110,
    placeholder="Example: Calculate 85 multiplied by 16.",
)

col1, col2 = st.columns(2)

with col1:
    run_clicked = st.button(
        "🚀 Run Agent",
        type="primary",
        use_container_width=True,
    )

with col2:
    clear_clicked = st.button(
        "🧹 Clear",
        use_container_width=True,
    )

if clear_clicked:
    st.session_state.agent_answer = ""
    st.rerun()

if run_clicked:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Agent is thinking..."):
                result = run_agent(question)

            st.session_state.agent_answer = result["answer"]

        except ollama.ResponseError as exc:
            st.error(f"Ollama model error: {exc}")

        except Exception as exc:
            st.error(
                f"Could not run the agent: {exc}\n\n"
                "Check that Ollama is running and the model is installed."
            )

st.subheader("📋 Answer")

if st.session_state.agent_answer:
    safe_answer = html.escape(str(st.session_state.agent_answer))

    st.markdown(
        f'<div class="result-box">'
        f'<strong>ANSWER : </strong>{safe_answer}'
        f'</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="result-box">'
        'Your answer will appear here.'
        '</div>',
        unsafe_allow_html=True,
    )
