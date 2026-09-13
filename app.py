import streamlit as st
from main import run_pipeline
from core.rag_engine import ask_question

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(99,102,241,0.15), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(168,85,247,0.12), transparent 30%),
        #0b0f19;
    color: #f8fafc;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Hero */
.hero {
    padding: 35px 40px;
    border-radius: 24px;
    background:
        linear-gradient(
            135deg,
            rgba(30,41,59,0.95),
            rgba(17,24,39,0.92)
        );
    border: 1px solid rgba(148,163,184,0.15);
    box-shadow: 0 20px 60px rgba(0,0,0,0.35);
    margin-bottom: 30px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 8px;
    background: linear-gradient(90deg,#a78bfa,#60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 17px;
}

/* Cards */
.card {
    background: rgba(15,23,42,0.75);
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
}

.card-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 12px;
}

/* Stats */
.stat-card {
    background: rgba(30,41,59,0.7);
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
}

.stat-number {
    font-size: 26px;
    font-weight: 800;
    color: #a78bfa;
}

.stat-label {
    color: #94a3b8;
    font-size: 13px;
}

/* Input */
.stTextInput > div > div > input {
    background: #111827;
    color: white;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 14px;
}

/* Select */
.stSelectbox > div > div {
    background: #111827;
    border-radius: 12px;
}

/* Button */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    border: none;
    padding: 12px 20px;
    font-weight: 700;
    font-size: 16px;
    background: linear-gradient(90deg,#7c3aed,#4f46e5);
    color: white;
    transition: 0.2s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(99,102,241,0.35);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 18px;
}

/* Divider */
hr {
    border-color: rgba(148,163,184,0.12);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #080c14;
    border-right: 1px solid rgba(148,163,184,0.12);
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    st.markdown("## 🎥 AI Video Assistant")

    st.markdown("---")

    st.markdown("### ⚙️ Settings")

    language = st.selectbox(
        "Transcript Language",
        ["english", "hinglish"]
    )

    st.markdown("---")

    st.markdown("### 🧠 Pipeline")

    st.markdown("""
**01** 🎬 Video Input

**02** 🎧 Audio Extraction

**03** 📝 Whisper Transcription

**04** 🧠 AI Analysis

**05** 🔎 Vector Search

**06** 💬 RAG Chat
""")

    st.markdown("---")

    st.caption("AI Video Assistant • Portfolio Project")


# -----------------------------
# Hero
# -----------------------------
st.markdown("""
<div class="hero">
<div class="hero-title">
🎥 AI Video Assistant
</div>
<div class="hero-subtitle">
Turn long videos into intelligent summaries, decisions,
action items and an interactive AI conversation.
</div>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# Video Input
# -----------------------------
st.markdown("### 🚀 Analyze a Video")

st.markdown("""
<div class="card">
<div class="card-title">📺 Video Source</div>
""", unsafe_allow_html=True)

source = st.text_input(
    "YouTube URL or local video/audio path",
    placeholder="https://youtube.com/watch?v=..."
)

process_button = st.button(
    "✨ Analyze Video"
)

st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Run Pipeline
# -----------------------------
if process_button:

    if not source:
        st.warning("Please enter a YouTube URL or file path.")

    else:

        progress = st.progress(0)

        status = st.empty()

        try:

            status.info("🎧 Downloading and preparing audio...")
            progress.progress(15)

            result = run_pipeline(source, language)

            progress.progress(100)

            status.success("✅ Video analysis completed!")

            st.session_state["result"] = result

            # Reset chat for new video
            st.session_state["messages"] = []

        except Exception as e:

            progress.empty()
            status.empty()

            st.error(f"❌ Something went wrong: {e}")


# -----------------------------
# Results
# -----------------------------
if "result" in st.session_state:

    result = st.session_state["result"]

    st.divider()

    # -----------------------------
    # Video Title
    # -----------------------------
    st.markdown(
        f"""
<div class="card">
<div class="card-title">📌 Video Title</div>
<h2>{result['title']}</h2>
</div>
""",
        unsafe_allow_html=True
    )


    # -----------------------------
    # Stats
    # -----------------------------
    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("""
<div class="stat-card">
<div class="stat-number">📝</div>
<div class="stat-label">Transcript Generated</div>
</div>
""", unsafe_allow_html=True)

    with col2:

        st.markdown("""
<div class="stat-card">
<div class="stat-number">🧠</div>
<div class="stat-label">AI Analysis</div>
</div>
""", unsafe_allow_html=True)

    with col3:

        st.markdown("""
<div class="stat-card">
<div class="stat-number">💬</div>
<div class="stat-label">RAG Chat Ready</div>
</div>
""", unsafe_allow_html=True)


    st.markdown("")


    # -----------------------------
    # Tabs
    # -----------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Summary",
        "✅ Action Items",
        "🔑 Key Decisions",
        "❓ Open Questions",
        "📄 Transcript"
    ])


    # -----------------------------
    # Summary
    # -----------------------------
    with tab1:

        st.markdown("### 📋 AI Summary")

        st.markdown(result["summary"])


    # -----------------------------
    # Action Items
    # -----------------------------
    with tab2:

        st.markdown("### ✅ Action Items")

        st.markdown(result["action_items"])


    # -----------------------------
    # Key Decisions
    # -----------------------------
    with tab3:

        st.markdown("### 🔑 Key Decisions")

        st.markdown(result["key_decisions"])


    # -----------------------------
    # Open Questions
    # -----------------------------
    with tab4:

        st.markdown("### ❓ Open Questions")

        st.markdown(result["open_questions"])


    # -----------------------------
    # Transcript
    # -----------------------------
    with tab5:

        st.markdown("### 📄 Full Transcript")

        st.text_area(
            "Transcript",
            result["transcript"],
            height=500,
            label_visibility="collapsed"
        )


    # -----------------------------
    # RAG Chat
    # -----------------------------
    st.divider()

    st.markdown("## 💬 Chat with your Video")

    st.caption(
        "Ask questions about the video and get answers from the transcript."
    )


    if "messages" not in st.session_state:

        st.session_state.messages = []


    # Display previous messages
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])


    # Chat input
    question = st.chat_input(
        "Ask something about this video..."
    )


    if question:

        # User message
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):

            st.markdown(question)


        # Assistant response
        with st.chat_message("assistant"):

            with st.spinner("🧠 Thinking..."):

                answer = ask_question(
                    result["rag_chain"],
                    question
                )

            st.markdown(answer)


        # Save assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })
