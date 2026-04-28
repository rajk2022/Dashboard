import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json, os, copy

# ── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Training Certification Dashboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CONSTANTS ──────────────────────────────────────────────────────────────
DATA_FILE   = os.path.join(os.path.dirname(__file__), "dashboard_data.json")
PERIODS     = ["2023","2024","2025","Jan-26","Feb-26","Mar-26","Apr-26",
               "May-26","Jun-26","Jul-26","Aug-26","Sep-26","Oct-26","Nov-26","Dec-26"]
DEPARTMENTS = ["Project","Molding","Production","SCM","Maintenance","QA","HR","Finance"]
TIER_ORDER  = ["Bronze","Silver","Gold"]

TIER_COLORS = {
    "Bronze": {"main":"#C07830","light":"#FEF0E0","dark":"#7A4A10","text":"#5A3010"},
    "Silver": {"main":"#6A7A8C","light":"#EEF2F6","dark":"#3A4A5A","text":"#2A3A4A"},
    "Gold":   {"main":"#B8960C","main":"#C8A010","light":"#FFFAE0","dark":"#7A6000","text":"#5A4000"},
}
PROG_COLORS = px.colors.qualitative.Bold

# ── LOAD / SAVE DATA ───────────────────────────────────────────────────────
def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def to_flat_df(data):
    rows = []
    for prog, pdata in data["programs"].items():
        for dept, vals in pdata["departments"].items():
            for i, period in enumerate(PERIODS):
                rows.append({
                    "Program": prog,
                    "Tier": pdata["tier"],
                    "Department": dept,
                    "Period": period,
                    "Certifications": int(vals[i])
                })
    return pd.DataFrame(rows)

# ── STYLES ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&family=Barlow:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Barlow', sans-serif; }

.main { background: #0E1520; }
[data-testid="stAppViewContainer"] { background: #0E1520; }
[data-testid="stHeader"] { background: transparent; }

.dash-header {
    background: linear-gradient(135deg, #0E1520 0%, #162240 50%, #1A2A50 100%);
    border-bottom: 3px solid #3A8FD8;
    padding: 18px 28px 14px;
    border-radius: 10px;
    margin-bottom: 16px;
}
.dash-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #fff;
    line-height: 1;
}
.dash-title span { color: #3A8FD8; }
.dash-sub {
    font-size: 0.72rem;
    color: #6A7A90;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 4px;
}

.kpi-card {
    background: #161F30;
    border: 1px solid #2A3850;
    border-radius: 8px;
    padding: 14px 18px;
    text-align: center;
}
.kpi-val {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2rem;
    font-weight: 900;
    line-height: 1;
}
.kpi-lbl {
    font-size: 0.65rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #6A7A90;
    margin-top: 3px;
}

.section-hdr {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 6px 14px;
    border-radius: 5px;
    margin: 18px 0 10px;
    display: inline-block;
}
.bronze-hdr { background: #7A4A10; color: #FEF0E0; border-left: 4px solid #C07830; }
.silver-hdr { background: #3A4A5A; color: #D8E0E8; border-left: 4px solid #8899AA; }
.gold-hdr   { background: #7A6000; color: #FFFAE0; border-left: 4px solid #C8A010; }
.master-hdr { background: #0A1428; color: #3A8FD8;  border-left: 4px solid #3A8FD8; }

.edit-banner {
    background: linear-gradient(90deg, #1A3A1A, #1E4A1E);
    border: 1px solid #2A6A2A;
    border-radius: 8px;
    padding: 12px 18px;
    margin-bottom: 16px;
    color: #90D890;
    font-size: 0.85rem;
}

.stTabs [data-baseweb="tab-list"] {
    background: #161F30;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #2A3850;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #6A7A90;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    border-radius: 6px;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background: #3A8FD8 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ── INIT SESSION STATE ─────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# ── HEADER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <div class="dash-title">Training <span>Certification</span> Dashboard</div>
  <div class="dash-sub">
    Programs: 5S · AD · SPS · VPM · LSW · PM · QCO · SMED · SW · AD Silver · OAC &nbsp;|&nbsp;
    Depts: Project · Molding · Production · SCM · Maintenance · QA · HR · Finance
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────
tab_dash, tab_edit = st.tabs(["📊  Dashboard", "✏️  Edit Data"])

# ══════════════════════════════════════════════════════════════════════════
#  TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════
with tab_dash:

    df = to_flat_df(data)
    programs = list(data["programs"].keys())
    tiers = {p: data["programs"][p]["tier"] for p in programs}

    # ── KPI ROW ──────────────────────────────────────────────────────────
    df25 = df[df["Period"] == "2025"]
    grand  = int(df25["Certifications"].sum())
    bronze = int(df25[df25["Tier"]=="Bronze"]["Certifications"].sum())
    silver = int(df25[df25["Tier"]=="Silver"]["Certifications"].sum())
    gold   = int(df25[df25["Tier"]=="Gold"]["Certifications"].sum())
    total23 = int(df[df["Period"]=="2023"]["Certifications"].sum())
    total24 = int(df[df["Period"]=="2024"]["Certifications"].sum())
    apr26  = int(df[df["Period"]=="Apr-26"]["Certifications"].sum())

    k1,k2,k3,k4,k5,k6,k7 = st.columns(7)
    def kpi(col, val, label, color):
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-val" style="color:{color}">{val}</div>
          <div class="kpi-lbl">{label}</div>
        </div>""", unsafe_allow_html=True)

    kpi(k1, grand,   "Grand Total 2025",  "#3A8FD8")
    kpi(k2, bronze,  "🥉 Bronze 2025",     "#C07830")
    kpi(k3, silver,  "🥈 Silver 2025",     "#99AABC")
    kpi(k4, gold,    "🥇 Gold 2025",       "#C8A010")
    kpi(k5, total23, "Total 2023",         "#3A8FD8")
    kpi(k6, total24, "Total 2024",         "#3A8FD8")
    kpi(k7, apr26,   "Planned Apr-26",     "#50D890")

    st.markdown("<br>", unsafe_allow_html=True)

    PLOT_BG   = "#0E1520"
    PAPER_BG  = "#161F30"
    GRID_COL  = "rgba(255,255,255,0.06)"
    TICK_COL  = "#6A7A90"
    FONT_FAM  = "Barlow, sans-serif"

    base_layout = dict(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(family=FONT_FAM, color="#E8EDF5"),
        margin=dict(l=10, r=10, t=36, b=10),
        xaxis=dict(gridcolor=GRID_COL, tickfont=dict(color=TICK_COL, size=10)),
        yaxis=dict(gridcolor=GRID_COL, tickfont=dict(color=TICK_COL, size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
    )

    # ── BRONZE ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr bronze-hdr">🥉  Bronze Programs — 5S · AD · SPS · VPM · LSW</div>', unsafe_allow_html=True)
    bronze_progs = [p for p in programs if tiers[p]=="Bronze"]
    cols = st.columns(len(bronze_progs))
    for col, prog in zip(cols, bronze_progs):
        prog_df = df[df["Program"]==prog].groupby("Period")["Certifications"].sum().reset_index()
        prog_df["Period"] = pd.Categorical(prog_df["Period"], categories=PERIODS, ordered=True)
        prog_df = prog_df.sort_values("Period")
        prog_df = prog_df[prog_df["Certifications"]>0]
        fig = px.bar(prog_df, x="Period", y="Certifications",
                     title=f"<b>{prog}</b>",
                     color_discrete_sequence=["#C07830"])
        fig.update_layout(**base_layout, height=220,
                          title=dict(font=dict(size=13, family="Barlow Condensed", color="#FEF0E0"), x=0.5))
        fig.update_traces(marker_line_width=0, marker_cornerradius=3)
        col.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── SILVER + GOLD ─────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr silver-hdr">🥈🥇  Silver & Gold Programs — PM · QCO · SMED · SW · AD Silver · OAC</div>', unsafe_allow_html=True)
    sg_progs = [p for p in programs if tiers[p] in ("Silver","Gold")]
    cols = st.columns(len(sg_progs))
    for col, prog in zip(cols, sg_progs):
        prog_df = df[df["Program"]==prog].groupby("Period")["Certifications"].sum().reset_index()
        prog_df["Period"] = pd.Categorical(prog_df["Period"], categories=PERIODS, ordered=True)
        prog_df = prog_df.sort_values("Period")
        prog_df = prog_df[prog_df["Certifications"]>0]
        color = "#C8A010" if tiers[prog]=="Gold" else "#8899AA"
        fig = px.bar(prog_df, x="Period", y="Certifications",
                     title=f"<b>{prog}</b>",
                     color_discrete_sequence=[color])
        fig.update_layout(**base_layout, height=220,
                          title=dict(font=dict(size=13, family="Barlow Condensed",
                                               color="#FFFAE0" if tiers[prog]=="Gold" else "#D8E0E8"), x=0.5))
        fig.update_traces(marker_line_width=0, marker_cornerradius=3)
        col.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── MASTER CHARTS ROW ─────────────────────────────────────────────────
    st.markdown('<div class="section-hdr master-hdr">📈  Master Overview — All Programs</div>', unsafe_allow_html=True)
    c_left, c_right = st.columns([2, 1])

    with c_left:
        # Trend line — all programs
        trend_df = df.groupby(["Program","Period"])["Certifications"].sum().reset_index()
        trend_df["Period"] = pd.Categorical(trend_df["Period"], categories=PERIODS, ordered=True)
        trend_df = trend_df.sort_values(["Program","Period"])
        fig_trend = px.line(trend_df, x="Period", y="Certifications", color="Program",
                            title="<b>All Programs — Certification Trend</b>",
                            color_discrete_sequence=PROG_COLORS,
                            markers=True)
        fig_trend.update_layout(**base_layout, height=320,
                                title=dict(font=dict(size=14, family="Barlow Condensed"), x=0.5),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.35))
        fig_trend.update_traces(line=dict(width=2.5), marker=dict(size=5))
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

    with c_right:
        # Dept breakdown — 2025
        dept_df = df25.groupby("Department")["Certifications"].sum().reset_index().sort_values("Certifications", ascending=True)
        fig_dept = px.bar(dept_df, x="Certifications", y="Department",
                          orientation="h",
                          title="<b>Dept Total — 2025</b>",
                          color="Certifications",
                          color_continuous_scale=["#1A3A5A","#3A8FD8"])
        fig_dept.update_layout(**base_layout, height=320, coloraxis_showscale=False,
                               title=dict(font=dict(size=14, family="Barlow Condensed"), x=0.5))
        fig_dept.update_traces(marker_cornerradius=3)
        st.plotly_chart(fig_dept, use_container_width=True, config={"displayModeBar": False})

    # ── BOTTOM ROW ────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        # Tier comparison bar
        tier_df = df[df["Period"].isin(["2023","2024","2025"])].groupby(["Tier","Period"])["Certifications"].sum().reset_index()
        fig_tier = px.bar(tier_df, x="Period", y="Certifications", color="Tier",
                          barmode="group",
                          title="<b>Bronze vs Silver vs Gold — Year Comparison</b>",
                          color_discrete_map={"Bronze":"#C07830","Silver":"#8899AA","Gold":"#C8A010"})
        fig_tier.update_layout(**base_layout, height=280,
                               title=dict(font=dict(size=13, family="Barlow Condensed"), x=0.5))
        fig_tier.update_traces(marker_cornerradius=3)
        st.plotly_chart(fig_tier, use_container_width=True, config={"displayModeBar": False})

    with c2:
        # Heatmap — program × period
        heat_df = df.groupby(["Program","Period"])["Certifications"].sum().reset_index()
        heat_pivot = heat_df.pivot(index="Program", columns="Period", values="Certifications").fillna(0)
        heat_pivot = heat_pivot[[p for p in PERIODS if p in heat_pivot.columns]]
        fig_heat = go.Figure(go.Heatmap(
            z=heat_pivot.values,
            x=list(heat_pivot.columns),
            y=list(heat_pivot.index),
            colorscale=[[0,"#0E1520"],[0.3,"#1B3A5C"],[1,"#3A8FD8"]],
            showscale=False,
            hovertemplate="<b>%{y}</b><br>%{x}: %{z}<extra></extra>"
        ))
        fig_heat.update_layout(**base_layout, height=280,
                               title=dict(text="<b>Heatmap — Program × Period</b>",
                                          font=dict(size=13, family="Barlow Condensed"), x=0.5))
        st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════
#  TAB 2 — EDIT DATA
# ══════════════════════════════════════════════════════════════════════════
with tab_edit:
    st.markdown("""
    <div class="edit-banner">
    ✏️  <b>Edit Mode</b> — Select a program below, edit the table, then click <b>Save Changes</b>.
    The dashboard updates instantly with your new numbers.
    </div>
    """, unsafe_allow_html=True)

    # Program selector
    prog_list = list(data["programs"].keys())
    sel_prog = st.selectbox(
        "Select Program to Edit",
        prog_list,
        format_func=lambda p: f"{p}  [{data['programs'][p]['tier']}]"
    )

    tier = data["programs"][sel_prog]["tier"]
    tier_col = {"Bronze":"#C07830","Silver":"#8899AA","Gold":"#C8A010"}[tier]

    st.markdown(f"### <span style='color:{tier_col}'>{sel_prog}</span> &nbsp;<small style='color:#6A7A90;font-size:0.7em'>{tier} Level</small>", unsafe_allow_html=True)
    st.caption("Edit numbers directly in the table below. 0 = no certifications that period.")

    # Build editable dataframe
    dept_data = data["programs"][sel_prog]["departments"]
    edit_df = pd.DataFrame(dept_data, index=PERIODS).T
    edit_df.index.name = "Department"
    edit_df = edit_df.reset_index()

    edited = st.data_editor(
        edit_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Department": st.column_config.TextColumn("Department", disabled=True, width="medium"),
            **{p: st.column_config.NumberColumn(p, min_value=0, max_value=999, step=1, width="small")
               for p in PERIODS}
        }
    )

    # Live preview while editing
    st.markdown("##### Live Preview — Totals")
    preview_totals = edited.drop("Department", axis=1).sum().reset_index()
    preview_totals.columns = ["Period","Total"]
    preview_totals["Period"] = pd.Categorical(preview_totals["Period"], categories=PERIODS, ordered=True)
    preview_totals = preview_totals.sort_values("Period")

    fig_prev = px.bar(preview_totals, x="Period", y="Total",
                      color_discrete_sequence=[tier_col])
    fig_prev.update_layout(
        plot_bgcolor="#0E1520", paper_bgcolor="#161F30",
        font=dict(family="Barlow, sans-serif", color="#E8EDF5"),
        margin=dict(l=10,r=10,t=10,b=10), height=200,
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#6A7A90",size=10)),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#6A7A90",size=10)),
    )
    fig_prev.update_traces(marker_cornerradius=3)
    st.plotly_chart(fig_prev, use_container_width=True, config={"displayModeBar":False})

    # Save button
    col_btn, col_msg = st.columns([1,3])
    with col_btn:
        if st.button("💾  Save Changes", type="primary", use_container_width=True):
            # Write back to data structure
            for _, row in edited.iterrows():
                dept = row["Department"]
                vals = [int(row[p]) for p in PERIODS]
                st.session_state.data["programs"][sel_prog]["departments"][dept] = vals
            save_data(st.session_state.data)
            with col_msg:
                st.success(f"✅ {sel_prog} data saved! Switch to Dashboard tab to see updated charts.")

    st.divider()
    st.caption("💡 Tip: After saving, click the **📊 Dashboard** tab — all charts refresh automatically with your new numbers.")
