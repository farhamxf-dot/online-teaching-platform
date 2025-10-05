"""
ماژول ضبط جلسه
Recording Module
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timedelta

RECORDINGS_FILE = Path("data/recordings.json")

def init_recordings_db():
    """Initialize recordings database"""
    RECORDINGS_FILE.parent.mkdir(exist_ok=True)
    if not RECORDINGS_FILE.exists():
        with open(RECORDINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False)

def load_recordings(room_id):
    """Load recordings for a room"""
    init_recordings_db()
    with open(RECORDINGS_FILE, 'r', encoding='utf-8') as f:
        all_recordings = json.load(f)
    return all_recordings.get(room_id, [])

def save_recording(room_id, recording_data):
    """Save recording information"""
    init_recordings_db()
    with open(RECORDINGS_FILE, 'r', encoding='utf-8') as f:
        all_recordings = json.load(f)
    
    if room_id not in all_recordings:
        all_recordings[room_id] = []
    
    all_recordings[room_id].append(recording_data)
    
    with open(RECORDINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_recordings, f, ensure_ascii=False, indent=2)

def show():
    """Show recording interface"""
    st.title("🎥 ضبط جلسه")
    
    if not st.session_state.room_id:
        st.warning("ابتدا باید وارد یک کلاس شوید")
        return
    
    st.info(f"کلاس فعال: {st.session_state.room_id}")
    
    if st.session_state.user_role == "مدرس":
        show_teacher_recording_view()
    else:
        show_student_recording_view()

def show_teacher_recording_view():
    """Show teacher's recording controls"""
    
    tab1, tab2, tab3 = st.tabs(["ضبط جلسه", "ضبط‌های ذخیره شده", "تنظیمات"])
    
    with tab1:
        st.subheader("کنترل ضبط")
        
        # Initialize recording state
        if 'recording_active' not in st.session_state:
            st.session_state.recording_active = False
        if 'recording_start_time' not in st.session_state:
            st.session_state.recording_start_time = None
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if not st.session_state.recording_active:
                if st.button("🔴 شروع ضبط", type="primary"):
                    st.session_state.recording_active = True
                    st.session_state.recording_start_time = datetime.now()
                    st.success("ضبط شروع شد!")
                    st.rerun()
        
        with col2:
            if st.session_state.recording_active:
                if st.button("⏸️ مکث"):
                    st.info("ضبط متوقف شد")
        
        with col3:
            if st.session_state.recording_active:
                if st.button("⏹️ پایان و ذخیره"):
                    end_time = datetime.now()
                    duration = end_time - st.session_state.recording_start_time
                    
                    recording_data = {
                        'id': f"rec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        'start_time': st.session_state.recording_start_time.isoformat(),
                        'end_time': end_time.isoformat(),
                        'duration': str(duration),
                        'recorded_by': st.session_state.username,
                        'file_size': '0 MB',  # Placeholder
                        # Where the recorded file will be stored (teacher can attach/upload later)
                        'file_path': str(Path('recordings') / f"{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"),
                        'status': 'processing'
                    }
                    
                    save_recording(st.session_state.room_id, recording_data)
                    
                    st.session_state.recording_active = False
                    st.session_state.recording_start_time = None
                    st.success("ضبط پایان یافت و ذخیره شد!")
                    st.rerun()
        
        if st.session_state.recording_active:
            st.divider()
            
            # Show recording info
            elapsed = datetime.now() - st.session_state.recording_start_time
            hours, remainder = divmod(elapsed.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #ffebee; 
                        border-radius: 10px; border: 2px solid #f44336;'>
                <h2 style='color: #f44336; margin: 0;'>🔴 در حال ضبط</h2>
                <h1 style='margin: 10px 0; font-family: monospace;'>
                    {hours:02d}:{minutes:02d}:{seconds:02d}
                </h1>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("### تنظیمات فعال ضبط:")
            col1, col2 = st.columns(2)
            with col1:
                st.checkbox("ضبط صدا", value=True, disabled=True, key="active_record_audio")
                st.checkbox("ضبط ویدیو", value=True, disabled=True, key="active_record_video")
            with col2:
                st.checkbox("ضبط صفحه", value=True, disabled=True, key="active_record_screen")
                st.checkbox("ضبط چت", value=True, disabled=True, key="active_record_chat")
        else:
            st.info("برای شروع ضبط، دکمه 'شروع ضبط' را بزنید")
    
    with tab2:
        st.subheader("ضبط‌های ذخیره شده")
        
        recordings = load_recordings(st.session_state.room_id)
        
        if not recordings:
            st.info("هنوز ضبطی ذخیره نشده است")
        else:
            for idx, rec in enumerate(recordings):
                with st.expander(f"🎥 ضبط {idx + 1} - {rec['id']}"):
                    start_dt = datetime.fromisoformat(rec['start_time'])
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**تاریخ:** {start_dt.strftime('%Y/%m/%d')}")
                        st.write(f"**ساعت شروع:** {start_dt.strftime('%H:%M:%S')}")
                        st.write(f"**مدت:** {rec['duration']}")
                        st.write(f"**وضعیت:** {rec['status']}")
                        st.write(f"**ضبط شده توسط:** {rec['recorded_by']}")
                    
                    with col2:
                        file_path = rec.get('file_path')
                        file_exists = file_path and Path(file_path).exists()

                        if rec['status'] == 'ready' and file_exists:
                            if st.button("⬇️ دانلود", key=f"dl_{rec['id']}"):
                                st.success("دانلود شروع شد")

                            if st.button("▶️ پخش", key=f"play_{rec['id']}"):
                                st.video(file_path)
                        else:
                            st.warning("در حال پردازش... یا فایل هنوز پیوست نشده است")
                            # Allow teacher to upload the actual recorded file to mark it ready
                            uploaded = st.file_uploader("آپلود فایل ضبط (mp4)", type=['mp4', 'mov', 'avi'], key=f"upload_{rec['id']}")
                            if uploaded is not None:
                                # save uploaded file to the recording file_path
                                out_path = Path(rec.get('file_path') or (Path('recordings') / f"{rec['id']}.mp4"))
                                out_path.parent.mkdir(parents=True, exist_ok=True)
                                with open(out_path, 'wb') as f:
                                    f.write(uploaded.getbuffer())
                                # update metadata
                                recordings = load_recordings(st.session_state.room_id)
                                for r in recordings:
                                    if r['id'] == rec['id']:
                                        r['file_path'] = str(out_path)
                                        r['file_size'] = f"{out_path.stat().st_size // 1024} KB"
                                        r['status'] = 'ready'
                                with open(RECORDINGS_FILE, 'w', encoding='utf-8') as f:
                                    json.dump({st.session_state.room_id: recordings}, f, ensure_ascii=False, indent=2)
                                st.success("فایل ضبط پیوست شد و آماده پخش است")
                                st.rerun()
                    
                    # Additional options
                    st.divider()
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("✏️ ویرایش نام", key=f"edit_{rec['id']}"):
                            st.info("ویرایش نام")
                    
                    with col2:
                        if st.button("🔗 اشتراک‌گذاری", key=f"share_{rec['id']}"):
                            share_link = f"https://example.com/recording/{rec['id']}"
                            st.code(share_link)
                            st.success("لینک اشتراک‌گذاری ایجاد شد!")
                    
                    with col3:
                        if st.button("🗑️ حذف", key=f"del_{rec['id']}"):
                            # delete associated file if exists
                            try:
                                fp = rec.get('file_path')
                                if fp and Path(fp).exists():
                                    Path(fp).unlink()
                            except Exception:
                                pass

                            recordings.remove(rec)
                            with open(RECORDINGS_FILE, 'w', encoding='utf-8') as f:
                                json.dump({st.session_state.room_id: recordings}, f, 
                                        ensure_ascii=False, indent=2)
                            st.success("ضبط حذف شد")
                            st.rerun()
    
    with tab3:
        st.subheader("تنظیمات ضبط")
        
        st.write("### کیفیت ضبط")
        video_quality = st.select_slider(
            "کیفیت ویدیو:",
            options=['پایین (360p)', 'متوسط (480p)', 'بالا (720p)', 'خیلی بالا (1080p)'],
            value='بالا (720p)'
        )
        
        audio_quality = st.select_slider(
            "کیفیت صدا:",
            options=['پایین', 'متوسط', 'بالا'],
            value='بالا'
        )
        
        st.divider()
        
        st.write("### محتوای ضبط")
        record_video = st.checkbox("ضبط ویدیو دوربین", value=True, key="setting_record_video")
        record_audio = st.checkbox("ضبط صدا", value=True, key="setting_record_audio")
        record_screen = st.checkbox("ضبط اشتراک صفحه", value=True, key="setting_record_screen")
        record_whiteboard = st.checkbox("ضبط تخته سفید", value=True, key="setting_record_whiteboard")
        record_chat = st.checkbox("ضبط چت", value=False, key="setting_record_chat")

        st.divider()
        
        st.write("### ذخیره‌سازی")
        auto_save = st.checkbox("ذخیره خودکار", value=True)
        save_location = st.text_input("مسیر ذخیره:", value="recordings/")
        
        if st.button("ذخیره تنظیمات"):
            st.success("تنظیمات ذخیره شد!")

def show_student_recording_view():
    """Show student's recording view"""
    
    st.subheader("ضبط‌های کلاس")
    
    recordings = load_recordings(st.session_state.room_id)
    ready_recordings = [r for r in recordings if r['status'] == 'ready']
    
    if not ready_recordings:
        st.info("هنوز ضبط آماده‌ای برای مشاهده وجود ندارد")
        return
    
    for idx, rec in enumerate(ready_recordings):
        with st.expander(f"🎥 ضبط {idx + 1}"):
            start_dt = datetime.fromisoformat(rec['start_time'])
            
            st.write(f"**تاریخ:** {start_dt.strftime('%Y/%m/%d')}")
            st.write(f"**ساعت:** {start_dt.strftime('%H:%M:%S')}")
            st.write(f"**مدت:** {rec['duration']}")
            
            col1, col2 = st.columns(2)

            file_path = rec.get('file_path')
            file_exists = file_path and Path(file_path).exists()

            with col1:
                if file_exists:
                    if st.button("▶️ پخش آنلاین", key=f"play_{idx}"):
                        st.video(file_path)
                else:
                    st.info("فایل ضبط هنوز پیوست نشده است")

            with col2:
                if file_exists:
                    if st.button("⬇️ دانلود", key=f"download_{idx}"):
                        st.success("دانلود شروع شد!")
                else:
                    if st.button("درخواست فایل از مدرس", key=f"req_{idx}"):
                        st.info("درخواست ارسال فایل برای مدرس فرستاده شد")
