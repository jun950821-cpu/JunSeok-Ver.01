import streamlit as st
import random
import json
import os

# --- 💾 랭킹 및 방명록 데이터 저장/불러오기 ---
RANKING_FILE = "ranking.json"
CHAT_FILE = "chat.json"

def load_ranking():
    if os.path.exists(RANKING_FILE):
        try:
            with open(RANKING_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [r for r in data if isinstance(r, dict) and "nickname" in r and "attempts" in r]
        except Exception:
            return []
    return []

def save_ranking(ranking_list):
    try:
        with open(RANKING_FILE, "w", encoding="utf-8") as f:
            json.dump(ranking_list, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def load_chat():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [c for c in data if isinstance(c, dict) and "name" in c and "msg" in c]
        except Exception:
            return []
    return []

def save_chat(chat_list):
    try:
        with open(CHAT_FILE, "w", encoding="utf-8") as f:
            json.dump(chat_list, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def get_top_3_by_difficulty(ranking_list, diff_name):
    filtered = [r for r in ranking_list if r.get("difficulty", "보통") == diff_name]
    sorted_ranking = sorted(filtered, key=lambda x: x["attempts"])
    return sorted_ranking[:3]


# --- 🎮 웹페이지 기본 설정 ---
st.set_page_config(page_title="Up & Down Arcade", page_icon="🕹️", layout="centered")

# ==========================================
# 🎨 [세련된 모던 레트로] 가독성 최적화 CSS 
# ==========================================
st.markdown("""
    <style>
        /* 1. 레트로 픽셀 폰트 & 모던 고딕 폰트 동시에 불러오기 */
        @import url('https://cdn.jsdelivr.net/gh/neodgm/neodgm-webfont@1.530/neodgm/style.css');
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        /* 2. 눈이 편안한 소프트 다크 그레이 배경 */
        [data-testid="stAppViewContainer"] {
            background-color: #18181b !important;
        }
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }

        /* 3. 일반 글씨는 가독성 최고의 '프리텐다드' + 부드러운 라이트 그레이 색상 */
        html, body, p, span, div, label, li {
            font-family: 'Pretendard', sans-serif !important;
            color: #d4d4d8 !important; 
            font-size: 1.05rem !important;
            font-weight: 400 !important;
        }

        /* 4. 제목과 특정 강조 부분만 '픽셀 폰트'로 감성 유지 */
        h1, h2, h3, .stButton>button, strong {
            font-family: 'NeoDunggeunmo', sans-serif !important;
        }

        /* 5. 은은한 파스텔 네온 타이틀 (눈부심 방지) */
        h1, h2, h3 {
            color: #fdfa72 !important; /* 소프트 옐로우 */
            text-shadow: 0 0 5px rgba(253, 250, 114, 0.4) !important;
            text-align: center !important;
        }
        h1 {
            color: #f472b6 !important; /* 소프트 핑크 */
            text-shadow: 0 0 8px rgba(244, 114, 182, 0.5) !important;
        }

        /* 6. 모던 레트로 스타일 버튼 */
        .stButton>button {
            background-color: #27272a !important;
            color: #34d399 !important; /* 소프트 형광 그린 */
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

        /* 7. 입력창 디자인 (카드형 가독성) */
        .stTextInput input, .stNumberInput input {
            background-color: #27272a !important;
            color: #34d399 !important;
            border: 1px solid #52525b !important;
            border-radius: 6px !important;
            font-family: 'Pretendard', sans-serif !important;
        }
        input::placeholder {
            color: #71717a !important; 
        }

        /* 8. 결과 알림창 (가독성 높은 딥 인디고 카드 디자인) */
        [data-testid="stAlert"] {
            background-color: #1e1b4b !important; 
            border: 1px solid #6366f1 !important; 
            border-radius: 10px !important;
        }
        [data-testid="stAlert"] * {
            color: #e0e7ff !important; 
            font-family: 'Pretendard', sans-serif !important;
            font-weight: 500 !important;
        }

        /* 9. 방명록 등 폼 영역 (카드 UI) */
        [data-testid="stForm"] {
            background-color: #1f1f22 !important;
            border: 1px solid #3f3f46 !important;
            border-radius: 12px !important;
            padding: 20px !important;
        }

        /* 10. 구분선 */
        hr {
            border-bottom: 2px dashed #52525b !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🕹️ UP & DOWN ARCADE 🕹️</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#34d399; font-weight:600;'>INSERT COIN TO PLAY... Created by J.S.Kim</p>", unsafe_allow_html=True)


# --- 🧠 기억 상자(세션) 초기화 ---
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.game_over = False
    st.session_state.is_clear = False

# ==========================================
# 1단계: 게임 시작 전
# ==========================================
if not st.session_state.game_started:
    st.subheader("▶ PLAYER LOG-IN")
    nickname = st.text_input("NICKNAME:", placeholder="이름을 입력하라...")
    
    selected_diff = st.radio(
        "▶ SELECT STAGE LEVEL",
        ["🟢 EASY (1~50) - HP 10", "🔵 NORMAL (1~100) - HP 7", "🔴 HELL (1~1000) - HP 5"],
        horizontal=True
    )
    
    if st.button("PRESS START BUTTON"):
        if nickname.strip() == "":
            st.warning("⚠️ 닉네임 입력 에러! 동전을 다시 넣어주세요.")
        else:
            if "EASY" in selected_diff:
                st.session_state.difficulty = "쉬움"
                st.session_state.max_value = 50
                st.session_state.hp = 10
            elif "HELL" in selected_diff:
                st.session_state.difficulty = "지옥"
                st.session_state.max_value = 1000
                st.session_state.hp = 5
            else:
                st.session_state.difficulty = "보통"
                st.session_state.max_value = 100
                st.session_state.hp = 7
                
            st.session_state.nickname = nickname
            st.session_state.secret_number = random.randint(1, st.session_state.max_value)
            st.session_state.attempts = 0
            st.session_state.history = [] 
            st.session_state.game_started = True
            st.session_state.game_over = False
            st.session_state.is_clear = False
            st.session_state.message = f"SYSTEM: [{nickname}] 접속 완료! 남은 HP: {'❤️' * st.session_state.hp}"
            st.rerun()
            
    st.divider()
    st.subheader("🏆 HALL OF FAME 🏆")
    
    tab1, tab2, tab3 = st.tabs(["🟢 EASY", "🔵 NORMAL", "🔴 HELL"])
    all_rankings = load_ranking()
    
    with tab1:
        easy_top3 = get_top_3_by_difficulty(all_rankings, "쉬움")
        if easy_top3:
            for i, record in enumerate(easy_top3):
                st.write(f"**[{i+1}위]** {record['nickname']} 님 (스코어: {record['attempts']}회)")
        else:
            st.caption("NO DATA.")
            
    with tab2:
        normal_top3 = get_top_3_by_difficulty(all_rankings, "보통")
        if normal_top3:
            for i, record in enumerate(normal_top3):
                st.write(f"**[{i+1}위]** {record['nickname']} 님 (스코어: {record['attempts']}회)")
        else:
            st.caption("NO DATA.")
            
    with tab3:
        hard_top3 = get_top_3_by_difficulty(all_rankings, "지옥")
        if hard_top3:
            for i, record in enumerate(hard_top3):
                st.write(f"**[{i+1}위]** {record['nickname']} 님 (스코어: {record['attempts']}회)")
        else:
            st.caption("NO DATA.")

# ==========================================
# 2단계: 게임 진행 화면
# ==========================================
if st.session_state.game_started and not st.session_state.game_over:
    st.success(st.session_state.message)
    
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
            if st.button("ATTACK (정답 확인)"):
                st.session_state.attempts += 1
                st.session_state.history.append(guess)
                
                if guess < st.session_state.secret_number:
                    st.session_state.hp -= 1
                    if st.session_state.hp <= 0:
                        st.session_state.message = f"💀 GAME OVER 💀 HP가 0이 되었습니다... 정답은 [{st.session_state.secret_number}]!"
                        st.session_state.game_over = True
                        st.session_state.is_clear = False
                    else:
                        st.session_state.message = f"🔺 UP!! [{guess}] 보다 높습니다. (남은 HP: {'❤️' * st.session_state.hp})"
                    st.rerun()
                    
                elif guess > st.session_state.secret_number:
                    st.session_state.hp -= 1
                    if st.session_state.hp <= 0:
                        st.session_state.message = f"💀 GAME OVER 💀 HP가 0이 되었습니다... 정답은 [{st.session_state.secret_number}]!"
                        st.session_state.game_over = True
                        st.session_state.is_clear = False
                    else:
                        st.session_state.message = f"🔻 DOWN!! [{guess}] 보다 낮습니다. (남은 HP: {'❤️' * st.session_state.hp})"
                    st.rerun()
                    
                else:
                    st.session_state.message = f"🎉 MISSION CLEAR! 정답: {st.session_state.secret_number} / 타격 횟수: {st.session_state.attempts}회"
                    st.session_state.game_over = True
                    st.session_state.is_clear = True 
                    
                    ranking = load_ranking()
                    ranking.append({
                        "nickname": st.session_state.nickname, 
                        "attempts": st.session_state.attempts,
                        "difficulty": st.session_state.difficulty
                    })
                    save_ranking(ranking)
                    st.rerun()
                    
        with btn_col2:
            if st.button("RESTART (새 게임)"):
                st.session_state.secret_number = random.randint(1, st.session_state.max_value)
                st.session_state.attempts = 0
                st.session_state.history = []
                
                if st.session_state.difficulty == "쉬움":
                    st.session_state.hp = 10
                elif st.session_state.difficulty == "지옥":
                    st.session_state.hp = 5
                else:
                    st.session_state.hp = 7
                    
                st.session_state.message = f"SYSTEM: 스테이지 재시작. (남은 HP: {'❤️' * st.session_state.hp})"
                st.rerun()
                
    with col2:
        st.subheader("📝 COMBAT LOG")
        if st.session_state.history:
            for idx, num in enumerate(st.session_state.history):
                st.write(f"[{idx+1}턴] 입력값: **{num}**")
        else:
            st.caption("대기 중...")
            
        # 개발자 전용 이스터에그 (치트키)
        if st.session_state.nickname == "KimJunSeok":
            st.markdown(f"<div style='text-align: right; color: #f472b6; font-size: 0.85rem; margin-top: 30px;'>[DEBUG] Target: {st.session_state.secret_number}</div>", unsafe_allow_html=True)

# ==========================================
# 3단계: 게임 종료 화면
# ==========================================
if st.session_state.game_over:
    if st.session_state.is_clear:
        st.balloons() 
        st.snow()     
        
    st.warning(st.session_state.message)
    st.info(f"▶ LOG 데이터: {', '.join(map(str, st.session_state.history))}")
    
    st.divider()
    st.subheader(f"🏆 {st.session_state.difficulty} RANKING 🏆")
    
    all_rankings = load_ranking()
    current_top3 = get_top_3_by_difficulty(all_rankings, st.session_state.difficulty)
    
    for i, record in enumerate(current_top3):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
        st.write(f"**{medal} RANK {i+1}:** {record['nickname']} ({record['attempts']} TRIES)")

    st.divider()
    
    if st.button("CONTINUE? (코인 넣기)"):
        st.session_state.game_started = False
        st.rerun()


# ==========================================
# 4단계: 방명록 섹션
# ==========================================
st.divider()
st.subheader("💬 GUEST BOOK")

with st.form("chat_form", clear_on_submit=True):
    if st.session_state.game_started:
        author_name = st.session_state.nickname
        st.text(f"ID: {author_name} (PLAYING)")
    else:
        author_name = st.text_input("ID:", max_chars=10, placeholder="닉네임")

    chat_message = st.text_input("MESSAGE:", max_chars=100, placeholder="메시지를 입력하세요...")
    submit_btn = st.form_submit_button("ENTER")

    if submit_btn:
        if not author_name.strip():
            st.error("ERROR: ID를 입력하세요.")
        elif not chat_message.strip():
            st.error("ERROR: 메시지를 입력하세요.")
        else:
            current_chats = load_chat()
            current_chats.append({"name": author_name, "msg": chat_message})
            save_chat(current_chats)
            st.rerun()

saved_chats = load_chat()
if saved_chats:
    for chat in reversed(saved_chats[-10:]):
        st.write(f"**[{chat['name']}]** > {chat['msg']}")
else:
    st.caption("데이터가 없습니다.")
