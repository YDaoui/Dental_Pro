import streamlit as st
import pandas as pd
import pyodbc
from contextlib import closing
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import plotly.express as px
import folium
from streamlit_folium import st_folium
from Utils_Dental import *
from Sales import *
from Recolts import *

def get_db_connection():
    """Établit une connexion à la base de données SQL Server."""
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

def logs_page(logs_df, start_date, end_date):
    """Affiche la page des logs avec les filtres spécifiés."""
    st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Logs Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #007bad; margin-top: 0;'>Analyse des Logs</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # Filtrage temporel initial
    mask = (logs_df['Date_creation'] >= pd.to_datetime(start_date)) & \
           (logs_df['Date_creation'] <= pd.to_datetime(end_date))
    filtered_logs = logs_df.loc[mask].copy()

    # Filtres dans des colonnes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        segment_filter = st.selectbox(
            "Segment",
            ['Tous'] + sorted(filtered_logs['Segment'].dropna().unique()),
            key='segment_filter'
        )
        statut_bp_filter = st.selectbox(
            "Statut BP",
            ['Tous'] + sorted(filtered_logs['Statut_BP'].dropna().unique()),
            key='statut_bp_filter'
        )
        
    with col2:
        canal_filter = st.selectbox(
            "Canal",
            ['Tous'] + sorted(filtered_logs['Canal'].dropna().unique()),
            key='canal_filter'
        )
        
        direction_filter = st.selectbox(
            "Direction",
            ['Tous'] + sorted(filtered_logs['Direction'].dropna().unique()),
            key='direction_filter'
        )
    
    with col3:
        qualification_filter = st.selectbox(
            "Qualification",
            ['Tous'] + sorted(filtered_logs['Qualification'].dropna().unique()),
            key='qualification_filter'
        )
        
        offre_filter = st.selectbox(
            "Offre",
            ['Tous'] + sorted(filtered_logs['Offre'].dropna().unique()),
            key='offre_filter'
        )

    # Application des filtres
    if segment_filter != 'Tous':
        filtered_logs = filtered_logs[filtered_logs['Segment'] == segment_filter]
    
    if statut_bp_filter != 'Tous':
        filtered_logs = filtered_logs[filtered_logs['Statut_BP'] == statut_bp_filter]

    if canal_filter != 'Tous':
        filtered_logs = filtered_logs[filtered_logs['Canal'] == canal_filter]
    
    if direction_filter != 'Tous':
        filtered_logs = filtered_logs[filtered_logs['Direction'] == direction_filter]
    
    if qualification_filter != 'Tous':
        filtered_logs = filtered_logs[filtered_logs['Qualification'] == qualification_filter]
    
    if offre_filter != 'Tous':
        filtered_logs = filtered_logs[filtered_logs['Offre'] == offre_filter]

    # Affichage des métriques
    st.markdown("---")
    st.subheader("Indicateurs Clés")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Logs", len(filtered_logs))
    
    min_date = filtered_logs['Date_creation'].min()
    max_date = filtered_logs['Date_creation'].max()
    
    col2.metric("Premier Log", min_date.strftime('%d/%m/%Y') if not pd.isna(min_date) else "N/A")
    col3.metric("Dernier Log", max_date.strftime('%d/%m/%Y') if not pd.isna(max_date) else "N/A")
    
    if not pd.isna(min_date) and not pd.isna(max_date):
        days = (max_date - min_date).days
        col4.metric("Période Couverte", f"{days} jours")
    else:
        col4.metric("Période Couverte", "N/A")

    # Visualisations
    st.markdown("---")
    st.subheader("Répartition des Logs")

    if not filtered_logs.empty:
        # Graphique 1: Répartition par canal
        fig1 = px.pie(
            filtered_logs,
            names='Canal',
            title="Répartition par Canal",
            color='Canal',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        # Graphique 2: Evolution temporelle
        daily_logs = filtered_logs.groupby(filtered_logs['Date_creation'].dt.date).size().reset_index(name='Count')
        fig2 = px.line(
            daily_logs,
            x='Date_creation',
            y='Count',
            title="Volume de Logs par Jour",
            line_shape='spline'
        )
        
        # Graphique 3: Répartition par offre
        fig3 = px.pie(
            filtered_logs,
            names='Offre',
            title="Répartition par Offre",
            color='Offre',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        col1, col2, col3 = st.columns(3)
    
        with col1:
            st.plotly_chart(fig1, use_container_width=True, key="canal_chart")
        with col2:
            st.plotly_chart(fig2, use_container_width=True, key="daily_logs_chart")
        with col3:
            st.plotly_chart(fig3, use_container_width=True, key="offre_chart")

        # Tableau de données
        st.markdown("---")
        st.subheader("Données Détailées")
        st.dataframe(filtered_logs.sort_values('Date_creation', ascending=False))
    else:
        st.warning("Aucune donnée disponible avec les filtres sélectionnés.")

if __name__ == "__main__":
    main()