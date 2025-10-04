"""
ماژول تخته سفید
Whiteboard Module
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json
from pathlib import Path
import numpy as np
from PIL import Image

def show():
    """Show whiteboard interface"""
    st.title("🖍️ تخته سفید")
    
    if not st.session_state.room_id:
        st.warning("ابتدا باید وارد یک کلاس شوید")
        return
    
    st.info(f"کلاس فعال: {st.session_state.room_id}")
    
    # Drawing tools
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        drawing_mode = st.selectbox(
            "ابزار رسم:",
            ("freedraw", "line", "rect", "circle", "transform")
        )
    
    with col2:
        stroke_width = st.slider("ضخامت خط:", 1, 25, 3)
    
    with col3:
        stroke_color = st.color_picker("رنگ:", "#000000")
    
    with col4:
        bg_color = st.color_picker("رنگ پس‌زمینه:", "#FFFFFF")
    
    # Clear and save buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        clear_board = st.button("پاک کردن تخته")
    with col2:
        save_board = st.button("ذخیره تخته")
    with col3:
        load_board = st.button("بارگذاری تخته")
    
    # Canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=500,
        drawing_mode=drawing_mode,
        key="canvas",
    )

    # Shared whiteboard image path (auto-saved snapshot of canvas)
    wb_image_path = Path(f"data/whiteboards/{st.session_state.room_id}_canvas.png")

    # If user is not a teacher, show the latest published whiteboard snapshot (read-only)
    # This allows students to view what the teacher is drawing (simple polling / refresh).
    if st.session_state.get('user_role') != "مدرس":
        if wb_image_path.exists():
            st.image(str(wb_image_path), caption="تخته سفید (ارائه شده توسط مدرس)", use_container_width=True)
            if st.button("بارگذاری مجدد تخته"):
                st.experimental_rerun()
        else:
            st.info("تخته‌ای توسط مدرس منتشر نشده است")
        # Students shouldn't get the drawing controls below; return early
        return
    
    # Save whiteboard data (explicit save to JSON)
    if save_board:
        if canvas_result.json_data is not None:
            wb_path = Path(f"data/whiteboards/{st.session_state.room_id}.json")
            wb_path.parent.mkdir(parents=True, exist_ok=True)
            with open(wb_path, 'w', encoding='utf-8') as f:
                json.dump(canvas_result.json_data, f)
            st.success("تخته سفید ذخیره شد!")

    # Auto-save an image snapshot of the canvas so students can quickly view the latest drawing.
    # st_canvas returns image_data as an ndarray (RGBA). Convert and save as PNG.
    try:
        if canvas_result is not None and getattr(canvas_result, 'image_data', None) is not None:
            arr = canvas_result.image_data
            # Convert float images to uint8 if needed
            if arr.dtype != np.uint8:
                arr = (arr * 255).astype('uint8')
            img = Image.fromarray(arr)
            wb_image_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(wb_image_path)
            # Indicate published state
            st.session_state['whiteboard_published'] = True
    except Exception:
        # Non-fatal; don't block the UI if saving snapshot fails
        pass
    
    # Text tools
    st.divider()
    st.subheader("ابزار متن")
    text_input = st.text_area("متن خود را وارد کنید:")
    text_size = st.slider("اندازه متن:", 10, 72, 24)
    
    if text_input:
        st.markdown(f"<p style='font-size:{text_size}px; text-align:right;'>{text_input}</p>", 
                   unsafe_allow_html=True)
    
    # Shape tools
    st.divider()
    st.subheader("اشکال آماده")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➡️ فلش"):
            st.info("فلش را روی تخته رسم کنید")
    with col2:
        if st.button("⭐ ستاره"):
            st.info("ستاره را روی تخته رسم کنید")
    with col3:
        if st.button("❤️ قلب"):
            st.info("قلب را روی تخته رسم کنید")
    with col4:
        if st.button("📝 یادداشت"):
            st.info("یادداشت را روی تخته رسم کنید")
