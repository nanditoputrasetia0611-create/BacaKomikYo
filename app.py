import streamlit as st
import os
import json
import pandas as pd

from db import record_read, get_top_comics   # 🔥 STATISTIK

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="BacaKomikYo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================== SESSION STATE ==================
if "mode" not in st.session_state:
    st.session_state.mode = "idle"  # idle | catalog | search | reader

if "selected_category" not in st.session_state:
    st.session_state.selected_category = None

if "selected_title" not in st.session_state:
    st.session_state.selected_title = None

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# ================== LOAD CSS ==================
if os.path.exists("style.css"):
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ================== FUNCTIONS ==================
def load_comics(base_path="Comics"):
    data = {}
    if not os.path.exists(base_path):
        return data

    for category in os.listdir(base_path):
        category_path = os.path.join(base_path, category)
        if os.path.isdir(category_path):
            data[category] = [
                title for title in os.listdir(category_path)
                if os.path.isdir(os.path.join(category_path, title))
            ]
    return data


def load_comic_info(folder):
    info_path = os.path.join(folder, "info.json")
    if os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_pages(folder):
    return sorted([
        f for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ])

# ================== DATA ==================
comics_data = load_comics()

# ================== SIDEBAR ==================
with st.sidebar:
    st.header("📚 Navigation")

    if not comics_data:
        st.error("No comics found")
        st.stop()

    if st.button("📚 Open Catalog", use_container_width=True):
        st.session_state.mode = "catalog"
        st.rerun()

    if st.session_state.mode == "catalog":
        st.markdown("---")
        category = st.selectbox(
            "Category",
            list(comics_data.keys()),
            key="category_select"
        )
    else:
        category = None

# ================== HEADER ==================
st.markdown("<div class='comic-title'>📖 BacaKomikYo</div>", unsafe_allow_html=True)

# ================== SEARCH BAR ==================
col1, col2 = st.columns([4, 1])

with col1:
    search_query = st.text_input(
        "Search comic",
        placeholder="Type comic title...",
        label_visibility="collapsed"
    )

with col2:
    search_btn = st.button("Search", use_container_width=True)

# ================== SEARCH LOGIC ==================
if search_btn and search_query:
    results = []
    for cat, titles in comics_data.items():
        for t in titles:
            if search_query.lower() in t.lower():
                results.append((cat, t))

    st.session_state.search_query = search_query
    st.session_state.search_results = results
    st.session_state.mode = "search"
    st.rerun()

# =================================================
# ================== MODE: IDLE ===================
# =================================================
if st.session_state.mode == "idle":
    st.markdown(
        """
        <div style="text-align:center; margin-top:120px;">
            <h1>📖 BacaKomikYo</h1>
            <p style="color:#666;">Search or open catalog to start reading</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 🔥 STATISTIK PALING DIBACA
st.subheader("🔥 Most Read Comics")

top = get_top_comics(limit=10)

if top:
    # ================= TABLE DATA =================
    df = pd.DataFrame(top)
    df = df.rename(columns={
        "title": "Comic",
        "views": "Views"
    }).set_index("Comic")

    # ================= BAR CHART =================
    st.bar_chart(df)

    # ================= DETAIL LIST =================
    st.markdown("### 📘 Detail Views")
    for _, row in df.iterrows():
        st.write(f"📘 {row.name} — {row.Views} views")

else:
    st.info("No reading data yet")

# =================================================
# ================== MODE: CATALOG =================
# =================================================
if st.session_state.mode == "catalog":

    if not category:
        st.info("Select category from sidebar")
        st.stop()

    st.subheader("📚 Comic Collection")

    cols = st.columns(6)
    i = 0

    for title in comics_data[category]:
        comic_folder = os.path.join("Comics", category, title)
        pages = get_pages(comic_folder)
        if not pages:
            continue

        cover_path = os.path.join(comic_folder, pages[0])
        info = load_comic_info(comic_folder)

        with cols[i % 6]:
            st.image(cover_path, width=150)
            st.markdown(
                f"""
                <div class="comic-title-small">{info.get('title', title)}</div>
                <div style="font-size:0.75rem;color:#666;text-align:center;">
                    {info.get('year','')}<br>{info.get('genre','')}
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Read", key=f"cat_{category}_{title}"):
                st.session_state.mode = "reader"
                st.session_state.selected_category = category
                st.session_state.selected_title = title
                st.rerun()

        i += 1

# =================================================
# ================== MODE: SEARCH ==================
# =================================================
if st.session_state.mode == "search":

    st.subheader(f"🔍 Search results for '{st.session_state.search_query}'")

    if not st.session_state.search_results:
        st.warning("Comic not found 😢")
        st.stop()

    cols = st.columns(6)
    i = 0

    for cat, title in st.session_state.search_results:
        comic_folder = os.path.join("Comics", cat, title)
        pages = get_pages(comic_folder)
        if not pages:
            continue

        cover_path = os.path.join(comic_folder, pages[0])
        info = load_comic_info(comic_folder)

        with cols[i % 6]:
            st.image(cover_path, width=150)
            st.markdown(
                f"""
                <div class="comic-title-small">{info.get('title', title)}</div>
                <div style="font-size:0.75rem;color:#666;text-align:center;">
                    {info.get('year','')}<br>{info.get('genre','')}
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Read", key=f"search_{cat}_{title}"):
                st.session_state.mode = "reader"
                st.session_state.selected_category = cat
                st.session_state.selected_title = title
                st.rerun()

        i += 1

# =================================================
# ================== MODE: READER ==================
# =================================================
if st.session_state.mode == "reader":

    category = st.session_state.selected_category
    title = st.session_state.selected_title

    # 🔥 CATAT STATISTIK
    record_read(category, title)

    comic_path = os.path.join("Comics", category, title)
    pages = get_pages(comic_path)
    info = load_comic_info(comic_path)

    if st.button("⬅ Back to catalog"):
        st.session_state.mode = "catalog"
        st.rerun()

    st.markdown(f"## {info.get('title', title)}")
    st.markdown(
        f"""
        **Publisher:** {info.get('publisher','-')}  
        **Year:** {info.get('year','-')}  
        **Genre:** {info.get('genre','-')}  

        {info.get('description','')}
        """
    )

    for page in pages:
        st.image(os.path.join(comic_path, page), use_container_width=True)
