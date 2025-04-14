import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px
from datetime import datetime
from streamlit_option_menu import option_menu
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from contextlib import closing
import plotly.graph_objects as go  
from PIL import Image
from Utils_Dental import *
from Supports import *
from Managers import *
from Utils_Dental import *




def agent_dashboard():
    # En-tête avec logo et titre
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image('Dental_Implant1.png', width=150)
    with col2:
        st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Tableau de Bord Agent</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: #007bad; margin-top: 0;'>Bienvenue {st.session_state.get('username', 'Agent')}</h2>", 
                   unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Menu sidebar
    with st.sidebar:
        st.image('Dental_Implant.png', width=350)
        menu_options = ["Accueil", "Mes Performances"]
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=["house", "bar-chart"],
            default_index=0,
            
            styles={
                "container": {"background-color": "#002a48"},
                "icon": {"color": "#00afe1", "font-size": "18px"},  
                "nav-link": {"color": "#ffffff", "font-size": "16px"},
                "nav-link-selected": {"background-color": "#007bad"}
            }
        )
    
    # Contenu principal
    if selected == "Mes Performances":
        afficher_performances_agent()

    else:
        st.write(f"Bienvenue {st.session_state.get('username', 'Agent')}")

def afficher_performances_agent():
    conn = get_db_connection()
    if not conn:
        st.error("Erreur de connexion à la base de données")
        return
    
    try:
        hyp_agent = st.session_state["hyp"]
        
        # Récupérer les informations de l'agent
        df_agent = pd.read_sql(f"SELECT * FROM Effectifs WHERE Hyp = '{hyp_agent}'", conn)
        if not df_agent.empty:
            agent = df_agent.iloc[0]
            st.markdown(f"""
            **Nom :** {agent["NOM"]}  
            **Prénom :** {agent["PRENOM"]}  
            **Team :** {agent["Team"]}  
            **Activité :** {agent["Activité"]}  
            """)
        
        # Création des onglets
        tab1, tab2 = st.tabs(["📈   Sales", "💰   Recolts"])
        
        with tab1:
            afficher_donnees_sales(conn, hyp_agent)
            
        with tab2:
            afficher_donnees_recolts(conn, hyp_agent)
            
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
    finally:
        conn.close()


def afficher_donnees_sales(conn, hyp_agent):
    # Chargement des données depuis la base
    df_sales = pd.read_sql(f"""
        SELECT ORDER_DATE, Total_sale, Rating, Country, City, SHORT_MESSAGE 
        FROM Sales 
        WHERE Hyp = '{hyp_agent}'
        ORDER BY ORDER_DATE DESC
    """, conn)

    if not df_sales.empty:
        # Nettoyage : suppression des lignes incomplètes
        df_sales = df_sales.dropna(subset=['City', 'SHORT_MESSAGE', 'Total_sale', 'Rating'])

        # Filtrage précis pour inclure uniquement les statuts ACCEPTED et REFUSED
        df_sales = df_sales[df_sales['SHORT_MESSAGE'].isin(['ACCEPTED', 'REFUSED'])]

        # 🔢 Calcul des KPI
        total_ventes = df_sales["Total_sale"].sum()
        moyenne_vente = df_sales["Total_sale"].mean()
        moyenne_rating = df_sales["Rating"].mean()

        # 🧾 Affichage des KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("Ventes Totales", f"€{total_ventes:,.2f}")
        col2.metric("Vente Moyenne", f"€{moyenne_vente:,.2f}")
        col3.metric("Note Moyenne", f"{moyenne_rating:.1f}/5")

        st.markdown("---")
        st.subheader("Analyse des Ventes par Ville")

        col1, col2, col3 = st.columns(3)

        # ➤ Total des ventes par ville
        with col1:
            ventes_par_ville = df_sales.groupby('City')['Total_sale'].sum().reset_index()
            st.dataframe(ventes_par_ville.sort_values('Total_sale', ascending=False))

        # ➤ Répartition des statuts de commande
        with col2:
            statuts = df_sales['SHORT_MESSAGE'].value_counts().reset_index()
            statuts.columns = ['Statut', 'Nombre']
            st.dataframe(statuts)

        # ➤ Note moyenne par ville
        with col3:
            note_par_ville = df_sales.groupby('City')['Rating'].mean().reset_index()
            st.dataframe(note_par_ville.sort_values('Rating', ascending=False))

        # 📊 Graphique 1 : Ventes par ville selon le statut
        st.markdown("### Ventes par Ville : Accepted vs Refused")
        
        # Préparation des données
        df_grouped = (
            df_sales.groupby(['City', 'SHORT_MESSAGE'])['Total_sale']
            .sum()
            .unstack(fill_value=0)
            .reset_index()
        )
        
        # Création du graphique à barres groupées
        fig1 = go.Figure()
        
        if 'ACCEPTED' in df_grouped.columns:
            fig1.add_trace(go.Bar(
                x=df_grouped['City'],
                y=df_grouped['ACCEPTED'],
                name='Accepted',
                marker_color='#007BAD',
                text=df_grouped['ACCEPTED'].apply(lambda x: f'€{x:,.2f}'),
                textposition='outside'
            ))

        if 'REFUSED' in df_grouped.columns:
            fig1.add_trace(go.Bar(
                x=df_grouped['City'],
                y=df_grouped['REFUSED'],
                name='Refused',
                marker_color='#FF4B4B',
                text=df_grouped['REFUSED'].apply(lambda x: f'€{x:,.2f}'),
                textposition='outside'
            ))
        
        # Mise en forme
        fig1.update_layout(
            barmode='group',
            xaxis_title='Ville',
            yaxis_title='Montant (€)',
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig1, use_container_width=True)

        # 📈 Graphique 2 : Ventes par heure
        st.markdown("### Ventes par Heure")

        df_sales['Heure'] = pd.to_datetime(df_sales['ORDER_DATE']).dt.hour
        ventes_par_heure = df_sales.groupby('Heure')['Total_sale'].sum().reset_index()

        fig2 = px.line(
            ventes_par_heure,
            x='Heure',
            y='Total_sale',
            labels={'Heure': 'Heure de la journée', 'Total_sale': 'Montant (€)'},
            title="Somme des ventes par heure",
            color_discrete_sequence=['#007BAD']
        )
        st.plotly_chart(fig2, use_container_width=True)

        # 📋 Détail des transactions
        st.subheader("Détail de vos transactions")
        st.dataframe(df_sales)

    else:
        st.info("Aucune donnée de vente trouvée pour cet agent.")




def afficher_donnees_recolts(conn, hyp_agent):
    df_recolts = pd.read_sql(f"""
        SELECT ORDER_DATE, Total_Recolt, Country, City, SHORT_MESSAGE, Banques
        FROM Recolts 
        WHERE Hyp = '{hyp_agent}'
        ORDER BY ORDER_DATE DESC
    """, conn)
    
    if not df_recolts.empty:
        # Calculer les métriques
        total_recoltes = df_recolts["Total_Recolt"].sum()
        moyenne_recolte = df_recolts["Total_Recolt"].mean()
        nombre_operations = len(df_recolts)
        
        # Afficher les KPI
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Recolté", f"€{total_recoltes:,.2f}")
        col2.metric("Moyenne par Opération", f"€{moyenne_recolte:,.2f}")
        col3.metric("Nombre d'Opérations", nombre_operations)
        
        # Section avec 3 colonnes
        st.markdown("---")
        st.subheader("Analyse des Recolts")
        
        # Colonne 1: Total des recolts par ville
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Par Ville")
            recolts_par_ville = df_recolts.groupby('City')['Total_Recolt'].sum().reset_index()
            st.dataframe(recolts_par_ville.sort_values('Total_Recolt', ascending=False))
        
        # Colonne 2: Par Banque
        with col2:
            st.subheader("Par Banque")
            recolts_par_banque = df_recolts.groupby('Banques')['Total_Recolt'].sum().reset_index()
            st.dataframe(recolts_par_banque.sort_values('Total_Recolt', ascending=False))
        
        # Colonne 3: Par Statut
        with col3:
            st.subheader("Par Statut")
            statuts = df_recolts['SHORT_MESSAGE'].value_counts().reset_index()
            statuts.columns = ['Statut', 'Nombre']
            st.dataframe(statuts)
        
        # Graphique 1: Recolts par ville avec statut
        fig1 = px.bar(df_recolts, 
                     x='City', 
                     y='Total_Recolt', 
                     color='SHORT_MESSAGE',
                     title='Recolts par Ville (Accepté/Refusé)',
                     labels={'City': 'Ville', 'Total_Recolt': 'Montant (€)', 'SHORT_MESSAGE': 'Statut'},
                     barmode='group')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Graphique 2: Recolts par banque
        fig2 = px.bar(df_recolts.groupby('Banques')['Total_Recolt'].sum().reset_index(),
                     x='Banques',
                     y='Total_Recolt',
                     title='Recolts par Banque',
                     labels={'Banques': 'Banque', 'Total_Recolt': 'Montant (€)'})
        st.plotly_chart(fig2, use_container_width=True)
        
        # Graphique 3: Historique des recolts
        fig3 = px.line(df_recolts, 
                      x="ORDER_DATE", 
                      y="Total_Recolt", 
                      title="Historique des recolts",
                      labels={"ORDER_DATE": "Date", "Total_Recolt": "Montant (€)"})
        st.plotly_chart(fig3, use_container_width=True)
        
        # Détail des opérations
        st.subheader("Détail des opérations")
        st.dataframe(df_recolts)
    else:
        st.info("Aucune donnée de recolts trouvée pour cet agent")