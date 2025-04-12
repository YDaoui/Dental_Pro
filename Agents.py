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
        
        # Récupérer les performances
        df_sales = pd.read_sql(f"""
            SELECT ORDER_DATE, Total_sale, Rating, Country, City 
            FROM Sales 
            WHERE Hyp = '{hyp_agent}'
            ORDER BY ORDER_DATE DESC
        """, conn)
        
        if not df_sales.empty:
            # Calculer les métriques
            total_ventes = df_sales["Total_sale"].sum()
            moyenne_vente = df_sales["Total_sale"].mean()
            moyenne_rating = df_sales["Rating"].mean()
            
            # Afficher les KPI
            col1, col2, col3 = st.columns(3)
            col1.metric("Ventes Totales", f"€{total_ventes:,.2f}")
            col2.metric("Vente Moyenne", f"€{moyenne_vente:,.2f}")
            col3.metric("Note Moyenne", f"{moyenne_rating:.1f}/5")
            
            # Graphique des ventes par date
            fig = px.line(df_sales, x="ORDER_DATE", y="Total_sale", 
                          title="Historique de vos ventes",
                          labels={"ORDER_DATE": "Date", "Total_sale": "Montant (€)"})
            st.plotly_chart(fig, use_container_width=True)
            
            # Détail des transactions
            st.subheader("Détail de vos transactions")
            st.dataframe(df_sales)
        else:
            st.info("Aucune donnée de vente trouvée pour cet agent")
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
    finally:
        conn.close()