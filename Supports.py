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
from st_aggrid import AgGrid, GridOptionsBuilder

# Modules internes
from Utils_Dental import *
from Managers import *

def support_dashboard():
    """Fonction principale pour afficher le tableau de bord Support"""
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image('Dental_Implant2.png', width=150)
    with col2:
        st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Dashboard Support</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #007bad; margin-top: 0;'>Settings All Agents</h2>", unsafe_allow_html=True)
        st.markdown("---")

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

def display_logs_with_interaction(df_logs, conn):
    """Affiche les logs avec interaction"""
    if df_logs.empty:
        st.warning("Aucune donnée à afficher")
        return

    # S'assurer que la colonne Num_Bp est accessible
    if 'Num_Bp' not in df_logs.columns and len(df_logs.columns) >= 4:
        df_logs = df_logs.rename(columns={df_logs.columns[3]: 'Num_Bp'})

    gb = GridOptionsBuilder.from_dataframe(df_logs)
    gb.configure_selection('single', use_checkbox=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        df_logs,
        gridOptions=grid_options,
        height=400,
        width='100%',
        theme='streamlit',
        enable_enterprise_modules=False,
        update_mode='SELECTION_CHANGED'
    )

    # Gestion spécifique du cas où selected_rows est un DataFrame
    selected_rows = grid_response.get('selected_rows', pd.DataFrame())
    
    if isinstance(selected_rows, pd.DataFrame):
        if not selected_rows.empty:
            # Convertir la première ligne du DataFrame en dictionnaire
            selected_row = selected_rows.iloc[0].to_dict()
            with st.expander("Détails de l'offre sélectionnée"):
                display_offer_details(selected_row, conn)
        else:
            st.info("Veuillez sélectionner une ligne dans le tableau pour voir les détails.")
    elif isinstance(selected_rows, list) and len(selected_rows) > 0:
        # Cas où selected_rows est une liste (version précédente)
        selected_row = selected_rows[0]
        if hasattr(selected_row, 'to_dict'):
            selected_row = selected_row.to_dict()
        with st.expander("Détails de l'offre sélectionnée"):
            display_offer_details(selected_row, conn)
    else:
        st.info("Veuillez sélectionner une ligne dans le tableau pour voir les détails.")

def display_offer_details(selected_row, conn):
    """Affiche les détails d'une offre sélectionnée"""
    # Conversion en dict si ce n'est pas déjà le cas
    if not isinstance(selected_row, dict):
        try:
            selected_row = dict(selected_row)
        except Exception as e:
            st.error(f"Erreur de conversion: {str(e)}")
            return

    # Création d'un layout en deux colonnes
    col1, col2 , col3 = st.columns(3)

    with col1:
        st.markdown(f"**Offre:** {selected_row.get('Offre', 'N/A')}")
        st.markdown(f"**Date:** {selected_row.get('Date de création', 'N/A')}")
        st.markdown(f"**Direction:** {selected_row.get('Direction', 'N/A')}")

    with col2:
        st.markdown(f"**Canal:** {selected_row.get('Canal', 'N/A')}")
        st.markdown(f"**Statut BP:** {selected_row.get('Statut Bp', 'N/A')}")
        st.markdown(f"**Sous motif :** {selected_row.get('Sous motif', 'N/A')}")

    # Extraction du Num_Bp avec plusieurs fallbacks
    num_bp = selected_row.get('Num_Bp') #or selected_row.get('Num_Bp') or selected_row.get('BP')
    
   
    
    if num_bp:
            st.markdown(f"**Numéro BP :** {num_bp}")
            if st.button("🔎 Rechercher des informations complémentaires"):
                search_additional_info(selected_row, conn)
    else:
            st.warning("Identifiant client non disponible pour cette offre")

def search_in_table(conn, num_bp, table_name):
    """Version qui tente de deviner la colonne ID"""
    try:
        # D'abord essayer avec les noms de colonnes courants
        for col in 'Num_Bp':
            try:
                query = f"SELECT  * FROM {table_name} WHERE ORDER_REFERENCE = ?"
                df = pd.read_sql(query, conn, params=[num_bp])
                if not df.empty:
                    st.success(f"Trouvé dans {table_name}.{col}")
                    st.dataframe(df)
                    return True
            except:
                continue
                
        st.info(f"Aucun résultat dans {table_name} (colonnes testées: Num_Bp, BP, ID_Client, etc.)")
        return False
        
    except Exception as e:
        st.error(f"Erreur grave avec {table_name}: {str(e)}")
        return False

def search_additional_info(selected_row, conn):
    """Recherche des informations complémentaires"""
    # Essayer différentes méthodes pour obtenir le Num_Bp
    num_bp = selected_row.get('Num_Bp')
    
    if num_bp is None and len(selected_row) >= 4:
        num_bp = list(selected_row.values())[3]  # 4ème colonne
        
    if not num_bp:
        st.error("Impossible de trouver le Numéro BP")
        return

    st.markdown("---")
    st.subheader(f"Résultats de la recherche pour le BP: {num_bp}")

    found_result = False

    found_result |= search_in_table(conn, num_bp, "Sales")
    found_result |= search_in_table(conn, num_bp, "Recolts")

    if not found_result:
        st.info("Aucun résultat trouvé dans les tables Sales ou Recolts.")


def afficher_coaching():
    """Affiche le module de coaching"""
    st.subheader("Coaching - Liste des Effectifs")

    conn = get_db_connection()
    if conn is None:
        st.error("Erreur de connexion à la base de données")
        return

    try:
        df_effectifs = pd.read_sql("SELECT * FROM Effectifs where Type = 'Agent'", conn)
        if df_effectifs.empty:
            st.warning("Aucun effectif trouvé dans la base de données")
            return

        if "NOM" in df_effectifs.columns and "PRENOM" in df_effectifs.columns:
            df_effectifs["NomComplet"] = df_effectifs["NOM"] + " " + df_effectifs["PRENOM"]
        else:
            st.error("Les colonnes 'NOM' ou 'PRENOM' sont absentes dans la table Effectifs.")
            return

        selection = st.selectbox("Sélectionner un agent", df_effectifs["NomComplet"].unique())

        if selection:
            nom, prenom = selection.split(" ", 1)
            agent = df_effectifs[(df_effectifs["NOM"] == nom) & (df_effectifs["PRENOM"] == prenom)]

            if agent.empty:
                st.error("Agent non trouvé")
                return

            agent = agent.iloc[0]
            st.markdown("---")
            col1, col2, col3  = st.columns(3)

            with col1:
                st.markdown(f"**Nom :** {agent['NOM']}")
                st.markdown(f"**Prénom :** {agent['PRENOM']}")
                st.markdown(f"**Team :** {agent['Team']}")
            with col2:
                
                st.markdown(f"**Activité :** {agent['Activité']}")
                st.markdown(f"**Departement :** {agent['Departement']}")
                st.markdown(f"**Date entrée  :** {agent['Date_In']}")
            with col3:
                st.markdown(f"**Hyp :** {agent['Hyp']}")

            hyp_agent = agent["Hyp"]
            df_logs = pd.read_sql("SELECT * FROM Logs WHERE Hyp = ?", conn, params=[hyp_agent])

            if df_logs.empty:
                st.info("Aucun historique trouvé pour cet agent")
                return

            display_logs_with_interaction(df_logs, conn)
    finally:
        conn.close()
