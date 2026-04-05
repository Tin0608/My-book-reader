import streamlit as st
import base64
from PyPDF2 import PdfReader
import requests

# =========================
# 🔐 权限校验 (云端安全版)
# =========================
def check_auth(code):
    # 【重要】部署后在 Streamlit 后台设置里填入 MY_VIP_CODE = "mmm_luv08"
    # 这样你的代码里就永远不会出现这个码，黑客也偷不走
    if "MY_VIP_CODE" in st.secrets:
        return code == st.secrets["MY_VIP_CODE"]
    else:
        # 本地测试时，如果没设 Secrets，默认还是这个
        return code == "mmm_luv08"

if 'is_paid' not in st.session_state:
    st.session_state.is_paid = False

# =========================
# 🌏 翻译接口
# =========================
@st.cache_data(show_spinner=False)
def translate_text(text):
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": text[:500], "langpair": "ko|zh-CN"}
        res = requests.get(url, params=params, timeout=10)
        return res.json()["responseData"]["translatedText"]
    except:
        return "⚠️ 翻译超时"

# =========================
# 🛠️ 页面基础
# =========================
st.set_page_config(page_title="沉浸式阅读空间", layout="wide")

@st.cache_data
def load_pdf_pages(file):
    reader = PdfReader(file)
    return [page.extract_text() for page in reader.pages]

def get_base64(file_obj):
    if file_obj:
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
        input_code = st.text_input("请输入会员码", type="password")
        if st.button("激活解锁"):
            if check_auth(input_code):
                st.session_state.is_paid = True
                st.success("解锁成功！")
                st.rerun()
            else:
                st.error("码不对哦")
    else:
        st.success("💎 已激活")

    st.divider()
    bg_file = st.file_uploader("🖼️ 更换爱豆背景", type=["jpg", "png", "jpeg"])
    font_size = st.slider("字号调整", 15, 60, 28)

# =========================
# 🎨 UI 样式 (包含之前的黑字修改)
# =========================
img_base64 = get_base64(bg_file)
bg_css = f'background-image: url("data:image/png;base64,{img_base64}"); background-size: cover; background-attachment: fixed;' if img_base64 else "background-color: #0E1117;"

st.markdown(f"""
<style>
.stApp {{ {bg_css} }}
.main::before {{ content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); z-index: -1; }}
.korean-text {{ font-size: {font_size}px; color: white; line-height: 1.6; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; text-shadow: 2px 2px 4px #000; }}
.chinese-text {{ font-size: {int(font_size*0.8)}px; color: black !important; background: rgba(255, 255, 255, 0.8); padding: 20px; border-radius: 12px; border-left: 6px solid #FF4B4B; }}
.lock-screen {{ background: rgba(0,0,0,0.8); padding: 50px; border: 2px solid #FF4B4B; text-align: center; border-radius: 20px; }}
</style>
""", unsafe_allow_html=True)

# =========================
# 📖 页面逻辑
# =========================
st.title("구의 증명 · 陪伴模式")
book_file = st.file_uploader("📖 上传 PDF", type=["pdf"])

if book_file:
    pages = load_pdf_pages(book_file)
    page_num = st.number_input("页码", min_value=1, max_value=len(pages), step=1)
    
    # 修改免费试读页数为 20
    if page_num > 20 and not st.session_state.is_paid:
        st.markdown('<div class="lock-screen"><h2>🔒 试读结束</h2><p>解锁请联系站长获取会员码</p></div>', unsafe_allow_html=True)
    else:
        text = pages[page_num - 1]
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f'<div class="korean-text">{text}</div>', unsafe_allow_html=True)
        with c2:
            if st.button("🌐 翻译"):
                st.markdown(f'<div class="chinese-text">{translate_text(text)}</div>', unsafe_allow_html=True)
else:
    st.info("👋 上传 PDF 开始沉浸式阅读（前20页试读）")
