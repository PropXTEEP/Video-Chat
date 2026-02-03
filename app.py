import streamlit as st
import datetime
import base64

# --- APP CONFIG ---
st.set_page_config(page_title="Gooncord", page_icon="💀", layout="wide")

# --- GLOBAL SHARED DATABASE ---
@st.cache_resource
def get_global_data():
    return {
        "messages": {
            "The Citadel": {"# general": [], "# memes": []},
            "Deep Thoughts": {"# philosophy": [], "# logic": []}
        },
        "active_users": {},
        "user_xp": {} # Track message counts for levels
    }

global_db = get_global_data()
session_id = str(id(st.session_state))

# --- IDENTITY & XP SYNC ---
if "user_name" not in st.session_state:
    st.session_state.user_name = f"Gooner_{id(st.session_state) % 1000}"
if "my_status" not in st.session_state:
    st.session_state.my_status = "Chilling"
if session_id not in global_db["user_xp"]:
    global_db["user_xp"][session_id] = 0

# --- THEME LOGIC ---
with st.sidebar:
    st.title("Gooncord 💀")
    goon_mode = st.toggle("🟣 GOON MODE", value=False)

if goon_mode:
    st.markdown("""
        <style>
            .stApp { background-color: #000; color: #39ff14; }
            [data-testid="stSidebar"] { background-color: #1a0033; border-right: 2px solid #bc13fe; }
            .member-box { background-color: #000; border: 1px solid #bc13fe; color: #39ff14; box-shadow: 0 0 10px #bc13fe; padding: 8px; border-radius: 4px; margin-bottom: 5px; }
            .stChatMessage { background-color: #111; border: 1px solid #39ff14 !important; }
            h1, h2, h3, p, span, label { color: #39ff14 !important; }
            .stProgress > div > div > div > div { background-color: #bc13fe; }
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

# --- SIDEBAR ---
with st.sidebar:
    # XP / Level Progress
    xp = global_db["user_xp"][session_id]
    level = (xp // 5) + 1
    st.write(f"**Level {level} Gooner** ({xp % 5}/5 XP to next level)")
    st.progress((xp % 5) / 5)

    with st.expander("👤 Profile Settings"):
        temp_name = st.text_input("Username", value=st.session_state.user_name)
        temp_stat = st.text_input("Status", value=st.session_state.my_status)
        if st.button("Save Profile"):
            st.session_state.user_name = temp_name
            st.session_state.my_status = temp_stat
            global_db["active_users"][session_id] = {"name": temp_name, "status": temp_stat}
            st.rerun()

    global_db["active_users"][session_id] = {"name": st.session_state.user_name, "status": st.session_state.my_status}

    st.divider()
    server = st.selectbox("Select Server", list(global_db["messages"].keys()))
    channel = st.radio("Channels", list(global_db["messages"][server].keys()))
    
    st.divider()
    st.write("### 📤 Media Studio (2GB Limit)")
    
    recorded_audio = st.audio_input("Record Voice")
    if recorded_audio and st.button("🎤 Send Recording"):
        b64 = base64.b64encode(recorded_audio.read()).decode()
        global_db["messages"][server][channel].append({
            "user": st.session_state.user_name, "time": datetime.datetime.now().strftime("%I:%M %p"), 
            "content": "", "image": None, "audio": b64, "video": None
        })
        global_db["user_xp"][session_id] += 1
        st.rerun()

    uploaded_file = st.file_uploader("Upload Image/Video", type=["png", "jpg", "jpeg", "mp4", "mov"])
    if uploaded_file and st.button("🚀 Post File"):
        b64 = base64.b64encode(uploaded_file.getvalue()).decode()
        file_type = uploaded_file.type.split('/')[0]
        
        msg_data = {"user": st.session_state.user_name, "time": datetime.datetime.now().strftime("%I:%M %p"), 
                    "content": "", "image": None, "audio": None, "video": None}
        if file_type == "image": msg_data["image"] = b64
        elif file_type == "video": msg_data["video"] = b64
            
        global_db["messages"][server][channel].append(msg_data)
        global_db["user_xp"][session_id] += 1
        st.rerun()

# --- MAIN CHAT ---
chat_col, member_col = st.columns([4, 1])

with chat_col:
    st.header(f"💬 {channel}")
    for msg in global_db["messages"][server][channel]:
        with st.chat_message("user"):
            st.markdown(f"**{msg['user']}** <small style='color: gray;'>{msg['time']}</small>", unsafe_allow_html=True)
            if msg.get("content"): st.write(msg["content"])
            if msg.get("image"): st.image(f"data:image/png;base64,{msg['image']}", use_container_width=True)
            if msg.get("audio"): st.audio(base64.b64decode(msg["audio"]), format="audio/wav")
            if msg.get("video"): st.video(base64.b64decode(msg["video"]))

    if prompt := st.chat_input(f"Message {channel}"):
        global_db["messages"][server][channel].append({
            "user": st.session_state.user_name, "time": datetime.datetime.now().strftime("%I:%M %p"), 
            "content": prompt, "image": None, "audio": None, "video": None
        })
        global_db["user_xp"][session_id] += 1
        st.rerun()

# --- MEMBER LIST ---
with member_col:
    st.write("### Members")
    for uid, data in global_db["active_users"].items():
        user_xp = global_db["user_xp"].get(uid, 0)
        u_lvl = (user_xp // 5) + 1
        is_me = " (You)" if uid == session_id else ""
        st.markdown(f'<div class="member-box">🟢 <b>{data["name"]}</b> <small>(Lvl {u_lvl})</small>{is_me}<br><span class="status-text">{data["status"]}</span></div>', unsafe_allow_html=True)
    st.button("🔄 Refresh")
