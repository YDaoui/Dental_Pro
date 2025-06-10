import streamlit as st
import pandas as pd
import plotly.graph_objects as go 
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

def filter_data(df, country, team, activity, start_date, end_date, staff_df):
    filtered_df = df.copy()
    
    # Filtrage par date (si la colonne ORDER_DATE ou Date_d_création existe)
    date_column = 'ORDER_DATE' if 'ORDER_DATE' in filtered_df.columns else 'Date_d_création'
    
    if date_column in filtered_df.columns:
        filtered_df[date_column] = pd.to_datetime(filtered_df[date_column], errors='coerce')
        filtered_df = filtered_df[
            (filtered_df[date_column].dt.date >= start_date) & 
            (filtered_df[date_column].dt.date <= end_date)
        ]

    if country != 'Tous' and 'Country' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Country'] == country]

    if team != 'Toutes' and not staff_df.empty:
        if 'Hyp' in staff_df.columns and 'Hyp' in filtered_df.columns:
            staff_in_team = staff_df[staff_df['Team'] == team]['Hyp'].unique()
            filtered_df = filtered_df[filtered_df['Hyp'].isin(staff_in_team)]
        elif 'Staff_ID' in filtered_df.columns and 'Hyp' in staff_df.columns:
            staff_in_team = staff_df[staff_df['Team'] == team]['Hyp'].unique()
            filtered_df = filtered_df[filtered_df['Staff_ID'].isin(staff_in_team)]

    if activity != 'Toutes' and not staff_df.empty:
        if 'Hyp' in staff_df.columns and 'Hyp' in filtered_df.columns:
            staff_in_activity = staff_df[staff_df['Activité'] == activity]['Hyp'].unique()
            filtered_df = filtered_df[filtered_df['Hyp'].isin(staff_in_activity)]
        elif 'Staff_ID' in filtered_df.columns and 'Hyp' in staff_df.columns:
            staff_in_activity = staff_df[staff_df['Activité'] == activity]['Hyp'].unique()
            filtered_df = filtered_df[filtered_df['Staff_ID'].isin(staff_in_activity)]
            
    return filtered_df

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
        st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Dashboard Supports</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #007bad; margin-top: 0;'>Coachings Agents</h2>", unsafe_allow_html=True)
        st.markdown("---")

    with st.sidebar:
        st.image('Dental_Implant.png', width=350)
        menu_options = ["Accueil", "Coachings", "My Coaching"]
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

    if selected == "Coachings":
        afficher_coaching()
    else:
        st.write("Bienvenue sur le tableau de bord Support")

def display_logs_with_interaction(df_logs, conn):
    """Affiche les logs avec interaction"""
    if df_logs.empty:
        st.warning("Aucune donnée à afficher")
        return

    # S'assurer que la colonne Num_Bp est accessible
    if 'BP_Logs' not in df_logs.columns and len(df_logs.columns) >= 4:
        df_logs = df_logs.rename(columns={df_logs.columns[3]: 'BP_Logs'})

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
            # Extraction du Num_Bp et Hyp
            num_bp = selected_row.get('BP_Logs')
            hyp_agent = selected_row.get('Hyp', 'N/A')
            
            # Afficher directement le bouton de recherche
            if num_bp:
    # Initialiser l'état si non existant
                if f'show_info_{num_bp}' not in st.session_state:
                    st.session_state[f'show_info_{num_bp}'] = False
                
                # Bouton pour basculer l'affichage
                if st.button("🔎 Afficher les informations afin de Coacher", 
                            key=f"btn_{num_bp}"):
                    st.session_state[f'show_info_{num_bp}'] = not st.session_state[f'show_info_{num_bp}']
                
                # Afficher les informations si l'état est True
                if st.session_state[f'show_info_{num_bp}']:
                    search_additional_info(conn, num_bp, hyp_agent)
            else:
                st.warning("Identifiant client non disponible")
    elif isinstance(selected_rows, list) and len(selected_rows) > 0:
        # Cas où selected_rows est une liste (version précédente)
        selected_row = selected_rows[0]
        if hasattr(selected_row, 'to_dict'):
            selected_row = selected_row.to_dict()
        num_bp = selected_row.get('BP_Logs')
        hyp_agent = selected_row.get('Hyp', 'N/A')
        
        if num_bp:
            if st.button("🔎 Rechercher des informations complémentaires", 
                        key=f"btn_{num_bp}"):
                search_additional_info(conn, num_bp, hyp_agent)
        else:
            st.warning("Identifiant client non disponible")
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
    num_bp = selected_row.get('BP_Logs')
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
        elif table_name == "Recolt":
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
    """Recherche et affiche les informations complémentaires dans un seul tableau fusionné"""
    try:
        query_agent = """
        SELECT NOM, PRENOM 
        FROM Effectifs 
        WHERE Hyp = ?
        """
        df_agent = pd.read_sql(query_agent, conn, params=[hyp_agent])
        agent_name = "Inconnu"
        if not df_agent.empty:
            agent_name = f"{df_agent.iloc[0]['PRENOM']} {df_agent.iloc[0]['NOM']}"
    except Exception as e:
        st.error(f"Erreur lors de la récupération du nom de l'agent: {str(e)}")
        agent_name = "Inconnu"

    st.markdown(
        f"""
        <h3 style='color:#002a48;'>
            Coaching - BP: {num_bp} 
            (<span style='color:#00afe1;'>Agent: {agent_name}</span>)
        </h3>
        """,
        unsafe_allow_html=True
    )
    
    # Dictionnaire pour stocker toutes les données fusionnées
    merged_data = {
        "Référence BP": num_bp,
        "Agent (Hyp)": hyp_agent,
        "Offre": "N/A",
        "Canal": "N/A",
        "Direction": "N/A",
        "Sous motif": "N/A",
        "Date commande": "N/A",
        "Pays": "N/A",
        "Ville": "N/A",
        "Montant (€)": "N/A",
        "Message": "N/A",
        "Statut": "N/A"
    }

    # 1. Recherche dans les tables Sales et Recolts
    for table in ["Sales", "Recolt"]:
        try:
            df = search_in_table(conn, hyp_agent, table)
            if df is not None and not df.empty:
                found_data = df.iloc[0]
                merged_data.update({
                    "Référence": found_data.get('Référence', 'N/A'),
                    "Date commande": found_data.get('Date commande', 'N/A'),
                    "Pays": found_data.get('Pays', 'N/A'),
                    "Ville": found_data.get('Ville', 'N/A'),
                    "Montant (€)": found_data.get('Montant (€)', 'N/A'),
                    "Message": found_data.get('Message', 'N/A'),
                    "Statut": "Vente" if table == "Sales" else "Recolte"
                })
                break
        except Exception as e:
            st.error(f"Erreur avec {table}: {str(e)}")

    # 2. Recherche dans la table Logs
    try:
        query_logs = """
        SELECT Offre, Sous_motif, Canal, Direction
        FROM Logs 
        WHERE Hyp = ? AND BP_Logs = ?
        """
        df_logs = pd.read_sql(query_logs, conn, params=[hyp_agent, num_bp])
        
        if not df_logs.empty:
            log_data = df_logs.iloc[0]
            merged_data.update({
                "Offre": log_data.get('Offre', 'N/A'),
                "Canal": log_data.get('Canal', 'N/A'),
                "Direction": log_data.get('Direction', 'N/A'),
                "Sous motif": log_data.get('Sous_motif', 'N/A')
            })
    except Exception as e:
        st.error(f"Erreur lors de la recherche dans les Logs: {str(e)}")

    # Création et affichage du tableau fusionné
    st.markdown("<h3 style='color: #007bad;'> Détails complets</h3>", unsafe_allow_html=True)
  
    # Organisation des données en colonnes logiques
    col1_data = {
        "Référence": merged_data["Référence"],
        "Date commande": merged_data["Date commande"],
        "Agent": merged_data["Agent (Hyp)"],
        "Offre": merged_data["Offre"]
    }
    
    col2_data = {
        "Pays d'opération": merged_data["Pays"],
        "Ville": merged_data["Ville"],
        "Canal": merged_data["Canal"],
        "Direction": merged_data["Direction"]
    }
    
    col3_data = {
        "Montant": merged_data["Montant (€)"],
        "Statut": merged_data["Statut"],
        "Sous motif": merged_data["Sous motif"],
        "Message": merged_data["Message"]
    }

    # Affichage en 3 colonnes pour une meilleure lisibilité
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.table(pd.DataFrame.from_dict(col1_data, orient='index', columns=["Valeur"]))
    
    with col2:
        st.table(pd.DataFrame.from_dict(col2_data, orient='index', columns=["Valeur"]))
    
    with col3:
        st.table(pd.DataFrame.from_dict(col3_data, orient='index', columns=["Valeur"]))

    # Section Évaluation du Coaching
    st.markdown("<h3 style='color: #007bad;'> Détails Coaching : </h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        phase_options = ["Already saled", "Already recolts", "Informations"]
        phase = st.selectbox("Phase", options=phase_options, key="phase_select")
        
        evaluation_options = [
            "Maitrise partielle metier",
            "Maitrise Parfaite metier", 
            "Tutorat demandé",
            "Tutorat suggéré",
            "Erreur Concentration"
        ]
        evaluation = st.selectbox("Évaluation", options=evaluation_options, key="eval_select")
    
    with col2:
        observation = st.text_area("Observation", height=140)
    
    with col3:
        #date_coaching = datetime.now().strftime("%d/%m/%Y %H:%M")
        st.markdown("<h3 style='color: #007bad; border-bottom: none;'>Action Coaching :</h3>", unsafe_allow_html=True)
#
        

# Section Annuler l'évaluation
        if st.button("Annuler l'évaluation", 
                    use_container_width=True,
                    type="primary",
                    key="cancel_eval"):
            
            # Réinitialisation des états (sauf la sélection d'agent)
            for key in list(st.session_state.keys()):
                if key not in ["coaching_agent_select", "selected_agent"]:
                    del st.session_state[key]
            
            st.success("Annulation enregistrée avec succès!")
            st.rerun()  # Rafraîchit l'affichage

        # Section Enregistrement (gardée comme dans votre exemple original)
        if st.button("Enregistrer l'évaluation", 
                    use_container_width=True,
                    type="primary",
                    key="save_eval"):
            st.success("Évaluation enregistrée avec succès!")
            

def afficher_donnees_sales(conn, hyp_agent, df_sales=None):
    """Affiche les données de vente avec possibilité de passer un DataFrame pré-filtré"""
    if df_sales is None:
        df_sales = pd.read_sql(f"""
            SELECT ORDER_DATE, Total_Sale, Rating, Country, City, SHORT_MESSAGE 
            FROM Sales 
            WHERE Hyp = '{hyp_agent}'
            ORDER BY ORDER_DATE DESC
        """, conn)

    if not df_sales.empty:
        # Nettoyage
        df_sales = df_sales.dropna(subset=['City', 'SHORT_MESSAGE', 'Total_Sale', 'Rating'])
        df_sales = df_sales[df_sales['SHORT_MESSAGE'].isin(['ACCEPTED', 'REFUSED'])]

        # 📊 Calcul KPI
        total_ventes = df_sales["Total_Sale"].sum()
        moyenne_vente = df_sales["Total_Sale"].mean()
        moyenne_rating = df_sales["Rating"].mean()

        # 🧾 Affichage KPI
        col1, col2, col3 = st.columns(3)

        
        col1.metric("Ventes Totales", f"€{total_ventes:,.2f}")
        col2.metric("Vente Moyenne", f"€{moyenne_vente:,.2f}")
        col3.metric("Note Moyenne", f"{moyenne_rating:.1f}/5")

        
        st.subheader("Analyse des Ventes")

        # 📊 Organisation des graphiques et du tableau
        col_display1, col_display2 = st.columns([1,2]) # Adjust column width ratio

        with col_display1:
            # 📋 Détail des ventes (Tableau)
            st.subheader("Détail de vos transactions")
            st.dataframe(df_sales)

        with col_display2:
            col_play1, col_play2 = st.columns([2,1])
            with col_play1:
            # Ventes par ville selon le statut (Graphique 1)
                st.subheader("Ventes par Ville")
                df_grouped = (
                    df_sales.groupby(['City', 'SHORT_MESSAGE'])['Total_Sale']
                    .sum()
                    .unstack(fill_value=0)
                    .reset_index()
                )

                fig1 = go.Figure()
                if 'ACCEPTED' in df_grouped.columns:
                    fig1.add_trace(go.Bar(
                        y=df_grouped['City'], # Swapped X and Y
                        x=df_grouped['ACCEPTED'], # Swapped X and Y
                        name='Accepted',
                        marker_color='#007BAD',
                        orientation='h', # Horizontal bars
                        text=df_grouped['ACCEPTED'].apply(lambda x: f'€{x:,.2f}'),
                        textposition='outside'
                    ))
                if 'REFUSED' in df_grouped.columns:
                    fig1.add_trace(go.Bar(
                        y=df_grouped['City'], # Swapped X and Y
                        x=df_grouped['REFUSED'], # Swapped X and Y
                        name='Refused',
                        marker_color='#FF4B4B',
                        orientation='h', # Horizontal bars
                        text=df_grouped['REFUSED'].apply(lambda x: f'€{x:,.2f}'),
                        textposition='outside'
                    ))

                fig1.update_layout(
                    barmode='group',
                    yaxis_title='Ville', # Swapped titles
                    xaxis_title='Montant (€)', # Swapped titles
                    hovermode='y unified', # Adjusted hovermode
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=400,
                    margin=dict(l=20, r=20, t=30, b=20),
                    showlegend=True
                )
                st.plotly_chart(fig1, use_container_width=True)
            with col_play2:

                # Ventes par heure (Graphique 2)
                st.subheader("Ventes par Heure")
                df_sales['Heure'] = pd.to_datetime(df_sales['ORDER_DATE']).dt.hour
                ventes_par_heure = df_sales.groupby('Heure')['Total_Sale'].sum().reset_index()

                fig2 = px.line(
                    ventes_par_heure,
                    x='Heure',
                    y='Total_Sale',
                    labels={'Heure': 'Heure de la journée', 'Total_Sale': 'Montant (€)'},
                    color_discrete_sequence=['#007BAD'],
                    height=400
                )
                st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Aucune donnée de vente trouvée pour cet agent.")


def afficher_donnees_recolts(conn, hyp_agent, df_recolts=None):
    """Affiche les données de récolte avec possibilité de passer un DataFrame pré-filtré"""
    if df_recolts is None:
        df_recolts = pd.read_sql(f"""
            SELECT ORDER_DATE, Total_Recolt, Country, City, SHORT_MESSAGE, Banques
            FROM Recolt
            WHERE Hyp = '{hyp_agent}'
            ORDER BY ORDER_DATE DESC
        """, conn)
    
    if not df_recolts.empty:
        # ... (le reste de la fonction reste inchangé)
        # Calcul KPI
        total_recoltes = df_recolts["Total_Recolt"].sum()
        moyenne_recolte = df_recolts["Total_Recolt"].mean()
        nombre_operations = len(df_recolts)

        # Affichage KPI
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Recolté", f"€{total_recoltes:,.2f}")
        col2.metric("Moyenne par Opération", f"€{moyenne_recolte:,.2f}")
        col3.metric("Nombre d'Opérations", nombre_operations)

        
        st.subheader("Analyse des Récoltes")

        # 📊 Organisation des graphiques et du tableau
        col_display1, col_display2 = st.columns([1.5, 2]) # Adjust column width ratio

        with col_display1:
            # 📋 Détail des opérations (Tableau)
            st.subheader("Détail des opérations")
            st.dataframe(df_recolts)

        with col_display2:
            col_1, col_2 = st.columns([1.5, 2])
            with col_1:
            # 📊 Graphique 1 : Récolts par ville selon le statut
                st.subheader("Récoltes par Ville :")
                df_grouped = (
                    df_recolts.groupby(['City', 'SHORT_MESSAGE'])['Total_Recolt']
                    .sum()
                    .unstack(fill_value=0)
                    .reset_index()
                )

                fig1 = go.Figure()

                if 'ACCEPTED' in df_grouped.columns:
                    fig1.add_trace(go.Bar(
                        y=df_grouped['City'], # Swapped X and Y
                        x=df_grouped['ACCEPTED'], # Swapped X and Y
                        name='Accepted',
                        marker_color='#007BAD',
                        orientation='h', # Horizontal bars
                        text=df_grouped['ACCEPTED'].apply(lambda x: f'€{x:,.2f}'),
                        textposition='outside'
                    ))

                if 'REFUSED' in df_grouped.columns:
                    fig1.add_trace(go.Bar(
                        y=df_grouped['City'], # Swapped X and Y
                        x=df_grouped['REFUSED'], # Swapped X and Y
                        name='Refused',
                        marker_color='#FF4B4B',
                        orientation='h', # Horizontal bars
                        text=df_grouped['REFUSED'].apply(lambda x: f'€{x:,.2f}'),
                        textposition='outside'
                    ))

                fig1.update_layout(
                    barmode='group',
                    yaxis_title='Ville', # Swapped titles
                    xaxis_title='Montant (€)', # Swapped titles
                    hovermode='y unified', # Adjusted hovermode
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=450,
                    margin=dict(l=20, r=20, t=40, b=20),
                    showlegend=True
                )

                st.plotly_chart(fig1, use_container_width=True)
            with col_2:
            # 📊 Graphique 2 : Récolts par banque (bar chart bleu harmonisé)
                st.subheader("Récoltes par Banque")
                df_banques = df_recolts.groupby('Banques')['Total_Recolt'].sum().reset_index()

                fig2 = go.Figure(go.Bar(
                    y=df_banques['Banques'], # Swapped X and Y
                    x=df_banques['Total_Recolt'], # Swapped X and Y
                    marker_color='#00B8A9',
                    orientation='h', # Horizontal bars
                    text=df_banques['Total_Recolt'].apply(lambda x: f'€{x:,.2f}'),
                    textposition='outside'
                ))

                fig2.update_layout(
                    yaxis_title='Banque', # Swapped titles
                    xaxis_title='Montant (€)', # Swapped titles
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=450,
                    margin=dict(l=20, r=20, t=40, b=20)
                )

                st.plotly_chart(fig2, use_container_width=True)

                # 📈 Graphique 3 : Historique des recolts (You can add a time series chart here if desired)
                # Example for a time series chart (you'll need to adapt it to your needs):
                # df_recolts['ORDER_DATE'] = pd.to_datetime(df_recolts['ORDER_DATE'])
                # daily_recolts = df_recolts.groupby(df_recolts['ORDER_DATE'].dt.date)['Total_Recolt'].sum().reset_index()
                # fig3 = px.line(daily_recolts, x='ORDER_DATE', y='Total_Recolt', title='Historique des Récoltes')
                # st.plotly_chart(fig3, use_container_width=True)

    else:
        st.info("Aucune donnée de recolts trouvée pour cet agent.")


def afficher_coaching():
    add_custom_css()
    """Affiche le module de coaching"""
    col1, col2 = st.columns([2, 2])

    with col1:
        st.markdown(
            "<h1 style='text-align: left; color: #002a48; margin-bottom: 0;'>Coachings</h1>",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            "<h1 style='text-align: right; color: #00afe1; margin-bottom: 0;'>Gestion d'Effectifs</h1>",
            unsafe_allow_html=True
        )

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

        # Selection de l'agent et bouton de recherche côte à côte
        col_select, col_button = st.columns([3, 1])
        with col_select:
            selection = st.selectbox("Sélectionner un agent",
                                     df_effectifs["NomComplet"].unique(),
                                     key="coaching_agent_select")
        with col_button:
            st.markdown("<br>", unsafe_allow_html=True) # Add some space for alignment
            search_button = st.button("🔎 Rechercher les transactions")

        if selection and search_button:
            # Récupération des informations de l'agent
            nom, prenom = selection.split(" ", 1)
            agent = df_effectifs[(df_effectifs["NOM"] == nom) &
                                 (df_effectifs["PRENOM"] == prenom)]

            if agent.empty:
                st.error("Agent non trouvé")
                return

            agent = agent.iloc[0]
            hyp_agent = agent["Hyp"]

            # Création d'onglets pour Sales et Recolts
            tab1, tab2 = st.tabs(["Ventes (Sales)", "Recoltes (Recolt)"])

            with tab1:
                afficher_donnees_sales(conn, hyp_agent)

            with tab2:
                afficher_donnees_recolts(conn, hyp_agent)

        
        st.subheader("Liste des Offres")
        
        # This part should be outside the if selection and search_button block
        # to ensure it's always displayed or displayed based on another trigger
        # For now, it's tied to selection for demonstration
        if selection:
            nom, prenom = selection.split(" ", 1)
            agent = df_effectifs[(df_effectifs["NOM"] == nom) &
                                 (df_effectifs["PRENOM"] == prenom)].iloc[0]
            
            query_logs = """
                SELECT DISTINCT l.* FROM Logs l
                LEFT JOIN Sales s ON l.BP_Logs = s.ORDER_REFERENCE
                LEFT JOIN Recolt r ON l.BP_Logs = r.ORDER_REFERENCE
                WHERE l.Hyp = ? 
                AND (s.ORDER_REFERENCE IS NOT NULL OR r.ORDER_REFERENCE IS NOT NULL)
                AND l.Offre <> ''
                ORDER BY l.[Date_d_création] DESC
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