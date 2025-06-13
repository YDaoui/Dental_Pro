import streamlit as st
import pandas as pd

from contextlib import closing
from datetime import datetime,timedelta  
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Définition de la palette de couleurs harmonisée
COLOR_PALETTE = {
    "primary": "#0a7fac",
    "secondary": "#043a64",
    "accent1": "#ffc107",
    "accent2": "#fc9307",
    "success": "#4CAF50",
    "light_bg": "#f0fff0"
}

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

def filter_recolts_data(df, country_filter, team_filter, activity_filter, agent_filter, start_date, end_date, staff_df):
    """Filtre les données de recolts selon les critères."""
    filtered_df = df.copy()

    if 'ORDER_DATE' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['ORDER_DATE'] >= pd.to_datetime(start_date)) &
            (filtered_df['ORDER_DATE'] <= pd.to_datetime(end_date))
        ]

    if country_filter != 'Tous' and 'Country' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Country'] == country_filter]
    
    if 'Hyp' in filtered_df.columns and not staff_df.empty:
        staff_filtered = staff_df.copy()

        if 'NOM' in staff_filtered.columns and 'PRENOM' in staff_filtered.columns:
            staff_filtered['NOM PRENOM'] = staff_filtered['NOM'] + ' ' + staff_filtered['PRENOM']
        
        if activity_filter != 'Toutes':
            staff_filtered = staff_filtered[staff_filtered['Activité'] == activity_filter]

        if team_filter != 'Toutes':
            staff_filtered = staff_filtered[staff_filtered['Team'] == team_filter]
               
        if agent_filter != 'Tous':
            if 'NOM PRENOM' in staff_filtered.columns:
                staff_filtered = staff_filtered[staff_filtered['NOM PRENOM'] == agent_filter]
            else:
                st.warning("Could not filter by agent name. Falling back to filtering by 'Hyp' if agent filter matches.")
                staff_filtered = staff_filtered[staff_filtered['Hyp'] == agent_filter]

        if 'Hyp' in staff_filtered.columns:
            filtered_df = filtered_df[filtered_df['Hyp'].isin(staff_filtered['Hyp'])]

    return filtered_df

def create_line_chart_for_kpi(df, x_col, y_col, title, value_prefix="", y_label="", line_color=COLOR_PALETTE["primary"], global_start_date=None, global_end_date=None):
    """
    Crée un graphique linéaire pour la tendance d'un KPI.
    """
    if df.empty:
        return None

    fig = px.line(df,
                  x=x_col,
                  y=y_col,
                  title=title,
                  labels={y_col: y_label},
                  line_shape='spline',
                  color_discrete_sequence=[line_color])

    fig.update_traces(
        mode='lines+markers',
        marker=dict(size=8, color=line_color, line=dict(width=1, color='#FFFFFF')),
        hovertemplate=f'{x_col}: %{{x|%Y-%m-%d}}<br>{y_label}: {value_prefix}%{{y:,.2f}}<extra></extra>',
        fill='tozeroy',
        fillcolor=f'rgba({int(line_color[1:3], 16)}, {int(line_color[3:5], 16)}, {int(line_color[5:7], 16)}, 0.2)'
    )

    x_axis_range = None
    if global_start_date and global_end_date:
        x_axis_range = [global_start_date, global_end_date + timedelta(days=1)]

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        xaxis_gridcolor='#E0E0E0',
        yaxis_gridcolor='#E0E0E0',
        xaxis=dict(
            tickfont=dict(size=12, color='#3D3B40'),
            tickformat='%Y-%m-%d',
            range=x_axis_range
        ),
        yaxis=dict(
            range=[0, df[y_col].max() * 1.2],
            tickfont=dict(size=12, color='#3D3B40')
        ),
        font=dict(family='Arial', size=12, color='#3D3B40'),
        margin=dict(t=30, b=30, l=30, r=30),
        title=dict(x=0.05, y=0.95, xanchor='left', yanchor='top', font=dict(size=16, color=COLOR_PALETTE["primary"])))
    return fig

def recolts_page1(recolts_df, staff_df, start_date, end_date):
    """Affiche la page des récoltes avec la palette de couleurs harmonisée."""

    if 'NOM' in staff_df.columns and 'PRENOM' in staff_df.columns:
        staff_df['NOM PRENOM'] = staff_df['NOM'] + ' ' + staff_df['PRENOM']
    else:
        st.warning("Columns 'NOM' and/or 'PRENOM' not found in staff data. Agent filter will use 'Hyp'.")
    
    if 'ORDER_DATE' in recolts_df.columns:
        recolts_df['ORDER_DATE'] = pd.to_datetime(recolts_df['ORDER_DATE'])

    col1, col2 = st.columns([2, 2])

    with col1:
        st.markdown(
            f"<h1 style='text-align: left; color: {COLOR_PALETTE['secondary']}; margin-bottom: 0;'>Récolts Dashboard</h1>", 
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"<h1 style='text-align: right; color: {COLOR_PALETTE['primary']}; margin-bottom: 0;'>Analyse des Résolts</h1>", 
            unsafe_allow_html=True
        )

    # Filters
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2,2])
    with col1:
        country_filter = st.selectbox("Filtrer par Pays", ['Tous'] + sorted(recolts_df['Country'].dropna().unique()), key='recolts_country_filter')
    with col2:
        activity_filter = st.selectbox("Sélectionner activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()), key='recolts_activity_filter')
    with col3:
        team_filter = st.selectbox("Sélectionner équipe", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()), key='recolts_team_filter')
        
    with col4:
        agents_in_team = ['Tous']
        if team_filter != 'Toutes':
            filtered_staff_for_dropdown = staff_df[staff_df['Team'] == team_filter]
            if 'NOM PRENOM' in filtered_staff_for_dropdown.columns:
                agents_in_team += sorted(filtered_staff_for_dropdown['NOM PRENOM'].dropna().unique())
            else:
                agents_in_team += sorted(filtered_staff_for_dropdown['Hyp'].dropna().unique())
        agent_filter = st.selectbox("Sélectionner Agent", agents_in_team, key='recolts_agent_filter')
    with col5:
        bank_filter = st.selectbox("Filtrer par Banque", ['Toutes'] + sorted(recolts_df['Banques'].dropna().unique()), key='recolts_bank_filter')

    # Filter data
    with st.spinner("Application des filtres..."):
        filtered_recolts = filter_recolts_data(recolts_df, country_filter, team_filter, activity_filter, agent_filter, start_date, end_date, staff_df)
        
        if bank_filter != 'Toutes':
            filtered_recolts = filtered_recolts[filtered_recolts['Banques'] == bank_filter]

    if not filtered_recolts.empty:
        global_start_date_dt = pd.to_datetime(start_date).date()
        global_end_date_dt = pd.to_datetime(end_date).date()

        # Métriques / KPIs
        col1_kpi, col2_kpi, col3_kpi = st.columns(3)

        with col1_kpi:
            st.markdown(f"""
                <div style='
                    border: 2px solid {COLOR_PALETTE['primary']}; 
                    border-radius: 10px; 
                    padding: 15px; 
                    text-align: center; 
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                    background-color: {COLOR_PALETTE['light_bg']};
                '>
                    <h3 style='color: #333333; margin-bottom: 5px;'>Total Récoltes</h3>
                    <p style='font-size: 24px; color: {COLOR_PALETTE['primary']}; font-weight: bold;'>{filtered_recolts['Total_Recolt'].sum():,.0f} €</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Tendance des Récoltes Totales"):
                daily_recolts_trend = filtered_recolts.groupby(filtered_recolts['ORDER_DATE'].dt.date)['Total_Recolt'].sum().reset_index()
                daily_recolts_trend.columns = ['Date', 'Total_Recolt']
                daily_recolts_trend['Date'] = pd.to_datetime(daily_recolts_trend['Date'])
                
                if not daily_recolts_trend.empty:
                    trend_min_date = daily_recolts_trend['Date'].min()
                    trend_max_date = daily_recolts_trend['Date'].max()
                else:
                    trend_min_date = global_start_date_dt
                    trend_max_date = global_end_date_dt
                    
                full_date_range = pd.date_range(start=trend_min_date, end=trend_max_date, freq='D')
                daily_recolts_trend = daily_recolts_trend.set_index('Date').reindex(full_date_range, fill_value=0).reset_index()
                daily_recolts_trend.rename(columns={'index': 'Date'}, inplace=True)

                if not daily_recolts_trend.empty:
                    fig_total_recolts_trend = create_line_chart_for_kpi(
                        daily_recolts_trend, 'Date', 'Total_Recolt', 'Tendance des Récoltes Quotidiennes', '€', 'Récoltes (€)', 
                        line_color=COLOR_PALETTE["primary"],
                        global_start_date=global_start_date_dt, 
                        global_end_date=global_end_date_dt
                    )
                    st.plotly_chart(fig_total_recolts_trend, use_container_width=True)
                else:
                    st.info("Pas de données de récoltes pour cette période.")

        with col2_kpi:
            st.markdown(f"""
                <div style='
                    border: 2px solid {COLOR_PALETTE['primary']}; 
                    border-radius: 10px; 
                    padding: 15px; 
                    text-align: center; 
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                    background-color: {COLOR_PALETTE['light_bg']};
                '>
                    <h3 style='color: #333333; margin-bottom: 5px;'>Récolte Moyenne</h3>
                    <p style='font-size: 24px; color: {COLOR_PALETTE['primary']}; font-weight: bold;'>{filtered_recolts['Total_Recolt'].mean():,.2f} €</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Tendance de la Récolte Moyenne"):
                daily_avg_recolts_trend = filtered_recolts.groupby(filtered_recolts['ORDER_DATE'].dt.date)['Total_Recolt'].mean().reset_index()
                daily_avg_recolts_trend.columns = ['Date', 'Average_Recolt']
                daily_avg_recolts_trend['Date'] = pd.to_datetime(daily_avg_recolts_trend['Date'])
                
                if not daily_avg_recolts_trend.empty:
                    trend_min_date = daily_avg_recolts_trend['Date'].min()
                    trend_max_date = daily_avg_recolts_trend['Date'].max()
                else:
                    trend_min_date = global_start_date_dt
                    trend_max_date = global_end_date_dt

                full_date_range = pd.date_range(start=trend_min_date, end=trend_max_date, freq='D')
                daily_avg_recolts_trend = daily_avg_recolts_trend.set_index('Date').reindex(full_date_range, fill_value=0).reset_index()
                daily_avg_recolts_trend.rename(columns={'index': 'Date'}, inplace=True)

                if not daily_avg_recolts_trend.empty:
                    fig_avg_recolts_trend = create_line_chart_for_kpi(
                        daily_avg_recolts_trend, 'Date', 'Average_Recolt', 'Tendance de la Récolte Moyenne Quotidienne', '€', 'Récolte Moyenne (€)',
                        line_color=COLOR_PALETTE["primary"],
                        global_start_date=global_start_date_dt, 
                        global_end_date=global_end_date_dt
                    )
                    st.plotly_chart(fig_avg_recolts_trend, use_container_width=True)
                else:
                    st.info("Pas de données de récoltes pour cette période.")
        
        with col3_kpi:
            st.markdown(f"""
                <div style='
                    border: 2px solid {COLOR_PALETTE['primary']}; 
                    border-radius: 10px; 
                    padding: 15px; 
                    text-align: center; 
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                    background-color: {COLOR_PALETTE['light_bg']};
                '>
                    <h3 style='color: #333333; margin-bottom: 5px;'>Total Transactions</h3>
                    <p style='font-size: 24px; color: {COLOR_PALETTE['primary']}; font-weight: bold;'>{len(filtered_recolts)}</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Tendance du Nombre de Transactions"):
                daily_transactions_trend = filtered_recolts.groupby(filtered_recolts['ORDER_DATE'].dt.date).size().reset_index(name='Total_Transactions')
                daily_transactions_trend.columns = ['Date', 'Total_Transactions']
                daily_transactions_trend['Date'] = pd.to_datetime(daily_transactions_trend['Date'])
                
                if not daily_transactions_trend.empty:
                    trend_min_date = daily_transactions_trend['Date'].min()
                    trend_max_date = daily_transactions_trend['Date'].max()
                else:
                    trend_min_date = global_start_date_dt
                    trend_max_date = global_end_date_dt

                full_date_range = pd.date_range(start=trend_min_date, end=trend_max_date, freq='D')
                daily_transactions_trend = daily_transactions_trend.set_index('Date').reindex(full_date_range, fill_value=0).reset_index()
                daily_transactions_trend.rename(columns={'index': 'Date'}, inplace=True)

                if not daily_transactions_trend.empty:
                    fig_total_transactions_trend = create_line_chart_for_kpi(
                        daily_transactions_trend, 'Date', 'Total_Transactions', 'Tendance du Nombre de Transactions Quotidiennes', '', 'Transactions',
                        line_color=COLOR_PALETTE["primary"],
                        global_start_date=global_start_date_dt, 
                        global_end_date=global_end_date_dt
                    )
                    st.plotly_chart(fig_total_transactions_trend, use_container_width=True)
                else:
                    st.info("Pas de données de transactions pour cette période.")

        # Principaux Graphiques
        st.markdown(f"<h2 style='text-align: center; color: {COLOR_PALETTE['secondary']};'>Analyses Principales</h2>", unsafe_allow_html=True)
        col_main1, col_main2, col_main3 = st.columns([2, 2, 2])
        with col_main1:
            st.markdown(f"<h3 style='color: {COLOR_PALETTE['primary']};'>Récoltes par Ville</h3>", unsafe_allow_html=True)
            recolts_ville = filtered_recolts.groupby('City')['Total_Recolt'].sum().reset_index()
            fig = px.bar(recolts_ville, y='City', x='Total_Recolt', orientation='h', 
                        color='Total_Recolt', color_continuous_scale=[COLOR_PALETTE['accent1'], COLOR_PALETTE['accent2']])
            fig.update_layout(
                xaxis=dict(title=None, tickfont=dict(size=14, family='Arial', color='black', weight='bold')),
                yaxis=dict(title=None, tickfont=dict(size=14, family='Arial', color='black', weight='bold')),
                showlegend=False,
                coloraxis_showscale=False)
            fig.update_traces(
                text=recolts_ville['Total_Recolt'].apply(lambda x: f"€{x:,.0f}".replace(",", " ")), 
                textposition='outside',
                textfont=dict(size=14, family='Arial', color='black', weight='bold'))
            st.plotly_chart(fig, use_container_width=True, key="recolts_par_ville")

        with col_main2:
            st.markdown(f"<h3 style='color: {COLOR_PALETTE['primary']};'>Statut des Transactions de Récoltes</h3>", unsafe_allow_html=True)
            status_recolts = filtered_recolts.groupby('SHORT_MESSAGE')['Total_Recolt'].sum().reset_index()
            fig = px.pie(status_recolts, 
                        values='Total_Recolt', 
                        names='SHORT_MESSAGE',
                        color='SHORT_MESSAGE',
                        color_discrete_map={'ACCEPTED': COLOR_PALETTE['accent1'], 'REFUSED': COLOR_PALETTE['secondary']},
                        hole=0.5)
            fig.update_traces(
                textinfo='value+percent',
                textposition='outside',
                textfont_size=14,
                textfont_color=[COLOR_PALETTE['accent2'], COLOR_PALETTE['secondary']],
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
                        text=f"Total: {status_recolts['Total_Recolt'].sum():,.0f}€",
                        x=0.5, y=0.5,
                        font_size=14,
                        showarrow=False,
                        font=dict(color='#333333'))
                ],
                uniformtext_minsize=10,
                uniformtext_mode='hide'
            )
            st.plotly_chart(fig, use_container_width=True, key="statut_recolts_pie")

        with col_main3:
            st.markdown(f"<h3 style='color: {COLOR_PALETTE['primary']};'>Récoltes par Banque</h3>", unsafe_allow_html=True)
            if 'Banques' in filtered_recolts.columns:
                recolts_by_bank_bar = filtered_recolts.groupby('Banques')['Total_Recolt'].sum().reset_index()
                fig = px.bar(recolts_by_bank_bar.sort_values(by='Total_Recolt', ascending=False),
                    y='Banques', x='Total_Recolt', orientation='h',
                    color='Total_Recolt', color_continuous_scale=[COLOR_PALETTE['accent1'], COLOR_PALETTE['accent2']])
                fig.update_layout(
                    xaxis=dict(title=None, tickfont=dict(size=14, family='Arial', color='black', weight='bold')),
                    yaxis=dict(title=None, tickfont=dict(size=14, family='Arial', color='black', weight='bold')),
                    showlegend=False,
                    coloraxis_showscale=False)
                fig.update_traces(
                    text=recolts_by_bank_bar['Total_Recolt'].apply(lambda x: f"€{x:,.0f}".replace(",", " ")), 
                    textposition='outside',
                    textfont=dict(size=14, family='Arial', color='black', weight='bold'))
                st.plotly_chart(fig, use_container_width=True, key="recolts_par_banque_bar")
            else:
                st.info("Les données de récoltes ne contiennent pas d'information sur les banques.")

        # Répartition Temporelle Détaillée
        st.markdown(f"<h2 style='text-align: center; color: {COLOR_PALETTE['secondary']};'>Répartition Temporelle Détaillée des Récoltes</h2>", unsafe_allow_html=True)
        col_temp1, col_temp2, col_temp3 = st.columns(3)

        with col_temp1:
            st.markdown(f"<h3 style='color: {COLOR_PALETTE['primary']};'>Récoltes par Jour de la Semaine</h3>", unsafe_allow_html=True)
            filtered_recolts['Weekday'] = filtered_recolts['ORDER_DATE'].dt.weekday
            recolts_jour = filtered_recolts.groupby('Weekday')['Total_Recolt'].sum().reset_index()
            jours = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}
            recolts_jour['Jour'] = recolts_jour['Weekday'].map(jours)
            all_days = pd.DataFrame({'Weekday': range(7)})
            recolts_jour = pd.merge(all_days, recolts_jour, on='Weekday', how='left').fillna(0)
            recolts_jour['Jour'] = recolts_jour['Weekday'].map(jours) 
            recolts_jour = recolts_jour.sort_values('Weekday')

            fig_jour = px.line(recolts_jour,
                                x='Jour',
                                y='Total_Recolt',
                                line_shape='spline',
                                color_discrete_sequence=[COLOR_PALETTE['accent2']])

            fig_jour.update_traces(
                line=dict(width=4, color=COLOR_PALETTE['accent1']),
                mode='lines+markers+text',
                marker=dict(size=10, color='#3D3B40', line=dict(width=1, color='#FFFFFF')), 
                text=[f"€{y:,.0f}" for y in recolts_jour['Total_Recolt']],
                textposition="top center", 
                textfont=dict(color=COLOR_PALETTE['secondary'], size=14, family='Arial', weight='bold'),
                hovertemplate='Jour: %{x}<br>Récoltes: €%{y:,.2f}<extra></extra>',
                fill='tozeroy',
                fillcolor=f'rgba({int(COLOR_PALETTE["accent1"][1:3], 16)}, {int(COLOR_PALETTE["accent1"][3:5], 16)}, {int(COLOR_PALETTE["accent1"][5:7], 16)}, 0.2)'
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
                    tickvals=recolts_jour['Jour'],
                    categoryorder='array', 
                    categoryarray=recolts_jour['Jour'],
                    tickfont=dict(size=16, color='#3D3B40', weight='bold') 
                ),
                yaxis=dict(
                    range=[0, recolts_jour['Total_Recolt'].max() * 1.2], 
                    tickfont=dict(size=16, color='#3D3B40') 
                ),
                font=dict(family='Arial', size=14, color='#3D3B40'), 
                margin=dict(t=50, b=50, l=50, r=50) 
            )
            st.plotly_chart(fig_jour, use_container_width=True, key="recolts_par_jour")
            
        with col_temp2:
            st.markdown(f"<h3 style='color: {COLOR_PALETTE['primary']};'>Récoltes par Heure de la Journée</h3>", unsafe_allow_html=True)
            filtered_recolts['ORDER_HOUR'] = filtered_recolts['ORDER_DATE'].dt.hour
            recolts_heure = filtered_recolts[
                (filtered_recolts['ORDER_DATE'].dt.hour >= 9) &
                (filtered_recolts['ORDER_DATE'].dt.hour <= 20)
            ].groupby(filtered_recolts['ORDER_DATE'].dt.hour)['Total_Recolt'].sum().reset_index()

            recolts_heure = recolts_heure.rename(columns={'ORDER_DATE': 'Heure'})
            all_hours = pd.DataFrame({'Heure': range(9, 21)}) 
            recolts_heure = pd.merge(all_hours, recolts_heure, on='Heure', how='left').fillna(0)
            recolts_heure = recolts_heure.sort_values('Heure')

            fig_heure = px.line(recolts_heure, x='Heure', y='Total_Recolt',
                                 line_shape='spline',
                                 color_discrete_sequence=[COLOR_PALETTE['accent1']])

            fig_heure.update_traces(
                line=dict(width=4, color=COLOR_PALETTE['accent1']),
                mode='lines+markers+text',
                marker=dict(size=10, color='#3D3B40', line=dict(width=1, color='#FFFFFF')), 
                text=[f"€{y:,.0f}" for y in recolts_heure['Total_Recolt']],
                textposition="top center", 
                textfont=dict(color=COLOR_PALETTE['secondary'], size=16, family='Arial', weight='bold'),
                hovertemplate='Heure: %{x}h<br>Récoltes: €%{y:,.2f}<extra></extra>',
                fill='tozeroy',
                fillcolor=f'rgba({int(COLOR_PALETTE["accent1"][1:3], 16)}, {int(COLOR_PALETTE["accent1"][3:5], 16)}, {int(COLOR_PALETTE["accent1"][5:7], 16)}, 0.2)'
            )

            fig_heure.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                plot_bgcolor='#FFFFFF',
                paper_bgcolor='#FFFFFF',
                xaxis_gridcolor='#E0E0E0',
                yaxis_gridcolor='#E0E0E0',
                xaxis=dict(
                    tickmode='linear',
                    dtick=1,
                    range=[8.5, 20.5],
                    tickfont=dict(size=16, color='#3D3B40', weight='bold')
                ),
                yaxis=dict(
                    range=[0, recolts_heure['Total_Recolt'].max() * 1.2],
                    tickfont=dict(size=16, color='#3D3B40')
                ),
                font=dict(family='Arial', size=14, color='#3D3B40'),
                margin=dict(t=50, b=50, l=50, r=50)
            )
            st.plotly_chart(fig_heure, use_container_width=True, key="recolts_par_heure")

        with col_temp3:
            st.markdown(f"<h3 style='color: {COLOR_PALETTE['primary']};'>Récoltes par Mois</h3>", unsafe_allow_html=True)
            filtered_recolts['MonthNum'] = filtered_recolts['ORDER_DATE'].dt.month
            recolts_mois = filtered_recolts.groupby('MonthNum')['Total_Recolt'].sum().reset_index()
            
            months = {
                1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 
                5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août', 
                9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
            }
            all_months = pd.DataFrame({'MonthNum': range(1, 13)})
            recolts_mois = pd.merge(all_months, recolts_mois, on='MonthNum', how='left').fillna(0)
            recolts_mois['Mois'] = recolts_mois['MonthNum'].map(months)
            recolts_mois = recolts_mois.sort_values('MonthNum') 

            fig_mois = px.line(recolts_mois,
                                x='Mois',
                                y='Total_Recolt',
                                line_shape='spline',
                                color_discrete_sequence=[COLOR_PALETTE['primary']])

            fig_mois.update_traces(
                line=dict(width=4, color=COLOR_PALETTE['primary']),
                mode='lines+markers+text',
                marker=dict(size=10, color='#3D3B40', line=dict(width=1, color='#FFFFFF')), 
                text=[f"€{y:,.0f}" for y in recolts_mois['Total_Recolt']],
                textposition="top center", 
                textfont=dict(color=COLOR_PALETTE['secondary'], size=16, family='Arial', weight='bold'),
                hovertemplate='Mois: %{x}<br>Récoltes: €%{y:,.2f}<extra></extra>',
                fill='tozeroy',
                fillcolor=f'rgba({int(COLOR_PALETTE["primary"][1:3], 16)}, {int(COLOR_PALETTE["primary"][3:5], 16)}, {int(COLOR_PALETTE["primary"][5:7], 16)}, 0.2)'
            )

            fig_mois.update_layout(
                xaxis_title=None, 
                yaxis_title=None, 
                plot_bgcolor='#FFFFFF', 
                paper_bgcolor='#FFFFFF', 
                xaxis_gridcolor='#E0E0E0', 
                yaxis_gridcolor='#E0E0E0', 
                xaxis=dict(
                    tickmode='array',
                    tickvals=recolts_mois['Mois'],
                    categoryorder='array', 
                    categoryarray=recolts_mois['Mois'],
                    tickfont=dict(size=16, color='#3D3B40', weight='bold') 
                ),
                yaxis=dict(
                    range=[0, recolts_mois['Total_Recolt'].max() * 1.2], 
                    tickfont=dict(size=16, color='#3D3B40') 
                ),
                font=dict(family='Arial', size=14, color='#3D3B40'), 
                margin=dict(t=50, b=50, l=50, r=50) 
            )
            st.plotly_chart(fig_mois, use_container_width=True, key="recolts_par_mois")

        # Performance et Tendances
        st.markdown(f"<h2 style='text-align: center; color: {COLOR_PALETTE['secondary']};'>Performance et Tendances</h2>", unsafe_allow_html=True)

        col_g1, col_g2, col_g3 = st.columns(3)

        with col_g1:
            st.markdown(f"<h3 style='color: {COLOR_PALETTE['primary']};'>Récoltes par Équipe</h3>", unsafe_allow_html=True)
            if 'Team' in staff_df.columns:
                recolts_by_team = filtered_recolts.merge(staff_df[['Hyp', 'Team']], on='Hyp', how='left')
                team_performance = recolts_by_team.groupby('Team')['Total_Recolt'].sum().reset_index()
                fig = px.bar(team_performance.sort_values(by='Total_Recolt', ascending=False),
                            y='Team', x='Total_Recolt', orientation='h',
                            color='Total_Recolt', 
                            color_continuous_scale=[COLOR_PALETTE['accent1'], COLOR_PALETTE['primary']])
                fig.update_layout(
                    xaxis=dict(title=None, tickfont=dict(size=14, family='Arial', color='black', weight='bold')),
                    yaxis=dict(title=None, tickfont=dict(size=14, family='Arial', color='black', weight='bold')),
                    showlegend=False,
                    coloraxis_showscale=False)
                fig.update_traces(
                    text=team_performance['Total_Recolt'].apply(lambda x: f"€{x:,.0f}".replace(",", " ")), 
                    textposition='inside',
                    textfont=dict(size=18, family='Arial', color='white', weight='bold'))
                st.plotly_chart(fig, use_container_width=True, key="recolts_par_equipe")
            else:
                st.info("Les données du personnel ne contiennent pas d'information sur les équipes.")

        with col_g2:
            st.markdown(f"<h3 style='color: {COLOR_PALETTE['primary']};'>Top 10 des Récolteurs</h3>", unsafe_allow_html=True)
            if 'Hyp' in filtered_recolts.columns:
                recolts_by_hyp = filtered_recolts.groupby('Hyp')['Total_Recolt'].sum().reset_index()
                top_recolteurs = recolts_by_hyp.sort_values(by='Total_Recolt', ascending=False).head(10)
                
                if 'NOM PRENOM' not in staff_df.columns and 'NOM' in staff_df.columns and 'PRENOM' in staff_df.columns:
                    staff_df['NOM PRENOM'] = staff_df['NOM'] + ' ' + staff_df['PRENOM']

                if 'NOM PRENOM' in staff_df.columns:
                    top_recolteurs = top_recolteurs.merge(staff_df[['Hyp', 'NOM PRENOM']], on='Hyp', how='left')
                    x_col = 'NOM PRENOM'
                else:
                    x_col = 'Hyp'

                fig = px.bar(top_recolteurs,
                            y=x_col, x='Total_Recolt', orientation='h',
                            color='Total_Recolt', 
                            color_continuous_scale=[COLOR_PALETTE['accent1'], COLOR_PALETTE['primary']])
                fig.update_layout(
                    xaxis=dict(title=None, tickfont=dict(size=14, family='Arial', color='black', weight='bold')),
                    yaxis=dict(title=None, tickfont=dict(size=14, family='Arial', color='black', weight='bold')),
                    showlegend=False,
                    coloraxis_showscale=False)
                fig.update_traces(
                    text=top_recolteurs['Total_Recolt'].apply(lambda x: f"€{x:,.0f}".replace(",", " ")), 
                    textposition='inside',
                    textfont=dict(size=16, family='Arial', color='white', weight='bold'))
                st.plotly_chart(fig, use_container_width=True, key="top_recolteurs")
            else:
                st.info("Les données de récoltes ne contiennent pas d'information sur les récolteurs (Hyp).")
            
        with col_g3:
            st.markdown(f"<h3 style='color: {COLOR_PALETTE['primary']};'>Distribution des Valeurs de Récolte</h3>", unsafe_allow_html=True)
            if 'Total_Recolt' in filtered_recolts.columns:
                fig = px.histogram(filtered_recolts, x='Total_Recolt', nbins=20,
                                labels={'Total_Recolt': 'Valeur de Récolte (€)'},
                                color_discrete_sequence=[COLOR_PALETTE['primary']])
                fig.update_layout(
                    xaxis=dict(title=None, tickfont=dict(size=14, family='Arial', color='black', weight='bold')),
                    yaxis=dict(title=None, tickfont=dict(size=14, family='Arial', color='black', weight='bold')),
                    showlegend=False)
                fig.update_traces(
                    texttemplate='%{y}',
                    textposition='inside',
                    textfont=dict(size=12, family='Arial', color='white', weight='bold'))
                st.plotly_chart(fig, use_container_width=True, key="distribution_valeurs_recolte")

        # Autres Analyses
        st.markdown(f"<h2 style='text-align: center; color: {COLOR_PALETTE['secondary']};'>Autres Analyses</h2>", unsafe_allow_html=True)
        
        st.markdown(f"<h3 style='text-align: center; color: {COLOR_PALETTE['primary']};'>Détails des Transactions de Récoltes</h3>", unsafe_allow_html=True)
        if not filtered_recolts.empty:
                recolts_list_df = filtered_recolts.copy()

                if 'NOM' in staff_df.columns and 'PRENOM' in staff_df.columns and 'NOM PRENOM' not in staff_df.columns:
                    staff_df['NOM PRENOM'] = staff_df['NOM'] + ' ' + staff_df['PRENOM']

                if 'Hyp' in recolts_list_df.columns and 'NOM PRENOM' in staff_df.columns:
                    recolts_list_df = recolts_list_df.merge(staff_df[['Hyp', 'NOM PRENOM']], on='Hyp', how='left')
                else:
                    recolts_list_df['NOM PRENOM'] = 'N/A'

                recolts_list_df['Acceptée'] = recolts_list_df['SHORT_MESSAGE'] == 'ACCEPTED'
                recolts_list_df['Refusée'] = recolts_list_df['SHORT_MESSAGE'] == 'REFUSED'
                
                display_cols = recolts_list_df[[
                    'NOM PRENOM', 'City', 'Banques', 'Total_Recolt', 'Acceptée', 'Refusée', 'ORDER_DATE'
                ]].rename(columns={
                    'NOM PRENOM': 'Nom Prénom',
                    'City': 'Ville',
                    'Banques': 'Banque',
                    'Total_Recolt': 'Montant (€)',
                    'ORDER_DATE': 'Date Création'
                })

                display_cols['Montant (€)'] = display_cols['Montant (€)'].apply(lambda x: f"€{x:,.2f}".replace(",", " "))
                display_cols['Date Création'] = display_cols['Date Création'].dt.strftime('%Y-%m-%d %H:%M')

                def apply_cell_style(val):
                    return 'font-weight: bold; text-align: center; font-size: 14px;'

                def highlight_accepted(s):
                    return [f'background-color: {COLOR_PALETTE["light_bg"]}; color: {COLOR_PALETTE["primary"]};' if v else '' for v in s]
                
                def highlight_refused(s):
                    return [f'background-color: #ffe6e6; color: {COLOR_PALETTE["secondary"]};' if v else '' for v in s]
                
                styled_df = display_cols.style \
                    .applymap(apply_cell_style) \
                    .apply(highlight_accepted, subset=['Acceptée']) \
                    .apply(highlight_refused, subset=['Refusée'])
                
                st.markdown(
                    f"""
                    <style>
                    .styled-dataframe-frame {{
                        border: 2px solid {COLOR_PALETTE['primary']};
                        border-radius: 10px;
                        padding: 10px;
                        box-shadow: 3px 3px 10px rgba(0,0,0,0.15);
                        background-color: #f8faff;
                        margin-top: 15px;
                    }}
                    .dataframe-styling {{
                        font-family: Arial, sans-serif;
                    }}
                    .dataframe-styling th {{
                        font-weight: bold;
                        text-align: center !important;
                        font-size: 14px;
                        background-color: {COLOR_PALETTE['primary']};
                        color: white;
                    }}
                    </style>
                    """, unsafe_allow_html=True
                )

                st.markdown("<div class='styled-dataframe-frame dataframe-styling'>", unsafe_allow_html=True)
                st.dataframe(styled_df, use_container_width=True, key="recolts_transactions_detail_list")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
                st.info("Aucune donnée de transaction de récoltes disponible pour les filtres sélectionnés.")