import streamlit as st
import pandas as pd
import numpy as np

# 设置页面配置
st.set_page_config(page_title="酒店电话数据分析工具", layout="wide")

# --- 自定义 CSS 样式（模仿图片中的 Excel 设计） ---
st.markdown("""
    <style>
    .main-title {
        color: #0070C0;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .date-label {
        color: #0070C0;
        font-size: 18px;
        margin-bottom: 20px;
    }
    .stats-table {
        width: 100%;
        border-collapse: collapse;
        text-align: center;
        font-family: "Microsoft YaHei", sans-serif;
    }
    .stats-table th, .stats-table td {
        border: 2px solid #BFBFBF;
        padding: 10px;
    }
    .bg-yellow { background-color: #FFFF00; font-weight: bold; }
    .bg-light-yellow { background-color: #FFF2CC; }
    .header-text { font-size: 16px; color: #000; }
    .value-text { font-size: 20px; font-weight: bold; }
    .sub-text { font-size: 12px; color: #595959; font-weight: normal; }
    </style>
    """, unsafe_allow_html=True)

# --- 侧边栏：文件上传 ---
st.sidebar.header("📁 上传数据文件")
uploaded_cloud = st.sidebar.file_uploader("1. 上传级联云原始数据 (Excel)", type=["xlsx"])
uploaded_ext = st.sidebar.file_uploader("2. 上传分机号数据 (Excel)", type=["xlsx"])
date_range = st.sidebar.text_input("数据周期 (例如: 0430-0506)", "0430-0506")

# --- 核心计算逻辑 ---
def calculate_metrics(df_cloud, df_ext):
    # 清洗函数
    def clean_num(x):
        if pd.isna(x): return None
        return str(x).split('.')[0].strip()

    # 处理分机号池
    ext_cols = [col for col in df_ext.columns if '分机' in col]
    all_extensions = []
    for col in ext_cols:
        all_extensions.extend(df_ext[col].apply(clean_num).dropna().tolist())
    ext_set = set(all_extensions)

    # 筛选真实数据
    df_cloud['主叫_清洗'] = df_cloud['主叫号码'].apply(clean_num)
    df_real = df_cloud[df_cloud['主叫_清洗'].isin(ext_set)].copy()

    # 指标计算
    idx1 = len(df_real) # 总来电量
    
    # AI 环节
    idx3 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '--')])
    idx4 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '接通')])
    idx5 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '未接通')])
    idx2 = idx3 + idx4 + idx5 # 进入AI量
    idx_ai_answered = idx3 + idx4 + idx5 # AI接通量
    idx6 = idx_ai_answered / idx2 if idx2 > 0 else 0 # AI接通率

    # 人工环节
    idx7 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '接通')])
    idx8 = len(df_real[(df_real['通话状态'] == '未接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '未接通')])
    
    # 按照图片逻辑：进入人工量 = 4+7+5+8
    idx9_human_total = idx4 + idx7 + idx5 + idx8 
    # 人工接通量 = 4+7
    idx_human_answered = idx4 + idx7
    idx10 = idx_human_answered / idx9_human_total if idx9_human_total > 0 else 0 # 人工接通率

    # 整体接通率 (AI解决 + 人工接通) / 总来电
    idx_overall = (idx3 + idx4 + idx7) / idx1 if idx1 > 0 else 0

    return {
        "idx1": idx1, "idx2": idx2, "idx_ai_ans": idx_ai_answered, "idx6": idx6,
        "idx9": idx9_human_total, "idx_hum_ans": idx_human_answered, "idx10": idx10,
        "idx_overall": idx_overall
    }

# --- 页面呈现 ---
st.markdown(f'<div class="date-label">数据周期: {date_range}</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">PART1：酒店电话数据</div>', unsafe_allow_html=True)

if uploaded_cloud and uploaded_ext:
    # 加载并计算
    df_cloud = pd.read_excel(uploaded_cloud)
    df_ext = pd.read_excel(uploaded_ext)
    res = calculate_metrics(df_cloud, df_ext)

    # --- 渲染模仿图片的 HTML 表格 ---
    html_table = f"""
    <table class="stats-table">
        <tr>
            <td colspan="3" class="bg-yellow">
                <div class="header-text">总来电量</div>
                <div class="sub-text">(所有启用AI的客房呼出的电话量)</div>
                <div class="value-text">{res['idx1']}</div>
            </td>
            <td rowspan="2" class="bg-light-yellow">
                <div class="header-text">整体电话接通率</div>
                <div class="header-text">(切换AI后)</div>
                <div style="font-size: 28px; color: #000; font-weight: bold; margin-top:20px;">{res['idx_overall']:.1%}</div>
            </td>
        </tr>
        <tr>
            <td class="bg-light-yellow">
                <div class="header-text">进入AI电话量</div>
                <div class="value-text" style="margin-top:15px;">{res['idx2']}</div>
            </td>
            <td class="bg-light-yellow">
                <div class="header-text">AI接通量</div>
                <div class="value-text" style="margin-top:15px; color: red;">{res['idx_ai_ans']}</div>
            </td>
            <td class="bg-light-yellow">
                <div class="header-text">AI接通率</div>
                <div class="sub-text">(AI接通量/进入AI电话量)</div>
                <div class="value-text" style="margin-top:5px;">{res['idx6']:.1%}</div>
            </td>
        </tr>
        <tr>
            <td class="bg-light-yellow">
                <div class="header-text">进入人工电话量</div>
                <div class="value-text" style="margin-top:15px;">{res['idx9']}</div>
            </td>
            <td class="bg-light-yellow">
                <div class="header-text">人工接通量</div>
                <div class="value-text" style="margin-top:15px;">{res['idx_hum_ans']}</div>
            </td>
            <td class="bg-light-yellow">
                <div class="header-text">人工接通率</div>
                <div class="sub-text">(人工接通量/进入人工电话量)</div>
                <div class="value-text" style="margin-top:5px;">{res['idx10']:.1%}</div>
            </td>
            <td class="bg-yellow" style="font-size: 24px;">
                {res['idx_overall']:.1%}
            </td>
        </tr>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)
    
    st.success("✅ 数据分析完成！您可以截屏保存上方的看板。")

else:
    st.info("👋 请在左侧上传对应的 Excel 文件开始分析。")
    # 预展示一个空表格结构（可选）
