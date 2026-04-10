"""training/marche_charts.py – Graphiques Plotly pour le cours marché immobilier."""
from __future__ import annotations

import plotly.graph_objects as go


def chart_taux_credit() -> go.Figure:
    """Évolution des taux de crédit immobilier en France (2015-2026)."""
    annees = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    taux = [2.2, 1.8, 1.5, 1.4, 1.2, 1.1, 1.0, 1.5, 3.5, 3.8, 3.6, 3.4]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=annees, y=taux,
        mode='lines+markers',
        name='Taux moyen',
        line=dict(color='#00B4A6', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(0,180,166,0.1)',
    ))

    # Zone de crise
    fig.add_vrect(x0=2022, x1=2024, fillcolor="rgba(255,0,0,0.05)",
                  line_width=0, annotation_text="Hausse BCE",
                  annotation_position="top left")

    fig.update_layout(
        title="📈 Taux de crédit immobilier moyen en France",
        xaxis_title="Année",
        yaxis_title="Taux (%)",
        yaxis=dict(range=[0, 5]),
        template="plotly_white",
        height=350,
        margin=dict(l=40, r=20, t=60, b=40),
        font=dict(size=12),
    )
    return fig


def chart_volumes_ventes() -> go.Figure:
    """Volumes de ventes dans l'ancien en France."""
    annees = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    volumes = [970000, 1070000, 1024000, 1178000, 1115000, 875000, 780000, 810000]

    colors = ['#00B4A6' if v >= 900000 else '#e21b3c' for v in volumes]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=annees, y=volumes,
        marker_color=colors,
        text=[f"{v/1000:.0f}k" for v in volumes],
        textposition='outside',
    ))

    # Ligne seuil
    fig.add_hline(y=900000, line_dash="dash", line_color="gray",
                  annotation_text="Seuil marché actif (900k)")

    fig.update_layout(
        title="📊 Volumes de ventes dans l'ancien (France)",
        xaxis_title="Année",
        yaxis_title="Nombre de transactions",
        template="plotly_white",
        height=350,
        margin=dict(l=40, r=20, t=60, b=40),
        font=dict(size=12),
    )
    return fig


def chart_impact_taux_budget(taux_actuel: float = 3.6) -> go.Figure:
    """Impact du taux sur la capacité d'emprunt (salaire 3000€/mois)."""
    taux_range = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
    # Capacité d'emprunt sur 25 ans, mensualité max 35% de 3000€ = 1050€
    mensualite = 1050
    capacites = []
    for t in taux_range:
        r = t / 100 / 12
        n = 25 * 12
        cap = mensualite * (1 - (1 + r) ** (-n)) / r
        capacites.append(round(cap))

    colors = ['#00B4A6' if t <= taux_actuel else '#94a3b8' for t in taux_range]
    idx_actuel = min(range(len(taux_range)), key=lambda i: abs(taux_range[i] - taux_actuel))
    colors[idx_actuel] = '#e21b3c'

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"{t}%" for t in taux_range],
        y=capacites,
        marker_color=colors,
        text=[f"{c/1000:.0f}k€" for c in capacites],
        textposition='outside',
    ))

    fig.update_layout(
        title="💰 Capacité d'emprunt selon le taux (salaire 3 000€/mois, 25 ans)",
        xaxis_title="Taux de crédit",
        yaxis_title="Capacité d'emprunt (€)",
        template="plotly_white",
        height=350,
        margin=dict(l=40, r=20, t=60, b=40),
        font=dict(size=12),
        annotations=[dict(
            x=f"{taux_actuel}%", y=capacites[idx_actuel],
            text=f"Taux actuel<br>{taux_actuel}%",
            showarrow=True, arrowhead=2, ay=-40,
            font=dict(color="#e21b3c", size=11),
        )],
    )
    return fig


def chart_dpe_repartition() -> go.Figure:
    """Répartition DPE du parc immobilier français."""
    dpe = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    pct = [2, 5, 16, 30, 24, 14, 9]
    colors = ['#1a9641', '#6db33f', '#a6d96a', '#fee08b', '#fdae61', '#f46d43', '#d73027']

    interdits = ['', '', '', '', '2034', '2028', '2025']
    texts = [f"{p}%" + (f"\n⛔{a}" if a else "") for p, a in zip(pct, interdits)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dpe, y=pct,
        marker_color=colors,
        text=texts,
        textposition='outside',
    ))

    fig.update_layout(
        title="🏠 Répartition DPE du parc français — Calendrier d'interdiction location",
        xaxis_title="Classe DPE",
        yaxis_title="% du parc",
        template="plotly_white",
        height=350,
        margin=dict(l=40, r=20, t=60, b=40),
        font=dict(size=12),
    )
    return fig
