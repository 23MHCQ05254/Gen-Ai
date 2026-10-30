
import streamlit as st
from main import run_experiment, OllamaError

st.set_page_config(
    page_title="Experiment 10 | Reasoning Lab",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f4f7fb;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

.hero {
    background: linear-gradient(120deg, #172554, #2563eb);
    color: white;
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 24px;
}

.hero h1 {
    color: white;
    font-size: 30px;
    margin-bottom: 8px;
}

.hero p {
    color: #dbeafe;
    margin-bottom: 0;
}

.section-title {
    font-size: 21px;
    font-weight: 750;
    color: #172554;
    margin-top: 24px;
    margin-bottom: 14px;
}

.method-card {
    background: white;
    border: 1px solid #dbe4f0;
    border-radius: 14px;
    padding: 17px;
    min-height: 125px;
}

.method-card h4 {
    color: #1e3a8a;
    margin-top: 0;
    margin-bottom: 8px;
}

.method-card p {
    color: #475569;
    font-size: 13px;
    margin-bottom: 0;
}

.result-heading {
    font-size: 18px;
    font-weight: 750;
    color: #1e3a8a;
    margin-bottom: 10px;
}

.stButton button {
    border-radius: 9px;
    font-weight: 600;
    min-height: 42px;
}

footer {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# Header
st.markdown("""
<div class="hero">
    <h1>🧠 Reasoning Lab</h1>
    <p>Experiment 10: Chain-of-Thought and Task Decomposition</p>
    <p>Compare direct answering, step-by-step prompting, and task decomposition.</p>
</div>
""", unsafe_allow_html=True)


# Session state
if "exp10_problem" not in st.session_state:
    st.session_state.exp10_problem = (
        "Ava is older than Ben. Ben is older than Cara. "
        "Who is the youngest person?"
    )

if "exp10_expected" not in st.session_state:
    st.session_state.exp10_expected = "Cara"

if "exp10_result" not in st.session_state:
    st.session_state.exp10_result = None

if "exp10_error" not in st.session_state:
    st.session_state.exp10_error = None


def clear_all():
    st.session_state.exp10_problem = ""
    st.session_state.exp10_expected = ""
    st.session_state.exp10_result = None
    st.session_state.exp10_error = None



# Input section
st.markdown(
    '<div class="section-title">① Enter Your Problem</div>',
    unsafe_allow_html=True
)

with st.container(border=True):
    problem_col, expected_col = st.columns([3, 1])

    with problem_col:
        problem = st.text_area(
            "Multi-step problem",
            key="exp10_problem",
            height=150,
            placeholder="Enter a logic puzzle or multi-step problem..."
        )

    with expected_col:
        expected_answer = st.text_input(
            "Expected Answer",
            key="exp10_expected",
            placeholder="Correct answer"
        )

    st.caption(
        "Enter a problem and optionally provide the correct answer "
        "to check the results."
    )
# Method cards
st.markdown(
    '<div class="section-title">② Reasoning Methods</div>',
    unsafe_allow_html=True
)

method1, method2, method3 = st.columns(3)

with method1:
    st.markdown("""
    <div class="method-card">
        <h4>⚡ Direct Answer</h4>
        <p>Ask the model to answer the problem directly.</p>
    </div>
    """, unsafe_allow_html=True)

with method2:
    st.markdown("""
    <div class="method-card">
        <h4>🔗 Zero-Shot CoT</h4>
        <p>Ask the model for a brief step-by-step explanation.</p>
    </div>
    """, unsafe_allow_html=True)

with method3:
    st.markdown("""
    <div class="method-card">
        <h4>🧩 Task Decomposition</h4>
        <p>Break the problem into smaller questions and combine the answers.</p>
    </div>
    """, unsafe_allow_html=True)


# Buttons
st.markdown("")

button1, button2, space = st.columns([1.5, 1, 4])

with button1:
    run_clicked = st.button(
        "▶ Run Comparison",
        type="primary",
        use_container_width=True
    )

with button2:
    st.button(
        "✕ Clear All",
        on_click=clear_all,
        use_container_width=True
    )


# Run experiment
if run_clicked:
    if not st.session_state.exp10_problem.strip():
        st.session_state.exp10_error = "Please enter a problem first."
        st.session_state.exp10_result = None
    else:
        try:
            with st.spinner(
                "Running all three reasoning methods with Ollama..."
            ):
                st.session_state.exp10_result = run_experiment(
                    st.session_state.exp10_problem.strip(),
                    st.session_state.exp10_expected.strip()
                )
                st.session_state.exp10_error = None

        except Exception as error:
            st.session_state.exp10_result = None
            st.session_state.exp10_error = str(error)


# Error display
if st.session_state.exp10_error:
    st.error(st.session_state.exp10_error)


# Results: only three result boxes, no Comparison Summary
if st.session_state.exp10_result:
    result = st.session_state.exp10_result
    comparison = result.get("comparison", {})

    st.markdown(
        '<div class="section-title">③ Results</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3, gap="medium")

    # Direct Answer
    with col1:
        st.markdown(
            '<div class="result-heading">⚡ Direct Answer</div>',
            unsafe_allow_html=True
        )

        with st.container(border=True):
            st.markdown("**Model Output**")
            st.write(result.get("direct", "No answer generated."))

            direct_match = comparison.get("direct_match")

            if direct_match is not None:
                st.divider()
                if direct_match:
                    st.success("Matches the expected answer")
                else:
                    st.warning("Does not match the expected answer")

    # Zero-Shot CoT
    with col2:
        st.markdown(
            '<div class="result-heading">🔗 Zero-Shot CoT</div>',
            unsafe_allow_html=True
        )

        with st.container(border=True):
            st.markdown("**Step-by-Step Output**")
            st.write(result.get("cot", "No answer generated."))

            cot_match = comparison.get("cot_match")

            if cot_match is not None:
                st.divider()
                if cot_match:
                    st.success("Matches the expected answer")
                else:
                    st.warning("Does not match the expected answer")

    # Task Decomposition
    with col3:
        st.markdown(
            '<div class="result-heading">🧩 Task Decomposition</div>',
            unsafe_allow_html=True
        )

        with st.container(border=True):
            decomposition = result.get("decomposition", {})
            partial_answers = decomposition.get("partial_answers", [])

            st.markdown("**Sub-questions and Answers**")

            if partial_answers:
                for index, item in enumerate(partial_answers, start=1):
                    if isinstance(item, dict):
                        question = item.get("question", "")
                        answer = item.get("answer", "")

                        st.markdown(f"**Step {index}:** {question}")
                        st.write(answer)
                    else:
                        st.markdown(f"**Step {index}**")
                        st.write(str(item))

                    if index < len(partial_answers):
                        st.divider()
            else:
                st.write("No intermediate answers generated.")

            st.divider()
            st.markdown("**Combined Final Answer**")

            final_answer = (
                decomposition.get("final_answer")
                or decomposition.get("combined_answer")
                or decomposition.get("answer")
                or "No final answer generated."
            )
            st.write(final_answer)

            decomposed_match = comparison.get("decomposed_match")

            if decomposed_match is not None:
                st.divider()
                if decomposed_match:
                    st.success("Matches the expected answer")
                else:
                    st.warning("Does not match the expected answer")



