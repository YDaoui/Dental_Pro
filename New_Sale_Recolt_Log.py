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


def New_Sale_Agent():
    add_custom_css()
    hyp_agent = st.session_state.get("hyp", None)

    conn = get_db_connection()
    st.markdown("---")
    st.subheader("Nouvelle  Vente")
    try:
        # En-tête avec logo et titre
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:

      
            st.markdown("### Numéro du BP")
            

            order_reference = st.text_input("Order Reference")
            order_date = st.date_input("Order Date", value=datetime.today())
            country = st.selectbox("Country", ["Autriche", "France"])

            # Villes selon le pays sélectionné
            cities_autriche = ["Vienne", "Graz", "Linz", "Salzbourg"]
            cities_france = ["Paris", "Lyon", "Marseille", "Toulouse"]
            city = st.selectbox("City", cities_autriche if country == "Autriche" else cities_france)

            
        with col2:
            
            

            
            st.markdown("### Montant (€)")
            short_message = st.selectbox("Short Message", ["Accepted", "Refused", "Error"])
            montant_col1, montant_col2 = st.columns([2, 1])
            with montant_col1:
                    montant_input = st.number_input("Saisir le montant", min_value=0.0, step=5.0, format="%.2f")
            with montant_col2:
                    montant_slider = st.slider("ou avec le slider", min_value=0, max_value=1000, step=5)
            rating = st.slider("Rating", min_value=1, max_value=9)
                # Rating de 1 à 9
            


            #with col3:
                

                #st.markdown("### Actions")
                
            # Montant avec slider et saisie manuelle
          
            valider, annuler = st.columns(2)
            with valider:
                    if st.button("✅ Valider"):
                        st.success("Données validées avec succès.")
                        # Tu peux ajouter ici l'insertion en base
            with annuler:
                    if st.button("❌ Annuler"):
                        st.warning("Saisie annulée.")
                    
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
    finally:
        conn.close()

     
def New_Recolt_Agent():
    add_custom_css()
    hyp_agent = st.session_state.get("hyp", None)

    conn = get_db_connection()
    st.markdown("---")
    st.subheader("Nouvelle Récolt")
    try:
        # En-tête avec logo et titre
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:

      
            st.markdown("### Numéro du BP")
            

            order_reference = st.text_input("Order Reference")
            order_date = st.date_input("Order Date", value=datetime.today())
            country = st.selectbox("Country", ["Autriche", "France"])

            # Villes selon le pays sélectionné
            cities_autriche = ["Vienne", "Graz", "Linz", "Salzbourg"]
            cities_france = ["Paris", "Lyon", "Marseille", "Toulouse"]
            city = st.selectbox("City", cities_autriche if country == "Autriche" else cities_france)

            
        with col2:
            
            

            
            st.markdown("### Montant (€)")
            short_message = st.selectbox("Short Message", ["Accepted", "Refused", "Error"])
            montant_col1, montant_col2 = st.columns([2, 1])
            with montant_col1:
                    montant_input = st.number_input("Saisir le montant", min_value=0.0, step=5.0, format="%.2f")
            with montant_col2:
                    montant_slider = st.slider("ou avec le slider", min_value=0, max_value=1000, step=5)
            rating = st.slider("Rating", min_value=1, max_value=9)
                # Rating de 1 à 9
            


            #with col3:
                

                #st.markdown("### Actions")
                
            # Montant avec slider et saisie manuelle
          
            valider, annuler = st.columns(2)
            with valider:
                    if st.button("✅ Valider"):
                        st.success("Données validées avec succès.")
                        # Tu peux ajouter ici l'insertion en base
            with annuler:
                    if st.button("❌ Annuler"):
                        st.warning("Saisie annulée.")
                    
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
    finally:
        conn.close()
