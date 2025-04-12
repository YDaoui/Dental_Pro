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

from Supports import *
from Managers import *

def login_page():
    col1, col2,col3, col4  = st.columns([1,1,2,1])
    with col2:
        st.image('Dental_Implant1.png', width=340)
    with col3:
        st.markdown("<h2 style='color:#007bad;'>Connexion</h2>", unsafe_allow_html=True)
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        col1, col2 = st.columns([1,5])
        with col1:
        
            if st.button("**Se connecter**", key="login_button"):
                user_data = authenticate(username, password)
                if user_data:
                    st.session_state.update({
                        "authenticated": True,
                        "hyp": user_data[0],
                        "user_type": user_data[1],
                        "date_in": user_data[2],
                        "username": username
                    })
                    st.success("Authentification réussie")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects")
        with col2:
            st.button("   **  Annuler  **    ", key="Annuler_button")

@st.cache_data


def setting_page():
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image('Dental_Implant2.png', width=150)
    with col2:
        st.markdown("<h1 style='color: #002a48; margin-bottom: 0;'>Global Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #007bad; margin-top: 0;'>Settings All Teams</h2>", unsafe_allow_html=True)

        st.markdown("---")

    st.markdown("<h2 style='font-size: 38px; font-weight: bold; color: #00afe1;'>Paramètres Utilisateur</h2>", unsafe_allow_html=True)
    
    hyp_input = st.text_input("Entrez l'ID (Hyp) de l'utilisateur")
    
    if hyp_input:
        user_details = get_user_details(hyp_input)
        
        if user_details:
            date_in = user_details[2]
            anciennete = (datetime.now().date() - date_in.date()).days // 365
            
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.markdown("<h2 style='font-size: 28px; color: #002a48;'>Informations Professionnelles : </h2>", unsafe_allow_html=True)
                st.write(f"**Nom:** {user_details[0]}")
                st.write(f"**Prénom:** {user_details[1]}")
                st.write(f"**Date d'entrée:** {date_in.strftime('%d/%m/%Y')}")
                st.write(f"**Ancienneté:** {anciennete} ans")
            
            with col2:
                st.subheader("")
                st.write(f"**Team:** {user_details[3]}")
                st.write(f"**Type:** {user_details[4]}")
                st.write(f"**Activité:** {user_details[5]}")
                st.write(f"**Nom d'utilisateur:** {user_details[6]}")
                st.write(f"**Dernière connexion:** {user_details[7] if user_details[7] else 'Jamais'}")
            
            with col3:
                st.markdown("<h2 style='font-size: 28px; font-weight: bold; color: #007bad;'>Action : </h2>", unsafe_allow_html=True)
                reset_pwd = st.checkbox("Réinitialiser le mot de passe")
                
                if reset_pwd:
                    if st.button("Confirmer la réinitialisation"):
                        if reset_password(hyp_input):
                            st.success(f"Mot de passe réinitialisé avec succès à la valeur: {hyp_input}")
                        else:
                            st.error("Erreur lors de la réinitialisation du mot de passe")
            st.markdown("---")
        else:
            st.warning("Aucun utilisateur trouvé avec cet ID (Hyp)")

            
def reset_password(hyp):
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                UPDATE Users
                SET PassWord = ?
                WHERE Hyp = ?
            """, (hyp, hyp))
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Erreur lors de la réinitialisation du mot de passe : {e}")
        return False
    finally:
        conn.close()





def get_db_connection():
    server = 'DESKTOP-2D5TJUA'
    database = 'Total_Stat'
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None
    







def get_db_connection():
    server = 'DESKTOP-2D5TJUA'
    database = 'Total_Stat'
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None



def authenticate(username, password):
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "SELECT u.Hyp, e.Type, e.Date_In FROM Users u "
                    "JOIN Effectifs e ON u.Hyp = e.Hyp "
                    "WHERE u.UserName = ? AND u.PassWord = ?", 
                    (username, password))
                result = cursor.fetchone()
                return result if result else None
        except Exception as e:
            st.error(f"Erreur d'authentification : {e}")
            return None
        finally:
            conn.close()