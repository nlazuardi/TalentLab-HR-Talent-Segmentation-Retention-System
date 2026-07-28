"""
TalentLab — HR Talent Segmentation Dashboard
Gaya visual terinspirasi ScoutLab/TeamsLab (dark scouting aesthetic).
Jalankan:  streamlit run app.py
Data:      hr_talent_matrix.xlsx (satu folder dengan app.py)
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ══════════════════════════════ CONFIG ══════════════════════════════

st.set_page_config(
    page_title="TalentLab — HR Talent Segmentation",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

ACCENT = "#2DE0BE"
DANGER = "#FF5C5C"
WARN = "#FFC53D"
MUTED = "#8A93AD"
TEXT = "#E8ECF5"
CARD_BG = "rgba(19,26,48,0.72)"
CARD_BORDER = "rgba(124,140,190,0.18)"

PERSONA_COLORS = {
    "The At-Risk Employee": "#FF7A2F",
    "The Loyal Performer": "#FF3D77",
    "The Established Performer": "#4D9FFF",
    "The Declining Performer": "#FFC53D",
    "The Rising Star": "#3DDC6A",
}
PERSONA_SHORT = {
    "The At-Risk Employee": "AT-RISK EMPLOYEE",
    "The Loyal Performer": "LOYAL PERFORMER",
    "The Established Performer": "ESTABLISHED PERFORMER",
    "The Declining Performer": "DECLINING PERFORMER",
    "The Rising Star": "RISING STAR",
}
TIER_ORDER = ["🔴 Critical", "🟡 Watchlist", "🟢 Stable"]

FEATS = ["PerformanceScore", "JobSatisfaction", "YearsAtCompany", "MonthlyIncome"]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
  background:
    radial-gradient(1200px 600px at 85% -10%, rgba(124,92,255,0.16), transparent 60%),
    radial-gradient(900px 500px at -10% 110%, rgba(45,224,190,0.10), transparent 55%),
    linear-gradient(160deg, #0B0E1A 0%, #10162B 55%, #0B0E1A 100%);
  color: #E8ECF5;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0A0D18 0%, #0D1122 100%);
  border-right: 1px solid rgba(124,140,190,0.15);
}
[data-testid="stSidebar"] * { color: #C9D2E8; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.stAppDeployButton, [data-testid="stMainMenu"] { display: none; }
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapseButton"] {
  visibility: visible !important; display: inline-flex !important;
}
[data-testid="stExpandSidebarButton"] svg,
[data-testid="stSidebarCollapseButton"] svg { color: #2DE0BE !important; }

h1, h2, h3 { font-family: 'Chakra Petch', sans-serif !important; letter-spacing: 0.5px; }

.tl-logo {
  font-family: 'Chakra Petch', sans-serif; font-weight: 700; font-size: 26px;
  color: #FFFFFF; letter-spacing: 1px; margin-bottom: 0px;
}
.tl-logo span { color: #2DE0BE; }
.tl-sub {
  font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 2.5px;
  color: #8A93AD; text-transform: uppercase; margin-bottom: 18px;
}
.tl-eyebrow {
  font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 3px;
  color: #2DE0BE; text-transform: uppercase; margin-bottom: 2px;
}
.tl-card {
  background: rgba(19,26,48,0.72);
  border: 1px solid rgba(124,140,190,0.18);
  border-radius: 14px; padding: 18px 20px; margin-bottom: 14px;
}
.tl-kpi-label {
  font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 2px;
  color: #8A93AD; text-transform: uppercase;
}
.tl-kpi-value { font-family: 'Chakra Petch', sans-serif; font-size: 30px; font-weight: 700; color: #FFFFFF; }
.tl-kpi-note { font-size: 12px; color: #8A93AD; }

.stDataFrame { border: 1px solid rgba(124,140,190,0.18); border-radius: 12px; }
div[data-baseweb="select"] > div {
  background: rgba(19,26,48,0.9); border-color: rgba(124,140,190,0.25);
}
.stRadio label, .stCheckbox label { color: #C9D2E8 !important; }
</style>
"""


# ══════════════════════════════ DATA ══════════════════════════════

@st.cache_data
def load_data():
    emp = pd.read_excel("hr_talent_matrix.xlsx", sheet_name="Employee Scores")
    summary = pd.read_excel("hr_talent_matrix.xlsx", sheet_name="Cluster Summary")
    profile = pd.read_excel("hr_talent_matrix.xlsx", sheet_name="Cluster Profile")
    tier_ct = pd.read_excel("hr_talent_matrix.xlsx", sheet_name="Persona x Tier")
    rekom_ct = pd.read_excel("hr_talent_matrix.xlsx", sheet_name="Persona x Rekomendasi")
    dept_sum = pd.read_excel("hr_talent_matrix.xlsx", sheet_name="Department Summary")
    dept_ct = pd.read_excel("hr_talent_matrix.xlsx", sheet_name="Department x Persona")

    # percentile rank per fitur (0-100) — konsisten dengan norm() di rumus
    pct = emp[FEATS].rank(pct=True) * 100
    pct.columns = [c + "_pct" for c in FEATS]
    emp = pd.concat([emp, pct.round(0).astype(int)], axis=1)

    # ranking prioritas
    emp = emp.sort_values("Priority", ascending=False).reset_index(drop=True)
    emp["PriorityRank"] = np.arange(1, len(emp) + 1)

    # jitter deterministik untuk sumbu engagement (nilai diskrit)
    rng = np.random.default_rng(42)
    emp["_jit"] = emp["Engagement"] + rng.uniform(-0.022, 0.022, len(emp))
    return emp, summary, profile, tier_ct, rekom_ct, dept_sum, dept_ct


@st.cache_data
def similarity_matrix(emp: pd.DataFrame):
    """Euclidean distance di ruang 4 fitur ter-percentile (0-1)."""
    X = emp[[c + "_pct" for c in FEATS]].to_numpy() / 100.0
    d = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(-1))
    return d  # (n, n)


@st.cache_data
def fit_predictor(emp: pd.DataFrame):
    """Parameter untuk memprediksi input baru.

    Assignment cluster memakai nearest-centroid di ruang ter-standarisasi —
    ekuivalen eksak dengan aturan assignment KMeans (terverifikasi 100% match
    terhadap 1.000 label existing)."""
    mu = emp[FEATS].mean()
    sd = emp[FEATS].std(ddof=0)  # ddof=0 = StandardScaler
    z = (emp[FEATS] - mu) / sd
    centroids = z.groupby(emp["Persona"]).mean()
    q50, q75 = emp["Priority"].quantile([0.50, 0.75])
    return mu, sd, centroids, float(q50), float(q75)


def pct_of(pop: pd.Series, v: float) -> float:
    """Percentile rank (0-1) nilai baru terhadap populasi, konvensi midrank."""
    pop = pop.to_numpy()
    return float(((pop < v).sum() + 0.5 * (pop == v).sum()) / len(pop))


def predict_employee(emp, mu, sd, centroids, q50, q75,
                     perf, js, tenure, income):
    # 1) cluster assignment — nearest centroid (≡ KMeans.predict)
    x = pd.Series({"PerformanceScore": perf, "JobSatisfaction": js,
                   "YearsAtCompany": tenure, "MonthlyIncome": income})
    z = (x - mu) / sd
    d = ((centroids - z) ** 2).sum(axis=1)
    persona = d.idxmin()

    # 2) rumus — percentile terhadap populasi existing
    p = {f: pct_of(emp[f], x[f]) for f in FEATS}
    risk_js = 1 - p["JobSatisfaction"]
    risk_gap = max(0.0, p["PerformanceScore"] - p["MonthlyIncome"])
    turnover = (risk_js + risk_gap) / 2
    impact = (p["PerformanceScore"] + p["MonthlyIncome"] + p["YearsAtCompany"]) / 3
    priority = turnover * impact
    engagement = p["JobSatisfaction"]

    # 3) tier, level, rekomendasi — aturan yang sama dengan pipeline notebook
    tier = "🔴 Critical" if priority >= q75 else ("🟡 Watchlist" if priority >= q50 else "🟢 Stable")
    eng_level = "Disengaged" if js <= 2 else ("Neutral" if js == 3 else "Engaged")
    if priority >= q50:
        if risk_gap > risk_js:
            rekom = "Compensation Review"
        elif risk_js >= 0.5:
            rekom = "Engagement Intervention"
        else:
            rekom = "Protect: Career Growth"
    else:
        rekom = "Performance Coaching" if p["PerformanceScore"] < 0.4 else "Maintain & Develop"

    rank = int((emp["Priority"] > priority).sum()) + 1
    return dict(persona=persona, pct=p, RiskJS=risk_js, RiskGap=risk_gap,
                TurnoverRisk=turnover, Impact=impact, Priority=priority,
                Engagement=engagement, tier=tier, eng_level=eng_level,
                rekom=rekom, rank=rank)


# ══════════════════════════════ HTML HELPERS ══════════════════════════════

def bar_color(value, risk=False):
    """Warna bar: metrik positif (tinggi=teal) vs metrik risiko (tinggi=merah)."""
    v = value if not risk else 100 - value
    if v >= 65:
        return ACCENT
    if v >= 38:
        return WARN
    return DANGER


def bar_row(label, value, risk=False, sub=False):
    color = bar_color(value, risk)
    indent = "18px" if sub else "0"
    lbl_color = MUTED if sub else TEXT
    size = "11px" if sub else "12px"
    prefix = "&#8627;&nbsp;" if sub else ""
    return f"""
    <div style="display:flex;align-items:center;gap:12px;margin:7px 0 7px {indent};">
      <div style="flex:0 0 210px;font-family:'JetBrains Mono',monospace;font-size:{size};
                  letter-spacing:1.5px;color:{lbl_color};text-transform:uppercase;">{prefix}{label}</div>
      <div style="flex:1;height:9px;background:rgba(124,140,190,0.14);border-radius:6px;overflow:hidden;">
        <div style="width:{value}%;height:100%;background:{color};border-radius:6px;"></div>
      </div>
      <div style="flex:0 0 34px;text-align:right;font-family:'JetBrains Mono',monospace;
                  font-weight:700;font-size:13px;color:{color};">{value:.0f}</div>
    </div>"""


def chip(label, value, color=ACCENT):
    return f"""
    <div style="background:rgba(13,18,36,0.85);border:1px solid rgba(124,140,190,0.22);
                border-radius:10px;padding:9px 16px;min-width:118px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:2px;
                  color:{MUTED};text-transform:uppercase;">{label}</div>
      <div style="font-family:'Chakra Petch',sans-serif;font-weight:600;font-size:17px;
                  color:{color};margin-top:2px;">{value}</div>
    </div>"""


def page_header(eyebrow, title, desc=""):
    d = f'<div style="color:{MUTED};font-size:13px;margin-top:2px;">{desc}</div>' if desc else ""
    st.markdown(
        f"""<div style="margin-bottom:16px;">
        <div class="tl-eyebrow">{eyebrow}</div>
        <div style="font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:30px;color:#FFF;">{title}</div>
        {d}</div>""",
        unsafe_allow_html=True,
    )


def plotly_dark(fig, height=520):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=TEXT, size=12),
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", y=1.08, x=0, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="rgba(124,140,190,0.12)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(124,140,190,0.12)", zeroline=False)
    return fig


# ── radar ──
RADAR_AXES = ["PERFORMANCE", "SATISFACTION", "TENURE", "INCOME", "IMPACT", "RETENTION<br>SAFETY"]


def _rgba(hex_color, a):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


def radar_values(row):
    """6 sumbu radar (0-100), semua searah: makin luas = makin sehat."""
    return [
        row["PerformanceScore_pct"],
        row["JobSatisfaction_pct"],
        row["YearsAtCompany_pct"],
        row["MonthlyIncome_pct"],
        row["Impact"] * 100,
        (1 - row["TurnoverRisk"]) * 100,
    ]


def radar_figure(traces, height=380):
    """traces: list of (name, hex_color, values[6], filled: bool)."""
    fig = go.Figure()
    for name, color, vals, filled in traces:
        fig.add_trace(go.Scatterpolar(
            r=list(vals) + [vals[0]],
            theta=RADAR_AXES + [RADAR_AXES[0]],
            name=name,
            line=dict(color=color, width=2.5 if filled else 1.5,
                      dash=None if filled else "dot"),
            fill="toself" if filled else None,
            fillcolor=_rgba(color, 0.22) if filled else None,
        ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono", color=MUTED, size=10),
        height=height,
        margin=dict(l=50, r=50, t=40, b=30),
        legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center",
                    bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", size=11, color=TEXT)),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 100], gridcolor="rgba(124,140,190,0.18)",
                            tickfont=dict(size=8), showline=False),
            angularaxis=dict(gridcolor="rgba(124,140,190,0.18)", linecolor="rgba(124,140,190,0.25)"),
        ),
    )
    return fig


# ══════════════════════════════ PAGES ══════════════════════════════

def page_summary(emp, summary, profile, tier_ct, rekom_ct, dept_sum, dept_ct):
    page_header("OVERVIEW", "Talent Summary",
                "Ringkasan lima segmen talenta hasil KMeans (k=5) + skor prioritas retensi.")

    n_crit = int((emp["PriorityTier"] == "🔴 Critical").sum())
    n_diseng = int((emp["EngagementLevel"] == "Disengaged").sum())
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        (c1, "Total Karyawan", f"{len(emp):,}", "5 segmen persona"),
        (c2, "Critical Tier", f"{n_crit}", "top-25% skor prioritas"),
        (c3, "Disengaged", f"{n_diseng}", "JobSatisfaction ≤ 2"),
        (c4, "Mean Priority", f"{emp['Priority'].mean():.3f}", "risk × impact, skala 0–1"),
    ]
    for col, label, value, note in kpis:
        col.markdown(
            f"""<div class="tl-card" style="padding:14px 18px;">
            <div class="tl-kpi-label">{label}</div>
            <div class="tl-kpi-value">{value}</div>
            <div class="tl-kpi-note">{note}</div></div>""",
            unsafe_allow_html=True,
        )

    st.markdown("#### Cluster Summary — skor rata-rata per persona")
    s = summary.set_index("Persona")
    st.dataframe(
        s.style.background_gradient(cmap="RdYlGn_r", subset=["TurnoverRisk", "Priority"])
        .background_gradient(cmap="RdYlGn", subset=["Impact", "Engagement"])
        .format({"TurnoverRisk": "{:.3f}", "Impact": "{:.3f}",
                 "Priority": "{:.3f}", "Engagement": "{:.3f}"}),
        width='stretch',
    )

    st.markdown("#### Cluster Profile — nilai fitur asli (mean)")
    st.dataframe(
        profile.set_index("Persona").style
        .background_gradient(cmap="RdYlGn", subset=["PerformanceScore", "JobSatisfaction"])
        .background_gradient(cmap="Blues", subset=["YearsAtCompany", "MonthlyIncome"])
        .format({"PerformanceScore": "{:.2f}", "JobSatisfaction": "{:.2f}",
                 "YearsAtCompany": "{:.1f}", "MonthlyIncome": "{:,.0f}"}),
        width='stretch',
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Persona × Priority Tier")
        st.dataframe(
            tier_ct.set_index("Persona").style.background_gradient(cmap="Reds", axis=None),
            width='stretch',
        )
    with col_b:
        st.markdown("#### Persona × Rekomendasi HR")
        st.dataframe(
            rekom_ct.set_index("Persona").style.background_gradient(cmap="Purples", axis=None),
            width='stretch',
        )

    st.markdown("#### Department View — unit mana yang paling butuh perhatian")
    col_c, col_d = st.columns(2)
    with col_c:
        st.dataframe(
            dept_sum.set_index("Department").style
            .background_gradient(cmap="Reds", subset=["Critical", "MeanPriority"])
            .background_gradient(cmap="RdYlGn", subset=["MeanEngagement"])
            .format({"MeanPriority": "{:.3f}", "MeanEngagement": "{:.3f}"}),
            width="stretch",
        )
    with col_d:
        st.dataframe(
            dept_ct.set_index("Department").style.background_gradient(cmap="Oranges", axis=None),
            width="stretch",
        )


def page_matrix(emp):
    page_header("DECISION MATRIX", "Retention & Engagement Matrix",
                "X = Engagement (norm JobSatisfaction) · Y = Priority (TurnoverRisk × Impact). "
                "Garis putus-putus = median populasi.")

    f1, f2, f3, f4 = st.columns([2, 1.6, 1.6, 1])
    personas = f1.multiselect("Persona", list(PERSONA_COLORS), default=list(PERSONA_COLORS))
    depts_all = sorted(emp["Department"].unique())
    depts = f2.multiselect("Department", depts_all, default=depts_all)
    tiers = f3.multiselect("Priority Tier", TIER_ORDER, default=TIER_ORDER)
    show_emp = f4.toggle("Show employees", value=True)

    d = emp[emp["Persona"].isin(personas) & emp["PriorityTier"].isin(tiers)
            & emp["Department"].isin(depts)]
    x_mid = emp["Engagement"].median()
    y_mid = emp["Priority"].median()

    fig = go.Figure()
    if show_emp:
        for p, g in d.groupby("Persona"):
            fig.add_trace(go.Scattergl(
                x=g["_jit"], y=g["Priority"], mode="markers", name=p,
                marker=dict(size=6, color=PERSONA_COLORS[p], opacity=0.32),
                customdata=np.stack([g["EmployeeID"], g["PriorityTier"], g["Rekomendasi"], g["Department"]], axis=-1),
                hovertemplate="<b>ID %{customdata[0]}</b> — " + p +
                              " · %{customdata[3]}"
                              "<br>Priority %{y:.3f} · Engagement %{x:.2f}"
                              "<br>%{customdata[1]} · %{customdata[2]}<extra></extra>",
            ))
    cen = d.groupby("Persona")[["Engagement", "Priority"]].mean()
    pop = d.groupby("Persona").size()
    for p, row in cen.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["Engagement"]], y=[row["Priority"]], mode="markers+text",
            marker=dict(size=max(18, pop[p] / 6), color=PERSONA_COLORS[p],
                        line=dict(color="white", width=2)),
            text=[f"<b>{PERSONA_SHORT[p]}</b> (n={pop[p]})"],
            textposition="top center", textfont=dict(size=11, color="white"),
            showlegend=False,
            hovertemplate=f"<b>{p}</b><br>Priority {row['Priority']:.3f}"
                          f"<br>Engagement {row['Engagement']:.3f}<extra></extra>",
        ))
    fig.add_vline(x=x_mid, line_dash="dash", line_color="rgba(200,210,235,0.35)")
    fig.add_hline(y=y_mid, line_dash="dash", line_color="rgba(200,210,235,0.35)")
    fig.update_xaxes(title="EMPLOYEE ENGAGEMENT →")
    fig.update_yaxes(title="HR RETENTION PRIORITY →")
    st.plotly_chart(plotly_dark(fig, 560), width='stretch',
                    config={"displayModeBar": False})

    st.markdown("#### Priority Ranking — antrian intervensi")
    top = d.head(25)[["PriorityRank", "EmployeeID", "Department", "Persona", "Priority",
                      "TurnoverRisk", "Impact", "PriorityTier", "Rekomendasi"]]
    st.dataframe(
        top.set_index("PriorityRank").style
        .background_gradient(cmap="Reds", subset=["Priority", "TurnoverRisk"])
        .format({"Priority": "{:.3f}", "TurnoverRisk": "{:.3f}", "Impact": "{:.3f}"}),
        width='stretch', height=420,
    )


def page_card(emp, dist):
    page_header("EMPLOYEE CARD", "Individual Talent Report",
                "Profil skor per karyawan — percentile vs 1.000 karyawan.")

    opts = emp.apply(
        lambda r: f"#{r['PriorityRank']:>4} · ID {r['EmployeeID']} · {PERSONA_SHORT[r['Persona']]}",
        axis=1,
    )
    pick = st.selectbox("Cari karyawan (urut prioritas)", opts, index=0)
    idx = opts[opts == pick].index[0]
    e = emp.loc[idx]
    pc = PERSONA_COLORS[e["Persona"]]

    # ── header card ──
    st.markdown(
        f"""
    <div class="tl-card" style="border-left:4px solid {pc};">
      <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
        <div style="width:74px;height:74px;border-radius:50%;background:rgba(13,18,36,0.9);
                    border:3px solid {pc};display:flex;align-items:center;justify-content:center;
                    font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:20px;color:{pc};">
          {e['EmployeeID']}</div>
        <div style="flex:1;min-width:230px;">
          <span style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:2px;
                       border:1px solid {pc};color:{pc};border-radius:5px;padding:3px 9px;">
            {PERSONA_SHORT[e['Persona']]}</span>
          <span style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:2px;
                       color:{MUTED};margin-left:8px;">{e['PriorityTier']} · RANK #{e['PriorityRank']} / {len(emp)}</span>
          <div style="font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:34px;
                      color:#FFF;line-height:1.15;">EMPLOYEE {e['EmployeeID']}</div>
        </div>
      </div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:16px;">
        {chip("Department", e['Department'])}
        {chip("Gender", e['Gender'])}
        {chip("Education", e['Education'])}
        {chip("Performance", f"{e['PerformanceScore']:.0f} / 5")}
        {chip("Job Satisfaction", f"{e['JobSatisfaction']:.0f} / 5")}
        {chip("Tenure", f"{e['YearsAtCompany']:.0f} yrs")}
        {chip("Monthly Income", f"{e['MonthlyIncome']:,.0f}")}
        {chip("Rekomendasi", e['Rekomendasi'], pc)}
      </div>
    </div>""",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.15, 1])

    # ── bars ──
    with left:
        bars = '<div class="tl-card">'
        bars += ('<div class="tl-eyebrow" style="margin-bottom:10px;">SCORE COMPONENTS '
                 '<span style="color:#8A93AD;">· PERCENTILE 0–100</span></div>')
        bars += bar_row("Engagement", e["Engagement"] * 100)
        bars += bar_row("Turnover Risk", e["TurnoverRisk"] * 100, risk=True)
        bars += bar_row("Risk: Dissatisfaction", e["RiskJS"] * 100, risk=True, sub=True)
        bars += bar_row("Risk: Pay Gap", e["RiskGap"] * 100, risk=True, sub=True)
        bars += bar_row("Impact", e["Impact"] * 100)
        bars += bar_row("Priority", e["Priority"] * 100, risk=True)
        bars += ('<div class="tl-eyebrow" style="margin:16px 0 10px;">FEATURE PERCENTILES</div>')
        bars += bar_row("Performance", e["PerformanceScore_pct"])
        bars += bar_row("Job Satisfaction", e["JobSatisfaction_pct"])
        bars += bar_row("Tenure", e["YearsAtCompany_pct"])
        bars += bar_row("Income", e["MonthlyIncome_pct"])
        bars += "</div>"
        st.markdown(bars, unsafe_allow_html=True)

        # radar: karyawan vs rata-rata persona-nya
        pmean = emp[emp["Persona"] == e["Persona"]][
            ["PerformanceScore_pct", "JobSatisfaction_pct", "YearsAtCompany_pct",
             "MonthlyIncome_pct", "Impact", "TurnoverRisk"]].mean()
        st.markdown('<div class="tl-eyebrow" style="margin:4px 0 0;">EMPLOYEE RADAR</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(
            radar_figure([
                (f"ID {e['EmployeeID']}", pc, radar_values(e), True),
                (f"Avg {PERSONA_SHORT[e['Persona']]}", "#8A93AD", radar_values(pmean), False),
            ]),
            width="stretch", config={"displayModeBar": False},
        )

    # ── mini matrix + similar ──
    with right:
        fig = go.Figure()
        fig.add_trace(go.Scattergl(
            x=emp["_jit"], y=emp["Priority"], mode="markers",
            marker=dict(size=5, color="rgba(138,147,173,0.28)"),
            hoverinfo="skip", showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=[e["Engagement"]], y=[e["Priority"]], mode="markers",
            marker=dict(size=17, color=pc, line=dict(color="white", width=2.5)),
            showlegend=False,
            hovertemplate=f"ID {e['EmployeeID']}<br>Priority {e['Priority']:.3f}<extra></extra>",
        ))
        fig.add_vline(x=emp["Engagement"].median(), line_dash="dash",
                      line_color="rgba(200,210,235,0.3)")
        fig.add_hline(y=emp["Priority"].median(), line_dash="dash",
                      line_color="rgba(200,210,235,0.3)")
        fig.update_xaxes(title="ENGAGEMENT →", title_font_size=10)
        fig.update_yaxes(title="PRIORITY →", title_font_size=10)
        st.plotly_chart(plotly_dark(fig, 300), width='stretch',
                        config={"displayModeBar": False})

        # similar employees
        dr = dist[idx].copy()
        dr[idx] = np.inf
        top5 = np.argsort(dr)[:5]
        rows = ""
        for rank, j in enumerate(top5, 1):
            s = emp.loc[j]
            score = max(0.0, (1 - dr[j] / 2.0)) * 100
            sc_color = PERSONA_COLORS[s["Persona"]]
            rows += f"""
            <div style="display:flex;align-items:center;gap:12px;padding:9px 4px;
                        border-bottom:1px solid rgba(124,140,190,0.12);">
              <div style="flex:0 0 16px;color:{MUTED};font-family:'JetBrains Mono',monospace;
                          font-size:12px;">{rank}</div>
              <div style="width:10px;height:10px;border-radius:50%;background:{sc_color};"></div>
              <div style="flex:1;">
                <div style="font-weight:600;font-size:14px;color:{TEXT};">ID {s['EmployeeID']}</div>
                <div style="font-size:11px;color:{MUTED};">{PERSONA_SHORT[s['Persona']]} · {s['PriorityTier']}</div>
              </div>
              <div style="width:42px;height:42px;border-radius:50%;border:2.5px solid {ACCENT};
                          display:flex;align-items:center;justify-content:center;
                          font-family:'JetBrains Mono',monospace;font-weight:700;
                          font-size:12px;color:{ACCENT};">{score:.0f}</div>
            </div>"""
        st.markdown(
            f"""<div class="tl-card">
            <div class="tl-eyebrow" style="margin-bottom:6px;">TOP 5 MOST SIMILAR EMPLOYEES</div>
            <div style="font-size:11px;color:{MUTED};margin-bottom:6px;">
              Euclidean distance · 4 fitur ter-percentile</div>{rows}</div>""",
            unsafe_allow_html=True,
        )


def page_compare(emp):
    page_header("COMPARISON", "Employee Comparison",
                "Bandingkan 2\u20133 karyawan berdampingan \u2014 radar overlay + tabel metrik.")

    opts = emp.apply(
        lambda r: f"ID {r['EmployeeID']} \u00b7 {PERSONA_SHORT[r['Persona']]} \u00b7 rank #{r['PriorityRank']}",
        axis=1,
    )
    default = list(opts.iloc[:2])
    picks = st.multiselect("Pilih 2\u20133 karyawan", list(opts), default=default, max_selections=3)
    if len(picks) < 2:
        st.info("Pilih minimal 2 karyawan untuk dibandingkan.")
        return

    idxs = [opts[opts == p].index[0] for p in picks]
    palette = [ACCENT, "#FF3D77", "#FFC53D"]

    # header mini-card per karyawan
    cols_ = st.columns(len(idxs))
    for c, i, col_hex in zip(cols_, idxs, palette):
        s = emp.loc[i]
        pcp = PERSONA_COLORS[s["Persona"]]
        c.markdown(
            f"""<div class="tl-card" style="border-left:4px solid {col_hex};padding:14px 16px;">
            <div style="font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:22px;color:#FFF;">
              ID {s['EmployeeID']}</div>
            <span style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:1.5px;
                         border:1px solid {pcp};color:{pcp};border-radius:5px;padding:2px 8px;">
              {PERSONA_SHORT[s['Persona']]}</span>
            <div style="font-size:11px;color:{MUTED};margin-top:6px;">
              {s['Department']} \u00b7 {s['PriorityTier']} \u00b7 rank #{s['PriorityRank']}</div>
            <div style="font-size:11px;color:{MUTED};">{s['Rekomendasi']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    left, right = st.columns([1, 1])
    with left:
        traces = [
            (f"ID {emp.loc[i, 'EmployeeID']}", col_hex, radar_values(emp.loc[i]), True)
            for i, col_hex in zip(idxs, palette)
        ]
        st.plotly_chart(radar_figure(traces, height=430), width="stretch",
                        config={"displayModeBar": False})
    with right:
        rows = ["Persona", "Department", "PriorityTier", "Rekomendasi", "Priority",
                "TurnoverRisk", "Impact", "Engagement", "PerformanceScore",
                "JobSatisfaction", "YearsAtCompany", "MonthlyIncome"]
        comp = emp.loc[idxs, rows].T
        comp.columns = [f"ID {emp.loc[i, 'EmployeeID']}" for i in idxs]
        st.dataframe(comp.astype(str), width="stretch", height=430)


def page_method():
    page_header("METHODOLOGY", "Rumus & Interpretasi",
                "Semua fitur dinormalisasi sebagai percentile rank (0–1) terhadap 1.000 karyawan.")
    st.markdown(
        """
```text
PayGap        = norm(PerformanceScore) − norm(MonthlyIncome)      # positif = under-rewarded

RiskJS        = 1 − norm(JobSatisfaction)                         # Tett & Meyer (1993)
RiskGap       = max(0, PayGap)                                    # Adams (1965), Equity Theory
TurnoverRisk  = (RiskJS + RiskGap) / 2

Impact        = (norm(PerformanceScore) + norm(MonthlyIncome)
                 + norm(YearsAtCompany)) / 3                      # Gallup: replacement cost ∝ gaji

Priority      = TurnoverRisk × Impact                             # sumbu Y
Engagement    = norm(JobSatisfaction)                             # sumbu X
```

Skor prioritas dihitung per karyawan sebagai hasil kali probabilitas kehilangan (turnover
risk) dan dampak bisnis kehilangan (impact). Turnover risk menggabungkan dua jalur keluar
yang didukung literatur: ketidakpuasan kerja dan ketidakadilan kompensasi. Impact
mengaproksimasi biaya kehilangan melalui performa, kompensasi (proxy replacement cost),
dan tenure. Bentuk perkalian dipilih agar prioritas tinggi hanya diberikan pada karyawan
yang berisiko keluar **sekaligus** mahal untuk digantikan — bukan salah satunya saja.

**Referensi**

1. Tett, R.P. & Meyer, J.P. (1993). *Personnel Psychology*, 46(2), 259–293.
   [doi:10.1111/j.1744-6570.1993.tb00874.x](https://doi.org/10.1111/j.1744-6570.1993.tb00874.x)
2. Griffeth, R.W., Hom, P.W., & Gaertner, S. (2000). *Journal of Management*, 26(3), 463–488.
   [doi:10.1016/S0149-2063(00)00043-X](https://doi.org/10.1016/S0149-2063(00)00043-X)
3. Adams, J.S. (1965). Inequity in Social Exchange. *Adv. in Experimental Social Psychology*, 2, 267–299.
   [doi:10.1016/S0065-2601(08)60108-2](https://doi.org/10.1016/S0065-2601(08)60108-2)
4. McFeely, S. & Wigert, B. (2019). *This Fixable Problem Costs U.S. Businesses $1 Trillion*. Gallup.

**Limitation** — dataset tidak memiliki label attrition historis, sehingga TurnoverRisk adalah
proxy berbasis literatur, bukan probabilitas hasil training model prediktif.
"""
    )


def page_predict(emp):
    page_header("PREDICT", "Simulasi Karyawan Baru",
                "Masukkan profil karyawan → sistem menentukan segmen (nearest-centroid, "
                "ekuivalen KMeans) dan menghitung skor prioritas + rekomendasi HR.")

    mu, sd, centroids, q50, q75 = fit_predictor(emp)

    i1, i2, i3, i4 = st.columns(4)
    perf = i1.slider("Performance Score", 1, 5, 3)
    js = i2.slider("Job Satisfaction", 1, 5, 3)
    tenure = i3.number_input("Years at Company", 0, 45,
                             int(emp["YearsAtCompany"].median()))
    income = i4.number_input(
        "Monthly Income", 0, 100_000, int(emp["MonthlyIncome"].median()), step=500)

    r = predict_employee(emp, mu, sd, centroids, q50, q75,
                         perf, js, tenure, income)
    pc = PERSONA_COLORS[r["persona"]]

    st.markdown(
        f"""
    <div class="tl-card" style="border-left:4px solid {pc};">
      <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
        <div style="width:74px;height:74px;border-radius:50%;background:rgba(13,18,36,0.9);
                    border:3px dashed {pc};display:flex;align-items:center;justify-content:center;
                    font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:22px;color:{pc};">
          NEW</div>
        <div style="flex:1;min-width:230px;">
          <span style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:2px;
                       border:1px solid {pc};color:{pc};border-radius:5px;padding:3px 9px;">
            {PERSONA_SHORT[r['persona']]}</span>
          <span style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:2px;
                       color:{MUTED};margin-left:8px;">
            {r['tier']} · SETARA RANK #{r['rank']} / {len(emp) + 1}</span>
          <div style="font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:34px;
                      color:#FFF;line-height:1.15;">{r['persona'].upper()}</div>
        </div>
      </div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:16px;">
        {chip("Priority Score", f"{r['Priority']:.3f}", bar_color(r['Priority'] * 100, risk=True))}
        {chip("Turnover Risk", f"{r['TurnoverRisk']:.3f}", bar_color(r['TurnoverRisk'] * 100, risk=True))}
        {chip("Impact", f"{r['Impact']:.3f}")}
        {chip("Engagement", r['eng_level'])}
        {chip("Rekomendasi HR", r['rekom'], pc)}
      </div>
    </div>""",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.15, 1])
    with left:
        bars = '<div class="tl-card">'
        bars += ('<div class="tl-eyebrow" style="margin-bottom:10px;">SCORE COMPONENTS '
                 '<span style="color:#8A93AD;">· PERCENTILE 0–100</span></div>')
        bars += bar_row("Engagement", r["Engagement"] * 100)
        bars += bar_row("Turnover Risk", r["TurnoverRisk"] * 100, risk=True)
        bars += bar_row("Risk: Dissatisfaction", r["RiskJS"] * 100, risk=True, sub=True)
        bars += bar_row("Risk: Pay Gap", r["RiskGap"] * 100, risk=True, sub=True)
        bars += bar_row("Impact", r["Impact"] * 100)
        bars += bar_row("Priority", r["Priority"] * 100, risk=True)
        bars += '<div class="tl-eyebrow" style="margin:16px 0 10px;">FEATURE PERCENTILES</div>'
        bars += bar_row("Performance", r["pct"]["PerformanceScore"] * 100)
        bars += bar_row("Job Satisfaction", r["pct"]["JobSatisfaction"] * 100)
        bars += bar_row("Tenure", r["pct"]["YearsAtCompany"] * 100)
        bars += bar_row("Income", r["pct"]["MonthlyIncome"] * 100)
        bars += "</div>"
        st.markdown(bars, unsafe_allow_html=True)

        new_row = pd.Series({
            "PerformanceScore_pct": r["pct"]["PerformanceScore"] * 100,
            "JobSatisfaction_pct": r["pct"]["JobSatisfaction"] * 100,
            "YearsAtCompany_pct": r["pct"]["YearsAtCompany"] * 100,
            "MonthlyIncome_pct": r["pct"]["MonthlyIncome"] * 100,
            "Impact": r["Impact"], "TurnoverRisk": r["TurnoverRisk"],
        })
        pmean = emp[emp["Persona"] == r["persona"]][
            ["PerformanceScore_pct", "JobSatisfaction_pct", "YearsAtCompany_pct",
             "MonthlyIncome_pct", "Impact", "TurnoverRisk"]].mean()
        st.markdown('<div class="tl-eyebrow" style="margin:4px 0 0;">EMPLOYEE RADAR</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(
            radar_figure([
                ("Karyawan baru", pc, radar_values(new_row), True),
                (f"Avg {PERSONA_SHORT[r['persona']]}", "#8A93AD", radar_values(pmean), False),
            ]),
            width="stretch", config={"displayModeBar": False},
        )

    with right:
        fig = go.Figure()
        fig.add_trace(go.Scattergl(
            x=emp["_jit"], y=emp["Priority"], mode="markers",
            marker=dict(size=5, color="rgba(138,147,173,0.28)"),
            hoverinfo="skip", showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=[r["Engagement"]], y=[r["Priority"]], mode="markers",
            marker=dict(size=20, color=pc, symbol="star",
                        line=dict(color="white", width=2)),
            showlegend=False,
            hovertemplate=f"Karyawan baru<br>Priority {r['Priority']:.3f}<extra></extra>",
        ))
        fig.add_vline(x=emp["Engagement"].median(), line_dash="dash",
                      line_color="rgba(200,210,235,0.3)")
        fig.add_hline(y=emp["Priority"].median(), line_dash="dash",
                      line_color="rgba(200,210,235,0.3)")
        fig.update_xaxes(title="ENGAGEMENT →", title_font_size=10)
        fig.update_yaxes(title="PRIORITY →", title_font_size=10)
        st.plotly_chart(plotly_dark(fig, 300), width="stretch",
                        config={"displayModeBar": False})

        # karyawan existing paling mirip
        v = np.array([r["pct"][f] for f in FEATS])
        X = emp[[c + "_pct" for c in FEATS]].to_numpy() / 100.0
        dr = np.sqrt(((X - v) ** 2).sum(1))
        top5 = np.argsort(dr)[:5]
        rows = ""
        for rank_i, j in enumerate(top5, 1):
            s = emp.loc[j]
            score = max(0.0, (1 - dr[j] / 2.0)) * 100
            sc_color = PERSONA_COLORS[s["Persona"]]
            rows += f"""
            <div style="display:flex;align-items:center;gap:12px;padding:9px 4px;
                        border-bottom:1px solid rgba(124,140,190,0.12);">
              <div style="flex:0 0 16px;color:{MUTED};font-family:'JetBrains Mono',monospace;
                          font-size:12px;">{rank_i}</div>
              <div style="width:10px;height:10px;border-radius:50%;background:{sc_color};"></div>
              <div style="flex:1;">
                <div style="font-weight:600;font-size:14px;color:{TEXT};">ID {s['EmployeeID']}</div>
                <div style="font-size:11px;color:{MUTED};">{PERSONA_SHORT[s['Persona']]} · {s['PriorityTier']}</div>
              </div>
              <div style="width:42px;height:42px;border-radius:50%;border:2.5px solid {ACCENT};
                          display:flex;align-items:center;justify-content:center;
                          font-family:'JetBrains Mono',monospace;font-weight:700;
                          font-size:12px;color:{ACCENT};">{score:.0f}</div>
            </div>"""
        st.markdown(
            f"""<div class="tl-card">
            <div class="tl-eyebrow" style="margin-bottom:6px;">KARYAWAN EXISTING PALING MIRIP</div>{rows}</div>""",
            unsafe_allow_html=True,
        )

    st.caption("Assignment segmen memakai nearest-centroid di ruang ter-standarisasi — "
               "ekuivalen eksak dengan aturan assignment KMeans (100% match pada 1.000 "
               "karyawan existing). Percentile dihitung terhadap populasi existing.")


# ══════════════════════════════ MAIN ══════════════════════════════

def main():
    st.markdown(CSS, unsafe_allow_html=True)
    emp, summary, profile, tier_ct, rekom_ct, dept_sum, dept_ct = load_data()
    dist = similarity_matrix(emp)

    with st.sidebar:
        st.markdown('<div class="tl-logo">Talent<span>Lab</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="tl-sub">HR Segmentation &amp; Projections</div>',
                    unsafe_allow_html=True)
        page = st.radio(
            "Navigation",
            ["📊 Summary", "🎯 Decision Matrix", "🪪 Employee Card",
             "⚔️ Comparison", "🔮 Predict", "📐 Metodologi"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        legend = "".join(
            f'<div style="display:flex;align-items:center;gap:8px;margin:5px 0;">'
            f'<div style="width:10px;height:10px;border-radius:50%;background:{c};"></div>'
            f'<span style="font-size:12px;">{PERSONA_SHORT[p]}</span></div>'
            for p, c in PERSONA_COLORS.items()
        )
        st.markdown(
            f'<div class="tl-kpi-label" style="margin-bottom:6px;">PERSONA</div>{legend}',
            unsafe_allow_html=True,
        )

    if page.endswith("Summary"):
        page_summary(emp, summary, profile, tier_ct, rekom_ct, dept_sum, dept_ct)
    elif page.endswith("Decision Matrix"):
        page_matrix(emp)
    elif page.endswith("Employee Card"):
        page_card(emp, dist)
    elif page.endswith("Comparison"):
        page_compare(emp)
    elif page.endswith("Predict"):
        page_predict(emp)
    else:
        page_method()


if __name__ == "__main__":
    main()
