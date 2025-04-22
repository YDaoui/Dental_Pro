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
from Logs import *

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
                st_folium(m, width=1000, height=600)

            with col2:
                display_df = valid_geocodes[['Country', 'City', 'Total_Recolt', 'Latitude', 'Longitude']]
                st.dataframe(display_df.sort_values(by='Total_Recolt', ascending=False), height=500)
               
        else:
            st.warning("Aucune coordonnée géographique valide trouvée.")
    else:
        st.warning("Données insuffisantes pour générer la carte.")