"""
ماژول مدیریت شرکت‌کنندگان
Participant Manager Module
"""

import streamlit as st
from modules.classroom import load_rooms, save_room
from modules.auth import load_users
from datetime import datetime

def show():
    """Show participant manager interface"""
    st.title("👥 مدیریت شرکت‌کنندگان")
    
    if not st.session_state.room_id:
        st.warning("ابتدا باید وارد یک کلاس شوید")
        return
    
    rooms = load_rooms()
    if st.session_state.room_id not in rooms:
        st.error("کلاس یافت نشد")
        return
    
    room = rooms[st.session_state.room_id]
    
    st.info(f"کلاس: {room['name']}")
    
    if st.session_state.user_role == "مدرس":
        show_teacher_participant_view(room)
    else:
        show_student_participant_view(room)

def show_teacher_participant_view(room):
    """Show teacher's participant management view"""
    
    tab1, tab2, tab3 = st.tabs(["لیست شرکت‌کنندگان", "دعوت", "مجوزها"])
    
    with tab1:
        st.subheader("شرکت‌کنندگان فعال")
        
        participants = room['participants']
        teacher = room['teacher']
        
        # Teacher info
        st.markdown("### 👨‍🏫 مدرس")
        users = load_users()
        teacher_info = users.get(teacher, {})
        st.write(f"**{teacher_info.get('full_name', teacher)}** (@{teacher})")
        
        st.divider()
        
        # Participants list
        st.markdown(f"### 👨‍🎓 دانش‌آموزان ({len(participants)} نفر)")
        
        if participants:
            for idx, participant in enumerate(participants):
                user_info = users.get(participant, {})
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{user_info.get('full_name', participant)}** (@{participant})")
                
                with col2:
                    if st.button("🔇 قطع صدا", key=f"mute_{idx}"):
                        st.success(f"صدای {participant} قطع شد")
                
                with col3:
                    if st.button("📹 قطع دوربین", key=f"cam_{idx}"):
                        st.success(f"دوربین {participant} قطع شد")
                
                with col4:
                    if st.button("🚫 اخراج", key=f"kick_{idx}"):
                        participants.remove(participant)
                        room['participants'] = participants
                        save_room(room)
                        st.warning(f"{participant} از کلاس اخراج شد")
                        st.rerun()
                
                st.divider()
        else:
            st.info("هنوز کسی به کلاس نپیوسته است")
        
        # Bulk actions
        st.subheader("عملیات گروهی")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔇 قطع صدای همه"):
                st.success("صدای همه قطع شد")
        with col2:
            if st.button("🔊 روشن صدای همه"):
                st.success("صدای همه روشن شد")
        with col3:
            if st.button("📹 قطع دوربین همه"):
                st.success("دوربین همه قطع شد")
    
    with tab2:
        st.subheader("دعوت از شرکت‌کنندگان")
        
        st.write("### لینک دعوت")
        invite_link = f"کد کلاس: {st.session_state.room_id}"
        st.code(invite_link)
        
        if st.button("کپی لینک"):
            st.success("لینک کپی شد!")
        
        st.divider()
        
        st.write("### ارسال دعوت‌نامه ایمیلی")
        email_addresses = st.text_area("آدرس‌های ایمیل (هر خط یک ایمیل):")
        custom_message = st.text_area("پیام سفارشی:")
        
        if st.button("ارسال دعوت‌نامه"):
            if email_addresses:
                st.success(f"دعوت‌نامه به {len(email_addresses.splitlines())} نفر ارسال شد")
            else:
                st.warning("لطفاً حداقل یک ایمیل وارد کنید")
    
    with tab3:
        st.subheader("تنظیمات مجوزها")
        
        st.write("### مجوزهای عمومی")
        
        allow_unmute = st.checkbox("اجازه روشن کردن میکروفون", value=True)
        allow_camera = st.checkbox("اجازه روشن کردن دوربین", value=True)
        allow_chat = st.checkbox("اجازه استفاده از چت", value=True)
        allow_screen_share = st.checkbox("اجازه اشتراک صفحه", value=False)
        allow_whiteboard = st.checkbox("اجازه استفاده از تخته سفید", value=False)
        
        if st.button("ذخیره تنظیمات"):
            st.success("تنظیمات ذخیره شد")
        
        st.divider()
        
        st.write("### لیست سیاه")
        blocked_users = st.multiselect("کاربران مسدود شده:", [])
        
        st.write("### لیست انتظار")
        waiting_users = st.multiselect("کاربران در انتظار تأیید:", [])

def show_student_participant_view(room):
    """Show student's participant view"""
    
    st.subheader("لیست شرکت‌کنندگان")
    
    participants = room['participants']
    teacher = room['teacher']
    
    # Teacher info
    st.markdown("### 👨‍🏫 مدرس")
    users = load_users()
    teacher_info = users.get(teacher, {})
    st.write(f"**{teacher_info.get('full_name', teacher)}**")
    
    st.divider()
    
    # Participants list
    st.markdown(f"### 👨‍🎓 دانش‌آموزان ({len(participants)} نفر)")
    
    if participants:
        for participant in participants:
            user_info = users.get(participant, {})
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{user_info.get('full_name', participant)}**")
            with col2:
                # Online status indicator
                st.markdown("🟢 آنلاین")
            
            st.divider()
    else:
        st.info("هنوز کسی دیگر به کلاس نپیوسته است")
