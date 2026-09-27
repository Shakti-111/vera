import streamlit as st
from generate_answer import ask_vera

st.set_page_config(page_title="Adaptive RAG System", page_icon="🧠", layout="centered")

# ============ CUSTOM STYLING ============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Overall app background - deep navy gradient */
.stApp {
    background: linear-gradient(160deg, #0B132B 0%, #16325C 50%, #0B132B 100%);
}

/* Center and constrain content width */
.block-container {
    max-width: 780px;
    padding-top: 2.5rem;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* Chat input container - match dark theme */
[data-testid="stChatInput"] {
    background: #0B132B;
    border-top: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stChatInput"] > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(34, 211, 238, 0.3) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #E4ECF5 !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #8B9BB4 !important;
}
[data-testid="stBottom"] {
    background: #0B132B;
}
[data-testid="stBottomBlockContainer"] {
    background: #0B132B;
    max-width: 780px;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* Hero header */
.hero-title {
    font-family: 'Poppins', sans-serif;
    font-size: 2.6em;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #22D3EE, #1E40AF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2em;
    animation: fadeInDown 0.8s ease;
}

.hero-subtitle {
    text-align: center;
    color: #B8C7D9;
    font-size: 1.05em;
    margin-bottom: 0.3em;
}

.badge-row {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-bottom: 2em;
    flex-wrap: wrap;
}

.badge {
    background: rgba(34, 211, 238, 0.12);
    border: 1px solid rgba(34, 211, 238, 0.4);
    color: #22D3EE;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.78em;
    font-weight: 600;
}

/* Chat bubbles */
.chat-bubble-user {
    background: linear-gradient(135deg, #1E40AF, #0EA5B7);
    color: white;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 10px 0;
    max-width: 85%;
    margin-left: auto;
    font-size: 0.96em;
    box-shadow: 0 4px 14px rgba(30, 64, 175, 0.35);
    animation: fadeInUp 0.4s ease;
}

.chat-bubble-assistant {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(6px);
    color: #E4ECF5;
    padding: 16px 20px;
    border-radius: 18px 18px 18px 4px;
    margin: 10px 0;
    max-width: 92%;
    font-size: 0.97em;
    line-height: 1.5;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    animation: fadeInUp 0.5s ease;
}

/* Trust score pill */
.trust-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.9em;
    margin-top: 12px;
}

.trust-high { background: rgba(34, 197, 94, 0.15); border: 1px solid #22C55E; color: #4ADE80; }
.trust-mid { background: rgba(234, 179, 8, 0.15); border: 1px solid #EAB308; color: #FACC15; }
.trust-low { background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; color: #F87171; }

/* Trust score bar track */
.trust-track {
    width: 100%;
    height: 8px;
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    margin-top: 10px;
    overflow: hidden;
}
.trust-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 0.6s ease;
}

/* Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Hide Streamlit default clutter */
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
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

# ============ CHAT STATE ============
if "messages" not in st.session_state:
    st.session_state.messages = []

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

# ============ RENDER HISTORY ============
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        render_assistant_message(msg["content"], msg["trust_score"], msg["reasoning"], msg["sources"])

# ============ INPUT ============
question = st.chat_input("Ask a question about the uploaded document...")

if question:
    st.markdown(f'<div class="chat-bubble-user">{question}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.spinner("🔎 Retrieving context and verifying answer..."):
        result = ask_vera(question)

    render_assistant_message(result["answer"], result["trust_score"], result["reasoning"], result["sources"])

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "trust_score": result["trust_score"],
        "reasoning": result["reasoning"],
        "sources": result["sources"]
    })