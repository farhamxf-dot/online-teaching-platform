import streamlit as st

def inject_css():
    """Inject polished CSS for a more professional RTL dashboard look."""
    st.markdown(
        """
        <style>
        /* App layout */
        .stApp {
            direction: rtl;
            text-align: right;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(180deg, #f7f9fc 0%, #ffffff 100%);
        }

        /* Header */
        .app-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 20px;
            border-radius: 8px;
            background: white;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            margin-bottom: 18px;
        }
        .app-title { font-size: 20px; font-weight: 700; margin: 0; }
        .app-subtitle { color: #6b7280; font-size: 13px; margin: 0; }

        /* Sidebar styling */
        .css-1d391kg { padding-top: 1rem; } /* slight tweak for Streamlit sidebar */
        .sidebar-card {
            background: linear-gradient(180deg, #ffffff, #fbfdff);
            padding: 12px;
            border-radius: 8px;
            box-shadow: 0 1px 4px rgba(2,6,23,0.04);
            margin-bottom: 12px;
        }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #2563eb, #7c3aed);
            color: white;
            border: none;
            padding: 8px 14px;
            border-radius: 8px;
        }
        .stButton>button:disabled { opacity: 0.6 }

        /* Card / panel */
        .panel-card {
            background: white;
            padding: 14px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
            margin-bottom: 18px;
        }

        /* Small helpers */
        .muted { color: #6b7280; font-size: 13px }
        .large { font-size: 18px; font-weight: 600 }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str = ""):
    """Render a compact header with title and subtitle."""
    st.markdown(
        f"""
        <div class='app-header'>
            <div>
                <h1 class='app-title'>{title}</h1>
                <p class='app-subtitle'>{subtitle}</p>
            </div>
            <div style='display:flex; gap:8px; align-items:center;'>
                <img src='https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f393.png' width='36' style='filter: none;'/>
            </div>
        </div>
        
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(user_name: str, user_role: str, menu_options: list, logout_label: str = "خروج"):
    """Render a polished sidebar with user info and navigation control. Returns selected menu.

    menu_options: list of (key_label, display_label) or strings
    """
    # Sidebar top card
    with st.sidebar:
        st.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
        st.write(f"**{user_name or 'کاربر مهمان'}**")
        st.write(f"<div class='muted'>نقش: {user_role or '-'}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)

        # Build options for radio
        if menu_options and isinstance(menu_options[0], (list, tuple)):
            labels = [m[1] for m in menu_options]
            keys = [m[0] for m in menu_options]
        else:
            labels = menu_options
            keys = menu_options

        selected = st.radio("منو", labels, key="navigation")

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button(logout_label):
            return selected, True

    return selected, False


def safe_rerun():
    """Attempt to rerun the Streamlit app with a safe fallback.

    If Streamlit exposes experimental_rerun(), use it. Otherwise toggle a
    small session_state counter to force a rerun.
    """
    try:
        rerun = getattr(st, "experimental_rerun", None)
        if callable(rerun):
            rerun()
            return
    except Exception:
        pass

    key = "__ui_safe_rerun_counter"
    if key not in st.session_state:
        st.session_state[key] = 0
    st.session_state[key] += 1
