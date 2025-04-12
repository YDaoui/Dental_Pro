
import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px
from datetime import datetime
from streamlit_option_menu import option_menu
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from contextlib import closing
from PIL import Image
from Utils_Dental import *

from Managers import *


def support_dashboard():
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image('Dental_Implant2.png', width=150)
    with col2:
        st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Dashboard Support</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #007bad; margin-top: 0;'>Settings All Agents</h2>", unsafe_allow_html=True)

        st.markdown("---")

    #st.markdown("<h2 style='font-size: 38px; font-weight: bold; color: #00afe1;'>Paramètres Utilisateur</h2>", unsafe_allow_html=True)
    #st.title("Dashboard Support")

    # Menu spécifique pour les supports
    with st.sidebar:
        st.image('Dental_Implant.png', width=350)
        menu_options = ["Accueil", "Coaching"]
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=["house", "people"],
            default_index=0,
            styles={
                "container": {"background-color": "#002a48"},
                "icon": {"color": "#00afe1", "font-size": "18px"},
                "nav-link": {"color": "#ffffff", "font-size": "16px"},
                "nav-link-selected": {"background-color": "#007bad"}
            }
        )

    if selected == "Coaching":
        afficher_coaching()
    else:
        st.write("Bienvenue sur le tableau de bord Support")

def afficher_coaching():
    st.subheader("Coaching - Liste des Effectifs")

    conn = get_db_connection()
    if not conn:
        st.error("Erreur de connexion à la base de données")
        return
    
    try:
        # Récupérer le team du support connecté
        user_hyp = st.session_state["hyp"]
        df_effectifs = pd.read_sql("SELECT * FROM Effectifs", conn)

        # Trouver l'équipe du support connecté
        team_support = df_effectifs.loc[df_effectifs["Hyp"] == user_hyp, "Team"].values[0]

        # Filtrer les effectifs de la même équipe
        equipe = df_effectifs[df_effectifs["Team"] == team_support]

        # Créer une liste des noms complets pour la sélection
        equipe["NomComplet"] = equipe["NOM"] + " " + equipe["PRENOM"]
        
        # Sélection de l'agent
        selection = st.selectbox("Sélectionner un agent", equipe["NomComplet"])

        if selection:
            nom, prenom = selection.split(" ", 1)
            agent = equipe[(equipe["NOM"] == nom) & (equipe["PRENOM"] == prenom)].iloc[0]

            # Afficher les informations de l'agent
            st.markdown(f"""
            **Nom :** {agent["NOM"]}  
            **Prénom :** {agent["PRENOM"]}  
            **Type :** {agent["Type"]}  
            **Activité :** {agent["Activité"]}  
            **Team :** {agent["Team"]}  
            **Date In :** {agent["Date_In"].strftime('%d/%m/%Y') if pd.notnull(agent["Date_In"]) else 'N/A'}  
            """)

            # Récupérer les infos de la table Logs
            hyp_agent = agent["Hyp"]
            df_logs = pd.read_sql(f"SELECT [Offre], [Date de création] FROM Logs WHERE Hyp = '{hyp_agent}'", conn)

            if not df_logs.empty:
                st.markdown("### Historique des Offres")
                st.dataframe(df_logs)
            else:
                st.info("Aucun historique d'offres trouvé pour cet agent")
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
    finally:
        conn.close()
