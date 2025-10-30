

import streamlit as st
import sqlite3 
import os
from PIL import Image
from datetime import datetime
from dateutil.relativedelta import relativedelta
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd
import plotly.express as px
from io import BytesIO
from contextlib import closing



def geocode_data(df):
    """Géocode les villes pour obtenir les coordonnées GPS."""
    if 'Latitude' in df.columns and 'Longitude' in df.columns and not df[['Latitude', 'Longitude']].isnull().all().all():
        return df

    geolocator = Nominatim(user_agent="sales_dashboard", timeout=10)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    locations = []
    unique_locations = df[['Ville', 'Pays']].dropna().drop_duplicates()

    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        existing_coords = df[['Ville', 'Pays', 'Latitude', 'Longitude']].dropna().drop_duplicates()
        unique_locations = unique_locations.merge(existing_coords, on=['City', 'Country'], how='left')

    for _, row in unique_locations.iterrows():
        if pd.isna(row.get('Latitude')) or pd.isna(row.get('Longitude')):
            try:
                location = geocode(f"{row['Ville']}, {row['Pays']}")
                if location:
                    locations.append({
                        'Ville': row['Ville'],
                        'Pays': row['Pays'],
                        'Latitude': location.latitude,
                        'Longitude': location.longitude
                    })
            except Exception as e:
                st.warning(f"Erreur de géocodage pour {row['Ville']}, {row['Pays']}: {str(e)}")
                continue
        else:
            locations.append({
                'Ville': row['Ville'],
                'Pays': row['Pays'],
                'Latitude': row['Latitude'],
                'Longitude': row['Longitude']
            })

    if locations:
        locations_df = pd.DataFrame(locations)
        df = pd.merge(df.drop(columns=['Latitude', 'Longitude'], errors='ignore'), locations_df, on=['City', 'Country'], how='left')
    return df






BACKGROUND_COLOR = '#040233'
ACCENT_COLOR = '#bb8654'
TEXT_COLOR = '#ffe7ad'
SECONDARY_COLOR = '#b28765'

from ui_utils import display_logo

def apply_custom_styles():
    """Applies custom CSS styles globally, making all text bold while preserving colors."""
    st.markdown(f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        /* Global font and text styling - Make ALL text bold */
        body, .stApp, .main, p, div, span, label, h1, h2, h3, h4, h5, h6, table, th, td {{
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
            font-weight: bold !important; /* Make all text bold */
        }}

        /* Masquer les éléments par défaut de Streamlit */
        footer {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
        
        /* Main container styling */
        .main .block-container {{
            max-width: 95%;
        }}
        
        /* Expander styling */
        div[data-testid="stExpander"] {{
            border: 1px solid {ACCENT_COLOR};
            border-radius: 5px;
            margin: 10px 0;
        }}
        
        div[data-testid="stExpander"] div[role="button"] p {{
            font-weight: bold; /* Already bold, ensure consistency */
            color: {TEXT_COLOR};
            font-size: 1.1rem;
        }}
        
        .streamlit-expanderContent {{
            background-color: {BACKGROUND_COLOR};
            padding: 15px;
            border-radius: 0 0 5px 5px;
            border-left: 4px solid {ACCENT_COLOR};
        }}
        
        /* Custom styled boxes */
        .custom-box {{
            background-color: {BACKGROUND_COLOR};
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid {ACCENT_COLOR};
            color: {TEXT_COLOR};
            margin-bottom: 15px;
        }}
        
        hr {{
            border-color: {ACCENT_COLOR};
            margin: 15px 0;
        }}

        /* ------------------- STYLE DES BOUTONS (sauf menu) ------------------- */
        /* Cible uniquement les boutons hors sidebar, incluant those in columns/horizontal blocks */
        .stButton:not([data-testid="stSidebar"]) > button,
        .stButton:not([class*="sidebar"]) > button,
        div[data-testid="column"] .stButton > button,
        div[data-testid="stHorizontalBlock"] .stButton > button {{
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            border: 1px solid #100f3d !important;
            border-radius: 5px !important;
            padding: 10px 20px !important;
            font-weight: bold !important; /* Ensure button text is bold */
            transition: all 0.2s !important;
            box-shadow: none !important;
        }}
        
        .stButton:not([data-testid="stSidebar"]) > button:hover,
        .stButton:not([class*="sidebar"]) > button:hover,
        div[data-testid="column"] .stButton > button:hover,
        div[data-testid="stHorizontalBlock"] .stButton > button:hover {{
            background-color: #0e0d35 !important;
            color: #ffe7ad !important;
            border-color: #bb8654 !important;
            opacity: 0.95;
        }}
        
        /* Boutons de login spécifiquement */
        div[class*="login"] .stButton > button,
        div[class*="Login"] .stButton > button {{
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            font-weight: bold !important; /* Ensure login button text is bold */
            border: 1px solid #bb8654 !important;
        }}
        
        div[class*="login"] .stButton > button:hover,
        div[class*="Login"] .stButton > button:hover {{
            background-color: #0e0d35 !important;
            color: #ffe7ad !important;
            opacity: 0.9;
        }}
        
        /* ------------------- AUTRES ÉLÉMENTS ------------------- */
        /* Titre personnalisé */
        .custom-title {{
            background-image: linear-gradient(to right, #100f3d, #bb8654);
            color: #ffe7ad !important;
            padding: 40px;
            border-radius: 5px;
            text-align: center;
            font-size: 40px;
            font-weight: bold; /* Ensure title is bold */
            height: 160px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}

        /* Tableaux */
        table.dataframe th,
        table th {{
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            padding: 12px 15px !important;
            text-align: center !important;
            position: sticky !important;
            top: 0 !important;
            font-weight: bold !important; /* Ensure table headers are bold */
            border: 1px solid #100f3d !important;
        }}

        table.dataframe td,
        table td {{
            padding: 12px 15px !important;
            text-align: center !important;
            border: 1px solid #e0e0e0 !important;
            background-color: #ffffff !important;
            color: #040233 !important;
            font-size: 14px !important;
            font-weight: bold !important; /* Ensure table cell text is bold */
        }}
        
        table.dataframe tr:nth-child(even) td,
        table tr:nth-child(even) td {{
            background-color: #f9f9f9 !important;
        }}
        
        table.dataframe tr:hover td,
        table tr:hover td {{
            background-color: #f0f0f0 !important;
            color: #040233 !important;
        }}
        
        /* Onglets */
        .stTabs [role="tablist"] {{
            border-bottom: 1px solid #bb8654;
        }}
        
        .stTabs [role="tab"] {{
            color: #040233;
            font-weight: bold !important; /* Ensure tab text is bold */
            padding: 10px 20px;
            margin-right: 5px;
            border-radius: 6px 6px 0 0;
            border: 1px solid transparent;
        }}
        
        .stTabs [role="tab"]:hover {{
            color: #bb8654;
            background-color: rgba(187, 134, 84, 0.1);
        }}
        
        .stTabs [aria-selected="true"] {{
            color: #bb8654 !important;
            border-color: #040233 #040233 #bb8654 !important;
            border-width: 1px 1px 3px 1px !important;
            font-weight: bold !important; /* Ensure selected tab text is bold */
        }}

        /* Cartes d'offres */
        .offer-card {{
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin: 10px;
            position: relative;
            height: 180px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid #e0e0e0;
        }}
        
        .offer-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }}
        
        .offer-info {{
            background: linear-gradient(transparent, rgba(16, 15, 61, 0.85)) !important;
            color: white !important;
            font-weight: bold !important; /* Ensure offer info text is bold */
        }}
        
        /* Input fields */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {{
            border: 1px solid #bb8654 !important;
            font-weight: bold !important; /* Ensure input text is bold */
        }}
    </style>
    """, unsafe_allow_html=True)
    """Applies custom CSS styles globally."""
    st.markdown(f"""
    <style>
        /* Main container styling */
        .main .block-container {{
            max-width: 95%;
        }}
        
        /* Expander styling */
        div[data-testid="stExpander"] {{
            border: 1px solid {ACCENT_COLOR};
            border-radius: 5px;
            margin: 10px 0;
        }}
        
        div[data-testid="stExpander"] div[role="button"] p {{
            font-weight: bold;
            color: {TEXT_COLOR};
            font-size: 1.1rem;
        }}
        
        .streamlit-expanderContent {{
            background-color: {BACKGROUND_COLOR};
            padding: 15px;
            border-radius: 0 0 5px 5px;
            border-left: 4px solid {ACCENT_COLOR};
        }}
        
        /* Custom styled boxes */
        .custom-box {{
            background-color: {BACKGROUND_COLOR};
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid {ACCENT_COLOR};
            color: {TEXT_COLOR};
            margin-bottom: 15px;
        }}
        
        hr {{
            border-color: {ACCENT_COLOR};
            margin: 15px 0;
        }}
    </style>
    """, unsafe_allow_html=True)


def add_custom_css():
    """
    Ajoute un CSS personnalisé unifié avec les boutons en #100f3d
    sans bordures et conserve le style original des boutons du menu.
    """
    custom_css = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        /* Masquer les éléments par défaut de Streamlit */
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        /* Styles de base */
        body, .stApp, .main {
            background-color: #fcfcfc !important;
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
            color: #040233 !important;
            font-weight: bold !important;
        }
        
        /* ------------------- STYLE DES BOUTONS (sauf menu) ------------------- */
        /* Cible uniquement les boutons hors sidebar */
        .stButton:not([data-testid="stSidebar"]) > button,
        .stButton:not([class*="sidebar"]) > button {
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            border: none !important; /* Suppression de la bordure */
            border-radius: 5px !important;
            padding: 10px 20px !important;
            font-weight: 500 !important;
            transition: all 0.2s !important;
            box-shadow: none !important; /* Suppression de l'ombre si présente */
        }
        
        .stButton:not([data-testid="stSidebar"]) > button:hover,
        .stButton:not([class*="sidebar"]) > button:hover {
            background-color: #0e0d35 !important; /* Légère variation de couleur au hover */
            color: #ffe7ad !important;
            opacity: 0.95;
        }
        
        /* Boutons de login spécifiquement */
        div[class*="login"] .stButton > button,
        div[class*="Login"] .stButton > button {
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            font-weight: bold !important;
            border: none !important; /* Suppression de la bordure */
        }
        
        div[class*="login"] .stButton > button:hover,
        div[class*="Login"] .stButton > button:hover {
            background-color: #ffe7ad !important;
            color: #ffe7ad !important;
        }
        
        /* ------------------- AUTRES ÉLÉMENTS ------------------- */
        /* Titre personnalisé */
        .custom-title {
            background-image: linear-gradient(to right, #100f3d, #bb8654);
            color: #ffe7ad !important;
            padding: 40px;
            border-radius: 5px;
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            height: 160px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        /* Tableaux */
        table.dataframe th,
        table th {
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            padding: 12px 15px !important;
            text-align: center !important;
            position: sticky !important;
            top: 0 !important;
            font-weight: 600 !important;
            border: none !important; /* Suppression de la bordure */
        }
        
        /* Onglets */
        .stTabs [role="tablist"] {
            border-bottom: 1px solid #bb8654;
        }
        
        .stTabs [aria-selected="true"] {
            color: #bb8654 !important;
            border: none !important; /* Suppression de la bordure */
            border-bottom: 3px solid #bb8654 !important; /* Garde uniquement la bordure inférieure */
        }

        /* Cartes d'offres */
        .offer-info {
            background: linear-gradient(transparent, rgba(16, 15, 61, 0.85)) !important;
            border: none !important; /* Suppression de la bordure si présente */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    """
    Ajoute un CSS personnalisé unifié avec les boutons en #100f3d
    et conserve le style original des boutons du menu.
    """
    custom_css = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        /* Masquer les éléments par défaut de Streamlit */
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        /* Styles de base */
        body, .stApp, .main {
            background-color: #fcfcfc !important;
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
            color: #040233 !important;
        }
         div[data-testid="column"] .stButton>button {
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            border: 1px solid #100f3d !important;
            border-radius: 5px !important;
            padding: 10px 20px !important;
            font-weight: 500 !important;
            transition: all 0.2s !important;
        }
        
        div[data-testid="column"] .stButton>button:hover {
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            border-color: #bb8654 !important;
            opacity: 0.9;
        }
        
        /* Boutons spécifiques dans les colonnes */
        div[data-testid="stHorizontalBlock"] .stButton>button {
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            font-weight: bold !important;
            
        }
        
        div[data-testid="stHorizontalBlock"] .stButton>button:hover {
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            opacity: 0.9;
        }
        
        .stButton:not([data-testid="stSidebar"]) > button:hover,
        .stButton:not([class*="sidebar"]) > button:hover {
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            border-color: #bb8654 !important;
            opacity: 0.9;
        }
        
        /* Boutons de login spécifiquement */
        div[class*="login"] .stButton > button,
        div[class*="Login"] .stButton > button {
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            font-weight: bold !important;
            border: 1px solid #bb8654 !important;
        }
        
        div[class*="login"] .stButton > button:hover,
        div[class*="Login"] .stButton > button:hover {
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            opacity: 0.9;
        }
        
        /* ------------------- AUTRES ÉLÉMENTS ------------------- */
        /* Titre personnalisé */
        .custom-title {
            background-image: linear-gradient(to right, #100f3d, #bb8654);
            color: #ffe7ad !important;
            padding: 40px;
            border-radius: 5px;
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            height: 160px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        /* Tableaux */
        table.dataframe th,
        table th {
            background-color: #100f3d !important;
            color: #ffe7ad !important;
            padding: 12px 15px !important;
            text-align: center !important;
            position: sticky !important;
            top: 0 !important;
            font-weight: 600 !important;
            border: 1px solid #100f3d !important;
        }
        
        /* Onglets */
        .stTabs [role="tablist"] {
            border-bottom: 1px solid #bb8654;
        }
        
        .stTabs [aria-selected="true"] {
            color: #bb8654 !important;
            border-color:   #bb8654 !important;
        }

        /* Cartes d'offres */
        .offer-info {
            background: linear-gradient(transparent, rgba(16, 15, 61, 0.85)) !important;
        }
        
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    """
    Ajoute un CSS personnalisé unifié avec un style professionnel
    en conservant le style original des boutons du menu.
    """
    custom_css = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        /* Masquer les éléments par défaut de Streamlit */
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        /* Styles de base */
        body, .stApp, .main {
            background-color: #fcfcfc !important;
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
            color: #040233 !important;
        }
        
        /* ------------------- STYLE DES BOUTONS (sauf menu) ------------------- */
        /* Cible uniquement les boutons hors sidebar */
        .stButton:not([data-testid="stSidebar"]) > button,
        .stButton:not([class*="sidebar"]) > button {
            background-color: #040233 !important;
            color: #ffe7ad !important;
            border: 1px solid #040233 !important;
            border-radius: 5px !important;
            padding: 10px 20px !important;
            font-weight: 500 !important;
            transition: all 0.2s !important;
        }
        
        .stButton:not([data-testid="stSidebar"]) > button:hover,
        .stButton:not([class*="sidebar"]) > button:hover {
            background-color: #bb8654 !important;
            color: #040233 !important;
            border-color: #040233 !important;
        }
        
        /* Boutons de login spécifiquement */
        div[class*="login"] .stButton > button,
        div[class*="Login"] .stButton > button {
            background-color: #040233 !important;
            color: #ffe7ad !important;
            font-weight: bold !important;
            border: 1px solid #bb8654 !important;
        }
        
        div[class*="login"] .stButton > button:hover,
        div[class*="Login"] .stButton > button:hover {
            background-color: #bb8654 !important;
            color: #040233 !important;
        }
        
        /* ------------------- AUTRES ÉLÉMENTS ------------------- */
        /* Titre personnalisé */
        .custom-title {
            background-image: linear-gradient(to right, #040233, #bb8654);
            color: #ffe7ad !important;
            padding: 40px;
            border-radius: 5px;
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            height: 160px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        /* Tableaux */
        table.dataframe th,
        table th {
            background-color: #040233 !important;
            color: #ffe7ad !important;
            padding: 12px 15px !important;
            text-align: center !important;
            position: sticky !important;
            top: 0 !important;
            font-weight: 600 !important;
            border: 1px solid #040233 !important;
        }
        
        table.dataframe td,
        table td {
            padding: 12px 15px !important;
            text-align: center !important;
            border: 1px solid #e0e0e0 !important;
            background-color: #ffffff !important;
            color: #040233 !important;
            font-size: 14px !important;
        }
        
        table.dataframe tr:nth-child(even) td,
        table tr:nth-child(even) td {
            background-color: #f9f9f9 !important;
        }
        
        table.dataframe tr:hover td,
        table tr:hover td {
            background-color: #f0f0f0 !important;
            color: #040233 !important;
        }

        /* Onglets */
        .stTabs [role="tablist"] {
            border-bottom: 1px solid #bb8654;
        }
        
        .stTabs [role="tab"] {
            color: #040233;
            font-weight: 500;
            padding: 10px 20px;
            margin-right: 5px;
            border-radius: 6px 6px 0 0;
            border: 1px solid transparent;
        }
        
        .stTabs [role="tab"]:hover {
            color: #bb8654;
            background-color: rgba(187, 134, 84, 0.1);
        }
        
        .stTabs [aria-selected="true"] {
            color: #bb8654 !important;
            border-color: #040233 #040233 #bb8654 !important;
            border-width: 1px 1px 3px 1px !important;
            font-weight: 600 !important;
        }

        /* Cartes d'offres */
        .offer-card {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin: 10px;
            position: relative;
            height: 180px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid #e0e0e0;
        }
        
        .offer-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        
        .offer-info {
            background: linear-gradient(transparent, rgba(4, 2, 51, 0.85));
            color: white !important;
        }
        
        /* Input fields */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border: 1px solid #bb8654 !important;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
def calculate_age(birth_date):
    if pd.isnull(birth_date):
        return "N/A"
    try:
        today = datetime.now()
        delta = relativedelta(today, birth_date)
        return f"{delta.years} ans"
    except Exception as e:
        print(f"Erreur calcul âge: {e}")
        return "N/A"

def calculate_anciennete(date_in):
    if pd.isnull(date_in):
        return "N/A"
    try:
        today = datetime.now()
        delta = relativedelta(today, date_in)
        return f"{delta.years} ans, {delta.months} mois"
    except Exception as e:
        print(f"Erreur calcul ancienneté: {e}")
        return "N/A"

def color_cells(val):
    if val == "Pause_Dej":
        return "background-color: #ffcb84"
    elif val == "G2P":
        return "background-color: #5ac2db"
    return ""

# === Visualisations ===
def plot_charts(effectifs_df, ventes_df):
    if effectifs_df.empty or ventes_df.empty:
        st.warning("Données insuffisantes pour générer les graphiques")
        return

    if 'Competence' in effectifs_df.columns:
        data = effectifs_df['Competence'].value_counts().reset_index()
        data.columns = ['Competence', 'Nombre d\'Agents']
        fig1 = px.bar(data, x='Competence', y='Nombre d\'Agents', text_auto=True,
                      color='Nombre d\'Agents', title="Agents par compétence",
                      color_continuous_scale=['#040233', '#bb8654', '#ffe7ad'])
        fig1.update_layout(xaxis_title="Compétence", yaxis_title="Nombre d'Agents",
                            plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF')
        st.plotly_chart(fig1)

    if 'ID_Citrix' in ventes_df.columns and 'Competence' in effectifs_df.columns:
        ventes_df = ventes_df.copy()
        map_comp = effectifs_df.set_index('ID_Citrix')['Competence']
        ventes_df['Competence'] = ventes_df['ID_Citrix'].map(map_comp)
        if 'TRANSACTION_AMOUNT' in ventes_df.columns:
            ventes_grouped = ventes_df.groupby('Competence')['TRANSACTION_AMOUNT'].count().reset_index()
            ventes_grouped.columns = ['Competence', 'Nombre de Ventes']
            fig2 = px.bar(ventes_grouped, x='Competence', y='Nombre de Ventes', text_auto=True,
                          color='Nombre de Ventes', title="Ventes par compétence",
                          color_continuous_scale=['#040233', '#b28765', '#ffe7ad'])
            fig2.update_layout(xaxis_title="Compétence", yaxis_title="Nombre de Ventes",
                                plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF')
            st.plotly_chart(fig2)

    if all(col in ventes_df.columns for col in ['Competence', 'Offres', 'TRANSACTION_AMOUNT']):
        group = ventes_df.groupby(['Competence', 'Offres'])['TRANSACTION_AMOUNT'].sum().reset_index()
        fig3 = px.bar(group, x='Offres', y='TRANSACTION_AMOUNT', text_auto=True,
                      color='TRANSACTION_AMOUNT', facet_col='Competence',
                      color_continuous_scale=['#040233', '#bb8654', '#ffe7ad'],
                      title="Ventes par offre et compétence")
        fig3.update_layout(xaxis_title="Offres", yaxis_title="Montant des Ventes",
                            plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF')
        st.plotly_chart(fig3)

# === Export Excel ===
def export_to_excel(df, sheet_name="Data"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

# === Fonctions de base de données ===
def get_db_connection():
    """Tente de se connecter à la base de données SQLite."""
    try:
        conn = sqlite3.connect('Accor_BD_Sqlite.db')
        conn.row_factory = sqlite3.Row #
        return conn
    except sqlite3.Error as e:
        st.error(f"Erreur de connexion à la base de données SQLite: {e}")
        return None

def authenticate(login, password):
    """Authentifie l'utilisateur et retourne le succès et l'ID_Citrix."""
    conn = get_db_connection()
    if not conn:
        return False, None
        
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ID_Citrix FROM Users 
            WHERE login = ? AND password = ?
        """, (login, password))
        user = cursor.fetchone()
        return (True, user['ID_Citrix']) if user else (False, None)
    except sqlite3.Error as e:
        st.error(f"Erreur d'authentification: {e}")
        return False, None
    finally:
        if conn: conn.close()

def get_user_status(ID_Citrix):
    """Récupère le statut de l'utilisateur."""
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Statut FROM effectifs WHERE ID_Citrix = ?", (ID_Citrix,))
        result = cursor.fetchone()
        return result['Statut'] if result else None
    except sqlite3.Error as e:
        st.error(f"Erreur de récupération du statut: {e}")
        return None
    finally:
        if conn: conn.close()

def get_user_team(ID_Citrix):
    """Récupère l'équipe de l'utilisateur. Retourne le Nom_Prenom de l'utilisateur s'il est manager."""
    conn = get_db_connection()
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT Team, Nom_Prenom, Statut FROM effectifs WHERE ID_Citrix = ?", (ID_Citrix,))
            result = cursor.fetchone()
            if result:
                if result['Statut'] == 'Manager':
                    return result['Nom_Prenom'] # Si manager, sa "team" est son propre nom
                else:
                    return result['Team']
            return None
    except sqlite3.Error as e:
        st.error(f"Erreur de récupération de l'équipe: {e}")
        return None
    finally:
        if conn: conn.close()

def get_user_name(ID_Citrix):
    """Récupère le nom complet de l'utilisateur."""
    conn = get_db_connection()
    if not conn:
        return "Utilisateur"
        
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Nom_Prenom FROM effectifs WHERE ID_Citrix = ?", (ID_Citrix,))
        result = cursor.fetchone()
        return result['Nom_Prenom'] if result else "Utilisateur"
    except sqlite3.Error as e:
        st.error(f"Erreur de récupération du nom: {e}")
        return "Utilisateur"
    finally:
        if conn: conn.close()

def get_effectifs_data():
    """Récupère les données des effectifs et des ventes."""
    conn = get_db_connection()
    if not conn:
        return None, None
        
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        
        # Vérification des tables
        required_tables = ['effectifs', 'sales', 'retards', 'absences']
        missing_tables = [t for t in required_tables if t not in tables]
        if missing_tables: 
            st.error(f"Tables manquantes dans la base de données: {', '.join(missing_tables)}. Veuillez vérifier les noms des tables (majuscules/minuscules).")
            return None, None

        effectifs_df = pd.read_sql("SELECT * FROM effectifs WHERE Statut = 'Agent';", conn)
        ventes_df = pd.read_sql("SELECT * FROM sales;", conn)

        for col in ['Birth_Date', 'Date_In']:
            if col in effectifs_df.columns:
                effectifs_df[col] = pd.to_datetime(effectifs_df[col], errors='coerce')

        if 'Date_In' in effectifs_df.columns:
            effectifs_df['Anciennete'] = effectifs_df['Date_In'].apply(calculate_anciennete)
        if 'Birth_Date' in effectifs_df.columns:
            effectifs_df['Age'] = effectifs_df['Birth_Date'].apply(calculate_age)

        return effectifs_df, ventes_df
    except Exception as err:
        st.error(f"Erreur lors de la récupération des données : {str(err)}")
        return None, None
    finally:
        if conn: conn.close()
def get_absences_agent_or_team(start_date, end_date, id_citrix=None, team_name=None):
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame() # Retourne un DataFrame vide si pas de connexion

    try:
        start_datetime_obj = datetime.combine(start_date, datetime.min.time())
        end_datetime_obj = datetime.combine(end_date, datetime.max.time())

        # Formatter en string pour la requête SQL
        start_datetime_str = start_datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        end_datetime_str = end_datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

        query = """
        SELECT DISTINCT e.ID_Citrix, e.Nom_Prenom, a.Date_Abs, a.Justif_Absence, a.Commentaire_Absence
        FROM effectifs e
        JOIN absences a ON e.ID_Citrix = a.ID_Citrix
        WHERE a.Date_Abs BETWEEN ? AND ?
        """
        params = [start_datetime_str, end_datetime_str]

        if id_citrix:
            query += " AND e.ID_Citrix = ?"
            params.append(str(id_citrix).strip()) # S'assurer que l'ID est bien formaté et stripé
        elif team_name:
            query += " AND e.Team = ?"
            params.append(team_name)
        
        query += " ORDER BY e.Nom_Prenom, a.Date_Abs"

        df = pd.read_sql_query(query, conn, params=params)
        return df
    except pd.io.sql.DatabaseError as e:
        st.error(f"Erreur de base de données lors de la récupération des absences : {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue lors de la récupération des absences : {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
# --- FONCTIONS pour récupérer les données spécifiques à l'équipe ---
def get_retards_agent_or_team(start_date, end_date, id_citrix=None, team_name=None):
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame() # Retourne un DataFrame vide si pas de connexion

    try:
        start_datetime_obj = datetime.combine(start_date, datetime.min.time())
        end_datetime_obj = datetime.combine(end_date, datetime.max.time())

        start_datetime_str = start_datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        end_datetime_str = end_datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

        query = """
        SELECT DISTINCT e.ID_Citrix, e.Nom_Prenom, r.Date_Ret, r.Dur_Retard, r.Motif, r.Justif_Retard
        FROM effectifs e
        JOIN retards r ON e.ID_Citrix = r.ID_Citrix
        WHERE r.Date_Ret BETWEEN ? AND ?
        """
        params = [start_datetime_str, end_datetime_str]

        if id_citrix:
            query += " AND e.ID_Citrix = ?"
            params.append(str(id_citrix).strip()) # S'assurer que l'ID est bien formaté et stripé
        elif team_name:
            query += " AND e.Team = ?"
            params.append(team_name)
        
        query += " ORDER BY e.Nom_Prenom, r.Date_Ret"

        df = pd.read_sql_query(query, conn, params=params)
        return df
    except pd.io.sql.DatabaseError as e:
        st.error(f"Erreur de base de données lors de la récupération des retards : {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue lors de la récupération des retards : {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
def get_absences_equipe(start_date, end_date, team_name):
    conn = get_db_connection()
    try:
        query = """
        SELECT DISTINCT e.ID_Citrix, e.Nom_Prenom, a.Date_Abs, a.Justif_Absence, a.Commentaire_Absence
        FROM effectifs e
        JOIN absences a ON e.ID_Citrix = a.ID_Citrix
        WHERE e.Statut = 'Agent' AND a.Date_Abs BETWEEN ? AND ? AND e.Team = ?
        ORDER BY e.Nom_Prenom, a.Date_Abs
        """
        # We've replaced 'a.Type_Abs' with 'a.Justif_Absence' and 'a.Commentaire_Absence'
        # based on your 'absences' table schema.
        df = pd.read_sql_query(query, conn, params=(start_date, end_date, team_name))
        return df
    except pd.io.sql.DatabaseError as e:
        st.error(f"Erreur de base de données lors de la récupération des absences : {e}")
        return pd.DataFrame() # Always return an empty DataFrame on error
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue lors de la récupération des absences : {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_retards_equipe(start_date, end_date, team_name): # <-- C'EST ICI LE CHANGEMENT
    conn = get_db_connection()
    try:
        query = """
        SELECT DISTINCT e.ID_Citrix, e.Nom_Prenom, r.Date_Ret, r.Dur_Retard, r.Motif, r.Justif_Retard
        FROM effectifs e
        JOIN retards r ON e.ID_Citrix = r.ID_Citrix
        WHERE e.Statut = 'Agent'
          AND r.Date_Ret BETWEEN ? AND ?  -- Filtre par date
          AND e.Team = ?                 -- Filtre par équipe
          -- SUPPRIMÉ : AND r.Justif_Retard = 'Non' -- Cette ligne est retirée pour inclure tous les retards
        ORDER BY e.Nom_Prenom, r.Date_Ret
        """
        df = pd.read_sql_query(query, conn, params=(start_date, end_date, team_name))
        return df
    except pd.io.sql.DatabaseError as e:
        st.error(f"Erreur de base de données lors de la récupération des retards : {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue lors de la récupération des retards : {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
            
def get_retards_non_justifies_equipe(start_date, end_date, team_name):
    conn = get_db_connection()
    try:
        query = """
        SELECT DISTINCT e.ID_Citrix, e.Nom_Prenom, r.Date_Ret, r.Dur_Retard, r.Motif, r.Justif_Retard
        FROM effectifs e
        JOIN retards r ON e.ID_Citrix = r.ID_Citrix
        WHERE e.Statut = 'Agent' AND r.Date_Ret BETWEEN ? AND ? AND e.Team = ? AND r.Justif_Retard = 'Non'
        ORDER BY e.Nom_Prenom, r.Date_Ret
        """
        # We've replaced a hypothetical 'Type_Retard' with 'r.Motif' and added 'r.Justif_Retard',
        # based on your 'retards' table schema.
        df = pd.read_sql_query(query, conn, params=(start_date, end_date, team_name))
        return df
    except pd.io.sql.DatabaseError as e:
        st.error(f"Erreur de base de données lors de la récupération des retards : {e}")
        return pd.DataFrame() # Always return an empty DataFrame on error
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue lors de la récupération des retards : {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_sales_equipe(start_date, end_date, team_name):
    """
    Récupère les ventes réalisées par les agents d'une équipe donnée sur une période.
    """
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        query = """
            SELECT DISTINCT e.ID_Citrix, e.Nom_Prenom, s.Date_Sale, s.TRANSACTION_AMOUNT, s.Offres
            FROM effectifs e
            JOIN sales s ON e.ID_Citrix = s.ID_Citrix
            WHERE e.Statut = 'Agent'
              AND s.Date_Sale BETWEEN ? AND ?
              AND e.Team = ?
            ORDER BY e.Nom_Prenom, s.Date_Sale
        """
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        print(f"DEBUG: Requête sales exécutée avec dates={start_date_str}, {end_date_str}, équipe={team_name}")

        df = pd.read_sql_query(query, conn, params=(start_date_str, end_date_str, team_name))
        return df
    except sqlite3.Error as e:
        st.error(f"Erreur SQLite lors de la récupération des ventes : {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue lors de la récupération des ventes : {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def get_recoins_equipe(start_date, end_date, team_name):
    """
    Récupère les données de "recoins" (à définir ce que c'est) pour une équipe sur une période.
    Assurez-vous d'avoir une table 'recoins' ou le nom de table correct.
    """
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        # NOTE: Remplacez 'recoins' et les colonnes par les vrais noms de votre table et colonnes
        query = """
            SELECT DISTINCT e.ID_Citrix, e.Nom_Prenom, r.Date_Recoin, r.Type_Recoin, r.Montant_Recoin
            FROM effectifs e
            JOIN recoins r ON e.ID_Citrix = r.ID_Citrix
            WHERE e.Statut = 'Agent'
              AND r.Date_Recoin BETWEEN ? AND ?
              AND e.Team = ?
            ORDER BY e.Nom_Prenom, r.Date_Recoin
        """
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        print(f"DEBUG: Requête recoins exécutée avec dates={start_date_str}, {end_date_str}, équipe={team_name}")

        df = pd.read_sql_query(query, conn, params=(start_date_str, end_date_str, team_name))
        return df
    except sqlite3.Error as e:
        st.error(f"Erreur SQLite lors de la récupération des recoins : {e}. Vérifiez si la table 'recoins' existe et ses colonnes.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue lors de la récupération des recoins : {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

# === Page de connexion ===
def login_page():
    add_custom_css
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        col1, col2 = st.columns([1, 2])

        with col1:
            display_logo(os.path.join("Images", "AC.png"), width=200)

        with col2:
            st.subheader("Page de connexion")
            login = st.text_input("Nom d'utilisateur : ")
            password = st.text_input("Mot de passe :", type="password")

            if st.button("Se connecter"):
                is_authenticated, ID_Citrix_User = authenticate(login, password)
                
                if is_authenticated:
                    user_team = get_user_team(ID_Citrix_User)
                    user_status = get_user_status(ID_Citrix_User)
                    user_name = get_user_name(ID_Citrix_User)
                    
                    st.session_state.update({
                        "authenticated": True,
                        "ID_Citrix": ID_Citrix_User,
                        "ID_Citrix_User": ID_Citrix_User,
                        "Nom_Prenom": user_name,
                        "Team": user_team, 
                        "Statut": user_status
                    })
                    
                    st.success(f"Connexion réussie en tant que {user_name}!")
                    st.rerun() 
                else:
                    st.error("Échec de l'authentification. Veuillez vérifier vos informations.")