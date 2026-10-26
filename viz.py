"""viz.py - Plotly figures for BBV ISS LIVE (maps and charts)."""

import plotly.graph_objects as go

import iss_core as core

LAND = "#1d4a2e"
OCEAN = "#0a1f44"
COAST = "#6ec6ff"
YELLOW = "#ffd84d"
SKY = "#6ec6ff"


def _style_geo(fig, projection, center=None):
    geo = dict(
        projection_type=projection,
        showland=True, landcolor=LAND,
        showocean=True, oceancolor=OCEAN,
        showcountries=True, countrycolor="rgba(255,255,255,0.25)",
        showcoastlines=True, coastlinecolor=COAST,
        showlakes=False, bgcolor="rgba(0,0,0,0)",
        lataxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.12)"),
        lonaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.12)"),
    )
    if center is not None:
        geo["projection_rotation"] = dict(lon=center[1], lat=center[0])
    fig.update_geos(**geo)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=0.02, x=0.01,
                    font=dict(color="white"), bgcolor="rgba(10,19,48,0.6)"),
        height=520,
    )


def build_map(readings, latest, projection="natural earth", rotate_to_latest=False,
              marker_name="ISS (latest reported)"):
    """World map / globe: ground track, latest ISS marker, India box and Pilani."""
    fig = go.Figure()

    # India bounding box (dotted) - clearly labelled as approximate
    b = core.INDIA_BOUNDS
    box_lat = [b["lat_min"], b["lat_min"], b["lat_max"], b["lat_max"], b["lat_min"]]
    box_lon = [b["lon_min"], b["lon_max"], b["lon_max"], b["lon_min"], b["lon_min"]]
    fig.add_trace(go.Scattergeo(
        lat=box_lat, lon=box_lon, mode="lines",
        line=dict(width=1.5, color="#ffab5e", dash="dot"),
        name="India (rough box)", hoverinfo="skip"))

    # Ground track (broken at the date line)
    if len(readings) > 1:
        lats, lons = core.track_with_gaps(readings)
        fig.add_trace(go.Scattergeo(
            lat=lats, lon=lons, mode="lines",
            line=dict(width=2.5, color=YELLOW),
            name="Recent ground track", hoverinfo="skip"))

    # Pilani
    fig.add_trace(go.Scattergeo(
        lat=[core.PILANI[0]], lon=[core.PILANI[1]], mode="markers+text",
        marker=dict(size=8, color="#ff7b7b", symbol="diamond"),
        text=["Pilani"], textposition="bottom right",
        textfont=dict(color="white", size=11), name="Pilani", hoverinfo="skip"))

    # Latest ISS position
    fig.add_trace(go.Scattergeo(
        lat=[latest["latitude"]], lon=[latest["longitude"]], mode="markers",
        marker=dict(size=15, color=SKY, line=dict(width=3, color="white")),
        name=marker_name,
        hovertemplate=("Lat %{lat:.2f}°<br>Lon %{lon:.2f}°<br>"
                       f"Altitude {latest['altitude_km']:.0f} km<extra></extra>")))

    center = (latest["latitude"], latest["longitude"]) if rotate_to_latest else None
    _style_geo(fig, projection, center)
    return fig


def metric_chart(readings, key, title, unit):
    """Small line chart of one value (altitude or speed) over time."""
    times = [core.ist_text(r["timestamp"]) for r in readings]
    values = [r[key] for r in readings]
    fig = go.Figure(go.Scatter(x=times, y=values, mode="lines+markers",
                               line=dict(color=SKY, width=2), marker=dict(size=4)))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        yaxis_title=unit, height=260, margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#eaf1ff"),
        xaxis=dict(showgrid=False, nticks=6),
        yaxis=dict(gridcolor="rgba(255,255,255,0.12)"))
    return fig
