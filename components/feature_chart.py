"""
HousingLens – Feature Importance Chart Component
--------------------------------------------------
Renders a Plotly horizontal bar chart of feature importances.
"""

import plotly.graph_objects as go
import streamlit as st


def render_feature_chart(importances: dict, title: str = "Top Feature Importances") -> None:
    """
    Render a horizontal bar chart of feature importances.

    Parameters
    ----------
    importances : dict
        { feature_name: importance_percent }  (values need not sum to 100)
    title : str
        Chart title.
    """
    # Sort descending
    sorted_items = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    features = [item[0] for item in sorted_items]
    values   = [item[1] for item in sorted_items]

    # Colour gradient based on value
    max_val = max(values) if values else 1
    bar_colours = [
        f"rgba(0,212,170,{0.45 + 0.55 * (v / max_val):.2f})"
        for v in values
    ]

    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation="h",
        marker=dict(
            color=bar_colours,
            line=dict(color="rgba(0,212,170,0.4)", width=1),
        ),
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
        textfont={"color": "#E8EDF5", "size": 12, "family": "Inter"},
        hovertemplate="<b>%{y}</b><br>Importance: %{x:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        title={
            "text": title,
            "font": {"size": 15, "color": "#E8EDF5", "family": "Space Grotesk"},
            "x": 0,
        },
        xaxis={
            "title": "Importance (%)",
            "color": "#8A94A8",
            "gridcolor": "rgba(255,255,255,0.04)",
            "zeroline": False,
        },
        yaxis={
            "color": "#E8EDF5",
            "autorange": "reversed",
            "tickfont": {"size": 12},
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=20, l=10, r=60),
        height=300,
        font={"family": "Inter", "color": "#E8EDF5"},
        bargap=0.35,
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_feature_chart_vertical(importances: dict, title: str = "Feature Importances") -> None:
    """
    Vertical bar variant (used on Analytics page with more features).
    """
    sorted_items = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    features = [item[0] for item in sorted_items]
    values   = [item[1] for item in sorted_items]

    fig = go.Figure(go.Bar(
        x=features,
        y=values,
        marker=dict(
            color=values,
            colorscale=[[0, "#131827"], [0.5, "#00A88A"], [1, "#00D4AA"]],
            showscale=False,
            line=dict(color="rgba(0,212,170,0.3)", width=1),
        ),
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
        textfont={"color": "#E8EDF5", "size": 11},
        hovertemplate="<b>%{x}</b><br>Importance: %{y:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        title={"text": title, "font": {"size": 15, "color": "#E8EDF5", "family": "Space Grotesk"}, "x": 0},
        xaxis={"color": "#E8EDF5", "tickangle": -20, "tickfont": {"size": 11}},
        yaxis={"color": "#8A94A8", "gridcolor": "rgba(255,255,255,0.04)", "zeroline": False},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=60, l=20, r=20),
        height=320,
        font={"family": "Inter"},
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
