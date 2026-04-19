import streamlit as st
import pandas as pd
import numpy as np
import io
import warnings
warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Bid Margin Optimizer",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS — Design 4 Olive/Sage/Teal theme ──────────────
st.markdown("""
<style>
  /* Page background */
  .stApp { background-color: #3d4a38 !important; }
  section[data-testid="stSidebar"] { display: none; }

  /* Hide default streamlit header/footer */
  #MainMenu, footer, header { visibility: hidden; }

  /* Top nav bar */
  .top-nav {
    background: #2e3828;
    border-bottom: 1px solid #4a5a44;
    padding: 14px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 12px;
    margin-bottom: 16px;
  }
  .nav-left { display: flex; align-items: center; gap: 14px; }
  .nav-icon {
    width: 42px; height: 42px;
    background: #546E7A;
    border-radius: 12px;
    display: flex; align-items: center;
    justify-content: center;
    font-size: 20px;
  }
  .nav-title { color: #ffffff; font-size: 18px; font-weight: 700; }
  .nav-sub   { color: #8a9e82; font-size: 11px; font-family: monospace; }

  /* Stat cards */
  .cards-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }
  .stat-card {
    background: #2e3828;
    border: 1px solid #4a5a44;
    border-radius: 16px;
    padding: 18px 20px;
  }
  .stat-icon {
    width: 28px; height: 28px;
    border-radius: 8px;
    display: inline-flex; align-items: center;
    justify-content: center; font-size: 13px;
    margin-bottom: 8px;
  }
  .stat-label {
    font-size: 9px; font-weight: 700;
    color: #8a9e82; letter-spacing: 0.08em;
    text-transform: uppercase; margin-bottom: 6px;
  }
  .stat-value {
    font-size: 26px; font-weight: 800;
    font-family: monospace; margin-bottom: 3px;
  }
  .stat-sub { font-size: 10px; color: #4a5a44; }

  /* Table card */
  .table-card {
    background: #2e3828;
    border: 1px solid #4a5a44;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 16px;
  }
  .table-header {
    padding: 16px 20px;
    border-bottom: 1px solid #4a5a44;
    display: flex; align-items: center;
    justify-content: space-between;
    background: #252e22;
  }
  .table-title { color: #ffffff; font-size: 14px; font-weight: 700; }
  .table-sub   { color: #8a9e82; font-size: 12px; margin-left: 10px; }
  .rec-badge {
    background: #3d4a38; color: #8a9e82;
    padding: 4px 14px; border-radius: 8px;
    font-size: 11px; font-weight: 600;
  }

  /* Data table */
  table.loan-table {
    width: 100%; border-collapse: collapse;
    font-family: 'Segoe UI', system-ui, sans-serif;
  }
  table.loan-table th {
    padding: 10px 16px; text-align: left;
    font-size: 10px; font-weight: 700;
    color: #ffffff; letter-spacing: 0.07em;
    text-transform: uppercase;
    border-bottom: 1px solid #4a5a44;
    background: #252e22;
  }
  table.loan-table td {
    padding: 11px 16px;
    border-bottom: 1px solid #4a5a44;
    font-size: 12px; color: #ffffff;
  }
  table.loan-table tr:nth-child(odd)  td { background: #2e3828; }
  table.loan-table tr:nth-child(even) td { background: #252e22; }
  table.loan-table tr:hover td { background: #3a4a34 !important; }

  .fico-pill {
    padding: 4px 12px; border-radius: 8px;
    font-size: 12px; font-weight: 700;
    display: inline-block;
  }
  .status-pill {
    padding: 4px 12px; border-radius: 8px;
    font-size: 11px; font-weight: 700;
    display: inline-block;
  }

  /* Upload area */
  .upload-box {
    background: #2e3828;
    border: 2px dashed #4a5a44;
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    margin: 20px 0;
  }
  .upload-title { color: #ffffff; font-size: 20px; font-weight: 700; margin-bottom: 8px; }
  .upload-sub   { color: #8a9e82; font-size: 13px; }

  /* Footer */
  .footer {
    background: #2e3828;
    border-top: 1px solid #4a5a44;
    padding: 14px 24px;
    display: flex; align-items: center;
    justify-content: space-between;
    border-radius: 12px; margin-top: 16px;
  }

  /* Streamlit file uploader override */
  [data-testid="stFileUploader"] {
    background: #2e3828 !important;
    border: 1px solid #4a5a44 !important;
    border-radius: 12px !important;
    padding: 12px !important;
  }
  [data-testid="stFileUploader"] label { color: #ffffff !important; }
  [data-testid="stFileUploaderDropzone"] {
    background: #252e22 !important;
    border: 2px dashed #4a5a44 !important;
    border-radius: 10px !important;
  }
  [data-testid="stFileUploaderDropzone"] p { color: #8a9e82 !important; }
  [data-testid="stDownloadButton"] button {
    background: #8A9A5B !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 10px 22px !important;
  }
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
    if f>=750: return ("#ffffff","#546E7A")
    if f>=700: return ("#ffffff","#4a7a6a")
    if f>=650: return ("#ffffff","#6a7a3a")
    return ("#ffffff","#5a3a3a")

def margin_color(m):
    if m>-0.40: return "#84cc16"
    if m>-0.50: return "#f59e0b"
    return "#f87171"

def bar_html(m):
    mn,mx=-0.65,-0.30
    pct=max(0,min(100,((m-mn)/(mx-mn))*100))
    c=margin_color(m)
    return f'''<div style="display:flex;align-items:center;gap:10px">
      <div style="width:80px;height:6px;background:#4a5a44;border-radius:99px;overflow:hidden">
        <div style="width:{pct:.0f}%;height:100%;background:{c};border-radius:99px"></div>
      </div>
      <span style="color:{c};font-weight:700;font-size:13px;font-family:monospace">{m:.4f}</span>
    </div>'''

def fico_bars_html(df):
    fico_dist=df["FicoBucket"].value_counts()
    max_cnt=max(fico_dist.values) if len(fico_dist)>0 else 1
    buckets=["451-500","501-550","551-600","601-650","651-700","701-750","751-800","801-850"]
    html=""
    colors={"751-800":"#c8f5b0","801-850":"#86efac","701-750":"#86efac",
            "651-700":"#fde68a","601-650":"#fde68a","551-600":"#fca5a5",
            "501-550":"#fca5a5","451-500":"#f87171"}
    for fb in buckets:
        cnt=fico_dist.get(fb,0)
        h=max(4,int((cnt/max_cnt)*52)) if cnt else 4
        c=colors.get(fb,"#4a5a44")
        op=1.0 if cnt else 0.2
        html+=f'''<div style="display:flex;flex-direction:column;align-items:center;gap:3px;flex:1">
          <div style="width:100%;height:{h}px;background:{c};border-radius:4px 4px 0 0;opacity:{op}"></div>
          <span style="font-size:8px;color:#8a9e82">{fb.split("-")[0]}</span>
        </div>'''
    return html

# ── Build loan table HTML ─────────────────────────────────────
def build_loan_table(df, loan_col):
    rows=""
    for i,(_,row) in enumerate(df.iterrows()):
        loan_num=str(row[loan_col])[-12:] if loan_col else "—"
        fico=int(row.get("_fico",0))
        rate=float(row.get("_rate",0))
        amt=float(row.get("_amount",0))
        fb=str(row.get("FicoBucket","—"))
        rb=str(row.get("RateBucket","—"))
        ab=str(row.get("AmountBucket","—"))
        rec=float(row.get("RecommendedMargin",0))
        status=str(row.get("BucketMatched","—"))
        ftc,fbc=fico_color(fico)
        mc=margin_color(rec)
        s_color="#84cc16" if status=="Matched" else "#6b7280"
        s_bg="#1a2e10" if status=="Matched" else "#3a4a34"
        rows+=f"""<tr>
          <td style="font-family:monospace;font-size:11px">{loan_num}</td>
          <td><span class="fico-pill" style="background:{fbc};color:{ftc}">{fico}</span></td>
          <td style="font-family:monospace;font-weight:600">{rate:.3f}%</td>
          <td style="font-family:monospace">${amt:,.0f}</td>
          <td style="color:#c8d8b0;font-size:11px">{fb}</td>
          <td>{rb}</td>
          <td>{ab}</td>
          <td>{bar_html(rec)}</td>
          <td><span class="status-pill" style="background:{s_bg};color:{s_color}">
            {"✓ Matched" if status=="Matched" else "— No History"}
          </span></td>
        </tr>"""
    return f"""
    <table class="loan-table">
      <thead><tr>
        <th>Loan #</th><th>FICO</th><th>Rate</th><th>Amount</th>
        <th>FICO Bucket</th><th>Rate Bkt</th><th>Amt Bkt</th>
        <th>Rec Margin</th><th>Status</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>"""

# ── Build bucket stats table HTML ────────────────────────────
def build_bucket_table(stats_df):
    rows=""
    for i,(_,r) in enumerate(stats_df.iterrows()):
        mc=margin_color(r['MedianMargin'])
        mc_bg="#1a2e10" if r['MedianMargin']>-0.40 else "#2a1f00" if r['MedianMargin']>-0.50 else "#2a1010"
        rows+=f"""<tr>
          <td style="font-family:monospace;font-size:11px">{str(r['BucketKey'])}</td>
          <td style="font-weight:700">{int(r['LoanCount'])}</td>
          <td><span style="background:{mc_bg};color:{mc};padding:3px 12px;border-radius:6px;
                           font-weight:700;font-family:monospace;font-size:12px">{r['MedianMargin']:.4f}</span></td>
          <td style="font-family:monospace">{r['AvgMargin']:.4f}</td>
          <td style="font-family:monospace">{r['P25Margin']:.4f}</td>
          <td style="font-family:monospace">{r['P75Margin']:.4f}</td>
        </tr>"""
    return f"""
    <table class="loan-table">
      <thead><tr>
        <th style="width:35%">Bucket Key</th><th style="width:10%">Count</th>
        <th style="width:15%">Median</th><th style="width:15%">Avg</th>
        <th style="width:12%">P25</th><th style="width:13%">P75</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>"""

# ── MAIN APP ──────────────────────────────────────────────────

# Top Nav
st.markdown("""
<div class="top-nav">
  <div class="nav-left">
    <div class="nav-icon">📊</div>
    <div>
      <div class="nav-title">Bid Margin Optimizer</div>
      <div class="nav-sub">Mortgage Analytics Dashboard</div>
    </div>
  </div>
  <div style="color:#8a9e82;font-size:12px">Upload your file below ↓</div>
</div>
""", unsafe_allow_html=True)

# File upload
uploaded_file = st.file_uploader(
    "Upload your loan file (Excel or CSV)",
    type=["xlsx","xls","csv"],
    label_visibility="collapsed"
)

if uploaded_file is None:
    st.markdown("""
    <div class="upload-box">
      <div style="font-size:48px;margin-bottom:16px">📂</div>
      <div class="upload-title">Drop your Excel or CSV file above</div>
      <div class="upload-sub">Supported formats: .xlsx, .xls, .csv</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Load file
with st.spinner("Loading and processing your file..."):
    try:
        if uploaded_file.name.endswith(".csv"):
            df_raw = pd.read_csv(uploaded_file, dtype=str)
        else:
            df_raw = pd.read_excel(uploaded_file, sheet_name=0, dtype=str)
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.stop()

    df          = assign_buckets(df_raw)
    result      = calibrate_margins(df)
    recs,stats  = result if isinstance(result,tuple) else (result,None)
    df          = recommend_margins(df, recs)
    loan_col    = next((c for c in ["LoanNumber","Loan Number","loan_number"] if c in df.columns),None)

# Summary values
total_loans = len(df)
total_vol   = df["_amount"].sum()
wtd_margin  = (df["RecommendedMargin"]*df["_amount"]).sum()/total_vol if total_vol>0 else 0
matched     = (df["BucketMatched"]=="Matched").sum()
coverage    = int(matched/total_loans*100) if total_loans>0 else 0
wmc         = margin_color(wtd_margin)
wmc_txt     = "#065f46" if wtd_margin>-0.40 else "#92400e" if wtd_margin>-0.50 else "#991b1b"

# Stat cards + FICO chart
bars = fico_bars_html(df)
st.markdown(f"""
<div class="cards-row">
  <div class="stat-card">
    <div class="stat-icon" style="background:#546E7A">📋</div>
    <div class="stat-label">Total Loans</div>
    <div class="stat-value" style="color:#ffffff">{total_loans}</div>
    <div class="stat-sub">records loaded</div>
  </div>
  <div class="stat-card">
    <div class="stat-icon" style="background:#2a4a3a">💰</div>
    <div class="stat-label">Total Volume</div>
    <div class="stat-value" style="color:#84cc16">${total_vol/1e6:.2f}M</div>
    <div class="stat-sub">portfolio size</div>
  </div>
  <div class="stat-card">
    <div class="stat-icon" style="background:{'#2a4a3a' if wtd_margin>-0.40 else '#2a1f00' if wtd_margin>-0.50 else '#2a0f0f'}">📈</div>
    <div class="stat-label">Wtd Avg Margin</div>
    <div class="stat-value" style="color:{wmc}">{wtd_margin:.4f}</div>
    <div class="stat-sub">weighted recommended</div>
  </div>
  <div class="stat-card">
    <div class="stat-icon" style="background:{'#2a4a3a' if coverage==100 else '#2a1f00'}">🎯</div>
    <div class="stat-label">Bucket Coverage</div>
    <div class="stat-value" style="color:{'#84cc16' if coverage==100 else '#f59e0b'}">{coverage}%</div>
    <div class="stat-sub">{matched}/{total_loans} matched</div>
  </div>
  <div class="stat-card">
    <div class="stat-label" style="margin-bottom:12px">FICO Distribution</div>
    <div style="display:flex;align-items:flex-end;gap:3px;height:52px">{bars}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Loan Detail Table
loan_table = build_loan_table(df, loan_col)
st.markdown(f"""
<div class="table-card">
  <div class="table-header">
    <div>
      <span class="table-title">Loan Detail</span>
      <span class="table-sub">— Recommended bid margins</span>
    </div>
    <span class="rec-badge">{total_loans} records</span>
  </div>
  <div style="overflow-x:auto">{loan_table}</div>
</div>
""", unsafe_allow_html=True)

# Bucket Statistics Table
if stats is not None and len(stats)>0:
    bucket_table = build_bucket_table(stats)
    st.markdown(f"""
    <div class="table-card">
      <div class="table-header">
        <div>
          <span class="table-title">Bucket Statistics</span>
          <span class="table-sub">— Historical All In Margin</span>
        </div>
      </div>
      <div style="overflow-x:auto">{bucket_table}</div>
    </div>
    """, unsafe_allow_html=True)

# Download button
output_cols=[]
for c in ["LoanNumber","Loan Number","Client","Program"]:
    if c in df.columns: output_cols.append(c)
for c in ["NoteRate","LoanAmount","FICO","LTV","Purpose","State"]:
    if c in df.columns: output_cols.append(c)
for c in ["All in Margin","AllInMargin"]:
    if c in df.columns: output_cols.append(c); break
for c in ["FicoBucket","RateBucket","AmountBucket","BucketKey","RecommendedMargin","BucketMatched"]:
    if c in df.columns: output_cols.append(c)
seen,final_cols=set(),[]
for c in output_cols:
    if c not in seen: seen.add(c); final_cols.append(c)
out_df=df[final_cols].copy()
csv_bytes=out_df.to_csv(index=False).encode("utf-8")

col1,col2,col3=st.columns([1,2,1])
with col2:
    st.download_button(
        label="↓ Download CSV Results",
        data=csv_bytes,
        file_name="bid_margin_recommendations.csv",
        mime="text/csv",
        use_container_width=True
    )

# Footer
st.markdown("""
<div class="footer">
  <span style="color:#8A9A5B;font-size:11px;font-weight:700">● Bid Margin Optimizer</span>
  <span style="color:#4a5a44;font-size:11px;font-family:monospace">Results ready — click Download CSV above</span>
</div>
""", unsafe_allow_html=True)
