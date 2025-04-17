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


def add_custom_css():
    """Ajoute du CSS personnalisé pour l'application."""
    custom_css = """
    <style>
        .stButton>button {
            background-color: #007bad;
            color: white !important;
            border: 2px solid #007bad !important;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: white !important;
            color: #007bad !important;
            border: 2px solid #00afe1 !important;
        }
        .stButton>button:active,
        .stButton>button:focus {
            background-color: #00afe1 !important;
            color: white !important;
            border: 2px solid #00afe1 !important;
        }
        /* Amélioration des onglets */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            border-radius: 4px;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

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
        st.image('Dental_Implant.png', width=440)
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
            if st.button("**Annuler**", key="Annuler_button"):
                st.experimental_rerun()

# Chargement des données
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
                WHERE SHORT_MESSAGE <> 'ERROR'
            """)
            sales_df = pd.DataFrame.from_records(cursor.fetchall(),
                                                 columns=[column[0] for column in cursor.description])

            # Chargement des récoltes
            cursor.execute("""
                SELECT Hyp, ORDER_REFERENCE, ORDER_DATE, SHORT_MESSAGE, Country, City, Total_Recolt, Banques, Id_Recolt 
                FROM Recolts
                WHERE SHORT_MESSAGE <> 'ERROR'
            """)
            recolts_df = pd.DataFrame.from_records(cursor.fetchall(),
                                                   columns=[column[0] for column in cursor.description])

            # Chargement du staff
            cursor.execute("""
                SELECT Hyp, Team, Activité, Date_In, Type 
                FROM Effectifs
                WHERE Type = 'Agent'
            """)
            staff_df = pd.DataFrame.from_records(cursor.fetchall(),
                                                 columns=[column[0] for column in cursor.description])

        return sales_df, recolts_df, staff_df
    except Exception as e:
        st.error(f"Erreur de chargement des données: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    finally:
        if conn:
            conn.close()


# Prétraitement des données
def preprocess_data(df):
    """Prétraite les données."""
    if 'ORDER_DATE' in df.columns:
        df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'], errors='coerce')
    if 'Total_sale' in df.columns:
        df['Total_sale'] = pd.to_numeric(df['Total_sale'], errors='coerce').fillna(0)
    if 'Total_Recolt' in df.columns:
        df['Total_Recolt'] = pd.to_numeric(df['Total_Recolt'], errors='coerce').fillna(0)
   
    if 'Date_In' in df.columns:
        df['Date_In'] = pd.to_datetime(df['Date_In'], errors='coerce')
    return df


# Géocodage sécurisé
def geocode_data(df):
    """Géocode les villes pour obtenir les coordonnées GPS."""
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        return df

    geolocator = Nominatim(user_agent="sales_dashboard", timeout=10)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    locations = []
    unique_locations = df[['City', 'Country']].dropna().drop_duplicates()

    for _, row in unique_locations.iterrows():
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

    if locations:
        locations_df = pd.DataFrame(locations)
        df = pd.merge(df, locations_df, on=['City', 'Country'], how='left')
    return df


# Filtrage des données
def filter_data(df, country_filter, team_filter, activity_filter, start_date, end_date, staff_df, current_hyp=None):
    """Filtre les données selon les critères."""
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

        if 'Hyp' in staff_filtered.columns:
            filtered_df = filtered_df[filtered_df['Hyp'].isin(staff_filtered['Hyp'])]

    return filtered_df


# Affichage de la page Ventes
def sales_page(sales_df, staff_df, start_date, end_date):
    """Affiche la page des ventes."""
    st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Global Sales Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #007bad; margin-top: 0;'>All Teams</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # Filtres
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        country_filter = st.selectbox("Filtrer par Pays", ['Tous'] + sorted(sales_df['Country'].dropna().unique()), key='sales_country')
    with col2:
        team_filter = st.selectbox("Sélectionner équipe", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()), key='sales_team')
    with col3:
        activity_filter = st.selectbox("Sélectionner activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()), key='sales_activity')

    # Filtrage
    filtered_sales = filter_data(sales_df, country_filter, team_filter, activity_filter, start_date, end_date, staff_df)

    if not filtered_sales.empty:
        # Métriques
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sales", f"€{filtered_sales['Total_sale'].sum():,.0f}".replace(",", " "))
        col2.metric("Average Sale", f"€{filtered_sales['Total_sale'].mean():,.2f}".replace(",", " "))

        if 'Rating' in filtered_sales.columns:
            avg_rating = filtered_sales['Rating'].mean()
            rating_display = f"{'★' * int(round(avg_rating))}{'☆' * (5 - int(round(avg_rating)))} ({avg_rating:.1f})"
            col3.metric("Average Rating", rating_display)
        else:
            col3.metric("Average Rating", "N/A")

        col4.metric("Transactions", len(filtered_sales))

        st.markdown("---")

        # Graphiques
        col1, col2 = st.columns(2)
        with col1:
            ventes_ville = filtered_sales.groupby('City')['Total_sale'].sum().reset_index()
            fig = px.bar(ventes_ville, x='City', y='Total_sale', title="Ventes par Ville",
                         color='Total_sale', color_continuous_scale=['#00afe1', '#007bad'])
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            ventes_date = filtered_sales.groupby(filtered_sales['ORDER_DATE'].dt.date)['Total_sale'].sum().reset_index()
            fig = px.line(ventes_date, x='ORDER_DATE', y='Total_sale', title="Évolution des Ventes",
                          line_shape='spline', color_discrete_sequence=['#007bad'])
            st.plotly_chart(fig, use_container_width=True)

        # Carte géographique
            st.markdown("---")
    st.subheader("Répartition Géographique")

    geocoded_sales = geocode_data(filtered_sales)

    if not geocoded_sales.empty and 'Latitude' in geocoded_sales.columns and 'Longitude' in geocoded_sales.columns:
        # Filtrer les lignes avec coordonnées valides
        valid_geocodes = geocoded_sales.dropna(subset=['Latitude', 'Longitude'])

        if not valid_geocodes.empty:
            # Création de la carte avec position moyenne ou centre par défaut (Europe)
            avg_lat = valid_geocodes['Latitude'].mean()
            avg_lon = valid_geocodes['Longitude'].mean()
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)

            # Ajout des marqueurs
            for _, row in valid_geocodes.iterrows():
                popup_text = (
                    f"<strong>{row.get('City', '')}, {row.get('Country', '')}</strong><br>"
                    f"Ventes : €{row['Total_sale']:,.2f}"
                )
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=max(row['Total_sale'] / 1000, 5),  # Minimum 5 pour être visible
                    popup=popup_text,
                    color='#007bad',
                    fill=True,
                    fill_opacity=0.7,
                    fill_color='#00afe1'
                ).add_to(m)

            # Mise en page : carte + tableau à côté
            col1, col2 = st.columns([3, 2])
            with col1:
                st_folium(m, width=800, height=500)

            with col2:
                display_df = valid_geocodes[['Country', 'City', 'Total_sale', 'Latitude', 'Longitude']]
                st.dataframe(display_df.sort_values(by='Total_sale', ascending=False), height=500)
        else:
            st.warning("Aucune coordonnée géographique valide trouvée.")
    else:
        st.warning("Données insuffisantes pour générer la carte.")


def recolts_page(recolts_df, staff_df, start_date, end_date):
    """Affiche la page des récoltes."""
    st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Global Recolts Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #007bad; margin-top: 0;'>All Teams</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtres
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        country_filter = st.selectbox("Filtrer par Pays", ['Tous'] + sorted(recolts_df['Country'].dropna().unique()), key='recolts_country')
    with col2:
        team_filter = st.selectbox("Sélectionner équipe", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()), key='recolts_team')
    with col3:
        activity_filter = st.selectbox("Sélectionner activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()), key='recolts_activity')
    
    filtered_recolts = filter_data(recolts_df, country_filter, team_filter, activity_filter, start_date, end_date, staff_df)
    
    if not filtered_recolts.empty:
        # Métriques
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Recolts", f"€{filtered_recolts['Total_Recolt'].sum():,.0f}".replace(",", " "))
        col2.metric("Average Recolt", f"€{filtered_recolts['Total_Recolt'].mean():,.2f}".replace(",", " "))
        col3.metric("Transactions", len(filtered_recolts))
        
        st.markdown("---")
        
        # Graphiques
        if 'Banques' in filtered_recolts.columns:
            st.subheader("Répartition par Banque")
            recolts_by_bank = filtered_recolts.groupby('Banques')['Total_Recolt'].sum().reset_index()
            
            col1, col2 = st.columns([3, 2])
            with col1:
                fig = px.bar(recolts_by_bank, x='Banques', y='Total_Recolt', 
                            title="Montant récolté par Banque",
                            color='Banques', color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.pie(recolts_by_bank, names='Banques', values='Total_Recolt',
                            title="Répartition par Banque", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
        
        # Affichage des données
        st.markdown("---")
        st.subheader("Données Détailées")
        st.dataframe(
            filtered_recolts,
            column_config={
                "ORDER_DATE": st.column_config.DateColumn("Date"),
                "Total_Recolt": st.column_config.NumberColumn("Montant", format="€%.2f")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("Aucune donnée de récolte à afficher pour les critères sélectionnés")

def dashboard_page(sales_df, recolts_df, staff_df, start_date, end_date):
    """Affiche le tableau de bord principal."""
    st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Dashboard Global</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #00afe1;'>Analyse Commerciale - Sales - Recolts</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Onglets
    tab1, tab2 = st.tabs(["📈 Sales Analytics", "💰 Recolts Analytics"])
    
    with tab1:
        sales_page(sales_df, staff_df, start_date, end_date)
    
    with tab2:
        recolts_page(recolts_df, staff_df, start_date, end_date)

def planning_page(sales_df, staff_df):
    """Affiche la page de planning."""
    st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Planning</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #007bad; margin-top: 0;'>All Teams</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtre par pays
    selected_country = st.selectbox("Sélectionner un pays", sorted(sales_df['Country'].unique()), key='country_filter')
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
    """Affiche la page des paramètres."""
    st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Paramètres</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #007bad; margin-top: 0;'>Gestion des Utilisateurs</h2>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h2 style='font-size: 28px; font-weight: bold; color: #00afe1;'>Paramètres Utilisateur</h2>", unsafe_allow_html=True)
    
    hyp_input = st.text_input("Entrez l'ID (Hyp) de l'utilisateur")
    
    if hyp_input:
        user_details = get_user_details(hyp_input)
        
        if user_details:
            date_in = user_details[2]
            anciennete = (datetime.now().date() - date_in.date()).days // 365
            
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.markdown("<h3 style='color: #002a48;'>Informations Professionnelles</h3>", unsafe_allow_html=True)
                st.write(f"**Nom:** {user_details[0]}")
                st.write(f"**Prénom:** {user_details[1]}")
                st.write(f"**Date d'entrée:** {date_in.strftime('%d/%m/%Y')}")
                st.write(f"**Ancienneté:** {anciennete} ans")
            
            with col2:
                st.markdown("<h3 style='color: #002a48;'>Détails</h3>", unsafe_allow_html=True)
                st.write(f"**Team:** {user_details[3]}")
                st.write(f"**Type:** {user_details[4]}")
                st.write(f"**Activité:** {user_details[5]}")
                st.write(f"**Nom d'utilisateur:** {user_details[6]}")
                st.write(f"**Dernière connexion:** {user_details[7] if user_details[7] else 'Jamais'}")
            
            with col3:
                st.markdown("<h3 style='color: #007bad;'>Actions</h3>", unsafe_allow_html=True)
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

def main():
    """Fonction principale de l'application."""
    add_custom_css()
    
    # Vérification de l'authentification
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        login_page()
        return
    
    # Chargement des données
    with st.spinner('Chargement des données...'):
        sales_df, recolts_df, staff_df = load_data()
        sales_df = preprocess_data(sales_df)
        recolts_df = preprocess_data(recolts_df)
        staff_df = preprocess_data(staff_df)
    
    # Dates par défaut
    start_date = pd.to_datetime("2023-01-01").date()
    end_date = pd.to_datetime("2023-12-31").date()
    
    # Navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown(f"**Connecté en tant que:** {st.session_state.username}")
    
    page = st.sidebar.radio("Menu", 
                           ["Dashboard", "Sales", "Recolts", "Planning", "Settings"],
                           index=0)
    
    if page == "Dashboard":
        dashboard_page(sales_df, recolts_df, staff_df, start_date, end_date)
    elif page == "Sales":
        sales_page(sales_df, staff_df, start_date, end_date)
    elif page == "Recolts":
        recolts_page(recolts_df, staff_df, start_date, end_date)
    elif page == "Planning":
        planning_page(sales_df, staff_df)
    elif page == "Settings":
        setting_page()

if __name__ == "__main__":
    main()