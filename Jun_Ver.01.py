# ==========================================
# 💡 [V1.1] Final Donation Section (Ko-fi Only)
# ==========================================
st.divider()
st.markdown("""
<style>
    .donate-container { text-align: center; margin-top: 40px; margin-bottom: 20px; }
    .kofi-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #f472b6 !important;
        color: #ffffff !important;
        padding: 16px 32px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 800; /* 훨씬 굵게 */
        font-family: 'NeoDunggeunmo', sans-serif;
        font-size: 1.5rem !important; /* 글씨 크기 대폭 확대 */
        transition: all 0.2s ease-in-out;
        box-shadow: 0 6px 0 #be185d; /* 입체감 강화 */
        border: none;
    }
    .kofi-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 0 #be185d;
        filter: brightness(1.1);
    }
</style>

<div class="donate-container">
    <p style="color: #a1a1aa; font-family: 'Pretendard', sans-serif; font-size: 1rem; margin-bottom: 20px;">
        Did you enjoy the game? Support the arcade! 🕹️
    </p>
    <a href="https://ko-fi.com/junseokkim" target="_blank" class="kofi-btn">
        ☕ SUPPORT ON KO-FI
    </a>
</div>
""", unsafe_allow_html=True)
