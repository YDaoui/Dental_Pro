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
from Logs import *
from Model_Planif import simulation_planning

# Fonctions de chargement et prétraitement des données

def main_dashboard(logs_df ,sales_df, recolts_df, staff_df, start_date, end_date):
    """Dashboard principal avec onglets Sales et Recolts."""
    
    tab1, tab2,tab3 = st.tabs(["📊 Ventes", "💰 Récompences","🧾 Logs "])

    with tab1:
        sales_page(sales_df, staff_df, start_date, end_date)

    with tab2:
        recolts_page(recolts_df, staff_df, start_date, end_date)
    with tab3:
        logs_page(logs_df, staff_df, start_date, end_date)
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
            menu_options = ["Dashbord Global", "Ventes", "Récompences", "Logs", "Coachings", "Settings"]
            icons = ["bar-chart", "credit-card", "box-seam", "file-earmark-text", "person-lines-fill", "gear"]

        elif st.session_state.get("user_type") == "Support":
            menu_options = ["Dashbord Global", "Coachings"]
            icons = ["bar-chart", "person-lines-fill"] # Changed to a more appropriate icon for Coachings

        elif st.session_state.get("user_type") == "Manager": # Specific condition for Manager
            menu_options = ["Dashbord Global", "Ventes", "Récompences", "Coachings", "Settings"] # Example menu for Manager
            icons = ["bar-chart", "credit-card", "box-seam", "person-lines-fill", "gear"]

        elif st.session_state.get("user_type") == "Agent": # Specific condition for Agent
            menu_options = ["Dashbord Global", "Ventes", "Récompences"] # Example menu for Agent
            icons = ["bar-chart", "credit-card", "box-seam"]
            
        else: # Fallback for any other user type or if user_type is not set
            menu_options = ["Dashbord Global"]
            icons = ["bar-chart"]
            
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=icons,
            default_index=0,
            styles={
                "container": {"background-color": "#05135c"},
                "icon": {"color": "#00afe1", "font-size": "18px"},
                "nav-link": {"color": "#ffffff", "font-size": "16px"},
                "nav-link-selected": {"background-color": "#007bad"}
            }
        )
        
        st.markdown("---")
        st.markdown("<h2 style='font-size: 16px; color: #0E2148;'>Filtres de Dates</h2>", unsafe_allow_html=True)
        
        with st.expander("Période", expanded=True):
            min_date = sales_df['ORDER_DATE'].min() if not sales_df.empty else datetime.now()
            max_date = sales_df['ORDER_DATE'].max() if not sales_df.empty else datetime.now()
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Date début", min_date, min_value=min_date, max_value=max_date)
            with col2:
                end_date = st.date_input("Date fin", max_date, min_value=min_date, max_value=max_date)

    # Gestion des pages
    if selected == "Dashbord Global":
        dashboard_page(logs_df, sales_df, recolts_df, staff_df, start_date, end_date)  # Now passing all required arguments
    elif selected == "Ventes":
        sales_page1(sales_df, staff_df, start_date, end_date)
    elif selected == "Récompences":
        recolts_page1(recolts_df, staff_df, start_date, end_date)
    elif selected == "Logs":
        logs_page1(logs_df, staff_df, start_date, end_date)
    elif selected == "Coachings":
        afficher_coaching()
    elif selected == "Settings":
        setting_page()

# Point d'entrée de l'application
if __name__ == "__main__":
    manager_dashboard()