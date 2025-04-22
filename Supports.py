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
from Utils_Dental import *
from Supports import *
from Logs import *
from Recolts import *
from Sales import *
from Supports import *
from Agents import *


def format_dataframe(df, table_type):
    """Formate le dataframe selon les spécifications"""
    if df is None or df.empty:
        return df
    
    # Copie du dataframe pour éviter les warnings
    df = df.copy()
    
    # Format ORDER_REFERENCE sans virgule (en entier)
    if 'ORDER_REFERENCE' in df.columns:
        df['ORDER_REFERENCE'] = df['ORDER_REFERENCE'].astype(str).str.replace(',', '').str.replace('.', '')
    
    # Format date "12 Mars 2018"
    if 'ORDER_DATE' in df.columns:
        df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE']).dt.strftime('%d %B %Y')
    
    # Format montant en euros
    if 'Montant' in df.columns:
        df['Montant'] = df['Montant'].apply(lambda x: f"{float(x):,.2f} €".replace(',', ' ').replace('.', ','))
    
    # Renommer les colonnes en français
    df = df.rename(columns={
        'ORDER_REFERENCE': 'Référence',
        'ORDER_DATE': 'Date commande',
        'SHORT_MESSAGE': 'Message',
        'Country': 'Pays',
        'City': 'Ville',
        'Montant': 'Montant (€)'
    })
    
    return df

def display_formatted_data(df, table_type):
    """Affiche les données formatées avec style"""
    if df is None or df.empty:
        st.info(f"Aucune donnée de {table_type} trouvée")
        return
    
    # Appliquer le style gradient
    def color_gradient(val):
        color = '#f0f8ff' if val.name % 2 == 0 else '#e6f3ff'
        return [f'background-color: {color}' for _ in val]
    
    # Afficher avec style
    st.dataframe(
        df.style
        .apply(color_gradient, axis=1)
        .set_properties(**{
            'text-align': 'left',
            'font-size': '14px',
            'border': '1px solid #007bad'
        }),
        height=400,
        use_container_width=True
    )

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
        menu_options = ["Accueil", "Coaching", "My Coaching"]
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=["house", "people","calendar"],
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
            display_offer_details(selected_row, conn)
        else:
            st.info("Veuillez sélectionner une ligne dans le tableau pour voir les détails.")
    elif isinstance(selected_rows, list) and len(selected_rows) > 0:
        # Cas où selected_rows est une liste (version précédente)
        selected_row = selected_rows[0]
        if hasattr(selected_row, 'to_dict'):
            selected_row = selected_row.to_dict()
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
    st.markdown("---")
    st.subheader("Détails de l'offre sélectionnée")
    
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

    # Bouton de recherche
    if num_bp:
        if st.button("🔎 Rechercher des informations complémentaires", 
                    key=f"btn_{num_bp}"):
            search_additional_info(conn, num_bp, hyp_agent)
    else:
        st.warning("Identifiant client non disponible")

def search_in_table(conn, hyp_agent, table_name):
    """Recherche dans une table spécifique et retourne les colonnes demandées"""
    try:
        if table_name == "Sales":
            query = f"""
            SELECT ORDER_REFERENCE, ORDER_DATE, SHORT_MESSAGE, Country, City, Total_Sale AS Montant 
            FROM {table_name} 
            WHERE CAST(Hyp AS VARCHAR) = ?
            ORDER BY ORDER_DATE DESC
            """
        elif table_name == "Recolts":
            query = f"""
            SELECT ORDER_REFERENCE, ORDER_DATE, SHORT_MESSAGE, Country, City, Total_Recolt AS Montant 
            FROM {table_name} 
            WHERE CAST(Hyp AS VARCHAR) = ?
            ORDER BY ORDER_DATE DESC
            """
        else:
            return None
            
        df = pd.read_sql(query, conn, params=[str(hyp_agent)])
        return format_dataframe(df, table_name)
        
    except Exception as e:
        st.error(f"Erreur avec {table_name}: {str(e)}")
        return None

def search_additional_info(conn, num_bp, hyp_agent):
    """Recherche des informations complémentaires"""
    st.markdown("---")
    st.subheader(f"Coaching - BP: {num_bp} (Agent: {hyp_agent})")
    
    # Recherche dans les tables Sales et Recolts
    found_data = None
    total_amount = None
    order_date = None
    country = None
    city = None
    short_message = None
    
    for table in ["Sales", "Recolts"]:
        df = search_in_table(conn, hyp_agent, table)
        if df is not None and not df.empty:
            found_data = df.iloc[0]
            st.success(f"Données trouvées dans la table {table}:")
            
            # Stocker les valeurs pour la colonne 2
            total_amount = found_data['Montant (€)']
            order_date = found_data['Date commande']
            country = found_data['Pays']
            city = found_data['Ville']
            short_message = found_data['Message']
            
            # Afficher les informations dans un tableau formaté
            data = {
                "Référence": [found_data['Référence']],
                "Date commande": [order_date],
                "Pays": [country],
                "Ville": [city],
                "Montant (€)": [total_amount],
                "Message": [short_message]
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
        SELECT Num_Bp ,Offre, [Sous Motif], Canal, Direction
        FROM Logs 
        WHERE Hyp = ? AND Num_Bp = ?
        """
        df_logs = pd.read_sql(query_logs, conn, params=[hyp_agent, num_bp])
        
        if not df_logs.empty:
            sous_motif = df_logs.iloc[0]['Sous Motif']
            log_data = {
                "Réféeance": [df_logs.iloc[0]['Num_Bp']],
                "Offre": [df_logs.iloc[0]['Offre']],
                "Canal": [df_logs.iloc[0]['Canal']],
                "Direction": [df_logs.iloc[0]['Direction']],
                "Sous motif": [sous_motif]
            }
            st.table(pd.DataFrame(log_data))
        else:
            st.info("Aucune information supplémentaire trouvée dans les Logs")
            sous_motif = "N/A"
            
    except Exception as e:
        st.error(f"Erreur lors de la recherche dans les Logs: {str(e)}")
        sous_motif = "N/A"
    
    # Section Évaluation du Coaching
    st.markdown("---")
    st.subheader("Évaluation du Coaching")
    
    # Récupération des informations utilisateur
    #input_user = get_user_details().username  # À adapter selon votre implémentation
    date_coaching = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Affichage des informations fixes
    #st.markdown(f"**Coach:** {input_user}")
    st.markdown(f"**Date de Coaching:** {date_coaching}")
    st.markdown(f"**ID Hyp:** {hyp_agent}")
    
    # Sélection de la Phase
    phase_options = ["Already saled", "Already recolts", "Informations"]
    phase = st.selectbox("Phase", options=phase_options, key="phase_select")
    
    # Sélection de l'Évaluation
    evaluation_options = [
        "Maitrise partielle metier",
        "Maitrise Parfaite metier", 
        "Tutorat demandé",
        "Tutorat suggéré",
        "Erreur Concentration"
    ]
    evaluation = st.selectbox("Évaluation", options=evaluation_options, key="eval_select")
    
    # Champ d'observation
    observation = st.text_area("Observation", height=100)
    
    # Affichage des données complémentaires
    st.markdown("---")
    st.subheader("Données Complémentaires")
    
    data_complement = {
        "Sous motif": [sous_motif],
        "Short Message": [short_message if short_message else "N/A"],
        "Country": [country if country else "N/A"],
        "City": [city if city else "N/A"],
        "Montant": [total_amount if total_amount else "N/A"],
        "Order Date": [order_date if order_date else "N/A"]
    }
    
    st.table(pd.DataFrame(data_complement))
    
    # Bouton de soumission
    if st.button("Enregistrer l'évaluation"):
        # Ici vous pouvez ajouter le code pour enregistrer en base de données
        st.success("Évaluation enregistrée avec succès!")

def afficher_coaching():
    
    #add_custom_css()
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

        # Sélection de l'agent
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
            
            # Affichage des informations de base de l'agent
            st.markdown("---")
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
                
                # Création d'onglets pour Sales et Recolts
                tab1, tab2 = st.tabs(["Ventes (Sales)", "Recoltes (Recolts)"])
                
                with tab1:
                    df_sales = search_in_table(conn, hyp_agent, "Sales")
                    display_formatted_data(df_sales, "vente")
                
                with tab2:
                    df_recolts = search_in_table(conn, hyp_agent, "Recolts")
                    display_formatted_data(df_recolts, "recolte")

            # Affichage des logs - NOUVELLE REQUÊTE AVEC LES DEUX CRITÈRES
            st.markdown("---")
            st.subheader("Liste des Offres")
            
            # Nouvelle requête qui joint Logs avec Sales ou Recolts
            query_logs = """
            SELECT DISTINCT l.* 
            FROM Logs l
            LEFT JOIN Sales s ON l.Num_Bp = s.ORDER_REFERENCE
            LEFT JOIN Recolts r ON l.Num_Bp = r.ORDER_REFERENCE
            WHERE l.Hyp = ? 
            AND (s.ORDER_REFERENCE IS NOT NULL OR r.ORDER_REFERENCE IS NOT NULL)
            AND l.Offre <> ''
            ORDER BY l.[Date de création] DESC
            """
            
            df_logs = pd.read_sql(query_logs, conn, params=[agent["Hyp"]])

            if df_logs.empty:
                st.info("Aucun historique trouvé pour cet agent")
            else:
                display_logs_with_interaction(df_logs, conn)

    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")
    finally:
        if conn:
            conn.close()