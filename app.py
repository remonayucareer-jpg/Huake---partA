import streamlit as st
import pandas as pd

# 设置页面配置
st.set_page_config(page_title="酒店周报数据分析", layout="wide")

# --- 样式极致对齐版 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; }
    
    /* 标题区域 */
    .header-container { padding: 1.5rem 0; border-bottom: 2px solid #E2E8F0; margin-bottom: 1.5rem; }
    .header-title { color: #0F172A; font-size: 2.2rem; font-weight: 800; }
    .header-date { color: #64748B; font-size: 1.1rem; margin-top: 8px; font-weight: 500; }
    
    /* 栏目分隔标题 */
    .header-part { color: #1E293B; font-size: 1.3rem; font-weight: 700; margin: 20px 0 12px 0; border-left: 4px solid #2563EB; padding-left: 12px; }

    .stColumn { display: flex; flex-direction: column; gap: 8px !important; }

    .data-box {
        border: 1px solid #E2E8F0;
        padding: 1rem;
        border-radius: 8px;
        background-color: #FFFFFF;
        display: flex;
        flex-direction: column;
        justify-content: center; 
        align-items: center;     
        text-align: center;      
        width: 100%;
        box-sizing: border-box;
    }
    
    /* 颜色统一调整为 #1E293B */
    .name-text { color: #1E293B; font-size: 0.9rem; font-weight: 700; margin-bottom: 4px; }
    .sub-text { color: #94A3B8; font-size: 0.75rem; line-height: 1.2; margin-bottom: 8px; }
    .value-text { color: #1E293B; font-size: 1.8rem; font-weight: 800; }
    
    /* 高度定义 */
    .h-summary { min-height: 120px; } /* 第二部分汇总卡片的高度 */
    .h-5 { min-height: 672px; }
    .h-3 { min-height: 400px; }
    .h-2 { min-height: 264px; }
    .h-1 { min-height: 128px; }
    
    .highlight-border { border: 2px solid #2563EB !important; background-color: #F8FAFC; }
    </style>
    """, unsafe_allow_html=True)

# --- 逻辑处理 ---
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
    
    # 基础指标计算
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

    # --- 新增：第二部分汇总指标计算 ---
    part2_total_call = idx1
    part2_ai_call = idx2
    part2_ai_connect = idx3 + idx4 + idx5
    part2_ai_rate = part2_ai_connect / part2_ai_call if part2_ai_call > 0 else 0
    part2_human_call = idx4 + idx5 + idx7 + idx8
    part2_human_connect = idx4 + idx7
    part2_human_rate = idx10 # 直接复用原人工接通率逻辑

    return locals()

# --- 侧边栏 ---
with st.sidebar:
    st.title("数据配置")
    up_cloud = st.file_uploader("1. 级联云原始数据", type=["xlsx"])
    up_ext = st.file_uploader("2. 分机号数据库", type=["xlsx"])
    date_val = st.text_input("统计日期", "2024.04.30 - 2024.05.06")

# --- 顶栏 ---
st.markdown(f"""
    <div class="header-container">
        <div class="header-title">酒店周报数据分析</div>
        <div class="header-date">{date_val}</div>
    </div>
    """, unsafe_allow_html=True)

if up_cloud and up_ext:
    data = run_analysis(pd.read_excel(up_cloud), pd.read_excel(up_ext))

    # --- PART 2: 汇总数据展示 (置于上方) ---
    st.markdown('<div class="header-part">PART 2：核心指标概览</div>', unsafe_allow_html=True)
    p2_cols = st.columns(7) # 7个数据指标
    
    p2_metrics = [
        ("总来电量", data["part2_total_call"], ""),
        ("进入AI电话量", data["part2_ai_call"], ""),
        ("AI接通量", data["part2_ai_connect"], ""),
        ("AI接通率", f"{data['part2_ai_rate']:.1%}", ""),
        ("进入人工电话量", data["part2_human_call"], ""),
        ("人工接通量", data["part2_human_connect"], ""),
        ("人工接通率", f"{data['part2_human_rate']:.1%}", "")
    ]

    for i, (name, val, sub) in enumerate(p2_metrics):
        with p2_cols[i]:
            st.markdown(f"""
                <div class="data-box h-summary">
                    <div class="name-text">{name}</div>
                    <div class="value-text" style="font-size: 1.5rem;">{val}</div>
                </div>
            """, unsafe_allow_html=True)

    # --- PART 1: 酒店电话数据细节 (置于下方) ---
    st.markdown('<div class="header-part">PART 1：流程明细数据</div>', unsafe_allow_html=True)
    cols = st.columns(5)

    with cols[0]:
        st.markdown(f'<div class="data-box h-5"><div class="name-text">总来电量</div><div class="sub-text">(所有启用AI的客房呼出量)</div><div class="value-text">{data["idx1"]}</div></div>', unsafe_allow_html=True)

    with cols[1]:
        st.markdown(f'<div class="data-box h-3"><div class="name-text">进入AI接待流程电话量</div><div class="sub-text">AI语音环节总量</div><div class="value-text">{data["idx2"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-2"><div class="name-text">直接进入人工接待</div><div class="sub-text">未触发AI直接外呼</div><div class="value-text">{data["idx9"]}</div></div>', unsafe_allow_html=True)

    with cols[2]:
        st.markdown(f'<div class="data-box h-1"><div class="name-text">AI接通量①</div><div class="sub-text">AI完成</div><div class="value-text">{data["idx3"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-1"><div class="name-text">AI接通量②</div><div class="sub-text">转人工接通</div><div class="value-text">{data["idx4"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-1"><div class="name-text">AI接通量③</div><div class="sub-text">转人工未接通</div><div class="value-text">{data["idx5"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-1"><div class="name-text">人工接通量④</div><div class="sub-text">直接人工接通</div><div class="value-text">{data["idx7"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-1"><div class="name-text">人工未接通量⑤</div><div class="sub-text">直接人工未接通</div><div class="value-text">{data["idx8"]}</div></div>', unsafe_allow_html=True)

    with cols[3]:
        st.markdown(f'<div class="data-box h-3"><div class="name-text">AI成功接通率</div><div class="sub-text">(①+②+③) / AI总量</div><div class="value-text">{data["idx6"]:.1%}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-2"><div class="name-text">人工成功接通率</div><div class="sub-text">人工环节占比</div><div class="value-text">{data["idx10"]:.1%}</div></div>', unsafe_allow_html=True)

    with cols[4]:
        st.markdown(f'<div class="data-box h-5 highlight-border"><div class="name-text">整体电话成功接通率</div><div class="sub-text">全口径成功比例</div><div class="value-text" style="font-size: 2.2rem;">{data["overall_rate"]:.1%}</div></div>', unsafe_allow_html=True)

else:
    st.info("👋 请上传 Excel 文件开始分析。")
