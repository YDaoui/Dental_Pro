import streamlit as st
import pandas as pd

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
                
                
            else:
                st.warning("Aucune donnée trouvée pour cet agent.")
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
    finally:
        conn.close()





   

    # Menu dans la sidebar
    with st.sidebar:
        
        st.image('Dental_Implant.png', width=350)
        menu_options = ["Accueil", "Mes Performances","New Sale", "New Récolt", "Logs"]
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=["house", "bar-chart","calendar","calendar","calendar"],
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
    if selected== "Logs":
        login_Logs()
    else:
        return
def login_Logs():
    """Affiche la page des logs avec les champs d'entrée."""
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        # "Logs" title: Blue, larger, and bold
        st.markdown(
            """
            <h3 style='color: #002a48; font-size: 40px; font-weight: bold;'>Logs</h3>
            """,
            unsafe_allow_html=True
        )
        # Date and time: Light blue, larger, and bold
        st.markdown(
            f"""
            <p style='color: #007bad; font-size: 30px; font-weight: bold;'>Date et heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            """,
            unsafe_allow_html=True
        )

    with col2:
        username = st.text_input("ID Logs ")
        password = st.text_input("Mot de passe", type="password")

    with col3:
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        if st.button("**Se connecter**", key="login_button", use_container_width=True):
            st.info("Bouton 'Se connecter' cliqué (aucgit statusune logique de connexion active).")

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        if st.button("**Annuler**", key="Annuler_button", use_container_width=True):
            st.rerun()

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    login_Logs()


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
        SELECT ORDER_DATE, Total_Sale, Rating, Country, City, SHORT_MESSAGE 
        FROM Sales 
        WHERE Hyp = '{hyp_agent}'
        ORDER BY ORDER_DATE DESC
    """, conn)

    if not df_sales.empty:
        df_sales = df_sales.dropna(subset=['City', 'SHORT_MESSAGE', 'Total_Sale', 'Rating'])
        df_sales = df_sales[df_sales['SHORT_MESSAGE'].isin(['ACCEPTED', 'REFUSED'])]

        total_ventes = df_sales["Total_Sale"].sum()
        moyenne_vente = df_sales["Total_Sale"].mean()
        moyenne_rating = df_sales["Rating"].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Ventes Totales", f"€{total_ventes:,.2f}")
        col2.metric("📊 Vente Moyenne", f"€{moyenne_vente:,.2f}")
        col3.metric("⭐ Note Moyenne", f"{moyenne_rating:.1f}/5")

        st.markdown("## 🎯 Analyse des Ventes")
        st.markdown("---")

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            # Regrouper et trier les ventes par ville
            df_grouped = (
                df_sales.groupby(['City', 'SHORT_MESSAGE'])['Total_Sale']
                .sum()
                .unstack(fill_value=0)
                .reset_index()
            )
            df_grouped['Total'] = df_grouped.get('ACCEPTED', 0) + df_grouped.get('REFUSED', 0)
            df_grouped = df_grouped.sort_values(by='Total', ascending=False)

            fig1 = go.Figure()
            for status, color in zip(['ACCEPTED', 'REFUSED'], ['#007BAD', '#FF4B4B']):
                if status in df_grouped.columns:
                    fig1.add_trace(go.Bar(
                        y=df_grouped['City'],
                        x=df_grouped[status],
                        name=status,
                        orientation='h',
                        marker=dict(color=color),
                        text=[f"<b>€{v:,.0f}</b>" for v in df_grouped[status]],
                        textposition='outside',
                        textfont=dict(size=14, color="black")
                    ))

            fig1.update_layout(
                barmode='stack',
                xaxis_title='Montant (€)',
                yaxis_title='Ville',
                title='💼 Ventes par Ville et Statut',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='white',
                font=dict(family="Arial", size=14),
                margin=dict(l=50, r=50, t=50, b=50),
                height=500
            )

            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            # Ventes par heure
            df_sales['Heure'] = pd.to_datetime(df_sales['ORDER_DATE']).dt.hour
            ventes_par_heure = df_sales.groupby('Heure')['Total_Sale'].sum().reset_index()

            fig2 = px.bar(
                ventes_par_heure,
                x='Heure',
                y='Total_Sale',
                text='Total_Sale',
                labels={'Heure': 'Heure (0-23)', 'Total_Sale': 'Montant (€)'},
                color_discrete_sequence=['#007BAD']
            )
            fig2.update_traces(
                texttemplate='<b>€%{text:.0f}</b>',
                textposition='outside',
                textfont_size=14
            )
            fig2.update_layout(
                title="🕒 Ventes par Heure",
                xaxis=dict(dtick=1),
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='white',
                font=dict(family="Arial", size=14),
                margin=dict(l=40, r=40, t=50, b=40)
            )

            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("📋 Détail des Transactions")
        st.dataframe(df_sales)

    else:
        st.info("Aucune donnée de vente trouvée pour cet agent.")


def afficher_donnees_recolts(conn, hyp_agent):
    df_recolts = pd.read_sql(f"""
        SELECT ORDER_DATE, Total_Recolt, Country, City, SHORT_MESSAGE, Banques
        FROM Recolt
        WHERE Hyp = '{hyp_agent}'
        ORDER BY ORDER_DATE DESC
    """, conn)
    
    if not df_recolts.empty:
        df_recolts = df_recolts.dropna(subset=['City', 'SHORT_MESSAGE', 'Total_Recolt'])
        df_recolts = df_recolts[df_recolts['SHORT_MESSAGE'].isin(['ACCEPTED', 'REFUSED'])]

        # KPIs
        total_recoltes = df_recolts["Total_Recolt"].sum()
        moyenne_recolte = df_recolts["Total_Recolt"].mean()
        nombre_operations = len(df_recolts)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Récolté", f"€{total_recoltes:,.2f}")
        col2.metric("Moyenne par Opération", f"€{moyenne_recolte:,.2f}")
        col3.metric("Nombre d'opérations", nombre_operations)

        st.markdown("---")
        st.subheader("Analyse des Récoltes")

        colg1, colg2 = st.columns(2)

        with colg1:
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
                    name='Acceptée',
                    marker_color='#28a745',
                    text=df_grouped['ACCEPTED'].apply(lambda x: f"€{x:,.0f}"),
                    textposition='outside',
                    textfont=dict(size=14, color='black', family='Arial Black')
                ))
            if 'REFUSED' in df_grouped.columns:
                fig1.add_trace(go.Bar(
                    x=df_grouped['City'],
                    y=df_grouped['REFUSED'],
                    name='Refusée',
                    marker_color='#dc3545',
                    text=df_grouped['REFUSED'].apply(lambda x: f"€{x:,.0f}"),
                    textposition='outside',
                    textfont=dict(size=14, color='black', family='Arial Black')
                ))

            fig1.update_layout(
                barmode='group',
                xaxis_title='Ville',
                yaxis_title='Montant (€)',
                title='Récoltes par Ville',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                margin=dict(t=40, b=40, l=20, r=20)
            )
            st.plotly_chart(fig1, use_container_width=True)

        with colg2:
            df_recolts['Heure'] = pd.to_datetime(df_recolts['ORDER_DATE']).dt.hour
            recoltes_par_heure = df_recolts.groupby('Heure')['Total_Recolt'].sum().reset_index()

            fig2 = px.bar(
                recoltes_par_heure,
                x='Heure',
                y='Total_Recolt',
                text='Total_Recolt',
                labels={'Heure': 'Heure de la journée', 'Total_Recolt': 'Montant (€)'},
                color_discrete_sequence=['#007bad']
            )
            fig2.update_traces(
                texttemplate='%{text:.0f}€',
                textposition='outside',
                textfont=dict(size=14, family='Arial Black')
            )
            fig2.update_layout(
                title='Récoltes par Heure',
                xaxis=dict(title='Heure'),
                yaxis=dict(title='Montant (€)'),
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                margin=dict(t=40, b=40, l=20, r=20)
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("Détail de vos Récoltes")
        st.dataframe(df_recolts)

    else:
        st.info("Aucune donnée de récolte trouvée pour cet agent.")
