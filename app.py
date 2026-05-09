import streamlit as st
import pandas as pd

# 设置页面配置
st.set_page_config(page_title="酒店AI+人工效能分析看板", layout="wide")

# --- 极简 CSS：核心在于控制卡片高度和对齐 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; }
    
    /* 容器对齐 */
    .stColumn { display: flex; flex-direction: column; gap: 12px; }

    .data-box {
        border: 1px solid #E2E8F0;
        padding: 1.2rem;
        border-radius: 8px;
        background-color: #FFFFFF;
        display: flex;
        flex-direction: column;
        justify-content: center;
        width: 100%;
        box-sizing: border-box;
    }
    
    .name-text { color: #1E293B; font-size: 0.95rem; font-weight: 700; margin-bottom: 2px; }
    .sub-text { color: #94A3B8; font-size: 0.75rem; line-height: 1.2; margin-bottom: 8px; }
    .value-text { color: #2563EB; font-size: 1.8rem; font-weight: 800; margin-top: auto; }
    .rate-value { color: #059669; }

    /* 高度控制：1行单位高度约130px (含间隔) */
    .h-5 { min-height: 698px; } /* 占5行 */
    .h-3 { min-height: 414px; } /* 占3行 */
    .h-2 { min-height: 272px; } /* 占2行 */
    .h-1 { min-height: 130px; } /* 占1行 */
    
    .highlight-border { border: 2px solid #2563EB !important; background-color: #F8FAFC; }
    </style>
    """, unsafe_allow_html=True)

# --- 逻辑部分 (保持不变) ---
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

# --- 布局部分 ---
st.title("酒店电话效能分析报告")

if up_cloud := st.sidebar.file_uploader("1. 级联云原始数据", type=["xlsx"]):
    if up_ext := st.sidebar.file_uploader("2. 分机号数据库", type=["xlsx"]):
        data = run_analysis(pd.read_excel(up_cloud), pd.read_excel(up_ext))
        
        # 使用 Streamlit Columns 分出 5 列
        cols = st.columns(5)

        # 第一列：总来电量 (跨5行)
        with cols[0]:
            st.markdown(f'<div class="data-box h-5"><div class="name-text">总来电量</div><div class="sub-text">(所有启用AI的客房呼出)</div><div class="value-text">{data["idx1"]}</div></div>', unsafe_allow_html=True)

        # 第二列：分流
        with cols[1]:
            st.markdown(f'<div class="data-box h-3"><div class="name-text">进入AI接待流程</div><div class="sub-text">AI语音环节总量</div><div class="value-text">{data["idx2"]}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-box h-2"><div class="name-text">直接进入人工接待</div><div class="sub-text">未触发AI，直接外呼转人工</div><div class="value-text">{data["idx9"]}</div></div>', unsafe_allow_html=True)

        # 第三列：细分 (1+1+1+1+1)
        with cols[2]:
            st.markdown(f'<div class="data-box h-1"><div class="name-text">AI接通量①</div><div class="sub-text">AI完成</div><div class="value-text">{data["idx3"]}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-box h-1"><div class="name-text">AI接通量②</div><div class="sub-text">AI转人工接通</div><div class="value-text">{data["idx4"]}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-box h-1"><div class="name-text">AI接通量③</div><div class="sub-text">AI转人工未接通</div><div class="value-text">{data["idx5"]}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-box h-1"><div class="name-text">人工接通量④</div><div class="sub-text">直接转人工接通</div><div class="value-text">{data["idx7"]}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-box h-1"><div class="name-text">人工未接通量⑤</div><div class="sub-text">直接转人工未接通</div><div class="value-text">{data["idx8"]}</div></div>', unsafe_allow_html=True)

        # 第四列：成功率
        with cols[3]:
            st.markdown(f'<div class="data-box h-3"><div class="name-text">AI成功接通率</div><div class="sub-text">(①+②+③) / AI总量</div><div class="value-text rate-value">{data["idx6"]:.1%}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-box h-2"><div class="name-text">人工成功接通率</div><div class="sub-text">人工环节综合占比</div><div class="value-text rate-value">{data["idx10"]:.1%}</div></div>', unsafe_allow_html=True)

        # 第五列：终极指标
        with cols[4]:
            st.markdown(f'<div class="data-box h-5 highlight-border"><div class="name-text" style="color: #2563EB;">整体电话成功率</div><div class="sub-text">全口径处理比例</div><div class="value-text" style="font-size: 2.2rem; color: #2563EB;">{data["overall_rate"]:.1%}</div></div>', unsafe_allow_html=True)

else:
    st.info("请在侧边栏上传数据。")
