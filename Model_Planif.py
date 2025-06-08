import streamlit as st
import pandas as pd
from datetime import time, timedelta
import numpy as np
import random

# --- Fonction principale pour toute la simulation de planning ---
def simulation_planning():
    # --- Votre fonction de style CSS personnalisée ---
    def add_custom_css():
        st.markdown("""
            <style>
            /* General Body Background - BLANC PUR */
            body {
                background-color: #FFFFFF; /* Fond blanc pur */
                color: #3D3B40; /* Primary Dark Blue for default text on light background */
            }
            .stApp {
                background-color: #FFFFFF; /* Streamlit app background */
            }

            /* ==== General Titles ==== */
            h1 {
                color: #3D3B40; /* Primary Dark Blue */
                margin-bottom: 10px;
                font-size: 3em;
                text-align: center;
                padding-bottom: 6px;
                border-bottom: 3px solid #525CEB; /* Accent Blue/Purple */
                font-weight: 900;
            }
            h2 {
                color: #3D3B40; /* Primary Dark Blue */
                margin-top: 8px;
                margin-bottom: 25px;
                font-size: 2em;
                text-align: center;
                font-weight: 800;
            }
            h3 {
                color: #3D3B40; /* Primary Dark Blue */
                margin-top: 35px;
                margin-bottom: 20px;
                border-bottom: 2px solid #525CEB; /* Accent Blue/Purple */
                padding-bottom: 6px;
                font-size: 1.6em;
                font-weight: 700;
            }
            hr {
                border: none;
                border-top: 2px solid #525CEB; /* Accent Blue/Purple */
                margin: 20px auto 25px auto;
                width: 85%;
                border-radius: 5px;
            }

            /* ==== Tabs ==== */
            .stTabs [data-baseweb="tab-list"] button {
                background-color: #BFCFE7; /* Lighter Accent/Text for tab background */
                border-radius: 8px 8px 0 0;
                padding: 10px 16px;
                margin-right: 8px;
                border: 1px solid #525CEB; /* Accent Blue/Purple */
                border-bottom: none;
                color: #3D3B40; /* Primary Dark Blue for text */
                font-weight: bold;
                font-size: 1em;
                transition: all 0.2s ease-in-out;
            }
            .stTabs [data-baseweb="tab-list"] button:hover {
                background-color: #525CEB; /* Accent Blue/Purple for hover */
                color: #FFFFFF; /* Blanc pur pour le texte au survol (contre le bleu) */
            }
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
                background-color: #3D3B40; /* Primary Dark Blue for selected tab */
                color: #BFCFE7; /* Lighter Accent/Text for text on selected tab */
                border-color: #3D3B40; /* Primary Dark Blue */
            }
            .stTabs {
                margin-top: -10px;
                margin-bottom: 20px;
            }

            /* ==== Metric Cards ==== */
            .metric-card {
                background-color: #BFCFE7; /* Lighter Accent/Text for card background */
                border: 1px solid #525CEB; /* Accent Blue/Purple */
                border-left: 6px solid #3D3B40; /* Primary Dark Blue for prominent border */
                border-radius: 10px;
                padding: 12px;
                margin-bottom: 12px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
                text-align: center;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                color: #3D3B40; /* Primary Dark Blue for text */
                min-height: 80px;
            }
            .metric-card:hover {
                transform: translateY(-4px);
                box-shadow: 3px 3px 14px rgba(0,0,0,0.5);
            }
            .metric-title {
                color: #3D3B40; /* Primary Dark Blue */
                font-size: 0.95em;
                font-weight: 700;
                margin-bottom: 6px;
                text-transform: uppercase;
                letter-spacing: 0.6px;
            }
            .metric-value {
                color: #3D3B40; /* Primary Dark Blue */
                font-size: 2em;
                font-weight: 800;
                line-height: 1;
            }

            /* ==== Selectbox ==== */
            .stSelectbox div[data-baseweb="select"] {
                border-radius: 8px;
                border: 2px solid #525CEB; /* Accent Blue/Purple */
                padding: 6px;
                box-shadow: inset 1px 1px 3px rgba(0,0,0,0.2);
            }
            .stSelectbox div[data-baseweb="select"] > div:first-child {
                background-color: #BFCFE7; /* Lighter Accent/Text for selectbox background */
                color: #3D3B40; /* Primary Dark Blue for text */
                font-weight: bold;
            }
            .stSelectbox div[data-baseweb="popover"] div[role="listbox"] {
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            .stSelectbox div[data-baseweb="menu"] {
                background-color: #3D3B40; /* Primary Dark Blue for dropdown menu background */
            }
            .stSelectbox div[data-baseweb="menu"] li {
                color: #FFFFFF; /* Blanc pur for menu items text */
                font-size: 1em;
            }
            .stSelectbox div[data-baseweb="menu"] li:hover {
                background-color: #525CEB; /* Accent Blue/Purple for hover */
                color: #FFFFFF; /* Blanc pur for text on hover */
            }

            /* ==== Button Styling ==== */
            .stButton button {
                background-color: #BFCFE7; /* Lighter Accent/Text for button background */
                color: #3D3B40; /* Primary Dark Blue for button text */
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 1em;
                transition: all 0.2s ease;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.15);
                cursor: pointer;
            }

            .stButton button:hover {
                background-color: #525CEB; /* Accent Blue/Purple for hover */
                color: #FFFFFF; /* Blanc pur pour le texte au survol */
                box-shadow: 3px 3px 12px rgba(0,0,0,0.25);
            }

            .stButton button:active,
            .stButton button:focus:not(:active) {
                background-color: #3D3B40; /* Primary Dark Blue for active/focus */
                color: #BFCFE7; /* Lighter Accent/Text for text */
                box-shadow: inset 2px 2px 6px rgba(0,0,0,0.2);
            }

            /* ==== DataFrame ==== */
            .stDataFrame {
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
            }
            .stDataFrame table {
                border-collapse: collapse;
                width: 100%;
            }
            .stDataFrame thead th {
                background-color: #3D3B40; /* Primary Dark Blue for header */
                color: #BFCFE7; /* Lighter Accent/Text for header text */
                padding: 12px;
                text-align: left;
                font-weight: bold;
            }
            .stDataFrame tbody tr:nth-child(odd) {
                background-color: #FFFFFF; /* Blanc pur pour les lignes impaires */
            }
            .stDataFrame tbody tr:hover {
                background-color: #525CEB; /* Accent Blue/Purple on hover */
                color: #FFFFFF; /* Blanc pur pour le texte au survol */
            }
            .stDataFrame tbody td {
                padding: 10px 12px;
                border-bottom: 1px solid #525CEB; /* Accent Blue/Purple */
                color: #3D3B40; /* Primary Dark Blue for text */
            }

            /* ==== Sidebar & Menu ==== */
            div[data-testid="stSidebar"] {
                background-color: #BFCFE7 !important; /* Lighter Accent/Text for sidebar background */
                color: #3D3B40 !important; /* Primary Dark Blue for sidebar text */
            }
            .css-1cypcdb, .css-1lcbmhc { /* Streamlit menu/option container */
                background-color: #BFCFE7 !important; /* Lighter Accent/Text */
                border: none;
            }
            .css-1cypcdb button, .css-1lcbmhc button { /* Streamlit menu/option buttons */
                color: #3D3B40 !important; /* Primary Dark Blue */
                background-color: transparent !important;
                font-weight: bold;
                padding: 10px 16px;
                margin-right: 8px;
                border-radius: 6px;
                transition: all 0.2s ease-in-out;
            }
            .css-1cypcdb button:hover, .css-1lcbmhc button:hover {
                background-color: #525CEB !important; /* Accent Blue/Purple */
                color: #FFFFFF !important; /* Blanc pur - text */
            }
            .css-1cypcdb button[data-selected="true"], .css-1lcbmhc button[data-selected="true"] {
                background-color: #3D3B40 !important; /* Primary Dark Blue - background */
                color: #BFCFE7 !important; /* Lighter Accent/Text - text */
            }

            /* ==== Date Input (Date Picker) ==== */
            .stDateInput div[data-baseweb="input"] {
                background-color: #BFCFE7; /* Lighter Accent/Text */
                color: #3D3B40; /* Primary Dark Blue for text */
                border: 2px solid #525CEB; /* Accent Blue/Purple */
                border-radius: 8px;
                padding: 6px;
            }
            .stDateInput div[data-baseweb="input"] input {
                background-color: #BFCFE7; /* Lighter Accent/Text */
                color: #3D3B40; /* Primary Dark Blue for input text */
                font-weight: bold;
            }
            /* Calendar/Picker styling */
            .stDateInput div[data-baseweb="calendar"] {
                background-color: #FFFFFF; /* Fond blanc pur pour le calendrier */
                border: 1px solid #525CEB; /* Accent Blue/Purple border */
                color: #3D3B40; /* Primary Dark Blue for calendar text */
                border-radius: 8px;
            }
            .stDateInput div[data-baseweb="calendar"] .DayPicker_weekdays {
                color: #525CEB; /* Accent Blue/Purple for weekday headers */
            }
            .stDateInput div[data-baseweb="calendar"] .DayPicker_day {
                color: #3D3B40; /* Primary Dark Blue for days */
            }
            .stDateInput div[data-baseweb="calendar"] .DayPicker_day--selected {
                background-color: #3D3B40 !important; /* Primary Dark Blue for selected day */
                color: #BFCFE7 !important; /* Lighter Accent/Text for selected day text */
            }
            .stDateInput div[data-baseweb="calendar"] .DayPicker_day--hovered {
                background-color: #525CEB !important; /* Accent Blue/Purple for hovered day */
                color: #FFFFFF !important; /* Blanc pur pour le texte au survol */
            }
            .stDateInput .flatpickr-calendar { /* Older Streamlit versions might use flatpickr */
                background-color: #FFFFFF !important;
                border: 1px solid #525CEB !important;
            }
            .stDateInput .flatpickr-day {
                color: #3D3B40 !important;
            }
            .stDateInput .flatpickr-day.selected, .stDateInput .flatpickr-day.startRange, .stDateInput .flatpickr-day.endRange {
                background-color: #3D3B40 !important;
                color: #BFCFE7 !important;
            }
            .stDateInput .flatpickr-day.today:not(.selected) {
                border-color: #525CEB !important;
            }
            .stDateInput .flatpickr-day.hover {
                background-color: #525CEB !important;
                color: #FFFFFF !important;
            }
            </style>
        """, unsafe_allow_html=True)

    # Appliquer le CSS personnalisé
    add_custom_css()

    st.title("Simulation de Planning Hebdomadaire")

    # --- Paramètres de l'Effectif ---
    total_staff = 150
    debc_staff_count = 12
    bus_staff_count = 1
    other_activities_staff_count = total_staff - debc_staff_count - bus_staff_count

    # Définir les horaires de travail
    debc_bus_shift_full = "09h00 - 20h00"
    other_activities_shift_standard = "10h00 - 20h00 (avec 1h pause déjeuner)"

    # --- Simulation de la Table `Effectifs` ---
    # Pour cette simulation, nous allons créer un DataFrame Pandas qui représente votre table `Effectifs`.
    # En production, vous chargeriez ces données depuis votre base de données ou un fichier.
    np.random.seed(42) # pour la reproductibilité
    random.seed(42) # pour la reproductibilité

    # Générer tous les noms du personnel
    all_staff_data = []
    for i in range(total_staff):
        all_staff_data.append({
            'NOM': f"Nom_{i+1}",
            'PRENOM': f"Prénom_{i+1}"
        })
    all_staff_df = pd.DataFrame(all_staff_data)

    # Attribuer l'activité en garantissant les décomptes spécifiques
    activities = ['DECB'] * debc_staff_count + \
                 ['BUS'] * bus_staff_count + \
                 ['Autre Activité'] * other_activities_staff_count
    random.shuffle(activities) # Mélanger pour distribuer les activités aléatoirement parmi le personnel
    all_staff_df['Activité'] = activities

    # Ajouter d'autres colonnes fictives pour compléter la table 'Effectifs'
    all_staff_df['Hyp'] = np.random.choice(['Hypothese A', 'Hypothese B', 'Hypothese C'], size=total_staff)
    all_staff_df['Team'] = np.random.randint(1, 6, size=total_staff) # 5 équipes
    all_staff_df['Date_In'] = pd.to_datetime('2022-01-01') + pd.to_timedelta(np.random.randint(0, 730, size=total_staff), unit='D') # Période des 2 dernières années
    all_staff_df['Type'] = np.random.choice(['CDI', 'CDD', 'Alternance'], size=total_staff)
    all_staff_df['Departement'] = np.random.choice(['Opérations', 'Clientèle', 'Ressources Humaines', 'IT', 'Marketing'], size=total_staff)

    Effectifs_df = all_staff_df.copy()

    # Extraire les listes de personnel par activité pour le planning
    debc_personnel = Effectifs_df[Effectifs_df['Activité'] == 'DECB'].apply(lambda row: f"{row['PRENOM']} {row['NOM']}", axis=1).tolist()
    bus_personnel = Effectifs_df[Effectifs_df['Activité'] == 'BUS'].apply(lambda row: f"{row['PRENOM']} {row['NOM']}", axis=1).tolist()
    other_activities_personnel_summary = f"{other_activities_staff_count} personnes (non listées individuellement ici)"

    # --- Logique de Planification Hebdomadaire ---
    # Cette fonction générera le planning en utilisant les listes de personnel extraites de votre table `Effectifs`.
    def generate_weekly_schedule_with_personnel(week_type, debc_staff_list, bus_staff_list, other_staff_summary):
        schedule_data = []
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

        if week_type == "Week A":
            st.subheader("Semaine A: **DECB** (9h-20h) | **BUS & Autres Activités** (10h-20h)")
            for day in days:
                schedule_data.append({
                    "Jour": day,
                    "Activité": "DECB",
                    "Personnel Assigné": ", ".join(debc_staff_list),
                    "Heures": debc_bus_shift_full
                })
                schedule_data.append({
                    "Jour": day,
                    "Activité": "BUS",
                    "Personnel Assigné": ", ".join(bus_staff_list),
                    "Heures": other_activities_shift_standard
                })
                schedule_data.append({
                    "Jour": day,
                    "Activité": "Autres Activités",
                    "Personnel Assigné": other_staff_summary,
                    "Heures": other_activities_shift_standard
                })

        elif week_type == "Week B":
            st.subheader("Semaine B: **BUS** (9h-20h) | **DECB & Autres Activités** (10h-20h)")
            for day in days:
                schedule_data.append({
                    "Jour": day,
                    "Activité": "BUS",
                    "Personnel Assigné": ", ".join(bus_staff_list),
                    "Heures": debc_bus_shift_full
                })
                schedule_data.append({
                    "Jour": day,
                    "Activité": "DECB",
                    "Personnel Assigné": ", ".join(debc_staff_list),
                    "Heures": other_activities_shift_standard
                })
                schedule_data.append({
                    "Jour": day,
                    "Activité": "Autres Activités",
                    "Personnel Assigné": other_staff_summary,
                    "Heures": other_activities_shift_standard
                })

        return pd.DataFrame(schedule_data)

    # --- Mise en Page de l'Application Streamlit ---
    st.write(f"Effectif total : **{total_staff} personnes**")
    st.write(f"Personnel DECB : **{debc_staff_count} personnes**")
    st.write(f"Personnel BUS : **{bus_staff_count} personne**")
    st.write(f"Personnel pour Autres Activités : **{other_activities_staff_count} personnes**")

    st.markdown("---")

    st.markdown("### Aperçu des Effectifs :")
    st.write("Voici un aperçu de la table des effectifs simulée, utilisée pour le planning :")
    st.dataframe(Effectifs_df[['NOM', 'PRENOM', 'Activité', 'Departement', 'Team', 'Type']], use_container_width=True)

    st.markdown("---")

    st.markdown("### Sélectionnez le type de semaine pour visualiser le planning :")
    week_choice = st.radio(
        "Type de Semaine",
        ("Week A", "Week B"),
        key="week_selector"
    )

    if week_choice:
        weekly_schedule_df = generate_weekly_schedule_with_personnel(
            week_choice,
            debc_personnel,
            bus_personnel,
            other_activities_personnel_summary
        )
        st.dataframe(weekly_schedule_df, use_container_width=True)

    st.markdown("---")
    #st.info("Ce planning est une simulation basée sur les données d'effectifs. Pour les 'Autres Activités', la gestion des pauses déjeuner et la répartition des tâches spécifiques doivent être planifiées en interne pour le personnel assigné. Adaptez les heures et la répartition exacte du personnel selon vos besoins spécifiques.")

# --- Appeler la fonction principale pour exécuter l'application ---
if __name__ == "__main__":
    simulation_planning()