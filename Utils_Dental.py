import streamlit as st
import pandas as pd
import pyodbc
from contextlib import closing
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import plotly.express as px










    

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

def login_page():
    col1, col2, col3, col4 = st.columns([1,1,2,1])
    with col2:
        st.image('Dental_Implant1.png', width=340)
    with col3:
        st.markdown("<h2 style='color:#007bad;'>Connexion</h2>", unsafe_allow_html=True)
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
            st.button("**Annuler**", key="Annuler_button")

def load_data():
    """Chargement des données depuis SQL Server."""
    try:
        conn = get_db_connection()
        if not conn:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        with closing(conn.cursor()) as cursor:
            # Chargement des ventes
            cursor.execute("""
                SELECT Hyp, ORDER_REFERENCE, ORDER_DATE, SHORT_MESSAGE, Country, City, Total_sale, Rating, Id_Sale 
                FROM Sales
                WHERE SHORT_MESSAGE <> 'ERROR'""")
            sales_df = pd.DataFrame.from_records(cursor.fetchall(), 
                                             columns=[column[0] for column in cursor.description])
            
            # Chargement des récoltes
            cursor.execute("""
                SELECT Hyp, ORDER_REFERENCE, ORDER_DATE, SHORT_MESSAGE, Country, City, Total_Recolt, Banques, Id_Recolt 
                FROM Recolts
                WHERE SHORT_MESSAGE <> 'ERROR'""")
            recolts_df = pd.DataFrame.from_records(cursor.fetchall(), 
                                             columns=[column[0] for column in cursor.description])

            # Chargement du staff
            cursor.execute("""
                SELECT Hyp, Team, Activité, Date_In, Type 
                FROM Effectifs
                WHERE Type = 'Agent'""")
            staff_df = pd.DataFrame.from_records(cursor.fetchall(),
                                             columns=[column[0] for column in cursor.description])

        return sales_df, recolts_df, staff_df
    except Exception as e:
        st.error(f"Erreur de chargement des données: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    finally:
        if conn:
            conn.close()

def preprocess_data(df):
    """Prétraitement des données."""
    if 'ORDER_DATE' in df.columns:
        df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'], errors='coerce')
    if 'Total_sale' in df.columns:
        df['Total_sale'] = pd.to_numeric(df['Total_sale'], errors='coerce').fillna(0)
    if 'Total_Recolt' in df.columns:
        df['Total_Recolt'] = pd.to_numeric(df['Total_Recolt'], errors='coerce').fillna(0)
    if 'Date_In' in df.columns:
        df['Date_In'] = pd.to_datetime(df['Date_In'], errors='coerce')
    return df

# Fonctions des différentes pages
def dashboard_page(sales_df, staff_df, start_date, end_date):
    """Page Tableau de bord principal."""
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image('Dental_Implant.png', width=200)
    with col2:
        st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Dashboard Global</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #00afe1;'>Analyse Commerciale - Sales - Recolts - Logs </h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtres
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        country_filter = st.selectbox("Filtrer par Pays", ['Tous'] + sorted(sales_df['Country'].dropna().unique()))
    with col2:
        team_filter = st.selectbox("Sélectionner équipe", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()))
    with col3:
        activity_filter = st.selectbox("Sélectionner activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()))
    
    # Appliquer les filtres
    filtered_sales = filter_data(sales_df, country_filter, team_filter, activity_filter, start_date, end_date, staff_df)
    
    if not filtered_sales.empty:
        # Métriques
        col1, col2, col3 = st.columns(3)
        col1.metric("Ventes Totales", f"€{filtered_sales['Total_sale'].sum():,.2f}".replace(",", " "))
        col2.metric("Vente Moyenne", f"€{filtered_sales['Total_sale'].mean():,.2f}".replace(",", " "))
        col3.metric("Nombre de Transactions", len(filtered_sales))
        
        st.markdown("---")
        
        # Graphiques
        col1, col2 = st.columns(2)
        with col1:
            ventes_ville = filtered_sales.groupby('City')['Total_sale'].sum().reset_index()
            fig = px.bar(ventes_ville, x='City', y='Total_sale', title="Ventes par Ville")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            ventes_date = filtered_sales.groupby(filtered_sales['ORDER_DATE'].dt.date)['Total_sale'].sum().reset_index()
            fig = px.line(ventes_date, x='ORDER_DATE', y='Total_sale', title="Évolution des Ventes")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucune donnée à afficher pour les critères sélectionnés")

def sales_page(sales_df, staff_df, start_date, end_date):
    """Page dédiée aux ventes."""
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
        country_filter = st.selectbox("Filtrer par Pays (Sales)", ['Tous'] + sorted(sales_df['Country'].dropna().unique()))
    with col2:
        team_filter = st.selectbox("Sélectionner équipe", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()))
    with col3:
        activity_filter = st.selectbox("Sélectionner activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()))
    
    # Appliquer les filtres
    filtered_sales = filter_data(sales_df, country_filter, team_filter, activity_filter, start_date, end_date, staff_df)
    
    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"€{filtered_sales['Total_sale'].sum():,.0f}".replace(",", " "))
    col2.metric("Average Sale", f"€{filtered_sales['Total_sale'].mean():,.2f}".replace(",", " "))
    
    avg_rating = filtered_sales['Rating'].mean()
    col3.metric("Average Rating", f"{'★' * int(avg_rating)}{'☆' * (5 - int(avg_rating))}")
    
    col4.metric("Transactions", len(filtered_sales))
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
            ventes_ville = filtered_sales.groupby('City')['Total_sale'].sum().reset_index()
            fig = px.bar(ventes_ville, x='City', y='Total_sale', title="Ventes par Ville")
            st.plotly_chart(fig, use_container_width=True)
        
    with col2:
            ventes_date = filtered_sales.groupby(filtered_sales['ORDER_DATE'].dt.date)['Total_sale'].sum().reset_index()
            fig = px.line(ventes_date, x='ORDER_DATE', y='Total_sale', title="Évolution des Ventes")
            st.plotly_chart(fig, use_container_width=True)
    
    # Affichage des données
    st.dataframe(filtered_sales)
def filter_data(df, country_filter, team_filter, activity_filter, start_date, end_date, staff_df, current_hyp=None):
    """Appliquer les filtres aux données."""
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
        if team_filter != 'Toutes':
            staff_filtered = staff_filtered[staff_filtered['Team'] == team_filter]
        if activity_filter != 'Toutes':
            staff_filtered = staff_filtered[staff_filtered['Activité'] == activity_filter]
        
        filtered_df = filtered_df[filtered_df['Hyp'].isin(staff_filtered['Hyp'])]

    return filtered_df

def recolts_page(recolts_df, staff_df, start_date, end_date):
    """Page dédiée aux récoltes."""
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image('Dental_Implant2.png', width=150)
    with col2:
        st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Global Recolts Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #007bad; margin-top: 0;'>All Teams</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtres
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        country_filter = st.selectbox("Filtrer par Pays (Recolts)", ['Tous'] + sorted(recolts_df['Country'].dropna().unique()))
    with col2:
        team_filter = st.selectbox("Sélectionner équipe", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()), key='recolt_team')
    with col3:
        activity_filter = st.selectbox("Sélectionner activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()), key='recolt_activity')
    
    # Appliquer les filtres
    filtered_recolts = filter_data(recolts_df, country_filter, team_filter, activity_filter, start_date, end_date, staff_df)
    
    # Métriques
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Recolts", f"€{filtered_recolts['Total_Recolt'].sum():,.0f}".replace(",", " "))
    col2.metric("Average Recolt", f"€{filtered_recolts['Total_Recolt'].mean():,.2f}".replace(",", " "))
    col3.metric("Transactions", len(filtered_recolts))
    
    st.markdown("---")
    
    # Graphique par banque
    if 'Banques' in filtered_recolts.columns:
        st.subheader("Récoltes par Banque")
        recolts_by_bank = filtered_recolts.groupby('Banques')['Total_Recolt'].sum().reset_index()
        fig = px.bar(recolts_by_bank, x='Banques', y='Total_Recolt', 
                    title="Montant récolté par Banque",
                    color='Banques')
        st.plotly_chart(fig, use_container_width=True)
    
    # Affichage des données
    st.dataframe(filtered_recolts)

def planning_page(sales_df, staff_df):
    """Page de planning."""
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image('Dental_Implant1.png', width=150)
    with col2:
        st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Planning</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #007bad; margin-top: 0;'>All Teams</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtre par pays
    selected_country = st.selectbox("Select Country", sorted(sales_df['Country'].unique()), key='country_filter')
    filtered_sales = sales_df[sales_df['Country'] == selected_country]
    
    # Métriques
    col1, col2 = st.columns(2)
    col1.metric("Ventes Totales", f"€{filtered_sales['Total_sale'].sum():,.0f}".replace(",", " "))
    col2.metric("Nombre de Transactions", len(filtered_sales))
    
    # Graphiques
    col1, col2 = st.columns(2)
    with col1:
        ventes_ville = filtered_sales.groupby('City')['Total_sale'].sum().reset_index()
        fig = px.bar(ventes_ville, x='City', y='Total_sale', title="Ventes par Ville")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not staff_df.empty:
            effectifs = staff_df[staff_df['Country'] == selected_country] if 'Country' in staff_df.columns else staff_df
            fig = px.pie(effectifs, names='Team', title="Répartition des Effectifs")
            st.plotly_chart(fig, use_container_width=True)


def setting_page():
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image('Dental_Implant2.png', width=150)
    with col2:
        st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Global Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #007bad; margin-top: 0;'>Settings All Teams</h2>", unsafe_allow_html=True)

        st.markdown("---")

    st.markdown("<h2 style='font-size: 38px; font-weight: bold; color: #00afe1;'>Paramètres Utilisateur</h2>", unsafe_allow_html=True)
    
    hyp_input = st.text_input("Entrez l'ID (Hyp) de l'utilisateur")
    
    if hyp_input:
        user_details = get_user_details(hyp_input)
        
        if user_details:
            date_in = user_details[2]
            anciennete = (datetime.now().date() - date_in.date()).days // 365
            
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.markdown("<h2 style='font-size: 28px; color: #002a48;'>Informations Professionnelles : </h2>", unsafe_allow_html=True)
                st.write(f"**Nom:** {user_details[0]}")
                st.write(f"**Prénom:** {user_details[1]}")
                st.write(f"**Date d'entrée:** {date_in.strftime('%d/%m/%Y')}")
                st.write(f"**Ancienneté:** {anciennete} ans")
            
            with col2:
                st.subheader("")
                st.write(f"**Team:** {user_details[3]}")
                st.write(f"**Type:** {user_details[4]}")
                st.write(f"**Activité:** {user_details[5]}")
                st.write(f"**Nom d'utilisateur:** {user_details[6]}")
                st.write(f"**Dernière connexion:** {user_details[7] if user_details[7] else 'Jamais'}")
            
            with col3:
                st.markdown("<h2 style='font-size: 28px; font-weight: bold; color: #007bad;'>Action : </h2>", unsafe_allow_html=True)
                reset_pwd = st.checkbox("Réinitialiser le mot de passe")
                
                if reset_pwd:
                    if st.button("Confirmer la réinitialisation"):
                        if reset_password(hyp_input):
                            st.success(f"Mot de passe réinitialisé avec succès à la valeur: {hyp_input}")
                        else:
                            st.error("Erreur lors de la réinitialisation du mot de passe")
            st.markdown("---")
        else:
            st.warning("Aucun utilisateur trouvé avec cet ID (Hyp)")

            
def reset_password(hyp):
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