
import streamlit as st
from main import run_experiment, check_connection

st.set_page_config(
    page_title="Experiment 9 | Structured Data Studio",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- THEME ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #eaf8f7, #edf1fb, #f4f7ff);
    color: #19334b;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    background: linear-gradient(115deg, #102e4a, #176b78, #39a6a0);
    padding: 30px;
    border-radius: 22px;
    color: white;
    margin-bottom: 28px;
}

.hero h1 {
    color: white;
    font-size: 32px;
    font-weight: 800;
}

.hero p {
    color: #e3fffc;
    margin-bottom: 4px;
}

.panel-heading {
    font-size: 21px;
    color: #145d6a;
    font-weight: 700;
    margin-bottom: 16px;
}

.format-card {
    background: #f5fbff;
    border: 1px solid #c9dfe9;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 14px;
    min-height: 120px;
}

.format-card h3 {
    color: #174c65;
    margin: 0 0 10px 0;
}

.format-card p {
    font-size: 13px;
    color: #587487;
    margin: 0;
}

.stTextArea textarea {
    background: #fbffff !important;
    color: #19334b !important;
    border: 1px solid #b9dcdc !important;
    border-radius: 12px !important;
}

div.stButton > button {
    border-radius: 12px;
    min-height: 46px;
    font-weight: 600;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #176b78, #35a69b);
    color: white;
    border: none;
}

div.stButton > button[kind="secondary"] {
    border: 1px solid #a8d4d5;
    color: #145d6a;
    background: #f7ffff;
}

.result-heading {
    color: #145d6a;
    font-size: 21px;
    font-weight: 700;
    margin: 18px 0 14px 0;
}

.result-box {
    background: #fbffff;
    border: 1px solid #c9e5e5;
    border-left: 5px solid #219b96;
    border-radius: 16px;
    padding: 18px;
    min-height: 280px;
}

.status-box {
    background: #f4f8ff;
    border: 1px solid #cedcf0;
    border-left: 5px solid #426a9b;
    border-radius: 16px;
    padding: 18px;
    min-height: 280px;
}

.footer {
    text-align: center;
    color: #587a8d;
    font-size: 13px;
    padding: 24px 0;
}

#MainMenu, footer, header {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>🧩 Structured Data Studio</h1>
    <p>EXPERIMENT 9 · JSON / YAML GENERATION</p>
    <p>Generate machine-readable data in your preferred format.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------

if "exp9_description" not in st.session_state:
    st.session_state.exp9_description = (
        "Create a dataset of three books. Each book must have "
        "title, author, and publication_year fields."
    )

if "exp9_format" not in st.session_state:
    st.session_state.exp9_format = "JSON"

if "exp9_result" not in st.session_state:
    st.session_state.exp9_result = None

if "exp9_error" not in st.session_state:
    st.session_state.exp9_error = None


def choose_format(value):
    st.session_state.exp9_format = value
    st.session_state.exp9_result = None
    st.session_state.exp9_error = None


def clear_all():
    st.session_state.exp9_description = ""
    st.session_state.exp9_result = None
    st.session_state.exp9_error = None


# ---------------- INPUT AND FORMAT ----------------

left, right = st.columns([1.35, 1], gap="large")

with left:
    st.markdown(
        '<div class="panel-heading">📝 Dataset Configuration</div>',
        unsafe_allow_html=True
    )

    st.text_area(
        "Describe the dataset you want to generate",
        key="exp9_description",
        height=175,
        placeholder="Describe your dataset and required fields..."
    )

    st.caption("Specify the records, fields, and expected data types.")

with right:
    st.markdown(
        '<div class="panel-heading">⚙️ Choose Output Format</div>',
        unsafe_allow_html=True
    )

    selected_format = st.session_state.exp9_format

    if selected_format == "JSON":
        title = "🟢 JSON"
        details = "Strict key-value format using double quotes."
    else:
        title = "🔵 YAML"
        details = "Readable structured format using indentation."

    st.markdown(
        f"""
        <div class="format-card">
            <h3>{title}</h3>
            <p>{details}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    json_col, yaml_col = st.columns(2)

    with json_col:
        st.button(
            "{} JSON",
            key="json_format_button",
            type="primary" if selected_format == "JSON" else "secondary",
            use_container_width=True,
            on_click=choose_format,
            args=("JSON",)
        )

    with yaml_col:
        st.button(
            "☷ YAML",
            key="yaml_format_button",
            type="primary" if selected_format == "YAML" else "secondary",
            use_container_width=True,
            on_click=choose_format,
            args=("YAML",)
        )

    st.caption(f"Selected format: {selected_format}")

# ---------------- ACTIONS ----------------

st.write("")

generate_col, clear_col, empty_col = st.columns([1.2, 0.7, 2.1])

with generate_col:
    generate_clicked = st.button(
        "⚡ Generate Data",
        type="primary",
        use_container_width=True
    )

with clear_col:
    st.button(
        "Clear All",
        on_click=clear_all,
        use_container_width=True
    )

# ---------------- GENERATION ----------------

if generate_clicked:
    description = st.session_state.exp9_description.strip()

    if not description:
        st.session_state.exp9_error = "Please enter a dataset description."
        st.session_state.exp9_result = None
    else:
        try:
            with st.spinner("Generating and checking your data..."):
                check_connection()

                st.session_state.exp9_result = run_experiment(
                    description=description,
                    output_format=st.session_state.exp9_format,
                    max_refinements=2
                )

                st.session_state.exp9_error = None

        except Exception as error:
            st.session_state.exp9_error = str(error)
            st.session_state.exp9_result = None

# ---------------- ERROR ----------------

if st.session_state.exp9_error:
    st.error(st.session_state.exp9_error)

# ---------------- RESULTS INSIDE BOXES ----------------

result = st.session_state.exp9_result

if result:
    data_col, status_col = st.columns(2, gap="large")

    with data_col:
        st.markdown(
            '<div class="result-heading">📄 Generated Data</div>',
            unsafe_allow_html=True
        )

        # Native Streamlit container keeps the generated output inside.
        with st.container(border=True):
            st.markdown(
                f"**Output format:** {st.session_state.exp9_format}"
            )

            st.code(
                result["output"],
                language=(
                    "json"
                    if st.session_state.exp9_format == "JSON"
                    else "yaml"
                ),
                wrap_lines=True
            )

    with status_col:
        st.markdown(
            '<div class="result-heading">📋 Parser Validation Result</div>',
            unsafe_allow_html=True
        )

        # All validation content is inside this native container.
        with st.container(border=True):
            if result["valid"]:
                st.success("✅ Valid structured data")
                st.write(
                    f"The parser successfully accepted the "
                    f"{st.session_state.exp9_format} output."
                )
            else:
                st.error("❌ Validation unsuccessful")
                st.write(
                    "The output could not be validated after "
                    "the refinement attempts."
                )

            st.write("**Validation details:**")
            st.write(result["message"])

            st.write(
                f"**Attempts used:** {len(result['attempts'])}"
            )


