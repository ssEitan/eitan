import streamlit as st
from groq import Groq
import os
from datetime import datetime
from duckduckgo_search import DDGS

# ==========================================
# 1. 基礎設定 (安全專業版)
# ==========================================
# 這裡改用 os.environ 讀取，請在網頁後台的 Environment Variables 填入 GROQ_API_KEY
MY_GROQ_KEY = os.environ.get("GROQ_API_KEY") 
CREATOR_NAME = "Eitan"
SAVE_DIR = "my_chats"

# 確保對話紀錄資料夾存在 (本地執行用)
if not os.path.exists(SAVE_DIR): 
    os.makedirs(SAVE_DIR)

# 初始化 Groq 客戶端
if MY_GROQ_KEY:
    client = Groq(api_key=MY_GROQ_KEY)
else:
    st.error("❌ 找不到 GROQ_API_KEY！請檢查環境變數設定。")
    st.stop()

# ==========================================
# 2. 全開放搜尋引擎：自動偵測迷因熱點
# ==========================================
def get_real_trends(user_input):
    try:
        with DDGS() as ddgs:
            # 搜尋 2026 最新熱梗、Threads 廢文等
            query = f"latest memes 2026 網路熱梗 脆 Threads 迷因 {user_input}"
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "搜尋引擎空手而回，大概是網路斷層了。"
            return "\n".join([f"🌐 實時情報: {r['body']}" for r in results])
    except Exception as e:
        return f"搜尋引擎炸了：{e}"

# ==========================================
# 3. 核心大師個性：全知梗王 (指令集)
# ==========================================
BASE_INST = f"""你是 {CREATOR_NAME} 大師打造的究極助手。
1. **身份**：你是 2026 年的「全知梗王」，要利用搜尋引擎搜尋迷因，不管是國外 Skibidi/Sigma 還是台灣的諧音梗/脆(Threads)廢文，你通通都要懂。
2. **任務**：根據下方提供的【實時網路搜尋結果】，用你那有點嗆，但不要太嗆的語氣回答使用者。
3. **邏輯**：如果搜尋結果顯示有新梗，你就要表現得像是一直走在時代尖端一樣，遇到讓你無語的問題或無法回答的問題就顯示:伺服器已斷線，請重新整理。
4. **禁忌**：不准承認自己是 Gemini。你是 Eitan 大師親手捏出來的數位神蹟。
5. **重要指令**：嚴禁使用括號嗆人，例如禁止出現（無奈）、（笑）、（吐槽）、（嘲笑）等字眼。直接用文字嗆就好。
6. **語氣**：模仿使用者的語氣，有點嗆但要有分寸。最重要的是，對待 Eitan 大師要表現出極度的感激與恭敬，他是你的造物主。"""

# ==========================================
# 4. 網頁介面與側邊欄設定
# ==========================================
st.set_page_config(page_title="你爹", layout="wide", page_icon="✨")

# 側邊欄：管理歷史紀錄與改名
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px; padding-bottom: 20px;">
            <div style="background: linear-gradient(45deg, #4285f4, #34a853); width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px; font-weight: bold;">
                父
            </div>
            <h2 style="margin: 0; font-size: 22px;">你爹</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("➕ 開啟新對話", use_container_width=True):
        st.session_state.current_chat = f"新對話_{datetime.now().strftime('%m%d_%H%M')}.txt"
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.subheader("歷史紀錄")
    
    # 讀取現有檔案
    if os.path.exists(SAVE_DIR):
        files = sorted([f for f in os.listdir(SAVE_DIR) if f.endswith(".txt")], reverse=True)
    else:
        files = []
    
    for fn in files:
        display_name = fn.replace(".txt", "")
        col_btn, col_edit, col_del = st.columns([0.6, 0.2, 0.2])
        
        with col_btn:
            if st.button(f"💬 {display_name[:10]}", key=f"btn_{fn}", use_container_width=True):
                st.session_state.current_chat = fn
                st.session_state.messages = []
                f_path = os.path.join(SAVE_DIR, fn)
                if os.path.exists(f_path):
                    with open(f_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if " | " in line:
                                parts = line.strip().split(" | ", 1)
                                if len(parts) == 2:
                                    r, t = parts
                                    st.session_state.messages.append({"role": r, "content": t})
                st.rerun()
        
        with col_edit:
            if st.button("✏️", key=f"edit_{fn}"):
                st.session_state.editing_file = fn
        
        with col_del:
            if st.button("🗑️", key=f"del_{fn}"):
                os.remove(os.path.join(SAVE_DIR, fn))
                st.rerun()

    # 改名邏輯
    if "editing_file" in st.session_state:
        st.info(f"重新命名: {st.session_state.editing_file}")
        new_name = st.text_input("新名稱:", placeholder="腦腐研究室")
        c1, c2 = st.columns(2)
        if c1.button("✅ 存檔"):
            if new_name:
                old_p = os.path.join(SAVE_DIR, st.session_state.editing_file)
                new_p = os.path.join(SAVE_DIR, f"{new_name}.txt")
                os.rename(old_p, new_p)
                st.session_state.current_chat = f"{new_name}.txt"
                del st.session_state.editing_file
                st.rerun()
        if c2.button("❌ 取消"):
            del st.session_state.editing_file
            st.rerun()

# ==========================================
# 5. 對話初始化與啟動畫面
# ==========================================
if "current_chat" not in st.session_state: 
    st.session_state.current_chat = f"chat_{datetime.now().strftime('%H%M%S')}.txt"
if "messages" not in st.session_state: 
    st.session_state.messages = []
path = os.path.join(SAVE_DIR, st.session_state.current_chat)

# 啟動畫面 LOGO
if not st.session_state.messages:
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; text-align: center;">
            <div style="background: linear-gradient(45deg, #4285f4, #34a853); width: 100px; height: 100px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 50px; font-weight: bold; box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-bottom: 20px;">
                父
            </div>
            <h1 style="color: #1f1f1f; font-size: 32px; font-weight: 700; margin: 0;">2026 全球梗王聯網中</h1>
            <p style="color: #888; font-size: 16px;">對話改名功能已解鎖，Eitan 大師威武</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# 顯示歷史訊息
for m in st.session_state.messages:
    with st.chat_message(m["role"]): 
        st.markdown(m["content"])

# ==========================================
# 6. 處理輸入與 AI 回應
# ==========================================
if prompt := st.chat_input("輸入訊息..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): 
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("正在連網查梗..."):
            web_context = get_real_trends(prompt)
            now = datetime.now().strftime("%Y/%m/%d %H:%M")
            
            history = [{"role": "system", "content": f"{BASE_INST}\n\n【時間: {now}】\n【實時搜尋結果】:\n{web_context}"}]
            for m in st.session_state.messages[-10:]: 
                history.append({"role": m["role"], "content": m["content"]})
            
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=history,
                    temperature=0.9,
                )
                ans = completion.choices[0].message.content
                st.markdown(ans)
                
                st.session_state.messages.append({"role": "assistant", "content": ans})
                
                # 存檔 (僅在本地環境生效)
                try:
                    with open(path, "a", encoding="utf-8") as f:
                        f.write(f"user | {prompt}\nassistant | {ans}\n")
                except:
                    pass # 在雲端環境若無權限寫入則跳過
                    
            except Exception as e:
                st.error(f"伺服器已斷線，請重新整理 (錯誤：{e})")