"""
ماژول اشتراک صفحه
Screen Share Module
"""

import streamlit as st
from pathlib import Path
import base64

def show():
    """Show screen share interface"""
    st.title("🖥️ اشتراک صفحه")
    
    if not st.session_state.room_id:
        st.warning("ابتدا باید وارد یک کلاس شوید")
        return
    
    st.info(f"کلاس فعال: {st.session_state.room_id}")
    
    # Only teachers can share screen
    if st.session_state.user_role == "مدرس":
        show_teacher_screen_share()
    else:
        show_student_screen_view()

def show_teacher_screen_share():
    """Show teacher screen share options"""
    st.subheader("اشتراک‌گذاری صفحه و محتوا")
    
    tab1, tab2, tab3 = st.tabs(["ارائه تصویر", "ارائه ویدیو", "اشتراک لینک"])
    
    with tab1:
        st.write("### آپلود و ارائه تصویر")
        uploaded_image = st.file_uploader("تصویر خود را انتخاب کنید",
                                         type=['png', 'jpg', 'jpeg', 'gif'],
                                         key="image_upload")
        
        if uploaded_image:
            st.image(uploaded_image, caption="تصویر ارائه شده", use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("شروع ارائه تصویر"):
                    # Save image for sharing
                    img_path = Path(f"data/screen_share/{st.session_state.room_id}_image.png")
                    img_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(img_path, 'wb') as f:
                        f.write(uploaded_image.getbuffer())
                    st.success("تصویر در حال ارائه است")
            
            with col2:
                if st.button("توقف ارائه"):
                    st.info("ارائه متوقف شد")
    
    with tab2:
        st.write("### آپلود و ارائه ویدیو")
        uploaded_video = st.file_uploader("ویدیو خود را انتخاب کنید",
                                         type=['mp4', 'avi', 'mov'],
                                         key="video_upload")
        
        if uploaded_video:
            st.video(uploaded_video)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("شروع ارائه ویدیو"):
                    # Save video for sharing
                    vid_path = Path(f"data/screen_share/{st.session_state.room_id}_video.mp4")
                    vid_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(vid_path, 'wb') as f:
                        f.write(uploaded_video.getbuffer())
                    st.success("ویدیو در حال ارائه است")
            
            with col2:
                if st.button("توقف ارائه ویدیو"):
                    st.info("ارائه متوقف شد")
    
    with tab3:
        st.write("### اشتراک‌گذاری لینک")
        link_url = st.text_input("آدرس URL را وارد کنید:")
        link_description = st.text_area("توضیحات:")
        
        if st.button("اشتراک‌گذاری لینک") and link_url:
            st.success(f"لینک به اشتراک گذاشته شد: {link_url}")
            st.markdown(f"[باز کردن لینک]({link_url})")

    # Camera snapshot sharing (teacher)
    st.divider()
    st.write("### اشتراک‌گذاری از وب‌کم")
    if "camera_snapshot_published" not in st.session_state:
        st.session_state.camera_snapshot_published = False

    # Capture image from teacher's webcam
    camera_image = st.camera_input("نمای وب‌کم (اگر در مرورگر پشتیبانی شود)")
    if camera_image is not None:
        st.image(camera_image, caption="پیش‌نمایش وب‌کم", use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("انتشار تصویر وب‌کم"):
                out_path = Path(f"data/screen_share/{st.session_state.room_id}_camera.png")
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with open(out_path, "wb") as f:
                    f.write(camera_image.getbuffer())
                st.session_state.camera_snapshot_published = True
                st.success("تصویر وب‌کم منتشر شد")

        with col2:
            if st.button("حذف تصویر منتشرشده"):
                out_path = Path(f"data/screen_share/{st.session_state.room_id}_camera.png")
                if out_path.exists():
                    out_path.unlink()
                st.session_state.camera_snapshot_published = False
                st.info("تصویر منتشرشده حذف شد")
    
    # Presentation controls
    st.divider()
    st.subheader("کنترل‌های ارائه")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⏸️ مکث"):
            st.info("ارائه متوقف شد")
    with col2:
        if st.button("▶️ ادامه"):
            st.info("ارائه ادامه یافت")
    with col3:
        if st.button("🔇 قطع صدا"):
            st.info("صدا قطع شد")
    with col4:
        if st.button("🔊 روشن صدا"):
            st.info("صدا روشن شد")

def show_student_screen_view():
    """Show student screen view"""
    st.subheader("مشاهده محتوای اشتراک‌گذاری شده")
    
    # Check if there's shared content
    img_path = Path(f"data/screen_share/{st.session_state.room_id}_image.png")
    vid_path = Path(f"data/screen_share/{st.session_state.room_id}_video.mp4")
    cam_path = Path(f"data/screen_share/{st.session_state.room_id}_camera.png")
    
    content_shown = False

    # Camera snapshot (prioritize teacher webcam snapshot)
    if cam_path.exists():
        st.image(str(cam_path), caption="نمای وب‌کم مدرس", use_container_width=True)
        content_shown = True

    # Then fall back to shared image or video
    if not content_shown and img_path.exists():
        st.image(str(img_path), caption="تصویر ارائه شده توسط مدرس", use_container_width=True)
        content_shown = True
    elif not content_shown and vid_path.exists():
        st.video(str(vid_path))
        content_shown = True

    if not content_shown:
        st.info("در حال حاضر محتوایی به اشتراک گذاشته نشده است")

    # Allow students to refresh view to pick up the latest published files
    if st.button("بارگذاری مجدد محتوا"):
        st.experimental_rerun()
    
    # View controls
    st.divider()
    st.subheader("کنترل‌های نمایش")
    col1, col2 = st.columns(2)
    
    with col1:
        zoom_level = st.slider("بزرگنمایی:", 50, 200, 100, 10)
        st.write(f"سطح بزرگنمایی: {zoom_level}%")
    
    with col2:
        quality = st.select_slider("کیفیت:", options=['پایین', 'متوسط', 'بالا'], value='متوسط')
        st.write(f"کیفیت تصویر: {quality}")
