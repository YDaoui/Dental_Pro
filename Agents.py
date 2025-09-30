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
                anciennete = (pd.Timestamp.now() - date_in).days // 30  
                
                
            else:
                st.warning("Aucune donnée trouvée pour cet agent.")
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
    finally:
        conn.close()




   

    
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
      
        st.markdown(
            """
            <h3 style='color: #002a48; font-size: 40px; font-weight: bold;'>Logs</h3>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
    """
    <div style='background-color:#fff3cd; color:#856404; padding:10px 20px; border-left:5px solid #ffeeba; border-radius:5px; margin:10px 0;'>
        ⚠️ Aucun PABX n'a été détecté. Veuillez vous logger ou contacter l'administrateur !
    </div>
    """,
    unsafe_allow_html=True
)

       
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
            st.warning("Aucune logique de connexion active.")

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
        
        # Récup info agent
        df_agent = pd.read_sql(f"SELECT * FROM Effectifs WHERE Hyp = '{hyp_agent}'", conn)
        if not df_agent.empty:
            agent = df_agent.iloc[0]
           # st.markdown(f"""
           # **Nom :** {agent["NOM"]}  
            #**Prénom :** {agent["PRENOM"]}  
            #**Team :** {agent["Team"]}  
            #**Activité :** {agent["Activité"]}  
            #""")
        
       
        tab1, tab2 = st.tabs(["📈   Sales", "💰   Recolts"])
        
        with tab1:
            afficher_donnees_sales(conn, hyp_agent)
            
        with tab2:
            afficher_donnees_recolts(conn, hyp_agent)
            
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
    finally:
        conn.close()
def kpi_card_html(column, title, value_html, color, icon_name):
    """Generates HTML for a custom-styled KPI card."""
    column.markdown(f"""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        <div style="
            padding: 20px;
            background: linear-gradient(145deg, {color} 0%, {color}CC 100%);
            border-radius: 12px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.15);
            height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            border-left: 8px solid {color}EE;
            position: relative;
            overflow: hidden;
            color: white;">
            <div style="position: absolute; right: 20px; top: 20px; opacity: 0.9;">
                <i class="fas fa-{icon_name}" style="font-size: 40px;"></i>
            </div>
            <h3 style="color: white; margin: 0 0 10px 0; font-size: 24px; font-weight: 600;">{title}</h3>
            <p style="font-size: 28px; color: white; font-weight: 700; margin: 0;">{value_html}</p>
        </div>
    """, unsafe_allow_html=True)




def agent_info_card_html(column, title, content_html):
    """Generates HTML for a custom-styled agent info card."""
    column.markdown(f"""
        <div style="
            padding: 20px;
            background: linear-gradient(145deg, #f0f2f6 0%, #e6e9ee 100%);
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            border-left: 6px solid #007bad;
            position: relative;
            overflow: hidden;
            color: #333;">
            <h3 style="color: #007bad; margin: 0 0 10px 0; font-size: 22px; font-weight: 600;">{title}</h3>
            <div style="font-size: 18px; line-height: 1.6;">{content_html}</div>
        </div>
    """, unsafe_allow_html=True)


def display_sales_graphs(df):
    """Affiche les graphiques de ventes sous le formulaire avec des améliorations visuelles"""
    if df.empty:
        st.info("Aucune donnée de vente disponible.")
        return

    st.markdown("---")
    st.markdown("### 📊 Statistiques de Ventes")

    # KPI 
    total_sales = df["Total_Sale"].sum()
    avg_sale = df["Total_Sale"].mean()
    avg_rating = df["Rating"].mean()

    col1, col2, col3 = st.columns(3)
    kpi_card_html(col1, "Total Ventes", f"{total_sales:,.2f}€", "#007bad", "money-bill-wave")
    kpi_card_html(col2, "Moyenne/vente", f"{avg_sale:,.2f}€", "#00afe1", "chart-line")
    kpi_card_html(col3, "Note moyenne", f"{avg_rating:.1f}/9", "#ffc107", "star")

    
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Ventes par Ville**")
        df_city = df.groupby('City')['Total_Sale'].sum().reset_index()
        fig_city = px.bar(df_city, x='Total_Sale', y='City', orientation='h', color='City',
                          text='Total_Sale', # Add text labels
                          title='Ventes par Ville')
        fig_city.update_traces(texttemplate='%{text:,.2f} €', textposition='ouside')
        fig_city.update_layout(uniformtext_minsize=10, uniformtext_mode='hide', yaxis={'categoryorder':'total ascending'}, showlegend=False) # Removed legend
        st.plotly_chart(fig_city, use_container_width=True)

    with col2:
        st.markdown("**Évolution des ventes**")
        try:
            df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'])
            df_date = df.groupby(df['ORDER_DATE'].dt.date)['Total_Sale'].sum().reset_index()
            fig_date = px.line(df_date, x='ORDER_DATE', y='Total_Sale',
                               title='Évolution des ventes au fil du temps')
            fig_date.update_xaxes(title_text='Date')
            fig_date.update_yaxes(title_text='Total Ventes (€)')
            # Add data labels for line chart
            fig_date.update_traces(mode='lines+markers+text', text=df_date['Total_Sale'].apply(lambda x: f'{x:,.2f}€'), textposition='top center')
            fig_date.update_layout(showlegend=False) # Removed legend
            st.plotly_chart(fig_date, use_container_width=True)
        except Exception:
            st.warning("Données de date indisponibles pour l'évolution des ventes.")

def display_recolt_graphs(df):
    """Affiche les graphiques de récoltes sous le formulaire avec des améliorations visuelles"""
    if df.empty:
        st.info("Aucune donnée de récolte disponible.")
        return

    st.markdown("---")
    st.markdown("### 📊 Statistiques de Récoltes")

   
    total_recolt = df["Total_Recolt"].sum()
    avg_recolt = df["Total_Recolt"].mean()
    avg_rating = df["Rating"].mean() 

    col1, col2, col3 = st.columns(3)
    kpi_card_html(col1, "Total Récolté", f"{total_recolt:,.2f} €", "#043a64", "leaf")
    kpi_card_html(col2, "Moyenne/récolte", f"{avg_recolt:,.2f} €", "#17a2b8", "seedling")
    kpi_card_html(col3, "Satisfaction", f"{avg_rating:.1f}/9", "#ffc107", "smile")


    # Graphs
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Récoltes par Ville**")
        df_city = df.groupby('City')['Total_Recolt'].sum().reset_index()
        fig_city = px.bar(df_city, x='Total_Recolt', y='City', orientation='h', color='City',
                          text='Total_Recolt',
                          title='Récoltes par Ville')
        fig_city.update_traces(texttemplate='%{text:,.2f}€', textposition='inside')
        fig_city.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', yaxis={'categoryorder':'total ascending'}, showlegend=False) # Removed legend
        st.plotly_chart(fig_city, use_container_width=True)

    with col2:
        st.markdown("**Récoltes par Banque**")
      
        if 'Banques' in df.columns:
            df_bank = df.groupby('Banques')['Total_Recolt'].sum().reset_index()
            fig_bank = px.bar(df_bank, x='Total_Recolt', y='Banques', orientation='h', color='Banques',
                              text='Total_Recolt', # Add text labels
                              title='Récoltes par Banque')
            fig_bank.update_traces(texttemplate='%{text:,.2f}€', textposition='inside')
            fig_bank.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', yaxis={'categoryorder':'total ascending'}, showlegend=False) # Removed legend
            st.plotly_chart(fig_bank, use_container_width=True)
        else:
            st.warning("La colonne 'Banques' n'est pas disponible pour afficher les récoltes par banque. Assurez-vous qu'elle est présente dans vos données de récolte.")
         
            st.markdown("**Évolution des récoltes (Fallback)**")
            try:
                df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'])
                df_date = df.groupby(df['ORDER_DATE'].dt.date)['Total_Recolt'].sum().reset_index()
                fig_date = px.line(df_date, x='ORDER_DATE', y='Total_Recolt',
                                   title='Évolution des récoltes au fil du temps')
                fig_date.update_xaxes(title_text='Date')
                fig_date.update_yaxes(title_text='Total Récoltes (€)')
                fig_date.update_traces(mode='lines+markers+text', text=df_date['Total_Recolt'].apply(lambda x: f'{x:,.2f}€'), textposition='top center')
                fig_date.update_layout(showlegend=False) # Removed legend
                st.plotly_chart(fig_date, use_container_width=True)
            except Exception:
                st.warning("Données de date indisponibles pour l'évolution des récoltes.")

    st.markdown("---")
    st.markdown("### Évolution Générale des Récoltes")
    try:
        df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'])
        df_date_overall = df.groupby(df['ORDER_DATE'].dt.date)['Total_Recolt'].sum().reset_index()
        fig_recolt_line_overall = px.line(df_date_overall, x='ORDER_DATE', y='Total_Recolt',
                               title='Évolution Générale des Récoltes au fil du temps')
        fig_recolt_line_overall.update_xaxes(title_text='Date')
        fig_recolt_line_overall.update_yaxes(title_text='Total Récoltes (€)')
        fig_recolt_line_overall.update_traces(mode='lines+markers+text', text=df_date_overall['Total_Recolt'].apply(lambda x: f'{x:,.2f}€'), textposition='top center')
        fig_recolt_line_overall.update_layout(showlegend=False) # Removed legend
        st.plotly_chart(fig_recolt_line_overall, use_container_width=True)
    except Exception:
        st.warning("Données de date indisponibles pour l'évolution générale des récoltes.")


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
        kpi_card_html(col1, "Ventes Totales", f"{total_ventes:,.2f} €", "#007bad", "money-bill-wave")
        kpi_card_html(col2, "Vente Moyenne", f"{moyenne_vente:,.2f} €", "#00afe1", "chart-line")
        kpi_card_html(col3, "Note Moyenne", f"{moyenne_rating:.1f}/5", "#ffc107", "star")

        st.markdown("## Analyse des Ventes")
        st.markdown("---")

        
        col_g1, col_g2 = st.columns(2)

        with col_g1:
    
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
                        text=[f"<b>{v:,.0f} €</b>" for v in df_grouped[status]],
                        textposition='outside',
                        textfont=dict(size=14, color="black")
                    ))

            fig1.update_layout(
                barmode='stack',
                xaxis_title='Montant (€)',
                yaxis_title='Ville',
                title='💼 Ventes par Ville',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='white',
                font=dict(family="Arial", size=14),
                margin=dict(l=50, r=50, t=50, b=50),
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
           
            df_sales['Heure'] = pd.to_datetime(df_sales['ORDER_DATE']).dt.hour
            ventes_par_heure = df_sales.groupby('Heure')['Total_Sale'].sum().reset_index()

            fig2 = px.bar(
                ventes_par_heure,
                x='Heure',
                y='Total_Sale',
                text='Total_Sale',
                labels={'Heure': 'Heure (0-23)', 'Total_Sale': 'Montant (€)'},
                color_discrete_sequence=['#00afe1']
            )
            fig2.update_traces(
                texttemplate='<b>€%{text:.0f}</b>',
                textposition='inside',
                textfont_size=14
            )
            fig2.update_layout(
                title="🕒 Ventes par Heure",
                xaxis=dict(dtick=1),
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='white',
                font=dict(family="Arial", size=14),
                margin=dict(l=40, r=40, t=50, b=40),
                showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True)

       
        st.markdown("---")
        col_g3, col_g4 = st.columns(2)

        with col_g3:
           
            try:
                df_sales['ORDER_DATE'] = pd.to_datetime(df_sales['ORDER_DATE'])
                df_date = df_sales.groupby(df_sales['ORDER_DATE'].dt.date)['Total_Sale'].sum().reset_index()
                
                fig3 = px.line(
                    df_date, 
                    x='ORDER_DATE', 
                    y='Total_Sale',
                    title='📈 Évolution des Ventes',
                    labels={'ORDER_DATE': 'Date', 'Total_Sale': 'Montant (€)'}
                )
                fig3.update_traces(
                    mode='lines+markers',
                    line=dict(color='#007bad', width=3),
                    marker=dict(size=8, color='#007bad'),
                    text=df_date['Total_Sale'].apply(lambda x: f'{x:,.0f} €'),
                    textposition='top center'
                )
                fig3.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='white',
                    font=dict(family="Arial", size=14),
                    showlegend=False
                )
                st.plotly_chart(fig3, use_container_width=True)
            except Exception as e:
                st.warning(f"Impossible d'afficher l'évolution temporelle: {str(e)}")

        with col_g4:
            
            df_rating = df_sales.groupby('City')['Rating'].mean().reset_index()
            df_rating = df_rating.sort_values('Rating', ascending=False)
            
            fig4 = px.bar(
                df_rating,
                x='City',
                y='Rating',
                text='Rating',
                title='⭐ Notes Moyennes par Ville',
                color_discrete_sequence=['#ffc107']
            )
            fig4.update_traces(
                texttemplate='<b>%{text:.1f}</b>',
                textposition='inside',
                textfont_size=16
            )
            fig4.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='white',
                font=dict(family="Arial", size=14),
                xaxis_title='Ville',
                yaxis_title='Note moyenne',
                yaxis_range=[0, 5],  
                showlegend=False
            )
            st.plotly_chart(fig4, use_container_width=True)

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

       
        total_recoltes = df_recolts["Total_Recolt"].sum()
        moyenne_recolte = df_recolts["Total_Recolt"].mean()
        nombre_operations = len(df_recolts)

        col1, col2, col3 = st.columns(3)
        kpi_card_html(col1, "Total Récolté", f"{total_recoltes:,.2f} €", "#28a745", "leaf")
        kpi_card_html(col2, "Moyenne par Opération", f"{moyenne_recolte:,.2f} €", "#17a2b8", "seedling")
        kpi_card_html(col3, "Nombre d'opérations", str(nombre_operations), "#ffc107", "tasks")

        st.markdown("---")
        st.subheader("Analyse des Récoltes")

      
        colg1, colg2 ,colg3= st.columns(3)

        with colg1:
        
            df_grouped = (
                df_recolts.groupby(['City', 'SHORT_MESSAGE'])['Total_Recolt']
                .sum()
                .unstack(fill_value=0)
                .reset_index()
            )
            df_grouped['Total'] = df_grouped.get('ACCEPTED', 0) + df_grouped.get('REFUSED', 0)
            df_grouped = df_grouped.sort_values(by='Total', ascending=False)

            fig1 = go.Figure()
            for status, color in zip(['ACCEPTED', 'REFUSED'], ['#28a745', '#dc3545']):
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
                title='🌍 Récoltes par Ville',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='white',
                font=dict(family="Arial", size=14),
                margin=dict(l=50, r=50, t=50, b=50),
                height=500,
                showlegend=False
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
                labels={'Heure': 'Heure (0-23)', 'Total_Recolt': 'Montant (€)'},
                color_discrete_sequence=['#17a2b8']
            )
            fig2.update_traces(
                texttemplate='<b>€%{text:.0f}</b>',
                textposition='inside',
                textfont_size=14
            )
            fig2.update_layout(
                title="🕒 Récoltes par Heure",
                xaxis=dict(dtick=1),
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='white',
                font=dict(family="Arial", size=14),
                margin=dict(l=40, r=40, t=50, b=40),
                showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True)
            if 'Banques' in df_recolts.columns:
                    df_banque = df_recolts.groupby('Banques')['Total_Recolt'].sum().reset_index()
                    df_banque = df_banque.sort_values('Total_Recolt', ascending=False)
                    
                    fig4 = px.bar(
                        df_banque,
                        x='Banques',
                        y='Total_Recolt',
                        text='Total_Recolt',
                        title='🏦 Récoltes par Banque',
                        color_discrete_sequence=['#007bad']
                    )
                    fig4.update_traces(
                        texttemplate='<b>€%{text:.0f}</b>',
                        textposition='outside',
                        textfont_size=14
                    )
                    fig4.update_layout(
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='white',
                        font=dict(family="Arial", size=14),
                        xaxis_title='Banque',
                        yaxis_title='Montant (€)',
                        showlegend=False
                    )
                    st.plotly_chart(fig4, use_container_width=True)

            with colg3:
          
                try:
                    df_recolts['ORDER_DATE'] = pd.to_datetime(df_recolts['ORDER_DATE'])
                    df_date = df_recolts.groupby(df_recolts['ORDER_DATE'].dt.date)['Total_Recolt'].sum().reset_index()
                    
                    fig3 = px.line(
                        df_date, 
                        x='ORDER_DATE', 
                        y='Total_Recolt',
                        title='📈 Évolution des Récoltes',
                        labels={'ORDER_DATE': 'Date', 'Total_Recolt': 'Montant (€)'}
                    )
                    fig3.update_traces(
                        mode='lines+markers',
                        line=dict(color='#28a745', width=3),
                        marker=dict(size=8, color='#28a745'),
                        text=df_date['Total_Recolt'].apply(lambda x: f'€{x:,.0f}'),
                        textposition='top center'
                    )
                    fig3.update_layout(
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='white',
                        font=dict(family="Arial", size=14),
                        showlegend=False
                    )
                    st.plotly_chart(fig3, use_container_width=True)
                except Exception as e:
                    st.warning(f"Impossible d'afficher l'évolution temporelle: {str(e)}")
                st.markdown("---")
                st.subheader("📋 Détail des Récoltes")
                st.dataframe(df_recolts)
           
             
                
                

        

    else:
        st.info("Aucune donnée de récolte trouvée pour cet agent.")
