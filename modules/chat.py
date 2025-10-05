"""
ماژول گفتگو
Chat Module
"""

import streamlit as st
from modules import ui
import json
from pathlib import Path
from datetime import datetime

CHAT_FILE = Path("data/chats.json")


def init_chat_db():
    """Ensure chat database file exists"""
    CHAT_FILE.parent.mkdir(exist_ok=True)
    if not CHAT_FILE.exists():
        with open(CHAT_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)


def load_chats(room_id):
    """Return list of messages for a room"""
    init_chat_db()
    with open(CHAT_FILE, "r", encoding="utf-8") as f:
        all_chats = json.load(f)
    return all_chats.get(room_id, [])


def save_message(room_id, username, message, message_type="public", to=None):
    """Save a message. 'to' is optional recipient for private messages."""
    init_chat_db()
    with open(CHAT_FILE, "r", encoding="utf-8") as f:
        all_chats = json.load(f)

    if room_id not in all_chats:
        all_chats[room_id] = []

    entry = {
        "username": username,
        "message": message,
        "type": message_type,
        "timestamp": datetime.now().isoformat(),
    }
    if to:
        entry["to"] = to

    all_chats[room_id].append(entry)

    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chats, f, ensure_ascii=False, indent=2)


def show():
    """Top-level chat UI with public and private tabs"""
    st.title("💬 گفتگو")

    room_id = st.session_state.get("room_id")
    username = st.session_state.get("username")

    if not room_id:
        st.warning("ابتدا باید وارد یک کلاس شوید")
        return

    st.info(f"کلاس فعال: {room_id}")

    tab1, tab2 = st.tabs(["گفتگوی عمومی", "پیام خصوصی"])

    with tab1:
        show_public_chat(room_id, username)

    with tab2:
        show_private_chat(room_id, username)


def _render_message_bubble(msg, current_user):
    """Helper to render a message bubble HTML"""
    timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M")
    if msg.get("username") == current_user:
        who = "شما"
        bg = "#D1E7FF"
        align = "right"
    else:
        who = msg.get("username")
        bg = "#F0F0F0"
        align = "right"

    html = f"""
    <div style='text-align: {align}; margin: 10px; padding: 10px; background-color: {bg}; border-radius: 10px;'>
        <strong>{who}</strong> <small>({timestamp})</small><br>
        {msg.get('message')}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def show_public_chat(room_id, username):
    st.subheader("گفتگوی عمومی")

    messages = load_chats(room_id)
    public_messages = [m for m in messages if m.get("type") == "public"]

    chat_container = st.container()
    with chat_container:
        for msg in public_messages:
            _render_message_bubble(msg, username)

    # Public message input
    with st.form("public_chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            new_message = st.text_input("پیام:", label_visibility="collapsed", placeholder="پیام خود را بنویسید...")
        with col2:
            send = st.form_submit_button("ارسال")

        if send and new_message:
            save_message(room_id, username, new_message, "public")
            ui.safe_rerun()

    # Quick responses
    st.divider()
    st.write("پاسخ‌های سریع:")
    col1, col2, col3, col4 = st.columns(4)
    quick_responses = {"👍": "موافقم", "👏": "عالی بود", "🙋": "سوال دارم", "✅": "متوجه شدم"}
    cols = [col1, col2, col3, col4]
    for idx, (emoji, text) in enumerate(quick_responses.items()):
        with cols[idx]:
            if st.button(f"{emoji} {text}"):
                save_message(room_id, username, f"{emoji} {text}", "public")
                ui.safe_rerun()


def show_private_chat(room_id, username):
    st.subheader("پیام خصوصی")

    # Load room participants
    from modules.classroom import load_rooms
    rooms = load_rooms()

    if room_id not in rooms:
        st.error("کلاس یافت نشد")
        return

    room = rooms[room_id]
    participants = room.get("participants", []) + [room.get("teacher")]
    participants = [p for p in participants if p and p != username]

    if not participants:
        st.info("هیچ شرکت‌کننده دیگری در کلاس نیست")
        return

    selected_user = st.selectbox("انتخاب کاربر:", participants)

    messages = load_chats(room_id)
    # Show only private messages between current user and selected_user
    private_messages = [
        m for m in messages if m.get("type") == "private" and (
            (m.get("username") == username and m.get("to") == selected_user) or
            (m.get("username") == selected_user and m.get("to") == username)
        )
    ]

    chat_container = st.container()
    with chat_container:
        for msg in private_messages:
            _render_message_bubble(msg, username)

    # Private message input
    with st.form("private_chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            private_message = st.text_input("پیام خصوصی:", label_visibility="collapsed", placeholder=f"پیام به {selected_user}...")
        with col2:
            send_private = st.form_submit_button("ارسال")

        if send_private and private_message:
            save_message(room_id, username, private_message, "private", to=selected_user)
            ui.safe_rerun()
