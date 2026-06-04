import streamlit as st
import random
import json
import os

# --- 💾 랭킹 및 방명록 데이터 저장/불러오기 ---
RANKING_FILE = "ranking.json"
CHAT_FILE = "chat.json"

def load_ranking():
    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_ranking(ranking_list):
    with open(RANKING_FILE, "w", encoding="utf-8") as f:
        json.dump(ranking_list, f, ensure_ascii=False, indent=4)

def load_chat():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_chat(chat_list):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_list, f, ensure_ascii=False, indent=4)


# --- 🎮 웹페이지 기본 설정 ---
st.set_page_config(page_title="Up & Down Game", page_icon="🎮")
st.title("🚀 U P  &  D O W N  G A M E")
st.caption("Created by J.S.Kim")

# --- 🧠 기억 상자(세션) 초기화 ---
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.game_over = False

# ==========================================
# 1단계: 게임 시작 전 (닉네임 입력 화면)
# ==========================================
if not st.session_state.game_started:
    st.subheader("환영합니다! 플레이어의 이름을 알려주세요.")
    nickname = st.text_input("💡 닉네임 입력:")
    
    if st.button("게임 시작하기"):
        if nickname.strip() == "":
            st.warning("닉네임을 입력해야 시작할 수 있습니다!")
        else:
            st.session_state.nickname = nickname
            st.session_state.secret_number = random.randint(1, 100)
            st.session_state.attempts = 0
            st.session_state.history = [] 
            st.session_state.game_started = True
            st.session_state.game_over = False
            st.session_state.message = f"반갑습니다, **{nickname}**님! 컴퓨터가 숫자를 골랐습니다."
            st.rerun()

# ==========================================
# 2단계: 게임 진행 화면
# ==========================================
if st.session_state.game_started and not st.session_state.game_over:
    st.info(st.session_state.message)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 💡 [UX 개선 핵심] 플레이어가 직접 입력 방식을 선택할 수 있는 토글 스위치
        input_mode = st.radio(
            "접속하신 환경에 맞는 입력 방식을 선택하세요:",
            ["⌨️ PC 환경 (직접 입력)", "📱 모바일 환경 (슬라이더)"],
            horizontal=True
        )
        
        st.write("") # 한 줄 띄우기
        
        # 선택한 모드에 따라 입력창을 다르게 보여줌
        if input_mode == "⌨️ PC 환경 (직접 입력)":
            guess = st.number_input("숫자를 입력하세요 (1~100):", min_value=1, max_value=100, value=50, step=1)
        else:
            guess = st.slider("숫자를 선택하세요 (1~100):", min_value=1, max_value=100, value=50)
        
        st.write("") # 한 줄 띄우기
        
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("정답 확인하기", use_container_width=True):
                st.session_state.attempts += 1
                st.session_state.history.append(guess)
                
                if guess < st.session_state.secret_number:
                    st.session_state.message = f"🔺 UP! {guess}보다 큽니다. (현재 시도: {st.session_state.attempts}회)"
                    st.rerun()
                elif guess > st.session_state.secret_number:
                    st.session_state.message = f"🔻 DOWN! {guess}보다 작습니다. (현재 시도: {st.session_state.attempts}회)"
                    st.rerun()
                else:
                    st.session_state.message = f"🎉 대정답! {st.session_state.secret_number}을(를) {st.session_state.attempts}번 만에 맞추셨습니다!"
                    st.session_state.game_over = True
                    
                    ranking = load_ranking()
                    ranking.append({"nickname": st.session_state.nickname, "attempts": st.session_state.attempts})
                    ranking = sorted(ranking, key=lambda x: x["attempts"])
                    save_ranking(ranking)
                    st.rerun()
                    
        with btn_col2:
            if st.button("🔄 현재 게임 리셋", use_container_width=True):
                st.session_state.secret_number = random.randint(1, 100)
                st.session_state.attempts = 0
                st.session_state.history = []
                st.session_state.message = f"🔄 게임이 리셋되었습니다! **{st.session_state.nickname}**님, 새로운 숫자를 맞춰보세요."
                st.rerun()
                
    with col2:
        st.subheader("📝 나의 기록")
        if st.session_state.history:
            for idx, num in enumerate(st.session_state.history):
                st.write(f"{idx+1}회차: **{num}**")
        else:
            st.caption("아직 입력한 숫자가 없습니다.")

# ==========================================
# 3단계: 게임 종료 및 명예의 전당(랭킹) 화면
# ==========================================
if st.session_state.game_over:
    st.balloons()
    st.success(st.session_state.message)
    st.info(f"내가 입력했던 숫자들: {', '.join(map(str, st.session_state.history))}")
    
    st.divider()
    st.subheader("🏆 명예의 전당 (Top 5) 🏆")
    
    ranking = load_ranking()
    for i, record in enumerate(ranking[:5]):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🏅"
        st.write(f"**{medal} {i+1}위:** {record['nickname']}님 ({record['attempts']}번 시도)")

    st.divider()
    
    if st.button("다른 닉네임으로 다시 도전하기"):
        st.session_state.game_started = False
        st.rerun()


# ==========================================
# 4단계: 한 줄 방명록 섹션 (화면 맨 아래 항상 노출)
# ==========================================
st.divider()
st.subheader("💬 J.S.Kim의 게임 방명록")

with st.form("chat_form", clear_on_submit=True):
    if st.session_state.game_started:
        author_name = st.session_state.nickname
        st.text(f"✍️ 작성자: {author_name} (게임 참가 중)")
    else:
        author_name = st.text_input("닉네임", max_chars=10, placeholder="이름")

    chat_message = st.text_input("응원 한 마디를 남겨주세요!", max_chars=100, placeholder="재밌네요! 등등")
    submit_btn = st.form_submit_button("댓글 달기")

    if submit_btn:
        if not author_name.strip():
            st.error("닉네임을 입력해 주세요!")
        elif not chat_message.strip():
            st.error("내용을 입력해 주세요!")
        else:
            current_chats = load_chat()
            current_chats.append({"name": author_name, "msg": chat_message})
            save_chat(current_chats)
            st.rerun()

saved_chats = load_chat()
if saved_chats:
    for chat in reversed(saved_chats[-10:]):
        st.write(f"**{chat['name']}** : {chat['msg']}")
else:
    st.caption("아직 작성된 메시지가 없습니다. 첫 번째 발자취를 남겨보세요!")
