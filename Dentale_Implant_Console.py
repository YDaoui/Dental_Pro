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




def add_custom_css():
    """Adds custom CSS styles to the Streamlit application."""
    st.markdown("""
        <style>
            /* Style for Streamlit buttons */
            div.stButton > button {
                width: 100%;
                background-color: #fc9307; /* Orange */
                color: white;
                border-radius: 5px;
                border: none;
                padding: 10px;
                font-size: 1.1em;
            }
            div.stButton > button:hover {
                background-color: #fcce22; /* Lighter orange on hover */
            }
            /* Custom styling for text inputs to align labels */
            .stTextInput label {
                display: none; /* Hide default Streamlit labels */
            }
            .stTextInput div[data-baseweb="input"] {
                margin-top: -10px; /* Adjust margin to align input with custom label */
            }
        </style>
    """, unsafe_allow_html=True)


    col1_main, col2_main, col3_main, col4_main = st.columns([1, 0.8, 2, 1])

    with col2_main:
        st.image('Dental_Implant.png', width=340)

    with col3_main:
        
    
        st.markdown("<h2 style='color:#fc9307;'>Connexion</h2>", unsafe_allow_html=True)
        #st.markdown("---")
        
        col_label_user, col_input_user = st.columns([1, 3])
        with col_label_user:
           
            st.markdown("<div style='color:#043a64; font-weight:bold; height: 38px; display: flex; align-items: center;'>Nom d'utilisateur :</div>", unsafe_allow_html=True)
        with col_input_user:
           
            username = st.text_input("", key="username_input", label_visibility="collapsed")

        col_label_pass, col_input_pass = st.columns([1, 3])
        with col_label_pass:
            
            st.markdown("<div style='color:#043a64; font-weight:bold; height: 38px; display: flex; align-items: center;'>Mot de passe :</div>", unsafe_allow_html=True)
            
        with col_input_pass:
            password = st.text_input("", type="password", key="password_input", label_visibility="collapsed")

    

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