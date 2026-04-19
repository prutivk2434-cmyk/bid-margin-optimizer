import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Bid Margin Optimizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS — Midnight Finance Theme ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #070b14 !important; }

/* ── Hide streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1rem !important; padding-left: 1rem !important; padding-right: 1rem !important; max-width: 100% !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: #0d1117 !important;
  border-right: 1px solid #1a2332 !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ── Sidebar content ── */
.sidebar-logo {
  padding: 24px 20px 20px;
  border-bottom: 1px solid #1a2332;
  margin-bottom: 8px;
}
.sidebar-logo-icon {
  width: 44px; height: 44px;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  border-radius: 12px;
  display: flex; align-items: center;
  justify-content: center; font-size: 20px;
  margin-bottom: 10px;
}
.sidebar-title { color: #f1f5f9; font-size: 15px; font-weight: 700; margin-bottom: 2px; }
.sidebar-sub   { color: #475569; font-size: 11px; }

.sidebar-section { padding: 16px 20px; border-bottom: 1px solid #1a2332; }
.sidebar-section-title {
  color: #475569; font-size: 9px; font-weight: 700;
  letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 12px;
}
.sidebar-stat {
  display: flex; align-items: center;
  justify-content: space-between; margin-bottom: 10px;
}
.sidebar-stat-label { color: #64748b; font-size: 12px; }
.sidebar-stat-value { color: #f1f5f9; font-size: 13px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }

/* ── Main area ── */
.main-content { padding: 8px 4px; }

/* ── Page title ── */
.page-title {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #1a2332;
  display: flex; align-items: center; justify-content: space-between;
}
.page-title-text { color: #f1f5f9; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; }
.page-title-sub  { color: #475569; font-size: 13px; margin-top: 4px; }
.live-badge {
  background: #052e16; border: 1px solid #166534;
  color: #4ade80; padding: 6px 14px; border-radius: 99px;
  font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 6px;
}

/* ── Metric cards ── */
.metrics-grid {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 14px; margin-bottom: 24px;
}
.metric-card {
  background: #0d1117;
  border: 1px solid #1a2332;
  border-radius: 16px;
  padding: 20px 22px;
  position: relative; overflow: hidden;
}
.metric-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 3px; border-radius: 16px 16px 0 0;
}
.metric-card.blue::before   { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
.metric-card.green::before  { background: linear-gradient(90deg, #22c55e, #84cc16); }
.metric-card.red::before    { background: linear-gradient(90deg, #ef4444, #f97316); }
.metric-card.amber::before  { background: linear-gradient(90deg, #f59e0b, #eab308); }

.metric-label { font-size: 10px; font-weight: 600; color: #475569; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 10px; }
.metric-value { font-size: 28px; font-weight: 800; font-family: 'JetBrains Mono', monospace; margin-bottom: 6px; letter-spacing: -0.5px; }
.metric-sub   { font-size: 11px; color: #334155; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: #0d1117 !important;
  border-bottom: 1px solid #1a2332 !important;
  gap: 0 !important; padding: 0 !important;
  border-radius: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: #475569 !important;
  font-size: 13px !important; font-weight: 500 !important;
  padding: 14px 24px !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
  background: transparent !important;
  color: #3b82f6 !important;
  border-bottom: 2px solid #3b82f6 !important;
}
.stTabs [data-baseweb="tab-panel"] {
  background: transparent !important;
  padding: 20px 0 0 !important;
}

/* ── Search & filters ── */
.filter-bar {
  background: #0d1117; border: 1px solid #1a2332;
  border-radius: 12px; padding: 16px 20px;
  margin-bottom: 16px;
  display: flex; gap: 12px; align-items: center; flex-wrap: wrap;
}
.stTextInput input {
  background: #070b14 !important;
  border: 1px solid #1a2332 !important;
  color: #f1f5f9 !important;
  border-radius: 8px !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 13px !important;
}
.stTextInput input:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 3px #3b82f620 !important; }
.stSelectbox > div > div {
  background: #070b14 !important;
  border: 1px solid #1a2332 !important;
  color: #f1f5f9 !important;
  border-radius: 8px !important;
}
label { color: #475569 !important; font-size: 12px !important; }

/* ── Table ── */
.table-wrap {
  background: #0d1117; border: 1px solid #1a2332;
  border-radius: 16px; overflow: hidden;
}
.table-head-bar {
  padding: 16px 22px; border-bottom: 1px solid #1a2332;
  display: flex; align-items: center; justify-content: space-between;
}
.table-head-title { color: #f1f5f9; font-size: 14px; font-weight: 700; }
.table-head-sub   { color: #475569; font-size: 12px; margin-left: 10px; }
.count-badge {
  background: #1a2332; color: #64748b;
  padding: 4px 12px; border-radius: 99px;
  font-size: 11px; font-weight: 600;
}

table.dtable { width: 100%; border-collapse: collapse; font-size: 12px; }
table.dtable th {
  padding: 11px 16px; text-align: left;
  font-size: 10px; font-weight: 700; color: #f1f5f9;
  letter-spacing: 0.08em; text-transform: uppercase;
  border-bottom: 1px solid #1a2332; background: #070b14;
  white-space: nowrap;
}
table.dtable td {
  padding: 12px 16px; color: #f1f5f9;
  border-bottom: 1px solid #0d1117;
  font-family: 'Inter', sans-serif;
}
table.dtable tr:nth-child(odd)  td { background: #0d1117; }
table.dtable tr:nth-child(even) td { background: #0a0f1a; }
table.dtable tr:hover td { background: #111827 !important; }

.fico-pill {
  padding: 3px 11px; border-radius: 6px;
  font-size: 12px; font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  display: inline-block;
}
.status-badge {
  padding: 3px 12px; border-radius: 99px;
  font-size: 11px; font-weight: 600; display: inline-block;
}

/* ── Download button ── */
.stDownloadButton button {
  background: linear-gradient(135deg, #3b82f6, #06b6d4) !important;
  color: white !important; border: none !important;
  border-radius: 10px !important; font-weight: 700 !important;
  font-size: 13px !important; padding: 12px 28px !important;
  width: 100% !important; transition: all .2s !important;
}
.stDownloadButton button:hover { opacity: 0.85 !important; }

/* ── Upload area ── */
[data-testid="stFileUploader"] {
  background: #0d1117 !important;
  border: 2px dashed #1a2332 !important;
  border-radius: 16px !important; padding: 20px !important;
}
[data-testid="stFileUploaderDropzone"] {
  background: transparent !important;
  border: none !important;
}
[data-testid="stFileUploaderDropzone"] p { color: #475569 !important; }

/* ── Slider ── */
.stSlider > div > div > div { background: #3b82f6 !important; }

/* ── Plotly chart bg ── */
.js-plotly-plot { border-radius: 12px; overflow: hidden; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #1a2332; border-radius: 99px; }
</style>
""", unsafe_allow_html=True)

# ── Bucket definitions ────────────────────────────────────────
FICO_BUCKETS = [
    ("451-500",451,500),("501-550",501,550),("551-600",551,600),
    ("601-650",601,650),("651-700",651,700),("701-750",701,750),
    ("751-800",751,800),("801-850",801,850),
]
RATE_BUCKETS = [
    (1,3.750,4.188),(2,4.188,4.626),(3,4.626,5.064),(4,5.064,5.502),
    (5,5.502,5.940),(6,5.940,6.378),(7,6.378,6.816),(8,6.816,7.254),
    (9,7.254,7.632),(10,7.632,8.130),
]
AMOUNT_BUCKETS = [
    (1,0,141533),(2,141534,169400),(3,169401,189900),(4,189901,205000),
    (5,205001,221906),(6,221907,235000),(7,235001,248224),(8,248225,261000),
    (9,261001,275000),(10,275001,289720),(11,289721,305000),(12,305001,320716),
    (13,320717,344000),(14,344001,372991),(15,372992,403000),(16,403001,437525),
    (17,437526,483117),(18,483118,545000),(19,545001,672000),(20,672001,2200000),
]

def get_fico_bucket(fico):
    for label,lo,hi in FICO_BUCKETS:
        if lo<=fico<=hi: return label
    return "Unknown"

def get_rate_bucket(rate):
    for bn,lo,hi in RATE_BUCKETS:
        if lo<=rate<=hi: return bn
    return -1

def get_amount_bucket(amount):
    for bn,lo,hi in AMOUNT_BUCKETS:
        if lo<=amount<=hi: return bn
    return -1

def assign_buckets(df):
    df=df.copy()
    def safe_col(d,cols):
        for c in cols:
            if c in d.columns: return d[c]
        return pd.Series(0,index=d.index,dtype=str)
    df["_fico"]  =pd.to_numeric(safe_col(df,["FICO","fico"]),errors="coerce").fillna(0)
    df["_rate"]  =pd.to_numeric(safe_col(df,["NoteRate","Note Rate"]),errors="coerce").fillna(0)
    df["_amount"]=pd.to_numeric(safe_col(df,["LoanAmount","Loan Amount"]),errors="coerce").fillna(0)
    df["FicoBucket"]  =df["_fico"].apply(get_fico_bucket)
    df["RateBucket"]  =df["_rate"].apply(get_rate_bucket)
    df["AmountBucket"]=df["_amount"].apply(get_amount_bucket)
    df["BucketKey"]=(df["FicoBucket"].astype(str)+" | Rate-"+
                     df["RateBucket"].astype(str)+" | Amt-"+
                     df["AmountBucket"].astype(str))
    return df

def calibrate_margins(df):
    aim_col=next((c for c in ["All in Margin","AllInMargin","all_in_margin","All In Margin"] if c in df.columns),None)
    if aim_col is None: return {},None
    df=df.copy()
    df["_aim"]=pd.to_numeric(df[aim_col],errors="coerce")
    color_col=next((c for c in ["Final_Color","FinalColor","Final Color","final_color"] if c in df.columns),None)
    bucket_stats=[]
    for bk,grp in df.groupby("BucketKey"):
        margins=grp["_aim"].dropna()
        if len(margins)==0: continue
        s={"BucketKey":bk,"LoanCount":len(grp),
           "AvgMargin":round(margins.mean(),4),"MedianMargin":round(margins.median(),4),
           "P25Margin":round(margins.quantile(0.25),4),"P75Margin":round(margins.quantile(0.75),4),
           "MinMargin":round(margins.min(),4),"MaxMargin":round(margins.max(),4)}
        if color_col:
            colors=pd.to_numeric(grp[color_col],errors="coerce").dropna()
            if len(colors)>0:
                s["AvgFinalColor"]=round(colors.mean(),4)
                s["AvgDistFromWin"]=round(colors[colors<0].mean(),4) if (colors<0).any() else 0
        bucket_stats.append(s)
    stats_df=pd.DataFrame(bucket_stats)
    recommendations={}
    for _,row in stats_df.iterrows():
        rec=row["MedianMargin"]
        if "AvgDistFromWin" in row and pd.notna(row["AvgDistFromWin"]) and row["AvgDistFromWin"]<0:
            dist=abs(row["AvgDistFromWin"])
            if dist<0.05: rec+=dist*0.5
            elif dist<0.15: rec+=dist*0.25
        recommendations[row["BucketKey"]]=round(rec,4)
    return recommendations,stats_df

def recommend_margins(df,recommendations):
    df=df.copy()
    def get_rec(row):
        k=row["BucketKey"]
        if k in recommendations: return recommendations[k]
        f=row.get("_fico",700)
        if f>=780: return 0.280
        elif f>=740: return 0.250
        elif f>=700: return 0.220
        elif f>=660: return 0.190
        elif f>=620: return 0.160
        else: return 0.130
    df["RecommendedMargin"]=df.apply(get_rec,axis=1)
    df["BucketMatched"]=df["BucketKey"].apply(lambda k:"Matched" if k in recommendations else "No History")
    return df

# ── Color helpers ─────────────────────────────────────────────
def fico_color(f):
    if f>=750: return ("#fff","#1d4ed8")
    if f>=700: return ("#fff","#0e7490")
    if f>=650: return ("#fff","#b45309")
    return ("#fff","#991b1b")

def margin_color(m):
    if m>-0.40: return "#22c55e"
    if m>-0.50: return "#f59e0b"
    return "#ef4444"

def bar_html(m):
    mn,mx=-0.65,-0.30
    pct=max(0,min(100,((m-mn)/(mx-mn))*100))
    c=margin_color(m)
    return f'''<div style="display:flex;align-items:center;gap:10px">
      <div style="width:80px;height:5px;background:#1a2332;border-radius:99px;overflow:hidden">
        <div style="width:{pct:.0f}%;height:100%;background:{c};border-radius:99px"></div>
      </div>
      <span style="color:{c};font-weight:700;font-size:12px;font-family:'JetBrains Mono',monospace">{m:.4f}</span>
    </div>'''

# ── Plotly chart theme ────────────────────────────────────────
CHART_THEME = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    font=dict(color="#64748b", family="Inter"),
    margin=dict(l=20,r=20,t=40,b=20),
)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <div class="sidebar-logo-icon">📊</div>
      <div class="sidebar-title">Bid Margin Optimizer</div>
      <div class="sidebar-sub">Mortgage Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:16px 20px 8px;border-bottom:1px solid #1a2332">
      <div style="color:#475569;font-size:9px;font-weight:700;letter-spacing:0.12em;
                  text-transform:uppercase;margin-bottom:12px">📂 Upload Loan File</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Excel or CSV",
        type=["xlsx","xls","csv"],
        help="Upload your Excel or CSV loan file"
    )

    if uploaded_file:
        st.markdown(f"""
        <div class="sidebar-section">
          <div class="sidebar-section-title">File Info</div>
          <div class="sidebar-stat">
            <span class="sidebar-stat-label">File</span>
            <span class="sidebar-stat-value" style="font-size:10px;color:#3b82f6">{uploaded_file.name[:18]}...</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── No file uploaded ──────────────────────────────────────────
if not uploaded_file:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;
                min-height:80vh;flex-direction:column;gap:20px;padding:40px">
      <div style="width:80px;height:80px;background:linear-gradient(135deg,#3b82f6,#06b6d4);
                  border-radius:20px;display:flex;align-items:center;
                  justify-content:center;font-size:36px">📊</div>
      <div style="text-align:center">
        <div style="color:#f1f5f9;font-size:28px;font-weight:800;margin-bottom:8px">
          Bid Margin Optimizer
        </div>
        <div style="color:#475569;font-size:15px;margin-bottom:6px">
          Mortgage Analytics Platform
        </div>
        <div style="color:#334155;font-size:13px">
          Upload your Excel or CSV file from the sidebar to get started ←
        </div>
      </div>
      <div style="display:flex;gap:24px;margin-top:10px">
        <div style="text-align:center">
          <div style="color:#3b82f6;font-size:22px;font-weight:800">FICO</div>
          <div style="color:#334155;font-size:11px">Bucket Analysis</div>
        </div>
        <div style="text-align:center">
          <div style="color:#06b6d4;font-size:22px;font-weight:800">Rate</div>
          <div style="color:#334155;font-size:11px">Calibration</div>
        </div>
        <div style="text-align:center">
          <div style="color:#22c55e;font-size:22px;font-weight:800">Margin</div>
          <div style="color:#334155;font-size:11px">Recommendation</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Load & process ────────────────────────────────────────────
@st.cache_data
def load_and_process(file_bytes, file_name):
    import io
    if file_name.endswith(".csv"):
        df_raw = pd.read_csv(io.BytesIO(file_bytes), dtype=str)
    else:
        df_raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0, dtype=str)
    df   = assign_buckets(df_raw)
    recs, stats = calibrate_margins(df)
    df   = recommend_margins(df, recs if recs else {})
    return df, stats, recs if recs else {}

file_bytes = uploaded_file.read()
with st.spinner("⚙️ Processing your loan file..."):
    df, stats_df, recs = load_and_process(file_bytes, uploaded_file.name)

loan_col    = next((c for c in ["LoanNumber","Loan Number","loan_number"] if c in df.columns), None)
total_loans = len(df)
total_vol   = df["_amount"].sum()
wtd_margin  = (df["RecommendedMargin"]*df["_amount"]).sum()/total_vol if total_vol>0 else 0
matched     = (df["BucketMatched"]=="Matched").sum()
coverage    = int(matched/total_loans*100) if total_loans>0 else 0
wmc         = margin_color(wtd_margin)

# ── Update sidebar with stats ─────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-section">
      <div class="sidebar-section-title">Portfolio Summary</div>
      <div class="sidebar-stat">
        <span class="sidebar-stat-label">Total Loans</span>
        <span class="sidebar-stat-value">{total_loans}</span>
      </div>
      <div class="sidebar-stat">
        <span class="sidebar-stat-label">Total Volume</span>
        <span class="sidebar-stat-value" style="color:#3b82f6">${total_vol/1e6:.2f}M</span>
      </div>
      <div class="sidebar-stat">
        <span class="sidebar-stat-label">Wtd Margin</span>
        <span class="sidebar-stat-value" style="color:{wmc}">{wtd_margin:.4f}</span>
      </div>
      <div class="sidebar-stat">
        <span class="sidebar-stat-label">Coverage</span>
        <span class="sidebar-stat-value" style="color:{'#22c55e' if coverage==100 else '#f59e0b'}">{coverage}%</span>
      </div>
    </div>
    <div class="sidebar-section">
      <div class="sidebar-section-title">FICO Breakdown</div>
    """, unsafe_allow_html=True)

    fico_counts = df["FicoBucket"].value_counts().sort_index()
    for bucket, count in fico_counts.items():
        pct = int(count/total_loans*100)
        st.markdown(f"""
        <div style="margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;margin-bottom:3px">
            <span style="color:#64748b;font-size:11px">{bucket}</span>
            <span style="color:#94a3b8;font-size:11px;font-family:'JetBrains Mono',monospace">{count}</span>
          </div>
          <div style="height:4px;background:#1a2332;border-radius:99px;overflow:hidden">
            <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#3b82f6,#06b6d4);border-radius:99px"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Download in sidebar
    st.markdown("<div style='padding:16px 20px'>", unsafe_allow_html=True)
    out_cols = [c for c in df.columns if not c.startswith("_")]
    csv_data = df[out_cols].to_csv(index=False).encode("utf-8")
    st.download_button("↓ Download Results CSV", csv_data,
                       "bid_margin_recommendations.csv", "text/csv",
                       use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Main content ──────────────────────────────────────────────
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Page title
st.markdown(f"""
<div class="page-title">
  <div>
    <div class="page-title-text">Bid Margin Dashboard</div>
    <div class="page-title-sub">{uploaded_file.name} · {total_loans} loans processed</div>
  </div>
  <div class="live-badge">
    <div style="width:7px;height:7px;border-radius:50%;background:#4ade80"></div>
    Live Analysis
  </div>
</div>
""", unsafe_allow_html=True)

# Metric cards
mc1,mc2,mc3,mc4 = "#3b82f6","#22c55e",wmc,"#22c55e" if coverage==100 else "#f59e0b"
card_class = lambda m: "green" if m=="#22c55e" else "blue" if m=="#3b82f6" else "red" if m=="#ef4444" else "amber"
st.markdown(f"""
<div class="metrics-grid">
  <div class="metric-card blue">
    <div class="metric-label">Total Loans</div>
    <div class="metric-value" style="color:#60a5fa">{total_loans}</div>
    <div class="metric-sub">records in portfolio</div>
  </div>
  <div class="metric-card blue">
    <div class="metric-label">Total Volume</div>
    <div class="metric-value" style="color:#22d3ee">${total_vol/1e6:.2f}M</div>
    <div class="metric-sub">total loan amount</div>
  </div>
  <div class="metric-card {'green' if wtd_margin>-0.40 else 'amber' if wtd_margin>-0.50 else 'red'}">
    <div class="metric-label">Wtd Avg Margin</div>
    <div class="metric-value" style="color:{wmc}">{wtd_margin:.4f}</div>
    <div class="metric-sub">weighted recommended</div>
  </div>
  <div class="metric-card {'green' if coverage==100 else 'amber'}">
    <div class="metric-label">Bucket Coverage</div>
    <div class="metric-value" style="color:{'#4ade80' if coverage==100 else '#fbbf24'}">{coverage}%</div>
    <div class="metric-sub">{matched}/{total_loans} loans matched</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋  Loan Detail", "📊  Analytics", "🗂️  Bucket Statistics"])

# ── TAB 1: Loan Detail ────────────────────────────────────────
with tab1:
    # Search & filter bar
    col1, col2, col3, col4 = st.columns([3,2,2,2])
    with col1:
        search = st.text_input("🔍 Search loan number...", placeholder="Enter loan #")
    with col2:
        fico_filter = st.selectbox("FICO Bucket", ["All"] + sorted(df["FicoBucket"].unique().tolist()))
    with col3:
        status_filter = st.selectbox("Status", ["All", "Matched", "No History"])
    with col4:
        margin_filter = st.selectbox("Margin Range", ["All", "Above -0.40", "-0.40 to -0.50", "Below -0.50"])

    # Apply filters
    filtered = df.copy()
    if search:
        if loan_col:
            filtered = filtered[filtered[loan_col].astype(str).str.contains(search, na=False)]
    if fico_filter != "All":
        filtered = filtered[filtered["FicoBucket"]==fico_filter]
    if status_filter != "All":
        filtered = filtered[filtered["BucketMatched"]==status_filter]
    if margin_filter == "Above -0.40":
        filtered = filtered[filtered["RecommendedMargin"]>-0.40]
    elif margin_filter == "-0.40 to -0.50":
        filtered = filtered[(filtered["RecommendedMargin"]<=-0.40)&(filtered["RecommendedMargin"]>-0.50)]
    elif margin_filter == "Below -0.50":
        filtered = filtered[filtered["RecommendedMargin"]<=-0.50]

    # Build table
    rows=""
    for i,(_,row) in enumerate(filtered.iterrows()):
        loan_num = str(row[loan_col])[-12:] if loan_col else "—"
        fico     = int(row.get("_fico",0))
        rate     = float(row.get("_rate",0))
        amt      = float(row.get("_amount",0))
        fb       = str(row.get("FicoBucket","—"))
        rb       = str(row.get("RateBucket","—"))
        ab       = str(row.get("AmountBucket","—"))
        rec      = float(row.get("RecommendedMargin",0))
        status   = str(row.get("BucketMatched","—"))
        ftc,fbc  = fico_color(fico)
        mc       = margin_color(rec)
        s_color  = "#22c55e" if status=="Matched" else "#64748b"
        s_bg     = "#052e16" if status=="Matched" else "#1a2332"
        rows    += f"""<tr>
          <td style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#64748b">{loan_num}</td>
          <td><span class="fico-pill" style="background:{fbc};color:{ftc}">{fico}</span></td>
          <td style="font-family:'JetBrains Mono',monospace;font-weight:600">{rate:.3f}%</td>
          <td style="font-family:'JetBrains Mono',monospace">${amt:,.0f}</td>
          <td style="color:#94a3b8;font-size:11px">{fb}</td>
          <td style="text-align:left">{rb}</td>
          <td style="text-align:left">{ab}</td>
          <td>{bar_html(rec)}</td>
          <td><span class="status-badge" style="background:{s_bg};color:{s_color}">
            {"✓ Matched" if status=="Matched" else "○ No History"}
          </span></td>
        </tr>"""

    st.markdown(f"""
    <div class="table-wrap">
      <div class="table-head-bar">
        <div>
          <span class="table-head-title">Loan Detail</span>
          <span class="table-head-sub">— Recommended bid margins</span>
        </div>
        <span class="count-badge">{len(filtered)} records</span>
      </div>
      <div style="overflow-x:auto">
        <table class="dtable">
          <thead><tr>
            <th>Loan #</th><th>FICO</th><th>Rate</th><th>Amount</th>
            <th>FICO Bucket</th><th>Rate Bkt</th><th>Amt Bkt</th>
            <th>Rec Margin</th><th>Status</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── TAB 2: Analytics ──────────────────────────────────────────
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        # Margin distribution histogram
        fig1 = go.Figure()
        fig1.add_trace(go.Histogram(
            x=df["RecommendedMargin"],
            nbinsx=20,
            marker=dict(
                color=df["RecommendedMargin"].apply(
                    lambda m: "#22c55e" if m>-0.40 else "#f59e0b" if m>-0.50 else "#ef4444"
                ),
                line=dict(color="#070b14", width=1)
            ),
            name="Margin Distribution"
        ))
        fig1.update_layout(
            title=dict(text="Margin Distribution", font=dict(color="#f1f5f9", size=14)),
            xaxis=dict(title="Recommended Margin", color="#475569", gridcolor="#1a2332"),
            yaxis=dict(title="Loan Count", color="#475569", gridcolor="#1a2332"),
            **CHART_THEME, showlegend=False,
            bargap=0.1
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        # FICO bucket bar chart
        fico_counts = df["FicoBucket"].value_counts().sort_index().reset_index()
        fico_counts.columns = ["FICO Bucket","Count"]
        colors_map = {
            "751-800":"#3b82f6","801-850":"#06b6d4",
            "701-750":"#22c55e","651-700":"#f59e0b",
            "601-650":"#f97316","551-600":"#ef4444",
            "501-550":"#dc2626","451-500":"#991b1b"
        }
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=fico_counts["FICO Bucket"],
            y=fico_counts["Count"],
            marker=dict(
                color=[colors_map.get(b,"#3b82f6") for b in fico_counts["FICO Bucket"]],
                line=dict(color="#070b14", width=1)
            ),
            name="FICO Buckets"
        ))
        fig2.update_layout(
            title=dict(text="FICO Bucket Distribution", font=dict(color="#f1f5f9", size=14)),
            xaxis=dict(color="#475569", gridcolor="#1a2332"),
            yaxis=dict(title="Count", color="#475569", gridcolor="#1a2332"),
            **CHART_THEME, showlegend=False, bargap=0.2
        )
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        # FICO vs Margin scatter
        fig3 = px.scatter(
            df, x="_fico", y="RecommendedMargin",
            color="BucketMatched",
            color_discrete_map={"Matched":"#22c55e","No History":"#ef4444"},
            labels={"_fico":"FICO Score","RecommendedMargin":"Recommended Margin"},
            title="FICO Score vs Recommended Margin",
        )
        fig3.update_traces(marker=dict(size=8, opacity=0.8))
        fig3.update_layout(
            **CHART_THEME,
            title=dict(font=dict(color="#f1f5f9", size=14)),
            xaxis=dict(color="#475569", gridcolor="#1a2332"),
            yaxis=dict(color="#475569", gridcolor="#1a2332"),
            legend=dict(font=dict(color="#64748b"), bgcolor="#0d1117", bordercolor="#1a2332"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        # Rate bucket pie
        rate_counts = df["RateBucket"].value_counts().reset_index()
        rate_counts.columns = ["Rate Bucket","Count"]
        rate_counts = rate_counts[rate_counts["Rate Bucket"]!=-1].sort_values("Rate Bucket")
        fig4 = go.Figure(go.Pie(
            labels=[f"Rate {r}" for r in rate_counts["Rate Bucket"]],
            values=rate_counts["Count"],
            hole=0.6,
            marker=dict(colors=px.colors.sequential.Blues[2:]),
        ))
        fig4.update_layout(
            title=dict(text="Rate Bucket Distribution", font=dict(color="#f1f5f9", size=14)),
            **CHART_THEME,
            legend=dict(font=dict(color="#64748b",size=10), bgcolor="#0d1117"),
            annotations=[dict(text=f"{total_loans}<br>loans",
                             x=0.5,y=0.5,font_size=14,
                             font_color="#f1f5f9",showarrow=False)]
        )
        st.plotly_chart(fig4, use_container_width=True)

# ── TAB 3: Bucket Statistics ──────────────────────────────────
with tab3:
    if stats_df is not None and len(stats_df)>0:
        brows=""
        for i,(_,r) in enumerate(stats_df.iterrows()):
            mc  = margin_color(r['MedianMargin'])
            mc_bg = "#052e16" if r['MedianMargin']>-0.40 else "#431407" if r['MedianMargin']>-0.50 else "#450a0a"
            brows+=f"""<tr>
              <td style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#94a3b8">{str(r['BucketKey'])}</td>
              <td style="font-weight:700;color:#f1f5f9">{int(r['LoanCount'])}</td>
              <td><span style="background:{mc_bg};color:{mc};padding:3px 12px;
                               border-radius:99px;font-weight:700;
                               font-family:'JetBrains Mono',monospace;font-size:12px">{r['MedianMargin']:.4f}</span></td>
              <td style="font-family:'JetBrains Mono',monospace;color:#94a3b8">{r['AvgMargin']:.4f}</td>
              <td style="font-family:'JetBrains Mono',monospace;color:#64748b">{r['P25Margin']:.4f}</td>
              <td style="font-family:'JetBrains Mono',monospace;color:#64748b">{r['P75Margin']:.4f}</td>
            </tr>"""

        st.markdown(f"""
        <div class="table-wrap">
          <div class="table-head-bar">
            <div>
              <span class="table-head-title">Bucket Statistics</span>
              <span class="table-head-sub">— Historical All In Margin by bucket</span>
            </div>
            <span class="count-badge">{len(stats_df)} buckets</span>
          </div>
          <div style="overflow-x:auto">
            <table class="dtable">
              <thead><tr>
                <th style="width:38%">Bucket Key</th>
                <th style="width:10%">Count</th>
                <th style="width:15%">Median</th>
                <th style="width:15%">Avg</th>
                <th style="width:11%">P25</th>
                <th style="width:11%">P75</th>
              </tr></thead>
              <tbody>{brows}</tbody>
            </table>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:60px;color:#475569">
          No historical margin data found (All In Margin column missing)
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
