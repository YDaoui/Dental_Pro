import sqlite3
import pandas as pd
from contextlib import closing

# --- Configuration de la base de données ---
# En production, utilisez des variables d'environnement ou un fichier de configuration sécurisé.
DB_PATH = 'Dentale_BD_Sqlite.db'  # <--- REMPLACEZ PAR LE CHEMIN RÉEL DE VOTRE BASE DE DONNÉES SQLITE
DB_PASSWORD = 'YDaoui2303' # <--- REMPLACEZ PAR VOTRE MOT DE PASSE RÉEL (si vous utilisez SQLCipher)

def get_db_connection():
    """Tente d'établir une connexion à la base de données SQLite."""
    print(f"DEBUG: Tentative de connexion à la base de données: {DB_PATH}")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        # ATTENTION: Cette ligne est pour SQLCipher (base de données chiffrée).
        # Si votre base de données 'Dentale_BD_Sqlite.db' n'est PAS chiffrée,
        # cette ligne DOIT être commentée ou supprimée.
        if DB_PASSWORD: # Vérifie si un mot de passe est fourni pour le PRAGMA key
            print(f"DEBUG: Tentative d'application du PRAGMA key avec un mot de passe.")
            conn.execute(f"PRAGMA key='{DB_PASSWORD}'")
        
        conn.row_factory = sqlite3.Row # Permet d'accéder aux colonnes par leur nom
        print("DEBUG: Connexion à la base de données réussie.")
        return conn
    except sqlite3.OperationalError as e:
        # Erreur spécifique si la base de données est chiffrée et que la clé est incorrecte, ou si le fichier n'est pas trouvé
        print(f"ERREUR SQLITE: Erreur opérationnelle lors de la connexion à la base de données. "
              f"Vérifiez le chemin ('{DB_PATH}') et le mot de passe SQLCipher si la BDD est chiffrée. Détails: {e}")
        if conn: conn.close() # Assurez-vous de fermer la connexion même en cas d'erreur
        return None
    except sqlite3.Error as e:
        print(f"ERREUR SQLITE: Erreur lors de la connexion à la base de données : {e}")
        if conn: conn.close()
        return None
    except Exception as e:
        print(f"ERREUR INATTENDUE: Une erreur inattendue est survenue lors de la connexion : {e}")
        if conn: conn.close()
        return None

def authenticate(username, password):
    """Authentifie l'utilisateur."""
    print(f"DEBUG: Appel de la fonction authenticate pour l'utilisateur: {username}")
    conn = get_db_connection()
    if not conn:
        print("DEBUG: La connexion à la base de données a échoué dans authenticate.")
        return None

    try:
        with closing(conn.cursor()) as cursor:
            print(f"DEBUG: Exécution de la requête d'authentification pour {username}.")
            cursor.execute(
                "SELECT u.Hyp, e.Type, e.Date_In FROM Users u "
                "JOIN Effectifs e ON u.Hyp = e.Hyp "
                "WHERE u.UserName = ? AND u.PassWord = ?",
                (username, password))
            result = cursor.fetchone()
            if result:
                print(f"DEBUG: Authentification réussie pour {username}. Hyp: {result[0]}, Type: {result[1]}")
            else:
                print(f"DEBUG: Authentification échouée pour {username}: identifiants incorrects.")
            return result if result else None
    except Exception as e:
        print(f"ERREUR AUTH: Erreur lors de l'authentification : {e}")
        return None
    finally:
        if conn:
            conn.close()
            print("DEBUG: Connexion à la base de données fermée après authentification.")

def load_data():
    """Chargement des données depuis SQLite."""
    print("DEBUG: Appel de la fonction load_data.")
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            print("DEBUG: La connexion à la base de données a échoué dans load_data.")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        sales_df = pd.DataFrame()
        recolts_df = pd.DataFrame()
        logs_df = pd.DataFrame()
        staff_df = pd.DataFrame()

        with closing(conn.cursor()) as cursor:
            print("DEBUG: Exécution de la requête pour la table Sales.")
            cursor.execute("SELECT * FROM Sales WHERE SHORT_MESSAGE <> 'ERROR'")
            sales_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

            print("DEBUG: Exécution de la requête pour la table Recolt.")
            cursor.execute("SELECT * FROM Recolt WHERE SHORT_MESSAGE <> 'ERROR'")
            recolts_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

            print("DEBUG: Exécution de la requête pour la table Logs.")
            cursor.execute("SELECT * FROM Logs WHERE Offre <> 'AB'")
            logs_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

            print("DEBUG: Exécution de la requête pour la table Effectifs.")
            cursor.execute("SELECT * FROM Effectifs WHERE Type = 'Agent'")
            staff_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

        print("DEBUG: Toutes les données chargées avec succès.")
        return sales_df, recolts_df, staff_df, logs_df
    except Exception as e:
        print(f"ERREUR CHARGEMENT DONNÉES: Erreur de chargement des données: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    finally:
        if conn:
            conn.close()
            print("DEBUG: Connexion à la base de données fermée après load_data.")

def preprocess_data(df):
    """Prétraite les données."""
    # Aucun changement, cette fonction n'interagit pas avec la BDD directement
    if 'ORDER_DATE' in df.columns:
        df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'], errors='coerce')
    if 'Total_Sale' in df.columns:
        df['Total_Sale'] = pd.to_numeric(df['Total_Sale'], errors='coerce').fillna(0)
    if 'Total_Recolt' in df.columns:
        df['Total_Recolt'] = pd.to_numeric(df['Total_Recolt'], errors='coerce').fillna(0)
    if 'Date_d_création' in df.columns:
        df['Date_d_création'] = pd.to_datetime(df['Date_d_création'], errors='coerce')
    if 'Date_In' in df.columns:
        df['Date_In'] = pd.to_datetime(df['Date_In'], errors='coerce')
    return df

def filter_data(df, country, team, activity, transaction_filter, start_date, end_date, staff_df):
    """Filtre les données des DataFrames en fonction des critères."""
    # Aucun changement, cette fonction n'interagit pas avec la BDD directement
    filtered_df = df.copy()

    date_column = None
    if 'ORDER_DATE' in filtered_df.columns:
        date_column = 'ORDER_DATE'
    elif 'Date_d_création' in filtered_df.columns:
        date_column = 'Date_d_création'

    if date_column and pd.api.types.is_datetime64_any_dtype(filtered_df[date_column]):
        filtered_df = filtered_df[
            (filtered_df[date_column].dt.date >= start_date) &
            (filtered_df[date_column].dt.date <= end_date)
        ]

    if country != 'Tous' and 'Country' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Country'] == country]

    if ('Team' not in filtered_df.columns or 'Activité' not in filtered_df.columns) and 'Hyp' in filtered_df.columns and not staff_df.empty:
        filtered_df = filtered_df.merge(staff_df[['Hyp', 'Team', 'Activité']].drop_duplicates(), on='Hyp', how='left')

    if team != 'Toutes' and 'Team' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Team'] == team]

    if activity != 'Toutes' and 'Activité' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Activité'] == activity]

    if transaction_filter != 'Toutes' and 'SHORT_MESSAGE' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['SHORT_MESSAGE'] == transaction_filter]

    return filtered_df

