import time
import streamlit as st
from generate_answer import ask_vera
from ingestion import ingest_pdf

DEFAULT_COLLECTION = "iot_notes"
DEFAULT_LABEL = "COMMUNICATION MODULES.pdf (demo document)"
UPLOAD_COLLECTION = "uploaded_doc"

st.set_page_config(page_title="Adaptive RAG System", page_icon="🧠", layout="centered", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(160deg, #0B132B 0%, #16325C 50%, #0B132B 100%); }
.block-container { max-width: 780px; padding-top: 2.5rem; margin-left: auto !important; margin-right: auto !important; }
[data-testid="stSidebar"] { background: #0B132B; border-right: 1px solid rgba(255,255,255,0.08); }
.sidebar-title { font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 1.15em; color: #22D3EE; margin-bottom: 0.2em; }
.sidebar-note { color: #9FB3C8; font-size: 0.85em; margin-bottom: 0.8em; }
.doc-card { background: rgba(34, 211, 238, 0.10); border: 1px solid rgba(34, 211, 238, 0.35); border-radius: 12px; padding: 12px 14px; color: #E4ECF5; font-size: 0.88em; margin-top: 0.8em; word-break: break-word; }
.doc-card b { color: #22D3EE; }
[data-testid="stChatInput"] { background: #0B132B; border-top: 1px solid rgba(255,255,255,0.08); }
[data-testid="stChatInput"] > div { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(34, 211, 238, 0.3) !important; border-radius: 14px !important; }
[data-testid="stChatInput"] textarea { background: transparent !important; color: #E4ECF5 !important; }
[data-testid="stChatInput"] textarea::placeholder { color: #8B9BB4 !important; }
[data-testid="stBottom"] { background: #0B132B; }
[data-testid="stBottomBlockContainer"] { background: #0B132B; max-width: 780px; margin-left: auto !important; margin-right: auto !important; }
.hero-title { font-family: 'Poppins', sans-serif; font-size: 2.6em; font-weight: 800; text-align: center; background: linear-gradient(90deg, #22D3EE, #1E40AF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.2em; }
.hero-subtitle { text-align: center; color: #B8C7D9; font-size: 1.05em; margin-bottom: 0.3em; }
.badge-row { display: flex; justify-content: center; gap: 10px; margin-bottom: 2em; flex-wrap: wrap; }
.badge { background: rgba(34, 211, 238, 0.12); border: 1px solid rgba(34, 211, 238, 0.4); color: #22D3EE; padding: 5px 14px; border-radius: 20px; font-size: 0.78em; font-weight: 600; }
.chat-bubble-user { background: linear-gradient(135deg, #1E40AF, #0EA5B7); color: white; padding: 14px 18px; border-radius: 18px 18px 4px 18px; margin: 10px 0; max-width: 85%; margin-left: auto; font-size: 0.96em; box-shadow: 0 4px 14px rgba(30, 64, 175, 0.35); }
.chat-bubble-assistant { background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); color: #E4ECF5; padding: 16px 20px; border-radius: 18px 18px 18px 4px; margin: 10px 0; max-width: 92%; font-size: 0.97em; line-height: 1.5; box-shadow: 0 4px 14px rgba(0,0,0,0.25); }
.trust-pill { display: inline-flex; align-items: center; gap: 8px; padding: 7px 16px; border-radius: 20px; font-weight: 700; font-size: 0.9em; margin-top: 12px; }
.trust-high { background: rgba(34, 197, 94, 0.15); border: 1px solid #22C55E; color: #4ADE80; }
.trust-mid { background: rgba(234, 179, 8, 0.15); border: 1px solid #EAB308; color: #FACC15; }
.trust-low { background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; color: #F87171; }
.trust-track { width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 10px; margin-top: 10px; overflow: hidden; }
.trust-fill { height: 100%; border-radius: 10px; }
#MainMenu, footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
header {background: transparent;}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_collection" not in st.session_state:
    st.session_state.active_collection = DEFAULT_COLLECTION
if "active_label" not in st.session_state:
    st.session_state.active_label = DEFAULT_LABEL
if "doc_info" not in st.session_state:
    st.session_state.doc_info = None
if "loaded_file_key" not in st.session_state:
    st.session_state.loaded_file_key = None
if "uploader_version" not in st.session_state:
    st.session_state.uploader_version = 0

with st.sidebar:
    st.markdown('<div class="sidebar-title">📄 Your Document</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-note">Upload a PDF and ask questions about it.</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload a PDF", type=["pdf"], key=f"uploader_{st.session_state.uploader_version}", label_visibility="collapsed")

    if uploaded is not None:
        file_key = f"{uploaded.name}-{uploaded.size}"
        if st.session_state.loaded_file_key != file_key:
            with st.spinner("Reading, chunking and indexing your document..."):
                try:
                    info = ingest_pdf(uploaded.getvalue(), UPLOAD_COLLECTION)
                    st.session_state.active_collection = UPLOAD_COLLECTION
                    st.session_state.active_label = uploaded.name
                    st.session_state.doc_info = info
                    st.session_state.loaded_file_key = file_key
                    st.session_state.messages = []
                except Exception as e:
                    st.error(f"Could not process this PDF: {e}")

    info_line = ""
    if st.session_state.doc_info:
        d = st.session_state.doc_info
        info_line = f"<br>{d['pages']} pages • {d['chunks']} chunks indexed"
    st.markdown(f'<div class="doc-card"><b>Active document</b><br>{st.session_state.active_label}{info_line}</div>', unsafe_allow_html=True)

    if st.session_state.active_collection != DEFAULT_COLLECTION:
        if st.button("↩ Switch back to demo document"):
            st.session_state.active_collection = DEFAULT_COLLECTION
            st.session_state.active_label = DEFAULT_LABEL
            st.session_state.doc_info = None
            st.session_state.loaded_file_key = None
            st.session_state.messages = []
            st.session_state.uploader_version += 1
            st.rerun()

st.markdown('<div class="hero-title">🧠 Adaptive Self-Evolving RAG System</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Every answer is independently verified and scored for trust — before it reaches you.</div>', unsafe_allow_html=True)
st.markdown("""
<div class="badge-row">
    <span class="badge">🔍 Semantic Retrieval</span>
    <span class="badge">✅ Independent Verification</span>
    <span class="badge">📊 Trust Scoring</span>
    <span class="badge">🔁 Auto Re-Check</span>
</div>
""", unsafe_allow_html=True)


def trust_class(score):
    if score >= 80:
        return "trust-high", "#4ADE80", "🟢"
    elif score >= 50:
        return "trust-mid", "#FACC15", "🟡"
    else:
        return "trust-low", "#F87171", "🔴"


def render_assistant_message(content, trust_score, reasoning, sources):
    css_class, bar_color, icon = trust_class(trust_score)
    st.markdown(f"""
    <div class="chat-bubble-assistant">
        {content}
        <div class="trust-pill {css_class}">{icon} Trust Score: {trust_score}/100</div>
        <div class="trust-track"><div class="trust-fill" style="width:{trust_score}%; background:{bar_color};"></div></div>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("🔎 View reasoning & source chunks"):
        st.write(f"**Reasoning:** {reasoning}")
        for i, chunk in enumerate(sources, 1):
            st.markdown(f"**Source {i}:**")
            st.text(chunk)


def ask_with_retry(question, collection_name, attempts=3):
    last_error = None
    for attempt in range(attempts):
        try:
            return ask_vera(question, collection_name=collection_name)
        except Exception as e:
            last_error = e
            if attempt < attempts - 1:
                time.sleep(5 * (attempt + 1))
    raise last_error


for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        render_assistant_message(msg["content"], msg["trust_score"], msg["reasoning"], msg["sources"])

question = st.chat_input("Ask a question about the active document...")

if question:
    st.markdown(f'<div class="chat-bubble-user">{question}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": question})

    try:
        with st.spinner("🔎 Retrieving context and verifying answer..."):
            result = ask_with_retry(question, st.session_state.active_collection)
        render_assistant_message(result["answer"], result["trust_score"], result["reasoning"], result["sources"])
        st.session_state.messages.append({
            "role": "assistant", "content": result["answer"], "trust_score": result["trust_score"],
            "reasoning": result["reasoning"], "sources": result["sources"]
        })
    except Exception:
        st.error("The AI service is busy right now (free-tier limits). Please try your question again in a moment.")