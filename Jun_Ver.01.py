import streamlit as st
import streamlit.components.v1 as components
import random
from supabase import create_client, Client

# ==========================================
# 💾 Cloud DB (Supabase) Connection
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def load_ranking():
    try:
        response = supabase.table("ranking").select("*").execute()
        return response.data
    except Exception:
        return []

def insert_ranking(nickname, attempts, difficulty):
    try:
        supabase.table("ranking").insert({
            "nickname": nickname, 
            "attempts": attempts, 
            "difficulty": difficulty
        }).execute()
    except Exception:
        pass

def load_chat():
    try:
        response = supabase.table("chat").select("*").order("created_at", desc=False).execute()
        return response.data
    except Exception:
        return []

def insert_chat(name, msg):
    try:
        supabase.table("chat").insert({
            "name": name, 
            "msg": msg
        }).execute()
    except Exception:
        pass

def get_top_3_by_difficulty(ranking_list, diff_name):
    # Compatibility mapping for existing Korean DB records
    mapping = {
        "EASY": ["EASY", "쉬움"],
        "NORMAL": ["NORMAL", "보통"],
        "HELL": ["HELL", "지옥"]
    }
    allowed_diffs = mapping.get(diff_name, [diff_name])
    filtered = [r for r in ranking_list if r.get("difficulty") in allowed_diffs]
    sorted_ranking = sorted(filtered, key=lambda x: x["attempts"])
    return sorted_ranking[:3]


# --- 🎮 Web Page Configuration ---
st.set_page_config(page_title="Up & Down Arcade", page_icon="🕹️", layout="centered")

# ==========================================
# 🎨 UI Style Sheet & Production Patch
# ==========================================
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/neodgm/neodgm-webfont@1.530/neodgm/style.css');
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        [data-testid="stAppViewContainer"] { background-color: #18181b !important; }
        [data-testid="stHeader"] { background-color: transparent !important; }

        p, label, li, div[data-testid="stMarkdownContainer"] > p {
            font-family: 'Pretendard', sans-serif !important;
            color: #d4d4d8 !important; 
            font-size: 1.05rem !important;
            font-weight: 400 !important;
        }

        h1, h1 * {
            font-family: 'NeoDunggeunmo', sans-serif !important;
            font-size: 2.5rem !important; 
            color: #f472b6 !important; 
            text-shadow: 0 0 8px rgba(244, 114, 182, 0.5) !important;
            text-align: center !important;
        }
        
        h2, h2 * {
            font-family: 'NeoDunggeunmo', sans-serif !important;
            font-size: 1.8rem !important;
            color: #fdfa72 !important;
            text-shadow: 0 0 5px rgba(253, 250, 114, 0.4) !important;
            text-align: center !important;
        }
        
        h3, h3 * {
            font-family: 'NeoDunggeunmo', sans-serif !important;
            font-size: 1.4rem !important;
            color: #34d399 !important;
        }

        div[data-testid="stRadio"] > div {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 15px !important;
        }
        
        div[data-testid="stRadio"] label {
            white-space: nowrap !important;
            font-size: 0.95rem !important;
        }

        .stButton>button {
            font-family: 'NeoDunggeunmo', sans-serif !important;
            font-size: 1.2rem !important;
            background-color: #27272a !important;
            color: #34d399 !important;
            border: 2px solid #34d399 !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
            transition: all 0.2s ease-in-out;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #34d399 !important;
            color: #18181b !important;
            box-shadow: 0 0 12px rgba(52, 211, 153, 0.6) !important;
            transform: scale(1.02);
        }

        .stTextInput input, .stNumberInput input {
            background-color: #27272a !important;
            color: #34d399 !important;
            border: 1px solid #52525b !important;
            border-radius: 6px !important;
            font-family: 'Pretendard', sans-serif !important;
            font-size: 1.1rem !important;
        }
        input::placeholder { color: #71717a !important; }

        [data-testid="stAlert"] {
            background-color: #1e1b4b !important; 
            border: 1px solid #6366f1 !important; 
            border-radius: 10px !important;
        }
        [data-testid="stAlert"] * {
            color: #e0e7ff !important; 
            font-family: 'Pretendard', sans-serif !important;
            font-size: 1.05rem !important;
            font-weight: 500 !important;
        }

        [data-testid="stForm"] {
            background-color: #1f1f22 !important;
            border: 1px solid #3f3f46 !important;
            border-radius: 12px !important;
            padding: 20px !important;
        }

        hr { border-bottom: 2px dashed #52525b !important; }

        .arcade-clear-banner {
            border: 4px double #34d399 !important; 
            background-color: #111111 !important;
            padding: 25px !important;
            border-radius: 12px !important;
            text-align: center !important;
            margin: 20px 0 30px 0 !important;
            box-shadow: 0 0 20px rgba(52, 211, 153, 0.25) !important;
        }
        .arcade-clear-text {
            font-family: 'NeoDunggeunmo', sans-serif !important;
            font-size: 3.8rem !important; 
            color: #34d399 !important;
            letter-spacing: 10px !important;
            margin: 0 !important;
            text-shadow: 0 0 12px rgba(52, 211, 153, 0.6) !important;
            animation: retro-flash 0.6s infinite alternate steps(2); 
        }
        @keyframes retro-flash {
            0% { opacity: 1; text-shadow: 0 0 15px #34d399; }
            100% { opacity: 0.5; text-shadow: 0 0 2px #34d399; }
        }

        /* Production Patch */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Donation Buttons */
        .donate-btn {
            display: inline-block;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            font-family: 'NeoDunggeunmo', sans-serif;
            font-size: 1.1rem;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border: 2px solid #18181b;
        }
        .donate-btn:hover {
            transform: scale(1.05);
        }

    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🕹️ UP & DOWN ARCADE 🕹️</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#34d399; font-weight:600;'>INSERT COIN TO PLAY... Created by J.S.Kim</p>", unsafe_allow_html=True)

# --- 🎵 BGM Player ---
bgm_html = """
<div style="display: flex; justify-content: center; align-items: center; flex-direction: column; margin-bottom: 25px;">
    <span style="color: #fdfa72; font-family: 'NeoDunggeunmo', sans-serif; font-size: 0.95rem; margin-bottom: 8px;">🎵 BGM ON/OFF</span>
    <audio autoplay loop controls style="height: 35px; width: 260px; border-radius: 8px; outline: none;">
        <source src="https://codeskulptor-demos.commondatastorage.googleapis.com/pang/paza-moduless.mp3" type="audio/mpeg">
        Your browser does not support the audio element.
    </audio>
</div>
"""
st.markdown(bgm_html, unsafe_allow_html=True)

# --- 🧠 Session State ---
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.game_over = False
    st.session_state.is_clear = False

# ==========================================
# Game Logic & UI
# ==========================================
if not st.session_state.game_started:
    st.subheader("▶ PLAYER LOG-IN")
    nickname = st.text_input("NICKNAME:", placeholder="Enter your hacker name...")
    selected_diff = st.radio("▶ SELECT STAGE LEVEL", ["🟢 EASY (1~50) - HP 10", "🔵 NORMAL (1~100) - HP 7", "🔴 HELL (1~1000) - HP 5"], horizontal=True)
    
    if st.button("PRESS START BUTTON"):
        if nickname.strip() == "": st.warning("⚠️ LOGIN ERROR!")
        else:
            diff_settings = {"🟢 EASY": ("EASY", 50, 10), "🔵 NORMAL": ("NORMAL", 100, 7), "🔴 HELL": ("HELL", 1000, 5)}
            d = next((v for k, v in diff_settings.items() if k in selected_diff), ("NORMAL", 100, 7))
            st.session_state.difficulty, st.session_state.max_value, st.session_state.hp = d
            st.session_state.nickname, st.session_state.secret_number = nickname, random.randint(1, d[1])
            st.session_state.attempts, st.session_state.history = 0, []
            st.session_state.current_min, st.session_state.current_max = 1, d[1]
            st.session_state.game_started, st.session_state.game_over, st.session_state.is_clear = True, False, False
            st.rerun()

    # Ranking Table
    st.divider()
    st.subheader("🏆 HALL OF FAME 🏆")
    tabs = st.tabs(["🟢 EASY", "🔵 NORMAL", "🔴 HELL"])
    all_rankings = load_ranking()
    for i, diff in enumerate(["EASY", "NORMAL", "HELL"]):
        with tabs[i]:
            for r in get_top_3_by_difficulty(all_rankings, diff):
                st.write(f"**[RANK]** {r['nickname']} ({r['attempts']} TRIES)")

elif st.session_state.game_started and not st.session_state.game_over:
    # 📌 추가된 부분: HP 표시
    st.markdown(f"""
    <div style="text-align: center; font-family: 'NeoDunggeunmo', sans-serif; color: #f472b6; font-size: 1.8rem; margin-bottom: 10px;">
        💖 HP: {st.session_state.hp}
    </div>
    """, unsafe_allow_html=True)

    # 📌 MIN/MAX 표시
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; font-family: 'NeoDunggeunmo', sans-serif; color: #34d399; font-size: 1.2rem; margin-bottom: 10px;">
        <span>MIN: {st.session_state.current_min}</span>
        <span>MAX: {st.session_state.current_max}</span>
    </div>
    """, unsafe_allow_html=True)
    
    left_pct = ((st.session_state.current_min - 1) / st.session_state.max_value) * 100
    width_pct = ((st.session_state.current_max - st.session_state.current_min + 1) / st.session_state.max_value) * 100
    st.markdown(f"""
    <div style="width: 100%; height: 35px; background-color: #27272a; border: 2px solid #52525b; border-radius: 6px; position: relative;">
        <div style="position: absolute; left: {left_pct}%; width: {width_pct}%; height: 100%; background-color: #34d399; box-shadow: 0 0 15px #34d399;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    guess = st.number_input("TARGET:", min_value=1, max_value=st.session_state.max_value, value=int(st.session_state.max_value/2))
    if st.button("ATTACK"):
        if guess in st.session_state.history: st.warning("⚠️ Already guessed this!")
        else:
            st.session_state.attempts += 1
            st.session_state.history.append(guess)
            if guess == st.session_state.secret_number:
                st.session_state.game_over, st.session_state.is_clear = True, True
                insert_ranking(st.session_state.nickname, st.session_state.attempts, st.session_state.difficulty)
            elif st.session_state.attempts >= 10 and st.session_state.difficulty == "HELL": st.session_state.game_over = True
            elif guess < st.session_state.secret_number: st.session_state.current_min = max(st.session_state.current_min, guess + 1)
            else: st.session_state.current_max = min(st.session_state.current_max, guess - 1)
            
            st.session_state.hp -= 1
            if st.session_state.hp <= 0: st.session_state.game_over = True
            st.rerun()

elif st.session_state.game_over:
    if st.session_state.is_clear: st.markdown('<div class="arcade-clear-banner"><p class="arcade-clear-text">STAGE CLEAR</p></div>', unsafe_allow_html=True)
    st.code(f"I cleared Up & Down Arcade [{st.session_state.difficulty}] in {st.session_state.attempts} TRIES!\nhttps://junseok-ver01.streamlit.app/", language="markdown")
    if st.button("CONTINUE?"): st.session_state.game_started = False; st.rerun()

# Guest Book
st.divider()
st.subheader("💬 GUEST BOOK")
with st.form("chat_form", clear_on_submit=True):
    name = st.text_input("ID:")
    msg = st.text_input("MESSAGE:")
    if st.form_submit_button("ENTER"): insert_chat(name, msg); st.rerun()
for chat in reversed(load_chat()[-5:]): st.write(f"**[{chat['name']}]** > {chat['msg']}")

# Final Donation Section
st.divider()
st.markdown("""
<div style="text-align: center; margin-top: 40px; margin-bottom: 20px;">
    <p style="color: #a1a1aa; font-family: 'Pretendard', sans-serif; font-size: 0.9rem;">Did you enjoy the game? Support the arcade!</p>
    <div style="display: flex; justify-content: center; gap: 15px; margin-top: 10px;">
        <a href="https://ko-fi.com/junseokkim" target="_blank" class="donate-btn" style="background-color: #f472b6; color: #ffffff;">☕ KO-FI</a>
    </div>
</div>
""", unsafe_allow_html=True)
