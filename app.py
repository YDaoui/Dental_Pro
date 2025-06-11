from flask import Flask, request, jsonify, send_from_directory, session
from flask_session import Session
from datetime import date, datetime
import os
import Utils as ud # Votre module Utils.py
import pandas as pd

app = Flask(__name__, static_folder='static', template_folder='templates')

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

print("INFO: Flask-Session initialisé avec SESSION_TYPE='filesystem'")

print("INFO: Chargement initial des données...")
global sales_df, recolts_df, staff_df, logs_df
sales_df, recolts_df, staff_df, logs_df = ud.load_data()
sales_df = ud.preprocess_data(sales_df)
recolts_df = ud.preprocess_data(recolts_df)
logs_df = ud.preprocess_data(logs_df)
staff_df = ud.preprocess_data(staff_df)
print("INFO: Données chargées et prétraitées.")

@app.route('/')
def index():
    print(f"DEBUG: Requête pour la page d'accueil. Session authentifiée: {session.get('authenticated')}")
    return send_from_directory('static', 'index.html')

@app.route('/dashboard')
def dashboard():
    print(f"DEBUG: Requête pour le tableau de bord. Session authentifiée: {session.get('authenticated')}")
    if not session.get('authenticated'):
        print("DEBUG: Accès au tableau de bord non autorisé, redirection vers la page de connexion.")
        return send_from_directory('static', 'index.html')
    print("DEBUG: Accès au tableau de bord autorisé.")
    return send_from_directory('static', 'dashboard.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    print(f"DEBUG: Tentative de connexion API pour l'utilisateur: {username}")
    user_data = ud.authenticate(username, password)
    if user_data:
        session['authenticated'] = True
        session['hyp'] = user_data[0]
        session['user_type'] = user_data[1]
        session['date_in'] = user_data[2]
        session['username'] = username
        print(f"INFO: Authentification réussie pour {username}. Session['authenticated'] = {session.get('authenticated')}")
        return jsonify({"authenticated": True, "message": "Authentification réussie !"})
    else:
        session['authenticated'] = False
        print(f"INFO: Authentification échouée pour {username}.")
        return jsonify({"authenticated": False, "message": "Identifiants incorrects."}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    print(f"DEBUG: Tentative de déconnexion. Session avant: {session.get('authenticated')}")
    session.clear()
    print(f"INFO: Déconnexion réussie. Session après: {session.get('authenticated')}")
    return jsonify({"message": "Déconnexion réussie."})

@app.route('/api/data')
def get_dashboard_data():
    print(f"DEBUG: Requête API /api/data. Session authentifiée: {session.get('authenticated')}")
    if not session.get('authenticated'):
        print("DEBUG: Accès API /api/data non autorisé.")
        return jsonify({"message": "Non autorisé"}), 401

    return jsonify({
        "total_sales": sales_df['Total_Sale'].sum() if 'Total_Sale' in sales_df.columns else 0,
        "total_recolts": recolts_df['Total_Recolt'].sum() if 'Total_Recolt' in recolts_df.columns else 0,
        "total_logs": len(logs_df),
        "active_agents": len(staff_df[staff_df['Type'] == 'Agent']) if 'Type' in staff_df.columns else 0
    })

@app.route('/api/logs_filtered')
def get_logs_filtered():
    print(f"DEBUG: Requête API /api/logs_filtered. Session authentifiée: {session.get('authenticated')}")
    if not session.get('authenticated'):
        return jsonify({"message": "Non autorisé"}), 401

    offre = request.args.get('offre', 'Tous')
    team = request.args.get('team', 'Toutes')
    activity = request.args.get('activity', 'Toutes')
    segment = request.args.get('segment', 'Tous')
    statut_bp = request.args.get('statut_bp', 'Tous')
    canal = request.args.get('canal', 'Tous')
    direction = request.args.get('direction', 'Tous')
    qualification = request.args.get('qualification', 'Tous')

    start_date_str = request.args.get('start_date', '2000-01-01')
    end_date_str = request.args.get('end_date', '2099-12-31')
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Format de date invalide. Utilisez YYYY-MM-DD."}), 400

    filtered_logs = ud.filter_data(
        logs_df,
        'Tous',
        team,
        activity,
        'Toutes',
        start_date,
        end_date,
        staff_df
    )

    if offre != 'Tous' and 'Offre' in filtered_logs.columns:
        filtered_logs = filtered_logs[filtered_logs['Offre'] == offre]
    if segment != 'Tous' and 'Segment' in filtered_logs.columns:
        filtered_logs = filtered_logs[filtered_logs['Segment'] == segment]
    if statut_bp != 'Tous' and 'Statut_BP' in filtered_logs.columns:
        filtered_logs = filtered_logs[filtered_logs['Statut_BP'] == statut_bp]
    if canal != 'Tous' and 'Canal' in filtered_logs.columns:
        filtered_logs = filtered_logs[filtered_logs['Canal'] == canal]
    if direction != 'Tous' and 'Direction' in filtered_logs.columns:
        filtered_logs = filtered_logs[filtered_logs['Direction'] == direction]
    if qualification != 'Tous' and 'Qualification' in filtered_logs.columns:
        filtered_logs = filtered_logs[filtered_logs['Qualification'] == qualification]

    logs_output = filtered_logs.to_dict(orient='records')
    for log in logs_output:
        for key, value in log.items():
            if isinstance(value, (datetime, date)):
                log[key] = value.isoformat()

    return jsonify(logs_output)


@app.route('/api/sales')
def get_sales_data():
    print(f"DEBUG: Requête API /api/sales. Session authentifiée: {session.get('authenticated')}")
    if not session.get('authenticated'):
        return jsonify({"message": "Non autorisé"}), 401

    country = request.args.get('country', 'Tous')
    team = request.args.get('team', 'Toutes')
    activity = request.args.get('activity', 'Toutes')
    transaction_filter = request.args.get('transaction_filter', 'Toutes')

    start_date_str = request.args.get('start_date', '2000-01-01')
    end_date_str = request.args.get('end_date', '2099-12-31')
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Format de date invalide. Utilisez YYYY-MM-DD."}), 400

    filtered_sales = ud.filter_data(
        sales_df,
        country,
        team,
        activity,
        transaction_filter,
        start_date,
        end_date,
        staff_df
    )

    sales_output = filtered_sales.to_dict(orient='records')
    for sale in sales_output:
        for key, value in sale.items():
            if isinstance(value, (datetime, date)):
                sale[key] = value.isoformat()

    return jsonify({
        "sales_data": sales_output,
        # Vous pouvez calculer et inclure ici les métriques agrégées pour les cartes (total sales, avg sales, etc.)
        # au lieu de les recalculer en JavaScript. C'est plus efficace.
        "total_sales_metric": filtered_sales['Total_Sale'].sum() if 'Total_Sale' in filtered_sales.columns else 0,
        "avg_sale_metric": filtered_sales['Total_Sale'].mean() if 'Total_Sale' in filtered_sales.columns else 0,
        "total_transactions_metric": len(filtered_sales)
    })

@app.route('/api/recolts')
def get_recolts_data():
    print(f"DEBUG: Requête API /api/recolts. Session authentifiée: {session.get('authenticated')}")
    if not session.get('authenticated'):
        return jsonify({"message": "Non autorisé"}), 401

    # Ajouter les filtres si nécessaire, comme pour les ventes et les logs
    filtered_recolts = recolts_df.copy() # Remplacez par ud.filter_data avec les filtres appropriés
    recolts_output = filtered_recolts.to_dict(orient='records')
    for recolt in recolts_output:
        for key, value in recolt.items():
            if isinstance(value, (datetime, date)):
                recolt[key] = value.isoformat()
    return jsonify({
        "recolts_data": recolts_output,
        "total_recolts_metric": filtered_recolts['Total_Recolt'].sum() if 'Total_Recolt' in filtered_recolts.columns else 0,
        "total_transactions_recolts_metric": len(filtered_recolts)
    })

@app.route('/api/agents')
def get_agents_data():
    print(f"DEBUG: Requête API /api/agents. Session authentifiée: {session.get('authenticated')}")
    if not session.get('authenticated'):
        return jsonify({"message": "Non autorisé"}), 401

    # Ajouter les filtres si nécessaire
    filtered_agents = staff_df.copy() # Remplacez par ud.filter_data avec les filtres appropriés
    agents_output = filtered_agents.to_dict(orient='records')
    for agent in agents_output:
        for key, value in agent.items():
            if isinstance(value, (datetime, date)):
                agent[key] = value.isoformat()
    return jsonify({
        "agents_data": agents_output,
        "total_agents_metric": len(filtered_agents)
    })

@app.route('/api/supports')
def get_supports_data():
    print(f"DEBUG: Requête API /api/supports. Session authentifiée: {session.get('authenticated')}")
    if not session.get('authenticated'):
        return jsonify({"message": "Non autorisé"}), 401
    # La table 'Supports' n'est pas chargée dans Utils.py.
    # Vous devriez l'ajouter dans load_data si elle existe.
    return jsonify({"supports_data": [], "message": "Données de support non implémentées ou table manquante."})

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')

    app.run(debug=True, port=5000)
