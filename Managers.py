import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_option_menu import option_menu
from Utils_Dental import *




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

def geocode_data(df):
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        return df
    
    geolocator = Nominatim(user_agent="sales_dashboard")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    locations = []
    for _, row in df[['City', 'Country']].drop_duplicates().iterrows():
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
        return pd.merge(df, pd.DataFrame(locations), on=['City', 'Country'], how='left')
    return df

def manager_dashboard():





    sales_df, staff_df = load_data()
    sales_df = preprocess_data(sales_df)
    staff_df = preprocess_data(staff_df)

    with st.sidebar:
        st.image('Dental_Implant.png', width=350)
        
        if st.session_state.get("user_type") == "Hyperviseur":
            menu_options = ["Tableau de bord", "Sales", "Recolt", "Logs","Coaching", "Planning", "Setting"]
            icons = ["bar-chart", "currency-dollar", "list-ul", "calendar","calendar","calendar", "gear"]
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

    # Gestion des pages
    if selected == "Tableau de bord":
        display_dashboard(sales_df, staff_df, start_date, end_date)
    elif selected == "Sales":
        display_sales(sales_df, staff_df, start_date, end_date)
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
            
            st.metric("Ventes Totales", f"€{filtered_sales['Total_sale'].sum():,.2f}".replace(",", " "))
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
    elif selected == "Setting":
        setting_page()



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
                SELECT Hyp, Banques, ORDER_REFERENCE, ORDER_DATE, SHORT_MESSAGE, Country, City, Total_Recolt, Id_Recolt 
                FROM Recolts""")
            Recolts_df = pd.DataFrame.from_records(cursor.fetchall(), 
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

def geocode_data(df):
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        return df
    
    geolocator = Nominatim(user_agent="sales_dashboard")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    locations = []
    for _, row in df[['City', 'Country']].drop_duplicates().iterrows():
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
        return pd.merge(df, pd.DataFrame(locations), on=['City', 'Country'], how='left')
    return df

def display_dashboard(sales_df, staff_df, start_date, end_date):
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image('Dental_Implant2.png', width=150)
    with col2:
        st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Dashboard Global</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #00afe1;'>Analyse Commerciale - Sales</h2>", unsafe_allow_html=True)
    
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
            # Ventes par ville
            ventes_ville = filtered_sales.groupby('City')['Total_sale'].sum().reset_index()
            fig = px.bar(ventes_ville, x='City', y='Total_sale', title="Ventes par Ville")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Évolution temporelle
            ventes_date = filtered_sales.groupby(filtered_sales['ORDER_DATE'].dt.date)['Total_sale'].sum().reset_index()
            fig = px.line(ventes_date, x='ORDER_DATE', y='Total_sale', title="Évolution des Ventes")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucune donnée à afficher pour les critères sélectionnés")

def display_sales(sales_df, staff_df, start_date, end_date):
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
    
    # Affichage des données
    st.dataframe(filtered_sales)

def display_planning(sales_df, staff_df):
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
        # Ventes par ville
        ventes_ville = filtered_sales.groupby('City')['Total_sale'].sum().reset_index()
        fig = px.bar(ventes_ville, x='City', y='Total_sale', title="Ventes par Ville")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Effectifs par équipe
        if not staff_df.empty:
            effectifs = staff_df[staff_df['Country'] == selected_country] if 'Country' in staff_df.columns else staff_df
            fig = px.pie(effectifs, names='Team', title="Répartition des Effectifs")
            st.plotly_chart(fig, use_container_width=True)
