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
from New_Sale_Recolt_Log import *


def agent_dashboard():
    add_custom_css()
    hyp_agent = st.session_state["hyp"]
    conn = get_db_connection()
    
    if not conn:
        st.error("Erreur de connexion à la base de données")
        return

    try:
        # En-tête avec logo et titre
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            st.image('Dental_Implant1.png', width=150)
        with col2:
            st.markdown(
                "<h1 style='color: #002a48; margin-bottom: 0;'>Tableau de Bord Agent</h1>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<h2 style='color: #007bad; margin-top: 0;'>Bienvenue {st.session_state.get('username', 'Agent')}</h2>",
                unsafe_allow_html=True
            )
        with col3:

            df_agent = pd.read_sql(f"SELECT * FROM Effectifs WHERE Hyp = '{hyp_agent}'", conn)
            if not df_agent.empty:
                agent = df_agent.iloc[0]
                date_in = pd.to_datetime(agent["Date_In"])
                anciennete = (pd.Timestamp.now() - date_in).days // 30  # Ancienneté en mois
                st.markdown(
                f"<h2 style='color: #007bad; margin-top: 0;'>Ancienneté par Mois : {anciennete}</h2>",
                unsafe_allow_html=True
            )
                st.markdown(f"""
                    **Nom :** {agent["NOM"]}  
                    **Prénom :** {agent["PRENOM"]}  
                    **Team :** {agent["Team"]}  
                    **Activité :** {agent["Activité"]}  
                
                """)
            else:
                st.warning("Aucune donnée trouvée pour cet agent.")
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
    finally:
        conn.close()





   

    # Menu dans la sidebar
    with st.sidebar:
        
        st.image('Dental_Implant.png', width=350)
        menu_options = ["Accueil", "Mes Performances","Planning","New Sale", "New Récolt", "Logs"]
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=["house", "bar-chart","calendar","calendar","calendar","calendar"],
            default_index=0,
            styles={
                "container": {"background-color": "#002a48"},
                "icon": {"color": "#00afe1", "font-size": "18px"},
                "nav-link": {"color": "#ffffff", "font-size": "16px"},
                "nav-link-selected": {"background-color": "#007bad"}
            }
        )

    # Affichage du contenu selon l'option choisie
    if selected == "Mes Performances":
        afficher_performances_agent()
    if selected == "New Sale":
        New_Sale_Agent()
    if selected == "New Récolt":
        New_Recolt_Agent()
    else:
        st.markdown(
            f"<p style='font-size: 18px;'>Bienvenue sur votre espace personnel, <strong>{st.session_state.get('username', 'Agent')}</strong> !</p>",
            unsafe_allow_html=True
        )




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
           # st.markdown(f"""
           # **Nom :** {agent["NOM"]}  
            #**Prénom :** {agent["PRENOM"]}  
            #**Team :** {agent["Team"]}  
            #**Activité :** {agent["Activité"]}  
            #""")
        
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
    df_sales = pd.read_sql(f"""
        SELECT ORDER_DATE, Total_sale, Rating, Country, City, SHORT_MESSAGE 
        FROM Sales 
        WHERE Hyp = '{hyp_agent}'
        ORDER BY ORDER_DATE DESC
    """, conn)

    if not df_sales.empty:
        # Nettoyage
        df_sales = df_sales.dropna(subset=['City', 'SHORT_MESSAGE', 'Total_sale', 'Rating'])
        df_sales = df_sales[df_sales['SHORT_MESSAGE'].isin(['ACCEPTED', 'REFUSED'])]

        # 📊 Calcul KPI
        total_ventes = df_sales["Total_sale"].sum()
        moyenne_vente = df_sales["Total_sale"].mean()
        moyenne_rating = df_sales["Rating"].mean()

        # 🧾 Affichage KPI
        col1, col2, col3 = st.columns(3)
        col1.metric("Ventes Totales", f"€{total_ventes:,.2f}")
        col2.metric("Vente Moyenne", f"€{moyenne_vente:,.2f}")
        col3.metric("Note Moyenne", f"{moyenne_rating:.1f}/5")

        st.markdown("---")
        st.subheader("Analyse des Ventes")

        # 📊 Organisation des graphiques
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            # Ventes par ville selon le statut
            df_grouped = (
                df_sales.groupby(['City', 'SHORT_MESSAGE'])['Total_sale']
                .sum()
                .unstack(fill_value=0)
                .reset_index()
            )

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

            fig1.update_layout(
                barmode='group',
                xaxis_title='Ville',
                yaxis_title='Montant (€)',
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            # Ventes par heure
            df_sales['Heure'] = pd.to_datetime(df_sales['ORDER_DATE']).dt.hour
            ventes_par_heure = df_sales.groupby('Heure')['Total_sale'].sum().reset_index()

            fig2 = px.line(
                ventes_par_heure,
                x='Heure',
                y='Total_sale',
                labels={'Heure': 'Heure de la journée', 'Total_sale': 'Montant (€)'},
                color_discrete_sequence=['#007BAD'],
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)

        # 📋 Détail des ventes
        st.markdown("---")
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
        # Calcul KPI
        total_recoltes = df_recolts["Total_Recolt"].sum()
        moyenne_recolte = df_recolts["Total_Recolt"].mean()
        nombre_operations = len(df_recolts)

        # Affichage KPI
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Recolté", f"€{total_recoltes:,.2f}")
        col2.metric("Moyenne par Opération", f"€{moyenne_recolte:,.2f}")
        col3.metric("Nombre d'Opérations", nombre_operations)

        st.markdown("---")
        st.subheader("Analyse des Récoltes")

        # 📊 Graphique 1 : Récolts par ville selon le statut (style Ventes)
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("### Récoltes par Ville : Accepted vs Refused")
            df_grouped = (
                df_recolts.groupby(['City', 'SHORT_MESSAGE'])['Total_Recolt']
                .sum()
                .unstack(fill_value=0)
                .reset_index()
            )

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

            fig1.update_layout(
                barmode='group',
                xaxis_title='Ville',
                yaxis_title='Montant (€)',
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                height=450,
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.plotly_chart(fig1, use_container_width=True)

        # 📊 Graphique 2 : Récolts par banque (bar chart bleu harmonisé)
        with col_g2:
            st.markdown("### Récoltes par Banque")
            df_banques = df_recolts.groupby('Banques')['Total_Recolt'].sum().reset_index()

            fig2 = go.Figure(go.Bar(
                x=df_banques['Banques'],
                y=df_banques['Total_Recolt'],
                marker_color='#00B8A9',
                text=df_banques['Total_Recolt'].apply(lambda x: f'€{x:,.2f}'),
                textposition='outside'
            ))

            fig2.update_layout(
                xaxis_title='Banque',
                yaxis_title='Montant (€)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=450,
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.plotly_chart(fig2, use_container_width=True)

        # 📈 Graphique 3 : Historique des recolts
        st.markdown("### Historique des Récoltes")
        fig3 = px.line(
            df_recolts,
            x="ORDER_DATE",
            y="Total_Recolt",
            labels={"ORDER_DATE": "Date", "Total_Recolt": "Montant (€)"},
            color_discrete_sequence=['#007BAD'],
            height=400
        )
        st.plotly_chart(fig3, use_container_width=True)

        # 📋 Détail des opérations
        st.markdown("---")
        st.subheader("Détail des opérations")
        st.dataframe(df_recolts)

    else:
        st.info("Aucune donnée de recolts trouvée pour cet agent.")

