import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from Utils_Dental import add_custom_css, get_db_connection, load_data

def display_sales_graphs(df):
    """Affiche les graphiques de ventes sous le formulaire"""
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
    col1.metric("Total Ventes", f"{total_sales:,.2f}€")
    col2.metric("Moyenne/vente", f"{avg_sale:,.2f}€")
    col3.metric("Note moyenne", f"{avg_rating:.1f}/9")
    
    # Graphiques
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Ventes par Ville**")
        df_city = df.groupby('City')['Total_Sale'].sum().reset_index()
        fig = px.bar(df_city, x='City', y='Total_Sale', color='City')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Évolution des ventes**")
        try:
            df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'])
            df_date = df.groupby(df['ORDER_DATE'].dt.date)['Total_Sale'].sum().reset_index()
            fig = px.line(df_date, x='ORDER_DATE', y='Total_Sale')
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.warning("Données de date indisponibles")

def display_recolt_graphs(df):
    """Affiche les graphiques de récoltes sous le formulaire"""
    if df.empty:
        st.info("Aucune donnée de récolte disponible.")
        return
    
    st.markdown("---")
    st.markdown("### 📊 Statistiques de Récoltes")
    
    # KPI
    total_recolt = df["Total_Recolt"].sum()
    avg_recolt = df["Total_Recolt"].mean()
    avg_rating = df["Rating"].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Récolté", f"{total_recolt:,.2f}€")
    col2.metric("Moyenne/récolte", f"{avg_recolt:,.2f}€")
    col3.metric("Satisfaction", f"{avg_rating:.1f}/9")
    
    # Graphiques
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Récoltes par Ville**")
        df_city = df.groupby('City')['Total_Recolt'].sum().reset_index()
        fig = px.bar(df_city, x='City', y='Total_Recolt', color='City')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Évolution des récoltes**")
        try:
            df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'])
            df_date = df.groupby(df['ORDER_DATE'].dt.date)['Total_Recolt'].sum().reset_index()
            fig = px.line(df_date, x='ORDER_DATE', y='Total_Recolt')
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.warning("Données de date indisponibles")

def New_Sale_Agent():
    add_custom_css()
    hyp_agent = st.session_state.get("hyp", None)
    
    # Charger les données existantes
    sales_df, _, _, _ = load_data()
    agent_sales = sales_df[sales_df['Hyp'] == hyp_agent] if hyp_agent else pd.DataFrame()

    conn = get_db_connection()
    st.markdown("---")
    
    st.markdown(
        f"<h2 style='color: #007bad;text-align: left;'>Nouvelle Vente au nom de : {st.session_state.get('username', 'Agent')}</h2>",
        unsafe_allow_html=True
    )
   
    try:
        # Formulaire de vente
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            st.markdown("### Numéro du BP")
            order_reference = st.text_input("Order Reference", key="sale_ref")
            order_date = st.date_input("Order Date", value=datetime.today(), key="sale_date")
            country = st.selectbox("Country", ["Autriche", "France"], key="sale_country")
            cities = ["Vienne", "Graz", "Linz", "Salzbourg"] if country == "Autriche" else ["Paris", "Lyon", "Marseille", "Toulouse"]
            city = st.selectbox("City", cities, key="sale_city")

        with col2:
            st.markdown("### Montant (€)")
            short_message = st.selectbox("Short Message", ["Accepted", "Refused", "Error"], key="sale_status")
            
            montant_col1, montant_col2 = st.columns([2, 1])
            with montant_col1:
                montant_input = st.number_input("Saisir le montant", min_value=0.0, step=5.0, format="%.2f", key="sale_amount")
            with montant_col2:
                montant_slider = st.slider("ou avec le slider", min_value=0, max_value=1000, step=5, key="sale_slider")
            
            rating = st.slider("Rating", min_value=1, max_value=9, key="sale_rating")

        valider, annuler = st.columns(2)
        with valider:
            if st.button("✅ Valider", key="validate_sale"):
                total_sale = montant_input if montant_input > 0 else montant_slider
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """INSERT INTO Sales (Hyp, ORDER_REFERENCE, ORDER_DATE, SHORT_MESSAGE, Country, City, Total_Sale, Rating)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (hyp_agent, order_reference, order_date, short_message, country, city, total_sale, rating)
                    )
                    conn.commit()
                    st.success("Vente enregistrée avec succès!")
                    st.cache_data.clear()  # Force le rechargement des données
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")
        
        with annuler:
            if st.button("❌ Annuler", key="cancel_sale"):
                st.warning("Opération annulée")

        # Afficher les graphiques après le formulaire
        display_sales_graphs(agent_sales)

    except Exception as e:
        st.error(f"Erreur: {e}")
    finally:
        if conn:
            conn.close()

def New_Recolt_Agent():
    add_custom_css()
    hyp_agent = st.session_state.get("hyp", None)
    
    # Charger les données existantes
    _, recolts_df, _, _ = load_data()
    agent_recolts = recolts_df[recolts_df['Hyp'] == hyp_agent] if hyp_agent else pd.DataFrame()

    conn = get_db_connection()
    st.markdown("---")
    st.markdown(
        f"<h2 style='color: #007bad;text-align: left;'>Nouvelle Récolte au nom de : {st.session_state.get('username', 'Agent')}</h2>",
        unsafe_allow_html=True
    )
    
    try:
        # Formulaire de récolte
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            st.markdown("### Numéro du BP")
            order_reference = st.text_input("Order Reference", key="recolt_ref")
            order_date = st.date_input("Order Date", value=datetime.today(), key="recolt_date")
            country = st.selectbox("Country", ["Autriche", "France"], key="recolt_country")
            cities = ["Vienne", "Graz", "Linz", "Salzbourg"] if country == "Autriche" else ["Paris", "Lyon", "Marseille", "Toulouse"]
            city = st.selectbox("City", cities, key="recolt_city")

        with col2:
            st.markdown("### Montant (€)")
            short_message = st.selectbox("Short Message", ["Accepted", "Refused", "Error"], key="recolt_status")
            
            montant_col1, montant_col2 = st.columns([2, 1])
            with montant_col1:
                montant_input = st.number_input("Saisir le montant", min_value=0.0, step=5.0, format="%.2f", key="recolt_amount")
            with montant_col2:
                montant_slider = st.slider("ou avec le slider", min_value=0, max_value=1000, step=5, key="recolt_slider")
            
            rating = st.slider("Rating", min_value=1, max_value=9, key="recolt_rating")

        valider, annuler = st.columns(2)
        with valider:
            if st.button("✅ Valider", key="validate_recolt"):
                total_recolt = montant_input if montant_input > 0 else montant_slider
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """INSERT INTO Recolt (Hyp, ORDER_REFERENCE, ORDER_DATE, SHORT_MESSAGE, Country, City, Total_Recolt, Rating)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (hyp_agent, order_reference, order_date, short_message, country, city, total_recolt, rating)
                    )
                    conn.commit()
                    st.success("Récolte enregistrée avec succès!")
                    st.cache_data.clear()  # Force le rechargement des données
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")
        
        with annuler:
            if st.button("❌ Annuler", key="cancel_recolt"):
                st.warning("Opération annulée")

        # Afficher les graphiques après le formulaire
        display_recolt_graphs(agent_recolts)

    except Exception as e:
        st.error(f"Erreur: {e}")
    finally:
        if conn:
            conn.close()