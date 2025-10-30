# C:\Users\YDaoui\Desktop\Project_2025\AccorHotels\Accor_Python\Managment_Accor\ui_utils.py

import streamlit as st
from PIL import Image
import os

def display_logo(image_path, width=200):
    """
    Affiche une image logo dans l'application Streamlit.
    """
    try:
        # Assurez-vous que le chemin d'accès à l'image est correct.
        # Si 'Images' est un dossier à côté du script, os.path.join est approprié.
        full_path = os.path.join(os.path.dirname(__file__), image_path)
        img = Image.open(full_path)
        st.image(img, width=width)
    except FileNotFoundError:
        st.error(f"Erreur: Image introuvable à l'emplacement '{image_path}'. Vérifiez le chemin.")
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'image : {e}")

def add_custom_cssZE():
    """
    Ajoute du CSS personnalisé pour styliser l'application Streamlit.
    """
    custom_css = """
    <style>
        footer {visibility: hidden;}
        body, .stApp, .main {background-color: #FFFFFF !important;}
        * {font-weight: bold !important; color: #1c1c4c !important;}
        .stButton>button {
            background-color: #bb8654;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #ffe7ad;
            color: #bb8654;
        }
        .stSelectbox>div>div>input {
            background-color: #ffe7ad;
            color: #bb8654;
        }
        .stSelectbox>div>div>input:focus {
            background-color: #bb8654;
            color: white;
        }
        .stSelectbox label {
            color: #b28765;
        }
        .sidebar .option-menu {
            background-color: #040233;
            color: white;
            padding: 20px;
            height: 100vh;
            overflow: auto;
        }
        .sidebar .option-menu .nav-link {
            color: white;
            font-size: 16px;
            text-align: left;
            padding: 10px;
            cursor: pointer;
        }
        .sidebar .option-menu .nav-link-selected {
            background-color: #b28765;
            color: white;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)