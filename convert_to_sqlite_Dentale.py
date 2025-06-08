import pandas as pd
import sqlite3

# Chemin vers votre fichier Excel
excel_file = "Dentale_Options.xlsx"

# Lire chaque feuille
users_df = pd.read_excel(excel_file, sheet_name="Users")
effectif_df = pd.read_excel(excel_file, sheet_name="Effectif")
sales_df = pd.read_excel(excel_file, sheet_name="Sales")
recolts_df = pd.read_excel(excel_file, sheet_name="Recolt")
Logs_df = pd.read_excel(excel_file, sheet_name="Logs")

# Créer la base SQLite
conn = sqlite3.connect("Dentale_BD_Sqlite.db")

# Stocker chaque feuille dans une table
users_df.to_sql("Users", conn, index=False, if_exists="replace")
effectif_df.to_sql("Effectifs", conn, index=False, if_exists="replace")
sales_df.to_sql("Sales", conn, index=False, if_exists="replace")
recolts_df.to_sql("Recolt", conn, index=False, if_exists="replace")
Logs_df.to_sql("Logs", conn, index=False, if_exists="replace")


# Vérification
print("Tables créées :", pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn))

conn.close()