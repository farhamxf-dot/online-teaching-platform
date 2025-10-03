"""
ماژول احراز هویت
Authentication Module
"""

import streamlit as st
import hashlib
import json
from pathlib import Path

# User database file
USERS_FILE = Path("data/users.json")

def init_users_db():
    """Initialize users database"""
    USERS_FILE.parent.mkdir(exist_ok=True)
    if not USERS_FILE.exists():
        default_users = {
            "admin": {
                "password": hashlib.sha256("admin123".encode()).hexdigest(),
                "role": "مدرس",
                "full_name": "مدیر سیستم"
            },
            "teacher1": {
                "password": hashlib.sha256("teacher123".encode()).hexdigest(),
                "role": "مدرس",
                "full_name": "معلم اول"
            },
            "student1": {
                "password": hashlib.sha256("student123".encode()).hexdigest(),
                "role": "دانش‌آموز",
                "full_name": "دانش‌آموز اول"
            }
        }
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, ensure_ascii=False, indent=2)

def load_users():
    """Load users from database"""
    init_users_db()
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_user(username, password, role, full_name):
    """Save new user to database"""
    users = load_users()
    users[username] = {
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "role": role,
        "full_name": full_name
    }
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def verify_credentials(username, password):
    """Verify user credentials"""
    users = load_users()
    if username in users:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if users[username]["password"] == password_hash:
            return True, users[username]
    return False, None

def show_login():
    """Show login interface"""
    st.title("🎓 پلتفرم آموزش آنلاین")
    st.subheader("ورود به سیستم")
    
    tab1, tab2 = st.tabs(["ورود", "ثبت‌نام"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("نام کاربری")
            password = st.text_input("رمز عبور", type="password")
            submit = st.form_submit_button("ورود")
            
            if submit:
                if username and password:
                    success, user_data = verify_credentials(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_role = user_data["role"]
                        st.session_state.full_name = user_data["full_name"]
                        st.success("ورود موفق!")
                        st.rerun()
                    else:
                        st.error("نام کاربری یا رمز عبور اشتباه است")
                else:
                    st.warning("لطفاً تمام فیلدها را پر کنید")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("نام کاربری", key="reg_user")
            new_password = st.text_input("رمز عبور", type="password", key="reg_pass")
            confirm_password = st.text_input("تکرار رمز عبور", type="password")
            full_name = st.text_input("نام و نام خانوادگی")
            role = st.selectbox("نقش", ["دانش‌آموز", "مدرس"])
            register = st.form_submit_button("ثبت‌نام")
            
            if register:
                if new_username and new_password and full_name:
                    if new_password != confirm_password:
                        st.error("رمز عبور و تکرار آن مطابقت ندارند")
                    elif new_username in load_users():
                        st.error("این نام کاربری قبلاً استفاده شده است")
                    else:
                        save_user(new_username, new_password, role, full_name)
                        st.success("ثبت‌نام موفق! اکنون می‌توانید وارد شوید")
                else:
                    st.warning("لطفاً تمام فیلدها را پر کنید")
    
    st.info("💡 اطلاعات پیش‌فرض:\n- admin / admin123 (مدرس)\n- teacher1 / teacher123 (مدرس)\n- student1 / student123 (دانش‌آموز)")

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_role = None
    st.session_state.full_name = None
