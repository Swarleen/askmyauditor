import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import anthropic
import json
import io
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ask the Auditor · AI Audit Analytics Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── STYLES ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main { background: #F8F9FC; }

  .hero {
    background: linear-gradient(135deg, #1B3A6B 0%, #0F2548 60%, #0A1A35 100%);
    border-radius: 16px;
    padding: 40px 48px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
  }
  .hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
  }
  .hero-sub {
    font-size: 1rem;
    color: rgba(255,255,255,0.7);
    margin: 0;
  }
  .hero-badge {
    display: inline-block;
    background: rgba(255,215,0,0.15);
    border: 1px solid rgba(255,215,0,0.4);
    color: #FFD700;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 16px;
  }

  .kpi-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    border-left: 4px solid #1B3A6B;
    box-shadow: 0 1px 8px rgba(0,0,0,0.06);
    height: 100%;
  }
  .kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #888;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
  }
  .kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1B3A6B;
    line-height: 1;
  }
  .kpi-sub {
    font-size: 0.78rem;
    color: #999;
    margin-top: 4px;
  }
  .kpi-red { border-left-color: #C0392B; }
  .kpi-red .kpi-value { color: #C0392B; }
  .kpi-amber { border-left-color: #E67E22; }
  .kpi-amber .kpi-value { color: #E67E22; }
  .kpi-green { border-left-color: #1A5C38; }
  .kpi-green .kpi-value { color: #1A5C38; }

  .answer-box {
    background: white;
    border-radius: 12px;
    padding: 28px 32px;
    border-left: 5px solid #1B3A6B;
    box-shadow: 0 2px 16px rgba(0,0,0,0.08);
    margin: 20px 0;
  }
  .answer-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #1B3A6B;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 12px;
  }
  .answer-text {
    font-size: 1.05rem;
    color: #1a1a1a;
    line-height: 1.75;
  }

  .rec-box {
    background: linear-gradient(135deg, #FFF8E1 0%, #FFFBF0 100%);
    border-radius: 12px;
    padding: 20px 24px;
    border-left: 5px solid #E67E22;
    margin: 16px 0;
  }
  .rec-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #E67E22;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  .rec-text {
    font-size: 0.95rem;
    color: #333;
    line-height: 1.65;
  }

  .example-btn {
    display: inline-block;
    background: white;
    border: 1.5px solid #E0E4F0;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.85rem;
    color: #1B3A6B;
    cursor: pointer;
    margin: 4px;
    transition: all 0.15s;
    font-family: 'Inter', sans-serif;
  }
  .example-btn:hover {
    background: #EEF1F7;
    border-color: #1B3A6B;
  }

  .sidebar-section {
    background: #F0F4FA;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 16px;
  }
  .sidebar-label {
    font-size: 0.7rem;
    font-weight: 700;
    color: #888;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .priority-critical { color: #C0392B; font-weight: 700; }
  .priority-high { color: #E67E22; font-weight: 700; }
  .priority-medium { color: #F39C12; font-weight: 600; }
  .priority-low { color: #1A5C38; font-weight: 600; }

  .powerbi-section {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 8px rgba(0,0,0,0.06);
    margin-top: 16px;
  }

  .chat-q {
    background: #EEF1F7;
    border-radius: 12px 12px 12px 0;
    padding: 14px 18px;
    margin: 8px 0;
    font-size: 0.95rem;
    color: #1B3A6B;
    font-weight: 500;
    max-width: 85%;
  }
  .chat-a {
    background: white;
    border-radius: 12px 12px 0 12px;
    padding: 14px 18px;
    margin: 8px 0 8px auto;
    font-size: 0.95rem;
    color: #222;
    border: 1px solid #E8ECF5;
    max-width: 90%;
  }

  div[data-testid="stMetric"] {
    background: white;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
  }
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel('IT_Audit_Universe.xlsx')
    df['Last_Audit_Date'] = pd.to_datetime(df['Last_Audit_Date'])
    return df

# ── AI AGENT ──────────────────────────────────────────────────────────────────
def build_system_prompt(df):
    schema = """
DATASET: IT Audit Universe — 44 auditable entities across 5 technology domains.

COLUMNS:
- Audit_Entity (text): Name of the auditable process or system
- Domain (text): One of: Cybersecurity | Cloud & Infrastructure | Data Governance | IT Governance | Compliance & Regulatory
- Inherent_Risk_Score (1-5): Raw risk before controls. 5 = highest.
- Control_Effectiveness (text): Strong | Adequate | Weak | Not Tested
- Last_Audit_Date (date): When the entity was last audited
- Months_Since_Last_Audit (integer): Months elapsed since last audit
- Residual_Risk_Score (1-5): Risk after controls applied. Drives priority.
- Audit_Priority (text): Critical | High | Medium | Low
- Recommended_Audit_Cycle (text): Annual | Biennial | Risk-Based
- Regulatory_Relevance (text): High | Medium | Low
- Open_Issues (integer): Unresolved audit findings
- Management_Response_Status (text): On Track | Overdue | Not Started
- Overdue_Flag (text): Yes | No — whether entity is overdue for review

KEY STATISTICS:
- Total entities: 44
- Critical priority: """ + str(len(df[df['Audit_Priority']=='Critical'])) + """
- High priority: """ + str(len(df[df['Audit_Priority']=='High'])) + """
- Overdue entities: """ + str(len(df[df['Overdue_Flag']=='Yes'])) + """
- Total open issues: """ + str(df['Open_Issues'].sum()) + """
- Weak/Not Tested controls: """ + str(len(df[df['Control_Effectiveness'].isin(['Weak','Not Tested'])])) + """

FULL DATASET (JSON):
""" + df.to_json(orient='records', date_format='iso') + """

YOUR ROLE:
You are an expert Technology Audit Analytics AI Agent. You answer questions about this audit universe dataset with the precision of a senior technology auditor and the clarity of a skilled data analyst.

RESPONSE FORMAT — always return a valid JSON object with these exact keys:
{
  "answer": "Your plain English analytical answer (2-4 sentences, specific, data-driven)",
  "key_finding": "One sentence — the single most important takeaway",
  "recommendation": "One specific, actionable audit recommendation based on the data",
  "chart_type": "bar | horizontal_bar | scatter | pie | none",
  "chart_data": {
    "x": ["label1", "label2"],
    "y": [10, 20],
    "color": ["#C0392B", "#E67E22"],
    "title": "Chart title",
    "x_label": "X axis label",
    "y_label": "Y axis label"
  },
  "data_table": [{"Column": "Value"}, ...],
  "entities_referenced": ["Entity1", "Entity2"]
}

RULES:
- Always cite specific numbers from the dataset
- chart_data colors: Critical=#C0392B, High=#E67E22, Medium=#F39C12, Low=#1A5C38, default=#1B3A6B
- If no chart makes sense, set chart_type to "none" and chart_data to null
- data_table should contain the most relevant rows for the question (max 10 rows)
- Never make up data — only use what is in the dataset
- Speak like a senior auditor — authoritative, specific, and action-oriented
"""
    return schema

def ask_agent(question, df):
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    system = build_system_prompt(df)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": question}]
    )
    
    raw = message.content[0].text.strip()
    
    # Clean JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    
    return json.loads(raw)

def render_chart(result):
    chart_type = result.get("chart_type", "none")
    chart_data = result.get("chart_data")
    
    if chart_type == "none" or not chart_data:
        return None
    
    x = chart_data.get("x", [])
    y = chart_data.get("y", [])
    colors = chart_data.get("color", ["#1B3A6B"] * len(x))
    title = chart_data.get("title", "")
    x_label = chart_data.get("x_label", "")
    y_label = chart_data.get("y_label", "")
    
    if chart_type == "bar":
        fig = px.bar(x=x, y=y, title=title,
                     labels={"x": x_label, "y": y_label},
                     color=x, color_discrete_sequence=colors)
        fig.update_traces(marker_color=colors)
    elif chart_type == "horizontal_bar":
        fig = px.bar(x=y, y=x, title=title,
                     labels={"x": y_label, "y": x_label},
                     orientation='h', color=x,
                     color_discrete_sequence=colors)
        fig.update_traces(marker_color=colors)
    elif chart_type == "pie":
        fig = px.pie(names=x, values=y, title=title,
                     color_discrete_sequence=colors)
    elif chart_type == "scatter":
        fig = px.scatter(x=x, y=y, title=title,
                        labels={"x": x_label, "y": y_label})
    else:
        return None
    
    fig.update_layout(
        font_family="Inter",
        title_font_size=15,
        title_font_color="#1B3A6B",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50, b=40, l=40, r=20),
        showlegend=False,
        xaxis=dict(gridcolor="#F0F0F0"),
        yaxis=dict(gridcolor="#F0F0F0")
    )
    return fig

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def render_sidebar(df):
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 16px 0 8px 0;'>
          <div style='font-size:2rem;'>🔍</div>
          <div style='font-weight:700; color:#1B3A6B; font-size:1.1rem;'>Ask the Auditor</div>
          <div style='font-size:0.75rem; color:#999; margin-top:4px;'>AI Audit Analytics Agent</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()

        # Universe snapshot
        st.markdown("<div class='sidebar-label'>🌐 Universe Snapshot</div>", unsafe_allow_html=True)
        critical = len(df[df['Audit_Priority']=='Critical'])
        high = len(df[df['Audit_Priority']=='High'])
        overdue = len(df[df['Overdue_Flag']=='Yes'])
        open_issues = df['Open_Issues'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", "44")
            st.metric("Critical", critical)
        with col2:
            st.metric("Overdue", overdue)
            st.metric("Open Issues", open_issues)
        
        st.divider()
        
        # Domain filter
        st.markdown("<div class='sidebar-label'>🏢 Filter by Domain</div>", unsafe_allow_html=True)
        domains = ["All Domains"] + df['Domain'].unique().tolist()
        selected_domain = st.selectbox("", domains, label_visibility="collapsed")
        
        st.divider()
        
        # Profile links
        st.markdown("<div class='sidebar-label'>👤 About the Analyst</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='sidebar-section'>
          <div style='font-weight:600; color:#1B3A6B; font-size:0.9rem;'>Swarleen Bhamra</div>
          <div style='font-size:0.78rem; color:#666; margin-top:2px;'>Data Analyst · Power BI · AI Analytics</div>
          <div style='margin-top:10px;'>
            <a href='https://www.swarleen.com' target='_blank' style='color:#1B3A6B; font-size:0.78rem; text-decoration:none;'>🌐 swarleen.com</a><br>
            <a href='https://www.linkedin.com/in/swarleenbhamra/' target='_blank' style='color:#1B3A6B; font-size:0.78rem; text-decoration:none;'>💼 LinkedIn</a><br>
            <a href='https://github.com/Swarleen' target='_blank' style='color:#1B3A6B; font-size:0.78rem; text-decoration:none;'>📂 GitHub</a>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        return selected_domain

# ── MAIN APP ──────────────────────────────────────────────────────────────────
def main():
    df = load_data()

    # Sidebar
    selected_domain = render_sidebar(df)
    filtered_df = df if selected_domain == "All Domains" else df[df['Domain'] == selected_domain]

    # Hero
    st.markdown("""
    <div class='hero'>
      <div class='hero-badge'>✦ AI-POWERED AUDIT ANALYTICS</div>
      <div class='hero-title'>🔍 Ask the Auditor</div>
      <div class='hero-sub'>Natural language queries on live audit universe data · Powered by Claude AI · Built by Swarleen Bhamra</div>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""<div class='kpi-card'>
          <div class='kpi-label'>Total Entities</div>
          <div class='kpi-value'>44</div>
          <div class='kpi-sub'>Across 5 domains</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        crit = len(df[df['Audit_Priority']=='Critical'])
        st.markdown(f"""<div class='kpi-card kpi-red'>
          <div class='kpi-label'>Critical Priority</div>
          <div class='kpi-value'>{crit}</div>
          <div class='kpi-sub'>Immediate attention</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        over = len(df[df['Overdue_Flag']=='Yes'])
        st.markdown(f"""<div class='kpi-card kpi-amber'>
          <div class='kpi-label'>Overdue</div>
          <div class='kpi-value'>{over}</div>
          <div class='kpi-sub'>Past review window</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        issues = df['Open_Issues'].sum()
        st.markdown(f"""<div class='kpi-card kpi-red'>
          <div class='kpi-label'>Open Issues</div>
          <div class='kpi-value'>{issues}</div>
          <div class='kpi-sub'>Unresolved findings</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        weak = len(df[df['Control_Effectiveness'].isin(['Weak','Not Tested'])])
        st.markdown(f"""<div class='kpi-card kpi-amber'>
          <div class='kpi-label'>Weak Controls</div>
          <div class='kpi-value'>{weak}</div>
          <div class='kpi-sub'>Weak or not tested</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🤖  Ask the Auditor", "📊  Power BI Dashboard", "📋  Audit Universe Data"])

    # ── TAB 1: AI AGENT ────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Ask anything about the audit universe")
        st.markdown("<div style='color:#888; font-size:0.9rem; margin-bottom:20px;'>Type a question in plain English — the AI agent analyses the audit data and returns findings, charts, and recommendations.</div>", unsafe_allow_html=True)

        # Example questions
        st.markdown("**Try one of these:**")
        examples = [
            "Which domains have the most overdue entities?",
            "Show me all Critical entities with weak controls",
            "Which entities have the most open issues?",
            "What is the coverage gap across all domains?",
            "Which entities haven't been audited in over 3 years?",
            "Show me Cybersecurity domain risk breakdown",
            "Which management responses are overdue or not started?",
            "What are the top 5 highest risk entities right now?",
        ]
        
        # Session state for example questions
        if "user_question" not in st.session_state:
            st.session_state.user_question = ""
        if "history" not in st.session_state:
            st.session_state.history = []

        cols = st.columns(4)
        for i, ex in enumerate(examples):
            with cols[i % 4]:
                if st.button(ex, key=f"ex_{i}", use_container_width=True):
                    st.session_state.user_question = ex

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

        # Input
        question = st.text_input(
            "Your question:",
            value=st.session_state.user_question,
            placeholder="e.g. Which domains are carrying the most unquantified risk?",
            label_visibility="collapsed"
        )

        # Model badge row + buttons
        col_btn1, col_btn2, col_badge = st.columns([1, 1, 4])
        with col_btn1:
            ask_clicked = st.button("🔍  Ask the Auditor", type="primary", use_container_width=True)
        with col_btn2:
            if st.button("🗑  Clear", use_container_width=True):
                st.session_state.history = []
                st.session_state.user_question = ""
                st.rerun()
        with col_badge:
            st.markdown("""
            <div style="display:flex; align-items:center; gap:8px; padding:6px 0; flex-wrap:wrap;">
              <div style="
                display:inline-flex; align-items:center; gap:6px;
                background:#F0F4FA;
                border:1px solid #D0D8EC;
                border-radius:20px;
                padding:4px 12px;
                font-size:12px; font-weight:600;
                color:#1B3A6B;
                font-family:'Inter',sans-serif;
                letter-spacing:0.2px;
              ">
                <span style="
                  width:7px; height:7px; border-radius:50%;
                  background:linear-gradient(135deg,#D4A843,#B8902A);
                  display:inline-block; flex-shrink:0;
                "></span>
                claude-sonnet-4.x &nbsp;·&nbsp; Anthropic
              </div>
              <div style="
                display:inline-flex; align-items:center; gap:5px;
                background:#EAF7EF;
                border:1px solid #C0E0CF;
                border-radius:20px;
                padding:4px 10px;
                font-size:11.5px; font-weight:600;
                color:#1A7A4A;
                font-family:'Inter',sans-serif;
              ">
                <span style="width:6px;height:6px;border-radius:50%;background:#1A7A4A;display:inline-block;"></span>
                SELECT only · Audit-safe
              </div>
            </div>
            """, unsafe_allow_html=True)

        if ask_clicked and question.strip():
            with st.spinner("Analysing audit universe data..."):
                try:
                    result = ask_agent(question, filtered_df)
                    st.session_state.history.append({"q": question, "r": result})
                    st.session_state.user_question = ""
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        # Display history — most recent first
        for item in reversed(st.session_state.history):
            q = item["q"]
            r = item["r"]

            # Question bubble
            st.markdown(f"<div class='chat-q'>❓  {q}</div>", unsafe_allow_html=True)

            # Answer
            st.markdown(f"""
            <div class='answer-box'>
              <div class='answer-label'>📋 Analysis</div>
              <div class='answer-text'>{r.get('answer', '')}</div>
              <div style="margin-top:12px;padding-top:10px;border-top:1px solid #E8ECF5;display:flex;align-items:center;gap:8px;">
                <div style="display:inline-flex;align-items:center;gap:5px;background:#F0F4FA;border:1px solid #D0D8EC;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;color:#1B3A6B;font-family:'Inter',sans-serif;">
                  <span style="width:6px;height:6px;border-radius:50%;background:linear-gradient(135deg,#D4A843,#B8902A);display:inline-block;"></span>
                  claude-sonnet-4.x · Anthropic
                </div>
                <span style="font-size:11px;color:#AAB4C8;font-family:'Inter',sans-serif;">Generated from IT Audit Universe · 44 entities</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Chart + Table side by side
            col_chart, col_table = st.columns([1.2, 1])

            with col_chart:
                fig = render_chart(r)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

            with col_table:
                table_data = r.get("data_table")
                if table_data:
                    st.markdown("<div style='font-size:0.78rem; font-weight:700; color:#1B3A6B; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;'>📄 DATA</div>", unsafe_allow_html=True)
                    tdf = pd.DataFrame(table_data)
                    st.dataframe(tdf, use_container_width=True, hide_index=True, height=240)

            # Key finding + Recommendation
            col_find, col_rec = st.columns(2)
            with col_find:
                kf = r.get("key_finding", "")
                if kf:
                    st.info(f"**🎯 Key Finding:** {kf}")
            with col_rec:
                rec = r.get("recommendation", "")
                if rec:
                    st.warning(f"**⚡ Recommendation:** {rec}")

            st.divider()

    # ── TAB 2: POWER BI ────────────────────────────────────────────────────
    with tab2:
        st.markdown("### IT Audit Universe — Power BI Dashboard")
        st.markdown("<div style='color:#888; font-size:0.9rem; margin-bottom:20px;'>Interactive dashboard with domain heatmap, risk scoring, coverage gap analysis, and overdue entity tracking. Use AI queries above to complement the visual analytics.</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class='powerbi-section'>
          <iframe
            title="IT Audit Universe Dashboard"
            width="100%"
            height="620"
            src="https://app.powerbi.com/view?r=eyJrIjoiMjQ1NDA3M2EtMTBjOC00YWJkLWIzZjktZGMzZjRhYjdjNWQzIiwidCI6IjMyMWIxNDA4LTIxZjAtNDE0My1hMzkwLTNiNjIwMmU2NWUxZiJ9"
            frameborder="0"
            allowFullScreen="true"
            style="border-radius:8px;">
          </iframe>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='margin-top:16px; padding:16px; background:#EEF1F7; border-radius:10px; font-size:0.85rem; color:#555;'>
          💡 <strong>How to use both tools together:</strong> Use the Power BI dashboard for visual exploration — filter by domain, drill into priorities, track coverage gaps.
          Then switch to the <strong>Ask the Auditor</strong> tab to ask specific questions about what you see.
          The AI layer and the visual layer are built on the same dataset.
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 3: DATA TABLE ──────────────────────────────────────────────────
    with tab3:
        st.markdown("### Audit Universe Dataset")
        st.markdown(f"<div style='color:#888; font-size:0.9rem; margin-bottom:16px;'>Showing {len(filtered_df)} of 44 entities · {selected_domain}</div>", unsafe_allow_html=True)

        # Filter controls
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            priority_filter = st.multiselect("Priority", ["Critical","High","Medium","Low"],
                                              default=["Critical","High","Medium","Low"])
        with col_f2:
            control_filter = st.multiselect("Control Effectiveness",
                                             ["Strong","Adequate","Weak","Not Tested"],
                                             default=["Strong","Adequate","Weak","Not Tested"])
        with col_f3:
            overdue_filter = st.selectbox("Overdue Flag", ["All","Yes","No"])

        display_df = filtered_df[
            (filtered_df['Audit_Priority'].isin(priority_filter)) &
            (filtered_df['Control_Effectiveness'].isin(control_filter))
        ]
        if overdue_filter != "All":
            display_df = display_df[display_df['Overdue_Flag'] == overdue_filter]

        # Colour the priority column
        def colour_priority(val):
            colours = {
                'Critical': 'background-color:#FDEDEC; color:#C0392B; font-weight:700',
                'High': 'background-color:#FEF9E7; color:#E67E22; font-weight:700',
                'Medium': 'background-color:#FFFDE7; color:#F39C12; font-weight:600',
                'Low': 'background-color:#EAFAF1; color:#1A5C38; font-weight:600'
            }
            return colours.get(val, '')

        styled = display_df.style.applymap(colour_priority, subset=['Audit_Priority'])
        st.dataframe(styled, use_container_width=True, hide_index=True, height=500)

        # Download
        buffer = io.BytesIO()
        display_df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        st.download_button(
            "⬇️  Download filtered data",
            data=buffer,
            file_name=f"audit_universe_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
