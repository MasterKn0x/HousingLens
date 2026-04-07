import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import numpy as np
from components.district_map import DISTRICT_COORDS

def render_heatmap(df):
    """
    Renders an interactive HeatMap of property density/value.
    Uses District coordinates and applies micro-jitter to simulate individual listings.
    """
    # ── Initial Map Configuration ──
    # Centered on Sri Lanka
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=7, tiles="CartoDB dark_matter")
    
    heat_data = []

    # Map each listing to a slight offset of its district center
    for idx, row in df.iterrows():
        district = row.get("district")
        price = row.get("price_lkr")
        
        if district in DISTRICT_COORDS and price:
            lat, lon = DISTRICT_COORDS[district]
            
            # Micro-jitter: simulate actual geographic spread instead of generic district pin
            jitter_lat = lat + np.random.normal(0, 0.08)
            jitter_lon = lon + np.random.normal(0, 0.08)
            
            # Weight is scaled by price (higher price -> hotter glow)
            # Clip between 0.1 and 1.0 for visuals
            weight = min(max(price / 10_000_000, 0.1), 1.0)
            
            heat_data.append([jitter_lat, jitter_lon, weight])

    if heat_data:
        HeatMap(
            heat_data,
            radius=15,          # Size of the glow bubbles
            blur=10,            # Smoothness of the blur
            min_opacity=0.3,
            gradient={0.2: '#38BDF8', 0.5: '#7B61FF', 0.8: '#FCD34D', 1.0: '#FC8181'} 
        ).add_to(m)

    # Render it via streamlit-folium
    st_folium(m, width=700, height=500, returned_objects=[])
