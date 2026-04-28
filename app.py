import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, os

st.set_page_config(
    page_title="Hollister — Department Growth Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE   = os.path.join(os.path.dirname(__file__), "dashboard_data.json")
PERIODS     = ["2023","2024","2025","Jan-26","Feb-26","Mar-26","Apr-26",
               "May-26","Jun-26","Jul-26","Aug-26","Sep-26","Oct-26","Nov-26","Dec-26"]
DEPARTMENTS = ["Project","Molding","Production","SCM","Maintenance","QA","HR","Finance"]

TIER_COLORS = {
    "Bronze": {"main":"#C07830","light":"#FEF3E8","border":"#E8A060","text":"#7A4A10"},
    "Silver": {"main":"#607080","light":"#EEF2F6","border":"#90A0B0","text":"#3A4A5A"},
    "Gold":   {"main":"#B8960C","light":"#FFFBE8","border":"#D4B030","text":"#5A4800"},
}

PROG_PALETTE = [
    "#E05A2B","#2B7BE0","#27AE60","#8E44AD","#E8B400",
    "#0097A7","#E91E63","#546E7A","#43A047","#F4511E","#1565C0",
]

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

def to_flat_df(data):
    rows = []
    for prog, pdata in data["programs"].items():
        for dept, vals in pdata["departments"].items():
            for i, period in enumerate(PERIODS):
                rows.append({
                    "Program": prog, "Tier": pdata["tier"],
                    "Department": dept, "Period": period,
                    "Value": int(vals[i])
                })
    return pd.DataFrame(rows)

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
[data-testid="stAppViewContainer"],.main,[data-testid="stHeader"],[data-testid="block-container"]{background:#F7F8FA!important;}
[data-testid="block-container"]{padding-top:0!important;}
[data-testid="stVerticalBlock"]>div:first-child{padding-top:0;}

.top-header{background:linear-gradient(135deg,#0A2540 0%,#133159 60%,#1A4080 100%);
  padding:22px 36px 18px;border-radius:0 0 16px 16px;margin-bottom:22px;position:relative;overflow:hidden;}
.top-header::after{content:'';position:absolute;right:-40px;top:-40px;width:280px;height:280px;
  background:radial-gradient(circle,rgba(255,255,255,0.06) 0%,transparent 65%);pointer-events:none;}
.co-name{font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;font-weight:700;letter-spacing:4px;
  text-transform:uppercase;color:rgba(255,255,255,0.45);margin-bottom:6px;}
.dash-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:26px;font-weight:800;color:#fff;line-height:1.1;}
.dash-title span{color:#60C0FF;}
.dash-meta{font-size:11px;color:rgba(255,255,255,0.4);margin-top:5px;letter-spacing:0.3px;}

.kpi-card{background:#fff;border:1px solid #E8EBF0;border-radius:12px;padding:14px 18px;
  box-shadow:0 1px 4px rgba(0,0,0,0.05);position:relative;overflow:hidden;}
.kpi-card::before{content:'';position:absolute;top:0;left:0;width:100%;height:3px;border-radius:12px 12px 0 0;}
.kpi-card.blue::before{background:#2563EB;} .kpi-card.bronze::before{background:#C07830;}
.kpi-card.silver::before{background:#607080;} .kpi-card.gold::before{background:#B8960C;}
.kpi-card.green::before{background:#16A34A;}
.kpi-val{font-family:'Plus Jakarta Sans',sans-serif;font-size:28px;font-weight:800;line-height:1;color:#0A2540;}
.kpi-card.blue .kpi-val{color:#2563EB;} .kpi-card.bronze .kpi-val{color:#C07830;}
.kpi-card.silver .kpi-val{color:#607080;} .kpi-card.gold .kpi-val{color:#B8960C;}
.kpi-card.green .kpi-val{color:#16A34A;}
.kpi-lbl{font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#9CA3AF;margin-top:4px;}
.kpi-sub{font-size:10px;color:#6B7280;margin-top:1px;}

.sec-hdr{display:flex;align-items:center;gap:10px;margin:6px 0 12px;}
.sec-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;}
.sec-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:15px;font-weight:700;color:#0A2540;}
.sec-line{flex:1;height:1px;background:#E5E7EB;}

.hero-card{background:#fff;border:1px solid #E8EBF0;border-radius:16px;overflow:hidden;
  box-shadow:0 4px 24px rgba(0,0,0,0.09);margin-bottom:22px;}
.hero-top{background:linear-gradient(135deg,#0A2540 0%,#1A4080 100%);padding:18px 26px 14px;
  display:flex;align-items:flex-start;justify-content:space-between;}
.hero-label{font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;
  color:rgba(255,255,255,0.4);margin-bottom:4px;}
.hero-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:18px;font-weight:800;color:#fff;}
.hero-desc{font-size:11px;color:rgba(255,255,255,0.45);margin-top:3px;}
.hero-body{padding:18px 18px 8px;}

.dept-card{background:#fff;border:1px solid #E8EBF0;border-radius:12px;
  padding:16px 18px;box-shadow:0 1px 4px rgba(0,0,0,0.05);height:100%;}
.dept-title{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;
  color:#9CA3AF;margin-bottom:14px;}

.stTabs [data-baseweb="tab-list"]{background:#fff;border-radius:10px;padding:4px;gap:2px;
  border:1px solid #E5E7EB;box-shadow:0 1px 3px rgba(0,0,0,0.05);}
.stTabs [data-baseweb="tab"]{background:transparent;color:#6B7280;font-family:'Plus Jakarta Sans',sans-serif;
  font-size:13px;font-weight:600;border-radius:8px;padding:8px 22px;}
.stTabs [aria-selected="true"]{background:#0A2540!important;color:white!important;}
.edit-banner{background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;
  padding:12px 18px;color:#1E40AF;font-size:13px;margin-bottom:16px;}
</style>
""", unsafe_allow_html=True)

# ── INIT ───────────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()
data = st.session_state.data

# ── HEADER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-header">
  <div class="co-name">🏭 &nbsp; Hollister Co.</div>
  <div class="dash-title">Department <span>Growth</span> Dashboard</div>
  <div class="dash-meta">
    Tracking workforce development across 11 elements &nbsp;·&nbsp;
    8 departments &nbsp;·&nbsp; 2023 → 2026
  </div>
</div>
""", unsafe_allow_html=True)

tab_dash, tab_edit = st.tabs(["📊  Overview & Charts", "✏️  Edit Data"])

# ══════════════════════════════════════════════════════════════════════════
with tab_dash:
    df = to_flat_df(data)
    programs   = list(data["programs"].keys())
    tiers      = {p: data["programs"][p]["tier"] for p in programs}
    prog_color = {p: PROG_PALETTE[i] for i, p in enumerate(programs)}

    df25 = df[df["Period"] == "2025"]
    grand   = int(df25["Value"].sum())
    bronze  = int(df25[df25["Tier"]=="Bronze"]["Value"].sum())
    silver  = int(df25[df25["Tier"]=="Silver"]["Value"].sum())
    gold    = int(df25[df25["Tier"]=="Gold"]["Value"].sum())
    total23 = int(df[df["Period"]=="2023"]["Value"].sum())
    total24 = int(df[df["Period"]=="2024"]["Value"].sum())
    apr26   = int(df[df["Period"]=="Apr-26"]["Value"].sum())

    # ── KPIs ──────────────────────────────────────────────────────────────
    k1,k2,k3,k4,k5,k6,k7 = st.columns(7)
    def kpi(col, val, lbl, sub, cls):
        col.markdown(f"""<div class="kpi-card {cls}">
          <div class="kpi-val">{val}</div>
          <div class="kpi-lbl">{lbl}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    kpi(k1, grand,   "Overall 2025",  "All elements",  "blue")
    kpi(k2, bronze,  "🥉 Bronze",      "5 elements",    "bronze")
    kpi(k3, silver,  "🥈 Silver",      "5 elements",    "silver")
    kpi(k4, gold,    "🥇 Gold",        "1 element",     "gold")
    kpi(k5, total23, "Growth 2023",   "Baseline year", "blue")
    kpi(k6, total24, "Growth 2024",   "Year 2",        "blue")
    kpi(k7, apr26,   "Target Apr-26", "Planned",       "green")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ══ HERO CHART ════════════════════════════════════════════════════════
    st.markdown("""<div class="sec-hdr">
      <div class="sec-dot" style="background:#2563EB"></div>
      <div class="sec-title">Overall Growth — All Elements Combined</div>
      <div class="sec-line"></div>
    </div>""", unsafe_allow_html=True)

    overall_df = df.groupby("Period")["Value"].sum().reset_index()
    overall_df["Period"] = pd.Categorical(overall_df["Period"], categories=PERIODS, ordered=True)
    overall_df = overall_df.sort_values("Period").rename(columns={"Value":"Total"})

    tier_period = df.groupby(["Period","Tier"])["Value"].sum().reset_index()
    tier_period["Period"] = pd.Categorical(tier_period["Period"], categories=PERIODS, ordered=True)
    tier_period = tier_period.sort_values("Period")

    col_hero, col_side = st.columns([3, 1])

    with col_hero:
        st.markdown("""<div class="hero-card">
          <div class="hero-top">
            <div>
              <div class="hero-label">Master Overview · Hollister Co.</div>
              <div class="hero-title">Department Growth Across All Elements</div>
              <div class="hero-desc">No. of employees who completed training under each element — 2023 to 2026</div>
            </div>
          </div>
          <div class="hero-body">""", unsafe_allow_html=True)

        fig_hero = go.Figure()
        tier_fills = {
            "Bronze": "rgba(192,120,48,0.18)",
            "Silver": "rgba(96,112,128,0.15)",
            "Gold":   "rgba(184,150,12,0.22)",
        }
        tier_lines = {"Bronze":"#E8A060","Silver":"#90A0B0","Gold":"#D4B030"}

        for tier_name in ["Gold","Silver","Bronze"]:
            td = tier_period[tier_period["Tier"]==tier_name]
            fig_hero.add_trace(go.Scatter(
                x=td["Period"], y=td["Value"],
                name=f"{tier_name}",
                stackgroup="one",
                mode="lines",
                line=dict(width=1.5, color=tier_lines[tier_name]),
                fillcolor=tier_fills[tier_name],
                hovertemplate=f"<b>{tier_name}</b>: %{{y}}<extra></extra>"
            ))

        # Total line — bold, stands out
        fig_hero.add_trace(go.Scatter(
            x=overall_df["Period"], y=overall_df["Total"],
            name="Total",
            mode="lines+markers",
            line=dict(color="#2563EB", width=3.5, dash="solid"),
            marker=dict(size=8, color="#2563EB", symbol="circle",
                        line=dict(color="#fff", width=2.5)),
            hovertemplate="<b>Total: %{y} employees</b><extra></extra>"
        ))

        # Annotate peak
        peak_idx = overall_df["Total"].idxmax()
        peak_period = overall_df.loc[peak_idx, "Period"]
        peak_val    = overall_df.loc[peak_idx, "Total"]
        fig_hero.add_annotation(
            x=peak_period, y=peak_val,
            text=f"<b>Peak: {peak_val}</b>",
            showarrow=True, arrowhead=2, arrowcolor="#2563EB",
            arrowsize=1.2, arrowwidth=1.5, ax=40, ay=-40,
            font=dict(size=11, color="#2563EB", family="Plus Jakarta Sans"),
            bgcolor="rgba(37,99,235,0.08)", bordercolor="#2563EB",
            borderwidth=1, borderpad=4
        )

        fig_hero.update_layout(
            plot_bgcolor="#fff", paper_bgcolor="#fff",
            font=dict(family="Inter, sans-serif", color="#374151"),
            height=360, margin=dict(l=10, r=20, t=10, b=70),
            hovermode="x unified",
            hoverlabel=dict(bgcolor="#0A2540", font_color="#fff",
                            font_family="Inter", font_size=12, bordercolor="#0A2540"),
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.28,
                xanchor="center", x=0.5,
                bgcolor="rgba(0,0,0,0)",
                font=dict(size=11, color="#374151"),
                itemsizing="constant", traceorder="reversed"
            ),
            xaxis=dict(showgrid=True, gridcolor="#F3F4F6", gridwidth=1,
                       tickfont=dict(size=10, color="#6B7280"),
                       showline=True, linecolor="#E5E7EB", zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="#F3F4F6", gridwidth=1,
                       tickfont=dict(size=10, color="#6B7280"),
                       title=dict(text="Employees", font=dict(size=10, color="#9CA3AF")),
                       zeroline=False),
        )
        st.plotly_chart(fig_hero, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div></div>", unsafe_allow_html=True)

    with col_side:
        dept_df = df25.groupby("Department")["Value"].sum().reset_index().sort_values("Value", ascending=False)
        max_val = int(dept_df["Value"].max()) if len(dept_df) else 1
        st.markdown('<div class="dept-card"><div class="dept-title">Dept Contribution · 2025</div>', unsafe_allow_html=True)
        blues = ["#1D4ED8","#2563EB","#3B82F6","#60A5FA","#93C5FD","#BAE6FD","#DBEAFE","#EFF6FF"]
        for i, (_, row) in enumerate(dept_df.iterrows()):
            pct = int(row["Value"] / max_val * 100) if max_val > 0 else 0
            bar_color = blues[min(i, len(blues)-1)]
            st.markdown(f"""
            <div style="margin-bottom:11px">
              <div style="display:flex;justify-content:space-between;margin-bottom:3px">
                <span style="font-size:11px;font-weight:500;color:#374151">{row['Department']}</span>
                <span style="font-size:11px;font-weight:700;color:#2563EB">{int(row['Value'])}</span>
              </div>
              <div style="background:#F3F4F6;border-radius:4px;height:8px;overflow:hidden">
                <div style="background:{bar_color};width:{pct}%;height:100%;border-radius:4px;
                            transition:width 0.3s ease"></div>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ══ INDIVIDUAL PROGRAM CHARTS ══════════════════════════════════════════
    CHART_BG = dict(
        plot_bgcolor="#fff", paper_bgcolor="#fff",
        font=dict(family="Inter, sans-serif", color="#374151"),
        margin=dict(l=6, r=6, t=34, b=8),
        xaxis=dict(showgrid=False, tickfont=dict(size=9, color="#9CA3AF"),
                   showline=True, linecolor="#E5E7EB"),
        yaxis=dict(showgrid=True, gridcolor="#F9FAFB",
                   tickfont=dict(size=9, color="#9CA3AF"), zeroline=False),
    )

    # Bronze
    st.markdown("""<div class="sec-hdr" style="margin-top:6px">
      <div class="sec-dot" style="background:#C07830"></div>
      <div class="sec-title">🥉 Bronze Elements — 5S · AD · SPS · VPM · LSW</div>
      <div class="sec-line"></div>
    </div>""", unsafe_allow_html=True)

    bronze_progs = [p for p in programs if tiers[p]=="Bronze"]
    cols = st.columns(len(bronze_progs))
    for col, prog in zip(cols, bronze_progs):
        pd_ = df[df["Program"]==prog].groupby("Period")["Value"].sum().reset_index()
        pd_["Period"] = pd.Categorical(pd_["Period"], categories=PERIODS, ordered=True)
        pd_ = pd_.sort_values("Period")
        pd_ = pd_[pd_["Value"] > 0]
        c = prog_color[prog]
        # subtle gradient fill using rgba
        cr = int(c[1:3],16); cg = int(c[3:5],16); cb = int(c[5:7],16)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=pd_["Period"], y=pd_["Value"],
            marker_color=f"rgba({cr},{cg},{cb},0.80)",
            marker_line_width=0, marker_cornerradius=5,
            hovertemplate=f"<b>{prog}</b><br>%{{x}}: <b>%{{y}}</b><extra></extra>"))
        fig.update_layout(**CHART_BG, height=210,
            title=dict(text=f"<b>{prog}</b>",
                       font=dict(size=12, family="Plus Jakarta Sans", color="#0A2540"), x=0.5))
        col.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # Silver + Gold
    st.markdown("""<div class="sec-hdr">
      <div class="sec-dot" style="background:#607080"></div>
      <div class="sec-title">🥈🥇 Silver & Gold Elements — PM · QCO · SMED · SW · AD Silver · OAC</div>
      <div class="sec-line"></div>
    </div>""", unsafe_allow_html=True)

    sg_progs = [p for p in programs if tiers[p] in ("Silver","Gold")]
    cols = st.columns(len(sg_progs))
    for col, prog in zip(cols, sg_progs):
        pd_ = df[df["Program"]==prog].groupby("Period")["Value"].sum().reset_index()
        pd_["Period"] = pd.Categorical(pd_["Period"], categories=PERIODS, ordered=True)
        pd_ = pd_.sort_values("Period")
        pd_ = pd_[pd_["Value"] > 0]
        c = prog_color[prog]
        cr = int(c[1:3],16); cg = int(c[3:5],16); cb = int(c[5:7],16)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=pd_["Period"], y=pd_["Value"],
            marker_color=f"rgba({cr},{cg},{cb},0.80)",
            marker_line_width=0, marker_cornerradius=5,
            hovertemplate=f"<b>{prog}</b><br>%{{x}}: <b>%{{y}}</b><extra></extra>"))
        fig.update_layout(**CHART_BG, height=210,
            title=dict(text=f"<b>{prog}</b>",
                       font=dict(size=12, family="Plus Jakarta Sans", color="#0A2540"), x=0.5))
        col.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # Bottom row
    st.markdown("""<div class="sec-hdr">
      <div class="sec-dot" style="background:#16A34A"></div>
      <div class="sec-title">Comparative Analysis</div>
      <div class="sec-line"></div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        tier_df = df[df["Period"].isin(["2023","2024","2025"])].groupby(["Tier","Period"])["Value"].sum().reset_index()
        fig_tier = px.bar(tier_df, x="Period", y="Value", color="Tier", barmode="group",
                          title="<b>Bronze vs Silver vs Gold — Year on Year</b>",
                          color_discrete_map={"Bronze":"#C07830","Silver":"#8090A0","Gold":"#C8A010"})
        fig_tier.update_layout(**CHART_BG, height=290,
            title=dict(font=dict(size=13, family="Plus Jakarta Sans", color="#0A2540"), x=0.5),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11),
                        orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5))
        fig_tier.update_traces(marker_cornerradius=4)
        st.plotly_chart(fig_tier, use_container_width=True, config={"displayModeBar":False})

    with c2:
        heat_df = df.groupby(["Program","Period"])["Value"].sum().reset_index()
        heat_pivot = heat_df.pivot(index="Program", columns="Period", values="Value").fillna(0)
        heat_pivot = heat_pivot[[p for p in PERIODS if p in heat_pivot.columns]]
        fig_heat = go.Figure(go.Heatmap(
            z=heat_pivot.values, x=list(heat_pivot.columns), y=list(heat_pivot.index),
            colorscale=[[0,"#F0F4FF"],[0.4,"#93C5FD"],[1,"#1D4ED8"]],
            showscale=True, colorbar=dict(thickness=10, len=0.8, tickfont=dict(size=9)),
            hovertemplate="<b>%{y}</b><br>%{x}: <b>%{z}</b><extra></extra>"))
        fig_heat.update_layout(
            plot_bgcolor="#fff", paper_bgcolor="#fff",
            font=dict(family="Inter", color="#374151"),
            margin=dict(l=6, r=6, t=34, b=8), height=290,
            title=dict(text="<b>Element × Period Growth Map</b>",
                       font=dict(size=13, family="Plus Jakarta Sans", color="#0A2540"), x=0.5),
            xaxis=dict(tickfont=dict(size=8, color="#9CA3AF")),
            yaxis=dict(tickfont=dict(size=9, color="#374151")))
        st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar":False})

# ══════════════════════════════════════════════════════════════════════════
with tab_edit:
    st.markdown("""<div class="edit-banner">
    ✏️  <b>Edit Data</b> — Choose an element, update numbers, click Save.
    All charts on the Overview tab update immediately.
    </div>""", unsafe_allow_html=True)

    prog_list = list(data["programs"].keys())
    sel_prog  = st.selectbox("Select Element", prog_list,
                             format_func=lambda p: f"{p}  [{data['programs'][p]['tier']}]")

    tier = data["programs"][sel_prog]["tier"]
    tc   = TIER_COLORS[tier]
    pc   = PROG_PALETTE[prog_list.index(sel_prog)]

    st.markdown(f"""<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
      <div style="width:12px;height:12px;background:{tc['main']};border-radius:50%"></div>
      <span style="font-family:'Plus Jakarta Sans';font-size:18px;font-weight:800;color:#0A2540">{sel_prog}</span>
      <span style="background:{tc['light']};color:{tc['text']};border:1px solid {tc['border']};
                   padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600">{tier}</span>
    </div>""", unsafe_allow_html=True)

    dept_data = data["programs"][sel_prog]["departments"]
    edit_df   = pd.DataFrame(dept_data, index=PERIODS).T.reset_index().rename(columns={"index":"Department"})

    edited = st.data_editor(edit_df, use_container_width=True, hide_index=True, num_rows="fixed",
        column_config={
            "Department": st.column_config.TextColumn("Department", disabled=True, width="medium"),
            **{p: st.column_config.NumberColumn(p, min_value=0, max_value=9999, step=1, width="small")
               for p in PERIODS}
        })

    st.markdown("##### Live Preview — Element Total by Period")
    preview = edited.drop("Department", axis=1).sum().reset_index()
    preview.columns = ["Period","Total"]
    preview["Period"] = pd.Categorical(preview["Period"], categories=PERIODS, ordered=True)
    preview = preview.sort_values("Period")
    cr = int(pc[1:3],16); cg = int(pc[3:5],16); cb_val = int(pc[5:7],16)
    fig_prev = go.Figure()
    fig_prev.add_trace(go.Bar(x=preview["Period"], y=preview["Total"],
        marker_color=f"rgba({cr},{cg},{cb_val},0.8)", marker_cornerradius=4, marker_line_width=0,
        hovertemplate="%{x}: <b>%{y}</b><extra></extra>"))
    fig_prev.update_layout(plot_bgcolor="#fff", paper_bgcolor="#F7F8FA",
        font=dict(family="Inter"), height=180, margin=dict(l=6,r=6,t=6,b=6),
        xaxis=dict(showgrid=False, tickfont=dict(size=9, color="#9CA3AF")),
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6", tickfont=dict(size=9, color="#9CA3AF")))
    st.plotly_chart(fig_prev, use_container_width=True, config={"displayModeBar":False})

    col_btn, col_msg = st.columns([1,3])
    with col_btn:
        if st.button("💾  Save Changes", type="primary", use_container_width=True):
            for _, row in edited.iterrows():
                dept = row["Department"]
                vals = [int(row[p]) for p in PERIODS]
                st.session_state.data["programs"][sel_prog]["departments"][dept] = vals
            save_data(st.session_state.data)
            with col_msg:
                st.success("✅ Saved! Go to **Overview & Charts** tab to see updated charts.")
