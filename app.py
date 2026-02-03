import streamlit as st
import datetime
import base64

# --- APP CONFIG ---
st.set_page_config(page_title="Gooncord", page_icon="💀", layout="wide")

# --- GOON MODE TOGGLE ---
with st.sidebar:
    st.title("Gooncord 💀")
    goon_mode = st.toggle("🟣 GOON MODE", value=False)

# --- THEME LOGIC ---
if goon_mode:
    primary_color = "#bc13fe" 
    bg_color = "#000000"
    text_color = "#39ff14" 
    st.markdown(f"""
        <style>
            .stApp {{ background-color: {bg_color}; color: {text_color}; }}
            [data-testid="stSidebar"] {{ background-color: #1a0033; border-right: 2px solid {primary_color}; }}
            .member-box {{ background-color: #000000; border: 1px solid {primary_color}; color: {text_color}; box-shadow: 0 0 10px {primary_color}; padding: 8px; border-radius: 4px; margin-bottom: 5px; }}
            .stChatMessage {{ background-color: #111; border: 1px solid {text_color} !important; box-shadow: 0 0 5px {text_color}; }}
            h1, h2, h3, p, span {{ color: {text_color} !important; }}
        </style>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { background-color: #2f3136; }
            .member-box { background-color: #1e1f22; padding: 8px; border-radius: 4px; margin-bottom: 5px; font-size: 0.85rem;}
            .status-text { color: #b9bbbe; font-style: italic; font-size: 0.8rem; }
        </style>
        """, unsafe_allow_html=True)

# --- GLOBAL SHARED DATABASE ---
@st.cache_resource
def get_global_data():
    return {
        "messages": {
            "The Citadel": {"# general": [], "# memes": []},
            "Deep Thoughts": {"# philosophy": [], "# logic": []}
        },
        "active_users": {} 
    }

global_db = get_global_data()

# --- SESSION STATE ---
if "user_name" not in st.session_state:
    st.session_state.user_name = f"Gooner_{id(st.session_state) % 1000}"
if "my_status" not in st.session_state:
    st.session_state.my_status = "Chilling"

# --- SIDEBAR CONTENT ---
with st.sidebar:
    # --- NEW: PROFILE SETTINGS ---
    with st.expander("👤 Profile Settings", expanded=True):
        new_name = st.text_input("Username", value=st.session_state.user_name)
        new_stat = st.text_input("Status", value=st.session_state.my_status)
        
        if st.button("Save Profile"):
            # Remove old name from global list if it changed
            if new_name != st.session_state.user_name:
                global_db["active_users"].pop(st.session_state.user_name, None)
            
            st.session_state.user_name = new_name
            st.session_state.my_status = new_stat
            global_db["active_users"][new_name] = new_stat
            st.success("Profile Updated!")
            st.rerun()

    # Register current user in global list
    global_db["active_users"][st.session_state.user_name] = st.session_state.my_status

    st.divider()
    server = st.selectbox("Select Server", list(global_db["messages"].keys()))
    channel = st.radio("Channels", list(global_db["messages"][server].keys()))
    
    st.divider()
    st.write("### 📤 Upload Media")
    
    img_file = st.file_uploader("Send Image", type=["png", "jpg", "jpeg"], key="img")
    if img_file and st.button("🖼️ Post Image"):
        b64 = base64.b64encode(img_file.getvalue()).decode()
        global_db["messages"][server][channel].append({"user": st.session_state.user_name, "time": datetime.datetime.now().strftime("%I:%M %p"), "content": "", "image": b64, "audio": None})
        st.rerun()

    audio_file = st.file_uploader("Send Goon Sound", type=["mp3", "wav"], key="audio")
    if audio_file and st.button("🔊 Post Audio"):
        b64 = base64.b64encode(audio_file.getvalue()).decode()
        global_db["messages"][server][channel].append({"user": st.session_state.user_name, "time": datetime.datetime.now().strftime("%I:%M %p"), "content": "", "image": None, "audio": b64})
        st.rerun()

# --- MAIN CHAT ---
chat_col, member_col = st.columns([4, 1])

with chat_col:
    st.header(f"💬 {channel}")
    messages = global_db["messages"][server][channel]
    
    for msg in messages:
        with st.chat_message("user"):
            st.markdown(f"**{msg['user']}** <small style='color: gray;'>{msg['time']}</small>", unsafe_allow_html=True)
            if msg.get("content"): st.write(msg["content"])
            if msg.get("image"): st.image(f"data:image/png;base64,{msg['image']}", use_container_width=True)
            if msg.get("audio"): st.audio(base64.b64decode(msg["audio"]), format="audio/mp3")

    if prompt := st.chat_input(f"Message {channel}"):
        global_db["messages"][server][channel].append({"user": st.session_state.user_name, "time": datetime.datetime.now().strftime("%I:%M %p"), "content": prompt, "image": None, "audio": None})
        st.rerun()

# --- MEMBER LIST ---
with member_col:
    st.write("### Members")
    for user, status in global_db["active_users"].items():
        is_me = " (You)" if user == st.session_state.user_name else ""
        st.markdown(f'''
            <div class="member-box">
                🟢 <b>{user}</b>{is_me}<br>
                <span class="status-text">{status}</span>
            </div>
        ''', unsafe_allow_html=True)
    
    if st.button("🔄 Refresh"): 
        st.rerun()
