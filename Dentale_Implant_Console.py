import streamlit as st
from Utils_Dental import *
from Managers import manager_dashboard
from Supports import support_dashboard
from Agents import agent_dashboard

# Configuration de la page
st.set_page_config(
    layout="wide",
    page_title="Global Sales Dashboard",
    page_icon="📊",
    initial_sidebar_state="expanded"
)
def login_page():
    col1, col2, col3, col4 = st.columns([1,1,2,1])
    with col2:
        st.image('Dental_Implant1.png', width=340)
    with col3:
        st.markdown("<h2 style='color:#007bad;'>Connexion</h2>", unsafe_allow_html=True)
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        col1, col2 = st.columns([1,1])
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
            st.button("**Annuler**", key="Annuler_button")


# CSS personnalisé

st.markdown("""
    <style>
    /* BASE STYLES */
    * {
        font-weight: bold !important; /* Tout en gras */
    }
    
    /* COULEURS */
    :root {
        --bleu-fonce: #003866;
        --bleu-ciel: #00a6d7;
        --orange: #ff7d00;
        --jaune: #ffcc00;
    }
    
    /* SIDEBAR BLANCHE */
    [data-testid="stSidebar"] {
        background: white !important;
    }
    
    /* MENU - UTILISE LES 4 COULEURS */
    [data-testid="stVerticalBlock"] > div:has(> .stButton) {
        background: linear-gradient(145deg, var(--bleu-fonce), var(--bleu-ciel));
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* BOUTONS (style inchangé) */
    .stButton>button {
        background: linear-gradient(to right, var(--orange), var(--jaune)) !important;
        color: var(--bleu-fonce) !important;
        border: none !important;
        border-radius: 8px !important;
    }
    
    /* TITRES (dégradé bleu) */
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(to right, var(--bleu-fonce), var(--bleu-ciel)) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    /* INPUTS (style inchangé) */
    .stTextInput>div>div>input {
        border: 1px solid var(--bleu-ciel) !important;
    }
    </style>
""", unsafe_allow_html=True)



def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state.get("authenticated"):
        if st.session_state.get("user_type") == "Manager":
            manager_dashboard()
        elif st.session_state.get("user_type") == "Hyperviseur":
            manager_dashboard()
        elif st.session_state.get("user_type") == "Support":
            support_dashboard()
        else:
            agent_dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()