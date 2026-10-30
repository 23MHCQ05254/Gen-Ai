
import streamlit as st
import pandas as pd

from main import (
    check_connection,
    generate_response,
    build_round_prompts,
    compare_responses,
    OllamaError
)

st.set_page_config(
    page_title="EXPERIMENT 3 · ITERATIVE PROMPT REFINEMENT",
    page_icon="🧪",
    layout="wide"
)

# ---------------- STYLE ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #10172A, #182746, #281B4D);
    color: #FFFFFF;
}
.block-container {
    max-width: 1550px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
h1, h2, h3, h4, p, label {
    color: #FFFFFF !important;
}
[data-testid="stCaptionContainer"] {
    color: #CBD5E8 !important;
}
div[data-testid="stTextArea"] textarea {
    background-color: #FFFFFF !important;
    color: #17213B !important;
    -webkit-text-fill-color: #17213B !important;
    border: 2px solid #A8B8E8 !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    opacity: 1 !important;
}
div[data-testid="stTextArea"] label {
    color: #FFFFFF !important;
}
div.stButton > button {
    background: linear-gradient(90deg, #7657FF, #16B9C8) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    min-height: 52px;
    font-weight: bold;
    font-size: 16px;
}
div.stButton > button:hover {
    filter: brightness(1.12);
}
.prompt-header {
    color: white;
    padding: 15px;
    min-height: 100px;
    border-radius: 12px 12px 0 0;
}
.purple { background: linear-gradient(120deg, #7657FF, #4934A5); }
.teal { background: linear-gradient(120deg, #11A6B5, #08717D); }
.orange { background: linear-gradient(120deg, #FF9B54, #C04D20); }
[data-testid="stDataFrame"] {
    background: white;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- STATE ----------------

defaults = {
    "prompt_a": (
        "Summarize the plot of the Shakespearean play Romeo and Juliet."
    ),
    "prompt_b": (
        "Summarize the plot of the Shakespearean play Romeo and Juliet "
        "in exactly two sentences using simple, clear English."
    ),
    "prompt_c": (
        "Summarize the plot of the Shakespearean play Romeo and Juliet "
        "in exactly two sentences using simple, clear English. "
        "Include the setting of Verona and the themes of love, "
        "family conflict, and tragedy."
    ),
    "response_box_1": "",
    "response_box_2": "",
    "response_box_3": "",
    "comparison_results": None,
    "comparison_requirements": None,
    "last_prompts": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------- MAIN HEADING ----------------

st.markdown("""
<div style="text-align:center; padding:20px 0 25px;">
    <h1 style="font-size:34px; color:white;">
        EXPERIMENT 3 · ITERATIVE PROMPT REFINEMENT
    </h1>
    <p style="color:#CBD5E8;">
        Generative AI Laboratory · Progressive Prompt Improvement
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------- PROMPT INPUTS ----------------

st.markdown("## 01 · Prompt Inputs")

a, b, c = st.columns(3, gap="medium")

with a:
    st.markdown("""
    <div class="prompt-header purple">
        <b>A. Minimal Instruction</b><br>
        <small>ROUND 1 · BASIC TASK</small>
    </div>
    """, unsafe_allow_html=True)
    st.text_area(
        "Prompt A",
        key="prompt_a",
        height=190,
        label_visibility="collapsed"
    )

with b:
    st.markdown("""
    <div class="prompt-header teal">
        <b>B. Length & Style Constraints</b><br>
        <small>ROUND 2 · FORMAT AND STYLE</small>
    </div>
    """, unsafe_allow_html=True)
    st.text_area(
        "Prompt B",
        key="prompt_b",
        height=190,
        label_visibility="collapsed"
    )

with c:
    st.markdown("""
    <div class="prompt-header orange">
        <b>C. Key Content Elements</b><br>
        <small>ROUND 3 · SPECIFIC DETAILS</small>
    </div>
    """, unsafe_allow_html=True)
    st.text_area(
        "Prompt C",
        key="prompt_c",
        height=190,
        label_visibility="collapsed"
    )

st.markdown("")

# ---------------- GENERATION ----------------

if st.button(
    "✨ GENERATE ALL RESPONSES & COMPARE",
    use_container_width=True
):
    try:
        prompts = build_round_prompts(
            st.session_state.prompt_a,
            st.session_state.prompt_b,
            st.session_state.prompt_c
        )

        with st.spinner("Checking Ollama connection..."):
            check_connection()

        # Clear old responses before generating a new set.
        st.session_state.response_box_1 = ""
        st.session_state.response_box_2 = ""
        st.session_state.response_box_3 = ""
        st.session_state.comparison_results = None
        st.session_state.comparison_requirements = None

        response_keys = [
            "response_box_1",
            "response_box_2",
            "response_box_3"
        ]

        responses = []
        progress = st.progress(0)
        status = st.empty()

        for i, prompt in enumerate(prompts):
            status.info(f"Generating response {i + 1} of 3...")

            answer = generate_response(prompt)

            if not answer.strip():
                raise OllamaError(
                    f"Round {i + 1} returned an empty response."
                )

            responses.append(answer)
            st.session_state[response_keys[i]] = answer
            progress.progress((i + 1) / 3)

        # Compare only the actual generated responses.
        results, requirements = compare_responses(
            prompts, responses
        )

        st.session_state.comparison_results = results
        st.session_state.comparison_requirements = requirements
        st.session_state.last_prompts = prompts

        status.success("All three responses and comparisons are ready!")

    except (OllamaError, ValueError) as error:
        st.error(str(error))

    except Exception as error:
        st.error(f"Unexpected error: {error}")

# ---------------- RESPONSE BOXES ----------------

st.markdown("---")
st.markdown("## 02 · AI-Generated Responses")

r1, r2, r3 = st.columns(3, gap="medium")

with r1:
    st.markdown("""
    <div class="prompt-header purple">
        <b>A. MINIMAL INSTRUCTION</b><br>
        <small>ROUND 1 RESPONSE</small>
    </div>
    """, unsafe_allow_html=True)
    st.text_area(
        "Response A",
        key="response_box_1",
        height=300,
        disabled=True,
        placeholder="The first AI response appears here.",
        label_visibility="collapsed"
    )

with r2:
    st.markdown("""
    <div class="prompt-header teal">
        <b>B. LENGTH & STYLE CONSTRAINTS</b><br>
        <small>ROUND 2 RESPONSE</small>
    </div>
    """, unsafe_allow_html=True)
    st.text_area(
        "Response B",
        key="response_box_2",
        height=300,
        disabled=True,
        placeholder="The second AI response appears here.",
        label_visibility="collapsed"
    )

with r3:
    st.markdown("""
    <div class="prompt-header orange">
        <b>C. KEY CONTENT ELEMENTS</b><br>
        <small>ROUND 3 RESPONSE</small>
    </div>
    """, unsafe_allow_html=True)
    st.text_area(
        "Response C",
        key="response_box_3",
        height=300,
        disabled=True,
        placeholder="The third AI response appears here.",
        label_visibility="collapsed"
    )

# ---------------- COMPARISON DASHBOARD ----------------

st.markdown("---")
st.markdown("## 03 · Response Comparison Dashboard")

results = st.session_state.comparison_results

if results:
    st.caption(
        "Scores are heuristic estimates based on text checks. "
        "They do not independently verify factual accuracy."
    )

    # Summary cards
    metric1, metric2, metric3 = st.columns(3)

    for col, result, color in zip(
        [metric1, metric2, metric3],
        results,
        ["#7657FF", "#11A6B5", "#FF9B54"]
    ):
        with col:
            st.markdown(
                f"""
                <div style="background:{color};padding:18px;
                border-radius:12px;text-align:center;color:white;">
                    <div style="font-size:14px;">
                        ROUND {result['round']}
                    </div>
                    <div style="font-size:30px;font-weight:bold;">
                        {result['overall']}%
                    </div>
                    <div style="font-size:13px;">
                        Estimated requirement score
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("### Evaluation Factors")

    # Make one row per evaluation factor.
    factor_names = list(results[0]["scores"].keys())

    table_rows = []
    for factor in factor_names:
        table_rows.append({
            "Evaluation factor": factor,
            "Round 1": results[0]["scores"].get(factor, "N/A"),
            "Round 2": results[1]["scores"].get(factor, "N/A"),
            "Round 3": results[2]["scores"].get(factor, "N/A"),
        })

    st.dataframe(
        pd.DataFrame(table_rows),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Length and Format Check")

    length_rows = []
    for result in results:
        length_rows.append({
            "Round": result["round"],
            "Word count": result["word_count"],
            "Detected sentences": result["sentence_count"],
            "Length requirement": result["length_note"]
        })

    st.dataframe(
        pd.DataFrame(length_rows),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Key Content Coverage")

    requirements = st.session_state.comparison_requirements or {}

    if requirements:
        for group, terms in requirements.items():
            if terms:
                st.write(f"**{group}:** {', '.join(terms)}")
    else:
        st.write(
            "No specific keywords were detected automatically. "
            "Review the prompts and responses above."
        )

    st.markdown("### Observed Changes")

    score1, score2, score3 = [
        result["overall"] for result in results
    ]

    change_2 = score2 - score1
    change_3 = score3 - score2

    st.write(
        f"- **Round 1 → Round 2:** estimated score changed by "
        f"{change_2:+d} percentage points."
    )
    st.write(
        f"- **Round 2 → Round 3:** estimated score changed by "
        f"{change_3:+d} percentage points."
    )

    if change_2 > 0:
        st.write(
            "Round 2 scored higher according to these automatic checks."
        )
    elif change_2 < 0:
        st.write(
            "Round 2 scored lower according to these automatic checks."
        )
    else:
        st.write(
            "Round 1 and Round 2 received the same estimated score."
        )

    if change_3 > 0:
        st.write(
            "Round 3 scored higher according to these automatic checks."
        )
    elif change_3 < 0:
        st.write(
            "Round 3 scored lower according to these automatic checks."
        )
    else:
        st.write(
            "Round 2 and Round 3 received the same estimated score."
        )

else:
    st.info(
        "Your comparison table and scores will appear here after "
        "you generate all three AI responses."
    )

# ---------------- FOOTER ----------------

st.markdown("---")

