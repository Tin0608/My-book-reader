import streamlit as st
from PyPDF2 import PdfReader
import requests

# 设置页面
st.set_page_config(page_title="爱豆伴读", layout="wide")

# 从 Secrets 获取会员码
try:
    VIP_CODE = st.secrets["MY_VIP_CODE"]
except:
    VIP_CODE = "mmm_luv08"

# 自定义样式：白底黑字翻译，半透明遮罩
st.markdown("""
    <style>
    .stApp { background-size: cover; background-position: center; }
    .trans-box {
        background-color: rgba(255, 255, 255, 0.95);
        color: #000000;
        padding: 20px;
        border-radius: 10px;
        line-height: 1.6;
        font-size: 18px;
        border: 2px solid #f0f0f0;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.title("💖 专属配置")
    auth_input = st.text_input("输入会员码激活全本", type="password")
    is_active = (auth_input == VIP_CODE)
    
    if is_active:
        st.success("💎 已激活全本权限")
    else:
        st.warning("🔒 试读模式（限10页）")
    
    bg_img = st.file_uploader("上传爱豆背景图")
    if bg_img:
        import base64
        data = base64.b64encode(bg_img.read()).decode()
        st.markdown(f" <style>.stApp {{ background-image: url('data:image/png;base64,{data}'); }} </style> ", unsafe_allow_html=True)

# 主界面
st.title("📚 沉浸式韩文阅读器")
uploaded_file = st.file_uploader("上传 PDF 电子书", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    total_pages = len(reader.pages)
    allowed_pages = total_pages if is_active else min(total_pages, 10)
    
    page_num = st.number_input("当前页码", min_value=1, max_value=total_pages, step=1)
    
    if not is_active and page_num > 10:
        st.error("🚫 此页已锁定，请输入会员码解锁全书。")
    else:
        text = reader.pages[page_num-1].extract_text()
        st.subheader(f"第 {page_num} 页原文")
        st.text_area("", text, height=300)
        
        if st.button("🌐 翻译成中文"):
            with st.spinner("正在努力翻译中..."):
                try:
                    res = requests.post("https://api.translated.net/get", 
                                      params={"q": text, "langpair": "ko|zh-CN"}).json()
                    trans_text = res['responseData']['translatedText']
                    st.markdown(f'<div class="trans-box"><strong>中文翻译：</strong><br>{trans_text}</div>', unsafe_allow_html=True)
                except:
                    st.error("翻译接口繁忙，请稍后再试。")
