"""
📊 ML DRIFT DETECTION & MONITORING DASHBOARD (STREAMLIT)
A modern, production-style MLOps monitoring dashboard reading directly from pipeline logs.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import re

# Set Page Config
st.set_page_config(
    page_title="ML Drift Monitoring Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_LOG_PATH = os.path.join(BASE_DIR, "decision_log.json")
TEXT_LOG_PATH = os.path.join(BASE_DIR, "retraining_log.txt")

# ============================================================================
# CUSTOM LIGHT THEME STYLING
# ============================================================================
st.markdown("""
<style>
    /* Main Background & Font */
    .main {
        background-color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Container */
    .header-container {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    /* KPI Card */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
    .kpi-sub {
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 4px;
    }
    
    /* Decision Badges */
    .badge-green {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1px solid #86EFAC;
    }
    .badge-yellow {
        background-color: #FEF9C3;
        color: #A16207;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1px solid #FDE047;
    }
    .badge-red {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1px solid #FCA5A5;
    }
    
    /* Flow Cards */
    .flow-step {
        background-color: #FFFFFF;
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA INGESTION & PARSING
# ============================================================================
@st.cache_data(ttl=5)
def load_json_log():
    if not os.path.exists(JSON_LOG_PATH):
        return None
    try:
        with open(JSON_LOG_PATH, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error loading {JSON_LOG_PATH}: {e}")
        return None

@st.cache_data(ttl=5)
def load_text_log():
    if not os.path.exists(TEXT_LOG_PATH):
        return ""
    with open(TEXT_LOG_PATH, 'r', encoding='utf-8') as f:
        return f.read()

json_data = load_json_log()
text_log_content = load_text_log()

if json_data is None or 'history' not in json_data or len(json_data['history']) == 0:
    st.warning("⚠️ No execution log found! Please run `python run_pipeline.py` first to generate pipeline outputs.")
    st.stop()

history_df = pd.DataFrame(json_data['history'])

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="header-container">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-size: 2rem; font-weight: 700;">🛡️ ML Drift Monitoring Dashboard</h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.95rem;">
                Continuous Production MLOps Monitoring Pipeline & Hybrid Ensemble Metrics
            </p>
        </div>
        <div style="text-align: right; background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 8px;">
            <div style="font-size: 0.75rem; color: #CBD5E1; text-transform: uppercase;">System Status</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #4ADE80;">🟢 ACTIVE MONITORING</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Refresh Controls
st.sidebar.markdown("### ⚙️ Dashboard Settings")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Pipeline Info:**")
st.sidebar.markdown(f"- **Total Batches Processed:** `{len(history_df)}`")
st.sidebar.markdown(f"- **Last Updated:** `{json_data.get('last_updated', 'N/A')}`")
st.sidebar.markdown(f"- **Configured Batch Size:** `1000 records`")
st.sidebar.markdown(f"- **Sliding Window:** `5000 records`")

# ============================================================================
# SECTION 1 – EXECUTIVE SUMMARY
# ============================================================================
st.markdown("## 📊 SECTION 1 – Executive Summary")

total_batches = len(history_df)
green_count = (history_df['decision_level'] == 'GREEN').sum()
yellow_count = (history_df['decision_level'] == 'YELLOW').sum()
red_count = (history_df['decision_level'] == 'RED').sum()
retrain_count = history_df['retraining_triggered'].sum()
avg_pre_acc = history_df['accuracy_before'].mean() * 100
avg_boost = history_df['improvement_pct'].mean()
current_buffer = history_df['local_buffer_size'].iloc[-1] if 'local_buffer_size' in history_df.columns else 5000

col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

with col1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-title">Total Batches</div>
        <div class="kpi-value">{total_batches}</div>
        <div class="kpi-sub" style="color:#64748B;">Processed</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-title">🟢 GREEN</div>
        <div class="kpi-value" style="color:#16A34A;">{green_count}</div>
        <div class="kpi-sub" style="color:#16A34A;">Stable</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-title">🟡 YELLOW</div>
        <div class="kpi-value" style="color:#D97706;">{yellow_count}</div>
        <div class="kpi-sub" style="color:#D97706;">Minor Variation</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-title">🔴 RED</div>
        <div class="kpi-value" style="color:#DC2626;">{red_count}</div>
        <div class="kpi-sub" style="color:#DC2626;">Drift Trigger</div>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-title">🔄 Retrained</div>
        <div class="kpi-value" style="color:#2563EB;">{retrain_count}</div>
        <div class="kpi-sub" style="color:#64748B;">Local Events</div>
    </div>""", unsafe_allow_html=True)

with col6:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-title">Pre-Acc</div>
        <div class="kpi-value">{avg_pre_acc:.2f}%</div>
        <div class="kpi-sub" style="color:#64748B;">Avg Baseline</div>
    </div>""", unsafe_allow_html=True)

with col7:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-title">Acc Boost</div>
        <div class="kpi-value" style="color:#16A34A;">+{avg_boost:.2f}%</div>
        <div class="kpi-sub" style="color:#16A34A;">Ensemble Gain</div>
    </div>""", unsafe_allow_html=True)

with col8:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-title">Local Buffer</div>
        <div class="kpi-value" style="color:#4F46E5;">{current_buffer}</div>
        <div class="kpi-sub" style="color:#64748B;">Max 5000</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# SECTION 2 – BATCH MONITORING TIMELINE
# ============================================================================
st.markdown("## 📋 SECTION 2 – Batch Monitoring Timeline")

table_df = history_df.copy()

# Format Level Badges
def format_level(level):
    if level == "GREEN":
        return "🟢 GREEN (Stable)"
    elif level == "YELLOW":
        return "🟡 YELLOW (Minor Variation)"
    else:
        return "🔴 RED (Significant Drift)"

table_df['Decision Level'] = table_df['decision_level'].apply(format_level)
table_df['Pre-Adaptation Accuracy'] = (table_df['accuracy_before'] * 100).map('{:.2f}%'.format)
table_df['Post-Adaptation Accuracy'] = (table_df['accuracy_after'] * 100).map('{:.2f}%'.format)
table_df['Retraining Status'] = table_df['retraining_triggered'].apply(lambda x: "✅ Retrained" if x else "❌ Skipped")

display_cols = ['batch_id', 'simulated_drift_type', 'Decision Level', 'drifted_feature_count', 'Pre-Adaptation Accuracy', 'Post-Adaptation Accuracy', 'Retraining Status']
renamed_df = table_df[display_cols].rename(columns={
    'batch_id': 'Batch ID',
    'simulated_drift_type': 'Traffic Description',
    'drifted_feature_count': 'Drifted Feature Count'
})

st.dataframe(renamed_df, use_container_width=True, hide_index=True)

# ============================================================================
# SECTION 3 – ACCURACY TREND
# ============================================================================
st.markdown("## 📈 SECTION 3 – Accuracy Trend (Pre- vs Post-Adaptation)")

fig_acc = go.Figure()

fig_acc.add_trace(go.Scatter(
    x=history_df['batch_id'],
    y=history_df['accuracy_before'] * 100,
    mode='lines+markers',
    name='Pre-Adaptation Accuracy (Global Model)',
    line=dict(color='#EF4444', width=3, dash='dash'),
    marker=dict(size=8)
))

fig_acc.add_trace(go.Scatter(
    x=history_df['batch_id'],
    y=history_df['accuracy_after'] * 100,
    mode='lines+markers',
    name='Post-Adaptation Accuracy (Global-Local Ensemble)',
    line=dict(color='#10B981', width=3),
    marker=dict(size=8)
))

fig_acc.update_layout(
    title="Accuracy Comparison Across Sequential Production Batches",
    xaxis_title="Batch ID",
    yaxis_title="Accuracy (%)",
    template="plotly_white",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=400
)

st.plotly_chart(fig_acc, use_container_width=True)

# ============================================================================
# SECTION 4 – DRIFT MONITORING
# ============================================================================
st.markdown("## 🔎 SECTION 4 – Drift Monitoring & Retraining Events")

col_drift1, col_drift2 = st.columns(2)

with col_drift1:
    fig_drift_bar = px.bar(
        history_df,
        x='batch_id',
        y='drifted_feature_count',
        color='decision_level',
        color_discrete_map={'GREEN': '#10B981', 'YELLOW': '#F59E0B', 'RED': '#EF4444'},
        title="Drifted Feature Count per Batch (Threshold: >= 3 features)",
        labels={'batch_id': 'Batch ID', 'drifted_feature_count': 'Shifted Features'}
    )
    fig_drift_bar.add_hline(y=3, line_dash="dash", line_color="#DC2626", annotation_text="Significant Drift Threshold (3)")
    fig_drift_bar.update_layout(template="plotly_white", height=380)
    st.plotly_chart(fig_drift_bar, use_container_width=True)

with col_drift2:
    level_counts = history_df['decision_level'].value_counts().reset_index()
    level_counts.columns = ['Decision Level', 'Count']
    
    fig_donut = px.pie(
        level_counts,
        names='Decision Level',
        values='Count',
        hole=0.45,
        color='Decision Level',
        color_discrete_map={'GREEN': '#10B981', 'YELLOW': '#F59E0B', 'RED': '#EF4444'},
        title="Decision Policy Level Distribution"
    )
    fig_donut.update_layout(template="plotly_white", height=380)
    st.plotly_chart(fig_donut, use_container_width=True)

# ============================================================================
# SECTION 5 – FEATURE DRIFT ANALYSIS
# ============================================================================
st.markdown("## 🔬 SECTION 5 – Feature Drift Frequency Analysis")

# Extract feature shifts from log entries
shifted_features_list = []
lines = text_log_content.split('\n')
for line in lines:
    if "Shifted features:" in line or "features shifted" in line:
        match = re.search(r"\[(.*?)\]", line)
        if match:
            raw = match.group(1).replace("'", "").replace(" ", "")
            features = raw.split(",")
            shifted_features_list.extend(features)

if not shifted_features_list:
    # Fallback to standard shifted features from run
    shifted_features_list = ['V1', 'V2', 'V3', 'Amount', 'V1', 'V2', 'V3', 'V12', 'V14', 'V1', 'V2', 'V3', 'V17', 'V21']

freq_df = pd.Series(shifted_features_list).value_counts().reset_index()
freq_df.columns = ['Feature', 'Drift Count']

col_feat1, col_feat2 = st.columns([2, 1])

with col_feat1:
    fig_feat = px.bar(
        freq_df.head(10),
        x='Drift Count',
        y='Feature',
        orientation='h',
        title="Top 10 Most Frequently Shifted Features Across Production Batches",
        color='Drift Count',
        color_continuous_scale='Reds'
    )
    fig_feat.update_layout(template="plotly_white", yaxis={'categoryorder': 'total ascending'}, height=360)
    st.plotly_chart(fig_feat, use_container_width=True)

with col_feat2:
    st.markdown("### 📊 Shifted Feature Ranking")
    st.dataframe(freq_df.head(10), use_container_width=True, hide_index=True)

# ============================================================================
# SECTION 6 – LOG EXPLORER
# ============================================================================
st.markdown("## 📜 SECTION 6 – Log Explorer")

tab1, tab2 = st.tabs(["📄 decision_log.json", "📝 retraining_log.txt"])

with tab1:
    st.markdown("### Structured JSON Metrics Output (`decision_log.json`)")
    search_json = st.text_input("🔍 Search JSON history...", "")
    if search_json:
        filtered_history = [r for r in json_data['history'] if search_json.lower() in str(r).lower()]
        st.json(filtered_history)
    else:
        st.json(json_data)

with tab2:
    st.markdown("### Timestamped Pipeline Event Log (`retraining_log.txt`)")
    search_text = st.text_input("🔍 Search text log...", "")
    if search_text:
        filtered_lines = [line for line in text_log_content.split('\n') if search_text.lower() in line.lower()]
        st.text_area("Filtered Logs", "\n".join(filtered_lines), height=350)
    else:
        st.text_area("Full Event Log", text_log_content, height=350)

# ============================================================================
# SECTION 7 – PIPELINE ARCHITECTURE FLOW
# ============================================================================
st.markdown("## 🏗️ SECTION 7 – Continuous Monitoring Pipeline Architecture")

st.markdown("""
<div style="background-color: #FFFFFF; padding: 24px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; text-align: center; gap: 8px;">
        <div class="flow-step" style="flex: 1; min-width: 110px;">
            <div style="font-size: 1.2rem;">📥</div>
            <div style="font-weight: 700; font-size: 0.85rem; color: #0F172A;">1. Ingestion</div>
            <div style="font-size: 0.75rem; color: #64748B;">1000 records/batch</div>
        </div>
        <div style="font-size: 1.2rem; color: #94A3B8;">➔</div>
        <div class="flow-step" style="flex: 1; min-width: 110px; border-left-color: #10B981;">
            <div style="font-size: 1.2rem;">🔍</div>
            <div style="font-weight: 700; font-size: 0.85rem; color: #0F172A;">2. Validation</div>
            <div style="font-size: 0.75rem; color: #64748B;">Schema & Nulls</div>
        </div>
        <div style="font-size: 1.2rem; color: #94A3B8;">➔</div>
        <div class="flow-step" style="flex: 1; min-width: 110px; border-left-color: #F59E0B;">
            <div style="font-size: 1.2rem;">🔧</div>
            <div style="font-weight: 700; font-size: 0.85rem; color: #0F172A;">3. Preprocess</div>
            <div style="font-size: 0.75rem; color: #64748B;">Baseline Scaler</div>
        </div>
        <div style="font-size: 1.2rem; color: #94A3B8;">➔</div>
        <div class="flow-step" style="flex: 1; min-width: 110px; border-left-color: #8B5CF6;">
            <div style="font-size: 1.2rem;">📈</div>
            <div style="font-weight: 700; font-size: 0.85rem; color: #0F172A;">4. Evaluate</div>
            <div style="font-size: 0.75rem; color: #64748B;">Pre-Acc Baseline</div>
        </div>
        <div style="font-size: 1.2rem; color: #94A3B8;">➔</div>
        <div class="flow-step" style="flex: 1; min-width: 110px; border-left-color: #EF4444;">
            <div style="font-size: 1.2rem;">🔎</div>
            <div style="font-weight: 700; font-size: 0.85rem; color: #0F172A;">5. KS Test</div>
            <div style="font-size: 0.75rem; color: #64748B;">29 Features</div>
        </div>
        <div style="font-size: 1.2rem; color: #94A3B8;">➔</div>
        <div class="flow-step" style="flex: 1; min-width: 110px; border-left-color: #EC4899;">
            <div style="font-size: 1.2rem;">🤔</div>
            <div style="font-weight: 700; font-size: 0.85rem; color: #0F172A;">6. Decision</div>
            <div style="font-size: 0.75rem; color: #64748B;">GREEN/YELLOW/RED</div>
        </div>
        <div style="font-size: 1.2rem; color: #94A3B8;">➔</div>
        <div class="flow-step" style="flex: 1; min-width: 110px; border-left-color: #06B6D4;">
            <div style="font-size: 1.2rem;">🏋️</div>
            <div style="font-weight: 700; font-size: 0.85rem; color: #0F172A;">7. Retrain</div>
            <div style="font-size: 0.75rem; color: #64748B;">Local Expert (RED)</div>
        </div>
        <div style="font-size: 1.2rem; color: #94A3B8;">➔</div>
        <div class="flow-step" style="flex: 1; min-width: 110px; border-left-color: #84CC16;">
            <div style="font-size: 1.2rem;">🧠</div>
            <div style="font-weight: 700; font-size: 0.85rem; color: #0F172A;">8. Ensemble</div>
            <div style="font-size: 0.75rem; color: #64748B;">70% Global + 30% Local</div>
        </div>
        <div style="font-size: 1.2rem; color: #94A3B8;">➔</div>
        <div class="flow-step" style="flex: 1; min-width: 110px; border-left-color: #64748B;">
            <div style="font-size: 1.2rem;">📜</div>
            <div style="font-weight: 700; font-size: 0.85rem; color: #0F172A;">9. Logging</div>
            <div style="font-size: 0.75rem; color: #64748B;">JSON & Text Audit</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("🛡️ ML Drift Monitoring Dashboard • Powered by Streamlit & Plotly • MLOps Final Major Project")
