import streamlit as st
import json
import random
from datetime import datetime
import os

# 設定頁面配置
st.set_page_config(
    page_title="智能單字卡",
    page_icon="📚",
    layout="centered"
)

# 資料檔案路徑
DATA_FILE = "vocabulary_data.json"

# 初始化資料結構
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "words": [
                {"word": "example", "translation": "範例", "familiarity": 0, "last_seen": None},
                {"word": "practice", "translation": "練習", "familiarity": 0, "last_seen": None},
                {"word": "study", "translation": "學習", "familiarity": 0, "last_seen": None}
            ]
        }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 根據熟悉度計算權重（熟悉度越低，權重越高）
def calculate_weight(familiarity):
    # familiarity 範圍: -10 (很不熟) 到 10 (很熟)
    # 權重範圍: 1 到 20
    return max(1, 20 - familiarity)

# 選擇下一個單字（加權隨機）
def select_next_word(words):
    if not words:
        return None
    
    weights = [calculate_weight(w['familiarity']) for w in words]
    return random.choices(words, weights=weights, k=1)[0]

# 初始化 session state
if 'data' not in st.session_state:
    st.session_state.data = load_data()
    st.session_state.current_word = select_next_word(st.session_state.data['words'])
    st.session_state.show_translation = False

# CSS 樣式
st.markdown("""
<style>
    .word-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 60px 40px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin: 20px 0;
    }
    .word-text {
        font-size: 48px;
        font-weight: bold;
        color: white;
        margin-bottom: 20px;
    }
    .translation-text {
        font-size: 32px;
        color: #f0f0f0;
        margin-top: 10px;
    }
    .familiarity-bar {
        margin: 20px 0;
    }
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# 標題
st.title("📚 智能單字卡")

# 顯示目前單字
if st.session_state.current_word:
    word_data = st.session_state.current_word
    
    # 單字卡片
    st.markdown(f"""
    <div class="word-card">
        <div class="word-text">{word_data['word']}</div>
        {f'<div class="translation-text">{word_data["translation"]}</div>' if st.session_state.show_translation else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # 顯示/隱藏翻譯按鈕
    if st.button("👁️ 顯示/隱藏翻譯", use_container_width=True):
        st.session_state.show_translation = not st.session_state.show_translation
        st.rerun()
    
    st.markdown("---")
    
    # 熟悉度顯示
    familiarity_percent = (word_data['familiarity'] + 10) / 20 * 100
    st.markdown(f"**熟悉度:** {word_data['familiarity']}")
    st.progress(familiarity_percent / 100)
    
    st.markdown("---")
    
    # 左右滑動按鈕
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ 不熟", use_container_width=True, type="secondary"):
            # 降低熟悉度
            for word in st.session_state.data['words']:
                if word['word'] == word_data['word']:
                    word['familiarity'] = max(-10, word['familiarity'] - 2)
                    word['last_seen'] = datetime.now().isoformat()
                    break
            
            save_data(st.session_state.data)
            st.session_state.current_word = select_next_word(st.session_state.data['words'])
            st.session_state.show_translation = False
            st.rerun()
    
    with col2:
        if st.button("➡️ 很熟", use_container_width=True, type="primary"):
            # 提高熟悉度
            for word in st.session_state.data['words']:
                if word['word'] == word_data['word']:
                    word['familiarity'] = min(10, word['familiarity'] + 2)
                    word['last_seen'] = datetime.now().isoformat()
                    break
            
            save_data(st.session_state.data)
            st.session_state.current_word = select_next_word(st.session_state.data['words'])
            st.session_state.show_translation = False
            st.rerun()

else:
    st.info("目前沒有單字，請先新增一些單字！")

st.markdown("---")

# 新增單字區域
st.subheader("➕ 新增生字")

with st.form("add_word_form"):
    new_word = st.text_input("英文單字", placeholder="例如: vocabulary")
    new_translation = st.text_input("中文翻譯", placeholder="例如: 詞彙")
    
    if st.form_submit_button("新增單字", use_container_width=True):
        if new_word and new_translation:
            # 檢查是否已存在
            exists = any(w['word'].lower() == new_word.lower() for w in st.session_state.data['words'])
            
            if not exists:
                st.session_state.data['words'].append({
                    "word": new_word,
                    "translation": new_translation,
                    "familiarity": 0,
                    "last_seen": None
                })
                save_data(st.session_state.data)
                st.success(f"✅ 成功新增單字: {new_word}")
                st.rerun()
            else:
                st.warning("⚠️ 這個單字已經存在！")
        else:
            st.error("❌ 請填寫完整的單字和翻譯")

# 側邊欄 - 統計資訊
with st.sidebar:
    st.header("📊 學習統計")
    
    total_words = len(st.session_state.data['words'])
    st.metric("總單字數", total_words)
    
    familiar_words = sum(1 for w in st.session_state.data['words'] if w['familiarity'] >= 5)
    st.metric("熟悉的單字", familiar_words)
    
    unfamiliar_words = sum(1 for w in st.session_state.data['words'] if w['familiarity'] <= -3)
    st.metric("需加強的單字", unfamiliar_words)
    
    st.markdown("---")
    
    # 單字列表
    st.subheader("📝 單字列表")
    
    if st.session_state.data['words']:
        # 按熟悉度排序
        sorted_words = sorted(st.session_state.data['words'], key=lambda x: x['familiarity'])
        
        for word in sorted_words:
            familiarity_emoji = "🟢" if word['familiarity'] >= 5 else "🟡" if word['familiarity'] >= 0 else "🔴"
            st.text(f"{familiarity_emoji} {word['word']} ({word['familiarity']})")
    
    st.markdown("---")
    
    # 重置資料按鈕
    if st.button("🔄 重置所有進度", use_container_width=True):
        for word in st.session_state.data['words']:
            word['familiarity'] = 0
            word['last_seen'] = None
        save_data(st.session_state.data)
        st.success("已重置所有進度！")
        st.rerun()
