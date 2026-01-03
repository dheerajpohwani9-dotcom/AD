import streamlit as st
import pdfplumber
import requests
import datetime

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Afaque & Dheeraj Chatbot",
    page_icon="🤖",
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
    st.markdown("### Smart AI Chatbot")
    st.markdown("---")
    st.markdown("📄 PDF-Based Knowledge")
    st.markdown("⚡ Powered by Groq (LLaMA 3)")
    st.markdown("🎨 Colorful Modern UI")
    st.markdown("🚀 Fast & Reliable")
    st.markdown("---")
    st.markdown("💡 Ask clearly. Get smart answers.")
    st.markdown("</div>", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="header-box">
    <div class="header-title">🤖 Afaque & Dheeraj Chatbot</div>
    <div class="header-sub">Colorful • Intelligent • AI-Powered • PDF-Aware</div>
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
            content = page.extract_text()
            if content:
                text += content + "\n"

    parts = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, buffer = [], ""

    for part in parts:
        if len(buffer) + len(part) <= max_chars:
            buffer += " " + part
        else:
            chunks.append(buffer.strip())
            buffer = part

    if buffer:
        chunks.append(buffer.strip())

    return chunks

pdf_chunks = load_chunks()

# ================= RETRIEVAL =================
def retrieve_context(query, top_k=3):
    query_words = set(query.lower().split())
    scored_chunks = []

    for chunk in pdf_chunks:
        score = len(query_words & set(chunk.lower().split()))
        if score > 0:
            scored_chunks.append((score, chunk))

    if not scored_chunks:
        return ""

    scored_chunks.sort(reverse=True)
    return "\n\n".join([c for _, c in scored_chunks[:top_k]])

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

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except:
        return "🚨 Groq API Error:\n" + str(data)

# ================= ANSWER LOGIC =================
def get_answer(question, history):
    context = retrieve_context(question)
    today = datetime.datetime.now().strftime("%d %B %Y")

    if len(context.strip()) < 50:
        system_prompt = f"""
You are **Afaque & Dheeraj Chatbot**.

Rules:
- Respond in clear, professional English only.
- Use updated general knowledge (today: {today}).
- Never mention searching, browsing, or knowledge cutoffs.
"""
    else:
        system_prompt = f"""
You are **Afaque & Dheeraj Chatbot**.

Use the following PDF context as the primary source.
Include updated information when relevant.

PDF Context:
{context}

Rules:
- English only.
- Be confident, clear, and helpful.
"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": question})

    return llama_chat(messages)

# ================= CHAT STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "👋 Welcome!\n\nI’m the **Afaque & Dheeraj Chatbot**.\nAsk me anything based on the PDF or general knowledge."
    }]

# ================= DISPLAY CHAT =================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================= INPUT =================
user_input = st.chat_input("Type your question here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = get_answer(user_input, st.session_state.messages)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
