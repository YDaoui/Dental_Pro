
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
from Managers import *
from Logs import *
from Recolts import *

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
            st.plotly_chart(fig, use_container_width=True, key="ventes_par_ville")

        with col2:
            status_sales = filtered_sales.groupby('SHORT_MESSAGE')['Total_sale'].sum().reset_index()
            
            fig = px.pie(status_sales, 
                        values='Total_sale', 
                        names='SHORT_MESSAGE',
                        title="Statut des Transactions :",
                        color='SHORT_MESSAGE',
                        color_discrete_map={'ACCEPTED': '#007bad', 'REFUSED': '#ff0000'},
                        hole=0.5)
            
            fig.update_traces(
                textinfo='value+percent',
                textposition='outside',
                textfont_size=12,
                textfont_color=['#007bad', '#ff0000'],
                marker=dict(line=dict(color='white', width=2)),
                pull=[0.05, 0],
                rotation=-90,
                direction='clockwise'
            )
            
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
            
            st.plotly_chart(fig, use_container_width=True, key="statut_transactions")

        with col3:
            ventes_date = filtered_sales.groupby(filtered_sales['ORDER_DATE'].dt.date)['Total_sale'].sum().reset_index()
            fig = px.line(ventes_date, x='ORDER_DATE', y='Total_sale', title="Évolution des Ventes",
                      line_shape='spline', color_discrete_sequence=['#007bad'])
            st.plotly_chart(fig, use_container_width=True, key="evolution_ventes")

        # Carte géographique
        st.markdown("---")
        st.subheader("Répartition Géographique")

        geocoded_sales = geocode_data(filtered_sales)

        if not geocoded_sales.empty and 'Latitude' in geocoded_sales.columns and 'Longitude' in geocoded_sales.columns:
            valid_geocodes = geocoded_sales.dropna(subset=['Latitude', 'Longitude'])

            if not valid_geocodes.empty:
                avg_lat = valid_geocodes['Latitude'].mean()
                avg_lon = valid_geocodes['Longitude'].mean()
                m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)

                for _, row in valid_geocodes.iterrows():
                    popup_text = (
                        f"<strong>{row.get('City', '')}, {row.get('Country', '')}</strong><br>"
                        f"Ventes : €{row['Total_sale']:,.2f}"
                    )
                    folium.CircleMarker(
                        location=[row['Latitude'], row['Longitude']],
                        radius=max(row['Total_sale'] / 1000, 5),
                        popup=popup_text,
                        color='#007bad',
                        fill=True,
                        fill_opacity=0.7,
                        fill_color='#00afe1'
                    ).add_to(m)

                col1, col2 = st.columns([1, 1])
                with col1:
                    st_folium(m, width=1000, height=600, key="carte_geographique")
             
                with col2:
                    display_df = valid_geocodes[['Country', 'City', 'Total_sale', 'Latitude', 'Longitude']]
                    st.dataframe(display_df.sort_values(by='Total_sale', ascending=False), 
                                height=500,
                                key="tableau_geographique")
            else:
                st.warning("Aucune coordonnée géographique valide trouvée.")
        else:
            st.warning("Données insuffisantes pour générer la carte.")