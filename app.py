import streamlit as st
import pandas as pd
import plotly.express as px
import anthropic
import json
import io
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AskMyAuditor · AI Audit Analytics Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── STYLES — matching the HTML design exactly ─────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@600;700&display=swap');

  html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif !important;
    background: #F5F6F8 !important;
  }

  /* Hide Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }
  div[data-testid="stToolbar"] { display: none; }
  div[data-testid="stDecoration"] { display: none; }
  div[data-testid="stStatusWidget"] { display: none; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #0D1F3C !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    min-width: 240px !important; max-width: 240px !important;
  }
  section[data-testid="stSidebar"] > div {
    padding: 0 !important; background: #0D1F3C !important;
  }
  section[data-testid="stSidebar"] label { color: rgba(255,255,255,0.4) !important; font-size: 10px !important; font-weight: 700 !important; letter-spacing: 1px !important; text-transform: uppercase !important; }
  section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.12) !important;
    color: rgba(255,255,255,0.8) !important;
    border-radius: 8px !important;
  }
  section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.06) !important; }
  section[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important; padding: 10px 12px !important;
  }
  section[data-testid="stSidebar"] [data-testid="stMetric"] label {
    color: rgba(255,255,255,0.4) !important; font-size: 10px !important;
    font-weight: 700 !important; letter-spacing: 0.8px !important; text-transform: uppercase !important;
  }
  section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #D4A843 !important; font-family: 'DM Mono', monospace !important;
    font-size: 20px !important; font-weight: 700 !important;
  }

  /* Main content */
  .main .block-container {
    padding: 20px 24px !important; max-width: 100% !important; background: #F5F6F8 !important;
  }

  /* Tabs */
  div[data-testid="stTabs"] > div:first-child {
    background: #FFFFFF; border-bottom: 1px solid rgba(13,31,60,0.1);
    border-radius: 10px 10px 0 0; padding: 0 4px; gap: 2px;
  }
  button[data-baseweb="tab"] {
    background: transparent !important; border: none !important;
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important; font-weight: 500 !important;
    color: #5A6A85 !important; padding: 10px 16px !important;
    margin: 4px 2px !important; transition: all 0.15s !important;
  }
  button[data-baseweb="tab"]:hover { background: #F5F6F8 !important; color: #0D1F3C !important; }
  button[data-baseweb="tab"][aria-selected="true"] {
    background: #0D1F3C !important; color: #FFFFFF !important; font-weight: 600 !important;
  }
  div[data-testid="stTabs"] > div:last-child {
    background: #FFFFFF; border: 1px solid rgba(13,31,60,0.1);
    border-top: none; border-radius: 0 0 10px 10px;
    padding: 20px 22px; box-shadow: 0 1px 8px rgba(13,31,60,0.06);
  }

  /* Buttons */
  div[data-testid="stButton"] button[kind="primary"] {
    background: #0D1F3C !important; color: #FFFFFF !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important; font-weight: 600 !important;
  }
  div[data-testid="stButton"] button[kind="primary"]:hover { background: #1E3A63 !important; }
  div[data-testid="stButton"] button {
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important; font-weight: 500 !important;
    border: 1px solid rgba(13,31,60,0.12) !important;
    background: #FFFFFF !important; color: #0D1F3C !important;
    padding: 6px 12px !important; transition: all 0.15s !important;
  }
  div[data-testid="stButton"] button:hover { background: #EEF1F7 !important; border-color: #0D1F3C !important; }

  /* Link button */
  div[data-testid="stLinkButton"] a {
    background: #0D1F3C !important; color: #FFFFFF !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important; font-weight: 600 !important;
    padding: 8px 14px !important;
  }

  /* Text input */
  div[data-testid="stTextInput"] input {
    background: #FFFFFF !important; border: 1.5px solid rgba(13,31,60,0.15) !important;
    border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important; color: #0D1F3C !important; padding: 10px 16px !important;
  }
  div[data-testid="stTextInput"] input:focus {
    border-color: #0D1F3C !important; box-shadow: 0 0 0 3px rgba(13,31,60,0.08) !important;
  }
  div[data-testid="stTextInput"] input::placeholder { color: #8A9AB5 !important; }

  /* Multiselect & selectbox */
  div[data-testid="stMultiSelect"] > div, div[data-testid="stSelectbox"] > div {
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
  }

  /* Dataframe */
  div[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden !important; border: 1px solid rgba(13,31,60,0.1) !important; }

  /* Download button */
  div[data-testid="stDownloadButton"] button {
    background: #0D1F3C !important; color: #FFFFFF !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
  }

  /* Divider */
  hr { border-color: rgba(13,31,60,0.08) !important; }

  /* Animations */
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  /* ── Custom Components ── */
  .brand-block {
    padding: 22px 20px 18px; border-bottom: 1px solid rgba(255,255,255,0.06);
  }
  .brand-icon {
    width: 34px; height: 34px; background: #D4A843; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; margin-bottom: 10px;
  }
  .brand-name {
    font-family: 'Playfair Display', serif; font-size: 15px; font-weight: 700;
    color: #FFFFFF; letter-spacing: -0.2px; line-height: 1.2;
  }
  .brand-sub { font-size: 11px; color: rgba(255,255,255,0.4); margin-top: 3px; }
  .nav-label {
    font-size: 9px; font-weight: 700; letter-spacing: 1.5px;
    color: rgba(255,255,255,0.3); padding: 12px 20px 6px; text-transform: uppercase;
  }
  .about-block {
    margin: 8px 14px 12px; padding: 12px 14px;
    background: rgba(255,255,255,0.05); border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.07);
  }
  .about-title {
    font-size: 9px; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; color: rgba(255,255,255,0.3); margin-bottom: 7px;
  }
  .about-text { font-size: 11.5px; color: rgba(255,255,255,0.5); line-height: 1.65; }
  .about-check {
    display: flex; align-items: center; gap: 6px;
    font-size: 10.5px; color: rgba(255,255,255,0.4); margin-top: 4px;
  }
  .analyst-wrap {
    padding: 12px 20px; border-top: 1px solid rgba(255,255,255,0.06);
  }

  /* Agent banner */
  .agent-banner {
    background: linear-gradient(90deg, #0D1F3C 0%, #152B4E 100%);
    border-radius: 12px; padding: 12px 18px;
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 18px; border: 1px solid rgba(255,255,255,0.06);
  }
  .agent-icon {
    width: 32px; height: 32px; background: #D4A843; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
  }
  .agent-title { font-size: 13px; font-weight: 700; color: #FFFFFF; }
  .agent-sub { font-size: 11px; color: rgba(255,255,255,0.5); margin-top: 2px; }
  .live-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(26,122,74,0.2); color: #4ADE80;
    font-size: 10px; font-weight: 700; letter-spacing: 0.8px;
    padding: 4px 10px; border-radius: 20px; margin-left: auto;
  }
  .live-dot { width: 6px; height: 6px; background: #4ADE80; border-radius: 50%; animation: pulse 2s infinite; }

  /* Chips */
  .suggest-label {
    font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; color: #8A9AB5; margin-bottom: 8px;
  }

  /* Chat */
  .msg-user { display: flex; justify-content: flex-end; margin: 10px 0; }
  .bubble-user {
    max-width: 80%; background: #0D1F3C; color: #FFFFFF;
    padding: 11px 15px; border-radius: 14px 14px 4px 14px;
    font-size: 13.5px; line-height: 1.6;
    box-shadow: 0 4px 14px rgba(13,31,60,0.2);
  }

  /* Answer card */
  .answer-card {
    background: #FFFFFF; border: 1px solid rgba(13,31,60,0.1);
    border-left: 4px solid #0D1F3C; border-radius: 4px 12px 12px 12px;
    padding: 16px 20px; margin: 10px 0;
    box-shadow: 0 1px 6px rgba(13,31,60,0.06);
  }
  .ai-label {
    font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; color: #D4A843; margin-bottom: 10px;
    display: flex; align-items: center; gap: 8px;
  }
  .ai-label-line { flex: 1; height: 1px; background: rgba(13,31,60,0.08); }
  .answer-text { font-size: 14px; color: #0D1F3C; line-height: 1.75; }
  .answer-footer {
    margin-top: 10px; padding-top: 10px;
    border-top: 1px solid rgba(13,31,60,0.07);
    display: flex; align-items: center; gap: 8px;
  }
  .model-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #F0F4FA; border: 1px solid #D0D8EC;
    border-radius: 20px; padding: 3px 10px;
    font-size: 11px; font-weight: 600; color: #0D1F3C;
    font-family: 'DM Mono', monospace;
  }
  .model-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: linear-gradient(135deg,#D4A843,#B8902A); display: inline-block;
  }
  .safe-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #EAF7EF; border: 1px solid #C0E0CF;
    border-radius: 20px; padding: 3px 10px;
    font-size: 11px; font-weight: 600; color: #1A7A4A;
  }
  .answer-meta { font-size: 11px; color: #AAB4C8; margin-left: 4px; }

  /* Finding / Rec cards */
  .find-card {
    background: #EEF1F7; border-left: 4px solid #0D1F3C;
    border-radius: 4px 8px 8px 4px; padding: 12px 16px; margin: 6px 0;
  }
  .find-label { font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: #0D1F3C; margin-bottom: 5px; }
  .find-text { font-size: 13px; color: #2A3A55; line-height: 1.6; }
  .rec-card {
    background: linear-gradient(135deg, #FFF8E1, #FFFBF0);
    border: 1px solid rgba(212,168,67,0.25); border-left: 4px solid #D4A843;
    border-radius: 4px 10px 10px 10px; padding: 12px 16px; margin: 6px 0;
  }
  .rec-label { font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: #9A7010; margin-bottom: 5px; }
  .rec-text { font-size: 13px; color: #333; line-height: 1.65; }

  /* Section headers */
  .section-title {
    font-family: 'Playfair Display', serif; font-size: 20px; font-weight: 700;
    color: #0D1F3C; letter-spacing: -0.3px; margin-bottom: 4px;
  }
  .section-sub { font-size: 12.5px; color: #5A6A85; margin-bottom: 14px; }

  /* PowerBI */
  .pbi-frame {
    background: #FFFFFF; border: 1px solid rgba(13,31,60,0.1);
    border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(13,31,60,0.08);
  }
  .pbi-header {
    padding: 10px 16px; border-bottom: 1px solid rgba(13,31,60,0.08);
    display: flex; align-items: center; gap: 10px; background: #FFFFFF;
  }
  .pbi-logo {
    background: #F2C811; border-radius: 3px; padding: 2px 5px;
    font-size: 10px; font-weight: 900; color: #1b1b1b; font-family: 'DM Mono', monospace;
  }
  .pbi-title { font-size: 12.5px; font-weight: 600; color: #0D1F3C; }
  .embedded-pill {
    margin-left: auto; display: flex; align-items: center; gap: 5px;
    background: #EAF7EF; color: #1A7A4A; font-size: 10px; font-weight: 700;
    letter-spacing: 0.8px; padding: 3px 10px; border-radius: 20px;
  }
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel('IT_Audit_Universe.xlsx')
    df['Last_Audit_Date'] = pd.to_datetime(df['Last_Audit_Date'])
    return df

# ── AI AGENT ──────────────────────────────────────────────────────────────────
def build_prompt(df):
    return (
        "DATASET: IT Audit Universe — 44 auditable entities across 5 technology domains.\n\n"
        "COLUMNS: Audit_Entity(text), Domain(text: Cybersecurity|Cloud & Infrastructure|Data Governance|IT Governance|Compliance & Regulatory), "
        "Inherent_Risk_Score(1-5), Control_Effectiveness(Strong|Adequate|Weak|Not Tested), Last_Audit_Date(date), "
        "Months_Since_Last_Audit(int), Residual_Risk_Score(1-5), Audit_Priority(Critical|High|Medium|Low), "
        "Recommended_Audit_Cycle(Annual|Biennial|Risk-Based), Regulatory_Relevance(High|Medium|Low), "
        "Open_Issues(int), Management_Response_Status(On Track|Overdue|Not Started), Overdue_Flag(Yes|No)\n\n"
        f"KEY STATS: 44 total | {len(df[df['Audit_Priority']=='Critical'])} Critical | "
        f"{len(df[df['Overdue_Flag']=='Yes'])} Overdue | {df['Open_Issues'].sum()} Open Issues\n\n"
        "FULL DATASET (JSON):\n" + df.to_json(orient='records', date_format='iso') + "\n\n"
        "YOUR ROLE: Expert Technology Audit Analytics AI Agent. Respond with the precision of a senior auditor.\n\n"
        'RESPONSE FORMAT — return ONLY valid JSON, no markdown fences:\n'
        '{"answer":"2-4 sentence analysis with specific numbers",'
        '"key_finding":"single most important takeaway",'
        '"recommendation":"one actionable audit recommendation",'
        '"chart_type":"bar|horizontal_bar|pie|none",'
        '"chart_data":{"x":[],"y":[],"color":[],"title":"","x_label":"","y_label":""},'
        '"data_table":[{"Column":"Value"}]}\n\n'
        "RULES: Never fabricate data. Colors: Critical=#C0392B, High=#E67E22, Medium=#F39C12, Low=#1A5C38, default=#1B3A6B."
    )

def ask_agent(question, df):
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=build_prompt(df),
        messages=[{"role": "user", "content": question}]
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip())

def render_chart(r):
    ct = r.get("chart_type","none")
    cd = r.get("chart_data")
    if ct == "none" or not cd: return None
    x, y = cd.get("x",[]), cd.get("y",[])
    colors = cd.get("color",["#1B3A6B"]*len(x))
    title, xl, yl = cd.get("title",""), cd.get("x_label",""), cd.get("y_label","")
    if ct == "bar":
        fig = px.bar(x=x, y=y, title=title, labels={"x":xl,"y":yl})
        fig.update_traces(marker_color=colors)
    elif ct == "horizontal_bar":
        fig = px.bar(x=y, y=x, title=title, labels={"x":yl,"y":xl}, orientation='h')
        fig.update_traces(marker_color=colors)
    elif ct == "pie":
        fig = px.pie(names=x, values=y, title=title, color_discrete_sequence=colors)
    else:
        return None
    fig.update_layout(
        font_family="DM Sans", title_font_size=14, title_font_color="#0D1F3C",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=44,b=32,l=32,r=16), showlegend=False,
        xaxis=dict(gridcolor="#F0F0F0"), yaxis=dict(gridcolor="#F0F0F0")
    )
    return fig

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def render_sidebar(df):
    with st.sidebar:
        st.markdown("""
        <div class='brand-block'>
          <div class='brand-icon'>🔍</div>
          <div class='brand-name'>AskMyAuditor</div>
          <div class='brand-sub'>AI Audit Analytics Agent</div>
        </div>
        <div class='nav-label'>Universe Snapshot</div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Entities", "44")
            st.metric("Critical", len(df[df['Audit_Priority']=='Critical']))
        with c2:
            st.metric("Overdue", len(df[df['Overdue_Flag']=='Yes']))
            st.metric("Issues", int(df['Open_Issues'].sum()))

        st.divider()
        st.markdown("<div class='nav-label'>Filter Domain</div>", unsafe_allow_html=True)
        domains = ["All Domains"] + sorted(df['Domain'].unique().tolist())
        selected = st.selectbox("", domains, label_visibility="collapsed")
        st.divider()

        st.markdown("""
        <div class='about-block'>
          <div class='about-title'>About This Tool</div>
          <div class='about-text'><b style='color:rgba(255,255,255,0.75)'>AskMyAuditor</b> is an AI agent built on a real IT Audit Universe — 44 entities · 5 domains · risk scored.</div>
          <div class='about-check'><span style='color:#D4A843'>✓</span> Natural language to audit insight</div>
          <div class='about-check'><span style='color:#D4A843'>✓</span> Powered by Claude · Anthropic</div>
          <div class='about-check'><span style='color:#D4A843'>✓</span> SELECT only · Audit-safe queries</div>
          <div class='about-check'><span style='color:#D4A843'>✓</span> Power BI dashboard embedded</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("""
        <div class='analyst-wrap'>
          <div style='display:flex;align-items:center;gap:10px;'>
            <div style='width:30px;height:30px;background:linear-gradient(135deg,#D4A843,#B8902A);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#0D1F3C;flex-shrink:0;'>SB</div>
            <div>
              <div style='font-size:12.5px;font-weight:600;color:#FFFFFF;'>Swarleen Bhamra</div>
              <div style='font-size:10.5px;color:rgba(255,255,255,0.4);margin-top:1px;'>Data Analyst · Power BI · AI</div>
            </div>
          </div>
          <div style='display:flex;gap:8px;margin-top:8px;'>
            <a href='https://www.swarleen.com' target='_blank' style='color:rgba(255,255,255,0.35);font-size:10.5px;text-decoration:none;'>swarleen.com</a>
            <span style='color:rgba(255,255,255,0.15)'>·</span>
            <a href='https://www.linkedin.com/in/swarleenbhamra/' target='_blank' style='color:rgba(255,255,255,0.35);font-size:10.5px;text-decoration:none;'>LinkedIn</a>
            <span style='color:rgba(255,255,255,0.15)'>·</span>
            <a href='https://github.com/Swarleen' target='_blank' style='color:rgba(255,255,255,0.35);font-size:10.5px;text-decoration:none;'>GitHub</a>
          </div>
        </div>
        """, unsafe_allow_html=True)

        return selected

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    df = load_data()
    selected_domain = render_sidebar(df)
    filtered_df = df if selected_domain == "All Domains" else df[df['Domain'] == selected_domain]

    # Banner
    st.markdown("""
    <div class='agent-banner'>
      <div class='agent-icon'>🔍</div>
      <div>
        <div class='agent-title'>AskMyAuditor — AI Audit Analytics Agent</div>
        <div class='agent-sub'>Ask anything in plain English · 44 auditable entities · 5 technology domains · Powered by Claude AI</div>
      </div>
      <div class='live-pill'><div class='live-dot'></div> LIVE</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🤖  AI Workspace", "📊  Power BI Dashboard", "📋  Audit Universe"])

    # ── TAB 1 ─────────────────────────────────────────────────────────────
    with tab1:
        st.markdown("<div class='suggest-label'>Suggested Analytics — click to try</div>", unsafe_allow_html=True)

        examples = [
            "Which domains have the most overdue entities?",
            "Show me all Critical entities with weak controls",
            "Which entities have the most open issues?",
            "What are the top 5 highest risk entities?",
            "Which management responses are overdue or not started?",
            "What is the coverage gap across all domains?",
            "Entities not audited in over 3 years?",
            "Cybersecurity domain risk breakdown",
        ]

        if "user_question" not in st.session_state: st.session_state.user_question = ""
        if "history" not in st.session_state: st.session_state.history = []

        cols = st.columns(4)
        for i, ex in enumerate(examples):
            with cols[i % 4]:
                if st.button(ex, key=f"ex_{i}", use_container_width=True):
                    st.session_state.user_question = ex

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        question = st.text_input(
            "question", value=st.session_state.user_question,
            placeholder="Ask anything about the audit universe in plain English...",
            label_visibility="collapsed"
        )

        col_ask, col_clear, col_badge = st.columns([1.2, 0.8, 4])
        with col_ask:
            ask_clicked = st.button("🔍  Ask the Auditor", type="primary", use_container_width=True)
        with col_clear:
            if st.button("🗑  Clear", use_container_width=True):
                st.session_state.history = []
                st.session_state.user_question = ""
                st.rerun()
        with col_badge:
            st.markdown("""
            <div style="display:flex;align-items:center;gap:8px;padding:6px 0;">
              <div class='model-pill'><span class='model-dot'></span>claude-sonnet-4.x &nbsp;·&nbsp; Anthropic</div>
              <div class='safe-pill'><span style='width:5px;height:5px;border-radius:50%;background:#1A7A4A;display:inline-block;'></span>SELECT only · Audit-safe</div>
            </div>
            """, unsafe_allow_html=True)

        if ask_clicked and question.strip():
            with st.spinner("Analysing audit universe data..."):
                try:
                    result = ask_agent(question, filtered_df)
                    st.session_state.history.append({"q": question, "r": result})
                    st.session_state.user_question = ""
                except Exception as e:
                    st.error(f"Analysis error: {str(e)}")

        for item in reversed(st.session_state.history):
            q, r = item["q"], item["r"]

            st.markdown(f"<div class='msg-user'><div class='bubble-user'>❓&nbsp; {q}</div></div>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class='answer-card'>
              <div class='ai-label'>🤖 AskMyAuditor<div class='ai-label-line'></div>
                <span style='font-size:9px;color:#8A9AB5;font-weight:500;'>AI Audit Analytics Agent</span>
              </div>
              <div class='answer-text'>{r.get('answer','')}</div>
              <div class='answer-footer'>
                <div class='model-pill'><span class='model-dot'></span>claude-sonnet-4.x · Anthropic</div>
                <span class='answer-meta'>Generated from IT Audit Universe · 44 entities</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            col_chart, col_table = st.columns([1.3, 1])
            with col_chart:
                fig = render_chart(r)
                if fig: st.plotly_chart(fig, use_container_width=True)
            with col_table:
                td = r.get("data_table")
                if td:
                    st.markdown("<div style='font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#5A6A85;margin-bottom:6px;'>📄 Data</div>", unsafe_allow_html=True)
                    st.dataframe(pd.DataFrame(td), use_container_width=True, hide_index=True, height=220)

            kf, rec = r.get("key_finding",""), r.get("recommendation","")
            if kf or rec:
                cf, cr = st.columns(2)
                with cf:
                    if kf: st.markdown(f"<div class='find-card'><div class='find-label'>🎯 Key Finding</div><div class='find-text'>{kf}</div></div>", unsafe_allow_html=True)
                with cr:
                    if rec: st.markdown(f"<div class='rec-card'><div class='rec-label'>⚡ Recommendation</div><div class='rec-text'>{rec}</div></div>", unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

    # ── TAB 2 ─────────────────────────────────────────────────────────────
    with tab2:
        st.markdown("<div class='section-title'>IT Audit Universe Dashboard</div><div class='section-sub'>Power BI · Risk scoring · Coverage gap · Domain heatmap · Overdue tracking</div>", unsafe_allow_html=True)

        _, col_btn = st.columns([5, 1])
        with col_btn:
            st.link_button("↗ Full Screen",
                "https://app.powerbi.com/view?r=eyJrIjoiMjQ1NDA3M2EtMTBjOC00YWJkLWIzZjktZGMzZjRhYjdjNWQzIiwidCI6IjMyMWIxNDA4LTIxZjAtNDE0My1hMzkwLTNiNjIwMmU2NWUxZiJ9",
                use_container_width=True)

        st.markdown("""
        <div class='pbi-frame'>
          <div class='pbi-header'>
            <div class='pbi-logo'>PBI</div>
            <div class='pbi-title'>IT Audit Universe · Risk-Based Planning Dashboard</div>
            <div class='embedded-pill'><div style='width:6px;height:6px;background:#1A7A4A;border-radius:50%;animation:pulse 2s infinite;'></div> EMBEDDED</div>
          </div>
          <iframe src="https://app.powerbi.com/view?r=eyJrIjoiMjQ1NDA3M2EtMTBjOC00YWJkLWIzZjktZGMzZjRhYjdjNWQzIiwidCI6IjMyMWIxNDA4LTIxZjAtNDE0My1hMzkwLTNiNjIwMmU2NWUxZiJ9"
            width="100%" height="600" frameborder="0" allowfullscreen="true" style="display:block;"></iframe>
        </div>
        <div style='margin-top:12px;padding:12px 16px;background:#EEF1F7;border-radius:8px;font-size:13px;color:#5A6A85;border-left:3px solid #0D1F3C;'>
          💡 Use Power BI for visual exploration, then switch to <strong>AI Workspace</strong> to ask specific questions. Both use the same dataset.
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 3 ─────────────────────────────────────────────────────────────
    with tab3:
        st.markdown(f"<div class='section-title'>Audit Universe Explorer</div><div class='section-sub'>44 entities · 5 domains · {selected_domain}</div>", unsafe_allow_html=True)

        cf1, cf2, cf3 = st.columns(3)
        with cf1: pf = st.multiselect("Priority", ["Critical","High","Medium","Low"], default=["Critical","High","Medium","Low"])
        with cf2: ctrl = st.multiselect("Control", ["Strong","Adequate","Weak","Not Tested"], default=["Strong","Adequate","Weak","Not Tested"])
        with cf3: ovr = st.selectbox("Overdue", ["All","Yes","No"])

        disp = filtered_df[filtered_df['Audit_Priority'].isin(pf) & filtered_df['Control_Effectiveness'].isin(ctrl)]
        if ovr != "All": disp = disp[disp['Overdue_Flag'] == ovr]

        def col_priority(val):
            return {'Critical':'background-color:#FDEDEC;color:#C0392B;font-weight:700','High':'background-color:#FEF9E7;color:#E67E22;font-weight:700','Medium':'background-color:#FFFDE7;color:#F39C12;font-weight:600','Low':'background-color:#EAFAF1;color:#1A5C38;font-weight:600'}.get(val,'')

        st.dataframe(disp.style.applymap(col_priority, subset=['Audit_Priority']), use_container_width=True, hide_index=True, height=520)
        st.markdown(f"<div style='font-size:11.5px;color:#8A9AB5;text-align:right;margin-top:6px;'>Showing {len(disp)} of 44 entities</div>", unsafe_allow_html=True)

        buf = io.BytesIO()
        disp.to_excel(buf, index=False, engine='openpyxl')
        buf.seek(0)
        st.download_button("⬇️  Download filtered data", data=buf,
            file_name=f"audit_universe_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()
