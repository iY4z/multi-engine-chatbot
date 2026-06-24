import streamlit as st
import random
import base64
from io import BytesIO
from gtts import gTTS
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

# -----------------------------------------------------------------
# Core App Setup & Audio Engine
# -----------------------------------------------------------------

def init_os():
    """
    Sets up the initial state for the app, including user auth,
    chat history tracking, and a random health metric for the dashboard UI.
    """
    if "authenticated" not in st.session_state: 
        st.session_state.authenticated = False
    if "users" not in st.session_state: 
        st.session_state.users = {"admin": "root"}
    if "messages" not in st.session_state: 
        st.session_state.messages = []
    if "operator" not in st.session_state: 
        st.session_state.operator = "GUEST"
    if "sys_health" not in st.session_state: 
        st.session_state.sys_health = random.randint(97, 100)

def speak_engine(text):
    """
    Converts text to speech using gTTS and generates an HTML audio tag
    with a base64 encoded string to trigger autoplay in the browser.
    """
    try:
        tts = gTTS(text=text[:250], lang="en")
        buf = BytesIO()
        tts.write_to_fp(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>'
    except Exception: 
        return ""

# -----------------------------------------------------------------
# UI Styling & Custom CSS Injection
# -----------------------------------------------------------------

def apply_visual_dna():
    """
    Injects custom CSS to build a custom sci-fi dark theme.
    It overrides default Streamlit wrappers to style the chat bubbles, 
    custom file upload icon, microphone icon, and layout spacing.
    """
    st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    /* Force true black background and crisp white text */
    .stApp { background: #000000 !important; color: #ffffff !important; }
    
    /* Max layout width constraints for clean message alignment */
    [data-testid="stChatMessage"] {
        max-width: 800px !important; margin: 0 auto 15px auto !important;
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,215,0,0.1) !important;
        border-radius: 15px !important;
    }

    /* Strip default text and borders from the file uploader */
    [data-testid="stFileUploader"] section { padding: 0 !important; border: none !important; background: transparent !important; }
    [data-testid="stFileUploader"] div, [data-testid="stFileUploader"] label, [data-testid="stFileUploader"] small { 
        display: none !important; 
    }
    
    /* Transform uploader button into a neat circular folder icon */
    [data-testid="stFileUploader"] { width: 42px !important; margin-top: 5px !important; }
    [data-testid="stFileUploader"] button {
        background: #FFD700 !important; color: black !important;
        border-radius: 50% !important; height: 38px !important; width: 38px !important;
        font-size: 0px !important; border: none !important;
    }
    [data-testid="stFileUploader"] button::before { content: "📁"; font-size: 16px; }

    /* Fix dimensions and tracking alignment for voice input tool */
    [data-testid="stAudioInput"] { width: 42px !important; min-width: 42px !important; margin-top: -3px !important; }
    [data-testid="stAudioInput"] > div { width: 42px !important; }

    /* Clean up input text panel container rules */
    .stChatInputContainer {
        max-width: 800px !important; margin: 0 auto !important;
        background: #151515 !important; border-radius: 25px !important;
        border: 1px solid #333 !important;
    }

    /* Linear gold gradient styling for titles */
    .iy4z-title {
        text-align: center; font-family: 'Syncopate', sans-serif; font-size: 3rem;
        background: linear-gradient(90deg, #FFD700, #fff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# Views & Navigation (Auth Panel & Interactive Dashboard)
# -----------------------------------------------------------------

def render_auth():
    """
    Renders a simple login interface that gates access to the dashboard.
    """
    st.markdown('<div class="iy4z-title">iY4z GATEWAY</div>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("### 🧬 NEURAL ACCESS")
        u = st.text_input("OPERATOR ID", key="auth_u")
        p = st.text_input("ACCESS KEY", type="password", key="auth_p")
        if st.button("RUN AUTHENTICATION", use_container_width=True):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.authenticated = True
                st.session_state.operator = u
                st.success("ACCESS GRANTED.")
                st.rerun()
            else:
                st.error("ACCESS DENIED.")

def main_os():
    """
    The main app interface. Includes the sidebar controls, model routing selection,
    and handles chat logging for text, images, and voice prompts.
    """
    with st.sidebar:
        st.markdown('<h2 style="color:#FFD700; font-family:Syncopate;">NEURAL OS</h2>', unsafe_allow_html=True)
        brain = st.selectbox("Neural Core", ["Llama 3.3 (Groq)", "Mixtral (Groq)", "GPT-4o", "GPT-4o-Mini"])
        st.metric("Kernel Health", f"{st.session_state.sys_health}%")
        
        if st.button("💀 TERMINATE", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    st.markdown('<div class="iy4z-title">iY4z AI assistant</div>', unsafe_allow_html=True)

    # Render complete list of previous conversation loops back to layout view
    for msg in st.session_state.messages:
        if isinstance(msg, dict) and "role" in msg:
            with st.chat_message(msg["role"]):
                if "image" in msg: 
                    st.image(msg["image"], width=300)
                st.markdown(msg["content"])

    # Center-aligned horizontal control deck for text input, mic, and media files
    st.write("---")
    _, c_hub, _ = st.columns([0.15, 0.7, 0.15])
    with c_hub:
        c1, c2, c3 = st.columns([0.06, 0.06, 0.88])
        with c1:
            uploaded = st.file_uploader("", type=["png", "jpg"], key="up", label_visibility="collapsed")
        with c2:
            # FIXED: Removed 'label_visibility' parameter entirely to prevent internal terminal crash
            voice_data = st.audio_input("", key="mic")
        with c3:
            prompt = st.chat_input("Command the Neural Core...")

    # Route active prompts and evaluate pipeline execution loops
    if prompt or voice_data or uploaded:
        text = prompt if prompt else ("Voice command detected." if voice_data else "Processing image...")
        user_msg = {"role": "user", "content": text}
        
        if uploaded: 
            user_msg["image"] = Image.open(uploaded)
            
        st.session_state.messages.append(user_msg)
        
        with st.chat_message("user"):
            if uploaded:
                st.image(user_msg["image"], width=300)
            st.markdown(text)
        
        with st.chat_message("assistant"):
            with st.spinner("Decoding..."):
                try:
                    # Safely load configuration options out of secrets variables
                    openai_key = st.secrets.get("OPENAI_API_KEY")
                    groq_key = st.secrets.get("GROQ_API_KEY")

                    # Handle API mapping based on dashboard selectbox parameters
                    if "GPT-4o" == brain: 
                        llm = ChatOpenAI(model="gpt-4o", api_key=openai_key)
                    elif "GPT-4o-Mini" == brain: 
                        llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)
                    elif "Llama" in brain: 
                        llm = ChatGroq(model="llama-3.3-70b-specdec", api_key=groq_key or None)
                    else: 
                        llm = ChatGroq(model="mixtral-8x7b-32768", api_key=groq_key or None)


                    res = llm.invoke(text).content
                    st.markdown(res)
                    st.markdown(speak_engine(res), unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                except Exception as e: 
                    st.error(f"🚨 Connection Failure: {e}")

# -----------------------------------------------------------------
# App Execution Block
# -----------------------------------------------------------------

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="iY4z OS", page_icon="⚡")
    init_os()
    apply_visual_dna()
    if not st.session_state.authenticated:
        render_auth()
    else:
        main_os()
