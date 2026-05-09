import streamlit as st
import pandas as pd

# 设置页面配置
st.set_page_config(page_title="酒店AI+人工效能分析看板", layout="wide")

# --- 高级 CSS：简约干净的表格风格 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; }
    
    /* 标题样式 */
    .header-container { padding: 1rem 0; border-bottom: 2px solid #F1F5F9; margin-bottom: 1.5rem; }
    .header-title { color: #0F172A; font-size: 1.8rem; font-weight: 700; }
    .header-subtitle { color: #64748B; font-size: 0.9rem; margin-top: 4px; }

    /* 模块标题 */
    .part-title { font-size: 1.2rem; font-weight: 700; color: #1E293B; padding: 1rem 0; border-top: 1px solid #F1F5F9; }

    /* 数据展示卡片：简约表格感 */
    .data-box {
        border: 1px solid #E2E8F0;
        padding: 1rem;
        border-radius: 4px;
        background-color: #F8FAFC;
        height: 100%;
    }
    .metric-name { color: #475569; font-size: 0.85rem; font-weight: 600; }
    .metric-value { color: #0F172A; font-size: 1.5rem; font-weight: 700; margin: 0.3rem 0; }
    .metric-sub { color: #94A3B8; font-size: 0.75rem; line-height: 1.2; }

    /* 成功率高亮 */
    .rate-highlight { color: #2563EB; font-size: 1.8rem; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- 核心计算函数 (逻辑保持不变) ---
def run_analysis(df_cloud, df_ext):
    def clean_num(x):
        if pd.isna(x): return None
        return str(x).split('.')[0].strip()

    ext_cols = [col for col in df_ext.columns if '分机' in col]
    all_extensions = []
    for col in ext_cols:
        all_extensions.extend(df_ext[col].apply(clean_num).dropna().tolist())
    ext_set = set(all_extensions)

    df_cloud['主叫_清洗'] = df_cloud['主叫号码'].apply(clean_num)
    df_real = df_cloud[df_cloud['主叫_清洗'].isin(ext_set)].copy()

    idx1 = len(df_real)
    idx3 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '--')])
    idx4 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '接通')])
    idx5 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '未接通')])
    idx2 = idx3 + idx4 + idx5
    idx6 = idx2 / idx2 if idx2 > 0 else 0 # 对应你提到的计算逻辑：(1+2+3)/2

    # 人工环节
    idx7 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '接通')])
    d1_8 = len(df_real[(df_real['通话状态'] == '未接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '--')])
    d2_8 = len(df_real[(df_real['通话状态'] == '未接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '未接通')])
    idx8 = d1_8 + d2_8
    idx9 = idx7 + idx8
    
    num_10 = idx4 + idx7
    den_10 = idx4 + idx7 + idx5 + idx8
    idx10 = num_10 / den_10 if den_10 > 0 else 0

    return locals()

# --- 界面展示 ---

# 1. 侧边栏 (仅保留文件上传)
with st.sidebar:
    st.title("控制台")
    up_cloud = st.file_uploader("1. 级联云原始数据", type=["xlsx"])
    up_ext = st.file_uploader("2. 分机号数据库", type=["xlsx"])
    st.divider()
    st.caption("内部自用校验版 v4.0")

# 2. 顶部标题 (保留原设计的专业感)
st.markdown("""
    <div class="header-container">
        <div class="header-title">酒店电话效能全口径分析</div>
        <div class="header-subtitle">数据报告周期：0430 - 0506  |  状态：实时分析中</div>
    </div>
    """, unsafe_allow_html=True)

if up_cloud and up_ext:
    data = run_analysis(pd.read_excel(up_cloud), pd.read_excel(up_ext))
    
    # --- 第一部分：给我自己看的部分 (PART 1) ---
    st.markdown('<div class="part-title">PART 1：酒店电话数据 (内部校验)</div>', unsafe_allow_html=True)

    # 布局 A：AI 环节指标呈现 (使用权重模拟面积配比)
    # 指标1(1) : 指标2(1/2) : 指标3/4/5(1/6各一份) : 指标6(1/2)
    # 转换为列权重比例：6 : 3 : 1 : 1 : 1 : 3
    c1, c2, c3, c4, c5, c6 = st.columns([6, 3, 1, 1, 1, 3])

    with c1:
        st.markdown(f'<div class="data-box"><div class="metric-name">指标 1：总来电量</div><div class="metric-value">{data["idx1"]}</div><div class="metric-sub">(所有启用AI的客房呼出电话量)</div></div>', unsafe_allow_html=True)
    
    with c2:
        st.markdown(f'<div class="data-box"><div class="metric-name">指标 2：进入AI接待流程</div><div class="metric-value">{data["idx2"]}</div><div class="metric-sub">进入AI环节的总量</div></div>', unsafe_allow_html=True)

    with c3:
        st.markdown(f'<div class="data-box"><div class="metric-name">指标 3：AI接通量①</div><div class="metric-value">{data["idx3"]}</div><div class="metric-sub">(AI接通，AI完成，未转人工)</div></div>', unsafe_allow_html=True)

    with c4:
        st.markdown(f'<div class="data-box"><div class="metric-name">指标 4：AI接通量②</div><div class="metric-value">{data["idx4"]}</div><div class="metric-sub">(AI接通，转接人工，人工接通)</div></div>', unsafe_allow_html=True)

    with c5:
        st.markdown(f'<div class="data-box"><div class="metric-name">指标 5：AI接通量③</div><div class="metric-value">{data["idx5"]}</div><div class="metric-sub">(AI接通，转接人工，人工未接通)</div></div>', unsafe_allow_html=True)

    with c6:
        st.markdown(f'<div class="data-box"><div class="metric-name">指标 6：AI成功接通率</div><div class="metric-value rate-highlight">{data["idx6"]:.1%}</div><div class="metric-sub">(①+②+③/指标2)</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 布局 B：人工环节指标呈现
    # 这里我们延续简约的比例，重点突出指标 10
    h1, h2, h3, h4 = st.columns([1, 1, 1, 1.5])
    
    with h1:
        st.markdown(f'<div class="data-box"><div class="metric-name">指标 7：人工接通④</div><div class="metric-value">{data["idx7"]}</div><div class="metric-sub">(直接转接人工，人工接通)</div></div>', unsafe_allow_html=True)
    
    with h2:
        st.markdown(f'<div class="data-box"><div class="metric-name">指标 8：人工未接通量⑤</div><div class="metric-value">{data["idx8"]}</div><div class="metric-sub">(直接进人工，人工未接通或客户放弃量)</div></div>', unsafe_allow_html=True)

    with h3:
        st.markdown(f'<div class="data-box"><div class="metric-name">指标 9：直接进入人工流程</div><div class="metric-value">{data["idx9"]}</div><div class="metric-sub">不经过AI，直接转人工总量</div></div>', unsafe_allow_html=True)

    with h4:
        st.markdown(f'<div class="data-box"><div class="metric-name">指标 10：人工成功接通率</div><div class="metric-value rate-highlight">{data["idx10"]:.1%}</div><div class="metric-sub">(最终对外展示核心指标)</div></div>', unsafe_allow_html=True)

    # 底部校验详情
    with st.expander("📝 内部数据校验日志"):
        st.write(f"指标 8 详情：[未接通/--/--]: {data['d1_8']} | [未接通/--/未接通]: {data['d2_8']}")
        st.write(f"人工分母校验 (4+7+5+8): {data['den_10']}")

else:
    st.info("👋 请在左侧上传 Excel 数据开始分析。")
