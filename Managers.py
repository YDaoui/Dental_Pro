
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
from Agents import *
from New_Sale_Recolt_Log import *
from Model_Planif import simulation_planning



def main_dashboard(logs_df ,sales_df, recolts_df, staff_df, start_date, end_date):
    """Dashboard principal avec onglets Sales et Recolts."""
    
    tab1, tab2,tab3 = st.tabs(["📊 Ventes", "💰 Récompences","🧾 Logs "])

    with tab1:
        sales_page(sales_df, staff_df, start_date, end_date)

    with tab2:
        recolts_page(recolts_df, staff_df, start_date, end_date)
    with tab3:
        logs_page(logs_df, staff_df, start_date, end_date)

def manager_dashboard():
    
    #add_custom_css()
    """Tableau de bord principal."""
  
    sales_df, recolts_df, staff_df, logs_df = load_data()
    logs_df = preprocess_data(logs_df)
    sales_df = preprocess_data(sales_df)
    recolts_df = preprocess_data(recolts_df)
    staff_df = preprocess_data(staff_df)


    with st.sidebar:
        st.image('Dental_Implant.png', width=350)
        #st.markdown(
       # f"<h2 style='color: #007bad;text-align: left;'>Créer par: {st.session_state.get('username', 'Agent')}</h2>",
       # unsafe_allow_html=True
    #)
        st.markdown(
        f"<h2 style='color: #007bad;text-align: center;'>Créer par : Yassine Daoui</h2>",
        unsafe_allow_html=True
    )
        st.markdown("<h2 style='font-size: 16px; color: #0E2148;'>Filtres de Dates</h2>", unsafe_allow_html=True)

        with st.expander("Période", expanded=True):
            min_date = sales_df['ORDER_DATE'].min() if not sales_df.empty else datetime.now()
            max_date = sales_df['ORDER_DATE'].max() if not sales_df.empty else datetime.now()
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Date début", min_date, min_value=min_date, max_value=max_date)
            with col2:
                end_date = st.date_input("Date fin", max_date, min_value=min_date, max_value=max_date)
        
      
        if st.session_state.get("user_type") == "Hyperviseur":
            menu_options = ["Dashbord Global", "Ventes", "Récompences", "Logs","Nouvelle Vente","Nouvelle Récolt", "Coachings", "Settings"]
            icons = ["bar-chart", "credit-card", "box-seam", "file-earmark-text","credit-card","credit-card", "person-lines-fill", "gear"]

        elif st.session_state.get("user_type") == "Support":
            menu_options = ["Dashbord Global", "Coachings"]
            icons = ["bar-chart", "person-lines-fill"] 

        elif st.session_state.get("user_type") == "Manager": 
            menu_options = ["Dashbord Global", "Ventes", "Récompences", "Coachings", "Settings"] 
            icons = ["bar-chart", "credit-card", "box-seam", "person-lines-fill", "gear"]

        elif st.session_state.get("user_type") == "Agent": 
            menu_options = ["Dashbord Global", "Ventes", "Récompences"] 
            icons = ["bar-chart", "credit-card", "box-seam"]
            
        else: 
            menu_options = ["Dashbord Global"]
            icons = ["bar-chart"]
            
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=icons,
            default_index=0,
            styles={
                "container": {"background-color": "#043a64"},
                "icon": {"color": "#00afe1", "font-size": "18px"},
                "nav-link": {"color": "#ffffff", "font-size": "16px"},
                "nav-link-selected": {"background-color": "#fc9307"}
            }
        )
        
        
     
    if selected == "Dashbord Global":
        dashboard_page(logs_df, sales_df, recolts_df, staff_df, start_date, end_date)  
    elif selected == "Ventes":
        sales_page1(sales_df, staff_df, start_date, end_date)
    elif selected == "Récompences":
        recolts_page1(recolts_df, staff_df, start_date, end_date)
    elif selected == "Logs":
        logs_page1(logs_df, staff_df, start_date, end_date)
    elif selected =="Nouvelle Vente":
        New_Sale_Agent()
    elif selected =="Nouvelle Récolt":
        New_Recolt_Agent()
    elif selected == "Coachings":
        afficher_coaching()
    elif selected == "Settings":
        setting_page()


if __name__ == "__main__":
    manager_dashboard()
