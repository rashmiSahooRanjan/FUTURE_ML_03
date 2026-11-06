"""
UI Helpers, Plotly Visualizations, and Style Utilities for TalentRank AI
"""

from typing import List, Dict, Any, Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import ASSETS_DIR, THEME


def load_custom_css():
    """Loads and injects custom SaaS CSS into Streamlit page."""
    css_path = ASSETS_DIR / "custom.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def render_hero_banner(title: str, subtitle: str, badge_text: str = "Enterprise AI Intelligence"):
    """Renders sleek top hero header banner."""
    html = f"""
    <div class="hero-container">
        <div class="hero-badge">⚡ {badge_text}</div>
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_kpi_card(title: str, value: str, subtext: str, icon: str = "📊", color_class: str = "kpi-icon-blue"):
    """Renders modern metric KPI card."""
    html = f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <span class="kpi-title">{title}</span>
            <div class="kpi-icon {color_class}">{icon}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def get_score_pill_html(score: float, recommendation: str) -> str:
    """Returns HTML styled score pill."""
    if score >= 80.0:
        cls = "score-strong"
    elif score >= 65.0:
        cls = "score-good"
    elif score >= 45.0:
        cls = "score-partial"
    else:
        cls = "score-review"
    return f'<span class="score-pill {cls}">{score:.1f}% • {recommendation}</span>'


def render_skill_badges(skills: List[str], badge_type: str = "matched", max_display: int = 25) -> str:
    """Renders formatted skill chip badges."""
    if not skills:
        return "<span style='color: #94a3b8; font-size: 0.85rem;'>None detected</span>"

    cls_map = {
        "matched": "badge-matched",
        "missing": "badge-missing",
        "preferred": "badge-preferred",
        "additional": "badge-additional",
        "neutral": "badge-neutral"
    }
    cls = cls_map.get(badge_type, "badge-neutral")

    badges = []
    for s in skills[:max_display]:
        badges.append(f'<span class="skill-badge {cls}">{s}</span>')

    if len(skills) > max_display:
        badges.append(f'<span class="skill-badge badge-neutral">+{len(skills) - max_display} more</span>')

    return "".join(badges)


# --- Plotly Visualizations ---
def plot_score_distribution(scores: List[float]):
    """Chart 1: Candidate Match Score Distribution."""
    if not scores:
        return go.Figure()

    ranges = {"80–100% (Strong)": 0, "60–79% (Good)": 0, "40–59% (Partial)": 0, "0–39% (Review)": 0}
    for s in scores:
        if s >= 80:
            ranges["80–100% (Strong)"] += 1
        elif s >= 60:
            ranges["60–79% (Good)"] += 1
        elif s >= 40:
            ranges["40–59% (Partial)"] += 1
        else:
            ranges["0–39% (Review)"] += 1

    df = pd.DataFrame(list(ranges.items()), columns=["Score Tier", "Count"])
    colors_list = ["#10b981", "#0284c7", "#f59e0b", "#ef4444"]

    fig = px.pie(
        df,
        values="Count",
        names="Score Tier",
        hole=0.55,
        color_discrete_sequence=colors_list,
        title="Candidate Match Score Distribution"
    )
    fig.update_layout(
        font=dict(family="Plus Jakarta Sans", size=12),
        margin=dict(t=40, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def plot_top_candidates(ranked_candidates: List[Dict[str, Any]], top_n: int = 10):
    """Chart 2: Top candidates horizontal bar chart."""
    if not ranked_candidates:
        return go.Figure()

    top_list = ranked_candidates[:top_n]
    names = [c.get("candidate_name", "Unknown")[:20] for c in reversed(top_list)]
    scores = [c.get("final_score", 0.0) for c in reversed(top_list)]

    fig = go.Figure(go.Bar(
        x=scores,
        y=names,
        orientation='h',
        marker=dict(
            color=scores,
            colorscale=[[0, '#0284c7'], [0.5, '#06b6d4'], [1.0, '#10b981']],
            showscale=False
        ),
        text=[f"{s:.1f}%" for s in scores],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=12, family="Plus Jakarta Sans")
    ))

    fig.update_layout(
        title=f"Top {len(top_list)} Candidate Rankings",
        xaxis=dict(title="Match Score (%)", range=[0, 105]),
        yaxis=dict(title=""),
        margin=dict(t=40, b=20, l=100, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", size=12)
    )
    return fig


def plot_skill_demand(required_skills: List[str]):
    """Chart 3: Skill Demand Analysis."""
    if not required_skills:
        return go.Figure()

    df = pd.DataFrame({"Skill": required_skills, "Demand Index": [1] * len(required_skills)})
    fig = px.bar(
        df,
        x="Skill",
        y="Demand Index",
        color="Skill",
        title="Key Skills Required for Role",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=30, l=20, r=20),
        font=dict(family="Plus Jakarta Sans", size=12)
    )
    return fig


def plot_experience_distribution(candidates: List[Dict[str, Any]]):
    """Chart 4: Candidate Experience Distribution."""
    exp_list = [c.get("candidate_exp", c.get("experience", 0.0)) for c in candidates]
    if not exp_list:
        return go.Figure()

    df = pd.DataFrame({"Experience (Years)": exp_list})
    fig = px.histogram(
        df,
        x="Experience (Years)",
        nbins=8,
        title="Candidate Experience Spread",
        color_discrete_sequence=["#0284c7"]
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=20, l=20, r=20),
        font=dict(family="Plus Jakarta Sans", size=12)
    )
    return fig


def plot_candidate_radar(candidate: Dict[str, Any]):
    """Radar chart of multi-dimensional evaluation for an individual candidate."""
    categories = [
        "Required Skills",
        "Text Similarity",
        "Preferred Skills",
        "Experience",
        "Education",
        "Keyword Relevance"
    ]
    values = [
        candidate.get("skill_score", 0.0),
        candidate.get("similarity_score", 0.0),
        candidate.get("preferred_skill_score", 0.0),
        candidate.get("experience_score", 0.0),
        candidate.get("education_score", 0.0),
        candidate.get("keyword_score", 0.0)
    ]
    # Close polygon
    values.append(values[0])
    categories.append(categories[0])

    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(2, 132, 199, 0.25)',
        line=dict(color='#0284c7', width=2),
        name=candidate.get("candidate_name", "Candidate")
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color="#94a3b8")
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=30, l=30, r=30),
        font=dict(family="Plus Jakarta Sans", size=11)
    )
    return fig
