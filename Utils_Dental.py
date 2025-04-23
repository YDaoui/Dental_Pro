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
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

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
            
            # Chargement des logs
            cursor.execute("""
                SELECT 
                    Hyp,
                    Num_Activity,
                    Num_Bp,
                    [Sous motif] as Sous_motif,
                    Canal,
                    Direction,
                    [Date de création] as Date_creation,
                    Qualification,
                    [Heure création] as Heure_creation,
                    Offre,
                    [Date ancienneté client] as Date_anciennete_client,
                    Segment,
                    [Statut BP] as Statut_BP,
                    [mode de facturation] as Mode_facturation,
                    [ancienneté client] as Anciennete_client,
                    Heure,
                    Id_Log 
                FROM Logs
                WHERE Offre <> 'AB'
            """)
            logs_df = pd.DataFrame.from_records(cursor.fetchall(),
                                              columns=[column[0] for column in cursor.description])

            # Chargement du staff
            cursor.execute("""
                SELECT Hyp, Team, Activité, Date_In, Type 
                FROM Effectifs
                WHERE Type = 'Agent'
            """)
            staff_df = pd.DataFrame.from_records(cursor.fetchall(),
                                               columns=[column[0] for column in cursor.description])

        return sales_df, recolts_df, staff_df, logs_df
    except Exception as e:
        st.error(f"Erreur de chargement des données: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
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
    if 'Date_creation' in df.columns:
        df['Date_creation'] = pd.to_datetime(df['Date_creation'], errors='coerce')
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
def logs_page(logs_df, start_date, end_date):
    """Affiche la page des logs avec les filtres spécifiés."""
    st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Logs Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #007bad; margin-top: 0;'>Analyse des Logs</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # Filtrage temporel initial
    mask = (logs_df['Date_creation'] >= pd.to_datetime(start_date)) & \
           (logs_df['Date_creation'] <= pd.to_datetime(end_date))
    filtered_logs = logs_df.loc[mask].copy()

    # Vérification de l'existence de la colonne 'Groupe_Origine'


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
        
        

    # Application des filtres
    if segment_filter != 'Tous':
        filtered_logs = filtered_logs[filtered_logs['Segment'] == segment_filter]
    
        
    if statut_bp_filter != 'Tous':
        filtered_logs = filtered_logs[filtered_logs['Statut_BP'] == statut_bp_filter]



    
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
        #st.plotly_chart(fig1, use_container_width=True)

        # Graphique 2: Evolution temporelle
        daily_logs = filtered_logs.groupby(filtered_logs['Date_creation'].dt.date).size().reset_index(name='Count')
        fig2 = px.line(
            daily_logs,
            x='Date_creation',
            y='Count',
            title="Volume de Logs par Jour",
            line_shape='spline'
        )
        fig3 = px.pie(
            filtered_logs,
            names='Offre',
            title="Répartition par Offre",
            color='Offre',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        col1, col2 , col3 = st.columns(3)
    
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.plotly_chart(fig2, use_container_width=True)
        with col3:
            st.plotly_chart(fig3, use_container_width=True)


        # Tableau de données
        st.markdown("---")
        st.subheader("Données Détailées")
        st.dataframe(filtered_logs.sort_values('Date_creation', ascending=False))
    else:
        st.warning("Aucune donnée disponible avec les filtres sélectionnés.")

# Affichage de la page Ventes
def sales_page(sales_df, staff_df, start_date, end_date):
    """Affiche la page des ventes."""
    #st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Global Sales Dashboard</h1>", unsafe_allow_html=True)
    #st.markdown("<h2 style='color: #007bad; margin-top: 0;'>All Teams</h2>", unsafe_allow_html=True)
    #st.markdown("---")

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
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        ventes_ville = filtered_sales.groupby('City')['Total_sale'].sum().reset_index()
        fig = px.bar(ventes_ville, x='City', y='Total_sale', title="Ventes par Ville",
                 color='Total_sale', color_continuous_scale=['#00afe1', '#007bad'])
        st.plotly_chart(fig, use_container_width=True)

    with col2:


        status_sales = filtered_sales.groupby('SHORT_MESSAGE')['Total_sale'].sum().reset_index()
        
        # Création du graphique semi-circulaire
        fig = px.pie(status_sales, 
                    values='Total_sale', 
                    names='SHORT_MESSAGE',
                    title="Statut des Transactions :",
                    color='SHORT_MESSAGE',
                    color_discrete_map={'ACCEPTED': '#007bad', 'REFUSED': '#ff0000'},  # Bleu et rouge vif
                    hole=0.5)
        
        # Personnalisation avancée
        fig.update_traces(
            textinfo='value+percent',  # Affiche valeur et pourcentage
            textposition='outside',    # Infobulles externes
            textfont_size=12,
            textfont_color=['#007bad', '#ff0000'],  # Couleur texte adaptée
            marker=dict(line=dict(color='white', width=2)),  # Contour blanc
            pull=[0.05, 0],           # Légère séparation
            rotation=-90,             # Commence à 12h
            direction='clockwise'
        )
        
        # Mise en page finale
        fig.update_layout(
            showlegend=False,
            margin=dict(t=100, b=50, l=50, r=50),
            annotations=[
                dict(
                    text=f"Total: {status_sales['Total_sale'].sum():,.0f}€",
                    x=0.5, y=0.5,
                    font_size=14,
                    showarrow=False,
                    font=dict(color='#333333')
                )
            ],
            uniformtext_minsize=10,
            uniformtext_mode='hide'
        )
        
        st.plotly_chart(fig, use_container_width=True)
            

    with col3:
    
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
            col1, col2 = st.columns([1, 1])
            with col1:
                #st_folium(m, width=1000, height=600)
                st.subheader("Remplacement de Geolocalisation ")
            with col2:
                display_df = valid_geocodes[['Country', 'City', 'Total_sale', 'Latitude', 'Longitude']]
                st.dataframe(display_df.sort_values(by='Total_sale', ascending=False), height=500)
               
        else:
            st.warning("Aucune coordonnée géographique valide trouvée.")
    else:
        st.warning("Données insuffisantes pour générer la carte.")


def recolts_page(recolts_df, staff_df, start_date, end_date):
    """Affiche la page des récoltes avec les nouvelles modifications."""
    st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Global Recolts Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #007bad; margin-top: 0;'>All Teams</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Nouveaux filtres sur 4 colonnes
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        country_filter = st.selectbox("Filtrer par Pays", ['Tous'] + sorted(recolts_df['Country'].dropna().unique()), key='recolts_country')
    with col2:
        team_filter = st.selectbox("Sélectionner équipe", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()), key='recolts_team')
    with col3:
        activity_filter = st.selectbox("Sélectionner activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()), key='recolts_activity')
    with col4:
        bank_filter = st.selectbox("Filtrer par Banque", ['Toutes'] + sorted(recolts_df['Banques'].dropna().unique()), key='recolts_bank')
    
    # Filtrage des données
    with st.spinner("Application des filtres..."):
        filtered_recolts = recolts_df.copy()
        
        if country_filter != 'Tous':
            filtered_recolts = filtered_recolts[filtered_recolts['Country'] == country_filter]
        
        if bank_filter != 'Toutes':
            filtered_recolts = filtered_recolts[filtered_recolts['Banques'] == bank_filter]
        
        if 'Hyp' in filtered_recolts.columns and not staff_df.empty:
            staff_filtered = staff_df.copy()
            if team_filter != 'Toutes':
                staff_filtered = staff_filtered[staff_filtered['Team'] == team_filter]
            if activity_filter != 'Toutes':
                staff_filtered = staff_filtered[staff_filtered['Activité'] == activity_filter]
            filtered_recolts = filtered_recolts[filtered_recolts['Hyp'].isin(staff_filtered['Hyp'])]
    
    if not filtered_recolts.empty:
        # Métriques
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Recolts", f"€{filtered_recolts['Total_Recolt'].sum():,.0f}".replace(",", " "))
        col2.metric("Average Recolt", f"€{filtered_recolts['Total_Recolt'].mean():,.2f}".replace(",", " "))
        col3.metric("Transactions", len(filtered_recolts))
        
        st.markdown("---")
        
        # Nouvelle disposition des graphiques
        col1, col2, col3 = st.columns([4, 3, 5])
        with col1:
        
        # Graphique 1: Total recolts par banque avec pourcentage

            recolts_by_bank = filtered_recolts.groupby('Banques')['Total_Recolt'].sum().reset_index()
            total = recolts_by_bank['Total_Recolt'].sum()
            recolts_by_bank['Percentage'] = (recolts_by_bank['Total_Recolt'] / total * 100).round(1)

            # Création du graphique avec couleur bleue unifiée
            fig = px.bar(recolts_by_bank, 
                        x='Banques', 
                        y='Total_Recolt',
                        text='Percentage',
                        title="Total Recolts par Banque (%)",
                        color_discrete_sequence=['#007bad'])  # Couleur bleue unifiée

            # Personnalisation avancée
            fig.update_traces(
                texttemplate='%{text}%', 
                textposition='outside',
                marker=dict(
                    color='#007bad',  # Couleur bleue pour toutes les barres
                    line=dict(color='#005b8c', width=2)  # Contour plus foncé
                ),
                opacity=0.8  # Légère transparence
            )

            # Amélioration de la mise en page
            fig.update_layout(
                uniformtext_minsize=10,
                uniformtext_mode='hide',
                plot_bgcolor='rgba(0,0,0,0)',  # Fond transparent
                xaxis=dict(
                    title='Banques',
                    tickangle=-45  # Inclinaison des labels
                ),
                yaxis=dict(
                    title='Montant (€)',
                    gridcolor='lightgray'
                ),
                hoverlabel=dict(
                    bgcolor='white',
                    font_size=12
                )
            )

            # Affichage avec largeur ajustée
            st.plotly_chart(fig, use_container_width=True)
        with col2:           
        # Graphique 2: Demi-cercle Accepted/Refused

            if 'SHORT_MESSAGE' in filtered_recolts.columns:
                status_recolts = filtered_recolts.groupby('SHORT_MESSAGE')['Total_Recolt'].sum().reset_index()
                
                fig = px.pie(status_recolts,
                             values='Total_Recolt',
                             names='SHORT_MESSAGE',
                             title="Statut des Recolts",
                             color='SHORT_MESSAGE',
                             color_discrete_map={'ACCEPTED': '#007bad', 'REFUSED': '#ff0000'},
                             hole=0.5)
                
                fig.update_traces(textinfo='value+percent',
                                textposition='outside',
                                textfont_color=['#007bad', '#ff0000'],
                                marker=dict(line=dict(color='white', width=2)),
                                pull=[0.05, 0],
                                rotation=-90,
                                direction='clockwise')
                
                fig.update_layout(showlegend=False,
                                annotations=[dict(text=f"Total: {status_recolts['Total_Recolt'].sum():,.0f}€",
                                                x=0.5, y=0.5,
                                                showarrow=False)])
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Graphique 3: Evolution temporelle
        with col3:
            recolts_by_date = filtered_recolts.groupby(filtered_recolts['ORDER_DATE'].dt.date)['Total_Recolt'].sum().reset_index()
            
            fig = px.line(recolts_by_date,
                          x='ORDER_DATE',
                          y='Total_Recolt',
                          title="Evolution des Recolts par Date",
                          line_shape='spline',
                          color_discrete_sequence=['#007bad'])
            
            fig.update_traces(mode='lines+markers', marker=dict(size=6))
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Affichage des données détaillées
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

        # Carte géographique
        st.markdown("---")
    st.subheader("Répartition Géographique")

    geocoded_recolt = geocode_data(filtered_recolts)

    if not geocoded_recolt.empty and 'Latitude' in geocoded_recolt.columns and 'Longitude' in geocoded_recolt.columns:
        # Filtrer les lignes avec coordonnées valides
        valid_geocodes = geocoded_recolt.dropna(subset=['Latitude', 'Longitude'])

        if not valid_geocodes.empty:
            # Création de la carte avec position moyenne ou centre par défaut (Europe)
            avg_lat = valid_geocodes['Latitude'].mean()
            avg_lon = valid_geocodes['Longitude'].mean()
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)

            # Ajout des marqueurs
            for _, row in valid_geocodes.iterrows():
                popup_text = (
                    f"<strong>{row.get('City', '')}, {row.get('Country', '')}</strong><br>"
                    f"Ventes : €{row['Total_Recolt']:,.2f}"
                )
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=max(row['Total_Recolt'] / 1000, 5),  # Minimum 5 pour être visible
                    popup=popup_text,
                    color='#007bad',
                    fill=True,
                    fill_opacity=0.7,
                    fill_color='#00afe1'
                ).add_to(m)

            # Mise en page : carte + tableau à côté
            col1, col2 = st.columns([1, 1])
            with col1:
                #st_folium(m, width=1000, height=600)
                 st.subheader("Remplacement de Geolocalisation ")
            with col2:
                display_df = valid_geocodes[['Country', 'City', 'Total_Recolt', 'Latitude', 'Longitude']]
                st.dataframe(display_df.sort_values(by='Total_Recolt', ascending=False), height=500)
               
        else:
            st.warning("Aucune coordonnée géographique valide trouvée.")
    else:
        st.warning("Données insuffisantes pour générer la carte.")

def dashboard_page(logs_df,sales_df, recolts_df, staff_df, start_date, end_date):

    """Affiche le tableau de bord principal."""
    st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Dashboard Global</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #00afe1;'>Analyse Commerciale - Sales - Recolts - Logs </h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Onglets
    tab1, tab2,tab3 = st.tabs(["📈 Sales Analytics", "💰 Recolts Analytics", "🧾 Logs Analytics"])
    
    with tab1:
        sales_page(sales_df, staff_df, start_date, end_date)
    
    with tab2:
        recolts_page(recolts_df, staff_df, start_date, end_date)
    with tab3:
        logs_page(logs_df, start_date, end_date)

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
        st.subheader("Remplacement de Geolocalisation ")
        #st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not staff_df.empty:
            effectifs = staff_df[staff_df['Country'] == selected_country] if 'Country' in staff_df.columns else staff_df
            fig = px.pie(effectifs, names='Team', title="Répartition des Effectifs")
            st.subheader("Remplacement de Geolocalisation ")
            #st.plotly_chart(fig, use_container_width=True)

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
        sales_df, recolts_df, staff_df , logs_df = load_data()
        logs_df = preprocess_data(logs_df)
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
    elif page == "Logs":
         logs_page(logs_df, start_date, end_date)      
    elif page == "Plannings":
        planning_page(sales_df, staff_df)
    elif page == "Settings":
        setting_page()

if __name__ == "__main__":
    main()