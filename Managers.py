import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_option_menu import option_menu
from Utils_Dental import *

def manager_dashboard():
    sales_df, staff_df = load_data()
    sales_df = preprocess_data(sales_df)
    staff_df = preprocess_data(staff_df)

    with st.sidebar:
        st.image('Dental_Implant.png', width=350)
        
        if st.session_state.get("user_type") == "Hyperviseur":
            menu_options = ["Tableau de bord", "Sales", "Recolt", "Planning", "Setting"]
            icons = ["bar-chart", "currency-dollar", "list-ul", "calendar", "gear"]
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
        display_planning(sales_df, staff_df)
    elif selected == "Setting":
        setting_page()

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
        col1.metric("Ventes Totales", f"${filtered_sales['Total_sale'].sum():,.2f}")
        col2.metric("Vente Moyenne", f"${filtered_sales['Total_sale'].mean():,.2f}")
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
    col1.metric("Ventes Totales", f"${filtered_sales['Total_sale'].sum():,.0f}")
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
