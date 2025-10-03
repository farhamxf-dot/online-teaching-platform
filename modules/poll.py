"""
ماژول نظرسنجی و کوئیز
Poll and Quiz Module
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

POLLS_FILE = Path("data/polls.json")

def init_polls_db():
    """Initialize polls database"""
    POLLS_FILE.parent.mkdir(exist_ok=True)
    if not POLLS_FILE.exists():
        with open(POLLS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False)

def load_polls(room_id):
    """Load polls for a room"""
    init_polls_db()
    with open(POLLS_FILE, 'r', encoding='utf-8') as f:
        all_polls = json.load(f)
    return all_polls.get(room_id, [])

def save_poll(room_id, poll_data):
    """Save poll to database"""
    init_polls_db()
    with open(POLLS_FILE, 'r', encoding='utf-8') as f:
        all_polls = json.load(f)
    
    if room_id not in all_polls:
        all_polls[room_id] = []
    
    all_polls[room_id].append(poll_data)
    
    with open(POLLS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_polls, f, ensure_ascii=False, indent=2)

def update_poll(room_id, poll_id, updated_poll):
    """Update poll in database"""
    init_polls_db()
    with open(POLLS_FILE, 'r', encoding='utf-8') as f:
        all_polls = json.load(f)
    
    if room_id in all_polls:
        for idx, poll in enumerate(all_polls[room_id]):
            if poll['id'] == poll_id:
                all_polls[room_id][idx] = updated_poll
                break
    
    with open(POLLS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_polls, f, ensure_ascii=False, indent=2)

def show():
    """Show poll interface"""
    st.title("📊 نظرسنجی و کوئیز")
    
    if not st.session_state.room_id:
        st.warning("ابتدا باید وارد یک کلاس شوید")
        return
    
    st.info(f"کلاس فعال: {st.session_state.room_id}")
    
    if st.session_state.user_role == "مدرس":
        show_teacher_poll_view()
    else:
        show_student_poll_view()

def show_teacher_poll_view():
    """Show teacher's poll creation and management view"""
    
    tab1, tab2 = st.tabs(["ایجاد نظرسنجی", "مدیریت نظرسنجی‌ها"])
    
    with tab1:
        st.subheader("ایجاد نظرسنجی جدید")
        
        poll_type = st.selectbox("نوع:", ["نظرسنجی ساده", "کوئیز", "سوال چند جوابی"])
        
        poll_question = st.text_input("سوال:")
        
        num_options = st.number_input("تعداد گزینه‌ها:", min_value=2, max_value=10, value=4)
        
        options = []
        correct_answer = None
        
        for i in range(num_options):
            col1, col2 = st.columns([4, 1])
            with col1:
                option = st.text_input(f"گزینه {i+1}:", key=f"option_{i}")
                options.append(option)
            
            with col2:
                if poll_type == "کوئیز":
                    if st.checkbox("صحیح", key=f"correct_{i}"):
                        correct_answer = i
        
        col1, col2 = st.columns(2)
        with col1:
            allow_multiple = st.checkbox("اجازه انتخاب چند گزینه")
        with col2:
            show_results = st.checkbox("نمایش نتایج به شرکت‌کنندگان", value=True)
        
        time_limit = st.slider("مهلت پاسخ (دقیقه):", 0, 30, 5)
        
        if st.button("ایجاد نظرسنجی", type="primary"):
            if poll_question and all(options):
                poll_data = {
                    'id': f"poll_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'type': poll_type,
                    'question': poll_question,
                    'options': options,
                    'correct_answer': correct_answer,
                    'allow_multiple': allow_multiple,
                    'show_results': show_results,
                    'time_limit': time_limit,
                    'created_at': datetime.now().isoformat(),
                    'created_by': st.session_state.username,
                    'responses': {},
                    'status': 'active'
                }
                save_poll(st.session_state.room_id, poll_data)
                st.success("نظرسنجی با موفقیت ایجاد شد!")
                st.rerun()
            else:
                st.warning("لطفاً تمام فیلدها را پر کنید")
    
    with tab2:
        st.subheader("نظرسنجی‌های فعال")
        
        polls = load_polls(st.session_state.room_id)
        
        if not polls:
            st.info("هنوز نظرسنجی ایجاد نشده است")
            return
        
        for poll in polls:
            with st.expander(f"📋 {poll['question']}"):
                st.write(f"**نوع:** {poll['type']}")
                st.write(f"**وضعیت:** {poll['status']}")
                st.write(f"**تعداد پاسخ‌ها:** {len(poll['responses'])}")
                
                # Show results
                if poll['responses']:
                    st.write("### نتایج:")
                    
                    # Count votes for each option
                    vote_counts = {}
                    for option in poll['options']:
                        vote_counts[option] = 0
                    
                    for user, response in poll['responses'].items():
                        if isinstance(response, list):
                            for r in response:
                                if r in vote_counts:
                                    vote_counts[r] += 1
                        else:
                            if response in vote_counts:
                                vote_counts[response] += 1
                    
                    # Display results
                    total_votes = sum(vote_counts.values())
                    for option, count in vote_counts.items():
                        percentage = (count / total_votes * 100) if total_votes > 0 else 0
                        st.progress(percentage / 100)
                        st.write(f"{option}: {count} رأی ({percentage:.1f}%)")
                
                # Poll controls
                col1, col2 = st.columns(2)
                with col1:
                    if poll['status'] == 'active':
                        if st.button("پایان نظرسنجی", key=f"end_{poll['id']}"):
                            poll['status'] = 'closed'
                            update_poll(st.session_state.room_id, poll['id'], poll)
                            st.success("نظرسنجی بسته شد")
                            st.rerun()
                with col2:
                    if st.button("حذف", key=f"delete_{poll['id']}"):
                        polls = [p for p in polls if p['id'] != poll['id']]
                        with open(POLLS_FILE, 'w', encoding='utf-8') as f:
                            json.dump({st.session_state.room_id: polls}, f, 
                                    ensure_ascii=False, indent=2)
                        st.success("نظرسنجی حذف شد")
                        st.rerun()

def show_student_poll_view():
    """Show student's poll participation view"""
    
    st.subheader("نظرسنجی‌های فعال")
    
    polls = load_polls(st.session_state.room_id)
    active_polls = [p for p in polls if p['status'] == 'active']
    
    if not active_polls:
        st.info("در حال حاضر نظرسنجی فعالی وجود ندارد")
        return
    
    for poll in active_polls:
        with st.expander(f"📋 {poll['question']}", expanded=True):
            st.write(f"**نوع:** {poll['type']}")
            
            # Check if user already responded
            user_responded = st.session_state.username in poll['responses']
            
            if user_responded:
                st.success("✅ شما به این نظرسنجی پاسخ داده‌اید")
                
                if poll['show_results']:
                    st.write("### نتایج:")
                    vote_counts = {}
                    for option in poll['options']:
                        vote_counts[option] = 0
                    
                    for user, response in poll['responses'].items():
                        if isinstance(response, list):
                            for r in response:
                                if r in vote_counts:
                                    vote_counts[r] += 1
                        else:
                            if response in vote_counts:
                                vote_counts[response] += 1
                    
                    total_votes = sum(vote_counts.values())
                    for option, count in vote_counts.items():
                        percentage = (count / total_votes * 100) if total_votes > 0 else 0
                        st.progress(percentage / 100)
                        st.write(f"{option}: {count} رأی ({percentage:.1f}%)")
            else:
                # Show options for voting
                if poll['allow_multiple']:
                    selected = []
                    for option in poll['options']:
                        if st.checkbox(option, key=f"{poll['id']}_{option}"):
                            selected.append(option)
                    
                    if st.button("ثبت پاسخ", key=f"submit_{poll['id']}"):
                        if selected:
                            poll['responses'][st.session_state.username] = selected
                            update_poll(st.session_state.room_id, poll['id'], poll)
                            st.success("پاسخ شما ثبت شد!")
                            st.rerun()
                        else:
                            st.warning("لطفاً حداقل یک گزینه انتخاب کنید")
                else:
                    selected = st.radio("گزینه خود را انتخاب کنید:", 
                                      poll['options'], 
                                      key=f"radio_{poll['id']}")
                    
                    if st.button("ثبت پاسخ", key=f"submit_{poll['id']}"):
                        poll['responses'][st.session_state.username] = selected
                        update_poll(st.session_state.room_id, poll['id'], poll)
                        st.success("پاسخ شما ثبت شد!")
                        st.rerun()
                
                # Show time remaining
                if poll['time_limit'] > 0:
                    st.info(f"⏰ مهلت پاسخ: {poll['time_limit']} دقیقه")