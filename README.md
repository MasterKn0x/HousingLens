# HousingLens: AI-Powered Property Valuation Platform 🏠

HousingLens is a state-of-the-art predictive analytics platform designed to modernize residential property valuation in the Sri Lankan market. By leveraging machine learning and geospatial intelligence, HousingLens provides transparent, data-driven insights for buyers, investors, and real estate professionals.

## 🚀 Key Features

- **AI-Powered Valuation:** Real-time property price estimation using high-performance gradient-boosted models (XGBoost).
- **Investment Risk Index (IRI):** A unique 1–10 transparency score that quantifies market volatility and prediction confidence.
- **Geospatial Analytics:** Deep integration with OpenStreetMap (OSM) to model proximity to essential amenities like schools, hospitals, and transit hubs.
- **Interactive Scenarios:** A planning tool to simulate "what-if" scenarios (e.g., adding a bathroom or floor) and visualize the immediate impact on value.
- **Market Heatmaps:** Geographic density visualizations showing property value distributions and investment hotspots.

## 🛠️ Technology Stack

- **Backend:** Python 3.11, Scikit-learn, XGBoost, TensorFlow/Keras
- **Frontend:** Streamlit (Custom Reactive UI)
- **Data:** BeautifulSoup4 (Scraper), OpenStreetMap Overpass API (Geospatial)
- **Analytics:** Pandas, NumPy, Plotly, Folium
- **Testing:** Pytest

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MasterKn0x/HousingLens.git
   cd HousingLens
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the application:**
   Ensure you have a local `users.db` and the pre-trained `model.pkl` in the root directory. If retraining is needed, use the Admin Panel.

4. **Launch the Dashboard:**
   ```bash
   streamlit run app.py
   ```

## 🔐 Security & Roles

- **User Role:** Access to Analytics, Price Prediction, and Scenario Planning.
- **Admin Role:** Full system control, including data scraping triggers, model retraining, and user management.

## 📬 Contact & Support

For support, partnerships, or data inquiries, please reach out via email:
[support@housinglens.com](mailto:support@housinglens.com)

---
*HousingLens is built with a commitment to market transparency and data-driven excellence.*
