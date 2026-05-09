import streamlit as st
import pandas as pd

# 设置页面配置
st.set_page_config(page_title="酒店AI+人工效能分析看板", layout="wide")

# --- 高级 CSS：极简数据看板风格 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; }
    
    .header-container { padding: 1rem 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 2rem; }
    .header-title { color: #0F172A; font-size: 1.8rem; font-weight: 700; }
    .header-subtitle { color: #64748B; font-size: 0.9rem; margin-top: 4px; }

    .part-title { font-size: 1.1rem; font-weight: 700; color: #475569; margin: 2rem 0 1rem 0; text-transform: uppercase; letter-spacing: 0.05em; }

    /* 纵向对齐的卡片容器 */
    .metric-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .data-box {
        border: 1px solid #E2E8F0;
        padding: 1.2rem;
        border-radius: 8px;
        background-color: #FFFFFF;
        text-align: left;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .name-text { color: #1E293B; font-size: 0.95rem; font-weight: 700; margin-bottom: 2px; }
    .sub-text { color: #94A3B8; font-size: 0.75rem; line-height: 1.3; margin-bottom: 10px; min-height: 2em; }
    .value-text { color: #2563EB; font-size: 1.8rem; font-weight: 800; margin-top: auto; }
    
    /* 成功率类数字使用更显眼的颜色 */
    .rate-value { color: #059669; } 
    </style>
    """, unsafe_allow_html=True)

# --- 核心计算函数 ---
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

    # 指标计算逻辑
    idx1 = len(df_real)
    idx3 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '--')])
    idx4 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '接通')])
    idx5 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '接通') & (df_real['人工通话状态'] == '未接通')])
    idx2 = idx3 + idx4 + idx5
    idx6 = idx2 / idx2 if idx2 > 0 else 0 

    idx7 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '接通')])
    d1_8 = len(df_real[(df_real['通话状态'] == '未接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '--')])
    d2_8 = len(df_real[(df_real['通话状态'] == '未接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '未接通')])
    idx8 = d1_8 + d2_8
    idx9 = idx7 + idx8
    
    num_10 = idx4 + idx7
    den_10 = idx4 + idx7 + idx5 + idx8
    idx10 = num_10 / den_10 if den_10 > 0 else 0
    
    overall_rate = (idx3 + idx4 + idx7) / idx1 if idx1 > 0 else 0

    return locals()

# --- 界面渲染 ---

with st.sidebar:
    st.title("控制台")
    up_cloud = st.file_uploader("1. 级联云原始数据", type=["xlsx"])
    up_ext = st.file_uploader("2. 分机号数据库", type=["xlsx"])
    st.divider()
    st.caption("内部自用校验版 v4.1")

st.markdown("""
    <div class="header-container">
        <div class="header-title">酒店电话效能全口径分析</div>
        <div class="header-subtitle">数据报告周期：0430 - 0506  |  状态：实时分析中</div>
    </div>
    """, unsafe_allow_html=True)

if up_cloud and up_ext:
    data = run_analysis(pd.read_excel(up_cloud), pd.read_excel(up_ext))
    
    st.markdown('<div class="part-title">PART 1：酒店电话数据 (内部校验流)</div>', unsafe_allow_html=True)

    # 核心 5 列布局
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1: # 第一列：总源头
        st.markdown(f"""
            <div class="metric-container">
                <div class="data-box">
                    <div class="name-text">总来电量</div>
                    <div class="sub-text">(所有启用AI的客房呼出电话量)</div>
                    <div class="value-text">{data['idx1']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c2: # 第二列：分流层
        st.markdown(f"""
            <div class="metric-container">
                <div class="data-box">
                    <div class="name-text">进入AI接待流程电话量</div>
                    <div class="sub-text">进入AI语音环节总量</div>
                    <div class="value-text">{data['idx2']}</div>
                </div>
                <div class="data-box">
                    <div class="name-text">直接进入人工接待流程电话量</div>
                    <div class="sub-text">未触发AI，直接外呼转人工量</div>
                    <div class="value-text">{data['idx9']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c3: # 第三列：行为细分
        st.markdown(f"""
            <div class="metric-container">
                <div class="data-box">
                    <div class="name-text">AI接通量①</div>
                    <div class="sub-text">(AI接通，AI完成，未转人工)</div>
                    <div class="value-text">{data['idx3']}</div>
                </div>
                <div class="data-box">
                    <div class="name-text">AI接通量②</div>
                    <div class="sub-text">(AI接通，转接人工，人工接通)</div>
                    <div class="value-text">{data['idx4']}</div>
                </div>
                <div class="data-box">
                    <div class="name-text">AI接通量③</div>
                    <div class="sub-text">(AI接通，转接人工，人工未接通)</div>
                    <div class="value-text">{data['idx5']}</div>
                </div>
                <div class="data-box">
                    <div class="name-text">人工接通④</div>
                    <div class="sub-text">(直接转接人工，人工接通)</div>
                    <div class="value-text">{data['idx7']}</div>
                </div>
                <div class="data-box">
                    <div class="name-text">人工未接通量⑤</div>
                    <div class="sub-text">(直接进人工，人工未接通或客户放弃量)</div>
                    <div class="value-text">{data['idx8']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c4: # 第四列：过程成功率
        st.markdown(f"""
            <div class="metric-container">
                <div class="data-box">
                    <div class="name-text">AI成功接通率</div>
                    <div class="sub-text">(AI接通量①+②+③ / 进入AI接待流程电话量)</div>
                    <div class="value-text rate-value">{data['idx6']:.1%}</div>
                </div>
                <div class="data-box">
                    <div class="name-text">人工成功接通率</div>
                    <div class="sub-text">(最终人工环节接通占比)</div>
                    <div class="value-text rate-value">{data['idx10']:.1%}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c5: # 第五列：终极指标
        st.markdown(f"""
            <div class="metric-container">
                <div class="data-box" style="border: 2px solid #2563EB;">
                    <div class="name-text" style="color: #2563EB;">整体电话成功接通率</div>
                    <div class="sub-text">全口径成功处理比例</div>
                    <div class="value-text rate-value" style="font-size: 2.2rem;">{data['overall_rate']:.1%}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

else:
    st.info("👋 请在左侧上传 Excel 数据开始分析。")
