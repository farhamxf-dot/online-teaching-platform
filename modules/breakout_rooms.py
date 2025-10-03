"""
ماژول اتاق‌های جانبی
Breakout Rooms Module
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

BREAKOUT_FILE = Path("data/breakout_rooms.json")

def init_breakout_db():
    """Initialize breakout rooms database"""
    BREAKOUT_FILE.parent.mkdir(exist_ok=True)
    if not BREAKOUT_FILE.exists():
        with open(BREAKOUT_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False)

def load_breakout_rooms(room_id):
    """Load breakout rooms for a class"""
    init_breakout_db()
    with open(BREAKOUT_FILE, 'r', encoding='utf-8') as f:
        all_rooms = json.load(f)
    return all_rooms.get(room_id, [])

def save_breakout_rooms(room_id, rooms):
    """Save breakout rooms"""
    init_breakout_db()
    with open(BREAKOUT_FILE, 'r', encoding='utf-8') as f:
        all_rooms = json.load(f)
    
    all_rooms[room_id] = rooms
    
    with open(BREAKOUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_rooms, f, ensure_ascii=False, indent=2)

def show():
    """Show breakout rooms interface"""
    st.title("🚪 اتاق‌های جانبی")
    
    if not st.session_state.room_id:
        st.warning("ابتدا باید وارد یک کلاس شوید")
        return
    
    st.info(f"کلاس فعال: {st.session_state.room_id}")
    
    if st.session_state.user_role == "مدرس":
        show_teacher_breakout_view()
    else:
        show_student_breakout_view()

def show_teacher_breakout_view():
    """Show teacher's breakout room management"""
    
    tab1, tab2 = st.tabs(["ایجاد اتاق‌ها", "مدیریت اتاق‌ها"])
    
    with tab1:
        st.subheader("ایجاد اتاق‌های جانبی")
        
        from modules.classroom import load_rooms
        rooms = load_rooms()
        room = rooms.get(st.session_state.room_id)
        
        if not room:
            st.error("کلاس یافت نشد")
            return
        
        participants = room['participants']
        
        if not participants:
            st.warning("هیچ شرکت‌کننده‌ای در کلاس نیست")
            return
        
        st.write(f"تعداد شرکت‌کنندگان: {len(participants)} نفر")
        
        # Automatic or manual assignment
        assignment_method = st.radio(
            "روش تقسیم:",
            ["تقسیم خودکار", "تقسیم دستی"]
        )
        
        if assignment_method == "تقسیم خودکار":
            num_rooms = st.number_input("تعداد اتاق‌ها:", min_value=2, max_value=10, value=3)
            
            if st.button("ایجاد اتاق‌ها", type="primary"):
                # Divide participants automatically
                room_size = len(participants) // num_rooms
                breakout_rooms = []
                
                for i in range(num_rooms):
                    start_idx = i * room_size
                    end_idx = start_idx + room_size if i < num_rooms - 1 else len(participants)
                    
                    room_participants = participants[start_idx:end_idx]
                    breakout_rooms.append({
                        'id': f"breakout_{i+1}",
                        'name': f"اتاق {i+1}",
                        'participants': room_participants,
                        'status': 'active',
                        'created_at': datetime.now().isoformat()
                    })
                
                save_breakout_rooms(st.session_state.room_id, breakout_rooms)
                st.success(f"{num_rooms} اتاق جانبی ایجاد شد!")
                st.rerun()
        
        else:  # Manual assignment
            num_rooms = st.number_input("تعداد اتاق‌ها:", min_value=2, max_value=10, value=3, key="manual_rooms")
            
            from modules.auth import load_users
            users = load_users()
            
            room_assignments = {}
            for i in range(num_rooms):
                st.write(f"### اتاق {i+1}")
                room_name = st.text_input(f"نام اتاق {i+1}:", value=f"اتاق {i+1}", key=f"name_{i}")
                selected = st.multiselect(
                    f"انتخاب شرکت‌کنندگان:",
                    participants,
                    key=f"participants_{i}",
                    format_func=lambda x: users.get(x, {}).get('full_name', x)
                )
                room_assignments[i] = {'name': room_name, 'participants': selected}
            
            if st.button("ایجاد اتاق‌های دستی", type="primary"):
                breakout_rooms = []
                for i, room_data in room_assignments.items():
                    if room_data['participants']:
                        breakout_rooms.append({
                            'id': f"breakout_{i+1}",
                            'name': room_data['name'],
                            'participants': room_data['participants'],
                            'status': 'active',
                            'created_at': datetime.now().isoformat()
                        })
                
                if breakout_rooms:
                    save_breakout_rooms(st.session_state.room_id, breakout_rooms)
                    st.success("اتاق‌های جانبی ایجاد شد!")
                    st.rerun()
                else:
                    st.warning("لطفاً حداقل یک اتاق با شرکت‌کننده ایجاد کنید")
    
    with tab2:
        st.subheader("اتاق‌های جانبی فعال")
        
        breakout_rooms = load_breakout_rooms(st.session_state.room_id)
        
        if not breakout_rooms:
            st.info("هنوز اتاق جانبی ایجاد نشده است")
            return
        
        from modules.auth import load_users
        users = load_users()
        
        for room in breakout_rooms:
            with st.expander(f"🚪 {room['name']} ({len(room['participants'])} نفر)"):
                st.write("**شرکت‌کنندگان:**")
                for participant in room['participants']:
                    user_info = users.get(participant, {})
                    st.write(f"- {user_info.get('full_name', participant)}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("ورود به اتاق", key=f"enter_{room['id']}"):
                        st.info("شما وارد اتاق شدید")
                
                with col2:
                    if st.button("ارسال پیام", key=f"msg_{room['id']}"):
                        msg = st.text_input("پیام:", key=f"msgtext_{room['id']}")
                        if msg:
                            st.success("پیام ارسال شد")
                
                with col3:
                    if st.button("بستن اتاق", key=f"close_{room['id']}"):
                        room['status'] = 'closed'
                        save_breakout_rooms(st.session_state.room_id, breakout_rooms)
                        st.success("اتاق بسته شد")
                        st.rerun()
        
        st.divider()
        
        # Global controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("بستن همه اتاق‌ها", type="primary"):
                for room in breakout_rooms:
                    room['status'] = 'closed'
                save_breakout_rooms(st.session_state.room_id, breakout_rooms)
                st.success("همه اتاق‌ها بسته شد")
                st.rerun()
        
        with col2:
            if st.button("حذف همه اتاق‌ها"):
                save_breakout_rooms(st.session_state.room_id, [])
                st.success("همه اتاق‌ها حذف شد")
                st.rerun()

def show_student_breakout_view():
    """Show student's breakout room view"""
    
    st.subheader("اتاق جانبی من")
    
    breakout_rooms = load_breakout_rooms(st.session_state.room_id)
    active_rooms = [r for r in breakout_rooms if r['status'] == 'active']
    
    if not active_rooms:
        st.info("هنوز اتاق جانبی ایجاد نشده است")
        return
    
    # Find user's assigned room
    user_room = None
    for room in active_rooms:
        if st.session_state.username in room['participants']:
            user_room = room
            break
    
    if not user_room:
        st.warning("شما به هیچ اتاق جانبی اختصاص داده نشده‌اید")
        return
    
    st.success(f"شما به **{user_room['name']}** اختصاص داده شده‌اید")
    
    st.write("### اعضای اتاق:")
    from modules.auth import load_users
    users = load_users()
    
    for participant in user_room['participants']:
        user_info = users.get(participant, {})
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"👤 {user_info.get('full_name', participant)}")
        with col2:
            if participant == st.session_state.username:
                st.write("(شما)")
    
    st.divider()
    
    # Room chat
    st.write("### گفتگوی اتاق")
    st.info("از منوی گفتگو برای چت در این اتاق استفاده کنید")
    
    if st.button("ورود به اتاق", type="primary"):
        st.success("شما وارد اتاق شدید!")