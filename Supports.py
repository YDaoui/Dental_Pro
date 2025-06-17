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
        st.image('Dental_Implant1.png', width=150)
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

    # Ajouter une colonne de sélection
    df_logs['Sélection'] = False
    edited_df = st.data_editor(
        df_logs,
        column_config={
            "Sélection": st.column_config.CheckboxColumn(
                "Sélectionner",
                help="Sélectionnez une ligne pour voir les détails",
                default=False,
            )
        },
        disabled=df_logs.columns.drop('Sélection').tolist(),
        hide_index=True,
        use_container_width=True
    )

    # Vérifier si une ligne a été sélectionnée
    selected_rows = edited_df[edited_df['Sélection']]
    
    if not selected_rows.empty:
        selected_row = selected_rows.iloc[0].to_dict()
        num_bp = selected_row.get('BP_Logs')
        hyp_agent = selected_row.get('Hyp', 'N/A')
        
        # Stocker le numéro BP dans session_state pour utilisation ultérieure
        st.session_state.selected_bp = num_bp
        st.session_state.selected_hyp = hyp_agent
        
        if num_bp:
            # Afficher directement les informations sans bouton supplémentaire
            search_additional_info(conn, num_bp, hyp_agent)
        else:
            st.warning("Identifiant client non disponible")
    else:
        st.info("Veuillez sélectionner une ligne dans le tableau pour voir les détails.")

def display_offer_details(selected_row, conn):
    """Affiche les détails d'une offre sélectionnée"""
   
    if not isinstance(selected_row, dict):
        try:
            selected_row = dict(selected_row)
        except Exception as e:
            st.error(f"Erreur de conversion: {str(e)}")
            return

    
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

   
    num_bp = selected_row.get('BP_Logs')
    hyp_agent = selected_row.get('Hyp', 'N/A')
    
    with col3:
        st.markdown(f"**Numéro BP:** {num_bp if num_bp else 'N/A'}")
        st.markdown(f"**Agent (Hyp):** {hyp_agent}")

 
    if num_bp:
        if st.button("Rechercher des informations complémentaires", 
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
        # Récupération du nom de l'agent
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

    # En-tête avec style
    st.markdown(
    f"""
    <div style='background-color:#002a48; padding:15px; border-radius:10px; margin-bottom:20px;'>
        <h3 style='color:white; margin:0;'>
            Coaching - BP: <span style='color:#00afe1;'>{int(num_bp)}</span> 
            (Agent: <span style='color:#00afe1;'>{agent_name}</span>)
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)

    
    # Initialisation des données fusionnées
    merged_data = {
        "Référence": num_bp,
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

    # Recherche dans les tables Sales et Recolt
    for table in ["Sales", "Recolt"]:
        try:
            query = f"""
            SELECT ORDER_REFERENCE, ORDER_DATE, SHORT_MESSAGE, Country, City, 
                   {'Total_Sale' if table == 'Sales' else 'Total_Recolt'} AS Montant 
            FROM {table} 
            WHERE ORDER_REFERENCE = ?
            ORDER BY ORDER_DATE DESC
            LIMIT 1
            """
            df = pd.read_sql(query, conn, params=[num_bp])
            
            if not df.empty:
                found_data = df.iloc[0]
                merged_data.update({
                    "Référence": found_data.get('ORDER_REFERENCE', 'N/A'),
                    "Date commande": found_data.get('ORDER_DATE', 'N/A'),
                    "Pays": found_data.get('Country', 'N/A'),
                    "Ville": found_data.get('City', 'N/A'),
                    "Montant (€)": f"{found_data.get('Montant', 0):,.2f} €",
                    "Message": found_data.get('SHORT_MESSAGE', 'N/A'),
                    "Statut": "Vente" if table == "Sales" else "Recolte"
                })
                break
        except Exception as e:
            st.error(f"Erreur avec {table}: {str(e)}")

    # Recherche dans les logs
    try:
        query_logs = """
        SELECT Offre, Sous_motif, Canal, Direction, Date_d_création
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
                "Sous motif": log_data.get('Sous_motif', 'N/A'),
                "Date création": log_data.get('Date_d_création', 'N/A')
            })
    except Exception as e:
        st.error(f"Erreur lors de la recherche dans les Logs: {str(e)}")

    # Affichage des détails en colonnes
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Informations générales**")
        st.markdown(f"- **Référence:** **{merged_data['Référence']}**")
        st.markdown(f"- **Date création:** **{merged_data.get('Date création', 'N/A')}**")
        st.markdown(f"- **Date commande:** **{merged_data['Date commande']}**")
        st.markdown(f"- **Agent:** **{merged_data['Agent (Hyp)']}**")
        st.markdown(f"- **Offre:** **{merged_data['Offre']}**")

    with col2:
        st.markdown("**Détails opérationnels**")
        st.markdown(f"- **Pays:** **{merged_data['Pays']}**")
        st.markdown(f"- **Ville:** **{merged_data['Ville']}**")
        st.markdown(f"- **Canal:** **{merged_data['Canal']}**")
        st.markdown(f"- **Direction:** **{merged_data['Direction']}**")
        st.markdown(f"- **Montant:** **{merged_data['Montant (€)']}**")


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
        observation = st.text_area("Observation", height=150)
    
    with col3:
        #date_coaching = datetime.now().strftime("%d/%m/%Y %H:%M")
        st.markdown("<h3 style='color: #007bad; border-bottom: none;'>Action Coaching :</h3>", unsafe_allow_html=True)
#
        st.markdown("""
                    <style>
                        div.stButton > button {
                            width: 100%;
                            background-color: #fcce22;
                            color: white;
                            border-radius: 5px;
                            border: none;
                            padding: 10px;
                            font-size: 1.1em;
                        }
                        div.stButton > button:hover {
                            background-color: #fcce22;
                        }
                    </style>
                    """, unsafe_allow_html=True)

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

        # 🧾 Affichage KPI avec style harmonisé
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
            <div style="
                padding: 20px;
                background: linear-gradient(145deg, #007BAD 0%, #007BADCC 100%);
                border-radius: 12px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.15);
                height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border-left: 8px solid #007BADEE;
                position: relative;
                overflow: hidden;
                color: white;">
                <div style="position: absolute; right: 20px; top: 20px; opacity: 0.9;">
                    <i class="fas fa-euro-sign" style="font-size: 40px;"></i>
                </div>
                <h3 style="color: white; margin: 0 0 10px 0; font-size: 24px; font-weight: 600;">Ventes Totales</h3>
                <p style="font-size: 28px; color: white; font-weight: 700; margin: 0;">{total_ventes:,.2f} €</p>
            </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
            <div style="
                padding: 20px;
                background: linear-gradient(145deg, #2596be 0%, #2596beCC 100%);
                border-radius: 12px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.15);
                height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border-left: 8px solid #2596beEE;
                position: relative;
                overflow: hidden;
                color: white;">
                <div style="position: absolute; right: 20px; top: 20px; opacity: 0.9;">
                    <i class="fas fa-chart-line" style="font-size: 40px;"></i>
                </div>
                <h3 style="color: white; margin: 0 0 10px 0; font-size: 24px; font-weight: 600;">Vente Moyenne</h3>
                <p style="font-size: 28px; color: white; font-weight: 700; margin: 0;">{moyenne_vente:,.2f} €</p>
            </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
            <div style="
                padding: 20px;
                background: linear-gradient(145deg, #fc9307 0%, #fc9307CC 100%);
                border-radius: 12px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.15);
                height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border-left: 8px solid #fc9307EE;
                position: relative;
                overflow: hidden;
                color: white;">
                <div style="position: absolute; right: 20px; top: 20px; opacity: 0.9;">
                    <i class="fas fa-star" style="font-size: 40px;"></i>
                </div>
                <h3 style="color: white; margin: 0 0 10px 0; font-size: 24px; font-weight: 600;">Note Moyenne</h3>
                <p style="font-size: 28px; color: white; font-weight: 700; margin: 0;">{moyenne_rating:.1f}/5</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='color: #007bad;'>Analyse des Ventes</h3>", unsafe_allow_html=True)

       
        col_display1, col_display2 = st.columns([1,2])

        with col_display1:
           
            st.markdown("<h4 style='color: #007bad;'>Détail de vos transactions</h4>", unsafe_allow_html=True)
            st.dataframe(df_sales)

        with col_display2:
            col_play1, col_play2 = st.columns([2,1])
            with col_play1:
                
                st.markdown("<h4 style='color: #007bad;'>Ventes par Ville</h4>", unsafe_allow_html=True)
                df_grouped = (
                    df_sales.groupby(['City', 'SHORT_MESSAGE'])['Total_Sale']
                    .sum()
                    .unstack(fill_value=0)
                    .reset_index()
                )

                fig1 = go.Figure()
                if 'ACCEPTED' in df_grouped.columns:
                    fig1.add_trace(go.Bar(
                        y=df_grouped['City'],
                        x=df_grouped['ACCEPTED'],
                        name='Accepted',
                        marker_color='#007BAD',
                        orientation='h',
                        text=df_grouped['ACCEPTED'].apply(lambda x: f'€{x:,.2f}'),
                        textposition='outside',
                        textfont=dict(size=12, family='Arial', color='black', weight='bold'),
                        marker=dict(line=dict(width=1, color='#333333')) # Contour des barres
                    ))
                if 'REFUSED' in df_grouped.columns:
                    fig1.add_trace(go.Bar(
                        y=df_grouped['City'],
                        x=df_grouped['REFUSED'],
                        name='Refused',
                        marker_color='#fc9307',
                        orientation='h',
                        text=df_grouped['REFUSED'].apply(lambda x: f'{x:,.2f} €'),
                        textposition='outside',
                        textfont=dict(size=12, family='Arial', color='black', weight='bold'),
                        marker=dict(line=dict(width=1, color='#333333')) # Contour des barres
                    ))

                fig1.update_layout(
                    barmode='group',
                    yaxis_title={
                        'text': 'Ville',
                        'font': {'size': 16, 'color': 'black', 'family': 'Arial', 'weight': 'bold'}
                    },
                    xaxis_title={
                        'text': 'Montant (€)',
                        'font': {'size': 16, 'color': 'black', 'family': 'Arial', 'weight': 'bold'}
                    },
                    hovermode='y unified',
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=400,
                    margin=dict(l=20, r=20, t=50, b=20), # Augmentation du top margin pour le titre du graphique
                    showlegend=False, 
                    font=dict(family='Arial', size=14, color='black'),
                    xaxis=dict(
                        tickfont=dict(size=12, family='Arial', color='black', weight='bold'),
                        gridcolor='#f0f0f0'
                    ),
                    yaxis=dict(
                        tickfont=dict(size=12, family='Arial', color='black', weight='bold')
                    ),
                    bargap=0.01, 
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=14,
                        font_family="Arial"
                    )
                )
                st.plotly_chart(fig1, use_container_width=True)

            with col_play2:
                # Ventes par heure (Graphique 2) - Style harmonisé
                st.markdown("<h4 style='color: #007bad;'>Ventes par Heure</h4>", unsafe_allow_html=True)
                df_sales['Heure'] = pd.to_datetime(df_sales['ORDER_DATE']).dt.hour
                ventes_par_heure = df_sales.groupby('Heure')['Total_Sale'].sum().reset_index()

                fig2 = px.line(
                    ventes_par_heure,
                    x='Heure',
                    y='Total_Sale',
                    labels={'Heure': 'Heure de la journée', 'Total_Sale': 'Montant (€)'},
                    color_discrete_sequence=['#525CEB'], # Couleur harmonisée pour les lignes
                    height=400
                )

                fig2.update_traces(
                    line=dict(width=4, color='#525CEB'), # Couleur de ligne harmonisée
                    mode='lines+markers+text', # Ajout de texte et marqueurs
                    marker=dict(size=10, color='#3D3B40', line=dict(width=1, color='#FFFFFF')), # Marqueurs harmonisés
                    text=[f"€{y:,.0f}" for y in ventes_par_heure['Total_Sale']], # Affichage des valeurs
                    textposition="top center",
                    textfont=dict(color="#F70F49", size=14, family='Arial', weight='bold'), # Style de texte harmonisé
                    hovertemplate='Heure: %{x}<br>Ventes: €%{y:,.2f}<extra></extra>', # Hovertemplate
                    fill='tozeroy', # Remplissage sous la ligne
                    fillcolor='rgba(179, 191, 231, 0.4)' # Couleur de remplissage
                )

                fig2.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family='Arial', size=14, color='black'),
                    xaxis=dict(
                        tickfont=dict(size=12, family='Arial', color='black', weight='bold'),
                        gridcolor='#f0f0f0'
                    ),
                    yaxis=dict(
                        tickfont=dict(size=12, family='Arial', color='black', weight='bold'),
                        gridcolor='#f0f0f0',
                        range=[0, ventes_par_heure['Total_Sale'].max() * 1.2] # Ajustement de la plage Y
                    ),
                    margin=dict(l=20, r=20, t=50, b=20) # Augmentation du top margin pour le titre du graphique
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
        # Nettoyage
        df_recolts = df_recolts.dropna(subset=['City', 'SHORT_MESSAGE', 'Total_Recolt', 'Banques'])

        # Calcul KPI
        total_recoltes = df_recolts["Total_Recolt"].sum()
        moyenne_recolte = df_recolts["Total_Recolt"].mean()
        nombre_operations = len(df_recolts)

        # Affichage KPI avec style harmonisé
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
            <div style="
                padding: 20px;
                background: linear-gradient(145deg, #007BAD 0%, #007BADCC 100%);
                border-radius: 12px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.15);
                height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border-left: 8px solid #007BADEE;
                position: relative;
                overflow: hidden;
                color: white;">
                <div style="position: absolute; right: 20px; top: 20px; opacity: 0.9;">
                    <i class="fas fa-hand-holding-usd" style="font-size: 40px;"></i>
                </div>
                <h3 style="color: white; margin: 0 0 10px 0; font-size: 24px; font-weight: 600;">Total Récolté</h3>
                <p style="font-size: 28px; color: white; font-weight: 700; margin: 0;">{total_recoltes:,.2f} €</p>
            </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
            <div style="
                padding: 20px;
                background: linear-gradient(145deg, #2596be 0%, #2596beCC 100%);
                border-radius: 12px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.15);
                height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border-left: 8px solid #2596beEE;
                position: relative;
                overflow: hidden;
                color: white;">
                <div style="position: absolute; right: 20px; top: 20px; opacity: 0.9;">
                    <i class="fas fa-calculator" style="font-size: 40px;"></i>
                </div>
                <h3 style="color: white; margin: 0 0 10px 0; font-size: 24px; font-weight: 600;">Moyenne par Opération</h3>
                <p style="font-size: 28px; color: white; font-weight: 700; margin: 0;">{moyenne_recolte:,.2f} €</p>
            </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
            <div style="
                padding: 20px;
                background: linear-gradient(145deg, #fc9307 0%, #fc9307CC 100%);
                border-radius: 12px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.15);
                height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border-left: 8px solid #fc9307EE;
                position: relative;
                overflow: hidden;
                color: white;">
                <div style="position: absolute; right: 20px; top: 20px; opacity: 0.9;">
                    <i class="fas fa-list-ol" style="font-size: 40px;"></i>
                </div>
                <h3 style="color: white; margin: 0 0 10px 0; font-size: 24px; font-weight: 600;">Nombre d'Opérations</h3>
                <p style="font-size: 28px; color: white; font-weight: 700; margin: 0;">{nombre_operations}</p>
            </div>
        """, unsafe_allow_html=True)


        st.markdown("<h3 style='color: #007bad;'>Analyse des Récoltes</h3>", unsafe_allow_html=True)

        # 📊 Organisation des graphiques et du tableau
        col_display1, col_display2 = st.columns([1, 2])

        with col_display1:
            # 📋 Détail des opérations (Tableau)
            st.markdown("<h4 style='color: #007bad;'>Détail des opérations</h4>", unsafe_allow_html=True)
            st.dataframe(df_recolts)

        with col_display2:
            col_1, col_2 = st.columns([1.5, 2])
            with col_1:
                # 📊 Graphique 1 : Récolts par ville selon le statut - Style harmonisé
                st.markdown("<h4 style='color: #007bad;'>Récoltes par Ville :</h4>", unsafe_allow_html=True)
                df_grouped = (
                    df_recolts.groupby(['City', 'SHORT_MESSAGE'])['Total_Recolt']
                    .sum()
                    .unstack(fill_value=0)
                    .reset_index()
                )

                fig1 = go.Figure()

                if 'ACCEPTED' in df_grouped.columns:
                    fig1.add_trace(go.Bar(
                        y=df_grouped['City'],
                        x=df_grouped['ACCEPTED'],
                        name='Accepted',
                        marker_color='#007BAD',
                        orientation='h',
                        text=df_grouped['ACCEPTED'].apply(lambda x: f'€{x:,.2f}'),
                        textposition='outside',
                        textfont=dict(size=12, family='Arial', color='black', weight='bold'),
                        marker=dict(line=dict(width=1, color='#333333'))
                    ))

                if 'REFUSED' in df_grouped.columns:
                    fig1.add_trace(go.Bar(
                        y=df_grouped['City'],
                        x=df_grouped['REFUSED'],
                        name='Refused',
                        marker_color='#fc9307',
                        orientation='h',
                        text=df_grouped['REFUSED'].apply(lambda x: f'€{x:,.2f}'),
                        textposition='outside',
                        textfont=dict(size=12, family='Arial', color='black', weight='bold'),
                        marker=dict(line=dict(width=1, color='#333333'))
                    ))

                fig1.update_layout(
                    barmode='group',
                    yaxis_title={
                        'text': 'Ville',
                        'font': {'size': 16, 'color': 'black', 'family': 'Arial', 'weight': 'bold'}
                    },
                    xaxis_title={
                        'text': 'Montant (€)',
                        'font': {'size': 16, 'color': 'black', 'family': 'Arial', 'weight': 'bold'}
                    },
                    hovermode='y unified',
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=450,
                    margin=dict(l=20, r=20, t=50, b=20),
                    showlegend=False, # Cache la légende
                    font=dict(family='Arial', size=14, color='black'),
                    xaxis=dict(
                        tickfont=dict(size=12, family='Arial', color='black', weight='bold'),
                        gridcolor='#f0f0f0'
                    ),
                    yaxis=dict(
                        tickfont=dict(size=12, family='Arial', color='black', weight='bold')
                    ),
                    bargap=0.1, # Augmentation de la largeur des barres (moins d'espace entre elles)
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=14,
                        font_family="Arial"
                    )
                )

                st.plotly_chart(fig1, use_container_width=True)

            with col_2:
                # 📊 Graphique 2 : Récolts par banque - Style harmonisé
                st.markdown("<h4 style='color: #007bad;'>Récoltes par Banque</h4>", unsafe_allow_html=True)
                df_banques = df_recolts.groupby('Banques')['Total_Recolt'].sum().reset_index()

                fig2 = go.Figure(go.Bar(
                    y=df_banques['Banques'],
                    x=df_banques['Total_Recolt'],
                    marker_color='#2596be',
                    orientation='h',
                    text=df_banques['Total_Recolt'].apply(lambda x: f'€{x:,.2f}'),
                    textposition='outside',
                    textfont=dict(size=12, family='Arial', color='black', weight='bold'),
                    marker=dict(line=dict(width=1, color='#333333'))
                ))

                fig2.update_layout(
                    yaxis_title={
                        'text': 'Banque',
                        'font': {'size': 16, 'color': 'black', 'family': 'Arial', 'weight': 'bold'}
                    },
                    xaxis_title={
                        'text': 'Montant (€)',
                        'font': {'size': 16, 'color': 'black', 'family': 'Arial', 'weight': 'bold'}
                    },
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=450,
                    margin=dict(l=20, r=20, t=50, b=20),
                    font=dict(family='Arial', size=14, color='black'),
                    xaxis=dict(
                        tickfont=dict(size=12, family='Arial', color='black', weight='bold'),
                        gridcolor='#f0f0f0'
                    ),
                    yaxis=dict(
                        tickfont=dict(size=12, family='Arial', color='black', weight='bold')
                    ),
                    bargap=0.3,
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=14,
                        font_family="Arial"
                    )
                )

                st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Aucune donnée de recolts trouvée pour cet agent.")

def afficher_coaching():
    st.markdown("""
    <style>
    /* Onglets inactifs - maintenant en bleu */
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #00afe1;  /* Fond bleu */
        color: white;              /* Texte blanc */
        border-radius: 5px 5px 0 0;
        padding: 10px 15px;
        margin-right: 5px;
        border: 1px solid #00afe1;
        border-bottom: none;
        font-weight: bold;
        transition: all 0.2s ease-in-out;
    }
    
    /* Effet de survol - bleu légèrement plus foncé */
    .stTabs [data-baseweb="tab-list"] button:hover {
        background-color: #00afe1;
    }
    
    /* Onglet actif - maintenant en blanc */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: white;    /* Fond blanc */
        color: #00afe1;            /* Texte bleu */
        border-color: #00afe1;
        border-bottom: 1px solid white; /* Cache la bordure du bas */
    }
    
    /* Style du conteneur principal */
    .stTabs {
        margin-top: -10px;
        margin-bottom: 15px;
    }
    
    /* Ligne sous les onglets */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid #00afe1;
    }

    /* Définir l'arrière-plan de la barre latérale en blanc */
    section[data-testid="stSidebar"] {
        background-color: white !important;
    }

    /* Style pour le compteur dans la barre latérale */
    div[data-testid="stSidebar"] .stNumberInput > div > div > input {
        color: #007bad !important; /* Couleur du texte du compteur */
        font-weight: bold; /* Optionnel: pour rendre le texte plus visible */
    }
    div[data-testid="stSidebar"] .stSlider > div > div > div > div {
        color: #007bad !important; /* Couleur du texte du slider si utilisé comme compteur */
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)
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
            search_button = st.button("**Rechercher les transactions**")

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

        
        st.markdown("---")
        st.subheader("Liste des Offres")
        
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