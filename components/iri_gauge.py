"""
HousingLens – IRI Gauge Component
----------------------------------
Renders a Plotly gauge chart for the 1-10 Investment Risk Index.
"""

import plotly.graph_objects as go
import streamlit as st
from model.iri_calculator import iri_colour, iri_label


def render_iri_gauge(iri: int, height: int = 280) -> None:
    """
    Render a styled Plotly gauge for the Investment Risk Index.

    Parameters
    ----------
    iri    : int   IRI score (1–10)
    height : int   Figure height in pixels
    """
    label_text, _ = iri_label(iri)
    colour = iri_colour(iri)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=iri,
        number={
            "font": {"size": 52, "color": colour, "family": "Space Grotesk"},
            "suffix": "/10",
        },
        title={
            "text": f"Investment Risk Index<br><span style='font-size:14px;color:#8A94A8'>{label_text}</span>",
            "font": {"size": 16, "color": "#E8EDF5", "family": "Inter"},
        },
        gauge={
            "axis": {
                "range": [1, 10],
                "tickvals": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "ticktext": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
                "tickfont": {"color": "#8A94A8", "size": 11},
                "tickcolor": "#8A94A8",
            },
            "bar": {"color": colour, "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [1, 3.5],  "color": "rgba(0,196,140,0.12)"},
                {"range": [3.5, 6.5],"color": "rgba(255,179,71,0.12)"},
                {"range": [6.5, 10], "color": "rgba(255,107,107,0.12)"},
            ],
            "threshold": {
                "line": {"color": colour, "width": 3},
                "thickness": 0.75,
                "value": iri,
            },
        },
    ))

    fig.update_layout(
        height=height,
        margin=dict(t=60, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E8EDF5"},
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
