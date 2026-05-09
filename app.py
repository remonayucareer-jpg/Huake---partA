import streamlit as st
import pandas as pd

# 设置页面配置
st.set_page_config(page_title="酒店AI+人工效能分析看板", layout="wide")

# --- 核心 CSS 修复版 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; }
    
    .header-container { padding: 1rem 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 1rem; }
    .header-title { color: #0F172A; font-size: 1.8rem; font-weight: 700; }
    .header-subtitle { color: #64748B; font-size: 0.9rem; margin-top: 4px; }

    /* 5列 5行 网格系统 */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        grid-template-rows: repeat(5, 130px);
        gap: 12px;
        width: 100%;
        margin-top: 20px;
    }

    .data-box {
        border: 1px solid #E2E8F0;
        padding: 1.2rem;
        border-radius: 8px;
        background-color: #FFFFFF;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .name-text { color: #1E293B; font-size: 0.95rem; font-weight: 700; margin-bottom: 2px; }
    .sub-text { color: #94A3B8; font-size: 0.75rem; line-height: 1.2; margin-bottom: 8px; min-height: 2.4rem; }
    .value-text { color: #2563EB; font-size: 1.8rem; font-weight: 800; margin-top: auto; }
    .rate-value { color: #059669; }

    /* 跨行逻辑 */
    .span-5 { grid-row: span 5; }
    .span-3 { grid-row: span 3; }
    .span-2 { grid-row: span 2; }
    
    .highlight-border { border: 2px solid #2563EB; background-color: #F8FAFC; }
    </style>
    """, unsafe_allow_html=True)

# --- 计算逻辑 (保持不变) ---
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
    idx6 = idx2 / idx2 if idx2 > 0 else 0 
    idx7 = len(df_real[(df_real['通话状态'] == '接通') & (df_real['AI通话状态'] == '--') & (df_real['人工通话状态'] == '接通')])
    idx8 = len(df_real[(df_real['通话状态'] == '未接通') & (df_real['AI通话状态'] == '--')]) # 简化逻辑
    idx9 = idx7 + idx8
    num_10, den_10 = (idx4 + idx7), (idx4 + idx7 + idx5 + idx8)
    idx10 = num_10 / den_10 if den_10 > 0 else 0
    overall_rate = (idx3 + idx4 + idx7) / idx1 if idx1 > 0 else 0
    return locals()

# --- 界面渲染 ---
with st.sidebar:
    st.title("控制台")
    up_cloud = st.file_uploader("1. 级联云原始数据", type=["xlsx"])
    up_ext = st.file_uploader("2. 分机号数据库", type=["xlsx"])

st.markdown("""
    <div class="header-container">
        <div class="header-title">酒店电话效能全口径分析</div>
        <div class="header-subtitle">数据报告周期：0430 - 0506</div>
    </div>
    """, unsafe_allow_html=True)

if up_cloud and up_ext:
    data = run_analysis(pd.read_excel(up_cloud), pd.read_excel(up_ext))
    
    st.markdown(f"""
    <div class="grid-container">
        <div class="data-box span-5">
            <div class="name-text">总来电量</div>
            <div class="sub-text">(所有启用AI的客房呼出电话量)</div>
            <div class="value-text">{data['idx1']}</div>
        </div>

        <div class="data-box span-3">
            <div class="name-text">进入AI接待流程电话量</div>
            <div class="sub-text">进入AI语音环节总量</div>
            <div class="value-text">{data['idx2']}</div>
        </div>
        <div class="data-box span-2">
            <div class="name-text">直接进入人工接待流程电话量</div>
            <div class="sub-text">未触发AI，直接外呼转人工量</div>
            <div class="value-text">{data['idx9']}</div>
        </div>

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
            <div class="name-text">人工接通量④</div>
            <div class="sub-text">(直接转接人工，人工接通)</div>
            <div class="value-text">{data['idx7']}</div>
        </div>
        <div class="data-box">
            <div class="name-text">人工未接通量⑤</div>
            <div class="sub-text">(直接进人工，人工未接通或客户放弃量)</div>
            <div class="value-text">{data['idx8']}</div>
        </div>

        <div class="data-box span-3">
            <div class="name-text">AI成功接通率</div>
            <div class="sub-text">(AI接通量①+②+③ / 进入AI接待流程电话量)</div>
            <div class="value-text rate-value">{data['idx6']:.1%}</div>
        </div>
        <div class="data-box span-2">
            <div class="name-text">人工成功接通率</div>
            <div class="sub-text">(最终人工环节接通占比)</div>
            <div class="value-text rate-value">{data['idx10']:.1%}</div>
        </div>

        <div class="data-box span-5 highlight-border">
            <div class="name-text" style="color: #2563EB;">整体电话成功接通率</div>
            <div class="sub-text">全口径成功处理比例</div>
            <div class="value-text rate-value" style="font-size: 2.2rem; color: #2563EB;">{data['overall_rate']:.1%}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("👋 请上传数据。")
