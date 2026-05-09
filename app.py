import streamlit as st
import pandas as pd

# 设置页面配置 - 使用宽屏模式和深色/浅色自适应主题
st.set_page_config(page_title="酒店AI+人工效能分析看板", layout="wide")

# --- 高级 CSS 注入：打造顾问级审美 ---
st.markdown("""
    <style>
    /* 引入现代字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC; /* 浅淡的底色 */
    }

    /* 顶部标题栏 */
    .header-container {
        padding: 1.5rem 0;
        border-bottom: 2px solid #E2E8F0;
        margin-bottom: 2rem;
    }
    .header-title {
        color: #0F172A;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        color: #64748B;
        font-size: 1rem;
    }

    /* 核心指标卡片 */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #F1F5F9;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-label {
        color: #64748B;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #0F172A;
        font-size: 2.25rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .metric-footer {
        font-size: 0.8rem;
        color: #94A3B8;
    }

    /* 区域划分容器 */
    .section-box {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid #E2E8F0;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-title::before {
        content: '';
        width: 4px;
        height: 20px;
        background: #3B82F6;
        border-radius: 2px;
    }

    /* 环状图与成功率卡片 */
    .rate-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
    }
    .rate-value {
        font-size: 3rem;
        font-weight: 700;
        color: #38BDF8;
    }
    </style>
    """, unsafe_allow_html=True)

def run_analysis(df_cloud, df_ext):
    def clean_num(x):
        if pd.isna(x): return None
        return str(x).split('.')[0].strip()

    # 1. 匹配多分机号池
    ext_cols = [col for col in df_ext.columns if '分机' in col]
    all_extensions = []
    for col in ext_cols:
        all_extensions.extend(df_ext[col].apply(clean_num).dropna().tolist())
    ext_set = set(all_extensions)

    # 2. 筛选真实数据
    df_cloud['主叫_清洗'] = df_cloud['主叫号码'].apply(clean_num)
    df_real = df_cloud[df_cloud['主叫_清洗'].isin(ext_set)].copy()

    # --- 核心指标计算 ---
    idx1 = len(df_real)
    
    # AI 环节
    idx3 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '--')])
    idx4 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '接通')])
    idx5 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '未接通')])
    idx2 = idx3 + idx4 + idx5
    idx6 = idx2 / idx2 if idx2 > 0 else 0 # 注意：这里根据你之前的定义，AI接通率通常是100%，除非有特殊定义

    # 人工环节
    idx7 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '接通')])
    d1_8 = len(df_real[(df_real['通话状态'] == '未接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '--')])
    d2_8 = len(df_real[(df_real['通话状态'] == '未接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '未接通')])
    idx8 = d1_8 + d2_8
    idx9 = idx7 + idx8

    # 指标 10 相关
    num_10 = idx4 + idx7
    den_10 = idx4 + idx7 + idx5 + idx8
    idx10 = num_10 / den_10 if den_10 > 0 else 0

    # 整体效率
    overall_rate = (idx3 + idx4 + idx7) / idx1 if idx1 > 0 else 0

    # --- 显式封装字典 (解决 KeyError 的关键) ---
    results = {
        "idx1": idx1,
        "idx2": idx2,
        "idx3": idx3,
        "idx4": idx4,
        "idx5": idx5,
        "idx6": idx6,
        "idx7": idx7,
        "idx8": idx8,
        "idx9": idx9,
        "idx10": idx10,
        "d1_8": d1_8,
        "d2_8": d2_8,
        "human_num": num_10,
        "human_den": den_10,
        "overall_rate": overall_rate
    }
    return results

# --- UI 渲染层 ---
# 侧边栏
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3208/3208726.png", width=80)
    st.title("控制台")
    up_cloud = st.file_uploader("1. 级联云原始数据", type=["xlsx"])
    up_ext = st.file_uploader("2. 分机号数据库", type=["xlsx"])
    date_str = st.text_input("分析周期", "0430 - 0506")
    st.divider()
    st.caption("Remona Hotel Analytics Project v3.0")

# 主页面
st.markdown(f"""
    <div class="header-container">
        <div class="header-title">酒店电话效能全口径分析</div>
        <div class="header-subtitle">数据报告周期：{date_str}  |  状态：实时分析中</div>
    </div>
    """, unsafe_allow_html=True)

if up_cloud and up_ext:
    data = run_analysis(pd.read_excel(up_cloud), pd.read_excel(up_ext))
    
    # 第一行：顶层核心汇总
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">总来电负荷</div><div class="metric-value">{data["idx1"]}</div><div class="metric-footer">指标 1 (真实客房拨打量)</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">整体接通率</div><div class="metric-value">{data["overall_rate"]:.1%}</div><div class="metric-footer">(AI解决 + 人工接待)</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="rate-box"><div style="font-size:0.875rem; opacity:0.8;">核心产出：人工成功接通率</div><div class="rate-value">{data["idx10"]:.1%}</div><div style="font-size:0.75rem;">最终指标 10 (4+7)/(4+7+5+8)</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 第二行：环节深度拆解
    col_ai, col_human = st.columns([1, 1])
    
    with col_ai:
        st.markdown('<div class="section-box"><div class="section-title">PART A: AI 环节效能 (指标 2-6)</div>', unsafe_allow_html=True)
        # 展示 AI 相关指标
        st.write(f"**进入AI总量：** {data['idx2']} (指标 2)")
        st.progress(data['idx6'], text=f"AI 接通率: {data['idx6']:.1%}")
        
        inner_c1, inner_c2 = st.columns(2)
        inner_c1.metric("AI 独立完成", f"{data['idx3']} 通", help="指标 3")
        inner_c2.metric("AI 转接成功", f"{data['idx4']} 通", help="指标 4")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_human:
        st.markdown('<div class="section-box"><div class="section-title">PART B: 人工环节效能 (指标 7-10)</div>', unsafe_allow_html=True)
        # 展示 人工 相关指标
        st.write(f"**进入人工流程总量：** {data['human_den']} (分母 4+7+5+8)")
        st.progress(data['idx10'], text=f"人工接通率: {data['idx10']:.1%}")
        
        inner_h1, inner_h2 = st.columns(2)
        inner_h1.metric("人工实际接听", f"{data['human_num']} 通", help="分子 4+7")
        inner_h2.metric("直接进人工量", f"{data['idx9']} 通", help="指标 9 (7+8)")
        st.markdown('</div>', unsafe_allow_html=True)

    # 导出数据的补充信息
    with st.expander("🔍 查看指标 8 深度构成"):
        st.write(f"数据 1 (未接通/--/--): **{data['d1_8']}**")
        st.write(f"数据 2 (未接通/--/未接通): **{data['d2_8']}**")
        st.write("---")
        st.caption("指标 8 总计 = 数据 1 + 数据 2")

else:
    st.info("👋 **请在控制台上传 Excel 数据文件开始生成看板。**")
    st.markdown("""
        ### 如何使用：
        1. 在侧边栏上传**级联云文档**和**分机号文档**。
        2. 系统将自动执行全量数据清洗。
        3. 页面将自动为您生成高阶顾问级的分析报告。
    """)
