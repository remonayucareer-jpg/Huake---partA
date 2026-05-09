import streamlit as st
import pandas as pd

# 设置页面配置
st.set_page_config(page_title="酒店周报数据分析", layout="wide")

# --- 终极微调 CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; }
    
    /* 标题区域样式 */
    .main-title { color: #0F172A; font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }
    .sub-title-date { color: #64748B; font-size: 1.1rem; font-weight: 500; margin-bottom: 0.2rem; }
    .sub-title-part { color: #1E293B; font-size: 1.2rem; font-weight: 700; border-left: 4px solid #2563EB; padding-left: 10px; margin-top: 10px; }

    /* 卡片容器对齐 */
    .stColumn { display: flex; flex-direction: column; gap: 12px; }

    .data-box {
        border: 1px solid #E2E8F0;
        padding: 1.5rem;
        border-radius: 8px;
        background-color: #FFFFFF;
        display: flex;
        flex-direction: column;
        justify-content: center; /* 垂直居中 */
        align-items: center;     /* 水平居中 */
        text-align: center;      /* 文字居中 */
        width: 100%;
        box-sizing: border-box;
    }
    
    .name-text { color: #1E293B; font-size: 1rem; font-weight: 700; margin-bottom: 4px; }
    .sub-text { color: #94A3B8; font-size: 0.8rem; line-height: 1.3; margin-bottom: 12px; min-height: 2.4rem; }
    .value-text { color: #2563EB; font-size: 2rem; font-weight: 800; }
    .rate-value { color: #059669; }

    /* 维持长宽高不变的高度参数 */
    .h-5 { min-height: 698px; }
    .h-3 { min-height: 414px; }
    .h-2 { min-height: 272px; }
    .h-1 { min-height: 130px; }
    
    .highlight-border { border: 2px solid #2563EB !important; background-color: #F8FAFC; }
    </style>
    """, unsafe_allow_html=True)

# --- 逻辑部分 (计算逻辑维持现状) ---
def run_analysis(df_cloud, df_ext):
    def clean_num(x):
        if pd.isna(x): return None
        return str(x).split('.')[0].strip()
    ext_cols = [col for col in df_ext.columns if '分机' in col]
    all_extensions = []
    for col in ext_cols: all_extensions.extend(df_ext[col].apply(clean_num).dropna().tolist())
    ext_set = set(all_extensions)
    df_cloud['主叫_清洗'] = df_cloud['主叫号码'].apply(clean_num)
    df_real = df_cloud[df_cloud['主叫_清洗'].isin(ext_set)].copy()
    
    idx1 = len(df_real)
    idx3 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '--')])
    idx4 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '接通')])
    idx5 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '未接通')])
    idx2 = idx3 + idx4 + idx5
    idx6 = idx2 / idx2 if idx2 > 0 else 0 
    idx7 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '接通')])
    idx8 = len(df_real[(df_real['通话状态'] == '未接通') & (df_real['AI通话状态'] == '--')])
    idx9 = idx7 + idx8
    num_10, den_10 = (idx4 + idx7), (idx4 + idx7 + idx5 + idx8)
    idx10 = num_10 / den_10 if den_10 > 0 else 0
    overall_rate = (idx3 + idx4 + idx7) / idx1 if idx1 > 0 else 0
    return locals()

# --- 标题区域重排 ---
st.markdown('<div class="main-title">酒店周报数据分析</div>', unsafe_allow_html=True)
date_input = st.sidebar.text_input("统计周期", "0430 - 0506")
st.markdown(f'<div class="sub-title-date">{date_input}</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title-part">PART1：酒店电话数据</div>', unsafe_allow_html=True)

# --- 数据上传与看板展示 ---
up_cloud = st.sidebar.file_uploader("1. 级联云原始数据", type=["xlsx"])
up_ext = st.sidebar.file_uploader("2. 分机号数据库", type=["xlsx"])

if up_cloud and up_ext:
    data = run_analysis(pd.read_excel(up_cloud), pd.read_excel(up_ext))
    cols = st.columns(5)

    # 第1列：总来电量 (居中对齐)
    with cols[0]:
        st.markdown(f'<div class="data-box h-5"><div class="name-text">总来电量</div><div class="sub-text">(所有启用AI的客房呼出量)</div><div class="value-text">{data["idx1"]}</div></div>', unsafe_allow_html=True)

    # 第2列：分流层 (居中对齐)
    with cols[1]:
        st.markdown(f'<div class="data-box h-3"><div class="name-text">进入AI接待流程电话量</div><div class="sub-text">进入AI语音环节总量</div><div class="value-text">{data["idx2"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-2"><div class="name-text">直接进入人工接待流程电话量</div><div class="sub-text">未触发AI直接转人工</div><div class="value-text">{data["idx9"]}</div></div>', unsafe_allow_html=True)

    # 第3列：行为细分 (原本就是1行，已经居中)
    with cols[2]:
        st.markdown(f'<div class="data-box h-1"><div class="name-text">AI接通量①</div><div class="sub-text">AI完成</div><div class="value-text">{data["idx3"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-1"><div class="name-text">AI接通量②</div><div class="sub-text">AI转人工接通</div><div class="value-text">{data["idx4"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-1"><div class="name-text">AI接通量③</div><div class="sub-text">AI转人工未接通</div><div class="value-text">{data["idx5"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-1"><div class="name-text">人工接通量④</div><div class="sub-text">直接转人工接通</div><div class="value-text">{data["idx7"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-1"><div class="name-text">人工未接通量⑤</div><div class="sub-text">直接转人工未接通</div><div class="value-text">{data["idx8"]}</div></div>', unsafe_allow_html=True)

    # 第4列：成功率层 (居中对齐)
    with cols[3]:
        st.markdown(f'<div class="data-box h-3"><div class="name-text">AI成功接通率</div><div class="sub-text">(①+②+③) / AI总量</div><div class="value-text rate-value">{data["idx6"]:.1%}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-2"><div class="name-text">人工成功接通率</div><div class="sub-text">人工环节接通占比</div><div class="value-text rate-value">{data["idx10"]:.1%}</div></div>', unsafe_allow_html=True)

    # 第5列：终极指标 (居中对齐)
    with cols[4]:
        st.markdown(f'<div class="data-box h-5 highlight-border"><div class="name-text" style="color: #2563EB;">整体电话成功接通率</div><div class="sub-text">全口径处理比例</div><div class="value-text" style="font-size: 2.2rem; color: #2563EB;">{data["overall_rate"]:.1%}</div></div>', unsafe_allow_html=True)

else:
    st.info("👋 欢迎回来！请在侧边栏上传本周数据。")
