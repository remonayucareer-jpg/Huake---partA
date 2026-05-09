import streamlit as st
import pandas as pd

# 设置页面配置
st.set_page_config(page_title="酒店电话数据分析工具 v2.0", layout="wide")

# --- 自定义 CSS 样式（深度还原图片设计） ---
st.markdown("""
    <style>
    .main-title { color: #0070C0; font-size: 26px; font-weight: bold; margin-bottom: 5px; }
    .date-label { color: #0070C0; font-size: 18px; margin-bottom: 20px; }
    .stats-table { width: 100%; border-collapse: collapse; text-align: center; font-family: "Microsoft YaHei", sans-serif; }
    .stats-table th, .stats-table td { border: 2px solid #BFBFBF; padding: 12px; }
    .bg-yellow { background-color: #FFFF00; font-weight: bold; }
    .bg-light-yellow { background-color: #FFF2CC; }
    .header-text { font-size: 16px; color: #000; font-weight: bold; }
    .value-text { font-size: 22px; font-weight: bold; margin-top: 8px; }
    .sub-text { font-size: 11px; color: #595959; font-weight: normal; margin-top: 4px; }
    .highlight-red { color: red; }
    </style>
    """, unsafe_allow_html=True)

# --- 侧边栏：文件上传 ---
st.sidebar.header("📁 数据上传区")
uploaded_cloud = st.sidebar.file_uploader("1. 上传级联云原始数据 (Excel)", type=["xlsx"])
uploaded_ext = st.sidebar.file_uploader("2. 上传分机号数据 (Excel)", type=["xlsx"])
date_range = st.sidebar.text_input("数据周期", "0430-0506")

# --- 核心计算引擎 ---
def run_analysis(df_cloud, df_ext):
    def clean_num(x):
        if pd.isna(x): return None
        return str(x).split('.')[0].strip()

    # 1. 构建分机号池（支持多列）
    ext_cols = [col for col in df_ext.columns if '分机' in col]
    all_extensions = []
    for col in ext_cols:
        all_extensions.extend(df_ext[col].apply(clean_num).dropna().tolist())
    ext_set = set(all_extensions)

    # 2. 筛选真实数据
    df_cloud['主叫_清洗'] = df_cloud['主叫号码'].apply(clean_num)
    df_real = df_cloud[df_cloud['主叫_清洗'].isin(ext_set)].copy()

    # --- 指标计算逻辑 ---
    # 指标 1: 总来电量
    idx1 = len(df_real)

    # AI 环节
    idx3 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '--')])
    idx4 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '接通')])
    idx5 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '未接通')])
    
    idx2 = idx3 + idx4 + idx5 # 进入AI量
    idx_ai_ans = idx3 + idx4 + idx5 # AI接通量
    idx6 = idx_ai_ans / idx2 if idx2 > 0 else 0

    # 人工环节
    idx7 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '接通')])
    
    # 修正后的指标 8 (数据1 + 数据2)
    d1_8 = len(df_real[(df_real['通话状态'] == '未接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '--')])
    d2_8 = len(df_real[(df_real['通话状态'] == '未接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '未接通')])
    idx8 = d1_8 + d2_8

    idx9 = idx7 + idx8 # 直接进入人工量
    
    # 指标 10 (最终人工成功接通率)
    num_10 = idx4 + idx7
    den_10 = idx4 + idx7 + idx5 + idx8
    idx10 = num_10 / den_10 if den_10 > 0 else 0

    # 整体接通率 (AI解决 + 人工接通) / 总来电
    idx_overall = (idx3 + idx4 + idx7) / idx1 if idx1 > 0 else 0

    return {
        "idx1": idx1, "idx2": idx2, "idx3": idx3, "idx4": idx4, "idx5": idx5,
        "idx_ai_ans": idx_ai_ans, "idx6": idx6, "idx7": idx7, "idx8": idx8,
        "idx9": idx9, "idx10": idx10, "idx_overall": idx_overall,
        "human_den": den_10, "human_num": num_10
    }

# --- 页面展示逻辑 ---
st.markdown(f'<div class="date-label">数据周期：{date_range}</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">PART1：酒店电话数据分析看板</div>', unsafe_allow_html=True)

if uploaded_cloud and uploaded_ext:
    with st.spinner('正在处理深度数据...'):
        res = run_analysis(pd.read_excel(uploaded_cloud), pd.read_excel(uploaded_ext))

    # 构建 HTML 表格看板
    html_board = f"""
    <table class="stats-table">
        <tr>
            <td colspan="3" class="bg-yellow">
                <div class="header-text">总来电量</div>
                <div class="sub-text">(所有启用AI的客房呼出的电话量)</div>
                <div class="value-text">{res['idx1']}</div>
            </td>
            <td rowspan="2" class="bg-light-yellow">
                <div class="header-text">整体电话接通率</div>
                <div class="sub-text">(切换AI后)</div>
                <div style="font-size: 32px; color: #000; font-weight: bold; margin-top:25px;">{res['idx_overall']:.1%}</div>
            </td>
        </tr>
        <tr>
            <td class="bg-light-yellow">
                <div class="header-text">进入AI电话量</div>
                <div class="sub-text">(指标 2)</div>
                <div class="value-text">{res['idx2']}</div>
            </td>
            <td class="bg-light-yellow">
                <div class="header-text">AI接通量</div>
                <div class="sub-text">(指标 3+4+5)</div>
                <div class="value-text highlight-red">{res['idx_ai_ans']}</div>
            </td>
            <td class="bg-light-yellow">
                <div class="header-text">AI接通率</div>
                <div class="sub-text">(AI接通量 / 进入AI电话量)</div>
                <div class="value-text">{res['idx6']:.1%}</div>
            </td>
        </tr>
        <tr>
            <td class="bg-light-yellow">
                <div class="header-text">进入人工电话量</div>
                <div class="sub-text">(计算分母: 4+7+5+8)</div>
                <div class="value-text">{res['human_den']}</div>
            </td>
            <td class="bg-light-yellow">
                <div class="header-text">人工接通量</div>
                <div class="sub-text">(计算分子: 4+7)</div>
                <div class="value-text">{res['human_num']}</div>
            </td>
            <td class="bg-light-yellow">
                <div class="header-text">人工接通率</div>
                <div class="sub-text">(最终指标 10)</div>
                <div class="value-text">{res['idx10']:.1%}</div>
            </td>
            <td class="bg-yellow" style="font-size: 28px; font-weight: bold;">
                {res['idx_overall']:.1%}
            </td>
        </tr>
    </table>
    """
    st.markdown(html_board, unsafe_allow_html=True)
    st.info("💡 提示：该结果已自动剔除无效拨打，并支持多分机号匹配。")
else:
    st.warning("👈 请在侧边栏上传相应的 Excel 文件以生成看板。")
