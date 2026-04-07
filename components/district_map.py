import streamlit as st
import folium
from streamlit_folium import st_folium

# Approximate center coordinates for Sri Lankan Districts
DISTRICT_COORDS = {
    "Colombo":      (6.9271, 79.8612),
    "Gampaha":      (7.0840, 80.0098),
    "Kalutara":     (6.5854, 79.9607),
    "Kandy":        (7.2906, 80.6337),
    "Matale":       (7.4675, 80.6234),
    "Nuwara Eliya": (6.9497, 80.7839),
    "Galle":        (6.0328, 80.2170),
    "Matara":       (5.9549, 80.5550),
    "Hambantota":   (6.1246, 81.1185),
    "Jaffna":       (9.6615, 80.0255),
    "Kilinochchi":  (9.3803, 80.3770),
    "Mannar":       (8.9810, 79.9044),
    "Vavuniya":     (8.7542, 80.4982),
    "Mullaitivu":   (9.2671, 80.8142),
    "Batticaloa":   (7.7203, 81.6705),
    "Ampara":       (7.2912, 81.6724),
    "Trincomalee":  (8.5874, 81.2152),
    "Kurunegala":   (7.4818, 80.3609),
    "Puttalam":     (8.0330, 79.8260),
    "Anuradhapura": (8.3114, 80.4037),
    "Polonnaruwa":  (7.9403, 81.0188),
    "Badulla":      (6.9934, 81.0550),
    "Monaragala":   (6.8728, 81.3475),
    "Ratnapura":    (6.7056, 80.3847),
    "Kegalle":      (7.2513, 80.3464),
}

def render_district_map(district_name: str, height: int = 250):
    """
    Renders an interactive Folium map centered on the specified district.
    """
    coords = DISTRICT_COORDS.get(district_name, DISTRICT_COORDS["Colombo"])
    
    # Colored OpenStreetMap tiles (most accurate and detailed)
    m = folium.Map(
        location=coords,
        zoom_start=11, # Increased zoom slightly for better detail
        tiles="OpenStreetMap",
        zoom_control=True,
    )
    
    # Add a glowing marker for the district
    folium.Marker(
        coords,
        tooltip=f"{district_name} District",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

    # Use st_folium to embed it into the Streamlit container seamlessly
    st_folium(
        m,
        height=height,
        use_container_width=True,
        returned_objects=[] # Disable bidirectional syncing for speed
    )
