import streamlit as st
import pandas as pd
import sqlite3

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
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from contextlib import closing
import io



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
            
            /* General Body Background */
            body {
                background-color: #FFFFFF;
                color: #043a64; /* bleu Foncé */
            }
            .stApp {
                background-color: #FFFFFF;
            }

            /* ==== General Titles ==== */
            h1 {
                color: #043a64; /* bleu Foncé */
                margin-bottom: 10px;
                font-size: 3em;
                text-align: center;
                padding-bottom: 6px;
                border-bottom: 3px solid #2596be; /* Bleu */
                font-weight: 900;
            }
            h2 {
                color: #043a64; /* bleu Foncé */
                margin-top: 8px;
                margin-bottom: 25px;
                font-size: 2em;
                text-align: center;
                font-weight: 800;
            }
            h3 {
                color: #043a64; /* bleu Foncé */
                margin-top: 35px;
                margin-bottom: 20px;
                border-bottom: 2px solid #2596be; /* Bleu */
                padding-bottom: 6px;
                font-size: 1.6em;
                font-weight: 700;
            }
            hr {
                border: none;
                border-top: 2px solid #2596be; /* Bleu */
                margin: 20px auto 25px auto;
                width: 85%;
                border-radius: 5px;
            }

            /* ==== Tabs ==== */
            .stTabs [data-baseweb="tab-list"] button {
                background-color: #e0e8dc; /* back ground */
                border-radius: 8px 8px 0 0;
                padding: 10px 16px;
                margin-right: 8px;
                border: 1px solid #2596be; /* Bleu */
                border-bottom: none;
                color: #043a64; /* bleu Foncé */
                font-weight: bold;
                font-size: 1em;
                transition: all 0.2s ease-in-out;
            }
            .stTabs [data-baseweb="tab-list"] button:hover {
                background-color: #2596be; /* Bleu */
                color: #FFFFFF;
            }
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
                background-color: #043a64; /* bleu Foncé */
                color: #e0e8dc; /* back ground */
                border-color: #043a64; /* bleu Foncé */
            }
            .stTabs {
                margin-top: -10px;
                margin-bottom: 20px;
            }

            /* ==== Metric Cards ==== */
            .metric-card {
                background-color: #e0e8dc; /* back ground */
                border: 1px solid #2596be; /* Bleu */
                border-left: 6px solid #043a64; /* bleu Foncé */
                border-radius: 10px;
                padding: 12px;
                margin-bottom: 12px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
                text-align: center;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                color: #043a64; /* bleu Foncé */
                min-height: 80px;
            }
            .metric-card:hover {
                transform: translateY(-4px);
                box-shadow: 3px 3px 14px rgba(0,0,0,0.5);
            }
            .metric-title {
                color: #043a64; /* bleu Foncé */
                font-size: 0.95em;
                font-weight: 700;
                margin-bottom: 6px;
                text-transform: uppercase;
                letter-spacing: 0.6px;
            }
            .metric-value {
                color: #043a64; /* bleu Foncé */
                font-size: 2em;
                font-weight: 800;
                line-height: 1;
            }

            /* ==== Team Performance Cards ==== */
            .team-performance-card {
                background-color: #e0e8dc; /* back ground */
                border: 1px solid #2596be; /* Bleu */
                border-left: 6px solid #043a64; /* bleu Foncé */
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 12px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
                text-align: left;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                color: #043a64; /* bleu Foncé */
            }
            .team-performance-card:hover {
                transform: translateY(-4px);
                box-shadow: 3px 3px 14px rgba(0,0,0,0.5);
            }
            .team-performance-title {
                font-size: 1.4em;
                font-weight: 800;
                color: #043a64; /* bleu Foncé */
                margin-bottom: 8px;
            }
            .team-stat-label {
                font-size: 0.9em;
                color: #555;
                margin-bottom: 3px;
                font-weight: 600;
            }
            .team-stat-value {
                font-size: 1.6em;
                font-weight: 800;
                color: #043a64; /* bleu Foncé */
                line-height: 1;
            }
            .team-conversion-value {
                font-size: 1.8em;
                font-weight: 900;
                color: #28a745;
            }
            .sms-rate-section {
                display: flex;
                justify-content: center;
                margin-top: 10px;
                padding-top: 8px;
                border-top: 1px dashed #2596be; /* Bleu */
            }

            /* ==== Selectbox ==== */
            .stSelectbox div[data-baseweb="select"] {
                border-radius: 8px;
                border: 2px solid #2596be; /* Bleu */
                padding: 6px;
                box-shadow: inset 1px 1px 3px rgba(0,0,0,0.2);
            }
            .stSelectbox div[data-baseweb="select"] > div:first-child {
                background-color: #e0e8dc; /* back ground */
                color: #043a64; /* bleu Foncé */
                font-weight: bold;
            }
            .stSelectbox div[data-baseweb="menu"] {
                background-color: #043a64; /* bleu Foncé */
            }
            .stSelectbox div[data-baseweb="menu"] li {
                color: #FFFFFF;
                font-size: 1em;
            }
            .stSelectbox div[data-baseweb="menu"] li:hover {
                background-color: #2596be; /* Bleu */
                color: #FFFFFF;
            }

            /* ==== Button Styling ==== */
            .stButton button {
                background-color: #e0e8dc; /* back ground */
                color: #043a64; /* bleu Foncé */
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
                background-color: #2596be; /* Bleu */
                color: #FFFFFF;
                box-shadow: 3px 3px 12px rgba(0,0,0,0.25);
            }

            .stButton button:active,
            .stButton button:focus:not(:active) {
                background-color: #043a64; /* bleu Foncé */
                color: #e0e8dc; /* back ground */
                box-shadow: inset 2px 2px 6px rgba(0,0,0,0.2);
            }

            /* ==== DataFrame ==== */
            .stDataFrame thead th {
                background-color: #043a64; /* bleu Foncé */
                color: #e0e8dc; /* back ground */
                padding: 12px;
                text-align: left;
                font-weight: bold;
            }
            .stDataFrame tbody tr:hover {
                background-color: #2596be; /* Bleu */
                color: #FFFFFF;
            }
            .stDataFrame tbody td {
                border-bottom: 1px solid #2596be; /* Bleu */
                color: #043a64; /* bleu Foncé */
            }

            /* ==== Sidebar & Menu ==== */
            div[data-testid="stSidebar"] {
                background-color: #e0e8dc !important; /* back ground */
                color: #043a64 !important; /* bleu Foncé */
            }
            .css-1cypcdb, .css-1lcbmhc {
                background-color: #e0e8dc !important; /* back ground */
            }
            .css-1cypcdb button, .css-1lcbmhc button {
                color: #043a64 !important; /* bleu Foncé */
            }
            .css-1cypcdb button:hover, .css-1lcbmhc button:hover {
                background-color: #2596be !important; /* Bleu */
                color: #FFFFFF !important;
            }
            .css-1cypcdb button[data-selected="true"], .css-1lcbmhc button[data-selected="true"] {
                background-color: #043a64 !important; /* bleu Foncé */
                color: #e0e8dc !important; /* back ground */
            }

            /* ==== Date Input ==== */
            .stDateInput div[data-baseweb="input"] {
                background-color: #e0e8dc; /* back ground */
                color: #043a64; /* bleu Foncé */
                border: 2px solid #2596be; /* Bleu */
            }
            .stDateInput div[data-baseweb="input"] input {
                background-color: #e0e8dc; /* back ground */
                color: #043a64; /* bleu Foncé */
            }
            .stDateInput div[data-baseweb="calendar"] {
                border: 1px solid #2596be; /* Bleu */
                color: #043a64; /* bleu Foncé */
            }
            .stDateInput div[data-baseweb="calendar"] .DayPicker_weekdays {
                color: #2596be; /* Bleu */
            }
            .stDateInput div[data-baseweb="calendar"] .DayPicker_day--selected {
                background-color: #043a64 !important; /* bleu Foncé */
                color: #e0e8dc !important; /* back ground */
            }
            .stDateInput div[data-baseweb="calendar"] .DayPicker_day--hovered {
                background-color: #2596be !important; /* Bleu */
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
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    
    with col2:
        # Centrer l'image avec HTML
        st.image("Dental_Implant.png", use_column_width=True)

    with col3:
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        col1, col2 = st.columns([1, 5])
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

def recolts_page(recolts_df, staff_df, start_date, end_date):
    """Affiche la page des récoltes avec le nouveau style, incluant les cartes Top 3 et les graphiques de ligne/transaction."""

    add_custom_css() # Appel de la fonction CSS personnalisée

    st.markdown("<h3 style='color: #007bad;'>Filtrage des Récoltes</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        with col1:
            country_filter = st.selectbox("Pays", ['Tous'] + sorted(recolts_df['Country'].dropna().unique()), key='recolts_country')
        with col2:
            team_filter = st.selectbox("Equipes", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()), key='recolts_team')
        with col3:
            activity_filter = st.selectbox("Activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()), key='recolts_activity')
        with col4:
            transaction_filter = st.selectbox("Transactions", ['Toutes'] + sorted(recolts_df['SHORT_MESSAGE'].dropna().unique()), key='recolts_transaction')

    with st.spinner("Application des filtres..."):
        filtered_recolts = filter_data(recolts_df, country_filter, team_filter, activity_filter, transaction_filter, start_date, end_date, staff_df)

        if not filtered_recolts.empty:
            # S'assurer que les dates sont au bon format pour les opérations temporelles
            if 'ORDER_DATE' in filtered_recolts.columns:
                filtered_recolts['ORDER_DATE'] = pd.to_datetime(filtered_recolts['ORDER_DATE'], errors='coerce')
                # Supprimer les lignes où la conversion de date a échoué
                filtered_recolts.dropna(subset=['ORDER_DATE'], inplace=True)

            # Géocoder les données après filtrage
            if 'City' in filtered_recolts.columns and 'Country' in filtered_recolts.columns:
                # Vérifier si filtered_recolts a déjà Latitude/Longitude ou si staff_df n'est pas nécessaire
                if 'Latitude' not in filtered_recolts.columns or 'Longitude' not in filtered_recolts.columns:
                    filtered_recolts = geocode_data(filtered_recolts.copy()) # Utiliser .copy() pour éviter SettingWithCopyWarning


            # Assurez-vous que 'Hyp' (employee ID) est disponible pour les métriques
            # et pour la jointure avec staff_df pour la colonne 'Team'
            if 'Hyp' not in filtered_recolts.columns and 'Hyp' in recolts_df.columns and 'Hyp' in staff_df.columns:
                 # Jointure pour ajouter la colonne 'Team' aux récoltes filtrées
                initial_recolts_rows = len(filtered_recolts)
                filtered_recolts = filtered_recolts.merge(
                    staff_df[['Hyp', 'Team', 'Activité']].drop_duplicates(), # Inclure 'Activité' pour le filtre si non déjà fait
                    on='Hyp',
                    how='left'
                )
                teams_found = filtered_recolts['Team'].notna().sum()
                if teams_found == 0 and initial_recolts_rows > 0:
                    st.warning("Aucune correspondance 'Hyp' trouvée entre les récoltes filtrées et les données du personnel.")


            # --- Métriques Clés (Top Cards) ---
            
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                total_recolts_sum = filtered_recolts['Total_Recolt'].sum() if 'Total_Recolt' in filtered_recolts.columns else 0
                kpi_card_html(col1, "Total Récoltes", f"{total_recolts_sum:,.0f}€", "#007bad", "seedling") # Icône 'seedling' pour les récoltes

            with col2:
                if 'Rating' in filtered_recolts.columns:
                    avg_rating = filtered_recolts['Rating'].mean()
                    if not pd.isna(avg_rating):
                        rating_display = f"{'★' * int(round(avg_rating))}{'☆' * (7 - int(round(avg_rating)))}"
                        kpi_card_html(col2, "Note Moyenne", rating_display, "#ffc107", "star") # Jaune pour la note
                    else:
                         kpi_card_html(col2, "Note Moyenne", "N/A", "#6c757d", "star-half-alt") # Gris si pas de note
                else:
                    kpi_card_html(col2, "Note Moyenne", "N/A", "#fc9307", "star-half-alt")

            with col3:
                total_transactions = len(filtered_recolts)
                kpi_card_html(col3, "Total Transactions", f"{total_transactions:,}", "#043a64", "exchange-alt") # Vert-bleu pour les transactions

            with col4:
                unique_employees = filtered_recolts['Hyp'].nunique() if 'Hyp' in filtered_recolts.columns else 0
                kpi_card_html(col4, "Employés Uniques", f"{unique_employees:,}", "#fc9307", "users") # Violet pour les employés

            # --- Carte et Top Équipes ---
            
            col_map, col_teams = st.columns([2, 1])

            with col_map:
                st.markdown("<h3 style='color: #007bad;'>Récoltes par Ville (Vue Carte)</h3>", unsafe_allow_html=True)
                # S'assurer que les colonnes Latitude et Longitude existent et ne sont pas toutes NaN
                if 'Latitude' in filtered_recolts.columns and 'Longitude' in filtered_recolts.columns and not filtered_recolts[['Latitude', 'Longitude']].dropna().empty:
                    city_recolts_map = filtered_recolts.groupby('City').agg(
                        Total_Recolt=('Total_Recolt', 'sum'),
                        Latitude=('Latitude', 'first'),
                        Longitude=('Longitude', 'first'),
                        Accepted_SMS=('SHORT_MESSAGE', lambda x: (x == 'ACCEPTED').sum()),
                        Refused_SMS=('SHORT_MESSAGE', lambda x: (x == 'REFUSED').sum()),
                        Error_SMS=('SHORT_MESSAGE', lambda x: (x == 'ERROR').sum())
                    ).reset_index()

                    city_recolts_map = city_recolts_map.dropna(subset=['Latitude', 'Longitude'])

                    if not city_recolts_map.empty:
                        city_recolts_map['Formatted_Recolt'] = city_recolts_map['Total_Recolt'].apply(lambda x: f"{x:,.0f}€")
                        city_recolts_map['Short_Recolt'] = city_recolts_map['Total_Recolt'].apply(lambda x: f"{x/1000:.0f}k" if x >= 1000 else f"{x:.0f}")

                        city_recolts_map['Total_SMS'] = city_recolts_map['Accepted_SMS'] + city_recolts_map['Refused_SMS'] + city_recolts_map['Error_SMS']
                        
                        city_recolts_map['Refused_SMS_Percentage'] = city_recolts_map.apply(
                            lambda row: (row['Refused_SMS'] / row['Total_SMS']) * 100 if row['Total_SMS'] > 0 else 0, axis=1
                        ).round(2)
                        city_recolts_map['Error_SMS_Percentage'] = city_recolts_map.apply(
                            lambda row: (row['Error_SMS'] / row['Total_SMS']) * 100 if row['Total_SMS'] > 0 else 0, axis=1
                        ).round(2)

                        fig_map = px.scatter_mapbox(
                            city_recolts_map,
                            lat="Latitude",
                            lon="Longitude",
                            size="Total_Recolt",
                            text="Short_Recolt",
                            color_discrete_sequence=['#007bad'] * len(city_recolts_map),
                            hover_name="City",
                            hover_data={
                                "Formatted_Recolt": True,
                                "Latitude": False,
                                "Longitude": False,
                                "Refused_SMS_Percentage": ":.2f",
                                "Error_SMS_Percentage": ":.2f",
                                "Total_Recolt": False,
                                "Accepted_SMS": False,
                                "Refused_SMS": False,
                                "Error_SMS": False,
                                "Short_Recolt": False
                            },
                            size_max=35,
                            zoom=5,
                            mapbox_style="carto-positron"
                        )

                        fig_map.update_traces(
                            textfont=dict(family="Arial", size=12, color="white"),
                            textposition="middle center",
                            hovertemplate="<b>%{hover_name}</b><br>" +
                                          "Récoltes: %{customdata[0]}<br>" +
                                          "Transactions Refusées: %{customdata[1]:.2f}%<br>" +
                                          "Transactions Erreur: %{customdata[2]:.2f}%" +
                                          "<extra></extra>",
                            customdata=city_recolts_map[['Formatted_Recolt', 'Refused_SMS_Percentage', 'Error_SMS_Percentage', 'City']]
                        )

                        fig_map.update_layout(
                            height=630,
                            margin={"r":0,"t":40,"l":0,"b":0},
                            hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial")
                        )
                        st.plotly_chart(fig_map, use_container_width=True)
                    else:
                        st.warning("Aucune donnée de récolte avec des coordonnées géographiques valides pour afficher sur la carte.")
                else:
                    st.warning("Les colonnes 'Latitude' ou 'Longitude' sont manquantes ou vides dans les données de récolte ou ne contiennent pas de valeurs valides.")

            with col_teams:
                st.markdown("<h3 style='color: #007bad;'>Performance des 3 Top Équipes</h3>", unsafe_allow_html=True)
                
                # S'assurer que 'Team' est présent pour le calcul des performances d'équipe
                if 'Team' not in filtered_recolts.columns or filtered_recolts['Team'].isnull().all():
                    st.warning("La colonne 'Team' est manquante ou vide après filtrage. Assurez-vous que la jointure avec 'staff_df' via 'Hyp' a réussi ou que 'Team' est déjà dans 'recolts_df'.")
                
                if 'Team' in filtered_recolts.columns and not filtered_recolts['Team'].dropna().empty:
                    team_stats = filtered_recolts.groupby('Team').agg(
                        Total_Recolt=('Total_Recolt', 'sum'),
                        Total_Transactions=('Total_Recolt', 'count'),
                        Accepted_SMS=('SHORT_MESSAGE', lambda x: (x == 'ACCEPTED').sum()),
                        Refused_SMS=('SHORT_MESSAGE', lambda x: (x == 'REFUSED').sum()),
                        Error_SMS=('SHORT_MESSAGE', lambda x: (x == 'ERROR').sum())
                    ).reset_index()

                    if not team_stats.empty:
                        team_stats['Total_SMS_Transactions'] = team_stats['Accepted_SMS'] + team_stats['Refused_SMS'] + team_stats['Error_SMS']
                        
                        team_stats['Acceptance_Rate'] = team_stats.apply(
                            lambda row: (row['Accepted_SMS'] / row['Total_SMS_Transactions']) * 100 if row['Total_SMS_Transactions'] > 0 else 0, axis=1
                        ).round(2)
                        
                        team_stats['Refusal_Rate'] = team_stats.apply(
                            lambda row: (row['Refused_SMS'] / row['Total_SMS_Transactions']) * 100 if row['Total_SMS_Transactions'] > 0 else 0, axis=1
                        ).round(2)
                        
                        team_stats['Error_Rate'] = team_stats.apply(
                            lambda row: (row['Error_SMS'] / row['Total_SMS_Transactions']) * 100 if row['Total_SMS_Transactions'] > 0 else 0, axis=1
                        ).round(2)

                        total_recolt_global = filtered_recolts['Total_Recolt'].sum()
                        team_stats['Conversion_Rate'] = team_stats['Total_Recolt'].apply(
                            lambda x: (x / total_recolt_global) * 100 if total_recolt_global > 0 else 0
                        ).round(2)

                        team_stats = team_stats.sort_values(by='Total_Recolt', ascending=False).head(3)
                        st.write("") # Espace pour alignement visuel

                        for index, row in team_stats.iterrows():
                            st.markdown(f"""
                                    <div class="team-performance-card" style="padding: 10px;">
                                        <div class="team-performance-title" style="font-size: 30px; font-weight: bold;">{row['Team']}</div>
                                        <div class="team-stat-row" style="display: flex; justify-content: space-between; align-items: center;">
                                            <div style="flex: 1; text-align: left;">
                                                <div class="team-stat-label" style="font-weight: bold; color: #fc6c04;">RÉCOLTES TOTALES:</div>
                                                <div class="team-stat-value" style="font-size: 38px; font-weight: bold;">{row['Total_Recolt']:,.0f}€</div>
                                            </div>
                                            <div style="flex: 1; text-align: center;">
                                                <div class="team-stat-label" style="font-weight: bold; color: #fc6c04;">TAUX CONVERSION:</div>
                                                <div class="team-conversion-value" style="font-size: 38px; font-weight: bold;">{row['Conversion_Rate']:.2f}%</div>
                                            </div>
                                            <div style="flex: 1; text-align: right;">
                                                <div class="team-stat-label" style="font-weight: bold; color: #fc6c04;">TRANSACTIONS:</div>
                                                <div class="team-stat-value" style="font-size: 38px; font-weight: bold;">{row['Total_Transactions']:,}</div>
                                            </div>
                                        </div>
                                        <div class="team-rates" style="display: flex; justify-content: right; margin-top: 5px; gap: 10px; font-size: 20px; font-weight: bold;">
                                            <span class="accepted" style="color: green;">✓ {row['Acceptance_Rate']:.1f}%</span>
                                            <span class="refused" style="color: red;">✗ {row['Refusal_Rate']:.1f}%</span>
                                            <span class="error" style="color: orange;">⚠ {row['Error_Rate']:.1f}%</span>
                                        </div>
                                    </div>
                                """.replace(",", " "), unsafe_allow_html=True)
                    else:
                        st.info("Aucune statistique d'équipe à afficher pour la sélection actuelle.")
                else:
                    st.warning("Impossible d'afficher les performances des équipes. Vérifiez que la colonne 'Team' est disponible après le filtrage ou que les données 'Hyp' permettent la jointure.")


            # --- Graphiques Linéaires et Camembert ---
           
            col_day, col_pie, col_hour = st.columns([1, 1, 1])

            with col_day:
                st.markdown("<h3 style='color: #007bad;'>Récoltes par Jour de la Semaine</h3>", unsafe_allow_html=True)
                if 'ORDER_DATE' in filtered_recolts.columns and not filtered_recolts['ORDER_DATE'].empty:
                    filtered_recolts['Weekday'] = filtered_recolts['ORDER_DATE'].dt.dayofweek # Renommé pour plus de clarté (0=Lundi)
                    recoltes_jour = filtered_recolts.groupby('Weekday')['Total_Recolt'].sum().reset_index()
                    jours = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}
                    
                    # Assurer que tous les jours sont présents même s'il n'y a pas de données
                    all_days_df = pd.DataFrame({'Weekday': range(7)})
                    recoltes_jour = pd.merge(all_days_df, recoltes_jour, on='Weekday', how='left').fillna(0)
                    recoltes_jour['Jour'] = recoltes_jour['Weekday'].map(jours)
                    recoltes_jour = recoltes_jour.sort_values('Weekday') # S'assurer de l'ordre des jours

                    fig_jour = px.line(recoltes_jour,
                                        x='Jour',
                                        y='Total_Recolt',
                                        line_shape='spline',
                                        color_discrete_sequence=['#525CEB'])

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
                    st.warning("Données de date de commande manquantes pour ce graphique ou pas de données filtrées.")

            with col_pie:
                st.markdown("<h3 style='color: #007bad;'>Transactions Acceptées vs Refusées</h3>", unsafe_allow_html=True)
                if 'SHORT_MESSAGE' in filtered_recolts.columns and 'Total_Recolt' in filtered_recolts.columns and not filtered_recolts['SHORT_MESSAGE'].empty:
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
                    st.warning("Données de message court ou de récolte totale manquantes pour ce graphique ou pas de données filtrées.")

            with col_hour:
                st.markdown("<h3 style='color: #007bad;'>Récoltes par Heure (9h-20h)</h3>", unsafe_allow_html=True)
                if 'ORDER_DATE' in filtered_recolts.columns and not filtered_recolts['ORDER_DATE'].empty:
                    recoltes_heure = filtered_recolts[
                        (filtered_recolts['ORDER_DATE'].dt.hour >= 9) &
                        (filtered_recolts['ORDER_DATE'].dt.hour <= 20)
                    ].groupby(filtered_recolts['ORDER_DATE'].dt.hour)['Total_Recolt'].sum().reset_index()

                    recoltes_heure = recoltes_heure.rename(columns={'ORDER_DATE': 'Heure'})
                    all_hours = pd.DataFrame({'Heure': range(9, 21)}) # Inclure toutes les heures même si pas de données
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
                    st.warning("Données de date de commande manquantes pour ce graphique ou pas de données filtrées.")
        else:
            st.warning("Aucune donnée de récolte ne correspond aux filtres sélectionnés.")

# --- Fonction Principale de la Page des Logs ---

def logs_page(logs_df, staff_df, start_date, end_date):
    

    add_custom_css() 

    st.markdown("<h3 style='color: #007bad;'>Filtrage des Logs</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        col1, col2, col3, col4,col5, col6, col7, col8 = st.columns(8)
        with col1:
            offre_filter = st.selectbox("Offres", ['Tous'] + sorted(logs_df['Offre'].dropna().unique().tolist()) if 'Offre' in logs_df.columns else ['Tous'], key='logs_offre_top')
        with col2:
            team_filter = st.selectbox("Equipes", ['Toutes'] + sorted(staff_df['Team'].dropna().unique().tolist()), key='logs_team')
        with col3:
            activity_filter = st.selectbox("Activités", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique().tolist()), key='logs_activity')
        with col4:
            segment_filter = st.selectbox("Segments", ['Tous'] + sorted(logs_df['Segment'].dropna().unique().tolist()) if 'Segment' in logs_df.columns else ['Tous'], key='segment_filter')

        
        with col5:
            statut_bp_filter = st.selectbox("Statut BP", ['Tous'] + sorted(logs_df['Statut_BP'].dropna().unique().tolist()) if 'Statut_BP' in logs_df.columns else ['Tous'], key='statut_bp_filter')
        with col6:
            canal_filter = st.selectbox("Canal", ['Tous'] + sorted(logs_df['Canal'].dropna().unique().tolist()) if 'Canal' in logs_df.columns else ['Tous'], key='canal_filter')
        with col7:
            direction_filter = st.selectbox("Direction", ['Tous'] + sorted(logs_df['Direction'].dropna().unique().tolist()) if 'Direction' in logs_df.columns else ['Tous'], key='direction_filter')
        with col8:
            qualification_filter = st.selectbox("Qualification", ['Tous'] + sorted(logs_df['Qualification'].dropna().unique().tolist()) if 'Qualification' in logs_df.columns else ['Tous'], key='qualification_filter')

    with st.spinner("Application des filtres..."):
        # Assurez-vous que la colonne 'ORDER_DATE' existe pour filter_data
        # Pour les logs, la colonne de date peut être 'Date_d_création'
        logs_df_for_filter = logs_df.copy()
        if 'Date_d_création' in logs_df_for_filter.columns and 'ORDER_DATE' not in logs_df_for_filter.columns:
            logs_df_for_filter = logs_df_for_filter.rename(columns={'Date_d_création': 'ORDER_DATE'})
            
        try:
            # La fonction filter_data est conçue pour les ventes/récoltes avec 'Country' et 'SHORT_MESSAGE'
            # Adaptons son appel pour les logs
            filtered_logs = filter_data(
                logs_df_for_filter, # Utilisation de logs_df_for_filter avec 'ORDER_DATE'
                'Tous', # Pas de filtre 'Country' spécifique pour les logs ici, mais 'filter_data' l'attend
                team_filter, 
                activity_filter, 
                'Toutes', # Pas de filtre 'transaction' spécifique pour les logs ici, mais 'filter_data' l'attend
                start_date, 
                end_date, 
                staff_df
            )
            # Renommer 'ORDER_DATE' si nécessaire pour les logs si elle a été changée pour 'filter_data'
            if 'Date_d_création' in logs_df.columns and 'ORDER_DATE' in filtered_logs.columns and 'Date_d_création' not in filtered_logs.columns:
                filtered_logs = filtered_logs.rename(columns={'ORDER_DATE': 'Date_d_création'})
        except NameError:
            st.warning("La fonction `filter_data` n'a pas été trouvée. Utilisation d'un filtre de date basique pour la démonstration.")
            if 'Date_d_création' in logs_df.columns:
                logs_df['Date_d_création'] = pd.to_datetime(logs_df['Date_d_création'], errors='coerce')
                filtered_logs = logs_df[(logs_df['Date_d_création'] >= start_date) & (logs_df['Date_d_création'] <= end_date)].copy()
            else:
                filtered_logs = logs_df.copy() # Pas de filtre de date si la colonne est manquante


        # Appliquer les filtres spécifiques aux logs
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
        #st.markdown("<h3 style='color: #007bad;'>Indicateurs Clés des Logs</h3>", unsafe_allow_html=True)

        total_logs_count = len(filtered_logs)
        total_unique_offres_count = filtered_logs['Offre'].nunique() if 'Offre' in filtered_logs.columns else 0

        # Calcul du taux de conversion
        if 'Direction' in filtered_logs.columns:
            incoming = len(filtered_logs[filtered_logs['Direction'] == 'InComming'])
            outgoing = len(filtered_logs[filtered_logs['Direction'] == 'OutComming'])
            conversion_rate = (outgoing / incoming * 100) if incoming > 0 else 0
        else:
            conversion_rate = "N/A"

        # Calcul du taux de Statut BP
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

        # Période Couverte
        if 'Date_d_création' in filtered_logs.columns and not filtered_logs['Date_d_création'].empty:
            filtered_logs['Date_d_création'] = pd.to_datetime(filtered_logs['Date_d_création'], errors='coerce')
            min_date = filtered_logs['Date_d_création'].min()
            max_date = filtered_logs['Date_d_création'].max()
            days = (max_date - min_date).days if pd.notna(min_date) and pd.notna(max_date) else "N/A"
        else:
            days = "N/A"

        # Affichage des cartes KPI avec kpi_card_html
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            kpi_card_html(col1, "Total Logs", f"{total_logs_count:,}", "#007bad", "clipboard-list")

        with col2:
            kpi_card_html(col2, "Offres Uniques", f"{total_unique_offres_count:,}", "#2596be", "tag")

        with col3:
            conversion_display = f"{conversion_rate:.1f}%" if isinstance(conversion_rate, (int, float)) else conversion_rate
            kpi_card_html(col3, "Taux de Conversion", conversion_display, "#ffc107", "chart-pie")

        with col4:
            bp_display = f"{bp_rate:.1f}%" if isinstance(bp_rate, (int, float)) else bp_rate
            kpi_card_html(col4, "Taux Statut BP", bp_display, "#fc9307", "clipboard-check")
            
        with col5:
            days_display = f"{days} jours" if days != "N/A" else "N/A"
            kpi_card_html(col5, "Période Couverte", days_display, "#043a64", "calendar-alt")

        #st.markdown("---")
        st.markdown("<h3 style='color: #007bad;'>Analyse des Logs</h3>", unsafe_allow_html=True)
        with st.container(border=True):
    # First row of charts (formerly second row): Qualification/Direction (col1), Mode de Facturation (col2)
  
            col1, col2 = st.columns([3, 1.1])
            with col1:
                st.markdown("<h4 style='color: #007bad;'>Tendance des Qualifications et Directions par Mois</h4>", unsafe_allow_html=True)
                if 'Qualification' in filtered_logs.columns and 'Direction' in filtered_logs.columns and 'Date_d_création' in filtered_logs.columns and not filtered_logs.empty:
                    filtered_logs['Date_d_création'] = pd.to_datetime(filtered_logs['Date_d_création'], errors='coerce')
                    df_combined = filtered_logs.dropna(subset=['Qualification', 'Direction', 'Date_d_création'])

                    if not df_combined.empty:
                        # Filtrer pour garder seulement les 12 derniers mois
                        df_combined = df_combined[df_combined['Date_d_création'] >= (df_combined['Date_d_création'].max() - pd.DateOffset(months=11))]
                        
                        df_combined['Qualification_Grouped'] = df_combined['Qualification'].apply(
                            lambda x: 'Transfert' if 'Transfert' in x else x
                        )
                        
                        df_combined['Month_Year_Str'] = df_combined['Date_d_création'].dt.to_period('M').astype(str)
                        df_combined['Month_Year_Dt'] = df_combined['Date_d_création'].dt.to_period('M').dt.to_timestamp()

                        qualification_monthly_counts = df_combined.groupby(['Month_Year_Str', 'Month_Year_Dt', 'Qualification_Grouped']).size().reset_index(name='Count')
                        qualification_monthly_counts = qualification_monthly_counts.sort_values('Month_Year_Dt')

                        direction_monthly_counts = df_combined.groupby(['Month_Year_Str', 'Month_Year_Dt', 'Direction']).size().reset_index(name='Count')
                        direction_monthly_counts = direction_monthly_counts.sort_values('Month_Year_Dt')

                        fig = make_subplots(specs=[[{"secondary_y": True}]])

                        qualification_colors = {
                            'Question': '#1f77b4',
                            'Suivi de souscription FOP': '#ff7f0e',
                            'Demande': '#2ca02c',
                            'Transfert': '#d62728'
                        }

                        sorted_qualifications = sorted(qualification_monthly_counts['Qualification_Grouped'].unique(), 
                                                    key=lambda x: (x != 'Question', x != 'Suivi de souscription FOP', 
                                                                    x != 'Demande', x != 'Transfert'))

                        for qual in sorted_qualifications:
                            if qual in ['Question', 'Suivi de souscription FOP', 'Demande', 'Transfert']:
                                df_qual = qualification_monthly_counts[qualification_monthly_counts['Qualification_Grouped'] == qual]
                                fig.add_trace(
                                    go.Scatter(
                                        x=df_qual['Month_Year_Dt'],
                                        y=df_qual['Count'],
                                        mode='lines+markers',
                                        name=f'Qualification: {qual}',
                                        line=dict(width=3, color=qualification_colors.get(qual, '#7f7f7f')),
                                        marker=dict(size=20),
                                        hovertemplate=f'Mois: %{{x|%B %Y}}<br>Qualification: {qual}<br>Logs: %{{y}}<extra></extra>'
                                    ),
                                    secondary_y=False,
                                )

                        direction_pivot = direction_monthly_counts.pivot(index='Month_Year_Dt', columns='Direction', values='Count').fillna(0).reset_index()
                        direction_pivot = direction_pivot.sort_values('Month_Year_Dt')

                        direction_pivot['Total'] = direction_pivot.sum(axis=1, numeric_only=True)
                        
                        if 'InComming' in direction_pivot.columns:
                            direction_pivot['InComming_Pct'] = (direction_pivot['InComming'] / direction_pivot['Total'] * 100).round(1)
                            fig.add_trace(
                                go.Bar(
                                    x=direction_pivot['Month_Year_Dt'],
                                    y=direction_pivot['InComming'],
                                    name='Direction: InComming',
                                    marker_color='#FFD700',
                                    opacity=0.9,
                                    text=direction_pivot.apply(lambda x: f"{int(x['InComming'])} ({x['InComming_Pct']}%)", axis=1),
                                    textposition='outside',
                                    textfont=dict(size=16, color='navy', family='Arial', weight='bold'),
                                    hovertemplate='Mois: %{x|%B %Y}<br>Direction: InComming<br>Logs: %{y}<extra></extra>'
                                ),
                                secondary_y=True,
                            )
                        if 'OutComming' in direction_pivot.columns:
                            direction_pivot['OutComming_Pct'] = (direction_pivot['OutComming'] / direction_pivot['Total'] * 100).round(1)
                            fig.add_trace(
                                go.Bar(
                                    x=direction_pivot['Month_Year_Dt'],
                                    y=direction_pivot['OutComming'],
                                    name='Direction: OutComming',
                                    marker_color='#8A2BE2',
                                    opacity=0.9,
                                    text=direction_pivot.apply(lambda x: f"{int(x['OutComming'])} ({x['OutComming_Pct']}%)", axis=1),
                                    textposition='outside',
                                    textfont=dict(size=16, color='navy', family='Arial', weight='bold'),
                                    hovertemplate='Mois: %{x|%B %Y}<br>Direction: OutComming<br>Logs: %{y}<extra></extra>'
                                ),
                                secondary_y=True,
                            )

                        # Générer les valeurs des ticks pour chaque mois
                        month_ticks = pd.date_range(
                            start=df_combined['Month_Year_Dt'].min(), 
                            end=df_combined['Month_Year_Dt'].max(), 
                            freq='MS'
                        )

                        fig.update_layout(
                            xaxis=dict(
                                tickfont=dict(size=16, family='Arial', color='black', weight='bold'),
                                tickformat="%B",  # Noms complets des mois
                                tickangle=0,      # Horizontal
                                tickmode='array', # Mode tableau pour contrôle précis
                                tickvals=month_ticks,  # Positions des ticks
                                range=[month_ticks[0] - pd.DateOffset(days=15),  # Marge avant
                                        month_ticks[-1] + pd.DateOffset(days=15)] # Marge après
                            ),
                            margin=dict(l=20, r=20, t=80, b=100),
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font=dict(color='black'),
                            hovermode="x unified",
                            barmode='stack',
                            showlegend=False
                            
                        )
                        # Ajouter cette partie après st.plotly_chart(fig, use_container_width=True)

                        
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown("""
                        <div style="margin-top: -50px; text-align: left;">
                            <p style="font-size: 14px; color: #555;">
                                <span style="color: #1f77b4; font-weight: bold;">● Question</span> | 
                                <span style="color: #ff7f0e; font-weight: bold;">● Suivi FOP</span> | 
                                <span style="color: #2ca02c; font-weight: bold;">● Demande</span> | 
                                <span style="color: #d62728; font-weight: bold;">● Transfert</span> | 
                            </p>
                            <p>
                                <span style="color: #FFD700; font-weight: bold;">■ InComming</span> | 
                                <span style="color: #8A2BE2; font-weight: bold;">■ OutComming</span>
                            </p>
                            
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("Données de qualification, direction ou date non valides pour ce graphique.")
                else:
                    st.warning("Colonnes 'Qualification', 'Direction' ou 'Date_d_création' manquantes ou vides pour ce graphique.")

          
        

            with col2:
                st.markdown("<h4 style='color: #007bad;'>Répartition par Mode de Facturation</h4>", unsafe_allow_html=True)
                if 'Mode_facturation' in filtered_logs.columns and not filtered_logs['Mode_facturation'].empty:
                    billing_mode_counts = filtered_logs['Mode_facturation'].value_counts().reset_index()
                    billing_mode_counts.columns = ['Mode_facturation', 'Count']
                    total = billing_mode_counts['Count'].sum()
                    
                    # Calcul des montants en euros
                    montants = {}
                    if 'Montant' in filtered_logs.columns:
                        for mode in billing_mode_counts['Mode_facturation']:
                            montants[mode] = filtered_logs[filtered_logs['Mode_facturation'] == mode]['Montant'].sum()
                    else:
                        # Valeurs factices si la colonne Montant n'existe pas
                        for mode in billing_mode_counts['Mode_facturation']:
                            montants[mode] = billing_mode_counts[billing_mode_counts['Mode_facturation'] == mode]['Count'].values[0] * 1000
                    
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=billing_mode_counts['Mode_facturation'],
                        values=billing_mode_counts['Count'],
                        hole=.4,
                        pull=[0.05 if i == billing_mode_counts['Count'].argmax() else 0 for i in range(len(billing_mode_counts))],
                        marker_colors=px.colors.qualitative.Set3,
                        textinfo='percent+label',
                        texttemplate='%{label}<br>%{percent}<br>%{customdata:,.0f}€',
                        customdata=[montants.get(mode, 0) for mode in billing_mode_counts['Mode_facturation']],
                        insidetextfont=dict(size=16, color='Black', family='Arial', weight='bold'),
                        outsidetextfont=dict(size=16, color='black', family='Arial', weight='bold'),
                        hovertemplate='Mode: %{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                    )])

                    fig_pie.update_layout(
                        margin=dict(l=20, r=20, t=50, b=20),
                        showlegend=False,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='black'),
                        uniformtext_minsize=12,
                        uniformtext_mode='hide'
                    )
                    
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.warning("Données non disponibles pour ce graphique (Mode de Facturation)")
           
            col1, col2, col3 = st.columns(3)

       
            with col1:
                st.markdown("<h4 style='color: #007bad;'>Répartition par Canal</h4>", unsafe_allow_html=True)
                if 'Canal' in filtered_logs.columns and not filtered_logs['Canal'].empty:
                    canal_counts = filtered_logs['Canal'].value_counts().reset_index()
                    canal_counts.columns = ['Canal', 'Count']
                    total = canal_counts['Count'].sum()
                    canal_counts['Percentage'] = (canal_counts['Count'] / total * 100).round(1)
                    
                    fig1 = px.bar(
                        canal_counts,
                        x='Count',
                        y='Canal',
                        orientation='h',
                        color='Canal',
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                    )
                    fig1.update_traces(
                        texttemplate='%{x} (%{customdata[0]}%)',
                        textposition='outside',
                        customdata=canal_counts[['Percentage']],
                        textfont=dict(size=16, color='black', family='Arial', weight='bold') # Adjusted font size
                    )
                    fig1.update_layout(
                        xaxis_title={
                            'text': "Nombre de Logs",
                            'font': {'size': 16, 'color': 'black', 'family': 'Arial', 'weight': 'bold'} # Adjusted font size
                        },
                        yaxis_title={
                            'text': "Canal",
                            'font': {'size': 16, 'color': 'black', 'family': 'Arial', 'weight': 'bold'} # Adjusted font size
                        },
                        xaxis=dict(
                            tickfont=dict(size=14, family='Arial', color='black', weight='bold') # Adjusted font size
                        ),
                        yaxis=dict(
                            tickfont=dict(size=14, family='Arial', color='black', weight='bold') # Adjusted font size
                        ),
                        margin=dict(l=30, r=20, t=50, b=20),
                        showlegend=False,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='black'),
                        bargap=0.3
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.warning("Données non disponibles pour ce graphique (Canal)")

            # Chart 3: Logs Over Time (Line Chart) - now in col2 (bottom center)
            with col2:
                st.markdown("<h4 style='color: #007bad;'>Volume de Logs au Fil du Temps</h4>", unsafe_allow_html=True)
                if 'Date_d_création' in filtered_logs.columns and not filtered_logs['Date_d_création'].empty:
                    daily_counts = filtered_logs['Date_d_création'].dt.to_period('D').value_counts().sort_index().reset_index()
                    daily_counts.columns = ['Date', 'Count']
                    daily_counts['Date'] = daily_counts['Date'].dt.to_timestamp()
                    
                    fig3 = px.line(
                        daily_counts,
                        x='Date',
                        y='Count',
                    )
                    fig3.update_traces(
                        mode='lines+markers',
                        marker=dict(size=8),
                    )
                    fig3.update_layout(
                        xaxis_title={
                            'text': "Date",
                            'font': {'size': 16, 'color': 'black', 'family': 'Arial', 'weight': 'bold'}
                        },
                        yaxis_title={
                            'text': "Nombre de Logs",
                            'font': {'size': 16, 'color': 'black', 'family': 'Arial', 'weight': 'bold'}
                        },
                        xaxis=dict(
                            tickfont=dict(size=14, family='Arial', color='black', weight='bold'),
                            tickformat="%b %Y"
                        ),
                        yaxis=dict(
                            tickfont=dict(size=14, family='Arial', color='black', weight='bold')
                        ),
                        margin=dict(l=20, r=20, t=50, b=20),
                        showlegend=False,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='black')
                    )
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.warning("Données non disponibles pour ce graphique (Date de création)")

            # Chart 2: Logs by Offer (Horizontal Bar Chart) - now in col3 (bottom right)
            with col3:
                st.markdown("<h4 style='color: #007bad;'>Répartition par Offre</h4>", unsafe_allow_html=True)
                if 'Offre' in filtered_logs.columns and not filtered_logs['Offre'].empty:
                    offre_counts = filtered_logs['Offre'].value_counts().reset_index()
                    offre_counts.columns = ['Offre', 'Count']
                    total = offre_counts['Count'].sum()
                    offre_counts['Percentage'] = (offre_counts['Count'] / total * 100).round(1)
                    
                    fig2 = px.bar(
                        offre_counts,
                        x='Count',
                        y='Offre',
                        orientation='h',
                        color='Offre',
                        color_discrete_sequence=px.colors.qualitative.Set2,
                    )
                    fig2.update_traces(
                        texttemplate='%{x} (%{customdata[0]}%)',
                        textposition='outside',
                        customdata=offre_counts[['Percentage']],
                        textfont=dict(size=14, color='black', family='Arial', weight='bold')
                    )
                    fig2.update_layout(
                        xaxis_title={
                            'text': "Nombre de Logs",
                            'font': {'size': 16, 'color': 'black', 'family': 'Arial', 'weight': 'bold'}
                        },
                        yaxis_title={
                            'text': "Offre",
                            'font': {'size': 16, 'color': 'black', 'family': 'Arial', 'weight': 'bold'}
                        },
                        xaxis=dict(
                            tickfont=dict(size=14, family='Arial', color='black', weight='bold')
                        ),
                        yaxis=dict(
                            tickfont=dict(size=14, family='Arial', color='black', weight='bold')
                        ),
                        margin=dict(l=20, r=20, t=50, b=20),
                        showlegend=False,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='black'),
                        bargap=0.3
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("Données non disponibles pour ce graphique (Offre)")

    
        st.markdown("<h3 style='color: #007bad;'>Données Détaillées des Logs</h3>", unsafe_allow_html=True)

        display_df = filtered_logs.sort_values('Date_d_création', ascending=False).copy()

        columns_to_drop = ['Id_Log', 'Day_of_Week', 'Month_Year', 'Sort_Key', 'Month_Year_Str', 'Month_Year_Dt', 'ORDER_DATE','BP_Logs']
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
            "Mode_facturation": st.column_config.Column("Mode de Facturation", width="medium"),
        }

        existing_columns_configs = {col: config for col, config in column_configs.items() if col in display_df.columns}

        st.dataframe(
            display_df,
            column_config=existing_columns_configs,
            hide_index=True,
            use_container_width=False,
            height=400,
        )
        
        # Add download button for Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            filtered_logs.to_excel(writer, index=False, sheet_name='Logs Data')
        excel_buffer.seek(0)

        st.download_button(
            label="Télécharger en Excel",
            data=excel_buffer,
            file_name="logs_filtered_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Cliquez ici pour télécharger les données filtrées au format Excel."
        )
    else:
        st.warning("Aucune donnée disponible avec les filtres sélectionnés. Veuillez ajuster vos sélections.")


def kpi_card_html(column, title, value_html, color, icon_name):
    column.markdown(f"""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        <div style="
            padding: 20px;
            background: linear-gradient(145deg, {color} 0%, {color}CC 100%);
            border-radius: 12px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.15);
            height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            border-left: 8px solid {color}EE;
            position: relative;
            overflow: hidden;
            color: white;">
            <div style="position: absolute; right: 20px; top: 20px; opacity: 0.9;">
                <i class="fas fa-{icon_name}" style="font-size: 40px;"></i>
            </div>
            <h3 style="color: white; margin: 0 0 10px 0; font-size: 24px; font-weight: 600;">{title}</h3>
            <p style="font-size: 28px; color: white; font-weight: 700; margin: 0;">{value_html}</p>
        </div>
    """, unsafe_allow_html=True)

def sales_page(sales_df, staff_df, start_date, end_date):
    

    add_custom_css()  # Appel de la fonction CSS personnalisée

    st.markdown("<h3 style='color: #007bad;'>Filtrage des Ventes</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        with col1:
            country_filter = st.selectbox("Pays", ['Tous'] + sorted(sales_df['Country'].dropna().unique()), key='sales_country')
        with col2:
            team_filter = st.selectbox("Equipes", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()), key='sales_team')
        with col3:
            activity_filter = st.selectbox("Activités", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()), key='sales_activity')
        with col4:
            transaction_filter = st.selectbox("Transactions", ['Toutes'] + sorted(sales_df['SHORT_MESSAGE'].dropna().unique()), key='sales_transaction')

        filtered_sales = filter_data(sales_df, country_filter, team_filter, activity_filter, transaction_filter, start_date, end_date, staff_df)

    if not filtered_sales.empty:
        if 'City' in filtered_sales.columns and 'Country' in filtered_sales.columns:
            filtered_sales = geocode_data(filtered_sales)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            kpi_card_html(col1, "Total Sales", f"{filtered_sales['Total_Sale'].sum():,.0f}€", "#043a64", "chart-line")

        with col2:
            kpi_card_html(col2, "Average Sale", f"{filtered_sales['Total_Sale'].mean():,.2f}€", "#fcce22", "money-bill-wave")

        with col3:
            if 'Rating' in filtered_sales.columns:
                avg_rating = filtered_sales['Rating'].mean()
                rating_display = f"{'★' * int(round(avg_rating))}{'☆' * (7 - int(round(avg_rating)))}"
                kpi_card_html(col3, "Average Rating", rating_display, "#fc9307", "smile")
            else:
                kpi_card_html(col3, "Average Rating", "N/A", "#fcce22", "star-half-alt")

        with col4:
            kpi_card_html(col4, "Transactions", f"{len(filtered_sales):,}", "#102831", "exchange-alt")

        # The rest of your sales_page function remains the same
        # ... (map, team performance, daily sales, transaction status, hourly sales)
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
                        height=630,
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
                                <div class="team-performance-card" style="padding: 10px;">
                                    <div class="team-performance-title" style="font-size: 30px; font-weight: bold;">{row['Team']}</div>
                                    <div class="team-stat-row" style="display: flex; justify-content: space-between; align-items: center;">
                                        <div style="flex: 1; text-align: left;">
                                            <div class="team-stat-label" style="font-weight: bold; color: #fc6c04;">VENTES TOTALES:</div>
                                            <div class="team-stat-value" style="font-size: 38px; font-weight: bold;">{row['Total_Sale']:,.0f}€</div>
                                        </div>
                                        <div style="flex: 1; text-align: center;">
                                            <div class="team-stat-label" style="font-weight: bold; color: #fc6c04;">TAUX CONVERSION:</div>
                                            <div class="team-conversion-value" style="font-size: 38px; font-weight: bold;">{row['Conversion_Rate']:.2f}%</div>
                                        </div>
                                        <div style="flex: 1; text-align: right;">
                                            <div class="team-stat-label" style="font-weight: bold; color: #fc6c04;">TRANSACTIONS:</div>
                                            <div class="team-stat-value" style="font-size: 38px; font-weight: bold;">{row['Total_Transactions']:,}</div>
                                        </div>
                                    </div>
                                    <div style="display: flex; justify-content: right; margin-top: 5px; gap: 10px; font-size: 20px; font-weight: bold;">
                                        <span style="color: green;">✓ {row['Acceptance_Rate']:.1f}%</span>
                                        <span style="color: red;">✗ {row['Refusal_Rate']:.1f}%</span>
                                        <span style="color: orange;">⚠ {row['Error_Rate']:.1f}%</span>
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

        # Calcul de la durée
        duration = end_date - start_date
        total_days = duration.days

        # Calcul des mois et jours
        # Une estimation simple des mois (30 jours par mois)
        months = total_days // 30
        remaining_days = total_days % 30

        duration_text = ""
        if months > 0:
            duration_text += f"{months} Mois "
        duration_text += f"{remaining_days} jours"


        st.markdown(
            f"""
            <h1 style='text-align: left; font-size: 2.1em; margin-bottom: 0; color: #002a48;'>
                Dashboard du
                <span style='color: #00afe1;'>{start_formatted}</span> au
                <span style='color: #00afe1;'>{end_formatted}</span>
                <span style='font-size: 0.7em; color: #555;'>({duration_text})</span>
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

    st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-weight: bold;
            color: #0a7fac;
            font-size: 1.9em
        }
    </style>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Logs Analytics", "Sales Analytics", "Recolts Analytics"])


    
    with tab1:
        logs_page(logs_df, staff_df, start_date, end_date)
        
    
    with tab2:
        sales_page(sales_df, staff_df, start_date, end_date)
    with tab3:
        recolts_page(recolts_df, staff_df, start_date, end_date)



def planning_page(sales_df, staff_df):
    """Affiche la page de planning."""
    st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Planning</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #007bad; margin-top: 0;'>All Teams</h2>", unsafe_allow_html=True)
    
    
    

    if sales_df.empty:
        st.warning("Aucune donnée de vente disponible.")
        return
    
    selected_country = st.selectbox("Pays", sorted(sales_df['Country'].dropna().unique()), key='country_filter')
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



def get_last_agent_id():
    """
    Récupère le dernier ID_Effectifs (numérique) de la table Effectifs pour en générer un nouveau.
    """
    conn = get_db_connection()
    if not conn:
        return 0 # Return 0 or handle error appropriately
    
    try:
        with closing(conn.cursor()) as cursor:
            # This query assumes ID is always a number and gets the max
            cursor.execute("SELECT MAX(ID) FROM Effectifs")
            last_id = cursor.fetchone()[0]
            # Convert to integer, as some drivers might return it as a string
            return int(last_id) if last_id is not None else 0
    except sqlite3.Error as e:
        st.error(f"Erreur lors de la récupération du dernier ID d'agent : {e}")
        return 0
    # The ValueError handling for 'invalid literal for int()' would become unnecessary if data is clean
    except ValueError as e: 
        st.error(f"Erreur de conversion de l'ID en entier (cette erreur ne devrait plus apparaître après nettoyage DB) : {e}")
        return 0
    finally:
        conn.close()
def get_last_agent_id():
    
    conn = get_db_connection()
    if not conn:
        return 0 
    
    max_id_trouve = 0 
    
    try:
        with closing(conn.cursor()) as cursor:
            
            cursor.execute("SELECT Id_Effectif FROM Effectifs")
            all_ids = cursor.fetchall() # Récupère tous les résultats

            for row in all_ids:
                current_id = row[0] # L'ID est le premier élément de chaque ligne
                
                if current_id is None:
                    continue # Ignore les valeurs NULL

                try:
                    # Tente de convertir l'ID actuel en entier
                    numeric_id = int(current_id)
                    # Si la conversion réussit, compare-le avec le maximum trouvé jusqu'à présent
                    if numeric_id > max_id_trouve:
                        max_id_trouve = numeric_id
                except ValueError:
                    # Cette erreur se produit si current_id n'est pas un nombre (ex: 'SRP_098')
                    # Nous l'ignorons silencieusement car nous voulons seulement les IDs numériques
                    st.warning(f"ID non numérique ignoré lors de la recherche du dernier ID : '{current_id}'")
                    pass
                except TypeError:
                    # Gère les cas où current_id n'est ni un str ni un int (ex: un objet non convertible)
                    st.warning(f"Type d'ID inattendu ignoré : '{current_id}' ({type(current_id)})")
                    pass
            
            return max_id_trouve # Retourne le plus grand ID numérique trouvé

    except sqlite3.Error as e:
        st.error(f"Erreur SQLite lors de la récupération des IDs d'agent : {e}")
        return 0
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue dans get_last_agent_id : {e}")
        return 0
    finally:
        conn.close()


def add_agent_to_db(agent_data):
    """
    Ajoute un nouvel agent à la table Effectifs et un utilisateur à la table Users.
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with closing(conn.cursor()) as cursor:
            # Insert into Effectifs table
            cursor.execute(
                """INSERT INTO Effectifs (Id_Effectif, Hyp, ID_AGTSDA, NOM, PRENOM, Team, Type, Activité, Departement, Date_In)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (agent_data["Id_Effectif"], agent_data["Hyp"], agent_data["ID_AGTSDA"], agent_data["NOM"], 
                 agent_data["PRENOM"], agent_data["Team"], agent_data["Type"], 
                 agent_data["Activité"], agent_data["Departement"], agent_data["Date_In"])
            )
            
            # Insert into Users table (assuming UserName and Hyp are also in Users table)
            # You might need to adjust this based on your Users table schema, especially for 'Cnx' and 'PassWord'
            cursor.execute(
                """INSERT INTO Users (Hyp, UserName, PassWord, Type_User, Cnx)
                   VALUES (?, ?, ?, ?, ?)""",
                (agent_data["Hyp"], agent_data["UserName"], agent_data["Hyp"], # Default password is Hyp
                 agent_data["Type"], None) # Assuming Type from Effectifs and Cnx is null or needs a default
            )
            
            conn.commit()
            return True
    except sqlite3.Error as e:
        st.error(f"Erreur lors de l'ajout de l'agent à la base de données : {e}")
        return False
    finally:
        conn.close()


def setting_page():
    
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

 
    with st.container():
        st.markdown("---")
        st.subheader("Rechercher un utilisateur existant")
        hyp_input = st.text_input("**Entrez l'ID (Hyp) de l'utilisateur**", 
                                  placeholder="Saisir l'identifiant Hyp...",
                                  help="Rechercher un utilisateur par son identifiant unique")
    
    if hyp_input:
        user_details = get_user_details(hyp_input) 
        
        if user_details:
            date_in = user_details["Date_In"] 
            date_obj = None
            date_str = "Date inconnue"
            anciennete = "N/A"
            
            if date_in:  
                if isinstance(date_in, str):
                    date_formats = [
                        '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', 
                        '%Y-%m-%d %H:%M:%S', '%d-%m-%Y', '%Y%m%d'     
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
                elif isinstance(date_in, (datetime, datetime.date)):  
                    date_obj = date_in
            
            if date_obj:
                try:
                    anciennete = (datetime.now().date() - date_obj.date()).days // 365
                    date_str = date_obj.strftime('%d/%m/%Y')
                except AttributeError:
                    pass
            
            with st.expander(f"🔍 Fiche utilisateur : {user_details['NOM']} {user_details['PRENOM']}", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 15px;'>
                        <h3 style='color: #002a48; border-bottom: 1px solid #dee2e6; padding-bottom: 10px;'>Informations Professionnelles</h3>
                        <p><strong>Nom:</strong> {user_details['NOM']}</p>
                        <p><strong>Prénom:</strong> {user_details['PRENOM']}</p>
                        <p><strong>Date d'entrée:</strong> {date_str}</p>
                        <p><strong>Ancienneté:</strong> {anciennete} {"an" if isinstance(anciennete, int) and anciennete == 1 else "ans" if isinstance(anciennete, int) else ""}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 15px;'>
                        <h3 style='color: #002a48; border-bottom: 1px solid #dee2e6; padding-bottom: 10px;'>Détails</h3>
                        <p><strong>Team:</strong> {user_details['Team']}</p>
                        <p><strong>Type:</strong> {user_details['Type']}</p>
                        <p><strong>Activité:</strong> {user_details['Activité']}</p>
                        <p><strong>Nom d'utilisateur:</strong> {user_details['UserName']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
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
            
    st.markdown("---")
    st.subheader("Options de gestion")
    
    selected_option = st.selectbox(
        "Sélectionnez une action :",
        ["-- Choisir une option --", "Ajouter un Agent", "Injecter des logs", "Injecter des sales", "Injecter des récoltes"]
    )

    if selected_option == "Ajouter un Agent":
        st.markdown("---")
        st.subheader("Ajouter un nouvel Agent")

        next_id = get_last_agent_id() + 1
        st.info(f"Le prochain ID d'Agent sera automatiquement attribué : **{next_id}**")

      
        teams = ["-- Sélectionner --"] + get_unique_values("Team")
        activites = ["-- Sélectionner --"] + get_unique_values("Activité")
        types = ["-- Sélectionner --"] + get_unique_values("Type")
        departements = ["-- Sélectionner --"] + get_unique_values("Departement")

        with st.form("add_agent_form"):
            col_form1, col_form2 = st.columns(2)
            with col_form1:
                hyp = st.text_input("ID (Hyp)", placeholder="Ex: HYP001", help="Identifiant unique de l'agent (Hyp)", key="agent_hyp")
                id_agtsda = st.text_input("ID_AGTSDA", placeholder="Ex: AGT123", help="Identifiant AGTSDA de l'agent", key="agent_id_agtsda")
                nom = st.text_input("NOM", placeholder="Ex: DUPONT", help="Nom de l'agent", key="agent_nom")
                
                
                team = st.selectbox("Team", options=teams, help="Équipe de l'agent", key="agent_team_select")
                activite = st.selectbox("Activité", options=activites, help="Activité principale de l'agent", key="agent_activite_select")

            with col_form2:
                username = st.text_input("UserName", placeholder="Ex: jean.dupont", help="Nom d'utilisateur pour la connexion", key="agent_username")
                prenom = st.text_input("PRENOM", placeholder="Ex: Jean", help="Prénom de l'agent", key="agent_prenom")
                type_agent = st.selectbox("Type", options=types, help="Type de contrat ou statut de l'agent", key="agent_type_select")
                departement = st.selectbox("Département", options=departements, help="Département de l'agent", key="agent_departement_select")
                date_in = st.date_input("Date d'entrée", help="Date d'entrée de l'agent", value=datetime.now().date(), key="agent_date_in")
            
            st.markdown("---")
            col_buttons = st.columns(2)
            with col_buttons[0]:
                submitted = st.form_submit_button("**Enregistrer**", type="primary")
            with col_buttons[1]:
                cancelled = st.form_submit_button("**Annuler**")

            if submitted:
                
                
                if any(val == "-- Sélectionner --" for val in [team, type_agent, activite, departement]):
                    st.error("Veuillez sélectionner une option valide pour les champs Team, Type, Activité et Département.")
                elif not all([hyp, id_agtsda, username, nom, prenom, date_in]):
                    st.error("Veuillez remplir tous les champs obligatoires (texte).")
                else:
                    agent_data = {
                        "Id_Effectif": next_id,
                        "Hyp": hyp,
                        "ID_AGTSDA": id_agtsda,
                        "UserName": username,
                        "NOM": nom,
                        "PRENOM": prenom,
                        "Team": team,
                        "Type": type_agent,
                        "Activité": activite,
                        "Departement": departement,
                        "Date_In": date_in.strftime('%Y-%m-%d')
                    }
                    if add_agent_to_db(agent_data):
                        st.success(f"L'agent **{nom} {prenom}** a été ajouté avec succès avec l'ID **{next_id}** !")
                        st.experimental_rerun()
                    else:
                        st.error("Une erreur est survenue lors de l'ajout de l'agent.")
            elif cancelled:
                st.info("Ajout de l'agent annulé.")
                

    elif selected_option == "Injecter des logs":
        st.markdown("---")
        st.subheader("Injecter des données de Logs")
        st.info("Cette section est dédiée à l'injection de données de logs. Développez l'interface ici.")

    elif selected_option == "Injecter des sales":
        st.markdown("---")
        st.subheader("Injecter des données de Ventes")
        st.info("Cette section est dédiée à l'injection de données de ventes. Développez l'interface ici.")

    elif selected_option == "Injecter des récoltes":
        st.markdown("---")
        st.subheader("Injecter des données de Récoltes")
        st.info("Cette section est dédiée à l'injection de données de récoltes. Développez l'interface ici.")


def get_unique_values(column_name):
    """
    Récupère toutes les valeurs uniques et non-NULL d'une colonne donnée de la table Effectifs,
    triées par ordre alphabétique.
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    unique_values = []
    try:
        with closing(conn.cursor()) as cursor:
           
            cursor.execute(f"SELECT DISTINCT {column_name} FROM Effectifs WHERE {column_name} IS NOT NULL ORDER BY {column_name}")
            results = cursor.fetchall()
            unique_values = [row[0] for row in results]
    except sqlite3.Error as e:
        st.error(f"Erreur SQLite lors de la récupération des valeurs uniques pour {column_name} : {e}")
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue lors de la récupération des valeurs uniques : {e}")
    finally:
        conn.close()
    return unique_values
        
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
