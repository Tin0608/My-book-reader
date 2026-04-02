import streamlit as st
from PyPDF2 import PdfReader
import requests

# 1. 基础页面设置
st.set_page_config(page_title="爱豆伴读 - 沉浸式阅读", layout="wide")

# 2. 从 Secrets 安全获取会员码（如果没设，默认是 mmm_luv08）
try:
    VIP_CODE = st.secrets["MY_VIP_CODE"]
except:
    VIP_CODE = "mmm_luv08"

# 3. 视觉样式美化（让翻译框更漂亮）
st.markdown("""
    <style>
    .stApp { background-size: cover; background-position: center; }
    .trans-box {
        background-color: rgba(255, 255, 255, 0.98);
        color: #000000;
        padding: 20px;
        border-radius: 12px;
        line-height: 1.8;
        font-size: 18px;
        border-left: 5px solid #ff4b4b;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 侧边栏：权限与个性化
with st.sidebar:
    st.title("💖 专属配置")
    auth_input = st.text_input("输入会员码激活全本", type="password")
    is_active = (auth_input == VIP_CODE)
    
    if is_active:
        st.success("💎 已激活全本权限")
    else:
        st.warning("🔒 试读模式（限10页）预览")
    
    st.divider()
    bg_img = st.file_uploader("上传爱豆背景图")
    if bg_img:
        import base64
        data = base64.b64encode(bg_img.read()).decode()
        st.markdown(f" <style>.stApp {{ background-image: url('data:image/png;base64,{data}'); }} </style> ", unsafe_allow_html=True)

# 5. 主界面逻辑
st.title("📚 沉浸式韩文阅读器")
uploaded_file = st.file_uploader("请上传你的 PDF 电子书", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    total_pages = len(reader.pages)
    
    # 翻页控制
    page_num = st.number_input("翻页 (当前页码)", min_value=1, max_value=total_pages, step=1)
    
    # 权限检查：非会员翻到10页以上报错
    if not is_active and page_num > 10:
        st.error("🚫 此页已锁定，请输入会员码解锁全书内容。")
    else:
        # 提取文字
        text = reader.pages[page_num-1].extract_text()
        st.subheader(f"第 {page_num} / {total_pages} 页原文")
        st.text_area("", text, height=300)
        
        # --- 核心修改：Google 翻译引擎 ---
        if st.button("🌐 点击 Google 翻译"):
            if not text.strip():
                st.warning("这一页好像没有文字可以翻译呢~")
            else:
                with st.spinner("Google 翻译官正在全力翻译中..."):
                    try:
                        # 使用 Google 翻译的公开备用接口，更稳定
                        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ko&tl=zh-CN&dt=t&q={text}"
                        res = requests.get(url, timeout=10).json()
                        # 自动拼接可能被拆分的翻译段落
                        trans_text = "".join([part[0] for part in res[0] if part[0]])
                        
                        st.markdown(f'''
                            <div class="trans-box">
                                <strong style="color:#ff4b4b;">🏮 Google 中文翻译：</strong><br>
                                {trans_text}
                            </div>
                        ''', unsafe_allow_html=True)
                    except Exception as e:
                        st.error("由于网络波动，翻译请求超时，请再试一次！")
