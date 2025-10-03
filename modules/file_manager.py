"""
ماژول مدیریت فایل
File Manager Module
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
import os

FILES_DB = Path("data/files.json")

def init_files_db():
    """Initialize files database"""
    FILES_DB.parent.mkdir(exist_ok=True)
    if not FILES_DB.exists():
        with open(FILES_DB, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False)

def load_files(room_id):
    """Load files for a room"""
    init_files_db()
    with open(FILES_DB, 'r', encoding='utf-8') as f:
        all_files = json.load(f)
    return all_files.get(room_id, [])

def save_file_info(room_id, file_info):
    """Save file information"""
    init_files_db()
    with open(FILES_DB, 'r', encoding='utf-8') as f:
        all_files = json.load(f)
    
    if room_id not in all_files:
        all_files[room_id] = []
    
    all_files[room_id].append(file_info)
    
    with open(FILES_DB, 'w', encoding='utf-8') as f:
        json.dump(all_files, f, ensure_ascii=False, indent=2)

def show():
    """Show file manager interface"""
    st.title("📁 مدیریت فایل")
    
    if not st.session_state.room_id:
        st.warning("ابتدا باید وارد یک کلاس شوید")
        return
    
    st.info(f"کلاس فعال: {st.session_state.room_id}")
    
    tab1, tab2 = st.tabs(["آپلود فایل", "فایل‌های کلاس"])
    
    with tab1:
        show_upload_section()
    
    with tab2:
        show_files_list()

def show_upload_section():
    """Show file upload section"""
    st.subheader("آپلود فایل جدید")
    
    uploaded_file = st.file_uploader(
        "فایل خود را انتخاب کنید",
        type=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 
              'txt', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'zip'],
        key="file_uploader"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            file_description = st.text_input("توضیحات فایل:")
            file_category = st.selectbox(
                "دسته‌بندی:",
                ["جزوه درسی", "تمرین", "پروژه", "منابع اضافی", "سایر"]
            )
        
        with col2:
            st.write("**اطلاعات فایل:**")
            st.write(f"نام: {uploaded_file.name}")
            st.write(f"اندازه: {uploaded_file.size / 1024:.2f} KB")
            st.write(f"نوع: {uploaded_file.type}")
        
        if st.button("آپلود فایل", type="primary"):
            # Save file
            file_dir = Path(f"data/uploads/{st.session_state.room_id}")
            file_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = file_dir / uploaded_file.name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Save file info to database
            file_info = {
                'filename': uploaded_file.name,
                'description': file_description,
                'category': file_category,
                'size': uploaded_file.size,
                'uploaded_by': st.session_state.username,
                'upload_date': datetime.now().isoformat(),
                'path': str(file_path)
            }
            save_file_info(st.session_state.room_id, file_info)
            
            st.success(f"فایل {uploaded_file.name} با موفقیت آپلود شد!")
            st.rerun()

def show_files_list():
    """Show list of uploaded files"""
    st.subheader("فایل‌های آپلود شده")
    
    files = load_files(st.session_state.room_id)
    
    if not files:
        st.info("هنوز فایلی آپلود نشده است")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox(
            "فیلتر بر اساس دسته:",
            ["همه", "جزوه درسی", "تمرین", "پروژه", "منابع اضافی", "سایر"]
        )
    with col2:
        sort_by = st.selectbox("مرتب‌سازی:", ["جدیدترین", "قدیمی‌ترین", "نام فایل"])
    
    # Filter files
    if filter_category != "همه":
        files = [f for f in files if f['category'] == filter_category]
    
    # Sort files
    if sort_by == "جدیدترین":
        files = sorted(files, key=lambda x: x['upload_date'], reverse=True)
    elif sort_by == "قدیمی‌ترین":
        files = sorted(files, key=lambda x: x['upload_date'])
    else:
        files = sorted(files, key=lambda x: x['filename'])
    
    # Display files
    for idx, file in enumerate(files):
        with st.expander(f"📄 {file['filename']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**توضیحات:** {file['description']}")
                st.write(f"**دسته:** {file['category']}")
                st.write(f"**آپلود شده توسط:** {file['uploaded_by']}")
                upload_date = datetime.fromisoformat(file['upload_date'])
                st.write(f"**تاریخ:** {upload_date.strftime('%Y/%m/%d - %H:%M')}")
                st.write(f"**حجم:** {file['size'] / 1024:.2f} KB")
            
            with col2:
                file_path = Path(file['path'])
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            "⬇️ دانلود",
                            f,
                            file_name=file['filename'],
                            key=f"download_{idx}"
                        )
                    
                    # Delete button (only for uploader or teacher)
                    if (st.session_state.username == file['uploaded_by'] or 
                        st.session_state.user_role == "مدرس"):
                        if st.button("🗑️ حذف", key=f"delete_{idx}"):
                            os.remove(file_path)
                            files.remove(file)
                            with open(FILES_DB, 'w', encoding='utf-8') as f:
                                json.dump({st.session_state.room_id: files}, f, 
                                        ensure_ascii=False, indent=2)
                            st.success("فایل حذف شد")
                            st.rerun()
