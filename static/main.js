document.addEventListener('DOMContentLoaded', () => {
    // Logique pour la page de connexion (si index.html est chargée)
    const loginButton = document.getElementById('loginButton');
    if (loginButton) {
        console.log("Élément 'loginButton' trouvé. Ajout de l'écouteur d'événement.");
        loginButton.addEventListener('click', async () => {
            const username = document.getElementById('username').value;
            // Correction de la faute de frappe ici:
            const password = document.getElementById('password').value;
            const messageDiv = document.getElementById('message');

            messageDiv.textContent = 'Connexion en cours...';
            messageDiv.style.color = '#007bad';

            console.log("Tentative de connexion avec l'utilisateur:", username);

            try {
                const payload = { username, password };
                console.log("Envoi de la charge utile (payload) au serveur:", JSON.stringify(payload));

                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                console.log("Statut de la réponse reçu du serveur:", response.status);

                const data = await response.json();
                console.log("Données de réponse JSON reçues:", data);

                if (response.ok) {
                    messageDiv.style.color = 'green';
                    messageDiv.textContent = data.message;
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 500);
                } else {
                    messageDiv.style.color = 'red';
                    messageDiv.textContent = data.message || `Erreur d'authentification. Statut HTTP: ${response.status}.`;
                    console.error("Échec de l'authentification. Réponse du serveur:", data);
                }
            } catch (error) {
                messageDiv.style.color = 'red';
                messageDiv.textContent = 'Erreur de connexion au serveur ou format de réponse invalide.';
                console.error('Erreur lors de la requête de connexion:', error);
            }
        });
    }

    const navButtons = document.querySelectorAll('.nav-item');
    const contentSections = document.querySelectorAll('.content-section');
    const logoutButton = document.getElementById('logoutButton');

    if (navButtons.length > 0 && contentSections.length > 0) {
        console.log("Éléments du tableau de bord trouvés. Initialisation de la logique du tableau de bord.");
        navButtons.forEach(button => {
            button.addEventListener('click', () => {
                const page = button.dataset.page;
                console.log("Navigation vers la page:", page);
                contentSections.forEach(section => {
                    if (section.id === `${page}-section`) {
                        section.classList.add('active');
                    } else {
                        section.classList.remove('active');
                    }
                });
                navButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                loadPageContent(page);
            });
        });

        if (logoutButton) {
            console.log("Élément 'logoutButton' trouvé. Ajout de l'écouteur d'événement.");
            logoutButton.addEventListener('click', async () => {
                try {
                    const response = await fetch('/api/logout', { method: 'POST' });
                    if (response.ok) {
                        console.log("Déconnexion réussie. Redirection.");
                        window.location.href = '/';
                    } else {
                        const errorData = await response.json();
                        console.error('Échec de la déconnexion. Serveur:', errorData.message || 'Erreur inconnue.');
                    }
                } catch (error) {
                    console.error('Erreur lors de la déconnexion:', error);
                }
            });
        }

        loadPageContent('dashboard');
    } else {
        console.log("Pas sur la page du tableau de bord ou éléments non trouvés.");
    }
});

async function loadPageContent(page, filters = {}) {
    console.log(`Chargement du contenu pour la page: ${page} avec les filtres:`, filters);
    const targetSection = document.getElementById(`${page}-section`);
    if (!targetSection) {
        console.warn(`Section cible '${page}-section' non trouvée.`);
        return;
    }

    targetSection.innerHTML = '<p>Chargement des données...</p>';
    targetSection.style.color = '#007bad';

    try {
        let apiUrl = '';
        let queryParams = new URLSearchParams(filters).toString();

        switch (page) {
            case 'dashboard':
                apiUrl = '/api/data';
                break;
            case 'sales':
                apiUrl = `/api/sales?${queryParams}`;
                break;
            case 'recolts':
                apiUrl = `/api/recolts?${queryParams}`;
                break;
            case 'logs':
                apiUrl = `/api/logs_filtered?${queryParams}`;
                break;
            case 'agents':
                apiUrl = `/api/agents?${queryParams}`;
                break;
            case 'supports':
                apiUrl = `/api/supports?${queryParams}`;
                break;
            default:
                console.warn('Page non reconnue:', page);
                targetSection.innerHTML = '<p style="color: red;">Page non reconnue.</p>';
                return;
        }

        const response = await fetch(apiUrl);
        console.log(`Statut de la réponse pour la page ${page}:`, response.status);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Erreur HTTP: ${response.status} - ${errorData.message || 'Erreur inconnue'}`);
        }
        const data = await response.json();
        console.log(`Données reçues pour la page ${page}:`, data);

        if (page === 'logs') {
            displayLogs(data, targetSection);
        } else if (page === 'sales') {
            displaySales(data.sales_data || data, targetSection);
        } else if (page === 'recolts') {
            displayRecolts(data.recolts_data || data, targetSection);
        } else if (page === 'agents') {
            displayAgents(data.agents_data || data, targetSection);
        } else if (page === 'supports') {
            displaySupports(data.supports_data || data, targetSection);
        } else if (page === 'dashboard') {
            displayDashboard(data, targetSection);
        }

    } catch (error) {
        console.error(`Erreur lors du chargement du contenu de la page ${page}:`, error);
        targetSection.innerHTML = `<p style="color: red;">Erreur lors du chargement des données: ${error.message}</p>`;
    }
}

// Fonction pour afficher les logs
function displayLogs(logsData, targetElement) {
    let htmlContent = `
        <h3>Filtrage des Logs</h3>
        <div class="filters-container">
            <label for="logOffre">Offre:</label>
            <select id="logOffre">
                <option value="Tous">Tous</option>
            </select>
            <label for="logTeam">Équipe:</label>
            <select id="logTeam">
                <option value="Toutes">Toutes</option>
            </select>
            <label for="logActivity">Activité:</label>
            <select id="logActivity">
                <option value="Toutes">Toutes</option>
            </select>
            <label for="logSegment">Segment:</label>
            <select id="logSegment">
                <option value="Tous">Tous</option>
            </select>
            <label for="logStatutBp">Statut BP:</label>
            <select id="logStatutBp">
                <option value="Tous">Tous</option>
            </select>
            <label for="logCanal">Canal:</label>
            <select id="logCanal">
                <option value="Tous">Tous</option>
            </select>
            <label for="logDirection">Direction:</label>
            <select id="logDirection">
                <option value="Tous">Tous</option>
            </select>
            <label for="logQualification">Qualification:</label>
            <select id="logQualification">
                <option value="Tous">Tous</option>
            </select>
            <label for="logStartDate">Date Début:</label>
            <input type="date" id="logStartDate">
            <label for="logEndDate">Date Fin:</label>
            <input type="date" id="logEndDate">
            <button id="applyLogsFilters">Appliquer les filtres</button>
        </div>
    `;

    const offreSelect = targetElement.querySelector('#logOffre');
    if (offreSelect && logsData && logsData.length > 0) {
        const uniqueOffres = [...new Set(logsData.map(log => log.Offre).filter(Boolean))].sort();
        offreSelect.innerHTML = '<option value="Tous">Tous</option>';
        uniqueOffres.forEach(offre => {
            const option = document.createElement('option');
            option.value = offre;
            option.textContent = offre;
            offreSelect.appendChild(option);
        });
    }

    if (logsData && logsData.length > 0) {
        htmlContent += `
            <h3 style='color: #007bad;'>Indicateurs Clés des Logs</h3>
            <div class="dashboard-metrics">
                <div class="metric-card">
                    <div class="metric-title">Total Logs</div>
                    <div class="metric-value">${logsData.length.toLocaleString()}</div>
                </div>
                <!-- Calculer les métriques spécifiques aux logs ici en JavaScript si nécessaire -->
            </div>
            <h3 style='color: #007bad;'>Détails des Logs</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Hyp</th>
                        <th>BP_Logs</th>
                        <th>Sous_motif</th>
                        <th>Canal</th>
                        <th>Direction</th>
                        <th>Date Création</th>
                        <th>Qualification</th>
                        <th>Statut BP</th>
                    </tr>
                </thead>
                <tbody>
        `;
        logsData.forEach(log => {
            const dateCreation = log.Date_d_création ? new Date(log.Date_d_création).toLocaleDateString() : '';
            htmlContent += `
                <tr>
                    <td>${log.Hyp || ''}</td>
                    <td>${log.BP_Logs || ''}</td>
                    <td>${log.Sous_motif || ''}</td>
                    <td>${log.Canal || ''}</td>
                    <td>${log.Direction || ''}</td>
                    <td>${dateCreation}</td>
                    <td>${log.Qualification || ''}</td>
                    <td>${log.Statut_BP || ''}</td>
                </tr>
            `;
        });
        htmlContent += `
                </tbody>
            </table>
        `;
    } else {
        htmlContent += '<p>Aucune donnée de logs trouvée avec les filtres actuels.</p>';
    }

    targetElement.innerHTML = htmlContent;

    const applyFiltersButton = targetElement.querySelector('#applyLogsFilters');
    if (applyFiltersButton) {
        applyFiltersButton.addEventListener('click', () => {
            const offre = targetElement.querySelector('#logOffre').value;
            const team = targetElement.querySelector('#logTeam').value;
            const activity = targetElement.querySelector('#logActivity').value;
            const segment = targetElement.querySelector('#logSegment').value;
            const statut_bp = targetElement.querySelector('#logStatutBp').value;
            const canal = targetElement.querySelector('#logCanal').value;
            const direction = targetElement.querySelector('#logDirection').value;
            const qualification = targetElement.querySelector('#logQualification').value;
            const startDate = targetElement.querySelector('#logStartDate').value;
            const endDate = targetElement.querySelector('#logEndDate').value;

            const filters = {
                offre, team, activity, segment, statut_bp, canal, direction, qualification,
                start_date: startDate,
                end_date: endDate
            };
            loadPageContent('logs', filters);
        });
    }
}

// Fonction pour afficher les ventes (implémente le rendu JS des métriques et un tableau)
function displaySales(salesData, targetElement) {
    let htmlContent = `
        <h3>Filtrage des Ventes</h3>
        <div class="filters-container">
            <label for="salesCountry">Pays:</label>
            <select id="salesCountry">
                <option value="Tous">Tous</option>
            </select>
            <label for="salesTeam">Équipe:</label>
            <select id="salesTeam">
                <option value="Toutes">Toutes</option>
            </select>
            <label for="salesActivity">Activité:</label>
            <select id="salesActivity">
                <option value="Toutes">Toutes</option>
            </select>
            <label for="salesTransactionType">Type de transaction:</label>
            <select id="salesTransactionType">
                <option value="Toutes">Toutes</option>
            </select>
            <label for="salesStartDate">Date Début:</label>
            <input type="date" id="salesStartDate">
            <label for="salesEndDate">Date Fin:</label>
            <input type="date" id="salesEndDate">
            <button id="applySalesFilters">Appliquer les filtres</button>
        </div>
    `;

    // Remplir les options des filtres (basé sur les données reçues, ou une API dédiée pour les options)
    if (salesData && salesData.length > 0) {
        const uniqueCountries = [...new Set(salesData.map(sale => sale.Country).filter(Boolean))].sort();
        const countrySelect = targetElement.querySelector('#salesCountry');
        if (countrySelect) {
            countrySelect.innerHTML = '<option value="Tous">Tous</option>';
            uniqueCountries.forEach(country => {
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                countrySelect.appendChild(option);
            });
        }
        // Pour Team et Activity, vous devrez probablement récupérer ces listes via une autre API
        // ou les rendre disponibles globalement si elles sont statiques.
        const uniqueTransactionTypes = [...new Set(salesData.map(sale => sale.SHORT_MESSAGE).filter(Boolean))].sort();
        const transactionTypeSelect = targetElement.querySelector('#salesTransactionType');
        if (transactionTypeSelect) {
            transactionTypeSelect.innerHTML = '<option value="Toutes">Toutes</option>';
            uniqueTransactionTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                transactionTypeSelect.appendChild(option);
            });
        }
    }


    if (salesData && salesData.length > 0) {
        // Calculer les métriques clés en JavaScript
        const totalSales = salesData.reduce((sum, sale) => sum + (sale.Total_Sale || 0), 0);
        const averageSale = salesData.length > 0 ? totalSales / salesData.length : 0;
        const totalTransactions = salesData.length;

        htmlContent += `
            <h3 style='color: #007bad;'>Indicateurs Clés des Ventes</h3>
            <div class="dashboard-metrics">
                <div class="metric-card">
                    <div class="metric-title">Total Sales</div>
                    <div class="metric-value">${totalSales.toLocaleString(undefined, { maximumFractionDigits: 0 })}€</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Average Sale</div>
                    <div class="metric-value">${averageSale.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}€</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Transactions</div>
                    <div class="metric-value">${totalTransactions.toLocaleString()}</div>
                </div>
                <!-- Ajoutez ici des cartes pour Average Rating et autres métriques si disponibles dans salesData -->
            </div>

            <div class="sales-charts-container">
                <h3 style='color: #007bad;'>Ventes par Ville (Carte)</h3>
                <div id="salesMapChart" style="height: 400px; width: 100%;"></div>

                <h3 style='color: #007bad;'>Performance des Top Équipes</h3>
                <div id="teamPerformanceChart" style="height: 300px; width: 100%;"></div>
                <!-- Ajoutez ici la section pour les cartes de performance d'équipe si elles sont rendues en JS -->
                <div id="teamPerformanceCards"></div>

                <h3 style='color: #007bad;'>Ventes par Jour de la Semaine</h3>
                <div id="salesWeekdayChart" style="height: 300px; width: 100%;"></div>

                <h3 style='color: #007bad;'>Transactions Acceptées vs Refusées</h3>
                <div id="transactionStatusChart" style="height: 300px; width: 100%;"></div>

                <h3 style='color: #007bad;'>Ventes par Heure</h3>
                <div id="salesHourlyChart" style="height: 300px; width: 100%;"></div>
            </div>

            <h3 style='color: #007bad;'>Détails des Ventes</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Réf. Commande</th>
                        <th>Date Commande</th>
                        <th>Vente Totale</th>
                        <th>Pays</th>
                        <th>Ville</th>
                    </tr>
                </thead>
                <tbody>
        `;
        salesData.forEach(sale => {
            const orderDate = sale.ORDER_DATE ? new Date(sale.ORDER_DATE).toLocaleDateString() : '';
            htmlContent += `
                <tr>
                    <td>${sale.ORDER_REFERENCE || ''}</td>
                    <td>${orderDate}</td>
                    <td>${sale.Total_Sale || 0}</td>
                    <td>${sale.Country || ''}</td>
                    <td>${sale.City || ''}</td>
                </tr>
            `;
        });
        htmlContent += `
                </tbody>
            </table>
        `;
    } else {
        htmlContent += '<p>Aucune donnée de ventes trouvée.</p>';
    }
    targetElement.innerHTML = htmlContent;

    // Ajouter l'écouteur d'événements pour les filtres de ventes
    const applySalesFiltersButton = targetElement.querySelector('#applySalesFilters');
    if (applySalesFiltersButton) {
        applySalesFiltersButton.addEventListener('click', () => {
            const country = targetElement.querySelector('#salesCountry').value;
            const team = targetElement.querySelector('#salesTeam').value;
            const activity = targetElement.querySelector('#salesActivity').value;
            const transaction_filter = targetElement.querySelector('#salesTransactionType').value;
            const startDate = targetElement.querySelector('#salesStartDate').value;
            const endDate = targetElement.querySelector('#salesEndDate').value;

            const filters = {
                country, team, activity, transaction_filter,
                start_date: startDate,
                end_date: endDate
            };
            loadPageContent('sales', filters);
        });
    }

    // --- RENDU DES GRAPHIQUES AVEC PLOTLY.JS (À IMPLÉMENTER) ---
    // Cette partie est la traduction de vos st.plotly_chart en code Plotly.js direct.
    // Elle nécessite des données formatées correctement par l'API Flask.

    // Exemple de rendu de graphique simple (Pie chart pour transactions)
    if (salesData && salesData.length > 0) {
        const transactionStatusCounts = salesData.reduce((acc, sale) => {
            const status = sale.SHORT_MESSAGE || 'UNKNOWN';
            acc[status] = (acc[status] || 0) + (sale.Total_Sale || 0); // Utilise Total_Sale comme valeur
            return acc;
        }, {});

        const pieData = [{
            values: Object.values(transactionStatusCounts),
            labels: Object.keys(transactionStatusCounts),
            type: 'pie',
            hole: 0.4,
            marker: {
                colors: Object.keys(transactionStatusCounts).map(status => {
                    if (status === 'ACCEPTED') return '#007bad';
                    if (status === 'REFUSED') return '#ff0000';
                    if (status === 'ERROR') return '#ffa500';
                    return '#cccccc';
                })
            },
            textinfo: 'percent',
            textposition: 'outside',
            automargin: true
        }];

        const pieLayout = {
            title: 'Transactions Acceptées vs Refusées',
            height: 300,
            margin: { t: 40, b: 0, l: 0, r: 0 }
        };

        const transactionStatusChartDiv = targetElement.querySelector('#transactionStatusChart');
        if (transactionStatusChartDiv) {
            Plotly.newPlot(transactionStatusChartDiv, pieData, pieLayout);
        }

        // --- Pour les autres graphiques (carte, ventes par jour, ventes par heure, etc.) ---
        // Vous devrez collecter et formater les données de `salesData` de la même manière
        // et utiliser Plotly.newPlot() avec les données et le layout appropriés.
        // C'est un travail conséquent de traduction du code Plotly Express/Streamlit en Plotly.js.

        // Exemple: Ventes par Jour de la Semaine
        const salesByWeekday = salesData.reduce((acc, sale) => {
            if (sale.ORDER_DATE) {
                const date = new Date(sale.ORDER_DATE);
                const weekday = date.getDay(); // 0 (Dimanche) à 6 (Samedi)
                acc[weekday] = (acc[weekday] || 0) + (sale.Total_Sale || 0);
            }
            return acc;
        }, {});

        const daysOrder = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
        const weekdayData = [];
        const weekdayLabels = [];
        for (let i = 0; i < 7; i++) {
            weekdayLabels.push(daysOrder[i]);
            weekdayData.push(salesByWeekday[i] || 0);
        }

        const weekdayTrace = {
            x: weekdayLabels,
            y: weekdayData,
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#525CEB', width: 4 },
            marker: { size: 10, color: '#3D3B40', line: { width: 1, color: '#FFFFFF' } },
            fill: 'tozeroy',
            fillcolor: 'rgba(179, 191, 231, 0.4)',
            hovertemplate: 'Jour: %{x}<br>Ventes: €%{y:,.2f}<extra></extra>'
        };

        const weekdayLayout = {
            title: 'Ventes par Jour de la Semaine',
            height: 300,
            xaxis: { title: 'Jour de la semaine' },
            yaxis: { title: 'Ventes (€)' },
            margin: { t: 40, b: 40, l: 40, r: 20 }
        };

        const salesWeekdayChartDiv = targetElement.querySelector('#salesWeekdayChart');
        if (salesWeekdayChartDiv) {
            Plotly.newPlot(salesWeekdayChartDiv, [weekdayTrace], weekdayLayout);
        }

        // Placeholder pour la carte des ventes par ville (nécessite des coordonnées Lat/Lon dans salesData)
        const salesMapChartDiv = targetElement.querySelector('#salesMapChart');
        if (salesMapChartDiv) {
            // Vous devrez regrouper salesData par ville et s'assurer que Latitude et Longitude sont inclus
            // Puis construire un trace Plotly de type 'scattermapbox'
            salesMapChartDiv.innerHTML = '<p>Carte des ventes par ville (implémentation Plotly.js pour mapbox requise)</p>';
        }

    }
}

// Nouvelle fonction pour afficher les métriques du tableau de bord
async function displayDashboard(data, targetElement) {
    const totalSalesMetric = targetElement.querySelector('#totalSalesMetric');
    const totalRecoltsMetric = targetElement.querySelector('#totalRecoltsMetric');
    const totalLogsMetric = targetElement.querySelector('#totalLogsMetric');
    const activeAgentsMetric = targetElement.querySelector('#activeAgentsMetric');

    if (totalSalesMetric) totalSalesMetric.textContent = data.total_sales.toLocaleString();
    if (totalRecoltsMetric) totalRecoltsMetric.textContent = data.total_recolts.toLocaleString();
    if (totalLogsMetric) totalLogsMetric.textContent = data.total_logs.toLocaleString();
    if (activeAgentsMetric) activeAgentsMetric.textContent = data.active_agents.toLocaleString();
}


// Fonctions pour les autres pages (Recolts, Agents, Supports)
// Similaires à displaySales/displayLogs, vous construisez le HTML et les graphiques
// à partir des `data` reçues via l'API Flask.

function displayRecolts(recoltsData, targetElement) {
    let htmlContent = `<h2>Données de Récoltes</h2>`;
    if (recoltsData && recoltsData.length > 0) {
        htmlContent += `
            <h3 style='color: #007bad;'>Indicateurs Clés des Récoltes</h3>
            <div class="dashboard-metrics">
                <div class="metric-card">
                    <div class="metric-title">Total Récoltes</div>
                    <div class="metric-value">${recoltsData.reduce((sum, recolt) => sum + (recolt.Total_Recolt || 0), 0).toLocaleString()}€</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Transactions Récoltes</div>
                    <div class="metric-value">${recoltsData.length.toLocaleString()}</div>
                </div>
            </div>
            <h3 style='color: #007bad;'>Détails des Récoltes</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Réf. Commande</th>
                        <th>Date Commande</th>
                        <th>Total Récolte</th>
                        <th>Banques</th>
                    </tr>
                </thead>
                <tbody>
        `;
        recoltsData.forEach(recolt => {
            const orderDate = recolt.ORDER_DATE ? new Date(recolt.ORDER_DATE).toLocaleDateString() : '';
            htmlContent += `
                <tr>
                    <td>${recolt.ORDER_REFERENCE || ''}</td>
                    <td>${orderDate}</td>
                    <td>${recolt.Total_Recolt || 0}</td>
                    <td>${recolt.Banques || ''}</td>
                </tr>
            `;
        });
        htmlContent += `
                </tbody>
            </table>
        `;
    } else {
        htmlContent += `<p>Aucune donnée de récoltes trouvée.</p>`;
    }
    targetElement.innerHTML = htmlContent;
}

function displayAgents(agentsData, targetElement) {
    let htmlContent = `<h2>Gestion des Agents</h2>`;
    if (agentsData && agentsData.length > 0) {
        htmlContent += `
            <h3 style='color: #007bad;'>Vue d'ensemble des Agents</h3>
            <div class="dashboard-metrics">
                <div class="metric-card">
                    <div class="metric-title">Total Agents</div>
                    <div class="metric-value">${agentsData.length.toLocaleString()}</div>
                </div>
                <!-- Ajoutez d'autres métriques pour les agents ici -->
            </div>
            <h3 style='color: #007bad;'>Détails des Agents</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Hyp</th>
                        <th>Nom</th>
                        <th>Prénom</th>
                        <th>Équipe</th>
                        <th>Activité</th>
                        <th>Date d'entrée</th>
                    </tr>
                </thead>
                <tbody>
        `;
        agentsData.forEach(agent => {
            const dateIn = agent.Date_In ? new Date(agent.Date_In).toLocaleDateString() : '';
            htmlContent += `
                <tr>
                    <td>${agent.Hyp || ''}</td>
                    <td>${agent.NOM || ''}</td>
                    <td>${agent.PRENOM || ''}</td>
                    <td>${agent.Team || ''}</td>
                    <td>${agent.Activité || ''}</td>
                    <td>${dateIn}</td>
                </tr>
            `;
        });
        htmlContent += `
                </tbody>
            </table>
        `;
    } else {
        htmlContent += `<p>Aucune donnée d'agents trouvée.</p>`;
    }
    targetElement.innerHTML = htmlContent;
}

function displaySupports(supportsData, targetElement) {
    targetElement.innerHTML = '<h2>Gestion des Supports</h2><p>Contenu des supports à venir...</p><p>Note: Si la table "Supports" existe, assurez-vous de l\'ajouter dans la fonction load_data de Utils.py et de créer une API correspondante dans app.py. Puis, implémentez l\'affichage ici.</p>';
}
