import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from Utils_Dental import add_custom_css, get_db_connection, load_data

# Helper function for KPI card HTML
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

def display_sales_graphs(df):
    """Affiche les graphiques de ventes sous le formulaire avec des améliorations visuelles"""
    if df.empty:
        st.info("Aucune donnée de vente disponible.")
        return
    
    st.markdown(
        f"<h2 style='color: #007bad;text-align: left;'>Statistique de Vente : {st.session_state.get('username', )}</h2>",
        unsafe_allow_html=True
    )

    # KPI Cards
    total_sales = df["Total_Sale"].sum()
    avg_sale = df["Total_Sale"].mean()
    avg_rating = df["Rating"].mean()

    col1, col2, col3 = st.columns(3)
    kpi_card_html(col1, "Total Ventes", f"{total_sales:,.2f}€", "#007bad", "money-bill-wave")
    kpi_card_html(col2, "Moyenne/vente", f"{avg_sale:,.2f}€", "#00afe1", "chart-line")
    kpi_card_html(col3, "Note moyenne", f"{avg_rating:.1f}/9", "#ffc107", "smile")

    # Graphs
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Ventes par Ville**")
        df_city = df.groupby('City')['Total_Sale'].sum().reset_index()
        fig_city = px.bar(df_city, 
                        x='Total_Sale', 
                        y='City', 
                        orientation='h', 
                        color='City',
                        text='Total_Sale'  # Étiquettes de données
                        )
        
        # Formatage des étiquettes
        fig_city.update_traces(
            texttemplate='%{text:,.2f} €',  # Format monétaire
            textposition='outside',        # Position extérieure
            textfont_size=20              # Taille de police
        )
        
        # Ajustement du layout
        fig_city.update_layout(
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),  # Ajuster les marges si nécessaire
            height=500                           # Hauteur fixe pour mieux voir
        )
        
        st.plotly_chart(fig_city, use_container_width=True)

    with col2:
        st.markdown("**Évolution des ventes**")
        try:
            df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'])
            df_date = df.groupby(df['ORDER_DATE'].dt.date)['Total_Sale'].sum().reset_index()
            fig_date = px.line(df_date, x='ORDER_DATE', y='Total_Sale'
                              )
            fig_date.update_xaxes(title_text='Date')
            fig_date.update_yaxes(title_text='Total Ventes (€)')
            # Add data labels for line chart
            fig_date.update_traces(mode='lines+markers+text', text=df_date['Total_Sale'].apply(lambda x: f'{x:,.2f}€'), textposition='top center')
            fig_date.update_layout(showlegend=False)  # Removed legend
            st.plotly_chart(fig_date, use_container_width=True)
        except Exception:
            st.warning("Données de date indisponibles pour l'évolution des ventes.")

def display_recolt_graphs(df):
    """Affiche les graphiques de récoltes sous le formulaire avec des améliorations visuelles"""
    if df.empty:
        st.info("Aucune donnée de récolte disponible.")
        return

    st.markdown(
        f"<h2 style='color: #007bad;text-align: left;'>Statistiques de Récoltes : {st.session_state.get('username', 'Agent')}</h2>",
        unsafe_allow_html=True
    )

    # KPI Cards
    total_recolt = df["Total_Recolt"].sum()
    avg_recolt = df["Total_Recolt"].mean()
    avg_rating = df["Rating"].mean()

    col1, col2, col3 = st.columns(3)
    kpi_card_html(col1, "Total Récolté", f"{total_recolt:,.2f}€", "#043a64", "leaf")  # Green for harvest
    kpi_card_html(col2, "Moyenne/récolte", f"{avg_recolt:,.2f}€", "#17a2b8", "seedling")
    kpi_card_html(col3, "Satisfaction", f"{avg_rating:.1f}/9", "#ffc107", "smile")

    # Graphs
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Récoltes par Ville**")
        df_city = df.groupby('City')['Total_Recolt'].sum().reset_index()
        fig_city = px.bar(
            df_city,
            x='Total_Recolt',
            y='City',
            orientation='h',
            color='City',
            text='Total_Recolt'  # Étiquettes de données
        )
        
        # Personnalisation des étiquettes
        fig_city.update_traces(
            texttemplate='%{text:,.2f} €',  # Format monétaire
            textposition='outside',        # Étiquettes à l'extérieur des barres
            textfont_size=16,             # Taille de police
            insidetextanchor='middle'      # Alignement si étiquettes trop longues
        )
        
        # Optimisation du layout
        fig_city.update_layout(
            uniformtext_minsize=16,
            uniformtext_mode='hide',
            yaxis={'categoryorder': 'total ascending'},  # Tri des villes par récolte
            showlegend=False,                            # Pas de légende
            margin=dict(l=20, r=20, t=40, b=20),        # Marges ajustées
            height=800,                                 # Hauteur fixe
            xaxis_title="Montant des récoltes (€)",    # Titre axe X
            yaxis_title="Ville"                         # Titre axe Y
        )
        
        st.plotly_chart(fig_city, use_container_width=True)

    with col2:
        st.markdown("**Récoltes par Banque**")
        # Ensure 'Banques' column exists before trying to group
        if 'Banques' in df.columns:
            df_bank = df.groupby('Banques')['Total_Recolt'].sum().reset_index()
            fig_bank = px.bar(df_bank, x='Total_Recolt', y='Banques', orientation='h', color='Banques',
                              text='Total_Recolt'  # Add text labels
                              )
            fig_bank.update_traces(texttemplate='%{text:,.2f}€', textposition='outside')
            fig_bank.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', yaxis={'categoryorder': 'total ascending'}, showlegend=False)  # Removed legend
            st.plotly_chart(fig_bank, use_container_width=True)
        else:
            st.warning("La colonne 'Banques' n'est pas disponible pour afficher les récoltes par banque. Assurez-vous qu'elle est présente dans vos données de récolte.")
            # Fallback to Evolution des récoltes if Bank column is not found
            st.markdown("**Évolution des récoltes (Fallback)**")
            try:
                df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'])
                df_date = df.groupby(df['ORDER_DATE'].dt.date)['Total_Recolt'].sum().reset_index()
                fig_date = px.line(df_date, x='ORDER_DATE', y='Total_Recolt',
                                  title='Évolution des récoltes au fil du temps')
                fig_date.update_xaxes(title_text='Date')
                fig_date.update_yaxes(title_text='Total Récoltes (€)')
                fig_date.update_traces(mode='lines+markers+text', text=df_date['Total_Recolt'].apply(lambda x: f'{x:,.2f}€'), textposition='top center')
                fig_date.update_layout(showlegend=False)  # Removed legend
                st.plotly_chart(fig_date, use_container_width=True)
            except Exception:
                st.warning("Données de date indisponibles pour l'évolution des récoltes.")

    # New: Evolution des récoltes as a separate full-width graph at the bottom
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
        fig_recolt_line_overall.update_layout(showlegend=False)  # Removed legend
        st.plotly_chart(fig_recolt_line_overall, use_container_width=True)
    except Exception:
        st.warning("Données de date indisponibles pour l'évolution générale des récoltes.")

def get_unique_values_from_table(table_name, column_name):
    """Récupère les valeurs uniques d'une colonne spécifique d'une table"""
    conn = get_db_connection()
    try:
        # Handle cases where column_name contains a WHERE clause
        if "WHERE" in column_name:
            # Split the column name and WHERE condition
            parts = column_name.split("WHERE")
            column = parts[0].strip()
            condition = parts[1].strip()
            query = f"SELECT DISTINCT {column} FROM {table_name} WHERE {condition}"
        else:
            query = f"SELECT DISTINCT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL"
        
        df = pd.read_sql(query, conn)
        return df[column_name.split("WHERE")[0].strip()].tolist()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
        return []
    finally:
        if conn:
            conn.close()

def clear_form():
    """Vide tous les champs du formulaire"""
    keys_to_clear = [key for key in st.session_state.keys() 
                    if key.startswith('sale_') or key.startswith('recolt_')]
    for key in keys_to_clear:
        del st.session_state[key]

def New_Sale_Agent():
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
     
    col1, col2 = st.columns([2, 2])

    with col1:
        st.markdown(
            "<h1 style='text-align: left; color: #002a48; margin-bottom: 0;'>Vente</h1>",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            "<h1 style='text-align: right; color: #00afe1; margin-bottom: 0;'>Nouvelle Vente</h1>",
            unsafe_allow_html=True
        )

    hyp_agent = st.session_state.get("hyp", None)

    # Charger les données existantes
    sales_df, _, _, _ = load_data()
    agent_sales = sales_df[sales_df['Hyp'] == hyp_agent] if hyp_agent else pd.DataFrame()

    conn = get_db_connection()

    st.markdown(
        f"<h2 style='color: #007bad;text-align: left;'>Nouvelle Vente au nom de : {st.session_state.get('username', 'Agent')}</h2>",
        unsafe_allow_html=True
    )

    try:
        # Récupérer les valeurs uniques depuis la table Sales
        countries = get_unique_values_from_table('Sales', 'Country')
        cities = get_unique_values_from_table('Sales', 'City')

        # Formulaire de vente
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            st.markdown("### Numéro du BP")
            order_reference = st.text_input("Order Reference", key="sale_ref")
            order_date = st.date_input("Order Date", value=datetime.today(), key="sale_date")
            country = st.selectbox("Country", countries, key="sale_country")
            
            # Filtrer les villes en fonction du pays sélectionné
            selected_country = st.session_state.get('sale_country', None)
            if selected_country:
                cities_in_country = get_unique_values_from_table('Sales', f"City WHERE Country = '{selected_country}' AND City IS NOT NULL")
                city = st.selectbox("City", cities_in_country, key="sale_city")
            else:
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
                if st.button("**Valider**", key="validate_sale", use_container_width=True):
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
                        # Reload data after successful insertion to update graphs
                        sales_df, _, _, _ = load_data()
                        agent_sales = sales_df[sales_df['Hyp'] == hyp_agent] if hyp_agent else pd.DataFrame()
                        st.session_state['agent_sales_updated'] = True # Use a session state to trigger re-render if needed
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")

            with annuler:
                st.markdown("""
                    <style>
                        div.stButton > button {
                            width: 100%;
                            background-color: #fcce22;
                            color: #333;
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
                if st.button("**Annuler**", key="cancel_sale", use_container_width=True):
                    
                    clear_form()
                    st.warning("Opération annulée et champs vidés")
        with col3:
            st.markdown("### Informations sur le Log :")
            st.warning("Opération imposible : Aucun Logs n'a été définis")
        display_sales_graphs(agent_sales)

    except Exception as e:
        st.error(f"Erreur: {e}")
    finally:
        if conn:
            conn.close()
def New_Recolt_Agent():
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
    # Header section
    col1, col2 = st.columns([2, 2])
    with col1:
        st.markdown(
            "<h1 style='text-align: left; color: #002a48; margin-bottom: 0;'>Récolts</h1>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            "<h1 style='text-align: right; color: #00afe1; margin-bottom: 0;'>Nouvelle Récolts</h1>",
            unsafe_allow_html=True
        )
    
    
    hyp_agent = st.session_state.get("hyp", None)

    # Load existing data
    _, recolts_df, _, _ = load_data()
    agent_recolts = recolts_df[recolts_df['Hyp'] == hyp_agent] if hyp_agent else pd.DataFrame()
    conn = get_db_connection()

    # Agent title
    st.markdown(
        f"<h2 style='color: #007bad;text-align: left;'>Nouvelle Récolte au nom de : {st.session_state.get('username', 'Agent')}</h2>",
        unsafe_allow_html=True
    )

    try:
        # Get unique values from database
        countries = get_unique_values_from_table('Recolt', 'Country')
        cities = get_unique_values_from_table('Recolt', 'City')
        banks = get_unique_values_from_table('Recolt', 'Banques')

        # Main form layout
        form_col1, form_col2, info_col = st.columns([1, 2, 2])
        
        # FORM COLUMN 1 - Basic information
        with form_col1:
            st.markdown("### Informations de base")
            order_reference = st.text_input("Référence du BP", key="recolt_ref")
            order_date = st.date_input("Date", value=datetime.today(), key="recolt_date")
            
            country = st.selectbox("Pays", countries, key="recolt_country")
            
            # Filter cities based on selected country
            selected_country = st.session_state.get('recolt_country', None)
            if selected_country:
                cities_in_country = get_unique_values_from_table('Recolt', 
                    f"City WHERE Country = '{selected_country}' AND City IS NOT NULL")
                city = st.selectbox("Ville", cities_in_country, key="recolt_city")
            else:
                city = st.selectbox("Ville", cities, key="recolt_city")

        # FORM COLUMN 2 - Transaction details
        with form_col2:
            st.markdown("### Détails de la transaction")
            status_col, bank_col = st.columns(2)
            with status_col:
                short_message = st.selectbox("Statut", ["Accepted", "Refused", "Error"], 
                    key="recolt_status")
            with bank_col:
                bank = st.selectbox("Banque", banks, key="recolt_bank")
            
            # Rating
            rating = st.slider("Évaluation (1-9)", min_value=1, max_value=9, 
                key="recolt_rating")
            
            
            
            # Amount section
            amount_col1, amount_col2 = st.columns([2, 1])
            with amount_col1:
                st.markdown("**Montant (€)**")
                montant_input = st.number_input("Saisir le montant", 
                    min_value=0.0, step=5.0, format="%.2f", key="recolt_amount",
                    label_visibility="collapsed")
            with amount_col2:
                st.markdown("**Ou utiliser le slider**")
                montant_slider = st.slider("", min_value=0, max_value=1000, 
                    step=5, key="recolt_slider", label_visibility="collapsed")
            
            # Status and bank
            

            # Action buttons
            valider, annuler = st.columns(2)
            with valider:
                st.markdown("""
                    <style>
                        div.stButton > button {
                            width: 100%;
                            background-color: #fc6c04;
                            color: white;
                            border-radius: 5px;
                            border: none;
                            padding: 10px;
                            font-size: 1.1em;
                        }
                        div.stButton > button:hover {
                            background-color: #fc6c04;
                        }
                    </style>
                    """, unsafe_allow_html=True)
                if st.button("**Valider**", key="validate_recolt"):
                    total_recolt = montant_input if montant_input > 0 else montant_slider
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            """INSERT INTO Recolt (Hyp, ORDER_REFERENCE, ORDER_DATE, 
                            SHORT_MESSAGE, Country, City, Total_Recolt, Rating, Banques)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (hyp_agent, order_reference, order_date, short_message, 
                             country, city, total_recolt, rating, bank)
                        )
                        conn.commit()
                        st.success("Récolte enregistrée avec succès!")
                        _, recolts_df, _, _ = load_data()
                        agent_recolts = recolts_df[recolts_df['Hyp'] == hyp_agent] if hyp_agent else pd.DataFrame()
                        st.session_state['agent_recolts_updated'] = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")
            
            with annuler:
                st.markdown("""
                    <style>
                        div.stButton > button {
                            width: 100%;
                            background-color: #fcce22;
                            color: #333;
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
                if st.button("**Annuler**", key="cancel_recolt"):
                    clear_form()
                    st.warning("Opération annulée et champs vidés")

        # INFO COLUMN - Log information and graphs
        with info_col:
            st.markdown("### Informations sur le Log")
            st.warning("Opération imposible : Aucun Logs n'a été définis")

        display_recolt_graphs(agent_recolts)

    except Exception as e:
        st.error(f"Erreur: {e}")
    finally:
        if conn:
            conn.close()