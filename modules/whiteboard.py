"""
ماژول تخته سفید
Whiteboard Module
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json
from pathlib import Path

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
    
    # Save whiteboard data
    if save_board:
        if canvas_result.json_data is not None:
            wb_path = Path(f"data/whiteboards/{st.session_state.room_id}.json")
            wb_path.parent.mkdir(parents=True, exist_ok=True)
            with open(wb_path, 'w') as f:
                json.dump(canvas_result.json_data, f)
            st.success("تخته سفید ذخیره شد!")
    
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
