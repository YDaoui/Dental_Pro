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
# Assuming Utils_Dental, Managers, Logs, Recolts are custom modules and available
# from Utils_Dental import *
# from Managers import *
# from Logs import *
# from Recolts import *

# Géocodage sécurisé


# Filtrage des données
def filter_data(df, country_filter, team_filter, activity_filter, agent_filter, start_date, end_date, staff_df, current_hyp=None):
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

        # Ensure 'NOM PRENOM' column exists for filtering, if 'NOM' and 'PRENOM' are present
        if 'NOM' in staff_filtered.columns and 'PRENOM' in staff_filtered.columns:
            staff_filtered['NOM PRENOM'] = staff_filtered['NOM'] + ' ' + staff_filtered['PRENOM']
        
        # Apply team filter
        if team_filter != 'Toutes':
            staff_filtered = staff_filtered[staff_filtered['Team'] == team_filter]
        
        # Apply activity filter
        if activity_filter != 'Toutes':
            staff_filtered = staff_filtered[staff_filtered['Activité'] == activity_filter]
        
        # Apply agent filter
        if agent_filter != 'Tous':
            # Check if 'NOM PRENOM' exists before trying to filter by it
            if 'NOM PRENOM' in staff_filtered.columns:
                staff_filtered = staff_filtered[staff_filtered['NOM PRENOM'] == agent_filter]
            else:
                # Fallback: if 'NOM PRENOM' isn't available, try to filter by Hyp if the agent filter value is an Hyp
                st.warning("Could not filter by agent name. Falling back to filtering by 'Hyp' if agent filter matches.")
                staff_filtered = staff_filtered[staff_filtered['Hyp'] == agent_filter]


        if 'Hyp' in staff_filtered.columns:
            filtered_df = filtered_df[filtered_df['Hyp'].isin(staff_filtered['Hyp'])]

    return filtered_df

# Affichage de la page Ventes
def sales_page1(sales_df, staff_df, start_date, end_date):
    """Affiche la page des ventes."""

    # Pre-process staff_df to create 'NOM PRENOM' once if 'NOM' and 'PRENOM' exist
    if 'NOM' in staff_df.columns and 'PRENOM' in staff_df.columns:
        staff_df['NOM PRENOM'] = staff_df['NOM'] + ' ' + staff_df['PRENOM']
    else:
        st.warning("Columns 'NOM' and/or 'PRENOM' not found in staff data. Agent filter will use 'Hyp'.")
    col1, col2 = st.columns([2, 2])
    with col1:
        st.markdown(
            "<h1 style='text-align: left; color: #002a48; margin-bottom: 0;'>Ventes Dashboard</h1>", 
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            "<h1 style='text-align: right; color: #00afe1; margin-bottom: 0;'>Analyse des Ventes</h1>", 
            unsafe_allow_html=True
        )

    # Filters
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        country_filter = st.selectbox("Filtrer par Pays", ['Tous'] + sorted(sales_df['Country'].dropna().unique()), key='sales_country')
    with col2:
        team_filter = st.selectbox("Sélectionner équipe", ['Toutes'] + sorted(staff_df['Team'].dropna().unique()), key='sales_team')
    with col3:
        activity_filter = st.selectbox("Sélectionner activité", ['Toutes'] + sorted(staff_df['Activité'].dropna().unique()), key='sales_activity')
    
    with col4:
        # Dynamically populate agent filter based on selected team
        agents_in_team = ['Tous']
        if team_filter != 'Toutes':
            # Filter staff_df by selected team for populating the agent dropdown
            filtered_staff_for_dropdown = staff_df[staff_df['Team'] == team_filter]
            if 'NOM PRENOM' in filtered_staff_for_dropdown.columns:
                agents_in_team += sorted(filtered_staff_for_dropdown['NOM PRENOM'].dropna().unique())
            else: # Fallback if 'NOM PRENOM' wasn't successfully created
                agents_in_team += sorted(filtered_staff_for_dropdown['Hyp'].dropna().unique())
        
        agent_filter = st.selectbox("Sélectionner Agent", agents_in_team, key='sales_agent')

    # Filtrage
    filtered_sales = filter_data(sales_df, country_filter, team_filter, activity_filter, agent_filter, start_date, end_date, staff_df)

    if not filtered_sales.empty:
        # Métriques / KPIs
        st.markdown("<h2 style='text-align: center; color: #002a48;'>Indicateurs Clés de Performance</h2>", unsafe_allow_html=True)
        col1_kpi, col2_kpi, col3_kpi, col4_kpi = st.columns(4)
        
        with col1_kpi:
            st.markdown(f"""
                <div style='
                    border: 2px solid #007bad; 
                    border-radius: 10px; 
                    padding: 15px; 
                    text-align: center; 
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                    background-color: #f0f8ff;
                '>
                    <h3 style='color: #333333; margin-bottom: 5px;'>Total Sales</h3>
                    <p style='font-size: 24px; color: #007bad; font-weight: bold;'>€{filtered_sales['Total_Sale'].sum():,.0f}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2_kpi:
            st.markdown(f"""
                <div style='
                    border: 2px solid #007bad; 
                    border-radius: 10px; 
                    padding: 15px; 
                    text-align: center; 
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                    background-color: #f0f8ff;
                '>
                    <h3 style='color: #333333; margin-bottom: 5px;'>Average Sale</h3>
                    <p style='font-size: 24px; color: #007bad; font-weight: bold;'>€{filtered_sales['Total_Sale'].mean():,.2f}</p>
                </div>
            """, unsafe_allow_html=True)

        with col3_kpi:
            if 'Rating' in filtered_sales.columns:
                avg_rating = filtered_sales['Rating'].mean()
                rating_display = f"{'★' * int(round(avg_rating))}{'☆' * (5 - int(round(avg_rating)))} ({avg_rating:.1f})"
                st.markdown(f"""
                    <div style='
                        border: 2px solid #007bad; 
                        border-radius: 10px; 
                        padding: 15px; 
                        text-align: center; 
                        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                        background-color: #f0f8ff;
                    '>
                        <h3 style='color: #333333; margin-bottom: 5px;'>Average Rating</h3>
                        <p style='font-size: 24px; color: #007bad; font-weight: bold;'>{rating_display}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='
                        border: 2px solid #007bad; 
                        border-radius: 10px; 
                        padding: 15px; 
                        text-align: center; 
                        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                        background-color: #f0f8ff;
                    '>
                        <h3 style='color: #333333; margin-bottom: 5px;'>Average Rating</h3>
                        <p style='font-size: 24px; color: #007bad; font-weight: bold;'>N/A</p>
                    </div>
                """, unsafe_allow_html=True)

        with col4_kpi:
            st.markdown(f"""
                <div style='
                    border: 2px solid #007bad; 
                    border-radius: 10px; 
                    padding: 15px; 
                    text-align: center; 
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                    background-color: #f0f8ff;
                '>
                    <h3 style='color: #333333; margin-bottom: 5px;'>Total Transactions</h3>
                    <p style='font-size: 24px; color: #007bad; font-weight: bold;'>{len(filtered_sales)}</p>
                </div>
            """, unsafe_allow_html=True)
        
       

        ## Principaux Graphiques
        st.markdown("<h2 style='text-align: center; color: #002a48;'>Analyses Principales</h2>", unsafe_allow_html=True)
        
        col_main1, col_main2, col_main3 = st.columns([2, 2, 2])
        with col_main1:
            st.markdown("<h3 style='color: #007bad;'>Ventes par Ville</h3>", unsafe_allow_html=True)
            ventes_ville = filtered_sales.groupby('City')['Total_Sale'].sum().reset_index()
            fig = px.bar(ventes_ville, y='City', x='Total_Sale', orientation='h', 
                         color='Total_Sale', color_continuous_scale=['#00afe1', '#007bad'])
            fig.update_layout(xaxis=dict(title=None, tickfont=dict(size=12, family='Arial', color='black', weight='bold')),
                              yaxis=dict(title=None, tickfont=dict(size=12, family='Arial', color='black', weight='bold')))
            fig.update_traces(text=ventes_ville['Total_Sale'].apply(lambda x: f"€{x:,.0f}".replace(",", " ")), textposition='outside',
                              textfont=dict(size=12, family='Arial', color='black', weight='bold'))
            st.plotly_chart(fig, use_container_width=True, key="ventes_par_ville") # Added key

        with col_main2:
            st.markdown("<h3 style='color: #007bad;'>Statut des Transactions</h3>", unsafe_allow_html=True)
            status_sales = filtered_sales.groupby('SHORT_MESSAGE')['Total_Sale'].sum().reset_index()
            
            fig = px.pie(status_sales, 
                         values='Total_Sale', 
                         names='SHORT_MESSAGE',
                        
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
                        text=f"Total: {status_sales['Total_Sale'].sum():,.0f}€",
                        x=0.5, y=0.5,
                        font_size=14,
                        showarrow=False,
                        font=dict(color='#333333')
                    )
                ],
                uniformtext_minsize=10,
                uniformtext_mode='hide'
            )
            
            st.plotly_chart(fig, use_container_width=True, key="statut_transactions_pie") # Added key

        with col_main3: # This is now the place for "Statut des Transactions par Pays"
            st.markdown("<h3 style='color: #007bad;'>Statut des Transactions par Pays</h3>", unsafe_allow_html=True)
            if 'SHORT_MESSAGE' in filtered_sales.columns and 'Country' in filtered_sales.columns:
                status_by_country = filtered_sales.groupby(['Country', 'SHORT_MESSAGE'])['Total_Sale'].sum().unstack(fill_value=0)
                fig = px.bar(status_by_country,
                             y=status_by_country.index, x=status_by_country.columns, orientation='h',
                            
                             color_discrete_map={'ACCEPTED': '#007bad', 'REFUSED': '#ff0000'})
                fig.update_layout(xaxis=dict(title=None, tickfont=dict(size=12, family='Arial', color='black', weight='bold')),
                                  yaxis=dict(title=None, tickfont=dict(size=12, family='Arial', color='black', weight='bold')))
                st.plotly_chart(fig, use_container_width=True, key="statut_transactions_par_pays_main") # Added key
            else:
                st.info("Données insuffisantes pour l'analyse du statut des transactions par pays.")


       
        ## Répartition Temporelle Détaillée
        st.markdown("<h2 style='text-align: center; color: #002a48;'>Répartition Temporelle Détaillée des Ventes</h2>", unsafe_allow_html=True)
        col_temp1, col_temp2, col_temp3 = st.columns(3)

        with col_temp1:
            # Ventes par Jour de la Semaine
            st.markdown("<h3 style='color: #007bad;'>Ventes par Jour de la Semaine</h3>", unsafe_allow_html=True)
            filtered_sales['Weekday'] = filtered_sales['ORDER_DATE'].dt.weekday
            ventes_jour = filtered_sales.groupby('Weekday')['Total_Sale'].sum().reset_index()
            jours = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}
            ventes_jour['Jour'] = ventes_jour['Weekday'].map(jours)
            all_days = pd.DataFrame({'Weekday': range(7)})
            ventes_jour = pd.merge(all_days, ventes_jour, on='Weekday', how='left').fillna(0)
            ventes_jour['Jour'] = ventes_jour['Weekday'].map(jours) 
            ventes_jour = ventes_jour.sort_values('Weekday')

            fig_jour = px.line(ventes_jour,
                                x='Jour',
                                y='Total_Sale',
                                line_shape='spline',
                                color_discrete_sequence=['#525CEB']) 

            fig_jour.update_traces(
                line=dict(width=4, color='#525CEB'), 
                mode='lines+markers+text',
                marker=dict(size=10, color='#3D3B40', line=dict(width=1, color='#FFFFFF')), 
                text=[f"€{y:,.0f}" for y in ventes_jour['Total_Sale']],
                textposition="top center", 
                textfont=dict(color="#F70F49", size=14, family='Arial', weight='bold'), 
                hovertemplate='Jour: %{x}<br>Ventes: €%{y:,.2f}<extra></extra>',
                fill='tozeroy',
                fillcolor='rgba(179, 191, 231, 0.4)' 
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
                    tickvals=ventes_jour['Jour'],
                    categoryorder='array', 
                    categoryarray=ventes_jour['Jour'],
                    tickfont=dict(size=14, color='#3D3B40', weight='bold') 
                ),
                yaxis=dict(
                    range=[0, ventes_jour['Total_Sale'].max() * 1.2], 
                    tickfont=dict(size=12, color='#3D3B40') 
                ),
                font=dict(family='Arial', size=12, color='#3D3B40'), 
                margin=dict(t=50, b=50, l=50, r=50) 
            )
            st.plotly_chart(fig_jour, use_container_width=True, key="ventes_par_jour") # Added key
            
        with col_temp2:
            # Ventes par Heure de la Journée
            st.markdown("<h3 style='color: #007bad;'>Ventes par Heure de la Journée</h3>", unsafe_allow_html=True)
            filtered_sales['ORDER_HOUR'] = filtered_sales['ORDER_DATE'].dt.hour
            ventes_heure = filtered_sales[
                (filtered_sales['ORDER_DATE'].dt.hour >= 9) &
                (filtered_sales['ORDER_DATE'].dt.hour <= 20)
            ].groupby(filtered_sales['ORDER_DATE'].dt.hour)['Total_Sale'].sum().reset_index()

            ventes_heure = ventes_heure.rename(columns={'ORDER_DATE': 'Heure'})
            all_hours = pd.DataFrame({'Heure': range(9, 21)}) 
            ventes_heure = pd.merge(all_hours, ventes_heure, on='Heure', how='left').fillna(0)
            ventes_heure = ventes_heure.sort_values('Heure')

            fig_heure = px.line(ventes_heure, x='Heure', y='Total_Sale',
                                 line_shape='spline',
                                 color_discrete_sequence=['#525CEB']) 

            fig_heure.update_traces(
                line=dict(width=4, color='#525CEB'), 
                mode='lines+markers+text',
                marker=dict(size=10, color='#3D3B40', line=dict(width=1, color='#FFFFFF')), 
                text=[f"€{y:,.0f}" for y in ventes_heure['Total_Sale']],
                textposition="top center", 
                textfont=dict(color="#F50808", size=14, family='Arial', weight='bold'), 
                hovertemplate='Heure: %{x}h<br>Ventes: €%{y:,.2f}<extra></extra>',
                fill='tozeroy',
                fillcolor='rgba(179, 191, 231, 0.4)' 
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
                    tickfont=dict(size=14, color='#3D3B40', weight='bold')
                ),
                yaxis=dict(
                    range=[0, ventes_heure['Total_Sale'].max() * 1.2],
                    tickfont=dict(size=12, color='#3D3B40')
                ),
                font=dict(family='Arial', size=12, color='#3D3B40'),
                margin=dict(t=50, b=50, l=50, r=50)
            )
            st.plotly_chart(fig_heure, use_container_width=True, key="ventes_par_heure") # Added key

        with col_temp3:
            # Ventes par Mois
            st.markdown("<h3 style='color: #007bad;'>Ventes par Mois</h3>", unsafe_allow_html=True)
            filtered_sales['MonthNum'] = filtered_sales['ORDER_DATE'].dt.month
            ventes_mois = filtered_sales.groupby('MonthNum')['Total_Sale'].sum().reset_index()
            
            months = {
                1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 
                5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août', 
                9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
            }
            all_months = pd.DataFrame({'MonthNum': range(1, 13)})
            ventes_mois = pd.merge(all_months, ventes_mois, on='MonthNum', how='left').fillna(0)
            ventes_mois['Mois'] = ventes_mois['MonthNum'].map(months)
            ventes_mois = ventes_mois.sort_values('MonthNum') 

            fig_mois = px.line(ventes_mois,
                                x='Mois',
                                y='Total_Sale',
                                line_shape='spline',
                                color_discrete_sequence=['#525CEB']) 

            fig_mois.update_traces(
                line=dict(width=4, color='#525CEB'), 
                mode='lines+markers+text',
                marker=dict(size=10, color='#3D3B40', line=dict(width=1, color='#FFFFFF')), 
                text=[f"€{y:,.0f}" for y in ventes_mois['Total_Sale']],
                textposition="top center", 
                textfont=dict(color="#F70F49", size=14, family='Arial', weight='bold'), 
                hovertemplate='Mois: %{x}<br>Ventes: €%{y:,.2f}<extra></extra>',
                fill='tozeroy',
                fillcolor='rgba(179, 191, 231, 0.4)' 
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
                    tickvals=ventes_mois['Mois'],
                    categoryorder='array', 
                    categoryarray=ventes_mois['Mois'],
                    tickfont=dict(size=14, color='#3D3B40', weight='bold') 
                ),
                yaxis=dict(
                    range=[0, ventes_mois['Total_Sale'].max() * 1.2], 
                    tickfont=dict(size=12, color='#3D3B40') 
                ),
                font=dict(family='Arial', size=12, color='#3D3B40'), 
                margin=dict(t=50, b=50, l=50, r=50) 
            )
            st.plotly_chart(fig_mois, use_container_width=True, key="ventes_par_mois") # Added key

        
        
        ## Graphiques de Performance et Tendances
        st.markdown("<h2 style='text-align: center; color: #002a48;'>Performance et Tendances</h2>", unsafe_allow_html=True)

        # First row of 3 charts
        col_g1, col_g2, col_g3 = st.columns(3)

        with col_g1:
            st.markdown("<h3 style='color: #007bad;'>Ventes par Équipe</h3>", unsafe_allow_html=True)
            if 'Team' in staff_df.columns:
                sales_by_team = filtered_sales.merge(staff_df[['Hyp', 'Team']], on='Hyp', how='left')
                team_performance = sales_by_team.groupby('Team')['Total_Sale'].sum().reset_index()
                fig = px.bar(team_performance.sort_values(by='Total_Sale', ascending=False),
                             y='Team', x='Total_Sale', orientation='h', 
                             color='Total_Sale', color_continuous_scale=px.colors.sequential.Teal)
                fig.update_layout(xaxis=dict(title=None, tickfont=dict(size=12, family='Arial', color='black', weight='bold')),
                                  yaxis=dict(title=None, tickfont=dict(size=12, family='Arial', color='black', weight='bold')))
                fig.update_traces(text=team_performance['Total_Sale'].apply(lambda x: f"€{x:,.0f}".replace(",", " ")), textposition='outside',
                                  textfont=dict(size=12, family='Arial', color='black', weight='bold'))
                st.plotly_chart(fig, use_container_width=True, key="ventes_par_equipe") # Added key
            else:
                st.info("Les données du personnel ne contiennent pas d'information sur les équipes.")

        with col_g2:
            st.markdown("<h3 style='color: #007bad;'>Top 10 des Vendeurs</h3>", unsafe_allow_html=True)
            if 'Hyp' in filtered_sales.columns:
                sales_by_hyp = filtered_sales.groupby('Hyp')['Total_Sale'].sum().reset_index()
                top_salespeople = sales_by_hyp.sort_values(by='Total_Sale', ascending=False).head(10)
                
                if 'NOM PRENOM' not in staff_df.columns and 'NOM' in staff_df.columns and 'PRENOM' in staff_df.columns:
                    staff_df['NOM PRENOM'] = staff_df['NOM'] + ' ' + staff_df['PRENOM']

                if 'NOM PRENOM' in staff_df.columns:
                    top_salespeople = top_salespeople.merge(staff_df[['Hyp', 'NOM PRENOM']], on='Hyp', how='left')
                    x_col = 'NOM PRENOM'
                else:
                    x_col = 'Hyp' # Fallback to Hyp if NOM PRENOM is not available

                fig = px.bar(top_salespeople,
                             y=x_col, x='Total_Sale', orientation='h',
                             color='Total_Sale', color_continuous_scale=px.colors.sequential.Plasma_r)
                fig.update_layout(xaxis=dict(title=None, tickfont=dict(size=12, family='Arial', color='black', weight='bold')),
                                  yaxis=dict(title=None, tickfont=dict(size=12, family='Arial', color='black', weight='bold')))
                fig.update_traces(text=top_salespeople['Total_Sale'].apply(lambda x: f"€{x:,.0f}".replace(",", " ")), textposition='outside',
                                  textfont=dict(size=12, family='Arial', color='black', weight='bold'))
                st.plotly_chart(fig, use_container_width=True, key="top_vendeurs") # Added key
            else:
                st.info("Les données de ventes ne contiennent pas d'information sur les vendeurs (Hyp).")
            
        with col_g3:
            st.markdown("<h3 style='color: #007bad;'>Distribution des Valeurs de Vente</h3>", unsafe_allow_html=True)
            if 'Total_Sale' in filtered_sales.columns:
                fig = px.histogram(filtered_sales, x='Total_Sale', nbins=20,
                                   
                                   labels={'Total_Sale': 'Valeur de Vente (€)'},
                                   color_discrete_sequence=['#00afe1'])
                fig.update_layout(xaxis=dict(title=None, tickfont=dict(size=12, family='Arial', color='black', weight='bold')),
                                  yaxis=dict(title=None, tickfont=dict(size=12, family='Arial', color='black', weight='bold')))
                st.plotly_chart(fig, use_container_width=True, key="distribution_valeurs_vente") # Added key
            else:
                st.info("Les données de ventes ne contiennent pas de 'Total_Sale'.")

    
    
       
        st.markdown("<h2 style='text-align: center; color: #002a48;'>Autres Analyses</h2>", unsafe_allow_html=True)
        

        
        
        
        
        st.markdown("<h3 style='text-align: center; color: #007bad;'>Détails des Transactions</h3>", unsafe_allow_html=True)
        if not filtered_sales.empty:
                # Prepare data for the transaction list
                sales_list_df = filtered_sales.copy()

                # Merge with staff_df to get "Nom Prénom"
                # Ensure 'NOM PRENOM' column is created in staff_df if not already
                if 'NOM' in staff_df.columns and 'PRENOM' in staff_df.columns and 'NOM PRENOM' not in staff_df.columns:
                    staff_df['NOM PRENOM'] = staff_df['NOM'] + ' ' + staff_df['PRENOM']

                if 'Hyp' in sales_list_df.columns and 'NOM PRENOM' in staff_df.columns:
                    sales_list_df = sales_list_df.merge(staff_df[['Hyp', 'NOM PRENOM']], on='Hyp', how='left')
                else:
                    sales_list_df['NOM PRENOM'] = 'N/A' # Fallback if agent name isn't available

                # Create accepted/refused columns
                sales_list_df['Acceptée'] = sales_list_df['SHORT_MESSAGE'] == 'ACCEPTED'
                sales_list_df['Refusée'] = sales_list_df['SHORT_MESSAGE'] == 'REFUSED'
                
                # Select and rename columns for display
                display_cols = sales_list_df[[
                    'NOM PRENOM', 'City', 'Total_Sale', 'Acceptée', 'Refusée', 'Rating', 'ORDER_DATE'
                ]].rename(columns={
                    'NOM PRENOM': 'Nom Prénom',
                    'City': 'Ville',
                    'Total_Sale': 'Montant (€)',
                    'ORDER_DATE': 'Date Création',
                    'Rating': 'Évaluation'
                })

                # Format 'Montant (€)'
                display_cols['Montant (€)'] = display_cols['Montant (€)'].apply(lambda x: f"€{x:,.2f}".replace(",", " "))
                
                # Format 'Date Création'
                display_cols['Date Création'] = display_cols['Date Création'].dt.strftime('%Y-%m-%d %H:%M')

                # Define styling functions
                def highlight_accepted(s):
                    return ['background-color: #e6ffe6; color: green; font-weight: bold;' if v else '' for v in s] # Light green for accepted
                
                def highlight_refused(s):
                    return ['background-color: #ffe6e6; color: red; font-weight: bold;' if v else '' for v in s] # Light red for refused

                def color_rating(val):
                    color = ''
                    if pd.notna(val):
                        if val >= 4:
                            color = '#28a745' # Green for good rating
                        elif val >= 3:
                            color = '#ffc107' # Yellow/Orange for neutral rating
                        else:
                            color = '#dc3545' # Red for low rating
                    return f'color: {color}; font-weight: bold;'
                
                # Apply styling
                styled_df = display_cols.style \
                    .apply(highlight_accepted, subset=['Acceptée']) \
                    .apply(highlight_refused, subset=['Refusée']) \
                    .map(color_rating, subset=['Évaluation'])
                
                # Inject custom CSS for the frame
                st.markdown(
                    """
                    <style>
                    .styled-dataframe-frame {
                        border: 2px solid #007bad;
                        border-radius: 10px;
                        padding: 10px;
                        box-shadow: 3px 3px 10px rgba(0,0,0,0.15);
                        background-color: #f8faff; /* Slightly off-white background */
                        margin-top: 15px;
                    }
                    </style>
                    """, unsafe_allow_html=True
                )

                # Display the dataframe within the custom frame
                st.markdown("<div class='styled-dataframe-frame'>", unsafe_allow_html=True)
                # Added a unique key for st.dataframe as well, good practice
                st.dataframe(styled_df, use_container_width=True, key="transactions_detail_list") 
                st.markdown("</div>", unsafe_allow_html=True)

        else:
                st.info("Aucune donnée de transaction disponible pour les filtres sélectionnés.")
        
        