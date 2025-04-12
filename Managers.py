
import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px
from datetime import datetime
from streamlit_option_menu import option_menu
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from contextlib import closing
from PIL import Image
from Utils_Dental import *
from Supports import *


def get_db_connection():
    server = 'DESKTOP-2D5TJUA'
    database = 'Total_Stat'
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None
    

def load_data():
    """Chargement des données depuis SQL Server."""
    try:
        conn = get_db_connection()
        if not conn:
            return pd.DataFrame(), pd.DataFrame()

        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT Hyp, ORDER_REFERENCE, ORDER_DATE, SHORT_MESSAGE, Country, City, Total_sale, Rating, Id_Sale 
                FROM Sales""")
            sales_df = pd.DataFrame.from_records(cursor.fetchall(), 
                                               columns=[column[0] for column in cursor.description])

            cursor.execute("""
                SELECT Hyp, Team, Activité, Date_In, Type 
                FROM Effectifs
                where Type = 'Agent'
                """)
            staff_df = pd.DataFrame.from_records(cursor.fetchall(),
                                               columns=[column[0] for column in cursor.description])

        return sales_df, staff_df
    except Exception as e:
        st.error(f"Erreur de chargement des données: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()
    finally:
        if conn:
            conn.close()

def preprocess_data(df):
    """Prétraitement des données."""
    if 'ORDER_DATE' in df.columns:
        df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'], errors='coerce')
    if 'Total_sale' in df.columns:
        df['Total_sale'] = pd.to_numeric(df['Total_sale'], errors='coerce').fillna(0)
    
    if 'Date_In' in df.columns:
        df['Date_In'] = pd.to_datetime(df['Date_In'], errors='coerce')
    return df

@st.cache_data
def filter_data(df, country_filter, team_filter, activity_filter, start_date, end_date, staff_df, current_hyp=None):
    """Appliquer les filtres aux données en utilisant Hyp comme clé."""
    filtered_df = df.copy()
    
    if current_hyp:
        return filtered_df[filtered_df['Hyp'] == current_hyp]
    
    if 'ORDER_DATE' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['ORDER_DATE'] >= pd.to_datetime(start_date)) & 
            (filtered_df['ORDER_DATE'] <= pd.to_datetime(end_date))
        ]
    
    if country_filter != 'Tous' and 'Country' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Country'] == country_filter]
    
    if 'Hyp' in filtered_df.columns and not staff_df.empty:
        staff_filtered = staff_df.copy()
        
        if current_hyp is None:
            staff_filtered = staff_filtered
        
        if team_filter != 'Toutes':
            staff_filtered = staff_filtered[staff_filtered['Team'] == team_filter]
        if activity_filter != 'Toutes':
            staff_filtered = staff_filtered[staff_filtered['Activité'] == activity_filter]
        
        filtered_df = filtered_df[filtered_df['Hyp'].isin(staff_filtered['Hyp'])]

    return filtered_df

def geocode_data(df):
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        return df
    
    geolocator = Nominatim(user_agent="sales_dashboard")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    cities = df[['City', 'Country']].drop_duplicates()
    locations = []
    
    for _, row in cities.iterrows():
        try:
            location = geocode(f"{row['City']}, {row['Country']}")
            if location:
                locations.append({
                    'City': row['City'], 
                    'Country': row['Country'],
                    'Latitude': location.latitude,
                    'Longitude': location.longitude
                })
        except:
            continue
    
    if locations:
        locations_df = pd.DataFrame(locations)
        df = pd.merge(df, locations_df, on=['City', 'Country'], how='left')
    return df

def manager_dashboard():
    sales_df, staff_df = load_data()
    sales_df = preprocess_data(sales_df)
    staff_df = preprocess_data(staff_df)

    with st.sidebar:
        st.image('Dental_Implant.png', width=350)
        
        if st.session_state.get("user_type") == "Hyperviseur":
            menu_options = ["Tableau de bord", "Sales", "Recolt", "Planning", "Setting"]
            icons = ["bar-chart", "currency-dollar", "list-ul", "calendar", "gear"]
        elif st.session_state.get("user_type") == "Support":
            menu_options = ["Tableau de bord", "Coaching"]
            icons = ["bar-chart", "currency-dollar", "list-ul", "calendar"]
        else:
            menu_options = ["Tableau de bord", "Sales", "Recolt", "Planning"]
            icons = ["bar-chart", "currency-dollar", "list-ul", "calendar"]
            
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=icons,
            default_index=0,
            styles={
                "container": {"background-color": "#002a48"},
                "icon": {"color": "#00afe1", "font-size": "18px"},
                "nav-link": {"color": "#ffffff", "font-size": "16px"},
                "nav-link-selected": {"background-color": "#007bad"}
            }
        )
        
        st.markdown("---")
        st.markdown("<h2 style='font-size: 16px; color: #00afe1;'>Filtres de Dates</h2>", unsafe_allow_html=True)
        
        with st.expander("Période", expanded=True):
            min_date = sales_df['ORDER_DATE'].min() if not sales_df.empty else datetime.now()
            max_date = sales_df['ORDER_DATE'].max() if not sales_df.empty else datetime.now()
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Date début", min_date, min_value=min_date, max_value=max_date)
            with col2:
                end_date = st.date_input("Date fin", max_date, min_value=min_date, max_value=max_date)
    
    # Gestion des différentes pages en fonction de la sélection
    if selected == "Tableau de bord":
        display_dashboard(sales_df, staff_df, start_date, end_date)
    elif selected == "Sales":
        display_sales(sales_df, staff_df, start_date, end_date)
    elif selected == "Planning":
        display_planning(sales_df, staff_df)
    # ... autres options de menu

def display_dashboard(sales_df, staff_df, start_date, end_date):
    # Implémentation de l'affichage du tableau de bord
    pass

def display_sales(sales_df, staff_df, start_date, end_date):
    # Implémentation de l'affichage des ventes
    pass

def display_planning(sales_df, staff_df):
    # Implémentation de l'affichage du planning
    pass