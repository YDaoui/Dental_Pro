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
        st.markdown("<h2 style='color: #007bad; margin-top: 0;'>Coaching Agent</h2>", unsafe_allow_html=True)
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

    # Création d'un layout en trois colonnes pour les informations principales
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**Offre:** {selected_row.get('Offre', 'N/A')}")
        st.markdown(f"**Date:** {selected_row.get('Date de création', 'N/A')}")
        st.markdown(f"**Direction:** {selected_row.get('Direction', 'N/A')}")

    with col2:
        st.markdown(f"**Canal:** {selected_row.get('Canal', 'N/A')}")
        st.markdown(f"**Statut BP:** {selected_row.get('Statut Bp', 'N/A')}")
        st.markdown(f"**Sous motif:** {selected_row.get('Sous motif', 'N/A')}")

    # Extraction du Num_Bp et Hyp
    num_bp = selected_row.get('Num_Bp')
    hyp_agent = selected_row.get('Hyp', 'N/A')
    
    with col3:
        st.markdown(f"**Numéro BP:** {num_bp if num_bp else 'N/A'}")
        st.markdown(f"**Agent (Hyp):** {hyp_agent}")

    # Bouton en dessous des colonnes, aligné à gauche
    if num_bp:
        col_btn, _ = st.columns([1, 1.5])  # 1/4 de largeur pour le bouton
        with col_btn:
            if st.button("🔎 Rechercher des informations complémentaires", 
                        key=f"btn_{num_bp}"):
                # Affichage des informations complémentaires sous le bouton
                with st.container():
                    search_additional_info(conn, num_bp, hyp_agent)
    else:
        st.warning("Identifiant client non disponible")

def search_in_table(conn, hyp_agent, table_name):
    """Recherche dans une table spécifique et retourne les colonnes demandées"""
    try:
        if table_name == "Sales":
            query = f"""
            SELECT ORDER_DATE, SHORT_MESSAGE, Country, City, Total_Sale AS Montant 
            FROM {table_name} 
            WHERE CAST(Hyp AS VARCHAR) = ?
            ORDER BY ORDER_DATE DESC
            """
        elif table_name == "Recolts":
            query = f"""
            SELECT ORDER_DATE, SHORT_MESSAGE, Country, City, Total_Recolt AS Montant 
            FROM {table_name} 
            WHERE CAST(Hyp AS VARCHAR) = ?
            ORDER BY ORDER_DATE DESC
            """
        else:
            return None
            
        df = pd.read_sql(query, conn, params=[str(hyp_agent)])  # Convertir en string pour être sûr
        return df
        
    except Exception as e:
        st.error(f"Erreur avec {table_name}: {str(e)}")
        return None

def search_additional_info(conn, num_bp, hyp_agent):
    """Recherche des informations complémentaires"""
    st.markdown("---")
    st.subheader(f"Coaching - BP: {num_bp} (Agent: {hyp_agent})")
    
    # Recherche dans les tables Sales et Recolts
    found_data = None
    
    for table in ["Sales", "Recolts"]:
        df = search_in_table(conn, num_bp, table)
        if df is not None and not df.empty:
            found_data = df
            st.success(f"Données trouvées dans la table {table}:")
            
            # Afficher les informations dans un tableau formaté
            data = {
                "Date commande": [df.iloc[0]['ORDER_DATE']],
                "Pays": [df.iloc[0]['Country']],
                "Ville": [df.iloc[0]['City']],
                "Montant": [df.iloc[0]['Montant']],
                "Message": [df.iloc[0]['SHORT_MESSAGE']]
            }
            st.table(pd.DataFrame(data))
            break
    
    if found_data is None:
        st.info("Aucun résultat trouvé dans les tables Sales ou Recolts.")
    
    # Recherche dans la table Logs
    st.markdown("---")
    st.subheader("Détails du coaching")
    
    try:
        query_logs = """
        SELECT Offre, [Sous Motif] 
        FROM Logs 
        WHERE Hyp = ? AND Num_Bp = ?
        """
        df_logs = pd.read_sql(query_logs, conn, params=[hyp_agent, num_bp])
        
        if not df_logs.empty:
            log_data = {
                "Offre": [df_logs.iloc[0]['Offre']],
                "Sous motif": [df_logs.iloc[0]['Sous Motif']]
            }
            st.table(pd.DataFrame(log_data))
        else:
            st.info("Aucune information supplémentaire trouvée dans les Logs")
            
    except Exception as e:
        st.error(f"Erreur lors de la recherche dans les Logs: {str(e)}")

def afficher_coaching():
    """Affiche le module de coaching"""
    st.subheader("Coaching - Liste des Effectifs")

    conn = get_db_connection()
    if conn is None:
        st.error("Erreur de connexion à la base de données")
        return

    try:
        # Chargement des données
        df_effectifs = pd.read_sql("SELECT * FROM Effectifs where Type = 'Agent'", conn)

        if df_effectifs.empty:
            st.warning("Aucun effectif trouvé dans la base de données")
            return

        # Vérification des colonnes nécessaires
        if "NOM" not in df_effectifs.columns or "PRENOM" not in df_effectifs.columns:
            st.error("Les colonnes 'NOM' ou 'PRENOM' sont absentes dans la table Effectifs.")
            return

        # Création du nom complet
        df_effectifs["NomComplet"] = df_effectifs["NOM"] + " " + df_effectifs["PRENOM"]

        # Layout en 2 colonnes (gauche pour infos agent et bouton, droite pour autres infos)
        col_left, col_right = st.columns([4, 6])

        # Colonne gauche: Sélection de l'agent et informations
        with col_left:
            selection = st.selectbox("Sélectionner un agent", 
                                   df_effectifs["NomComplet"].unique(),
                                   key="coaching_agent_select")

            if selection:
                # Récupération des informations de l'agent
                nom, prenom = selection.split(" ", 1)
                agent = df_effectifs[(df_effectifs["NOM"] == nom) & 
                                  (df_effectifs["PRENOM"] == prenom)]

                if agent.empty:
                    st.error("Agent non trouvé")
                    return

                agent = agent.iloc[0]
                st.markdown("---")

                # Affichage des informations de base de l'agent
                st.markdown(f"**Nom :** {agent['NOM']}")
                st.markdown(f"**Prénom :** {agent['PRENOM']}")
                st.markdown(f"**Team :** {agent['Team']}")
                st.markdown(f"**Activité :** {agent['Activité']}")
                st.markdown(f"**Departement :** {agent['Departement']}")
                st.markdown(f"**Date entrée :** {agent['Date_In']}")
                st.markdown(f"**Hyp :** {agent['Hyp']}")

                # Bouton de recherche
                if st.button("🔎 Rechercher les transactions"):
                    hyp_agent = agent["Hyp"]
                    
                    # Recherche dans les tables Sales et Recolts
                    with st.expander("Historique des transactions"):
                        # Création d'onglets pour Sales et Recolts
                        tab1, tab2 = st.tabs(["Ventes (Sales)", "Recoltes (Recolts)"])
                        
                        with tab1:
                            df_sales = search_in_table(conn, hyp_agent, "Sales")
                            if df_sales is not None and not df_sales.empty:
                                st.dataframe(df_sales)
                            else:
                                st.info("Aucune donnée de vente trouvée")
                        
                        with tab2:
                            df_recolts = search_in_table(conn, hyp_agent, "Recolts")
                            if df_recolts is not None and not df_recolts.empty:
                                st.dataframe(df_recolts)
                            else:
                                st.info("Aucune donnée de recolte trouvée")

        # Colonne droite: Affichage des logs
        with col_right:
            if selection:
                hyp_agent = agent["Hyp"]
                df_logs = pd.read_sql("SELECT * FROM Logs WHERE Hyp = ?", 
                                      conn, 
                                      params=[hyp_agent])

                if df_logs.empty:
                    st.info("Aucun historique trouvé pour cet agent")
                else:
                    display_logs_with_interaction(df_logs, conn)

    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")
    finally:
        if conn:
            conn.close()