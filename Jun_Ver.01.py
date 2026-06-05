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

        /* Production Patch: Hide Streamlit Default UI Elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🕹️ UP & DOWN ARCADE 🕹️</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#34d399; font-weight:600;'>INSERT COIN TO PLAY... Created by J.S.Kim</p>", unsafe_allow_html=True)

# --- 🎵 BGM Player ---
# 💡 [신규] 아케이드 BGM 플레이어 추가 (자동재생 및 반복)
bgm_html = """
<div style="display: flex; justify-content: center; align-items: center; flex-direction: column; margin-bottom: 25px;">
    <span style="color: #fdfa72; font-family: 'NeoDunggeunmo', sans-serif; font-size: 0.95rem; margin-bottom: 8px;">🎵 BGM ON/OFF</span>
    <audio autoplay loop controls style="height: 35px; width: 260px; border-radius: 8px; outline: none;">
        <source src="https://assets.mixkit.co/music/preview/mixkit-arcade-retro-background-219.mp3" type="audio/mpeg">
        Your browser does not support the audio element.
    </audio>
</div>
"""
st.markdown(bgm_html, unsafe_allow_html=True)


# --- 🧠 Session State Initialization ---
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.game_over = False
    st.session_state.is_clear = False

# ==========================================
# Phase 1: Game Start / Menu Screen
# ==========================================
if not st.session_state.game_started:
    st.subheader("▶ PLAYER LOG-IN")
    nickname = st.text_input("NICKNAME:", placeholder="Enter your hacker name...")
    
    selected_diff = st.radio(
        "▶ SELECT STAGE LEVEL",
        ["🟢 EASY (1~50) - HP 10", "🔵 NORMAL (1~100) - HP 7", "🔴 HELL (1~1000) - HP 5"],
        horizontal=True
    )
    
    if st.button("PRESS START BUTTON"):
        if nickname.strip() == "":
            st.warning("⚠️ LOGIN ERROR! Please enter your nickname to insert a coin.")
        else:
            if "EASY" in selected_diff:
                st.session_state.difficulty = "EASY"
                st.session_state.max_value = 50
                st.session_state.hp = 10
            elif "HELL" in selected_diff:
                st.session_state.difficulty = "HELL"
                st.session_state.max_value = 1000
                st.session_state.hp = 5
            else:
                st.session_state.difficulty = "NORMAL"
                st.session_state.max_value = 100
                st.session_state.hp = 7
                
            st.session_state.nickname = nickname
            st.session_state.secret_number = random.randint(1, st.session_state.max_value)
            st.session_state.attempts = 0
            st.session_state.history = [] 
            
            st.session_state.current_min = 1
            st.session_state.current_max = st.session_state.max_value
            
            st.session_state.game_started = True
            st.session_state.game_over = False
            st.session_state.is_clear = False
            st.session_state.message = f"SYSTEM: [{nickname}] Initialized! HP Status: {'❤️' * st.session_state.hp}"
            st.rerun()
            
    st.divider()
    st.subheader("🏆 HALL OF FAME 🏆")
    
    tab1, tab2, tab3 = st.tabs(["🟢 EASY", "🔵 NORMAL", "🔴 HELL"])
    all_rankings = load_ranking()
    
    with tab1:
        easy_top3 = get_top_3_by_difficulty(all_rankings, "EASY")
        if easy_top3:
            for i, record in enumerate(easy_top3):
                st.write(f"**[RANK {i+1}]** {record['nickname']} (Score: {record['attempts']} TRIES)")
        else:
            st.caption("NO DATA AVAILABLE.")
            
    with tab2:
        normal_top3 = get_top_3_by_difficulty(all_rankings, "NORMAL")
        if normal_top3:
            for i, record in enumerate(normal_top3):
                st.write(f"**[RANK {i+1}]** {record['nickname']} (Score: {record['attempts']} TRIES)")
        else:
            st.caption("NO DATA AVAILABLE.")
            
    with tab3:
        hard_top3 = get_top_3_by_difficulty(all_rankings, "HELL")
        if hard_top3:
            for i, record in enumerate(hard_top3):
                st.write(f"**[RANK {i+1}]** {record['nickname']} (Score: {record['attempts']} TRIES)")
        else:
            st.caption("NO DATA AVAILABLE.")

# ==========================================
# Phase 2: In-Game Screen
# ==========================================
if st.session_state.game_started and not st.session_state.game_over:
    st.success(st.session_state.message)
    
    # Radar Bar Rendering
    left_pct = ((st.session_state.current_min - 1) / st.session_state.max_value) * 100
    width_pct = ((st.session_state.current_max - st.session_state.current_min + 1) / st.session_state.max_value) * 100
    
    radar_html = f"""
    <div style="margin: 20px 0 30px 0;">
        <p style="text-align: center; font-family: 'NeoDunggeunmo'; color: #fdfa72; font-size: 1.2rem; margin-bottom: 8px;">▶ TARGET RADAR ◀</p>
        <div style="width: 100%; height: 35px; background-color: #27272a; border: 2px solid #52525b; border-radius: 6px; position: relative; overflow: hidden;">
            <div style="
                position: absolute;
                left: {left_pct}%;
                width: {width_pct}%;
                height: 100%;
                background-color: #34d399;
                box-shadow: 0 0 15px rgba(52, 211, 153, 0.8);
                transition: all 0.6s cubic-bezier(0.25, 1, 0.5, 1);
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 10px;
                box-sizing: border-box;
            ">
                <span style="color: #18181b; font-weight: bold; font-family: 'NeoDunggeunmo'; font-size: 1.1rem;">{st.session_state.current_min}</span>
                <span style="color: #18181b; font-weight: bold; font-family: 'NeoDunggeunmo'; font-size: 1.1rem;">{st.session_state.current_max}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(radar_html, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        input_mode = st.radio(
            "▶ CONTROLLER TYPE",
            ["⌨️ KEYBOARD", "📱 JOYSTICK(SLIDER)"],
            horizontal=True
        )
        st.write("") 
        
        if input_mode == "⌨️ KEYBOARD":
            guess = st.number_input(f"TARGET (1~{st.session_state.max_value}):", min_value=1, max_value=st.session_state.max_value, value=int(st.session_state.max_value/2), step=1)
        else:
            guess = st.slider(f"TARGET (1~{st.session_state.max_value}):", min_value=1, max_value=st.session_state.max_value, value=int(st.session_state.max_value/2))
        st.write("") 
        
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("ATTACK"):
                st.session_state.attempts += 1
                st.session_state.history.append(guess)
                
                if guess < st.session_state.secret_number:
                    st.session_state.current_min = max(st.session_state.current_min, guess + 1)
                    st.session_state.hp -= 1
                    if st.session_state.hp <= 0:
                        st.session_state.message = f"💀 GAME OVER 💀 HP reduced to 0... The core target was [{st.session_state.secret_number}]!"
                        st.session_state.game_over = True
                        st.session_state.is_clear = False
                    else:
                        st.session_state.message = f"🔺 UP!! Aim higher than [{guess}]. (Remaining HP: {'❤️' * st.session_state.hp})"
                    st.rerun()
                    
                elif guess > st.session_state.secret_number:
                    st.session_state.current_max = min(st.session_state.current_max, guess - 1)
                    st.session_state.hp -= 1
                    if st.session_state.hp <= 0:
                        st.session_state.message = f"💀 GAME OVER 💀 HP reduced to 0... The core target was [{st.session_state.secret_number}]!"
                        st.session_state.game_over = True
                        st.session_state.is_clear = False
                    else:
                        st.session_state.message = f"🔻 DOWN!! Aim lower than [{guess}]. (Remaining HP: {'❤️' * st.session_state.hp})"
                    st.rerun()
                    
                else:
                    st.session_state.message = f"🎉 MISSION CLEAR! Target: {st.session_state.secret_number} / Score: {st.session_state.attempts} Tries"
                    st.session_state.game_over = True
                    st.session_state.is_clear = True 
                    insert_ranking(st.session_state.nickname, st.session_state.attempts, st.session_state.difficulty)
                    st.rerun()
                    
        with btn_col2:
            if st.button("RESTART"):
                st.session_state.secret_number = random.randint(1, st.session_state.max_value)
                st.session_state.attempts = 0
                st.session_state.history = []
                st.session_state.current_min = 1
                st.session_state.current_max = st.session_state.max_value
                
                if st.session_state.difficulty == "EASY":
                    st.session_state.hp = 10
                elif st.session_state.difficulty == "HELL":
                    st.session_state.hp = 5
                else:
                    st.session_state.hp = 7
                    
                st.session_state.message = f"SYSTEM: Stage Reset. (Remaining HP: {'❤️' * st.session_state.hp})"
                st.rerun()
                
    with col2:
        st.subheader("📝 COMBAT LOG")
        if st.session_state.history:
            for idx, num in enumerate(st.session_state.history):
                st.write(f"[Turn {idx+1}] Guess: **{num}**")
        else:
            st.caption("Standby...")
            
        if st.session_state.nickname == "KimJunSeok":
            st.markdown(f"<div style='text-align: right; color: #f472b6; font-size: 0.85rem; margin-top: 30px;'>[DEBUG] Target: {st.session_state.secret_number}</div>", unsafe_allow_html=True)

# ==========================================
# Phase 3: Game Over / Scoreboard Screen
# ==========================================
if st.session_state.game_over:
    if st.session_state.is_clear:
        st.markdown("""
            <div class="arcade-clear-banner">
                <p class="arcade-clear-text">STAGE CLEAR</p>
            </div>
        """, unsafe_allow_html=True)
        
    st.warning(st.session_state.message)
    st.info(f"▶ LOG DATA: {', '.join(map(str, st.session_state.history))}")
    
    st.divider()
    st.subheader(f"🏆 {st.session_state.difficulty} RANKING 🏆")
    
    all_rankings = load_ranking()
    current_top3 = get_top_3_by_difficulty(all_rankings, st.session_state.difficulty)
    
    for i, record in enumerate(current_top3):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
        st.write(f"**{medal} RANK {i+1}:** {record['nickname']} ({record['attempts']} TRIES)")

    st.divider()
    
    if st.button("CONTINUE? (Insert Coin)"):
        st.session_state.game_started = False
        st.rerun()


# ==========================================
# Phase 4: Guest Book Section
# ==========================================
st.divider()
st.subheader("💬 GUEST BOOK")

with st.form("chat_form", clear_on_submit=True):
    if st.session_state.game_started:
        author_name = st.session_state.nickname
        st.text(f"ID: {author_name} (PLAYING)")
    else:
        author_name = st.text_input("ID:", max_chars=10, placeholder="Your Nickname")

    chat_message = st.text_input("MESSAGE:", max_chars=100, placeholder="Type your arcade transmission message...")
    submit_btn = st.form_submit_button("ENTER")

    if submit_btn:
        if not author_name.strip():
            st.error("ERROR: ID cannot be empty.")
        elif not chat_message.strip():
            st.error("ERROR: Message cannot be empty.")
        else:
            insert_chat(author_name, chat_message)
            st.rerun()

saved_chats = load_chat()
if saved_chats:
    for chat in reversed(saved_chats[-10:]):
        st.write(f"**[{chat['name']}]** > {chat['msg']}")
else:
    st.caption("No transmissions available.")
