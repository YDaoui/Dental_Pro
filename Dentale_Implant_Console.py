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
from Managers import *
from Agents import *








# Configuration de la page Streamlit
st.set_page_config(
    layout="wide",
    page_title="Global Sales Dashboard",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# CSS pour changer le fond de la page
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)
# Style CSS personnalisé
st.markdown("""
    <style>
        /* Couleurs principales */
        :root {
            --primary: #002a48;
            --secondary: #007bad;
            --accent: #00afe1;
            --background: #ffffff;
        }

        /* Style général */
        .stApp {
            background-color: var(--background);
        }

        /* Titres */
        h1 {
            color: var(--primary) !important;
        }

        h2 {
            color: var(--secondary) !important;
        }

        h3 {
            color: var(--accent) !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--background) !important;  /* Fond blanc */
        }

        .sidebar .sidebar-content {
            background-color: var(--background);  /* Fond blanc */
        }

        /* Boutons */
        .stButton>button {
            background-color: var(--secondary);
            color: white;
        }

        .stButton>button:hover {
            background-color: var(--accent);
            color: white;
        }

        /* Sélecteurs */
        .stSelectbox>div>div>select {
            border-color: var(--secondary);
        }

        /* Onglets */
        .stTabs [aria-selected="true"] {
            color: var(--accent) !important;
        }

        /* Metrics */
        [data-testid="stMetric"] {
            background-color: #f0f2f6;
            border-left: 4px solid var(--accent);
        }

        /* Dataframes */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--secondary);
        }
    </style>
""", unsafe_allow_html=True)


# Connexion à SQL Server
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

# Fonction pour récupérer les détails de l'utilisateur
def get_user_details(hyp):
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

# Fonction pour réinitialiser le mot de passe


# Authentification
def authenticate(username, password):
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

# Page de connexion




if selected == "Setting":
    setting_page()
elif selected == "Sales":
    
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image('Dental_Implant2.png', width=150)
        with col2:
            st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Global Sales Dashboard</h1>", unsafe_allow_html=True)
            st.markdown("<h2 style='color: #007bad; margin-top: 0;'>All Teams</h2>", unsafe_allow_html=True)
            st.markdown("---")
        
        # Filtres
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            country_sales_filter = st.selectbox("Filtrer par Pays (Sales)", ['Tous'] + sorted(sales_df['Country'].dropna().unique()))
        with col2:
            selected_team = st.selectbox("Sélectionner équipe", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()))
        with col3:
            selected_activity = st.selectbox("Sélectionner activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()))
        
        st.markdown("---")
        
        # Appliquer les filtres
        filtered_sales = filter_data(sales_df, country_sales_filter, selected_team, selected_activity, start_date, end_date, staff_df)
        
        # Métriques avec les données filtrées
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Sales", f"€{filtered_sales['Total_sale'].sum():,.0f}".replace(",", " "))
        with col2:
            st.metric("Average Sale", f"€{filtered_sales['Total_sale'].mean():,.2f}".replace(",", " "))
        with col3:
            avg_rating = filtered_sales['Rating'].mean()
            st.metric(
                label="Average Rating", 
                value=f"{'★' * int(avg_rating)}{'☆' * (5 - int(avg_rating))}"# {avg_rating:.1f}/5"
            )
            
            # Utilisation d'une carte métrique standard avec HTML pour les étoiles
            
        with col4:
            st.metric("Transactions", len(filtered_sales))
            
        st.markdown("---")
        
        # Affichage du dataframe filtré
        st.dataframe(filtered_sales)

elif selected == "Tableau de bord":
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image('Dental_Implant2.png', width=150)
        with col2:
            st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Dashboard Global</h1>", unsafe_allow_html=True)
            #st.markdown("<h2 style='color: #007bad; margin-top: 0;'>All Teams</h2>", unsafe_allow_html=True)

            st.markdown("<h2 style='color: #00afe1;'>Analyse Commerciale - Sales</h2>", unsafe_allow_html=True)
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            country_sales_filter = st.selectbox(
                "Filtrer par Pays (Sales)", 
                ['Tous'] + sorted(sales_df['Country'].dropna().unique())
            )
        with col2:
            selected_team = st.selectbox(
                "Sélectionner équipe", 
                ['Toutes'] + sorted(staff_df['Team'].dropna().unique())
            )
        with col3:
            selected_activity = st.selectbox(
                "Sélectionner activité", 
                ['Toutes'] + sorted(staff_df['Activité'].dropna().unique())
            )
        
        filtered_sales = filter_data(
            sales_df, 
            country_sales_filter, 
            selected_team, 
            selected_activity, 
            start_date, 
            end_date, 
            staff_df
        )
        
        if not filtered_sales.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric(
                "Ventes Totales", 
                f"${filtered_sales['Total_sale'].sum():,.2f}",
                help="Somme totale des ventes pour la période sélectionnée"
            )
            col2.metric(
                "Vente Moyenne", 
                f"${filtered_sales['Total_sale'].mean():,.2f}",
                help="Moyenne des ventes par transaction"
            )
            col3.metric(
                "Nombre de Transactions", 
                len(filtered_sales),
                help="Nombre total de transactions"
            )
            
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                sales_by_city = filtered_sales.groupby('City')['Total_sale'].sum().reset_index()
                fig = px.bar(
                    sales_by_city, 
                    x='City', 
                    y='Total_sale', 
                    color='City', 
                    title="Ventes par Ville",
                    labels={'Total_sale': 'Montant des ventes ($)'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if not staff_df.empty and 'Hyp' in filtered_sales.columns:
                    sales_with_team = filtered_sales.merge(
                        staff_df[['Hyp', 'Team', 'Type']], 
                        on='Hyp', 
                        how='left'
                    )
                    sales_with_team = sales_with_team[sales_with_team['Type'] != 'Agent']
                    sales_by_team = sales_with_team.groupby('Team')['Total_sale'].sum().reset_index()
                    fig = px.pie(
                        sales_by_team, 
                        names='Team', 
                        values='Total_sale', 
                        title="Répartition des ventes par équipe",
                        hole=0.3
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                if not staff_df.empty and 'Hyp' in filtered_sales.columns:
                    sales_with_activity = filtered_sales.merge(
                        staff_df[['Hyp', 'Activité', 'Type']], 
                        on='Hyp', 
                        how='left'
                    )
                    sales_with_activity = sales_with_activity[sales_with_activity['Type'] != 'Agent']
                    sales_by_activity = sales_with_activity.groupby('Activité')['Total_sale'].sum().reset_index()
                    fig = px.pie(
                        sales_by_activity, 
                        names='Activité', 
                        values='Total_sale', 
                        title="Répartition des ventes par Activité",
                        hole=0.3
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.markdown("<h3 style='color: #002a48;'>Évolution des ventes dans le temps</h3>", unsafe_allow_html=True)
            sales_by_date = filtered_sales.groupby(filtered_sales['ORDER_DATE'].dt.to_period('M'))['Total_sale'].sum().reset_index()
            sales_by_date['ORDER_DATE'] = sales_by_date['ORDER_DATE'].astype(str)
            fig = px.line(
                sales_by_date, 
                x='ORDER_DATE', 
                y='Total_sale', 
                title="Évolution mensuelle des ventes",
                markers=True,
                labels={'ORDER_DATE': 'Mois', 'Total_sale': 'Ventes ($)'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning("Aucune donnée à afficher pour les critères sélectionnés")
            
elif selected == "Planning":
    
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image('Dental_Implant1.png', width=150)
        with col2:
            st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Planning </h1>", unsafe_allow_html=True)
            st.markdown("<h2 style='color: #007bad; margin-top: 0;'>All Teams</h2>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Country Filter at the top
        countries = sorted(sales_df['Country'].unique())
        selected_country = st.selectbox("Select Country", countries, key='country_filter')
        filtered_sales = sales_df[sales_df['Country'] == selected_country]
        
        # 1. Récupérer les ventes groupées par hyp
        sales_by_hyp = filtered_sales.groupby('Hyp')['Total_sale'].sum().reset_index()
        
        # 2. Fusionner avec les activités depuis Effectifs
        if not staff_df.empty and 'Hyp' in staff_df.columns:
            activity_sales = sales_by_hyp.merge(
                staff_df[['Hyp', 'Activité']].drop_duplicates(),
                on='Hyp',
                how='left'
            ).fillna({'Activité': 'Non spécifié'})
            
            # 3. Agréger les ventes par activité
            ventes_par_activite = activity_sales.groupby('Activité')['Total_sale'].sum().reset_index()
        else:
            ventes_par_activite = pd.DataFrame({'Activité': ['Non spécifié'], 'Total_sale': [filtered_sales['Total_sale'].sum()]})
        
        # Metrics Row
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Ventes Totales", f"${filtered_sales['Total_sale'].sum():,.0f}")
        with col2:
            st.metric("Nombre de Transactions", len(filtered_sales))
        
        # First Row of Charts
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Ventes par Ville
            ventes_par_ville = filtered_sales.groupby('City')['Total_sale'].sum().reset_index()
            fig = px.bar(
                ventes_par_ville,
                x='City',
                y='Total_sale',
                title="Ventes par Ville",
                color='City',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Répartition des effectifs
            if not staff_df.empty:
                staff_filtre = staff_df[staff_df['Country'] == selected_country] if 'Country' in staff_df.columns else staff_df
                fig = px.bar(
                    staff_filtre.groupby('Team').size().reset_index(name='Count'),
                    x='Team',
                    y='Count',
                    title="Effectifs par Équipe",
                    color='Team',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Ventes par Activité
            fig = px.bar(
                ventes_par_activite.sort_values('Total_sale', ascending=False),
                x='Activité',
                y='Total_sale',
                title="Ventes par Activité",
                color='Activité',
                text_auto='.2s',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(
                showlegend=False,
                xaxis_title="Activité",
                yaxis_title="Montant des ventes ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Map Section
        if 'Latitude' not in filtered_sales.columns or 'Longitude' not in filtered_sales.columns:
            with st.spinner("Géocodage des villes en cours..."):
                filtered_sales = geocode_data(filtered_sales)
        
        if 'Latitude' in filtered_sales.columns:
            geo_data = filtered_sales.groupby(['City', 'Latitude', 'Longitude']).agg(
                Ventes=('Total_sale', 'sum'),
                Transactions=('Total_sale', 'count')
            ).reset_index().dropna()
            
            if not geo_data.empty:
                st.markdown("<h3 style='color: #002a48;'>Carte des Ventes</h3>", unsafe_allow_html=True)
                fig = px.scatter_mapbox(
                    geo_data,
                    lat="Latitude",
                    lon="Longitude",
                    size="Ventes",
                    color="Ventes",
                    hover_name="City",
                    hover_data={"Ventes": ":$.2f", "Transactions": True},
                    zoom=5,
                    center={"lat": geo_data['Latitude'].mean(), "lon": geo_data['Longitude'].mean()},
                    title=f"Ventes par Ville - {selected_country}",
                    color_continuous_scale=px.colors.sequential.Viridis,
                    mapbox_style="open-street-map"
                )
                fig.update_layout(
                    height=600, 
                    margin={"r":0,"t":40,"l":0,"b":0},
                    coloraxis_colorbar={
                        "title": "Montant des ventes",
                        "tickprefix": "$"
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Data Table
        st.markdown("<h3 style='color: #002a48;'>Détail des Transactions</h3>", unsafe_allow_html=True)
        st.dataframe(
            filtered_sales.sort_values('Total_sale', ascending=False),
            use_container_width=True,
            height=400,
            column_config={
                "ORDER_DATE": "Date",
                "Total_sale": st.column_config.NumberColumn(
                    "Montant",
                    format="$%.2f"
                ),
                "Rating": "Évaluation"
            }
        )
        
        st.markdown("---")
# Gestion de l'état de connexion


# [...] (le reste de votre code existant reste inchangé)

# Gestion de l'état de connexion
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if st.session_state.get("authenticated"):
    if st.session_state.get("user_type") in ["Manager", "Hyperviseur"]:
        manager_dashboard()
    elif st.session_state.get("user_type") == "Support":
        support_dashboard()
    else:  # Pour les agents
        agent_dashboard()
else:
    login_page()
