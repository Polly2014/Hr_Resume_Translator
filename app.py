#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历解析助手 - Web 界面
一键将简历转换为标准化 Excel 模板
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
from datetime import datetime
import json

# 导入核心模块
from resume_parser import extract_text_from_resume, parse_resume_with_llm
from resume_template_generator import ResumeTemplateGenerator

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="简历解析助手",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================== 自定义样式 ====================
st.markdown("""
<style>
    /* 主题色 */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --success-color: #48bb78;
        --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 页面背景 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    }
    
    /* 标题样式 */
    .main-title {
        text-align: center;
        padding: 2rem 0 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0;
    }
    
    .sub-title {
        text-align: center;
        color: #718096;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* 卡片样式 */
    .card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
    }
    
    /* 上传区域样式 */
    .upload-section {
        border: 2px dashed #cbd5e0;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #667eea;
        background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);
    }
    
    /* 进度条样式 */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 成功消息 */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #28a745;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* 统计卡片 */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        color: #718096;
        font-size: 0.9rem;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* 下载按钮特殊样式 */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4);
    }
    
    /* 文件上传器 */
    .stFileUploader > div > div {
        border-radius: 12px;
    }
    
    /* 信息框 */
    .info-box {
        background: linear-gradient(135deg, #e8f4fd 0%, #d1e9fc 100%);
        border-left: 4px solid #667eea;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    
    /* 步骤指示器 */
    .step-indicator {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        opacity: 0.5;
    }
    
    .step.active {
        opacity: 1;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .step-text {
        font-size: 0.85rem;
        color: #4a5568;
    }
    
    /* 解析结果预览 */
    .result-preview {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1rem;
        max-height: 300px;
        overflow-y: auto;
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 0.85rem;
    }
    
    /* 动画 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Emoji 图标放大 */
    .big-emoji {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 辅助函数 ====================
def get_template_path():
    """获取模板文件路径"""
    return Path(__file__).parent / "Templates" / "template.xlsx"


def process_resume(uploaded_file) -> tuple:
    """
    处理上传的简历文件
    
    Returns:
        (success, parsed_data, excel_bytes, error_message)
    """
    try:
        # 保存上传的文件到临时目录
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name
        
        # 步骤1: 提取文本
        resume_text = extract_text_from_resume(tmp_path)
        
        # 步骤2: AI 解析
        parsed_data = parse_resume_with_llm(resume_text)
        
        if "error" in parsed_data:
            return False, None, None, parsed_data["error"]
        
        # 步骤3: 生成 Excel
        template_path = get_template_path()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_excel:
            generator = ResumeTemplateGenerator(str(template_path))
            generator.generate(parsed_data, tmp_excel.name)
            
            # 读取生成的 Excel 文件
            with open(tmp_excel.name, "rb") as f:
                excel_bytes = f.read()
        
        # 清理临时文件
        os.unlink(tmp_path)
        os.unlink(tmp_excel.name)
        
        return True, parsed_data, excel_bytes, None
        
    except Exception as e:
        return False, None, None, str(e)


# ==================== 主界面 ====================
def main():
    # 标题
    st.markdown('<h1 class="main-title">📄 简历解析助手</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">智能解析简历，一键生成标准化 Excel 模板</p>', unsafe_allow_html=True)
    
    # 步骤指示器
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 2rem;">📤</div>
            <div style="color: #667eea; font-weight: 600;">1. 上传简历</div>
            <div style="color: #a0aec0; font-size: 0.85rem;">PDF / Word</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 2rem;">🤖</div>
            <div style="color: #667eea; font-weight: 600;">2. AI 解析</div>
            <div style="color: #a0aec0; font-size: 0.85rem;">智能提取信息</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 2rem;">📥</div>
            <div style="color: #667eea; font-weight: 600;">3. 下载模板</div>
            <div style="color: #a0aec0; font-size: 0.85rem;">Excel 格式</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 上传区域
    st.markdown("""
    <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "将简历拖拽到这里，或点击选择文件",
        type=["pdf", "docx"],
        help="支持 PDF 和 Word (.docx) 格式",
        label_visibility="collapsed"
    )
    
    # 上传提示
    if not uploaded_file:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #718096;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
            <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">将简历拖拽到这里</div>
            <div style="font-size: 0.9rem; color: #a0aec0;">或点击上方区域选择文件</div>
            <div style="font-size: 0.85rem; color: #a0aec0; margin-top: 1rem;">
                支持格式：PDF、Word (.docx)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 处理上传的文件
    if uploaded_file:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 显示文件信息
        file_size = len(uploaded_file.getbuffer()) / 1024  # KB
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #e8f4fd 0%, #d1e9fc 100%); 
                    border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1rem;">
            <span style="font-size: 1.2rem;">📎</span>
            <strong>{uploaded_file.name}</strong>
            <span style="color: #718096; margin-left: 1rem;">{file_size:.1f} KB</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 开始处理按钮
        if st.button("🚀 开始解析", use_container_width=True):
            
            # 进度显示
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 步骤1
            status_text.markdown("**⏳ 正在提取文本...**")
            progress_bar.progress(20)
            
            # 步骤2
            status_text.markdown("**🤖 AI 正在分析简历...**")
            progress_bar.progress(50)
            
            # 实际处理
            success, parsed_data, excel_bytes, error = process_resume(uploaded_file)
            
            # 步骤3
            status_text.markdown("**📝 正在生成 Excel 模板...**")
            progress_bar.progress(80)
            
            progress_bar.progress(100)
            
            if success:
                status_text.empty()
                progress_bar.empty()
                
                # 成功提示
                st.markdown("""
                <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); 
                            border-radius: 12px; padding: 1.5rem; text-align: center; margin: 1rem 0;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎉</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #155724;">解析完成！</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 解析结果统计
                st.markdown("<br>", unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                # 统计数据
                name = parsed_data.get("basic_info", {}).get("name", "未知")
                edu_count = len(parsed_data.get("education", []))
                work_count = len(parsed_data.get("work_experience", []))
                proj_count = len(parsed_data.get("project_experience", []))
                
                with col1:
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 1rem; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                        <div style="font-size: 1.5rem;">👤</div>
                        <div style="font-weight: 600; color: #4a5568;">{name}</div>
                        <div style="font-size: 0.8rem; color: #a0aec0;">姓名</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 1rem; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                        <div style="font-size: 1.5rem;">🎓</div>
                        <div style="font-weight: 600; color: #667eea;">{edu_count}</div>
                        <div style="font-size: 0.8rem; color: #a0aec0;">学历</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 1rem; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                        <div style="font-size: 1.5rem;">💼</div>
                        <div style="font-weight: 600; color: #667eea;">{work_count}</div>
                        <div style="font-size: 0.8rem; color: #a0aec0;">工作经历</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 1rem; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                        <div style="font-size: 1.5rem;">📂</div>
                        <div style="font-weight: 600; color: #667eea;">{proj_count}</div>
                        <div style="font-size: 0.8rem; color: #a0aec0;">项目经历</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # 下载按钮
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_stem = Path(uploaded_file.name).stem
                download_name = f"{file_stem}_filled_{timestamp}.xlsx"
                
                st.download_button(
                    label="📥 下载 Excel 模板",
                    data=excel_bytes,
                    file_name=download_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                # 查看详细信息（可折叠）
                with st.expander("🔍 查看解析详情"):
                    st.json(parsed_data)
                    
            else:
                status_text.empty()
                progress_bar.empty()
                
                st.error(f"❌ 解析失败: {error}")
                st.markdown("""
                <div style="background: #fff5f5; border-radius: 12px; padding: 1rem; margin-top: 1rem;">
                    <strong>可能的原因：</strong>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem; color: #718096;">
                        <li>简历格式不正确或已损坏</li>
                        <li>网络连接问题</li>
                        <li>AI 服务暂时不可用</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    # 页脚
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #a0aec0; font-size: 0.85rem; padding: 2rem 0;">
        Made with ❤️ for you
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
