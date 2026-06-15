import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
st.set_page_config(page_title="AI Chatbot", layout="wide")

st.markdown("""
<style>
    .chat-header {
        background: #16191f;
        border: 1px solid #2a2d3e;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    [data-testid="stChatMessage"] {
        background: #16191f;
        border-radius: 8px;
        border: 1px solid #2a2d3e;
        padding: 4px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = {}

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    return Groq(api_key=api_key) if api_key else None

def chat(user_message):
    client = get_groq_client()
    if not client:
        return "GROQ_API_KEY not found in .env file."

    data = st.session_state.analysis_data
    context = ""
    if data:
        context = f"""The user has analyzed {data.get('company')} ({data.get('ticker')}):
- Risk Score: {data.get('composite_score')}/100 — {data.get('label')}
- Volatility: {data.get('regime')}
- 99% VaR: {data.get('var_99')}%
- Sentiment Risk: {data.get('sentiment_score')}/100
"""

    system_prompt = f"""You are MarketPulse AI, a professional investment assistant for Indian retail investors.
Be concise, clear, and helpful. Use plain language — no jargon.
{context}
Important: always clarify this is not financial advice and suggest consulting a SEBI-registered advisor for major decisions."""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages[-8:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=600,
        messages=messages
    )
    return response.choices[0].message.content

# --- Page ---
st.markdown("## MarketPulse AI")

data = st.session_state.analysis_data
if data:
    st.markdown(f"""
    <div class="chat-header">
        <strong>Context loaded</strong> — {data.get('company')} ({data.get('ticker')}) &nbsp;·&nbsp;
        Risk Score: {data.get('composite_score')}/100 &nbsp;·&nbsp; {data.get('label')}
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="chat-header" style="color:#888">
        No analysis loaded yet. Run a stock analysis first for context-aware answers,
        or ask general investing questions below.
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col2:
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "assets/bot.png" if False else "🤖"):
        st.markdown(msg["content"])

if not st.session_state.messages:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Suggested questions**")
    suggestions = [
        "Should I invest in this stock right now?",
        "What does VaR mean in simple terms?",
        "How do I diversify my portfolio?",
        "What is the difference between High Vol and Low Vol regime?",
    ]
    scols = st.columns(2)
    for i, s in enumerate(suggestions):
        if scols[i % 2].button(s, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": s})
            with st.chat_message("user", avatar="👤"):
                st.markdown(s)
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner(""):
                    response = chat(s)
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

if prompt := st.chat_input("Ask anything about stocks or investing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner(""):
            response = chat(prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})