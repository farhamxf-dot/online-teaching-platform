"""
ماژول کلاس درس
Classroom Module
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

ROOMS_FILE = Path("data/rooms.json")

def init_rooms_db():
    """Initialize rooms database"""
    ROOMS_FILE.parent.mkdir(exist_ok=True)
    if not ROOMS_FILE.exists():
        with open(ROOMS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False)

def load_rooms():
    """Load rooms from database"""
    init_rooms_db()
    with open(ROOMS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_room(room_data):
    """Save room to database"""
    rooms = load_rooms()
    rooms[room_data['id']] = room_data
    with open(ROOMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(rooms, f, ensure_ascii=False, indent=2)

def show():
    """Show classroom interface"""
    st.title("📚 کلاس درس")
    
    if st.session_state.user_role == "مدرس":
        show_teacher_view()
    else:
        show_student_view()

def show_teacher_view():
    """Show teacher classroom view"""
    tab1, tab2 = st.tabs(["ایجاد کلاس", "کلاس‌های من"])
    
    with tab1:
        st.subheader("ایجاد کلاس جدید")
        with st.form("create_room"):
            room_name = st.text_input("نام کلاس")
            room_desc = st.text_area("توضیحات")
            max_participants = st.number_input("حداکثر تعداد شرکت‌کنندگان", min_value=2, max_value=100, value=30)
            password = st.text_input("رمز عبور (اختیاری)", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("تاریخ شروع")
            with col2:
                start_time = st.time_input("ساعت شروع")
            
            enable_chat = st.checkbox("فعال‌سازی چت", value=True)
            enable_whiteboard = st.checkbox("فعال‌سازی تخته سفید", value=True)
            enable_screen_share = st.checkbox("فعال‌سازی اشتراک صفحه", value=True)
            
            submit = st.form_submit_button("ایجاد کلاس")
            
            if submit and room_name:
                room_id = f"room_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                room_data = {
                    'id': room_id,
                    'name': room_name,
                    'description': room_desc,
                    'teacher': st.session_state.username,
                    'max_participants': max_participants,
                    'password': password,
                    'start_date': str(start_date),
                    'start_time': str(start_time),
                    'features': {
                        'chat': enable_chat,
                        'whiteboard': enable_whiteboard,
                        'screen_share': enable_screen_share
                    },
                    'created_at': datetime.now().isoformat(),
                    'participants': [],
                    'status': 'scheduled'
                }
                save_room(room_data)
                st.success(f"کلاس با موفقیت ایجاد شد! کد کلاس: {room_id}")
    
    with tab2:
        st.subheader("کلاس‌های من")
        rooms = load_rooms()
        my_rooms = {k: v for k, v in rooms.items() if v['teacher'] == st.session_state.username}
        
        if my_rooms:
            for room_id, room in my_rooms.items():
                with st.expander(f"📖 {room['name']} - {room_id}"):
                    st.write(f"**توضیحات:** {room['description']}")
                    st.write(f"**تاریخ:** {room['start_date']} - ساعت: {room['start_time']}")
                    st.write(f"**شرکت‌کنندگان:** {len(room['participants'])} / {room['max_participants']}")
                    st.write(f"**وضعیت:** {room['status']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("شروع کلاس", key=f"start_{room_id}"):
                            room['status'] = 'active'
                            save_room(room)
                            st.session_state.room_id = room_id
                            st.success("کلاس شروع شد!")
                            st.rerun()
                    with col2:
                        if st.button("پایان کلاس", key=f"end_{room_id}"):
                            room['status'] = 'ended'
                            save_room(room)
                            st.success("کلاس پایان یافت!")
                            st.rerun()
                    with col3:
                        if st.button("حذف", key=f"del_{room_id}"):
                            rooms = load_rooms()
                            del rooms[room_id]
                            with open(ROOMS_FILE, 'w', encoding='utf-8') as f:
                                json.dump(rooms, f, ensure_ascii=False, indent=2)
                            st.success("کلاس حذف شد!")
                            st.rerun()
        else:
            st.info("شما هنوز کلاسی ایجاد نکرده‌اید")

def show_student_view():
    """Show student classroom view"""
    st.subheader("ورود به کلاس")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        room_code = st.text_input("کد کلاس را وارد کنید")
    with col2:
        room_password = st.text_input("رمز عبور (در صورت نیاز)", type="password")
    
    if st.button("ورود به کلاس"):
        rooms = load_rooms()
        if room_code in rooms:
            room = rooms[room_code]
            if room['password'] and room['password'] != room_password:
                st.error("رمز عبور اشتباه است")
            elif len(room['participants']) >= room['max_participants']:
                st.error("ظرفیت کلاس تکمیل است")
            elif room['status'] != 'active':
                st.warning("این کلاس هنوز شروع نشده است")
            else:
                if st.session_state.username not in room['participants']:
                    room['participants'].append(st.session_state.username)
                    save_room(room)
                st.session_state.room_id = room_code
                st.success(f"به کلاس {room['name']} خوش آمدید!")
                st.rerun()
        else:
            st.error("کد کلاس اشتباه است")
    
    st.divider()
    st.subheader("کلاس‌های فعال")
    rooms = load_rooms()
    active_rooms = {k: v for k, v in rooms.items() if v['status'] == 'active'}
    
    if active_rooms:
        for room_id, room in active_rooms.items():
            with st.expander(f"📖 {room['name']}"):
                st.write(f"**مدرس:** {room['teacher']}")
                st.write(f"**توضیحات:** {room['description']}")
                st.write(f"**شرکت‌کنندگان:** {len(room['participants'])} / {room['max_participants']}")
                st.code(f"کد کلاس: {room_id}")
                # Guest join option for students without password
                st.write("---")
                st.write("ورود به‌عنوان مهمان (بدون نیاز به حساب کاربری)")
                guest_name_key = f"guest_name_{room_id}"
                guest_name = st.text_input("نام نمایشی (اختیاری)", value="مهمان", key=guest_name_key)
                if st.button("ورود به‌عنوان مهمان", key=f"guest_join_{room_id}"):
                    if len(room['participants']) >= room['max_participants']:
                        st.error("ظرفیت کلاس تکمیل است")
                    else:
                        # create a guest username and set session state without password
                        guest_username = f"guest_{room_id}_{len(room['participants']) + 1}"
                        display_name = guest_name or guest_username
                        if guest_username not in room['participants']:
                            room['participants'].append(guest_username)
                            save_room(room)
                        # set minimal session info for guest
                        st.session_state.authenticated = True
                        st.session_state.username = display_name
                        st.session_state.user_role = "دانش‌آموز"
                        st.session_state.full_name = display_name
                        st.session_state.room_id = room_id
                        st.success(f"شما به عنوان {display_name} وارد کلاس {room['name']} شدید")
                        st.rerun()
    else:
        st.info("در حال حاضر کلاس فعالی وجود ندارد")
