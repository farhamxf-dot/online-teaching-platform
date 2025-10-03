"""
پلتفرم آموزش آنلاین - فایل اصلی
Online Teaching Platform - Main File
"""

import streamlit as st
from pathlib import Path
import sys

# Add modules directory to path
sys.path.append(str(Path(__file__).parent))

# Import modules
from modules import auth
from modules import classroom
from modules import whiteboard
from modules import chat
from modules import screen_share
from modules import file_manager
from modules import participant_manager
from modules import poll
from modules import breakout_rooms
from modules import recording
from modules import ui

# Page configuration
st.set_page_config(
    page_title="پلتفرم آموزش آنلاین",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# RTL CSS for Persian
## Use central UI helpers for polished styling and layout
ui.inject_css()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'room_id' not in st.session_state:
    st.session_state.room_id = None

def main():
    """Main application function"""
    # Authentication
    if not st.session_state.authenticated:
        auth.show_login()
        return

    # Header
    ui.render_header("پلتفرم آموزش آنلاین", f"خوش آمدید، {st.session_state.username}")

    # Sidebar (polished)
    menu_options = [
        "کلاس درس",
        "تخته سفید",
        "گفتگو",
        "اشتراک صفحه",
        "مدیریت فایل",
        "شرکت‌کنندگان",
        "نظرسنجی",
        "اتاق‌های جانبی",
        "ضبط جلسه",
    ]

    selected, did_logout = ui.render_sidebar(st.session_state.username, st.session_state.user_role, menu_options)
    if did_logout:
        auth.logout()
        st.rerun()

    # Main content area
    if selected == "کلاس درس":
        classroom.show()
    elif selected == "تخته سفید":
        whiteboard.show()
    elif selected == "گفتگو":
        chat.show()
    elif selected == "اشتراک صفحه":
        screen_share.show()
    elif selected == "مدیریت فایل":
        file_manager.show()
    elif selected == "شرکت‌کنندگان":
        participant_manager.show()
    elif selected == "نظرسنجی":
        poll.show()
    elif selected == "اتاق‌های جانبی":
        breakout_rooms.show()
    elif selected == "ضبط جلسه":
        recording.show()

if __name__ == "__main__":
    main()
