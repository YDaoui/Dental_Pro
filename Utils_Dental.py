import streamlit as st
import pandas as pd
import sqlite3
import pyodbc
from contextlib import closing
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import plotly.express as px
import folium
from streamlit_folium import st_folium
import numpy as np
from dotenv import load_dotenv
import os


load_dotenv()

def add_custom_css():
    st.markdown("""
        <style>
            /* Contenu principal à 70% */
            section.main > div:first-child > div:first-child > div:first-child > div:first-child {
                width: 70%;
                margin: 0 auto;
            }
            
            /* Ajustement pour les éléments full-width comme les headers */
            section.main > div:first-child > div:first-child > div:first-child > div:first-child > div:first-child {
                width: 100%;
            }
            
            /* General Body Background - BLANC PUR */
            body {
                background-color: #FFFFFF; /* Fond blanc pur */
                color: #3D3B40; /* Primary Dark Blue for default text on light background */
            }
            .stApp {
                background-color: #FFFFFF; /* Streamlit app background */
            }

            /* ==== General Titles ==== */
            h1 {
                color: #3D3B40; /* Primary Dark Blue */
                margin-bottom: 10px;
                font-size: 3em;
                text-align: center;
                padding-bottom: 6px;
                border-bottom: 3px solid #525CEB; /* Accent Blue/Purple */
                font-weight: 900;
            }
            h2 {
                color: #3D3B40; /* Primary Dark Blue */
                margin-top: 8px;
                margin-bottom: 25px;
                font-size: 2em;
                text-align: center;
                font-weight: 800;
            }
            h3 {
                color: #3D3B40; /* Primary Dark Blue */
                margin-top: 35px;
                margin-bottom: 20px;
                border-bottom: 2px solid #525CEB; /* Accent Blue/Purple */
                padding-bottom: 6px;
                font-size: 1.6em;
                font-weight: 700;
            }
            hr {
                border: none;
                border-top: 2px solid #525CEB; /* Accent Blue/Purple */
                margin: 20px auto 25px auto;
                width: 85%;
                border-radius: 5px;
            }

            /* ==== Tabs ==== */
            .stTabs [data-baseweb="tab-list"] button {
                background-color: #BFCFE7; /* Lighter Accent/Text for tab background */
                border-radius: 8px 8px 0 0;
                padding: 10px 16px;
                margin-right: 8px;
                border: 1px solid #525CEB; /* Accent Blue/Purple */
                border-bottom: none;
                color: #3D3B40; /* Primary Dark Blue for text */
                font-weight: bold;
                font-size: 1em;
                transition: all 0.2s ease-in-out;
            }
            .stTabs [data-baseweb="tab-list"] button:hover {
                background-color: #525CEB; /* Accent Blue/Purple for hover */
                color: #FFFFFF; /* Blanc pur pour le texte au survol (contre le bleu) */
            }
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
                background-color: #3D3B40; /* Primary Dark Blue for selected tab */
                color: #BFCFE7; /* Lighter Accent/Text for text on selected tab */
                border-color: #3D3B40; /* Primary Dark Blue */
            }
            .stTabs {
                margin-top: -10px;
                margin-bottom: 20px;
            }

            /* ==== Metric Cards ==== */
            .metric-card {
                background-color: #BFCFE7; /* Lighter Accent/Text for card background */
                border: 1px solid #525CEB; /* Accent Blue/Purple */
                border-left: 6px solid #3D3B40; /* Primary Dark Blue for prominent border */
                border-radius: 10px;
                padding: 12px;
                margin-bottom: 12px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
                text-align: center;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                color: #3D3B40; /* Primary Dark Blue for text */
                min-height: 80px;
            }
            .metric-card:hover {
                transform: translateY(-4px);
                box-shadow: 3px 3px 14px rgba(0,0,0,0.5);
            }
            .metric-title {
                color: #3D3B40; /* Primary Dark Blue */
                font-size: 0.95em;
                font-weight: 700;
                margin-bottom: 6px;
                text-transform: uppercase;
                letter-spacing: 0.6px;
            }
            .metric-value {
                color: #3D3B40; /* Primary Dark Blue */
                font-size: 2em;
                font-weight: 800;
                line-height: 1;
            }

            /* ==== UPDATED: Team Performance Cards (for Top 3 or all teams) ==== */
            .team-performance-card {
                background-color: #BFCFE7; /* Consistent with metric-card background */
                border: 1px solid #525CEB; /* Accent Blue/Purple */
                border-left: 6px solid #3D3B40; /* Primary Dark Blue for prominent border, consistent */
                border-radius: 10px;
                padding: 15px; /* Slightly more padding for multiple stats */
                margin-bottom: 12px; /* Consistent margin */
                box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
                text-align: left; /* Align text to left for better readability of multiple stats */
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                color: #3D3B40; /* Primary Dark Blue for text */
            }
            .team-performance-card:hover {
                transform: translateY(-4px); /* Hover effect consistent with metric-card */
                box-shadow: 3px 3px 14px rgba(0,0,0,0.5);
            }
            .team-performance-title {
                font-size: 1.4em; /* PLUS GRAND: Team name */
                font-weight: 800; /* More bold */
                color: #3D3B40; /* Primary Dark Blue */
                margin-bottom: 8px;
            }
            .team-stat-row {
                display: flex;
                justify-content: space-between;
                align-items: flex-end; /* Align values at the bottom */
                margin-bottom: 8px; /* Space between rows */
            }
            .team-stat-item {
                display: flex;
                flex-direction: column; /* Stack label and value */
                text-align: center; /* Center align text within each item */
                flex: 1; /* Distribute space evenly */
                padding: 0 5px; /* Little padding */
            }
            .team-stat-item:first-child { text-align: left; } /* Align first item to left */
            .team-stat-item:last-child { text-align: right; } /* Align last item to right */

            .team-stat-label {
                font-size: 0.9em; /* Slightly larger label */
                color: #555; /* Slightly lighter color for labels */
                margin-bottom: 3px;
                font-weight: 600;
            }
            .team-stat-value {
                font-size: 1.6em; /* PLUS GRAND: Value size for sales & transactions */
                font-weight: 800; /* Bolder */
                color: #3D3B40; /* Primary Dark Blue */
                line-height: 1;
            }
            .team-conversion-value {
                font-size: 1.8em; /* PLUS GRAND: Larger for conversion rate */
                font-weight: 900;
                color: #28a745; /* Strong green for conversion */
            }
            .sms-rate-section {
                display: flex;
                justify-content: center; /* Center the combined SMS rates */
                margin-top: 10px;
                padding-top: 8px;
                border-top: 1px dashed #525CEB; /* Separator for SMS rates */
            }
            /* Corrected styling for transaction percentages */
            .sms-rate-combined {
                font-size: 1.2em; /* Adjusted size for clarity */
                font-weight: bolder; /* Made bolder */
            }
            .sms-rate-accepted {
                color: green; /* Green for accepted part */
            }
            .sms-rate-refused {
                color: red; /* Red for refused part */
            }
            .sms-rate-error {
                color: black; /* Black for error part */
            }


            /* ==== Selectbox ==== */
            .stSelectbox div[data-baseweb="select"] {
                border-radius: 8px;
                border: 2px solid #525CEB; /* Accent Blue/Purple */
                padding: 6px;
                box-shadow: inset 1px 1px 3px rgba(0,0,0,0.2);
            }
            .stSelectbox div[data-baseweb="select"] > div:first-child {
                background-color: #BFCFE7; /* Lighter Accent/Text for selectbox background */
                color: #3D3B40; /* Primary Dark Blue for text */
                font-weight: bold;
            }
            .stSelectbox div[data-baseweb="popover"] div[role="listbox"] {
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            .stSelectbox div[data-baseweb="menu"] {
                background-color: #3D3B40; /* Primary Dark Blue for dropdown menu background */
            }
            .stSelectbox div[data-baseweb="menu"] li {
                color: #FFFFFF; /* Blanc pur for menu items text */
                font-size: 1em;
            }
            .stSelectbox div[data-baseweb="menu"] li:hover {
                background-color: #525CEB; /* Accent Blue/Purple for hover */
                color: #FFFFFF; /* Blanc pur for text on hover */
            }

            /* ==== Button Styling ==== */
            .stButton button {
                background-color: #BFCFE7; /* Lighter Accent/Text for button background */
                color: #3D3B40; /* Primary Dark Blue for button text */
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 1em;
                transition: all 0.2s ease;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.15);
                cursor: pointer;
            }

            .stButton button:hover {
                background-color: #525CEB; /* Accent Blue/Purple for hover */
                color: #FFFFFF; /* Blanc pur pour le texte au survol */
                box-shadow: 3px 3px 12px rgba(0,0,0,0.25);
            }

            .stButton button:active,
            .stButton button:focus:not(:active) {
                background-color: #3D3B40; /* Primary Dark Blue for active/focus */
                color: #BFCFE7; /* Lighter Accent/Text for text */
                box-shadow: inset 2px 2px 6px rgba(0,0,0,0.2);
            }

            /* ==== DataFrame ==== */
            .stDataFrame {
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
            }
            .stDataFrame table {
                border-collapse: collapse;
                width: 100%;
            }
            .stDataFrame thead th {
                background-color: #3D3B40; /* Primary Dark Blue for header */
                color: #BFCFE7; /* Lighter Accent/Text for header text */
                padding: 12px;
                text-align: left;
                font-weight: bold;
            }
            .stDataFrame tbody tr:nth-child(odd) {
                background-color: #FFFFFF; /* Blanc pur pour les lignes impaires */
            }
            .stDataFrame tbody tr:hover {
                background-color: #525CEB; /* Accent Blue/Purple on hover */
                color: #FFFFFF; /* Blanc pur pour le texte au survol */
            }
            .stDataFrame tbody td {
                padding: 10px 12px;
                border-bottom: 1px solid #525CEB; /* Accent Blue/Purple */
                color: #3D3B40; /* Primary Dark Blue for text */
            }

            /* ==== Sidebar & Menu ==== */
            div[data-testid="stSidebar"] {
                background-color: #BFCFE7 !important; /* Lighter Accent/Text for sidebar background */
                color: #3D3B40 !important; /* Primary Dark Blue for sidebar text */
            }
            .css-1cypcdb, .css-1lcbmhc { /* Streamlit menu/option container */
                background-color: #BFCFE7 !important; /* Lighter Accent/Text */
                border: none;
            }
            .css-1cypcdb button, .css-1lcbmhc button { /* Streamlit menu/option buttons */
                color: #3D3B40 !important; /* Primary Dark Blue */
                background-color: transparent !important;
                font-weight: bold;
                padding: 10px 16px;
                margin-right: 8px;
                border-radius: 6px;
                transition: all 0.2s ease-in-out;
            }
            .css-1cypcdb button:hover, .css-1lcbmhc button:hover {
                background-color: #525CEB !important; /* Accent Blue/Purple */
                color: #FFFFFF !important; /* Blanc pur - text */
            }
            .css-1cypcdb button[data-selected="true"], .css-1lcbmhc button[data-selected="true"] {
                background-color: #3D3B40 !important; /* Primary Dark Blue - background */
                color: #BFCFE7 !important; /* Lighter Accent/Text - text */
            }

            /* ==== Date Input (Date Picker) ==== */
            .stDateInput div[data-baseweb="input"] {
                background-color: #BFCFE7; /* Lighter Accent/Text */
                color: #3D3B40; /* Primary Dark Blue for text */
                border: 2px solid #525CEB; /* Accent Blue/Purple */
                border-radius: 8px;
                padding: 6px;
            }
            .stDateInput div[data-baseweb="input"] input {
                background-color: #BFCFE7; /* Lighter Accent/Text */
                color: #3D3B40; /* Primary Dark Blue for input text */
                font-weight: bold;
            }
            /* Calendar/Picker styling */
            .stDateInput div[data-baseweb="calendar"] {
                background-color: #FFFFFF; /* Fond blanc pur pour le calendrier */
                border: 1px solid #525CEB; /* Accent Blue/Purple border */
                color: #3D3B40; /* Primary Dark Blue for calendar text */
                border-radius: 8px;
            }
            .stDateInput div[data-baseweb="calendar"] .DayPicker_weekdays {
                color: #525CEB; /* Accent Blue/Purple for weekday headers */
            }
            .stDateInput div[data-baseweb="calendar"] .DayPicker_day {
                color: #3D3B40; /* Primary Dark Blue for days */
            }
            .stDateInput div[data-baseweb="calendar"] .DayPicker_day--selected {
                background-color: #3D3B40 !important; /* Primary Dark Blue for selected day */
                color: #BFCFE7 !important; /* Lighter Accent/Text for selected day text */
            }
            .stDateInput div[data-baseweb="calendar"] .DayPicker_day--hovered {
                background-color: #525CEB !important; /* Accent Blue/Purple for hovered day */
                color: #FFFFFF !important; /* Blanc pur pour le texte au survol */
            }
            .stDateInput .flatpickr-calendar { /* Older Streamlit versions might use flatpickr */
                background-color: #FFFFFF !important;
                border: 1px solid #525CEB !important;
            }
            .stDateInput .flatpickr-day {
                color: #3D3B40 !important;
            }
            .stDateInput .flatpickr-day.selected, .stDateInput .flatpickr-day.startRange, .stDateInput .flatpickr-day.endRange {
                background-color: #3D3B40 !important;
                color: #BFCFE7 !important;
            }
            .stDateInput .flatpickr-day.today:not(.selected) {
                border-color: #525CEB !important;
            }
            .stDateInput .flatpickr-day.hover {
                background-color: #525CEB !important;
                color: #FFFFFF !important;
            }
        </style>
    """, unsafe_allow_html=True)

def get_db_connection():
    # Accédez aux secrets via st.secrets
    try:
        db_path = st.secrets["database"]["path"]
        password = st.secrets["database"]["password"]
    except KeyError as e:
        st.error(f"Erreur de configuration des secrets : {e}. Assurez-vous que 'path' et 'password' sont définis dans [database] dans secrets.toml.")
        return None

    try:
        conn = sqlite3.connect(db_path)
        # Si vous utilisez SQLCipher (et non sqlite3 standard), cette ligne est valide.
        # Sinon, pour sqlite3 standard, elle n'aura aucun effet de chiffrement.
        if password: # S'assurer que le mot de passe n'est pas vide
             conn.execute(f"PRAGMA key='{password}'")
        
        # Exemple de configuration supplémentaire (comme le mode de row_factory)
        conn.row_factory = sqlite3.Row # Accéder aux colonnes par leur nom
        
        return conn
    except sqlite3.Error as e: # Capturez les erreurs spécifiques à sqlite3
        st.error(f"Erreur de connexion à la base de données : {e}")
        return None
    except Exception as e: # Capturez d'autres erreurs inattendues
        st.error(f"Une erreur inattendue est survenue lors de la connexion : {e}")
        return None

def authenticate(username, password):
    """Authentifie l'utilisateur."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                "SELECT u.Hyp, e.Type, e.Date_In FROM Users u "
                "JOIN Effectifs e ON u.Hyp = e.Hyp "
                "WHERE u.UserName = ? AND u.PassWord = ?", 
                (username, password))
            result = cursor.fetchone()
            return result if result else None
    except Exception as e:
        st.error(f"Erreur d'authentification : {e}")
        return None
    finally:
        conn.close()

def get_user_details(hyp):
    """Récupère les détails d'un utilisateur."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT e.Nom, e.Prenom, e.Date_In, e.Team, e.Type, e.Activité, u.UserName, u.Cnx
                FROM Effectifs e
                JOIN Users u ON e.Hyp = u.Hyp
                WHERE u.Hyp = ?""", (hyp,))
            result = cursor.fetchone()
            return result if result else None
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données utilisateur: {e}")
        return None
    finally:
        conn.close()

def reset_password(hyp):
    """Réinitialise le mot de passe d'un utilisateur."""
    conn = get_db_connection()
    if not conn:
        return False
   
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                UPDATE Users
                SET PassWord = ?
                WHERE Hyp = ?
            """, (hyp, hyp))
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Erreur lors de la réinitialisation du mot de passe : {e}")
        return False
    finally:
        conn.close()

def login_page():
    """Affiche la page de connexion."""
    col1, col2, col3, col4 = st.columns([1,1,2,1])
    with col2:
        st.image('Dental_Implant.png', width=380)
    with col3:
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        col1, col2 = st.columns([1,5])
        with col1:
            if st.button("**Se connecter**", key="login_button"):
                user_data = authenticate(username, password)
                if user_data:
                    st.session_state.update({
                        "authenticated": True,
                        "hyp": user_data[0],
                        "user_type": user_data[1],
                        "date_in": user_data[2],
                        "username": username
                    })
                    st.success("Authentification réussie")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects")
        with col2:
            if st.button("**Annuler**", key="Annuler_button"):
                st.experimental_rerun()

def load_data():
    """Chargement des données depuis SQLite."""
    try:
        conn = get_db_connection()
        if not conn:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT Hyp, ORDER_REFERENCE, ORDER_DATE, SHORT_MESSAGE, Country, Latitude, Longitude, City, Total_Sale, Rating, Id_Sale 
                FROM Sales
                WHERE SHORT_MESSAGE <> 'ERROR'
            """)
            sales_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

            cursor.execute("""
                SELECT Hyp, ORDER_REFERENCE, ORDER_DATE, SHORT_MESSAGE, Country, Latitude, Longitude, City, Rating, Total_Recolt, Banques, Id_Recolt 
                FROM Recolt
                WHERE SHORT_MESSAGE <> 'ERROR'
            """)
            recolts_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
            
            cursor.execute("""
                SELECT Hyp, BP_Logs, Sous_motif, Canal, Direction, Date_d_création,
                       Qualification, Heure_création, Offre, Date_anciennete_client, Segment,
                       Statut_BP, Mode_facturation, Anciennete_client, Id_Log 
                FROM Logs
                WHERE Offre <> 'AB'
            """)
            logs_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

            cursor.execute("""
                SELECT Hyp, Team, Activité, Date_In, NOM, PRENOM, Type 
                FROM Effectifs
                WHERE Type = 'Agent'
            """)
            staff_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

        return sales_df, recolts_df, staff_df, logs_df
    except Exception as e:
        st.error(f"Erreur de chargement des données: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    finally:
        if conn:
            conn.close()

def preprocess_data(df):
    """Prétraite les données."""
    if 'ORDER_DATE' in df.columns:
        df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'], errors='coerce')
    if 'Total_Sale' in df.columns:
        df['Total_Sale'] = pd.to_numeric(df['Total_Sale'], errors='coerce').fillna(0)
    if 'Total_Recolt' in df.columns:
        df['Total_Recolt'] = pd.to_numeric(df['Total_Recolt'], errors='coerce').fillna(0)
    if 'Date_d_création' in df.columns:
        df['Date_d_création'] = pd.to_datetime(df['Date_d_création'], errors='coerce')
    if 'Date_In' in df.columns:
        df['Date_In'] = pd.to_datetime(df['Date_In'], errors='coerce')
    return df

def geocode_data(df):
    """Géocode les villes pour obtenir les coordonnées GPS."""
    if 'Latitude' in df.columns and 'Longitude' in df.columns and not df[['Latitude', 'Longitude']].isnull().all().all():
        return df

    geolocator = Nominatim(user_agent="sales_dashboard", timeout=10)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    locations = []
    unique_locations = df[['City', 'Country']].dropna().drop_duplicates()

    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        existing_coords = df[['City', 'Country', 'Latitude', 'Longitude']].dropna().drop_duplicates()
        unique_locations = unique_locations.merge(existing_coords, on=['City', 'Country'], how='left')

    for _, row in unique_locations.iterrows():
        if pd.isna(row.get('Latitude')) or pd.isna(row.get('Longitude')):
            try:
                location = geocode(f"{row['City']}, {row['Country']}")
                if location:
                    locations.append({
                        'City': row['City'],
                        'Country': row['Country'],
                        'Latitude': location.latitude,
                        'Longitude': location.longitude
                    })
            except Exception as e:
                st.warning(f"Erreur de géocodage pour {row['City']}, {row['Country']}: {str(e)}")
                continue
        else:
            locations.append({
                'City': row['City'],
                'Country': row['Country'],
                'Latitude': row['Latitude'],
                'Longitude': row['Longitude']
            })

    if locations:
        locations_df = pd.DataFrame(locations)
        df = pd.merge(df.drop(columns=['Latitude', 'Longitude'], errors='ignore'), locations_df, on=['City', 'Country'], how='left')
    return df


def filter_data(df, country, team, activity, transaction_filter, start_date, end_date, staff_df):
    
    filtered_df = df.copy()
    
    date_column = 'ORDER_DATE' if 'ORDER_DATE' in filtered_df.columns else 'Date_d_création'
    
    if date_column in filtered_df.columns:
        filtered_df[date_column] = pd.to_datetime(filtered_df[date_column], errors='coerce')
        filtered_df = filtered_df[
            (filtered_df[date_column].dt.date >= start_date) & 
            (filtered_df[date_column].dt.date <= end_date)
        ]

    if country != 'Tous' and 'Country' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Country'] == country]


    if 'Team' not in filtered_df.columns and 'Hyp' in filtered_df.columns and 'Hyp' in staff_df.columns:

        filtered_df = filtered_df.merge(staff_df[['Hyp', 'Team', 'Activité']].drop_duplicates(), on='Hyp', how='left')
    
    if team != 'Toutes' and 'Team' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Team'] == team]

    if activity != 'Toutes' and 'Activité' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Activité'] == activity]
    

    if transaction_filter != 'Toutes' and 'SHORT_MESSAGE' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['SHORT_MESSAGE'] == transaction_filter]
            
    return filtered_df


def logs_page(logs_df, staff_df, start_date, end_date):
    """Affiche la page des logs avec les filtres spécifiés et un style homogène."""
    

    st.markdown("<h3 style='color: #007bad;'>Filtrage des Logs</h3>", unsafe_allow_html=True)

    with st.container(border=True): 
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            offre_filter = st.selectbox("Filtrer par Offre", ['Tous'] + sorted(logs_df['Offre'].dropna().unique().tolist()) if 'Offre' in logs_df.columns else ['Tous'], key='logs_offre_top')
        with col2:
            team_filter = st.selectbox("Sélectionner équipe", ['Toutes'] + sorted(staff_df['Team'].dropna().unique().tolist()), key='logs_team')
        with col3:
            activity_filter = st.selectbox("Sélectionner activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique().tolist()), key='logs_activity')
        with col4:
            segment_filter = st.selectbox("Segment", ['Tous'] + sorted(logs_df['Segment'].dropna().unique().tolist()) if 'Segment' in logs_df.columns else ['Tous'], key='segment_filter')

        col5, col6, col7, col8 = st.columns(4)
        with col5:
            statut_bp_filter = st.selectbox("Statut BP", ['Tous'] + sorted(logs_df['Statut_BP'].dropna().unique().tolist()) if 'Statut_BP' in logs_df.columns else ['Tous'], key='statut_bp_filter')
        with col6:
            canal_filter = st.selectbox("Canal", ['Tous'] + sorted(logs_df['Canal'].dropna().unique().tolist()) if 'Canal' in logs_df.columns else ['Tous'], key='canal_filter')
        with col7:
            direction_filter = st.selectbox("Direction", ['Tous'] + sorted(logs_df['Direction'].dropna().unique().tolist()) if 'Direction' in logs_df.columns else ['Tous'], key='direction_filter')
        with col8:
            qualification_filter = st.selectbox("Qualification", ['Tous'] + sorted(logs_df['Qualification'].dropna().unique().tolist()) if 'Qualification' in logs_df.columns else ['Tous'], key='qualification_filter')

    
    with st.spinner("Application des filtres..."):
        # Pass 'Tous' for country_filter and transaction_filter, and staff_df
        filtered_logs = filter_data(logs_df, 'Tous', team_filter, activity_filter, 'Toutes', start_date, end_date, staff_df)

        
        if offre_filter != 'Tous' and 'Offre' in filtered_logs.columns:
            filtered_logs = filtered_logs[filtered_logs['Offre'] == offre_filter]
        if segment_filter != 'Tous' and 'Segment' in filtered_logs.columns:
            filtered_logs = filtered_logs[filtered_logs['Segment'] == segment_filter]
        if statut_bp_filter != 'Tous' and 'Statut_BP' in filtered_logs.columns:
            filtered_logs = filtered_logs[filtered_logs['Statut_BP'] == statut_bp_filter]
        if canal_filter != 'Tous' and 'Canal' in filtered_logs.columns:
            filtered_logs = filtered_logs[filtered_logs['Canal'] == canal_filter]
        if direction_filter != 'Tous' and 'Direction' in filtered_logs.columns:
            filtered_logs = filtered_logs[filtered_logs['Direction'] == direction_filter]
        if qualification_filter != 'Tous' and 'Qualification' in filtered_logs.columns:
            filtered_logs = filtered_logs[filtered_logs['Qualification'] == qualification_filter]

    if not filtered_logs.empty:
        st.markdown("<h3 style='color: #007bad;'>Indicateurs Clés des Logs</h3>", unsafe_allow_html=True)

    
        total_logs_count = len(filtered_logs)
        total_unique_offres_count = filtered_logs['Offre'].nunique() if 'Offre' in filtered_logs.columns else 0
        
    
        if 'Direction' in filtered_logs.columns:
            incoming = len(filtered_logs[filtered_logs['Direction'] == 'InComming'])
            outgoing = len(filtered_logs[filtered_logs['Direction'] == 'OutComming'])
            conversion_rate = (outgoing / incoming * 100) if incoming > 0 else 0 
        else:
            conversion_rate = "N/A"
        
        
    
        if 'Statut_BP' in filtered_logs.columns:
            actif = len(filtered_logs[filtered_logs['Statut_BP'] == 'actif'])
            resilie = len(filtered_logs[filtered_logs['Statut_BP'] == 'résilié'])

            total_relevant_logs = actif + resilie


            if total_relevant_logs > 0:
                
                bp_rate = (resilie / total_relevant_logs * 100) 
            else:
                bp_rate = 0 
        else:
            bp_rate = "N/A"

    
        if 'Date_d_création' in filtered_logs.columns:
            filtered_logs['Date_d_création'] = pd.to_datetime(filtered_logs['Date_d_création'], errors='coerce')
            min_date = filtered_logs['Date_d_création'].min()
            max_date = filtered_logs['Date_d_création'].max()
            days = (max_date - min_date).days if pd.notna(min_date) and pd.notna(max_date) else "N/A"
        else:
            days = "N/A"

    
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="margin-top: 20px;">
                <div class="metric-title">Total Logs</div>
                <div class="metric-value">{total_logs_count:,}</div>
            </div>
            """.replace(",", " "), unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card" style="margin-top: 20px;">
                <div class="metric-title">Offres Vendus</div>
                <div class="metric-value">{total_unique_offres_count:,}</div>
            </div>
            """.replace(",", " "), unsafe_allow_html=True)

        with col3:
            conversion_display = f"{conversion_rate:.1f}%" if isinstance(conversion_rate, (int, float)) else conversion_rate
            st.markdown(f"""
            <div class="metric-card" style="margin-top: 20px;">
                <div class="metric-title">Taux de Conversion</div>
                <div class="metric-value">{conversion_display}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            bp_display = f"{bp_rate:.1f}%" if isinstance(bp_rate, (int, float)) else bp_rate
            st.markdown(f"""
            <div class="metric-card" style="margin-top: 20px;">
                <div class="metric-title">Taux Statut BP</div>
                <div class="metric-value">{bp_display}</div>
            </div>
            """, unsafe_allow_html=True)
        with col5:
        # Période couverte dans une nouvelle ligne si nécessaire
            if days != "N/A":
                st.markdown(f"""
                <div class="metric-card" style="margin-top: 20px;">
                    <div class="metric-title">Période Couverte</div>
                    <div class="metric-value">{days} jours</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<h3 style='color: #007bad;'>Répartition des Logs</h3>", unsafe_allow_html=True)

        with st.container(border=True):
            col1, col2, col3 = st.columns(3)

            # Graphique 1: Répartition par Canal
            with col1:
                st.markdown("<h3 style='color: #007bad;'>Logs par Canal</h3>", unsafe_allow_html=True)
                if 'Canal' in filtered_logs.columns and not filtered_logs.empty:
                    canal_counts = filtered_logs['Canal'].value_counts().reset_index()
                    canal_counts.columns = ['Canal', 'Count']
                    
                    fig1 = px.bar(
                        canal_counts,
                        x='Count',
                        y='Canal',
                        orientation='h',
                        color='Canal',
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        text='Count'
                    )
                    fig1.update_traces(
                        textposition='auto',
                        textfont=dict(size=16, color='black', family='Arial')
                    )
                    fig1.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        showlegend=False,
                        xaxis=dict(
                            title="",
                            tickfont=dict(size=16, family='Arial', color='black')
                        ),
                        yaxis=dict(
                            title="",
                            tickfont=dict(size=16, family='Arial', color='black')
                        ),
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.warning("Données non disponibles pour ce graphique")

            # Graphique 2: Volume de Logs par Jour
            with col2:
                st.markdown("<h3 style='color: #007bad;'>Logs par Jours</h3>", unsafe_allow_html=True)
                if 'Date_d_création' in filtered_logs.columns and not filtered_logs.empty:
                    filtered_logs['Day_of_Week'] = filtered_logs['Date_d_création'].dt.day_name(locale='fr_FR')
                    day_order = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

                    daily_logs_by_day = filtered_logs['Day_of_Week'].value_counts().reindex(day_order, fill_value=0).reset_index()
                    daily_logs_by_day.columns = ['Day_of_Week', 'Count']

                    fig2 = px.line(
                        daily_logs_by_day,
                        x='Day_of_Week',
                        y='Count',
                        line_shape='spline',
                        color_discrete_sequence=['#007bad'],
                        category_orders={"Day_of_Week": day_order},
                        text='Count'
                    )
                    fig2.update_traces(
                        mode='lines+markers+text',
                        textposition='top center',
                        textfont=dict(size=16, color='black', family='Arial'),
                        line=dict(width=3),
                        marker=dict(size=10, color='#007bad')
                    )
                    fig2.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        xaxis=dict(
                            title="",
                            tickfont=dict(size=16, family='Arial', color='black')
                        ),
                        yaxis=dict(
                            title="",
                            tickfont=dict(size=16, family='Arial', color='black')
                        ),
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("Données non disponibles pour ce graphique")

            # Graphique 3: Répartition par Offre
            with col3:
                st.markdown("<h3 style='color: #007bad;'>Logs par Offre</h3>", unsafe_allow_html=True)
                if 'Offre' in filtered_logs.columns and not filtered_logs.empty:
                    offre_counts = filtered_logs['Offre'].value_counts().reset_index()
                    offre_counts.columns = ['Offre', 'Count']
                    
                    fig3 = px.bar(
                        offre_counts,
                        x='Count',
                        y='Offre',
                        orientation='h',
                        color='Offre',
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        text='Count'
                    )
                    fig3.update_traces(
                        textposition='auto',
                        textfont=dict(size=16, color='black', family='Arial')
                    )
                    fig3.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        showlegend=False,
                        xaxis=dict(
                            title="",
                            tickfont=dict(size=16, family='Arial', color='black')
                        ),
                        yaxis=dict(
                            title="",
                            tickfont=dict(size=16, family='Arial', color='black')
                        ),
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.warning("Données non disponibles pour ce graphique")

        st.markdown("<h3 style='color: #007bad;'>Données Détaillées des Logs</h3>", unsafe_allow_html=True)

        display_df = filtered_logs.sort_values('Date_d_création', ascending=False).copy()

        # Supprimer les colonnes spécifiées si elles existent
        columns_to_drop = ['Id_Log', 'Day_of_Week'] 
        display_df = display_df.drop(columns=[col for col in columns_to_drop if col in display_df.columns], errors='ignore')

        column_configs = {
            "Date_d_création": st.column_config.DatetimeColumn(
                "Date de Création",
                format="DD/MM/YYYY HH:mm",
                width="medium",
            ),
            "Canal": st.column_config.Column("Canal", width="small"),
            "Offre": st.column_config.Column("Offre", width="medium"),
            "Statut_BP": st.column_config.Column("Statut BP", width="medium"),
            "Direction": st.column_config.Column("Direction", width="medium"),
            "Qualification": st.column_config.Column("Qualification", width="medium"),
            "Segment": st.column_config.Column("Segment", width="small"),
        }

        existing_columns_configs = {col: config for col, config in column_configs.items() if col in display_df.columns}

        st.dataframe(
            display_df,
            column_config=existing_columns_configs,
            hide_index=True,
            use_container_width=True,
            height=400,
        )
        st.markdown("""
        <style>
        .stDataFrame td {
            text-align: center;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

    else:
        st.warning("Aucune donnée disponible avec les filtres sélectionnés. Veuillez ajuster vos sélections.")

def sales_page(sales_df, staff_df, start_date, end_date):
    """Affiche la page des ventes avec le nouveau style."""

    add_custom_css() # Appel de la fonction CSS personnalisée

    st.markdown("<h3 style='color: #007bad;'>Filtrage des Ventes</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        with col1:
            country_filter = st.selectbox("Filtrer par Pays", ['Tous'] + sorted(sales_df['Country'].dropna().unique()), key='sales_country')
        with col2:
            team_filter = st.selectbox("Sélectionner équipe", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()), key='sales_team')
        with col3:
            activity_filter = st.selectbox("Sélectionner activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()), key='sales_activity')
        with col4:
            transaction_filter = st.selectbox("Type de transaction", ['Toutes'] + sorted(sales_df['SHORT_MESSAGE'].dropna().unique()), key='sales_transaction')

        # Assurez-vous de passer transaction_filter ici
        filtered_sales = filter_data(sales_df, country_filter, team_filter, activity_filter, transaction_filter, start_date, end_date, staff_df)

    if not filtered_sales.empty:
        # Geocode data for map after filtering to ensure map reflects filters
        if 'City' in filtered_sales.columns and 'Country' in filtered_sales.columns:
            filtered_sales = geocode_data(filtered_sales)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Sales</div>
                <div class="metric-value">{filtered_sales['Total_Sale'].sum():,.0f}€</div>
            </div>
            """.replace(",", " "), unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Average Sale</div>
                <div class="metric-value">{filtered_sales['Total_Sale'].mean():,.2f}€</div>
            </div>
            """.replace(",", " "), unsafe_allow_html=True)

        with col3:
            if 'Rating' in filtered_sales.columns:
                avg_rating = filtered_sales['Rating'].mean()
                rating_display = f"{'★' * int(round(avg_rating))}{'☆' * (7 - int(round(avg_rating)))}"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Average Rating</div>
                    <div class="metric-value">{rating_display}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-title">Average Rating</div>
                    <div class="metric-value">N/A</div>
                </div>
                """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Transactions</div>
                <div class="metric-value">{len(filtered_sales):,}</div>
            </div>
            """.replace(",", " "), unsafe_allow_html=True)


        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("<h3 style='color: #007bad;'>Ventes par Ville (Vue Carte)</h3>", unsafe_allow_html=True)
            if 'Latitude' in filtered_sales.columns and 'Longitude' in filtered_sales.columns:
                city_sales_map = filtered_sales.groupby('City').agg(
                    Total_Sale=('Total_Sale', 'sum'),
                    Latitude=('Latitude', 'first'),
                    Longitude=('Longitude', 'first'),
                    Accepted_SMS=('SHORT_MESSAGE', lambda x: (x == 'ACCEPTED').sum()),
                    Refused_SMS=('SHORT_MESSAGE', lambda x: (x == 'REFUSED').sum()),
                    Error_SMS=('SHORT_MESSAGE', lambda x: (x == 'ERROR').sum()) # Added for ERROR count
                ).reset_index()

                city_sales_map = city_sales_map.dropna(subset=['Latitude', 'Longitude'])

                if not city_sales_map.empty:
                    city_sales_map['Formatted_Sale'] = city_sales_map['Total_Sale'].apply(lambda x: f"{x:,.0f}€")
                    city_sales_map['Short_Sale'] = city_sales_map['Total_Sale'].apply(lambda x: f"{x/1000:.0f}k" if x >= 1000 else f"{x:.0f}")

                    # Adjusted for combined total for percentage calculation
                    city_sales_map['Total_SMS'] = city_sales_map['Accepted_SMS'] + city_sales_map['Refused_SMS'] + city_sales_map['Error_SMS']

                    city_sales_map['Refused_SMS_Percentage'] = city_sales_map.apply(
                        lambda row: (row['Refused_SMS'] / row['Total_SMS']) * 100 if row['Total_SMS'] > 0 else 0,
                        axis=1
                    ).round(2)
                    # New: Error SMS Percentage
                    city_sales_map['Error_SMS_Percentage'] = city_sales_map.apply(
                        lambda row: (row['Error_SMS'] / row['Total_SMS']) * 100 if row['Total_SMS'] > 0 else 0,
                        axis=1
                    ).round(2)

                    fig_map = px.scatter_mapbox(
                        city_sales_map,
                        lat="Latitude",
                        lon="Longitude",
                        size="Total_Sale",
                        text="Short_Sale",  # Ajout du texte à afficher sur les cercles
                        color_discrete_sequence=['blue'] * len(city_sales_map),
                        hover_name="City",
                        hover_data={
                            "Formatted_Sale": True,
                            "Latitude": False,
                            "Longitude": False,
                            "Refused_SMS_Percentage": ":.2f",
                            "Error_SMS_Percentage": ":.2f", # Added for hover data
                            "Total_Sale": False,
                            "Accepted_SMS": False,
                            "Refused_SMS": False,
                            "Error_SMS": False, # Exclude raw count from hover
                            "Short_Sale": False # Ne pas afficher dans le tooltip
                        },
                        size_max=35,
                        zoom=5,
                        mapbox_style="carto-positron"
                    )

                    fig_map.update_traces(
                        textfont=dict(
                            family="Arial",
                            size=12,
                            color="white"
                        ),
                        textposition="middle center",
                        hovertemplate="<b>%{hover_name}</b><br>" + # Use hover_name directly
                                      "Ventes: %{customdata[0]}<br>" +
                                      "Transactions Refusées: %{customdata[1]:.2f}%<br>" +
                                      "Transactions Erreur: %{customdata[2]:.2f}%" + # Added to hover template
                                      "<extra></extra>",
                        customdata=city_sales_map[['Formatted_Sale', 'Refused_SMS_Percentage', 'Error_SMS_Percentage', 'City']]
                    )

                    fig_map.update_layout(
                        height=600,
                        margin={"r":0,"t":40,"l":0,"b":0},
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=14,
                            font_family="Arial"
                        )
                    )
                    st.plotly_chart(fig_map, use_container_width=True)
                else:
                    st.warning("Aucune donnée de vente avec des coordonnées géographiques valides pour afficher sur la carte.")
            else:
                st.warning("Les colonnes 'Latitude' ou 'Longitude' sont manquantes ou vides dans les données de vente.")

        with col2:
            st.markdown("<h3 style='color: #007bad;'>Performance des 3 Top Équipes</h3>", unsafe_allow_html=True)
            st.write("")


            try:
                if 'debug_msg' not in st.session_state:
                    st.session_state.debug_msg = []
                st.session_state.debug_msg = []

                if 'Team' not in filtered_sales.columns:
                    if 'Hyp' in filtered_sales.columns and 'Hyp' in staff_df.columns:
                        initial_sales_rows = len(filtered_sales)
                        filtered_sales = filtered_sales.merge(
                            staff_df[['Hyp', 'Team']].drop_duplicates(),
                            on='Hyp',
                            how='left'
                        )
                        st.session_state.debug_msg.append(f"Taille de filtered_sales après jointure: {len(filtered_sales)}")

                        teams_found = filtered_sales['Team'].notna().sum()
                        if teams_found == 0 and initial_sales_rows > 0:
                            st.warning("Aucune correspondance 'Hyp' trouvée entre les ventes filtrées et les données du personnel. Assurez-vous que les valeurs 'Hyp' sont cohérentes.")
                            st.session_state.debug_msg.append(f"Valeurs uniques de 'Hyp' dans filtered_sales: {filtered_sales['Hyp'].dropna().unique().tolist()[:5]}...")
                            st.session_state.debug_msg.append(f"Valeurs uniques de 'Hyp' dans staff_df: {staff_df['Hyp'].dropna().unique().tolist()[:5]}...")
                    else:
                        st.error("Les colonnes 'Hyp' sont manquantes dans les données de vente ou du personnel, impossibilité de joindre les équipes.")
                        st.session_state.debug_msg.append(f"Colonnes filtered_sales: {filtered_sales.columns.tolist()}")
                        st.session_state.debug_msg.append(f"Colonnes staff_df: {staff_df.columns.tolist()}")

                if 'Team' in filtered_sales.columns and not filtered_sales['Team'].dropna().empty:
                    team_stats = filtered_sales.groupby('Team').agg(
                        Total_Sale=('Total_Sale', 'sum'),
                        Total_Transactions=('Total_Sale', 'count'), # Nombre de transactions
                        Accepted_SMS=('SHORT_MESSAGE', lambda x: (x == 'ACCEPTED').sum()),
                        Refused_SMS=('SHORT_MESSAGE', lambda x: (x == 'REFUSED').sum()),
                        Error_SMS=('SHORT_MESSAGE', lambda x: (x == 'ERROR').sum()) # Added for ERROR count
                    ).reset_index()

                    if not team_stats.empty:
                        # Calcul des taux d'acceptation, refus et erreur des SMS
                        team_stats['Total_SMS_Transactions'] = team_stats['Accepted_SMS'] + team_stats['Refused_SMS'] + team_stats['Error_SMS']

                        team_stats['Acceptance_Rate'] = team_stats.apply(
                            lambda row: (row['Accepted_SMS'] / row['Total_SMS_Transactions']) * 100
                            if row['Total_SMS_Transactions'] > 0 else 0,
                            axis=1
                        ).round(2)

                        team_stats['Refusal_Rate'] = team_stats.apply(
                            lambda row: (row['Refused_SMS'] / row['Total_SMS_Transactions']) * 100
                            if row['Total_SMS_Transactions'] > 0 else 0,
                            axis=1
                        ).round(2)

                        team_stats['Error_Rate'] = team_stats.apply(
                            lambda row: (row['Error_SMS'] / row['Total_SMS_Transactions']) * 100
                            if row['Total_SMS_Transactions'] > 0 else 0,
                            axis=1
                        ).round(2)

                        # Calcul du taux de conversion (Total Sale de l'équipe / Total Sale global filtré)
                        total_sales_global = filtered_sales['Total_Sale'].sum()
                        team_stats['Conversion_Rate'] = team_stats['Total_Sale'].apply(
                            lambda x: (x / total_sales_global) * 100 if total_sales_global > 0 else 0
                        ).round(2)

                        team_stats = team_stats.sort_values(by='Total_Sale', ascending=False)

                        # Affichage des cartes de performance d'équipe
                        for index, row in team_stats.iterrows():
                            st.markdown(f"""
                            <div class="team-performance-card">
                                <div class="team-performance-title">{row['Team']}</div>
                                <div class="team-stat-row">
                                    <div>
                                        <div class="team-stat-label">Ventes Totales:</div>
                                        <div class="team-stat-value">{row['Total_Sale']:,.0f}€</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div class="team-stat-label">Taux Conversion:</div>
                                        <div class="team-conversion-value">{row['Conversion_Rate']:.2f}%</div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div class="team-stat-label">Transactions:</div>
                                        <div class="team-stat-value">{row['Total_Transactions']:,}</div>
                                    </div>
                                </div>
                                <div style="display: flex; justify-content: space-around; margin-top: 10px; flex-wrap: wrap;">
                                    <div style="text-align: center; margin-right: 10px;">
                                        <span class="sms-rate-label">Accepté: </span><span class="sms-accepted-value">{row['Acceptance_Rate']:.2f}%</span>
                                    </div>
                                    <div style="text-align: center; margin-left: 10px;">
                                        <span class="sms-rate-label">Refusé: </span><span class="sms-refused-value">{row['Refusal_Rate']:.2f}%</span>
                                    </div>
                                    <div style="text-align: center;">
                                        <span class="sms-rate-label">Erreur: </span><span class="sms-error-value">{row['Error_Rate']:.2f}%</span>
                                    </div>
                                </div>
                            </div>
                            """.replace(",", " "), unsafe_allow_html=True)
                    else:
                        st.info("Aucune statistique d'équipe à afficher pour la sélection actuelle.")
                else:
                    st.warning("Impossible d'afficher les performances des équipes. Vérifiez que la colonne 'Team' est disponible après le filtrage ou que les données 'Hyp' permettent la jointure.")
                    with st.expander("Détails du problème"):
                        st.write("Informations de debug:")
                        for msg in st.session_state.debug_msg:
                            st.write(msg)
            except Exception as e:
                st.error(f"Une erreur inattendue est survenue lors du calcul des performances d'équipe : {str(e)}")
                with st.expander("Détails de l'erreur"):
                    st.write("Informations de debug:")
                    for msg in st.session_state.debug_msg:
                        st.write(msg)
                    import traceback
                    st.code(traceback.format_exc())


        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.markdown("<h3 style='color: #007bad;'>Ventes par Jour de la Semaine</h3>", unsafe_allow_html=True)
            filtered_sales['Weekday'] = filtered_sales['ORDER_DATE'].dt.weekday
            ventes_jour = filtered_sales.groupby('Weekday')['Total_Sale'].sum().reset_index()
            jours = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}
            ventes_jour['Jour'] = ventes_jour['Weekday'].map(jours)
            all_days = pd.DataFrame({'Weekday': range(7)})
            ventes_jour = pd.merge(all_days, ventes_jour, on='Weekday', how='left').fillna(0)
            ventes_jour['Jour'] = ventes_jour['Weekday'].map(jours)
            ventes_jour = ventes_jour.sort_values('Weekday')


            fig_jour = px.line(ventes_jour,
                                x='Jour',
                                y='Total_Sale',
                                line_shape='spline',
                                color_discrete_sequence=['#525CEB'])

            fig_jour.update_traces(
                line=dict(width=4, color='#525CEB'),
                mode='lines+markers+text',
                marker=dict(size=10, color='#3D3B40', line=dict(width=1, color='#FFFFFF')),
                text=[f"€{y:,.0f}" for y in ventes_jour['Total_Sale']],
                textposition="top center",
                textfont=dict(color="#F70F49", size=14, family='Arial', weight='bold'),
                hovertemplate='Jour: %{x}<br>Ventes: €%{y:,.2f}<extra></extra>',
                fill='tozeroy',
                fillcolor='rgba(179, 191, 231, 0.4)'
            )

            fig_jour.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                plot_bgcolor='#FFFFFF',
                paper_bgcolor='#FFFFFF',
                xaxis_gridcolor='#E0E0E0',
                yaxis_gridcolor='#E0E0E0',
                xaxis=dict(
                    tickmode='array',
                    tickvals=ventes_jour['Jour'],
                    categoryorder='array',
                    categoryarray=ventes_jour['Jour'],
                    tickfont=dict(size=14, color='#3D3B40', weight='bold')
                ),
                yaxis=dict(
                    range=[0, ventes_jour['Total_Sale'].max() * 1.2],
                    tickfont=dict(size=12, color='#3D3B40')
                ),
                font=dict(family='Arial', size=12, color='#3D3B40'),
                margin=dict(t=50, b=50, l=50, r=50)
            )

            st.plotly_chart(fig_jour, use_container_width=True)

        with col2:
            st.markdown("<h3 style='color: #007bad;'>Transactions Acceptées vs Refusées</h3>", unsafe_allow_html=True)
            status_sales = filtered_sales.groupby('SHORT_MESSAGE')['Total_Sale'].sum().reset_index()

            fig = px.pie(status_sales,
                                    values='Total_Sale',
                                    names='SHORT_MESSAGE',
                                    color='SHORT_MESSAGE',
                                    color_discrete_map={'ACCEPTED': '#007bad', 'REFUSED': '#ff0000', 'ERROR': '#ffa500'}, # Ajout couleur pour ERROR
                                    hole=0.4)

            fig.update_traces(
                textinfo='value+percent',
                textposition='outside',
                textfont_size=18,
                textfont_color=['#007bad', '#ff0000', '#ffa500'], # Mettre à jour pour ERROR
                marker=dict(line=dict(color='white', width=2)),
                pull=[0.05, 0, 0], # Ajuster si vous voulez tirer d'autres parts
                rotation=-90
            )

            st.plotly_chart(fig, use_container_width=True)

        with col3:
            st.markdown("<h3 style='color: #007bad;'>Ventes par Heure (9h-20h)</h3>", unsafe_allow_html=True)

            ventes_heure = filtered_sales[
                (filtered_sales['ORDER_DATE'].dt.hour >= 9) &
                (filtered_sales['ORDER_DATE'].dt.hour <= 20)
            ].groupby(filtered_sales['ORDER_DATE'].dt.hour)['Total_Sale'].sum().reset_index()

            ventes_heure = ventes_heure.rename(columns={'ORDER_DATE': 'Heure'})
            all_hours = pd.DataFrame({'Heure': range(9, 21)})
            ventes_heure = pd.merge(all_hours, ventes_heure, on='Heure', how='left').fillna(0)
            ventes_heure = ventes_heure.sort_values('Heure')

            fig = px.line(ventes_heure, x='Heure', y='Total_Sale',
                                     line_shape='spline',
                                     color_discrete_sequence=['#525CEB'])

            fig.update_traces(
                line=dict(width=4, color='#525CEB'),
                mode='lines+markers+text',
                marker=dict(size=10, color='#3D3B40', line=dict(width=1, color='#FFFFFF')),
                text=[f"€{y:,.0f}" for y in ventes_heure['Total_Sale']],
                textposition="top center",
                textfont=dict(color="#F50808", size=14, family='Arial', weight='bold'),
                hovertemplate='Heure: %{x}h<br>Ventes: €%{y:,.2f}<extra></extra>',
                fill='tozeroy',
                fillcolor='rgba(179, 191, 231, 0.4)'
            )

            fig.update_layout(
                xaxis_title="Heure de la journée",
                yaxis_title=None,
                plot_bgcolor='#FFFFFF',
                paper_bgcolor='#FFFFFF',
                xaxis_gridcolor='#E0E0E0',
                yaxis_gridcolor='#E0E0E0',
                xaxis=dict(
                    tickmode='linear',
                    dtick=1,
                    range=[8.5, 20.5],
                    tickfont=dict(size=14, color='#3D3B40', weight='bold')
                ),
                yaxis=dict(
                    range=[0, ventes_heure['Total_Sale'].max() * 1.2],
                    tickfont=dict(size=12, color='#3D3B40')
                ),
                font=dict(family='Arial', size=12, color='#3D3B40'),
                margin=dict(t=50, b=50, l=50, r=50)
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Aucune donnée de vente ne correspond aux filtres sélectionnés.")


def recolts_page(recolts_df, staff_df, start_date, end_date):
    """Affiche la page des récoltes avec le nouveau style, incluant les cartes Top 3 et les graphiques de ligne/transaction."""

    add_custom_css()

    st.markdown("<h3 style='color: #007bad;'>Filtrage des Récoltes</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        with col1:
            country_filter = st.selectbox("Filtrer par Pays", ['Tous'] + sorted(recolts_df['Country'].dropna().unique()), key='recolts_country')
        with col2:
            team_filter = st.selectbox("Sélectionner équipe", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()), key='recolts_team')
        with col3:
            activity_filter = st.selectbox("Sélectionner activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()), key='recolts_activity')
        with col4:
            # Ajout du filtre de transactions pour les récoltes
            transaction_filter = st.selectbox("Type de transaction", ['Toutes'] + sorted(recolts_df['SHORT_MESSAGE'].dropna().unique()), key='recolts_transaction')

    with st.spinner("Application des filtres..."):
        # Assurez-vous de passer transaction_filter ici
        filtered_recolts = filter_data(recolts_df, country_filter, team_filter, activity_filter, transaction_filter, start_date, end_date, staff_df)

        if not filtered_recolts.empty:
            # Geocode data for map after filtering to ensure map reflects filters
            if 'City' in filtered_recolts.columns and 'Country' in filtered_recolts.columns:
                filtered_recolts = geocode_data(filtered_recolts)

            # Ensure 'Hyp' (employee ID) column is available for 'Employés Uniques' metric and team performance
            if 'Hyp' not in filtered_recolts.columns:
                # Assuming 'Hyp' is the common column for merging staff_df
                if 'Hyp' in staff_df.columns and 'Hyp' in recolts_df.columns: # Check if 'Hyp' exists in both
                     filtered_recolts = filtered_recolts.merge(
                        staff_df[['Hyp', 'Team']].drop_duplicates(),
                        on='Hyp',
                        how='left'
                    )
                else:
                    st.warning("La colonne 'Hyp' est manquante pour l'association équipe-récolte.")


            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Total Récoltes</div>
                    <div class="metric-value">{filtered_recolts['Total_Recolt'].sum():,.0f}€</div>
                </div>
                """.replace(",", " "), unsafe_allow_html=True)

            with col2:
                if 'Rating' in filtered_recolts.columns:
                    avg_rating = filtered_recolts['Rating'].mean()
                    rating_display = f"{'★' * int(round(avg_rating))}{'☆' * (7 - int(round(avg_rating)))}"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Note Moyenne</div>
                        <div class="metric-value">{rating_display}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-title">Note Moyenne</div>
                        <div class="metric-value">N/A</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col3:
                # Total transactions, regardless of status
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Total Transactions</div>
                    <div class="metric-value">{len(filtered_recolts):,}</div>
                </div>
                """.replace(",", " "), unsafe_allow_html=True)

            with col4:
                unique_employees = filtered_recolts['Hyp'].nunique() if 'Hyp' in filtered_recolts.columns else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Employés Uniques</div>
                    <div class="metric-value">{unique_employees:,}</div>
                </div>
                """.replace(",", " "), unsafe_allow_html=True)

            # --- Map and Top Teams ---
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("<h3 style='color: #007bad;'>Récoltes par Ville (Vue Carte)</h3>", unsafe_allow_html=True)
                if 'Latitude' in filtered_recolts.columns and 'Longitude' in filtered_recolts.columns:
                    city_recolts_map = filtered_recolts.groupby('City').agg(
                        Total_Recolt=('Total_Recolt', 'sum'),
                        Latitude=('Latitude', 'first'),
                        Longitude=('Longitude', 'first'),
                        Accepted_SMS=('SHORT_MESSAGE', lambda x: (x == 'ACCEPTED').sum()),
                        Refused_SMS=('SHORT_MESSAGE', lambda x: (x == 'REFUSED').sum()),
                        Error_SMS=('SHORT_MESSAGE', lambda x: (x == 'ERROR').sum()) # Added for ERROR count
                    ).reset_index()

                    city_recolts_map = city_recolts_map.dropna(subset=['Latitude', 'Longitude'])

                    if not city_recolts_map.empty:
                        city_recolts_map['Formatted_Recolt'] = city_recolts_map['Total_Recolt'].apply(lambda x: f"{x:,.0f}€")
                        city_recolts_map['Short_Recolt'] = city_recolts_map['Total_Recolt'].apply(lambda x: f"{x/1000:.0f}k" if x >= 1000 else f"{x:.0f}")

                        # Adjusted for combined total for percentage calculation
                        city_recolts_map['Total_SMS'] = city_recolts_map['Accepted_SMS'] + city_recolts_map['Refused_SMS'] + city_recolts_map['Error_SMS']

                        city_recolts_map['Refused_SMS_Percentage'] = city_recolts_map.apply(
                            lambda row: (row['Refused_SMS'] / row['Total_SMS']) * 100 if row['Total_SMS'] > 0 else 0,
                            axis=1
                        ).round(2)
                        # New: Error SMS Percentage
                        city_recolts_map['Error_SMS_Percentage'] = city_recolts_map.apply(
                            lambda row: (row['Error_SMS'] / row['Total_SMS']) * 100 if row['Total_SMS'] > 0 else 0,
                            axis=1
                        ).round(2)

                        fig_map = px.scatter_mapbox(
                            city_recolts_map,
                            lat="Latitude",
                            lon="Longitude",
                            size="Total_Recolt",
                            text="Short_Recolt", # Ajout du texte à afficher sur les cercles
                            color_discrete_sequence=['#007bad'] * len(city_recolts_map), # Blue color for consistency
                            hover_name="City",
                            hover_data={
                                "Formatted_Recolt": True,
                                "Latitude": False,
                                "Longitude": False,
                                "Refused_SMS_Percentage": ":.2f",
                                "Error_SMS_Percentage": ":.2f", # Added for hover data
                                "Total_Recolt": False,
                                "Accepted_SMS": False,
                                "Refused_SMS": False,
                                "Error_SMS": False, # Exclude raw count from hover
                                "Short_Recolt": False # Ne pas afficher dans le tooltip
                            },
                            size_max=35,
                            zoom=5,
                            mapbox_style="carto-positron"
                        )

                        fig_map.update_traces(
                            textfont=dict(
                                family="Arial",
                                size=12,
                                color="white"
                            ),
                            textposition="middle center",
                            hovertemplate="<b>%{hover_name}</b><br>" + # Use hover_name directly
                                          "Récoltes: %{customdata[0]}<br>" +
                                          "Transactions Refusées: %{customdata[1]:.2f}%<br>" +
                                          "Transactions Erreur: %{customdata[2]:.2f}%" + # Added to hover template
                                          "<extra></extra>",
                            customdata=city_recolts_map[['Formatted_Recolt', 'Refused_SMS_Percentage', 'Error_SMS_Percentage', 'City']]
                        )

                        fig_map.update_layout(
                            height=600,
                            margin={"r":0,"t":40,"l":0,"b":0},
                            hoverlabel=dict(
                                bgcolor="white",
                                font_size=14,
                                font_family="Arial"
                            )
                        )
                        st.plotly_chart(fig_map, use_container_width=True)
                    else:
                        st.warning("Aucune donnée de récolte avec des coordonnées géographiques valides pour afficher sur la carte.")
                else:
                    st.warning("Les colonnes 'Latitude' ou 'Longitude' sont manquantes ou vides dans les données de récolte.")

            with col2:
                st.markdown("<h3 style='color: #007bad;'>Performance des 3 Top Équipes</h3>", unsafe_allow_html=True)
                try:
                    if 'debug_msg_recolts' not in st.session_state:
                        st.session_state.debug_msg_recolts = []
                    st.session_state.debug_msg_recolts = []

                    if 'Team' not in filtered_recolts.columns:
                        if 'Hyp' in filtered_recolts.columns and 'Hyp' in staff_df.columns:
                            initial_recolts_rows = len(filtered_recolts)
                            filtered_recolts = filtered_recolts.merge(
                                staff_df[['Hyp', 'Team']].drop_duplicates(),
                                on='Hyp',
                                how='left'
                            )
                            st.session_state.debug_msg_recolts.append(f"Taille de filtered_recolts après jointure: {len(filtered_recolts)}")

                            teams_found = filtered_recolts['Team'].notna().sum()
                            if teams_found == 0 and initial_recolts_rows > 0:
                                st.warning("Aucune correspondance 'Hyp' trouvée entre les récoltes filtrées et les données du personnel. Assurez-vous que les valeurs 'Hyp' sont cohérentes.")
                                st.session_state.debug_msg_recolts.append(f"Valeurs uniques de 'Hyp' dans filtered_recolts: {filtered_recolts['Hyp'].dropna().unique().tolist()[:5]}...")
                                st.session_state.debug_msg_recolts.append(f"Valeurs uniques de 'Hyp' dans staff_df: {staff_df['Hyp'].dropna().unique().tolist()[:5]}...")
                        else:
                            st.error("Les colonnes 'Hyp' sont manquantes dans les données de récolte ou du personnel, impossibilité de joindre les équipes.")
                            st.session_state.debug_msg_recolts.append(f"Colonnes filtered_recolts: {filtered_recolts.columns.tolist()}")
                            st.session_state.debug_msg_recolts.append(f"Colonnes staff_df: {staff_df.columns.tolist()}")

                    if 'Team' in filtered_recolts.columns and not filtered_recolts['Team'].dropna().empty:
                        team_stats = filtered_recolts.groupby('Team').agg(
                            Total_Recolt=('Total_Recolt', 'sum'),
                            Total_Transactions=('Total_Recolt', 'count'), # Nombre de transactions
                            Accepted_SMS=('SHORT_MESSAGE', lambda x: (x == 'ACCEPTED').sum()),
                            Refused_SMS=('SHORT_MESSAGE', lambda x: (x == 'REFUSED').sum()),
                            Error_SMS=('SHORT_MESSAGE', lambda x: (x == 'ERROR').sum()) # Added for ERROR count
                        ).reset_index()

                        if not team_stats.empty:
                            # Calcul des taux d'acceptation, refus et erreur des SMS
                            team_stats['Total_SMS_Transactions'] = team_stats['Accepted_SMS'] + team_stats['Refused_SMS'] + team_stats['Error_SMS']

                            team_stats['Acceptance_Rate'] = team_stats.apply(
                                lambda row: (row['Accepted_SMS'] / row['Total_SMS_Transactions']) * 100
                                if row['Total_SMS_Transactions'] > 0 else 0,
                                axis=1
                            ).round(2)

                            team_stats['Refusal_Rate'] = team_stats.apply(
                                lambda row: (row['Refused_SMS'] / row['Total_SMS_Transactions']) * 100
                                if row['Total_SMS_Transactions'] > 0 else 0,
                                axis=1
                            ).round(2)

                            team_stats['Error_Rate'] = team_stats.apply(
                                lambda row: (row['Error_SMS'] / row['Total_SMS_Transactions']) * 100
                                if row['Total_SMS_Transactions'] > 0 else 0,
                                axis=1
                            ).round(2)

                            # Calcul du taux de conversion (Total Recolt de l'équipe / Total Recolt global filtré)
                            total_recolt_global = filtered_recolts['Total_Recolt'].sum()
                            team_stats['Conversion_Rate'] = team_stats['Total_Recolt'].apply(
                                lambda x: (x / total_recolt_global) * 100 if total_recolt_global > 0 else 0
                            ).round(2)

                            team_stats = team_stats.sort_values(by='Total_Recolt', ascending=False).head(3) # Top 3 teams
                            st.write("")



                            # Affichage des cartes de performance d'équipe
                            for index, row in team_stats.iterrows():
                                
                                st.markdown(f"""
                                            
                                <div class="team-performance-card">
                                    <div class="team-performance-title">{row['Team']}</div>
                                    <div class="team-stat-row">
                                        <div>
                                            <div class="team-stat-label">Récoltes Totales:</div>
                                            <div class="team-stat-value">{row['Total_Recolt']:,.0f}€</div>
                                        </div>
                                        <div style="text-align: center;">
                                            <div class="team-stat-label">Taux Conversion:</div>
                                            <div class="team-conversion-value">{row['Conversion_Rate']:.2f}%</div>
                                        </div>
                                        <div style="text-align: right;">
                                            <div class="team-stat-label">Transactions:</div>
                                            <div class="team-stat-value">{row['Total_Transactions']:,}</div>
                                        </div>
                                    </div>
                                    <div style="display: flex; justify-content: space-around; margin-top: 10px; flex-wrap: wrap;">
                                        <div style="text-align: center; margin-right: 10px;">
                                            <span class="sms-rate-label">Accepté: </span><span class="sms-accepted-value">{row['Acceptance_Rate']:.2f}%</span>
                                        </div>
                                        <div style="text-align: center; margin-right: 10px;">
                                            <span class="sms-rate-label">Refusé: </span><span class="sms-refused-value">{row['Refusal_Rate']:.2f}%</span>
                                        </div>
                                        <div style="text-align: center;">
                                            <span class="sms-rate-label">Erreur: </span><span class="sms-error-value">{row['Error_Rate']:.2f}%</span>
                                        </div>
                                    </div>
                                </div>
                                """.replace(",", " "), unsafe_allow_html=True)
                        else:
                            st.info("Aucune statistique d'équipe à afficher pour la sélection actuelle.")
                    else:
                        st.warning("Impossible d'afficher les performances des équipes. Vérifiez que la colonne 'Team' est disponible après le filtrage ou que les données 'Hyp' permettent la jointure.")
                        with st.expander("Détails du problème"):
                            st.write("Informations de debug:")
                            for msg in st.session_state.debug_msg_recolts:
                                st.write(msg)
                except Exception as e:
                    st.error(f"Une erreur inattendue est survenue lors du calcul des performances d'équipe : {str(e)}")
                  
                        
                       

            # --- Line Charts and Pie Chart ---
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                st.markdown("<h3 style='color: #007bad;'>Récoltes par Jour de la Semaine</h3>", unsafe_allow_html=True)
                if 'ORDER_DATE' in filtered_recolts.columns:
                    filtered_recolts['Weekday'] = filtered_recolts['ORDER_DATE'].dt.weekday
                    recoltes_jour = filtered_recolts.groupby('Weekday')['Total_Recolt'].sum().reset_index()
                    jours = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}
                    recoltes_jour['Jour'] = recoltes_jour['Weekday'].map(jours)
                    all_days = pd.DataFrame({'Weekday': range(7)})
                    recoltes_jour = pd.merge(all_days, recoltes_jour, on='Weekday', how='left').fillna(0)
                    recoltes_jour['Jour'] = recoltes_jour['Weekday'].map(jours)
                    recoltes_jour = recoltes_jour.sort_values('Weekday')

                    fig_jour = px.line(recoltes_jour,
                                        x='Jour',
                                        y='Total_Recolt',
                                        line_shape='spline',
                                        color_discrete_sequence=['#525CEB']) # Consistent color

                    fig_jour.update_traces(
                        line=dict(width=4, color='#525CEB'),
                        mode='lines+markers+text',
                        marker=dict(size=10, color='#3D3B40', line=dict(width=1, color='#FFFFFF')),
                        text=[f"€{y:,.0f}" for y in recoltes_jour['Total_Recolt']],
                        textposition="top center",
                        textfont=dict(color="#F70F49", size=14, family='Arial', weight='bold'),
                        hovertemplate='Jour: %{x}<br>Récoltes: €%{y:,.2f}<extra></extra>',
                        fill='tozeroy',
                        fillcolor='rgba(179, 191, 231, 0.4)'
                    )

                    fig_jour.update_layout(
                        xaxis_title=None,
                        yaxis_title=None,
                        plot_bgcolor='#FFFFFF',
                        paper_bgcolor='#FFFFFF',
                        xaxis_gridcolor='#E0E0E0',
                        yaxis_gridcolor='#E0E0E0',
                        xaxis=dict(
                            tickmode='array',
                            tickvals=recoltes_jour['Jour'],
                            categoryorder='array',
                            categoryarray=recoltes_jour['Jour'],
                            tickfont=dict(size=14, color='#3D3B40', weight='bold')
                        ),
                        yaxis=dict(
                            range=[0, recoltes_jour['Total_Recolt'].max() * 1.2],
                            tickfont=dict(size=12, color='#3D3B40')
                        ),
                        font=dict(family='Arial', size=12, color='#3D3B40'),
                        margin=dict(t=50, b=50, l=50, r=50)
                    )

                    st.plotly_chart(fig_jour, use_container_width=True)
                else:
                    st.warning("Données de date de commande manquantes pour ce graphique.")

            with col2:
                st.markdown("<h3 style='color: #007bad;'>Transactions Acceptées vs Refusées</h3>", unsafe_allow_html=True)
                if 'SHORT_MESSAGE' in filtered_recolts.columns and 'Total_Recolt' in filtered_recolts.columns:
                    status_recolts = filtered_recolts.groupby('SHORT_MESSAGE')['Total_Recolt'].sum().reset_index()

                    fig_pie = px.pie(status_recolts,
                                    values='Total_Recolt',
                                    names='SHORT_MESSAGE',
                                    color='SHORT_MESSAGE',
                                    color_discrete_map={'ACCEPTED': '#007bad', 'REFUSED': '#ff0000', 'ERROR': '#ffa500'},
                                    hole=0.4)

                    fig_pie.update_traces(
                        textinfo='value+percent',
                        textposition='outside',
                        textfont_size=18,
                        textfont_color=['#007bad', '#ff0000', '#ffa500'],
                        marker=dict(line=dict(color='white', width=2)),
                        pull=[0.05, 0, 0],
                        rotation=-90
                    )

                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.warning("Données de message court ou de récolte totale manquantes pour ce graphique.")

            with col3:
                st.markdown("<h3 style='color: #007bad;'>Récoltes par Heure (9h-20h)</h3>", unsafe_allow_html=True)
                if 'ORDER_DATE' in filtered_recolts.columns:
                    recoltes_heure = filtered_recolts[
                        (filtered_recolts['ORDER_DATE'].dt.hour >= 9) &
                        (filtered_recolts['ORDER_DATE'].dt.hour <= 20)
                    ].groupby(filtered_recolts['ORDER_DATE'].dt.hour)['Total_Recolt'].sum().reset_index()

                    recoltes_heure = recoltes_heure.rename(columns={'ORDER_DATE': 'Heure'})
                    all_hours = pd.DataFrame({'Heure': range(9, 21)})
                    recoltes_heure = pd.merge(all_hours, recoltes_heure, on='Heure', how='left').fillna(0)
                    recoltes_heure = recoltes_heure.sort_values('Heure')

                    fig_heure = px.line(recoltes_heure, x='Heure', y='Total_Recolt',
                                    line_shape='spline',
                                    color_discrete_sequence=['#525CEB'])

                    fig_heure.update_traces(
                        line=dict(width=4, color='#525CEB'),
                        mode='lines+markers+text',
                        marker=dict(size=10, color='#3D3B40', line=dict(width=1, color='#FFFFFF')),
                        text=[f"€{y:,.0f}" for y in recoltes_heure['Total_Recolt']],
                        textposition="top center",
                        textfont=dict(color="#F50808", size=14, family='Arial', weight='bold'),
                        hovertemplate='Heure: %{x}h<br>Récoltes: €%{y:,.2f}<extra></extra>',
                        fill='tozeroy',
                        fillcolor='rgba(179, 191, 231, 0.4)'
                    )

                    fig_heure.update_layout(
                        xaxis_title="Heure de la journée",
                        yaxis_title=None,
                        plot_bgcolor='#FFFFFF',
                        paper_bgcolor='#FFFFFF',
                        xaxis_gridcolor='#E0E0E0',
                        yaxis_gridcolor='#E0E0E0',
                        xaxis=dict(
                            tickmode='linear',
                            dtick=1,
                            range=[8.5, 20.5],
                            tickfont=dict(size=14, color='#3D3B40', weight='bold')
                        ),
                        yaxis=dict(
                            range=[0, recoltes_heure['Total_Recolt'].max() * 1.2],
                            tickfont=dict(size=12, color='#3D3B40')
                        ),
                        font=dict(family='Arial', size=12, color='#3D3B40'),
                        margin=dict(t=50, b=50, l=50, r=50)
                    )

                    st.plotly_chart(fig_heure, use_container_width=True)
                else:
                    st.warning("Données de date de commande manquantes pour ce graphique.")
        else:
            st.warning("Aucune donnée de récolte ne correspond aux filtres sélectionnés.")



def dashboard_page(logs_df, sales_df, recolts_df, staff_df, start_date, end_date):
    """Affiche le tableau de bord principal."""
    

    col1, col2 = st.columns([2, 2])

    with col1:
        mois_fr = {
            1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
            5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
            9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
        }

        start_formatted = f"{start_date.day:02d} {mois_fr[start_date.month]} {start_date.year}"
        end_formatted = f"{end_date.day:02d} {mois_fr[end_date.month]} {end_date.year}"

        st.markdown(
            f"""
            <h1 style='text-align: left; font-size: 2.1em; margin-bottom: 0; color: #002a48;'>
                Dashboard du 
                <span style='color: #00afe1;'>{start_formatted}</span> au 
                <span style='color: #00afe1;'>{end_formatted}</span>
            </h1>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            "<h1 style='color: #00afe1; text-align: right; font-size: 2.1em; margin-bottom: 0; padding-top: 20px;'>"
            "Analyse Commerciale - Sales - Recolts - Logs</h1>",
            unsafe_allow_html=True
        )

    # Custom CSS for tabs
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] button {
            background-color: #f0f2f6; /* Lighter background for tabs */
            border-radius: 5px 5px 0 0; /* Rounded top corners */
            padding: 10px 15px; /* Adjust padding to reduce vertical space */
            margin-right: 5px; /* Space between tabs */
            border: 1px solid #ddd; /* Light border */
            border-bottom: none; /* No border at the bottom to blend with content */
            color: #002a48; /* Darker text color */
            font-weight: bold; /* Make tab titles bold */
            transition: all 0.2s ease-in-out; /* Smooth transition on hover/active */
        }
        .stTabs [data-baseweb="tab-list"] button:hover {
            background-color: #e6e8eb; /* Slightly darker on hover */
        }
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: #00afe1; /* Active tab color */
            color: white; /* White text for active tab */
            border-color: #00afe1; /* Active tab border color */
            border-bottom: none; /* Ensure no bottom border */
        }
        /* Reduce vertical space for the overall tab container */
        .stTabs {
            margin-top: -10px; /* Adjust as needed to pull tabs up */
            margin-bottom: 15px; /* Space below tabs */
        }
        </style>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Sales Analytics", "💰 Recolts Analytics", "🧾 Logs Analytics"])


    
    with tab1:
        sales_page(sales_df, staff_df, start_date, end_date)
    
    with tab2:
        recolts_page(recolts_df, staff_df, start_date, end_date)
    with tab3:
        logs_page(logs_df, staff_df, start_date, end_date)



def planning_page(sales_df, staff_df):
    """Affiche la page de planning."""
    st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Planning</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #007bad; margin-top: 0;'>All Teams</h2>", unsafe_allow_html=True)
    
    
    

    if sales_df.empty:
        st.warning("Aucune donnée de vente disponible.")
        return
    
    selected_country = st.selectbox("Sélectionner un pays", sorted(sales_df['Country'].dropna().unique()), key='country_filter')
    filtered_sales = sales_df[sales_df['Country'] == selected_country]

    col1, col2 = st.columns(2)
    col1.metric("Ventes Totales", f"€{filtered_sales['Total_Sale'].sum():,.0f}".replace(",", " "))
    col2.metric("Nombre de Transactions", len(filtered_sales))

    col1, col2 = st.columns(2)
    with col1:
        ventes_ville = filtered_sales.groupby('City')['Total_Sale'].sum().reset_index()
        if not ventes_ville.empty:
            fig = px.bar(ventes_ville, x='City', y='Total_Sale', title="Ventes par Ville")
            st.plotly_chart(fig, use_container_width=True, key="ventes_ville_planning")
        else:
            st.info("Pas de ventes par ville pour ce pays.")
    
    with col2:
        if not staff_df.empty:
            if 'Country' in staff_df.columns:
                effectifs = staff_df[staff_df['Country'] == selected_country]
            else:
                effectifs = staff_df.copy()

            if not effectifs.empty and 'City' in effectifs.columns:
                effectif_par_ville = effectifs['City'].value_counts().reset_index()
                effectif_par_ville.columns = ['City', 'Nombre']
                fig2 = px.bar(effectif_par_ville, x='City', y='Nombre', title="Effectif par Ville")
                st.plotly_chart(fig2, use_container_width=True, key="effectif_ville_planning")
            else:
                st.info("Aucun effectif disponible pour ce pays.")
        else:
            st.warning("Aucune donnée de personnel disponible.")




def setting_page():
    add_custom_css()
    """Affiche la page des paramètres."""

    
    st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Paramètres</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #007bad; margin-top: 0;'>Gestion des Utilisateurs</h2>", unsafe_allow_html=True)

    
    
    st.markdown("<h2 style='font-size: 28px; font-weight: bold; color: #00afe1;'>Paramètres Utilisateur</h2>", unsafe_allow_html=True)
    
    hyp_input = st.text_input("**Entrez l'ID (Hyp) de l'utilisateur**",
                            placeholder="Saisir l'identifiant Hyp...",
                            help="Rechercher un utilisateur par son identifiant unique")

    # Exemple d'utilisation de l'input (pour montrer que ça fonctionne toujours)
    if hyp_input:
        st.write(f"Vous avez saisi : {hyp_input}")


    if hyp_input:
        user_details = get_user_details(hyp_input)  # À définir ailleurs

        if user_details:
            try:
                date_in = pd.to_datetime(user_details[2])
                anciennete = (datetime.now().date() - date_in.date()).days // 365

                col1, col2, col3 = st.columns([2, 2, 2])
                with col1:
                    st.markdown("<h3 style='color: #002a48;'>Informations Professionnelles</h3>", unsafe_allow_html=True)
                    st.write(f"**Nom:** {user_details[0]}")
                    st.write(f"**Prénom:** {user_details[1]}")
                    st.write(f"**Date d'entrée:** {date_in.strftime('%d/%m/%Y')}")
                    st.write(f"**Ancienneté:** {anciennete} ans")
            except Exception as e:
                st.error(f"Erreur lors de l'affichage des détails utilisateur : {e}")

def setting_page():
    """Affiche la page des paramètres avec un design modernisé."""
    # En-tête avec les titres alignés
    col1, col2 = st.columns([2, 2])

    with col1:
        st.markdown(
            "<h1 style='text-align: left; color: #002a48; margin-bottom: 0;'>Paramètres</h1>", 
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            "<h1 style='text-align: right; color: #00afe1; margin-bottom: 0;'>Gestion des Utilisateurs</h1>", 
            unsafe_allow_html=True
        )

    
    # Section recherche utilisateur
    with st.container():
                
        hyp_input = st.text_input("**Entrez l'ID (Hyp) de l'utilisateur**", 
                                placeholder="Saisir l'identifiant Hyp...",
                                help="Rechercher un utilisateur par son identifiant unique")
    
    if hyp_input:
        user_details = get_user_details(hyp_input)
        
        if user_details:
            # Conversion de la date en objet datetime
            date_in = user_details[2]
            date_obj = None
            date_str = "Date inconnue"
            anciennete = "N/A"
            
            if date_in:  # Si la date existe
                if isinstance(date_in, str):
                    # Essayer plusieurs formats de date courants
                    date_formats = [
                        '%Y-%m-%d',  # 2023-12-31
                        '%d/%m/%Y',  # 31/12/2023
                        '%m/%d/%Y',  # 12/31/2023
                        '%Y-%m-%d %H:%M:%S',  # 2023-12-31 23:59:59
                        '%d-%m-%Y',  # 31-12-2023
                        '%Y%m%d'     # 20231231
                    ]
                    
                    for fmt in date_formats:
                        try:
                            date_obj = datetime.strptime(date_in, fmt)
                            break
                        except ValueError:
                            continue
                    
                    if not date_obj:
                        st.error(f"Format de date non reconnu: {date_in}")
                        date_str = date_in
                elif hasattr(date_in, 'strftime'):  # Si c'est déjà un objet date/datetime
                    date_obj = date_in
            
            if date_obj:
                try:
                    anciennete = (datetime.now().date() - date_obj.date()).days // 365
                    date_str = date_obj.strftime('%d/%m/%Y')
                except AttributeError:
                    pass
            
            # Carte utilisateur
            with st.expander(f"🔍 Fiche utilisateur : {user_details[0]} {user_details[1]}", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 15px;'>
                        <h3 style='color: #002a48; border-bottom: 1px solid #dee2e6; padding-bottom: 10px;'>Informations Professionnelles</h3>
                        <p><strong>Nom:</strong> {user_details[0]}</p>
                        <p><strong>Prénom:</strong> {user_details[1]}</p>
                        <p><strong>Date d'entrée:</strong> {date_str}</p>
                        <p><strong>Ancienneté:</strong> {anciennete} {"an" if isinstance(anciennete, int) and anciennete == 1 else "ans" if isinstance(anciennete, int) else ""}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 15px;'>
                        <h3 style='color: #002a48; border-bottom: 1px solid #dee2e6; padding-bottom: 10px;'>Détails</h3>
                        <p><strong>Team:</strong> {}</p>
                        <p><strong>Type:</strong> {}</p>
                        <p><strong>Activité:</strong> {}</p>
                        <p><strong>Nom d'utilisateur:</strong> {}</p>
                        
                    </div>
                    """.format(
                        user_details[3], 
                        user_details[4], 
                        user_details[5], 
                        user_details[6], 
                        user_details[7] if user_details[7] else 'Jamais'
                    ), unsafe_allow_html=True)
                
                with col3:
                    st.markdown("""
                    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 15px; height: 100%;'>
                        <h3 style='color: #007bad; border-bottom: 1px solid #dee2e6; padding-bottom: 8px;'>Actions</h3>
                    """, unsafe_allow_html=True)
                    
                    reset_pwd = st.checkbox("🔑 Réinitialiser le mot de passe")
                    
                    if reset_pwd:
                        if st.button("**Confirmer la réinitialisation**", 
                                   type="primary",
                                   help="Réinitialise le mot de passe à l'identifiant Hyp par défaut"):
                            if reset_password(hyp_input):
                                st.success(f"Mot de passe réinitialisé avec succès à la valeur: `{hyp_input}`")
                            else:
                                st.error("Erreur lors de la réinitialisation du mot de passe")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
           
           
        else:
            st.warning("⚠️ Aucun utilisateur trouvé avec cet ID (Hyp)")
                
                # ... (le reste du code reste inchangé)
def main():
    """Fonction principale de l'application."""
    add_custom_css()
    
    # Vérification de l'authentification
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        login_page()
        return
    
    # Chargement des données
    with st.spinner('Chargement des données...'):
        sales_df, recolts_df, staff_df, logs_df = load_data()
        logs_df = preprocess_data(logs_df)
        sales_df = preprocess_data(sales_df)
        recolts_df = preprocess_data(recolts_df)
        staff_df = preprocess_data(staff_df)
    
    # Navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown(f"**Connecté en tant que:** {st.session_state.username}")
    
    # Ajoutez les sélecteurs de date dans la sidebar
    st.sidebar.markdown("### Période d'analyse")
    start_date = st.sidebar.date_input("Date de début", 
                                      pd.to_datetime("2023-01-01").date(),
                                      key="start_date")
    end_date = st.sidebar.date_input("Date de fin", 
                                    pd.to_datetime("2023-12-31").date(),
                                    key="end_date")
    
    # Vérification que la date de fin est après la date de début
    if start_date > end_date:
        st.sidebar.error("La date de fin doit être postérieure à la date de début")
        end_date = start_date
    
    page = st.sidebar.radio("Menu", 
                           ["Dashboard", "Sales", "Recolts", "Logs", "Planning", "Settings"],
                           index=0)
    
    if page == "Dashboard":
        dashboard_page(logs_df, sales_df, recolts_df, staff_df, start_date, end_date)
    elif page == "Sales":
        sales_page(sales_df, staff_df, start_date, end_date)
    elif page == "Recolts":
        recolts_page(recolts_df, staff_df, start_date, end_date)
    elif page == "Logs":
        logs_page(logs_df, staff_df, start_date, end_date)    
    elif page == "Planning":
        planning_page(sales_df, staff_df)
    elif page == "Settings":
        setting_page()