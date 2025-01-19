# app.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from groq import Groq
import numpy as np
from audio_recorder_streamlit import audio_recorder
import tempfile
import os
import warnings
warnings.filterwarnings('ignore')
# Page config must be the first Streamlit command
st.set_page_config(
    page_title="ANTNA",
    page_icon="🐜",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "ANTNA - Crisis Management System 🐜"
    }
)

# Custom CSS with Space Mono font and darker theme
st.markdown("""
    <style>
    /* Import Space Mono font */
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
    
    /* Main theme */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%) !important;
    }

    .stApp > header {
        background-color: transparent !important;
    }

    .main .block-container {
        background-color: transparent !important;
    }

    /* Global text styling */
    .stApp, .stMarkdown, div[data-testid="stMarkdownContainer"] p {
        font-family: 'Space Mono', monospace !important;
        color: #ffffff !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Mono', monospace !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Custom container styles */
    .stats-box {
        background: linear-gradient(145deg, rgba(26, 26, 26, 0.9), rgba(32, 32, 32, 0.9));
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid rgba(51, 51, 51, 0.5);
        backdrop-filter: blur(10px);
    }

    .social-update {
        background: linear-gradient(145deg, rgba(26, 26, 26, 0.9), rgba(32, 32, 32, 0.9));
        padding: 16px;
        border-radius: 12px;
        margin: 12px 0;
        backdrop-filter: blur(10px);
    }
    
    .update-header {
        margin-bottom: 12px;
    }
    
    .account-info {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .username {
        color: #888;
        font-size: 0.95em;
    }
    
    .badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        font-size: 12px;
        margin-left: 4px;
    }
    
    .verified {
        background: #00ff9d33;
        color: #00ff9d;
    }
    
    .unverified {
        background: #ff006e33;
        color: #ff006e;
    }
    
    .update-content {
        margin: 12px 0;
        line-height: 1.4;
        font-size: 1.05em;
    }
    
    .update-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #888;
        font-size: 0.9em;
    }
    
    .meta-item {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .meta-separator {
        color: #444;
    }
    
    .trust-high { 
        border-left: 4px solid #00ff9d;
        box-shadow: -4px 0 8px -2px rgba(0, 255, 157, 0.3);
    }
    
    .trust-medium { 
        border-left: 4px solid #ffbe0b;
        box-shadow: -4px 0 8px -2px rgba(255, 190, 11, 0.3);
    }
    
    .trust-low { 
        border-left: 4px solid #ff006e;
        box-shadow: -4px 0 8px -2px rgba(255, 0, 110, 0.3);
    }
    
    /* AI response styling */
    .ai-response {
        background: linear-gradient(145deg, rgba(26, 26, 26, 0.9), rgba(32, 32, 32, 0.9));
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #00ff9d;
        box-shadow: -4px 0 8px -2px rgba(0, 255, 157, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Alert styling */
    .alert-box {
        background: linear-gradient(145deg, rgba(26, 26, 26, 0.9), rgba(32, 32, 32, 0.9));
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #ff006e;
        box-shadow: -4px 0 8px -2px rgba(255, 0, 110, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Streamlit elements override */
    .stButton>button {
        background: linear-gradient(90deg, #00ff9d, #00f5d4) !important;
        color: black !important;
        font-family: 'Space Mono', monospace !important;
        font-weight: bold !important;
        border: none !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 255, 157, 0.3) !important;
    }

    .stButton>button:active {
        transform: translateY(0) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00ff9d, #00f5d4) !important;
        border-radius: 999px !important;
    }
    
    .stProgress {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0a, #1a1a1a) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    section[data-testid="stSidebar"] .block-container {
        background: transparent !important;
    }
    
    /* Custom title block with animated border */
    .title-block {
        background: linear-gradient(90deg, rgba(0, 255, 157, 0.1), transparent);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }

    .title-block::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 10px;
        padding: 1px;
        background: linear-gradient(90deg, #00ff9d, #00f5d4);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
    }
    
    /* Status indicator with enhanced pulse */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
        position: relative;
    }
    
    .status-active {
        background: #00ff9d;
        box-shadow: 0 0 10px rgba(0, 255, 157, 0.5);
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    @keyframes pulse {
        0%, 100% { 
            box-shadow: 0 0 0 0 rgba(0, 255, 157, 0.7);
            transform: scale(1);
        }
        50% { 
            box-shadow: 0 0 20px 3px rgba(0, 255, 157, 0.3);
            transform: scale(1.1);
        }
    }
    
    /* Tab styling with hover effects */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(26, 26, 26, 0.6);
        padding: 10px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #ffffff;
        background-color: rgba(51, 51, 51, 0.6);
        padding: 10px 20px;
        font-family: 'Space Mono', monospace;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(0, 255, 157, 0.2);
        transform: translateY(-2px);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00ff9d, #00f5d4) !important;
        color: black !important;
        font-weight: bold !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 255, 157, 0.3);
    }

    /* Input fields */
    .stTextInput input {
        background-color: rgba(51, 51, 51, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        font-family: 'Space Mono', monospace !important;
    }

    .stTextInput input:focus {
        border-color: #00ff9d !important;
        box-shadow: 0 0 0 1px #00ff9d !important;
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(26, 26, 26, 0.6);
    }

    ::-webkit-scrollbar-thumb {
        background: #00ff9d;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #00f5d4;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Groq client
try:
    # Try to get from Streamlit secrets first (for cloud deployment)
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    # Fallback to local environment variable (for local development)
    GROQ_API_KEY = "GROQ_API_KEY"

try:
    groq_client = Groq(api_key=GROQ_API_KEY)
    st.success("Successfully initialized Groq client!")
except Exception as e:
    st.error(f"Failed to initialize Groq client: {str(e)}")
    st.error("Please ensure GROQ_API_KEY is properly set in Streamlit Cloud secrets")
    st.stop()

# Generate simulated data
@st.cache_data
def generate_data():
    # Alerts data
    alerts_data = {
        'type': ['Sandstorm', 'Heat Wave', 'Flash Flood', 'Dust Storm', 'Strong Winds'],
        'severity': ['High', 'High', 'Medium', 'Medium', 'Low'],
        'location': ['Al Wakrah', 'Doha', 'Al Khor', 'Al Rayyan', 'Lusail'],
        'time': [
            (datetime.now() - timedelta(minutes=x*30)).strftime('%Y-%m-%d %H:%M')
            for x in range(5)
        ],
        'description': [
            'Severe sandstorm approaching with reduced visibility',
            'Extreme temperatures expected to reach 48°C',
            'Heavy rainfall may cause local flooding',
            'Moderate dust storm affecting visibility',
            'Strong winds expected up to 40km/h'
        ]
    }
    alerts_df = pd.DataFrame(alerts_data)

    # Shelters data
    shelters_data = {
        'name': [
            'Lusail Sports Arena', 'Al Thumama Stadium', 'Education City Stadium',
            'Al Bayt Stadium Complex', 'Khalifa International Stadium'
        ],
        'capacity': [800, 600, 500, 1000, 700],
        'current': [234, 156, 123, 445, 289],
        'lat': [25.430560, 25.230844, 25.311667, 25.652222, 25.263889],
        'lon': [51.488970, 51.532197, 51.424722, 51.487778, 51.448333],
        'type': ['Primary', 'Secondary', 'Primary', 'Primary', 'Secondary'],
        'contact': [f'+974-4000-{x}111' for x in range(1, 6)]
    }
    shelters_df = pd.DataFrame(shelters_data)

    # Resources data
    resources_data = pd.DataFrame({
        'location': shelters_data['name'],
        'water_supply': [1000, 800, 600, 1200, 900],
        'food_supply': [800, 600, 500, 1000, 700],
        'medical_kits': [50, 40, 30, 60, 45],
        'generators': [10, 8, 6, 12, 9],
        'beds': [500, 400, 300, 600, 450],
        'last_updated': [datetime.now().strftime('%Y-%m-%d %H:%M')] * 5
    })
    resources_df = pd.DataFrame(resources_data)
    # Social updates data
    social_updates_data = {
        'timestamp': [(datetime.now() - timedelta(minutes=x*15)).strftime('%Y-%m-%dT%H:%M:%S') for x in range(10)],
        'source': ['Twitter'] * 10,
        'account_type': ['Official', 'Citizen', 'Emergency', 'Official', 'Healthcare',
                        'Citizen', 'Official', 'Emergency', 'Official', 'Media'],
        'username': ['@QatarWeather', '@QatarResident1', '@QatarRedCrescent', 
                    '@QatarMOI', '@HamadMedical', '@DohaResident', '@QatarMet',
                    '@CivilDefenceQA', '@MunicipalityQA', '@QatarNews'],
        'message': [
            'Severe sandstorm warning for Al Wakrah region. Visibility reduced to 500m.',
            'Heavy sand in Al Wakrah area. Roads barely visible.',
            'Emergency teams deployed to Al Wakrah. Shelter available.',
            'Traffic diverted on Al Wakrah Road due to poor visibility.',
            'Al Wakrah Hospital ready to receive emergency cases.',
            'Temperature hitting 47°C in Doha. Multiple cases of heat exhaustion.',
            'Extreme heat warning: Temperature to reach 48°C in Doha.',
            'Flash flood warning for Al Khor. Emergency teams on high alert.',
            'Storm drains being cleared in Al Khor to prevent flooding.',
            'Live updates: Multiple weather-related incidents across Qatar.'
        ],
        'location': ['Al Wakrah']*4 + ['Doha']*3 + ['Al Khor']*2 + ['Qatar'],
        'trust_score': [0.95, 0.95, 0.98, 0.97, 0.96, 0.95, 0.99, 0.97, 0.94, 0.93],
        'verified': [True, False, True, True, True, False, True, True, True, True],
        'engagement': [1205, 342, 892, 1567, 723, 445, 2341, 1123, 567, 1892],
        'emergency_type': ['Sandstorm']*4 + ['Heat Wave']*3 + ['Flood']*2 + ['Multiple']
    }
    social_updates_df = pd.DataFrame(social_updates_data)

    return alerts_df, shelters_df, resources_df, social_updates_df

# Voice transcription function
def process_voice_input(audio_bytes):
    if not audio_bytes:
        return None
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        try:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name
            
            with open(temp_audio_path, 'rb') as audio_file:
                response = groq_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3"
                )
            return response.text
        except Exception as e:
            st.error(f"Transcription error: {str(e)}")
            return None
        finally:
            try:
                os.remove(temp_audio_path)
            except:
                pass

# RAG simulation
def process_query_with_rag(query, social_updates_df):
    try:
        relevant_updates = social_updates_df[
            social_updates_df['message'].str.contains('|'.join(query.split()), case=False, na=False)
        ]
        
        context = "\n".join(relevant_updates['message'].tolist())
        
        messages = [
            {"role": "system", "content": """You are ANTNA, an AI assistant for emergency management in Qatar. 
             Provide clear, accurate information based on available data and social media updates."""},
            {"role": "user", "content": f"Context from verified social media:\n{context}\n\nUser Question: {query}"}
        ]
        
        try:
            response = groq_client.chat.completions.create(
                messages=messages,
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=500,
                top_p=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI processing error: {str(e)}"
            
    except Exception as e:
        return f"Error processing query: {str(e)}"

def main():
    # Generate data
    alerts_df, shelters_df, resources_df, social_updates_df = generate_data()

    # Sidebar
    with st.sidebar:
        st.markdown("""
            <div class="title-block">
                <h1>🐜 ANTNA</h1>
                <p><span class="status-indicator status-active"></span>Active Monitoring</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Voice Assistant
        st.subheader("🎤 Voice Input")
        audio_bytes = audio_recorder(
            text="",  # Minimal text
            recording_color="#00ff9d",
            neutral_color="#333333"
        )
        
        if audio_bytes:
            with st.spinner("Processing voice..."):
                transcribed_text = process_voice_input(audio_bytes)
                if transcribed_text:
                    st.info(f"You said: {transcribed_text}")
                    with st.spinner("Processing..."):
                        response = process_query_with_rag(transcribed_text, social_updates_df)
                        st.markdown(f"""
                            <div class="ai-response">
                                <strong>ANTNA:</strong><br>{response}
                            </div>
                        """, unsafe_allow_html=True)
        
        # Text Input
        user_query = st.text_input("💬 Ask ANTNA", placeholder="Type your question...")
        if user_query:
            with st.spinner("Processing..."):
                response = process_query_with_rag(user_query, social_updates_df)
                st.markdown(f"""
                    <div class="ai-response">
                        <strong>ANTNA:</strong><br>{response}
                    </div>
                """, unsafe_allow_html=True)

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["⚠️ Alerts", "🏥 Centers", "📱 Updates", "✅ Prep"])
    
    # Alerts Tab
    with tab1:
        st.markdown("<h2>⚠️ Active Alerts</h2>", unsafe_allow_html=True)
        for _, alert in alerts_df.iterrows():
            severity_color = {
                "High": "🔴", 
                "Medium": "🟡",
                "Low": "🟢"
            }.get(alert["severity"], "⚪")
            
            st.markdown(f"""
                <div class="alert-box">
                    <h3>{severity_color} {alert['type']} Alert</h3>
                    <p>📍 <b>Location:</b> {alert['location']}</p>
                    <p>🕒 <b>Time:</b> {alert['time']}</p>
                    <p>⚠️ <b>Severity:</b> {alert['severity']}</p>
                    <p>ℹ️ <b>Details:</b> {alert['description']}</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Resources Tab
    with tab2:
        st.markdown("<h2>🏥 Emergency Centers</h2>", unsafe_allow_html=True)
        
        # Interactive Map
        m = folium.Map(
            location=[25.3548, 51.1839],
            zoom_start=10,
            tiles="cartodbdark_matter"
        )
        
        for _, shelter in shelters_df.iterrows():
            capacity_pct = (shelter["current"] / shelter["capacity"]) * 100
            color = "green" if capacity_pct < 70 else "orange" if capacity_pct < 90 else "red"
            
            popup_html = f"""
                <div style="font-family: 'Space Mono', monospace; width: 200px;">
                    <h4>{shelter['name']}</h4>
                    <p><b>Capacity:</b> {shelter['current']}/{shelter['capacity']}</p>
                    <p><b>Type:</b> {shelter['type']}</p>
                    <p><b>Contact:</b> {shelter['contact']}</p>
                    <div style="background: {'#00ff9d' if capacity_pct < 70 else '#ffbe0b' if capacity_pct < 90 else '#ff006e'}; 
                         width: {capacity_pct}%; 
                         height: 10px; 
                         border-radius: 5px;">
                    </div>
                </div>
            """
            
            folium.Marker(
                [shelter["lat"], shelter["lon"]],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=color)
            ).add_to(m)
        
        st_folium(m, width=None, height=400)
        
        # Resources Grid
        st.markdown("<h3>📦 Available Resources</h3>", unsafe_allow_html=True)
        cols = st.columns(3)
        
        for idx, (_, resource) in enumerate(resources_df.iterrows()):
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class='stats-box'>
                        <h3>{resource['location']}</h3>
                        <p>💧 Water: {resource['water_supply']} units</p>
                        <p>🍲 Food: {resource['food_supply']} units</p>
                        <p>🏥 Medical: {resource['medical_kits']} kits</p>
                        <p>⚡ Power: {resource['generators']} generators</p>
                        <p>🛏️ Beds: {resource['beds']}</p>
                        <p><small>Updated: {resource['last_updated']}</small></p>
                    </div>
                """, unsafe_allow_html=True)

    # Inside Tab 3 (Social Updates)
    with tab3:
        st.markdown("<h2>📱 Live Updates</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2,3])
        with col1:
            min_trust_score = st.slider("Trust Score Filter", 0.0, 1.0, 0.7, 0.1)
        with col2:
            account_types = st.multiselect(
                "Source Filter",
                options=social_updates_df['account_type'].unique(),
                default=social_updates_df['account_type'].unique()
            )
        
        # Filter updates
        filtered_updates = social_updates_df[
            (social_updates_df['trust_score'] >= min_trust_score) &
            (social_updates_df['account_type'].isin(account_types))
        ].sort_values(['timestamp', 'trust_score'], ascending=[False, False])
        
        # Display updates
        for _, update in filtered_updates.iterrows():
            # Determine trust class and verification status
            trust_class = {
                True: "trust-high" if update['trust_score'] >= 0.9 else "trust-medium",
                False: "trust-low"
            }[update['trust_score'] >= 0.7]
            
            verification_badge = "verified" if update['verified'] else "unverified"
            
            # Select badge color based on account type and verification
            badge_color = {
                'Official': '#00ff9d',
                'Healthcare': '#00ff9d',
                'Emergency': '#00ff9d',
                'Media': '#ffbe0b',
                'Citizen': '#888888'
            }.get(update['account_type'], '#888888')
            
            st.markdown(f"""
                <div class='social-update {trust_class}'>
                    <div class="update-header">
                        <div class="account-info">
                            <strong style="color: {badge_color}">{update['account_type']}</strong>
                            <span class="username">{update['username']}</span>
                            <span class="badge {verification_badge}">
                                {' ✓' if update['verified'] else '✕'}
                            </span>
                        </div>
                    </div>
                    <div class="update-content">
                        {update['message']}
                    </div>
                    <div class="update-meta">
                        <span class="meta-item">📍 {update['location']}</span>
                        <span class="meta-separator">|</span>
                        <span class="meta-item">💯 Trust: {update['trust_score']:.2f}</span>
                        <span class="meta-separator">|</span>
                        <span class="meta-item">👥 {update['engagement']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)


    
    # Preparation Tab
    with tab4:
        st.markdown("<h2>✅ Emergency Preparedness</h2>", unsafe_allow_html=True)
        
        # Checklist in a clean container
        st.markdown("<h3>📋 Essential Items</h3>", unsafe_allow_html=True)
        with st.container():
            checklist_items = {
                "Water (5L per person per day)": False,
                "Non-perishable food": False,
                "First aid kit": False,
                "Portable fan/cooling devices": False,
                "Dust masks": False,
                "Emergency contact list": False,
                "Portable radio": False,
                "Power bank": False,
                "Important documents in waterproof container": False,
                "Sand/dust protection for electronics": False
            }
            
            for item in checklist_items:
                checklist_items[item] = st.checkbox(item)
        
        # Readiness Score with visual indicator
        readiness = sum(checklist_items.values()) / len(checklist_items) * 100
        st.markdown("<h3>🎯 Readiness Score</h3>", unsafe_allow_html=True)
        st.progress(readiness / 100)
        st.markdown(f"""
            <div class="stats-box" style="text-align: center;">
                <h2 style="color: {'#00ff9d' if readiness > 70 else '#ffbe0b' if readiness > 40 else '#ff006e'};">
                    {readiness:.1f}%
                </h2>
                <p>Preparedness Level</p>
            </div>
        """, unsafe_allow_html=True)

        # Emergency Contacts
        st.markdown("<h3>☎️ Emergency Contacts</h3>", unsafe_allow_html=True)
        st.markdown("""
            <div class="stats-box">
                <p>🚔 <b>Police:</b> 999</p>
                <p>🚑 <b>Ambulance:</b> 999</p>
                <p>🚒 <b>Civil Defence:</b> 999</p>
                <p>🏥 <b>Hamad Hospital:</b> 4439 5777</p>
                <p>⚡ <b>Kahramaa (Utilities):</b> 991</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Quick Tips
        with st.expander("📖 Quick Emergency Guidelines"):
            st.markdown("""
                <div class="stats-box">
                    <h4>Before Emergency:</h4>
                    - Keep important documents in a waterproof container<br>
                    - Maintain emergency supplies<br>
                    - Learn evacuation routes<br><br>
                    
                    <h4>During Emergency:</h4>
                    - Stay informed through official channels<br>
                    - Follow evacuation orders immediately<br>
                    - Help others if safe to do so<br><br>
                    
                    <h4>After Emergency:</h4>
                    - Check on family and neighbors<br>
                    - Document any damage<br>
                    - Follow official recovery guidance
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
