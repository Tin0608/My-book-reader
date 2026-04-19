import streamlit as st
import base64
import hashlib
import uuid
from PyPDF2 import PdfReader
import requests

# 1. 基础配置：强制展开侧边栏，让用户第一眼看到“待激活”和“机器码”
st.set_page_config(
    page_title="马丁研习空间", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# =========================
# 🔐 核心权限加密引擎
# =========================

def get_machine_code():
    node = uuid.getnode()
    return hashlib.sha256(str(node).encode()).hexdigest()[:10].upper()

def verify_token(m_code, input_token):
    SECRET = "MARTIN_PRO_MAX_2026"
    levels = {
        "LEVEL_MONTH": hashlib.md5((m_code + "LM" + SECRET).encode()).hexdigest()[:8].upper(),    # ¥29.9
        "LEVEL_YEAR": hashlib.md5((m_code + "LY" + SECRET).encode()).hexdigest()[:8].upper(),     # ¥98
        "LEVEL_PERP": hashlib.md5((m_code + "LP" + SECRET).encode()).hexdigest()[:8].upper()      # ¥299
    }
    for lv, code in levels.items():
        if input_token == code:
            return lv
    return None

if 'auth_level' not in st.session_state:
    st.session_state.auth_level = None

# =========================
# ⚙️ 侧边栏：阶梯权益与视觉配置
# =========================
with st.sidebar:
    st.title("✨ 空间配置")
    m_code = get_machine_code()
    
    # 权限状态显示
    if not st.session_state.auth_level:
        st.error("🔒 待激活 (限时试读中)")
        st.markdown(f"**机器码：** `{m_code}`")
        st.caption("复制上方机器码发给站长获取专属口令")
        
        token = st.text_input("输入验证口令", type="password")
        if st.button("开启全篇模式"):
            res = verify_token(m_code, token)
            if res:
                st.session_state.auth_level = res
                st.rerun()
            else:
                st.error("口令无效，请核对权限档位")
        
        st.divider()
        st.markdown("""
        ### 📥 权益说明
        - **¥29.9**: 月度内测 (全功能+单书)
        - **¥98**: 年度 Pro (不限书籍)
        - **¥299**: 永久 Creator (全解锁)
        """)
        bg_file = None 
    else:
        names = {"LEVEL_MONTH": "月度内测版", "LEVEL_YEAR": "年度 Pro", "LEVEL_PERP": "永久 Creator"}
        st.success(f"💎 当前身份：{names.get(st.session_state.auth_level)}")
        st.divider()
        st.subheader("🖼️ 视觉配置")
        # 付费用户开启背景更换
        bg_file = st.file_uploader("配置专属氛围背景", type=["jpg", "png", "jpeg"])

    st.divider()
    font_size = st.slider("阅读字阶", 18, 55, 28)

# =========================
# 🎨 UI 样式渲染
# =========================
def get_b64(file):
    if file:
        data = file.read()
        file.seek(0)
        return base64.b64encode(data).decode()
    return None

img_data = get_b64(bg_file)
bg_style = f'background-image: url("data:image/png;base64,{img_data}"); background-size: cover !important; background-attachment: fixed !important;' if img_data else "background-color: #1e1e1e !important;"

st.markdown(f"""
<style>
.stApp {{ {bg_style} background-position: center !important; }}
header {{visibility: hidden !important;}}
.stAppDeployButton {{display:none !important;}}
footer {{visibility: hidden !important;}}

.korean-panel {{ 
    font-size: {font_size}px; color: white; line-height: 1.7; 
    background: rgba(0,0,0,0.4); padding: 35px; border-radius: 20px; 
    backdrop-filter: blur(12px); text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    min-height: 400px;
}}
.chinese-panel {{ 
    font-size: {int(font_size*0.85)}px; color: black !important; 
    background: rgba(255, 255, 255, 0.92); padding: 25px; border-radius: 15px; 
    border-left: 10px solid #4B9BFF;
}}
</style>
""", unsafe_allow_html=True)

# =========================
# 📖 阅读主逻辑
# =========================
st.title("구의 증명 · 陪伴式研习")
book = st.file_uploader("📂 载入 PDF 文档", type=["pdf"])

if book:
    # 核心：解析 PDF
    reader = PdfReader(book)
    pages = [p.extract_text() for p in reader.pages]
    total_pages = len(pages)
    
    # 页面选择
    page_no = st.number_input("跳转页码", min_value=1, max_value=total_pages, step=1, value=1)
    
    # --- 🔒 权限拦截逻辑 ---
    # 1. 试读拦截：未激活用户超过 20 页
    is_trial_limit = (not st.session_state.auth_level) and (page_no > 20)
    
    # 2. 书籍拦截：月度版只能读《九的证明》
    is_target_book = "구" in book.name or "九" in book.name
    is_book_blocked = (st.session_state.auth_level == "LEVEL_MONTH") and (not is_target_book)
    
    if is_trial_limit:
        st.warning(f"🔒 **前 20 页试读已结束**。后续内容共 {total_pages - 20} 页，请在侧边栏输入授权口令解锁全本。")
        st.info("💡 站长提示：购买月度版即可解锁马丁专属背景及全篇阅读。")
    elif is_book_blocked:
        st.error("🚫 月度版仅支持《九的证明》单书研读，更多书籍请升级至年度版。")
    else:
        # --- 🔓 通过拦截，显示内容 ---
        txt = pages[page_no - 1]
        if txt.strip():
            c1, c2 = st.columns([1.8, 1])
            with c1:
                st.markdown(f'<div class="korean-panel">{txt}</div>', unsafe_allow_html=True)
            with c2:
                if st.button("🌐 语义解析"):
                    with st.spinner('AI 同步中...'):
                        try:
                            res = requests.get("https://api.mymemory.translated.net/get", 
                                             params={"q": txt[:450], "langpair": "ko|zh-CN"}).json()
                            st.markdown(f'<div class="chinese-panel">{res["responseData"]["translatedText"]}</div>', unsafe_allow_html=True)
                        except:
                            st.error("网络翻译接口忙，请稍后再试。")
        else:
            st.info("这一页似乎没有可识别的文字内容。")
