import streamlit as st
import base64
from PyPDF2 import PdfReader
import requests

# =========================
# 🔐 权限校验 (云端安全版)
# =========================
def check_auth(code):
    if "MY_VIP_CODE" in st.secrets:
        return code == st.secrets["MY_VIP_CODE"]
    else:
        return code == "mmm_luv08"

# 使用 session_state 确保刷新网页后登录状态不消失
if 'is_paid' not in st.session_state:
    st.session_state.is_paid = False

# =========================
# 🌏 谷歌翻译接口 (比之前的 MyMemory 更稳)
# =========================
@st.cache_data(show_spinner=False)
def translate_text(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ko&tl=zh-CN&dt=t&q={text}"
        res = requests.get(url, timeout=10).json()
        return "".join([part[0] for part in res[0] if part[0]])
    except:
        return "⚠️ 翻译官去喝咖啡了，请重试"

# =========================
# 🛠️ 页面基础设置
# =========================
# 【修改点 1：浏览器标签页标题】
st.set_page_config(page_title="爱豆伴读空间", layout="wide")

@st.cache_data
def load_pdf_pages(file):
    reader = PdfReader(file)
    return [page.extract_text() for page in reader.pages]

def get_base64(file_obj):
    if file_obj:
        # 兼容手机端上传和处理
        file_bytes = file_obj.read()
        file_obj.seek(0)
        return base64.b64encode(file_bytes).decode()
    return None

# =========================
# ⚙️ 侧边栏
# =========================
with st.sidebar:
    st.header("✨ 会员中心")
    if not st.session_state.is_paid:
        input_code = st.text_input("请输入会员码激活", type="password")
        if st.button("立即解锁"):
            if check_auth(input_code):
                st.session_state.is_paid = True
                st.success("💎 解锁成功！")
                st.rerun()
            else:
                st.error("码不对哦，请重新检查")
    else:
        st.success("💎 已激活全本权限")

    st.divider()
    bg_file = st.file_uploader("🖼️ 更换爱豆背景", type=["jpg", "png", "jpeg"])
    font_size = st.slider("韩文字号调整", 15, 60, 28)

# =========================
# 🎨 UI 样式 (黑字翻译框 + 半透明遮罩)
# =========================
img_base64 = get_base64(bg_file)
# 如果没上传背景，显示深色背景；上传了则全屏覆盖
bg_css = f'background-image: url("data:image/png;base64,{img_base64}"); background-size: cover; background-attachment: fixed;' if img_base64 else "background-color: #0E1117;"

st.markdown(f"""
<style>
.stApp {{ {bg_css} }}
/* 增加一层黑色半透明遮罩，防止背景图太花看不清字 */
.main::before {{ 
    content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
    background-color: rgba(0, 0, 0, 0.4); z-index: -1; 
}}
.korean-text {{ 
    font-size: {font_size}px; color: white; line-height: 1.6; 
    background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; 
    text-shadow: 2px 2px 4px #000; 
}}
/* 重点：翻译框强制设为黑字白底 */
.chinese-text {{ 
    font-size: {int(font_size*0.7)}px; color: #000000 !important; 
    background: rgba(255, 255, 255, 0.9); padding: 20px; 
    border-radius: 12px; border-left: 8px solid #FF4B4B; 
    margin-top: 10px; font-weight: 500;
}}
.lock-screen {{ 
    background: rgba(0,0,0,0.85); padding: 50px; border: 2px solid #FF4B4B; 
    text-align: center; border-radius: 20px; color: white;
}}
</style>
""", unsafe_allow_html=True)

# =========================
# 📖 页面主逻辑
# =========================
# 【修改点 2：网页中央的大标题】
st.title("📚 CORTIS · 专属阅读空间")

book_file = st.file_uploader("📖 请上传 PDF 电子书", type=["pdf"])

if book_file:
    pages = load_pdf_pages(book_file)
    total = len(pages)
    page_num = st.number_input("翻页控制", min_value=1, max_value=total, step=1)
    
    # 权限检查逻辑
    if page_num > 10 and not st.session_state.is_paid:
        st.markdown(f'<div class="lock-screen"><h2>🔒 试读已结束 (10/{total})</h2><p>请输入会员码解锁后续内容</p></div>', unsafe_allow_html=True)
    else:
        text = pages[page_num - 1]
        c1, c2 = st.columns([1.5, 1]) # 左右布局：原文大一点，翻译小一点
        
        with c1:
            st.markdown(f'<div class="korean-text">{text}</div>', unsafe_allow_html=True)
        
        with c2:
            if st.button("🌐 点击翻译本页"):
                with st.spinner("正在翻译..."):
                    result = translate_text(text)
                    st.markdown(f'<div class="chinese-text"><strong>中文翻译：</strong><br>{result}</div>', unsafe_allow_html=True)
else:
    st.info("👋 欢迎！上传 PDF 即可开始阅读（前10页免费试读）")
