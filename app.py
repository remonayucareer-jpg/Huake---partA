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
    .header-part { color: #1E293B; font-size: 1.3rem; font-weight: 700; margin-top: 12px; border-left: 4px solid #2563EB; padding-left: 12px; }

    /* 布局容器：缩小间距以对齐高度 */
    .stColumn { display: flex; flex-direction: column; gap: 8px !important; } /* 间距由12px调为8px */

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
    
    .name-text { color: #1E293B; font-size: 0.9rem; font-weight: 700; margin-bottom: 4px; }
    .sub-text { color: #94A3B8; font-size: 0.75rem; line-height: 1.2; margin-bottom: 8px; }
    .value-text { color: #2563EB; font-size: 1.8rem; font-weight: 800; }
    .rate-value { color: #059669; }

    /* 高度精准微调：确保 (5个h-1 + 4个gap) = h-5 */
    .h-5 { min-height: 672px; } /* 总高保持稳定 */
    .h-3 { min-height: 400px; }
    .h-2 { min-height: 264px; }
    .h-1 { min-height: 128px; } /* 稍微缩减了2px以抵消间距影响 */
    
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

# --- 侧边栏 ---
with st.sidebar:
    st.title("数据配置")
    up_cloud = st.file_uploader("1. 级联云原始数据", type=["xlsx"])
    up_ext = st.file_uploader("2. 分机号数据库", type=["xlsx"])
    date_val = st.text_input("统计日期", "2024.04.30 - 2024.05.06")

# --- 顶栏渲染 ---
st.markdown(f"""
    <div class="header-container">
        <div class="header-title">酒店周报数据分析</div>
        <div class="header-date">{date_val}</div>
        <div class="header-part">PART 1：酒店电话数据</div>
    </div>
    """, unsafe_allow_html=True)

# --- 布局核心 ---
if up_cloud and up_ext:
    data = run_analysis(pd.read_excel(up_cloud), pd.read_excel(up_ext))
    cols = st.columns(5)

    with cols[0]:
        st.markdown(f'<div class="data-box h-5"><div class="name-text">总来电量</div><div class="sub-text">(所有启用AI的客房呼出量)</div><div class="value-text">{data["idx1"]}</div></div>', unsafe_allow_html=True)

    with cols[1]:
        st.markdown(f'<div class="data-box h-3"><div class="name-text">进入AI接待流程电话量</div><div class="sub-text">AI语音环节总量</div><div class="value-text">{data["idx2"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-2"><div class="name-text">直接进入人工接待</div><div class="sub-text">未触发AI直接外呼</div><div class="value-text">{data["idx9"]}</div></div>', unsafe_allow_html=True)

    with cols[2]:
        # 第三列：5个小格子，确保高度与 h-5 严格相等
        st.markdown(f'<div class="data-box h-1"><div class="name-text">AI接通量①</div><div class="sub-text">AI完成</div><div class="value-text">{data["idx3"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-1"><div class="name-text">AI接通量②</div><div class="sub-text">转人工接通</div><div class="value-text">{data["idx4"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-1"><div class="name-text">AI接通量③</div><div class="sub-text">转人工未接通</div><div class="value-text">{data["idx5"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-1"><div class="name-text">人工接通量④</div><div class="sub-text">直接人工接通</div><div class="value-text">{data["idx7"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-1"><div class="name-text">人工未接通量⑤</div><div class="sub-text">直接人工未接通</div><div class="value-text">{data["idx8"]}</div></div>', unsafe_allow_html=True)

    with cols[3]:
        st.markdown(f'<div class="data-box h-3"><div class="name-text">AI成功接通率</div><div class="sub-text">(①+②+③) / AI总量</div><div class="value-text rate-value">{data["idx6"]:.1%}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-box h-2"><div class="name-text">人工成功接通率</div><div class="sub-text">人工环节占比</div><div class="value-text rate-value">{data["idx10"]:.1%}</div></div>', unsafe_allow_html=True)

    with cols[4]:
        st.markdown(f'<div class="data-box h-5 highlight-border"><div class="name-text" style="color: #2563EB;">整体电话成功接通率</div><div class="sub-text">全口径成功比例</div><div class="value-text" style="font-size: 2.2rem; color: #2563EB;">{data["overall_rate"]:.1%}</div></div>', unsafe_allow_html=True)

else:
    st.info("👋 请上传 Excel 文件开始分析。")
