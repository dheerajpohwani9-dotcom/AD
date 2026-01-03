import streamlit as st
import pdfplumber
import requests
import datetime

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Afaque & Dheeraj Chatbot",
    page_icon="🦄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ================= COLORFUL CSS =================
st.markdown("""
<style>
.main {
    background: linear-gradient(120deg, #ff6ec4, #7873f5, #42e695);
}

.header-box {
    background: linear-gradient(90deg, #ff512f, #dd2476);
    padding: 25px;
    border-radius: 18px;
    text-align: center;
    color: white;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.3);
    margin-bottom: 25px;
}

.header-title {
    font-size: 40px;
    font-weight: 900;
}

.header-sub {
    font-size: 16px;
    opacity: 0.95;
}

.stChatMessage {
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(12px);
    border-radius: 18px;
    padding: 12px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}

.sidebar-box {
    background: linear-gradient(180deg, #00c6ff, #0072ff);
    padding: 18px;
    border-radius: 15px;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("<div class='sidebar-box'>", unsafe_allow_html=True)
    st.markdown("## 🤖 Afaque & Dheeraj")
    st.markdown("### ✨ Smart AI Chatbot")
    st.markdown("---")
    st.markdown("📘 **PDF Brain**")
    st.markdown("⚡ **Groq LLaMA 3**")
    st.markdown("🎨 **Colorful UI**")
    st.markdown("🚀 **Fast & Smart**")
    st.markdown("---")
    st.markdown("💡 *Ask freely. Get smart answers.*")
    st.markdown("</div>", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="header-box">
    <div class="header-title">🦄 Afaque & Dheeraj Chatbot</div>
    <div class="header-sub">✨ Colourful • Smart • AI Powered • PDF Aware ✨</div>
</div>
""", unsafe_allow_html=True)

# ================= CONFIG =================
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
PDF_PATH = "comapanypolicys.pdf"
MODEL_NAME = "llama-3.1-8b-instant"

# ================= LOAD PDF =================
@st.cache_data
def load_chunks(max_chars=600):
    text = ""
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

    parts = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, buf = [], ""

    for p in parts:
        if len(buf) + len(p) <= max_chars:
            buf += " " + p
        else:
            chunks.append(buf.strip())
            buf = p

    if buf:
        chunks.append(buf.strip())

    return chunks

pdf_chunks = load_chunks()

# ================= RETRIEVAL =================
def retrieve_context(query, top_k=3):
    q = set(query.lower().split())
    scored = []

    for ch in pdf_chunks:
        score = len(q & set(ch.lower().split()))
        if score:
            scored.append((score, ch))

    if not scored:
        return ""

    scored.sort(reverse=True)
    return "\n\n".join([c for _, c in scored[:top_k]])

# ================= GROQ API =================
def llama_chat(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.4,
    }

    r = requests.post(url, json=payload, headers=headers)
    data = r.json()

    try:
        return data["choices"][0]["message"]["content"]
    except:
        return "🚨 **Oops! Groq API Error**\n\n" + str(data)

# ================= ANSWER LOGIC =================
def get_answer(question, history):
    context = retrieve_context(question)
    today = datetime.datetime.now().strftime("%d %B %Y")

    if len(context.strip()) < 50:
        system_prompt = f"""
You are 🌈 **Afaque & Dheeraj Chatbot**.

Rules:
- Be friendly, colourful, and confident.
- Use updated knowledge (today: {today}).
- Never say you are searching or outdated.
"""
    else:
        system_prompt = f"""
You are 🌈 **Afaque & Dheeraj Chatbot**.

Use this PDF context smartly and add updated info if needed.

PDF Context:
{context}

Rules:
- Friendly, clear, confident.
"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": question})

    return llama_chat(messages)

# ================= CHAT STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "👋✨ **Hey there!**\n\nI’m your **Afaque & Dheeraj Chatbot** 🦄💬\nAsk me anything — PDF or general knowledge 🚀"
    }]

# ================= DISPLAY CHAT =================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================= INPUT =================
user_input = st.chat_input("💬 Type your colourful question here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("✨ Thinking magic..."):
            reply = get_answer(user_input, st.session_state.messages)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
