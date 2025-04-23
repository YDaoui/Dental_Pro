# Import des bibliothèques
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_option_menu import option_menu
from Utils_Dental import *
from Supports import *
from Sales import *
from Recolts import *

# Fonctions de chargement et prétraitement des données

def main_dashboard(logs_df ,sales_df, recolts_df, staff_df, start_date, end_date):
    """Dashboard principal avec onglets Sales et Recolts."""
    
    tab1, tab2,tab3 = st.tabs(["📊 Ventes", "💰 Récoltes","🧾 Logs "])

    with tab1:
        sales_page(sales_df, staff_df, start_date, end_date)

    with tab2:
        recolts_page(recolts_df, staff_df, start_date, end_date)
    with tab3:
        logs_page(logs_df, start_date, end_date)
# Fonction principale
def manager_dashboard():
    add_custom_css()
    """Tableau de bord principal."""
    # Chargement des données
    sales_df, recolts_df, staff_df, logs_df = load_data()
    logs_df = preprocess_data(logs_df)
    sales_df = preprocess_data(sales_df)
    recolts_df = preprocess_data(recolts_df)
    staff_df = preprocess_data(staff_df)

    # Sidebar
    with st.sidebar:
        st.image('Dental_Implant.png', width=350)
        
        # Menu en fonction du type d'utilisateur
        if st.session_state.get("user_type") == "Hyperviseur":
            menu_options = ["Tableau de bord", "Sales", "Recolt", "Logs", "Coaching", "Planning", "Setting"]
            icons = ["bar-chart", "currency-dollar", "list-ul", "calendar", "calendar", "calendar", "gear"]
        elif st.session_state.get("user_type") == "Support":
            menu_options = ["Tableau de bord", "Coaching"]
            icons = ["bar-chart", "currency-dollar"]
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
        dashboard_page(logs_df, sales_df, recolts_df, staff_df, start_date, end_date)  # Now passing all required arguments
    elif selected == "Sales":
        sales_page(sales_df, staff_df, start_date, end_date)
    elif selected == "Recolt":
        recolts_page(recolts_df, staff_df, start_date, end_date)
    elif selected == "Logs":
        logs_page(logs_df, start_date, end_date)
    elif selected == "Coaching":
        afficher_coaching()
    elif selected == "Planning":
        planning_page(sales_df, staff_df)
    elif selected == "Setting":
        setting_page()

# Point d'entrée de l'application
if __name__ == "__main__":
    manager_dashboard()  