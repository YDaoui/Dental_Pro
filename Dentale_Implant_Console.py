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
    add_custom_css()
    col1, col2, col3, col4 = st.columns([1,0.8,2,1])
    with col2:
        st.image('Dental_Implant.png', width=340)
    with col3:
        #st.markdown("<h2 style='color:#007bad;'>Connexion</h2>", unsafe_allow_html=True)
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("**Se connecter**", key="login_button", use_container_width=True):
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
            st.button("**Annuler**", key="Annuler_button", use_container_width=True)

def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state.get("authenticated"):
        user_type = st.session_state.get("user_type", "")
        
        if user_type in ["Manager", "Hyperviseur"]:
            manager_dashboard()
        elif user_type == "Support":
            support_dashboard()
        else:
            agent_dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()