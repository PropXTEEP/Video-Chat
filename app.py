import streamlit as st
import streamlit.components.v1 as components

# --- Page Config ---
st.set_page_config(
    page_title="Streamlit Video Conference",
    page_icon="📹",
    layout="wide"
)

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")
    
    # User inputs
    username = st.text_input("Your Name", value="User")
    room_name = st.text_input("Room Name", value="StreamlitConferenceRoom")
    
    st.markdown("---")
    st.markdown(
        """
        **How to use:**
        1. Enter a **Room Name** (share this with your team).
        2. Enter your **Name**.
        3. The video conference will load automatically.
        4. Send the URL to up to 2 other people to join!
        """
    )
    
    st.warning("Note: You must allow camera/microphone permissions in your browser.")

# --- Main Interface ---
st.title("📹 Live Video Conference")

# Sanitize room name to ensure valid URL
# Replaces spaces with dashes and removes special characters
safe_room_name = "".join(c if c.isalnum() else "-" for c in room_name).strip("-")

if not safe_room_name:
    st.info("Please enter a room name in the sidebar to start.")
else:
    # --- Jitsi Meet Embed ---
    # We use the public Jitsi Meet instance.
    # We construct a URL with the room name and user display name.
    
    jitsi_url = f"https://meet.jit.si/{safe_room_name}"
    
    # Jitsi allows passing config via hash params, but for simple embedding,
    # just the URL is enough. The user will set their name inside the UI 
    # if not passed via API, but we can try to pass it if Jitsi supports deep linking specific params.
    # For stability, we stick to the clean room URL.

    st.success(f"Connected to room: **{safe_room_name}**")
    
    # Create a container for the video
    with st.container():
        # Embed Jitsi using an iframe. 
        # 'allow' parameters are crucial for browser permissions.
        components.html(
            f"""
            <iframe allow="camera; microphone; display-capture; fullscreen" 
                    src="{jitsi_url}" 
                    style="height: 600px; width: 100%; border: none;">
            </iframe>
            """,
            height=600,
        )
