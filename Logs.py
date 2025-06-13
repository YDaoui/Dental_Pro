import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

def logs_page1(logs_df, staff_df, start_date, end_date):
    # Ensure logs_df and staff_df are not modified outside this function
    logs_df_copy = logs_df.copy()
    staff_df_copy = staff_df.copy()

    # --- Pre-process staff_df to create 'Nom Prénom' once ---
    if 'NOM' in staff_df_copy.columns and 'PRENOM' in staff_df_copy.columns:
        staff_df_copy['Nom Prénom'] = staff_df_copy['NOM'] + ' ' + staff_df_copy['PRENOM']
    else:
        st.warning("Colonnes 'NOM' et/ou 'PRENOM' non trouvées dans les données du personnel. Utilisation de 'Hyp' si disponible.")
        if 'Hyp' in staff_df_copy.columns:
            staff_df_copy['Nom Prénom'] = staff_df_copy['Hyp']
        else:
            staff_df_copy['Nom Prénom'] = ""

    # Centered Main Title
    col1, col2 = st.columns([2, 2])
    with col1:
        st.markdown("<h1 style='text-align: left; color: #002a48; margin-bottom: 0;'>Logs Dashboard</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h1 style='text-align: right; color: #00afe1; margin-bottom: 0;'>Analyse des Logs</h1>", unsafe_allow_html=True)

  
    #st.markdown("<h2 style='text-align: center; color: #002a48;'>Filtres Avancés</h2>", unsafe_allow_html=True)

    # Filters
    col1_f, col2_f, col3_f, col4_f = st.columns(4)

    with col1_f:
        segment_options = ['Tous'] + sorted(logs_df_copy['Segment'].dropna().unique().tolist()) if 'Segment' in logs_df_copy.columns else ['Tous']
        segment_filter = st.selectbox("Segment", segment_options, key='log_segment_filter')
        
        sous_motif_options = ['Tous'] + sorted(logs_df_copy['Sous_motif'].dropna().unique().tolist()) if 'Sous_motif' in logs_df_copy.columns else ['Tous']
        sous_motif_filter = st.selectbox("Sous-motif", sous_motif_options, key='log_sous_motif_filter')

    with col2_f:
        canal_options = ['Tous'] + sorted(logs_df_copy['Canal'].dropna().unique().tolist()) if 'Canal' in logs_df_copy.columns else ['Tous']
        canal_filter = st.selectbox("Canal", canal_options, key='log_canal_filter')
        
        direction_options = ['Tous'] + sorted(logs_df_copy['Direction'].dropna().unique().tolist()) if 'Direction' in logs_df_copy.columns else ['Tous']
        direction_filter = st.selectbox("Direction", direction_options, key='log_direction_filter')

    with col3_f:
        statut_bp_options = ['Tous'] + sorted(logs_df_copy['Statut_BP'].dropna().unique().tolist()) if 'Statut_BP' in logs_df_copy.columns else ['Tous']
        statut_bp_filter = st.selectbox("Statut BP", statut_bp_options, key='log_statut_bp_filter')
        
        mode_facturation_options = ['Tous'] + sorted(logs_df_copy['Mode_facturation'].dropna().unique().tolist()) if 'Mode_facturation' in logs_df_copy.columns else ['Tous']
        mode_facturation_filter = st.selectbox("Mode de facturation", mode_facturation_options, key='log_mode_facturation_filter')

    with col4_f:
        equipe_options = ['Tous'] + sorted(staff_df_copy['Team'].dropna().unique().tolist()) if 'Team' in staff_df_copy.columns else ['Tous']
        equipe_filter = st.selectbox("Equipe", equipe_options, key='log_equipe_filter')
        
        agents_for_dropdown = ['Tous']
        if equipe_filter != 'Tous':
            filtered_staff = staff_df_copy[staff_df_copy['Team'] == equipe_filter]
            if 'Nom Prénom' in filtered_staff.columns:
                agents_for_dropdown += sorted(filtered_staff['Nom Prénom'].dropna().unique().tolist())
            elif 'Hyp' in filtered_staff.columns:
                agents_for_dropdown += sorted(filtered_staff['Hyp'].dropna().unique().tolist())
        else:
            if 'Nom Prénom' in staff_df_copy.columns:
                agents_for_dropdown += sorted(staff_df_copy['Nom Prénom'].dropna().unique().tolist())
            elif 'Hyp' in staff_df_copy.columns:
                agents_for_dropdown += sorted(staff_df_copy['Hyp'].dropna().unique().tolist())
        
        agent_filter = st.selectbox("Agent (Nom et Prénom)", agents_for_dropdown, key='log_agent_filter')

    # --- Apply filters ---
    with st.spinner("Application des filtres..."):
        filtered_logs = logs_df_copy.copy()

        # Date filtering
        if 'Date_d_création' in filtered_logs.columns and pd.api.types.is_datetime64_any_dtype(filtered_logs['Date_d_création']):
            filtered_logs = filtered_logs[
                (filtered_logs['Date_d_création'].dt.date >= start_date) & 
                (filtered_logs['Date_d_création'].dt.date <= end_date)
            ]
        else:
            st.warning("La colonne 'Date_d_création' n'est pas au format datetime ou est manquante. Le filtrage par date ne sera pas appliqué.")
            filtered_logs = pd.DataFrame(columns=logs_df_copy.columns) # Empty df if date col is problematic

        # Other filters
        if segment_filter != 'Tous' and 'Segment' in filtered_logs.columns:
            filtered_logs = filtered_logs[filtered_logs['Segment'] == segment_filter]
        if sous_motif_filter != 'Tous' and 'Sous_motif' in filtered_logs.columns:
            filtered_logs = filtered_logs[filtered_logs['Sous_motif'] == sous_motif_filter]
        if canal_filter != 'Tous' and 'Canal' in filtered_logs.columns:
            filtered_logs = filtered_logs[filtered_logs['Canal'] == canal_filter]
        if direction_filter != 'Tous' and 'Direction' in filtered_logs.columns:
            filtered_logs = filtered_logs[filtered_logs['Direction'] == direction_filter]
        if statut_bp_filter != 'Tous' and 'Statut_BP' in filtered_logs.columns:
            filtered_logs = filtered_logs[filtered_logs['Statut_BP'] == statut_bp_filter]
        if mode_facturation_filter != 'Tous' and 'Mode_facturation' in filtered_logs.columns:
            filtered_logs = filtered_logs[filtered_logs['Mode_facturation'] == mode_facturation_filter]

        # Apply Equipe and Agent filters
        if 'Hyp' in filtered_logs.columns and not staff_df_copy.empty and 'Hyp' in staff_df_copy.columns:
            temp_staff_df = staff_df_copy.copy()
            if equipe_filter != 'Tous' and 'Team' in temp_staff_df.columns:
                temp_staff_df = temp_staff_df[temp_staff_df['Team'] == equipe_filter]
            if agent_filter != 'Tous':
                if 'Nom Prénom' in temp_staff_df.columns and agent_filter in temp_staff_df['Nom Prénom'].unique():
                    temp_staff_df = temp_staff_df[temp_staff_df['Nom Prénom'] == agent_filter]
                elif 'Hyp' in temp_staff_df.columns and agent_filter in temp_staff_df['Hyp'].unique():
                    temp_staff_df = temp_staff_df[temp_staff_df['Hyp'] == agent_filter]
            
            if not temp_staff_df.empty and 'Hyp' in temp_staff_df.columns:
                filtered_logs = filtered_logs[filtered_logs['Hyp'].isin(temp_staff_df['Hyp'])]
            else:
                # If agent/team filter leads to no staff, then no logs should be shown
                filtered_logs = pd.DataFrame(columns=filtered_logs.columns)
        elif agent_filter != 'Tous' or equipe_filter != 'Tous':
             st.warning("La colonne 'Hyp' est manquante dans les logs ou les données du personnel pour appliquer les filtres Agent/Équipe.")
             filtered_logs = pd.DataFrame(columns=filtered_logs.columns) # No agent/team filtering possible

  

    if not filtered_logs.empty:
        # --- KPIs Section ---
        #st.markdown("<h2 style='text-align: center; color: #002a48;'>Indicateurs Clés</h2>", unsafe_allow_html=True)
        col1_kpi, col2_kpi, col3_kpi, col4_kpi = st.columns(4)

        total_logs = len(filtered_logs)
        unique_clients = filtered_logs['BP_Logs'].nunique() if 'BP_Logs' in filtered_logs.columns else 0
        avg_logs_per_client = round(total_logs / unique_clients, 2) if unique_clients > 0 else 0

        quality_of_service_value = "N/A"
        if 'Statut_BP' in filtered_logs.columns and total_logs > 0:
            successful_logs_count = filtered_logs[filtered_logs['Statut_BP'].isin(['Validé', 'Terminé'])].shape[0]
            quality_of_service_value = f"{(successful_logs_count / total_logs) * 100:.2f}%" if total_logs > 0 else "0.00%"

        incomming_percent = outcomming_percent = 0.0
        if 'Direction' in filtered_logs.columns and total_logs > 0:
            incomming_count = filtered_logs[filtered_logs['Direction'] == 'InComming'].shape[0]
            outcomming_count = filtered_logs[filtered_logs['Direction'] == 'OutComming'].shape[0]
            incomming_percent = (incomming_count / total_logs) * 100
            outcomming_percent = (outcomming_count / total_logs) * 100

        combined_quality_direction_value = f"<span style='color:white;'>In: {incomming_percent:.2f}%</span> / " \
                                         f"<span style='color:white;'>Out: {outcomming_percent:.2f}%</span>"

        def kpi_card_html(column, title, value_html, color, icon_name):
            column.markdown(f"""
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
                <div style="
                    padding: 20px;
                    background: linear-gradient(165deg, {color} 0%, {color}CC 100%);
                    border-radius: 12px;
                    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
                    height: 140px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    border-left: 8px solid {color}EE;
                    position: relative;
                    overflow: hidden;
                    color: white;">
                    <div style="position: absolute; right: 20px; top: 20px; opacity: 0.9;">
                        <i class="fas fa-{icon_name}" style="font-size: 40px;"></i>
                    </div>
                    <h3 style="color: white; margin: 0 0 10px 0; font-size: 24px; font-weight: 600;">{title}</h3>
                    <p style="font-size: 40px; color: white; font-weight: 700; margin: 0;">{value_html}</p>
                </div>
            """, unsafe_allow_html=True)

        kpi_card_html(col1_kpi, "Total Logs", f"{total_logs:,}", "#043a64", "file-alt")
        kpi_card_html(col2_kpi, "Clients Uniques", f"{unique_clients:,}", "#2596be", "users")
        kpi_card_html(col3_kpi, "Moyenne Logs/Client", f"{avg_logs_per_client:.2f}", "#fcd25b", "chart-line")
        kpi_card_html(col4_kpi, "Qualité de Services", combined_quality_direction_value, "#fc9307", "exchange-alt")

       
        st.markdown("<h2 style='text-align: center; color: #002a48;'>Analyses Principales</h2>", unsafe_allow_html=True)

        # Common layout configuration - Potential source of error
        # Ensure all keys and values are valid for plotly.graph_objs.Layout
        common_layout = dict(
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='x unified',
            xaxis=dict(
                title="", # Title can be an empty string, not None
                tickfont=dict(size=14, family='Arial', color='black'),
                titlefont=dict(size=16),
                showgrid=True,
                gridcolor='#e0e0e0',
                linecolor='black',
                linewidth=1
            ),
            yaxis=dict(
                title="", # Title can be an empty string, not None
                tickfont=dict(size=14, family='Arial', color='black'),
                titlefont=dict(size=16),
                showgrid=True,
                gridcolor='#e0e0e0',
                linecolor='black',
                linewidth=1
            ),
            uniformtext=dict(
                minsize=14, # minsize should be int
                mode='hide' # mode should be 'hide' or 'overlay'
            ),
            font=dict(size=14, color='#333', family='Arial'),
            # Adding margin might help with text clipping, adjust as needed
            margin=dict(l=40, r=40, t=40, b=40) 
        )

        # First row of charts
        col1_g, col2_g, col3_g = st.columns(3)

        with col1_g:
            st.markdown("<h3 style='color: #007bad;'>Volume de Logs par Mois</h3>", unsafe_allow_html=True)
            if 'Date_d_création' in filtered_logs.columns:
                logs_per_period = filtered_logs.copy()
                logs_per_period['Mois'] = logs_per_period['Date_d_création'].dt.to_period('M')
                monthly_data = logs_per_period.groupby('Mois').size().reset_index(name='Count')
                monthly_data['Mois_dt'] = monthly_data['Mois'].dt.to_timestamp()
                monthly_data = monthly_data.sort_values('Mois_dt')
                monthly_data['Mois_Nom'] = monthly_data['Mois_dt'].dt.strftime('%B %Y').apply(lambda x: x.replace(
                    'January', 'Janvier').replace('February', 'Février').replace('March', 'Mars').replace('April', 'Avril')
                    .replace('May', 'Mai').replace('June', 'Juin').replace('July', 'Juillet').replace('August', 'Août')
                    .replace('September', 'Septembre').replace('October', 'Octobre').replace('November', 'Novembre')
                    .replace('December', 'Décembre'))

                fig_month = px.line(monthly_data, x='Mois_Nom', y='Count',
                                    color_discrete_sequence=['#4ecdc4'],
                                    markers=True,
                                    line_shape='spline',
                                    text='Count')
                fig_month.update_traces(
                    mode='lines+markers+text',
                    marker=dict(size=10, symbol='circle', line=dict(width=2, color='DarkSlateGrey')),
                    hovertemplate='<b>Mois:</b> %{x}<br><b>Logs:</b> %{y:,}<extra></extra>',
                    textposition="top center",
                    textfont=dict(size=14, color='black', family='Arial', weight='bold'),
                    fill='tozeroy',
                    fillcolor='rgba(78, 205, 196, 0.2)'
                )
                try:
                    # Apply common layout
                    fig_month.update_layout(common_layout)
                    # Specific updates for this chart
                    #fig_month.update_xaxes(title="Mois", automargin=True)
                    #fig_month.update_yaxes(title="Nombre de Logs", automargin=True)
                    st.plotly_chart(fig_month, use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur lors de la création du graphique mensuel : {e}")
                    st.info("Impossible d'afficher le graphique mensuel.")
            else:
                st.info("La colonne 'Date_d_création' n'est pas disponible.")

        with col2_g:
            st.markdown("<h3 style='color: #007bad;'>Distribution Horaire des Logs (8H à 23H)</h3>", unsafe_allow_html=True)
            if 'Heure_création' in filtered_logs.columns:
                try:
                    # Convertir l'heure en format datetime, puis extraire l'heure
                    # Prioritize exact format, then more flexible parsing
                    filtered_logs['Heure'] = pd.to_datetime(filtered_logs['Heure_création'], format='%H:%M:%S.%f', errors='coerce').dt.hour
                    filtered_logs.loc[filtered_logs['Heure'].isnull(), 'Heure'] = pd.to_datetime(filtered_logs['Heure_création'], format='%H:%M:%S', errors='coerce').dt.hour
                except Exception as e:
                    st.warning(f"Erreur de conversion de l'heure : {str(e)}. Essai d'utiliser 'Date_d_création'.")
                    if 'Date_d_création' in filtered_logs.columns:
                        filtered_logs['Heure'] = filtered_logs['Date_d_création'].dt.hour
                    else:
                        filtered_logs['Heure'] = np.nan
            else:
                if 'Date_d_création' in filtered_logs.columns:
                    filtered_logs['Heure'] = filtered_logs['Date_d_création'].dt.hour
                else:
                    filtered_logs['Heure'] = np.nan

            if 'Heure' in filtered_logs.columns and not filtered_logs['Heure'].isnull().all():
                hourly_data = filtered_logs[(filtered_logs['Heure'] >= 8) & (filtered_logs['Heure'] <= 23)]
                hourly_data = hourly_data.groupby('Heure').size().reset_index(name='Count')
                hourly_data = hourly_data.sort_values('Heure')

                all_hours = pd.DataFrame({'Heure': range(8, 24)})
                hourly_data = pd.merge(all_hours, hourly_data, on='Heure', how='left').fillna(0)

                fig_hour = px.line(hourly_data, x='Heure', y='Count',
                                    color_discrete_sequence=['#fcd25b'],
                                    markers=True,
                                    line_shape='spline',
                                    text='Count')
                fig_hour.update_traces(
                    mode='lines+markers+text',
                    marker=dict(size=10, symbol='circle', line=dict(width=2, color='DarkSlateGrey')),
                    hovertemplate='<b>Heure:</b> %{x}H<br><b>Logs:</b> %{y:,}<extra></extra>',
                    textposition="top center",
                    textfont=dict(size=14, color='black', family='Arial', weight='bold'),
                    fill='tozeroy',
                    fillcolor='rgba(252, 210, 91, 0.2)'
                )
                try:
                    fig_hour.update_layout(common_layout)
                    #fig_hour.update_xaxes(title="Heure (H)", tickvals=list(range(8, 24, 1)), automargin=True)
                    #fig_hour.update_yaxes(title="Nombre de Logs", automargin=True)
                    st.plotly_chart(fig_hour, use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur lors de la création du graphique horaire : {e}")
                    st.info("Impossible d'afficher le graphique horaire.")
            else:
                st.info("Données horaires non disponibles.")

        with col3_g:
            st.markdown("<h3 style='color: #007bad;'>Volume de Logs par Jour</h3>", unsafe_allow_html=True)
            if 'Date_d_création' in filtered_logs.columns:
                jours = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi',
                                3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}
                weekday_order = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
                filtered_logs['Jour'] = filtered_logs['Date_d_création'].dt.weekday.map(jours)
                weekday_data = filtered_logs.groupby('Jour').size().reset_index(name='Count')

                all_days_df = pd.DataFrame({'Jour': weekday_order})
                weekday_data = pd.merge(all_days_df, weekday_data, on='Jour', how='left').fillna(0)
                weekday_data['Jour'] = pd.Categorical(weekday_data['Jour'], categories=weekday_order, ordered=True)
                weekday_data = weekday_data.sort_values('Jour')

                fig_day = px.line(weekday_data, x='Jour', y='Count',
                                    color_discrete_sequence=['#ff6b6b'],
                                    markers=True,
                                    line_shape='spline',
                                    text='Count')
                fig_day.update_traces(
                    mode='lines+markers+text',
                    marker=dict(size=10, symbol='circle', line=dict(width=2, color='DarkSlateGrey')),
                    hovertemplate='<b>Jour:</b> %{x}<br><b>Logs:</b> %{y:,}<extra></extra>',
                    textposition="top center",
                    textfont=dict(size=14, color='black', family='Arial', weight='bold'),
                    fill='tozeroy',
                    fillcolor='rgba(255, 107, 107, 0.2)'
                )
                try:
                    fig_day.update_layout(common_layout)
                    #fig_day.update_xaxes(title="Jour", automargin=True)
                    #fig_day.update_yaxes(title="Nombre de Logs", automargin=True)
                    st.plotly_chart(fig_day, use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur lors de la création du graphique par jour : {e}")
                    st.info("Impossible d'afficher le graphique par jour.")
            else:
                st.info("La colonne 'Date_d_création' n'est pas disponible.")

      
        col1_b, col2_b, col3_b = st.columns(3)

        # Bar chart for segments
        with col1_b:
    
            st.markdown("<h3 style='color: #007bad;'>Répartition par Segment</h3>", unsafe_allow_html=True)
            if 'Segment' in filtered_logs.columns:
                segment_data = filtered_logs.groupby('Segment').size().reset_index(name='Count')
                total = segment_data['Count'].sum()
                segment_data['Percentage'] = (segment_data['Count'] / total * 100).round(1)
                fig_segment = px.bar(segment_data, x='Count', y='Segment',
                                        orientation='h',
                                        color='Count',
                                        color_continuous_scale='Blues',
                                        text=[f'{count:,}<br>({perc}%)' for count, perc in zip(segment_data['Count'], segment_data['Percentage'])])
                fig_segment.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    textfont=dict(size=18, family='Arial', color='black')
                )
                updated_layout = {
                    **common_layout,
                    'yaxis': {
                        **common_layout['yaxis'],
                        'categoryorder': 'total ascending',
                        'tickfont': {'size': 14, 'weight': 'bold', 'family': 'Arial'},
                        'title_font': {'size': 16, 'weight': 'bold', 'family': 'Arial'}
                    },
                    'xaxis': { # Added to hide x-axis
                        'visible': False,
                        'showticklabels': False
                    },
                    'showlegend': False,
                    'coloraxis_showscale': False,
                    'font': {'family': 'Arial', 'size': 14, 'weight': 'bold'},
                    'margin': {'r': 50 }
                    }
                try:
                    fig_segment.update_layout(updated_layout)
                    st.plotly_chart(fig_segment, use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur lors de la création du graphique par segment : {e}")
                    st.info("Impossible d'afficher le graphique par segment.")
            else:
                st.info("La colonne 'Segment' est manquante.")

        with col2_b:
            st.markdown("<h3 style='color: #007bad;'>Logs par Canal</h3>", unsafe_allow_html=True)
            if 'Canal' in filtered_logs.columns:
                canal_data = filtered_logs.groupby('Canal').size().reset_index(name='Count')
                total = canal_data['Count'].sum()
                canal_data['Percentage'] = (canal_data['Count'] / total * 100).round(1)
                fig_canal = px.bar(canal_data, x='Count', y='Canal',
                                orientation='h',
                                color='Count',
                                color_continuous_scale='Blues',
                                text=[f'{count:,}<br>({perc}%)' for count, perc in zip(canal_data['Count'], canal_data['Percentage'])])
                fig_canal.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    textfont=dict(size=18, family='Arial', color='black')
                )
                updated_layout = {
                    **common_layout,
                    'yaxis': {
                        **common_layout['yaxis'],
                        'categoryorder': 'total ascending',
                        'tickfont': {'size': 14, 'weight': 'bold', 'family': 'Arial'},
                        'title_font': {'size': 16, 'weight': 'bold', 'family': 'Arial'}
                    },
                    'xaxis': { # Added to hide x-axis
                        'visible': False,
                        'showticklabels': False
                    },
                    'showlegend': False,
                    'coloraxis_showscale': False,
                    'font': {'family': 'Arial', 'size': 14, 'weight': 'bold'}
                }
                try:
                    fig_canal.update_layout(updated_layout)
                    st.plotly_chart(fig_canal, use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur lors de la création du graphique par canal : {e}")
                    st.info("Impossible d'afficher le graphique par canal.")
            else:
                st.info("La colonne 'Canal' est manquante.")

        with col3_b:
            st.markdown("<h3 style='color: #007bad;'>Top 10 Sous-motifs</h3>", unsafe_allow_html=True)
            if 'Sous_motif' in filtered_logs.columns:
                sous_motif_data = filtered_logs.groupby('Sous_motif').size().reset_index(name='Count')
                total = sous_motif_data['Count'].sum()
                top_motifs = sous_motif_data.sort_values('Count', ascending=True).tail(10)
                top_motifs['Percentage'] = (top_motifs['Count'] / total * 100).round(1)

                max_count_motif = top_motifs['Count'].max()
                # Crucially, ensure enough space on the x-axis for text
                x_axis_range_motif = [0, max_count_motif * 1.2] # Increased buffer for more space

                fig_motif = px.bar(top_motifs, x='Count', y='Sous_motif',
                                    orientation='h',
                                    color='Count',
                                    color_continuous_scale='Blues',
                                    text=[f'{count:,}<br>({perc}%)' for count, perc in zip(top_motifs['Count'], top_motifs['Percentage'])])
                fig_motif.update_traces(
                    texttemplate='%{text}',
                    textposition='outside', # Set to 'outside' for persistent visibility
                    textfont=dict(size=18, family='Arial', color='black'),
                    cliponaxis=True # Added this to prevent clipping if labels extend beyond plot area
                )
                updated_layout_motif = { # Renamed to avoid clash
                    **common_layout,
                    'yaxis': {
                        **common_layout['yaxis'],
                        'categoryorder': 'total ascending',
                        'tickfont': {'size': 14, 'weight': 'bold', 'family': 'Arial'},
                        'title_font': {'size': 16, 'weight': 'bold', 'family': 'Arial'}
                    },
                    'xaxis': { # Hide x-axis and set range
                        'visible': False,
                        'showticklabels': False,
                        'range': x_axis_range_motif
                    },
                    'showlegend': False,
                    'coloraxis_showscale': False,
                    'font': {'family': 'Arial', 'size': 14, 'weight': 'bold'}
                }
                try:
                    fig_motif.update_layout(updated_layout_motif)
                    st.plotly_chart(fig_motif, use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur lors de la création du graphique des sous-motifs : {e}")
                    st.info("Impossible d'afficher le graphique des sous-motifs.")
            else:
                st.info("La colonne 'Sous_motif' est manquante.")
            

        with col3_b:
            st.markdown("<h3 style='color: #007bad;'>Mode de Facturation</h3>", unsafe_allow_html=True)
            if 'Mode_facturation' in filtered_logs.columns:
                facturation_data = filtered_logs.groupby('Mode_facturation').size().reset_index(name='Count')
                total = facturation_data['Count'].sum()
                facturation_data['Percentage'] = (facturation_data['Count'] / total * 100).round(1)
                fig_facturation = px.bar(facturation_data, x='Count', y='Mode_facturation',
                                            orientation='h',
                                            color='Count',
                                            color_continuous_scale='Blues',
                                            text=[f'{count:,}<br>({perc}%)' for count, perc in zip(facturation_data['Count'], facturation_data['Percentage'])])
                fig_facturation.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    textfont=dict(size=20, family='Arial', color='black')
                )
                updated_layout = {
                    **common_layout,
                    'yaxis': {
                        **common_layout['yaxis'],
                        'categoryorder': 'total ascending',
                        'tickfont': {'size': 14, 'weight': 'bold', 'family': 'Arial'},
                        'title_font': {'size': 16, 'weight': 'bold', 'family': 'Arial'}
                    },
                    'xaxis': { # Added to hide x-axis
                        'visible': False,
                        'showticklabels': False
                    },
                    'showlegend': False,
                    'coloraxis_showscale': False,
                    'font': {'family': 'Arial', 'size': 14, 'weight': 'bold'}
                }
                try:
                    fig_facturation.update_layout(updated_layout)
                    st.plotly_chart(fig_facturation, use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur lors de la création du graphique de mode de facturation : {e}")
                    st.info("Impossible d'afficher le graphique de mode de facturation.")
            else:
                st.info("La colonne 'Mode_facturation' est manquante.")

        st.markdown("<h2 style='text-align: center; color: #002a48; font-weight: bold;'>Détails des Logs</h2>", unsafe_allow_html=True)

        # Display columns
        display_cols = [
            'Date_d_création', 'Heure_création', 'Segment', 'Canal',
            'Sous_motif', 'Statut_BP', 'Offre', 'Mode_facturation',
            'Anciennete_client', 'Total', 'Hyp'
        ]
        available_cols = [col for col in display_cols if col in filtered_logs.columns]
        display_df = filtered_logs[available_cols].copy()

        # Merge with staff data
        if 'Hyp' in display_df.columns and not staff_df_copy.empty and 'Hyp' in staff_df_copy.columns:
            staff_cols_to_merge = ['Hyp']
            if 'Nom Prénom' in staff_df_copy.columns:
                staff_cols_to_merge.append('Nom Prénom')
            if 'Team' in staff_df_copy.columns:
                staff_cols_to_merge.append('Team')

            # Ensure 'Hyp' column from staff_df_copy is unique before merging to avoid duplicates
            display_df = display_df.merge(staff_df_copy[staff_cols_to_merge].drop_duplicates(subset=['Hyp']), on='Hyp', how='left')
            if 'Nom Prénom' in display_df.columns:
                display_df.rename(columns={'Nom Prénom': 'Nom Prénom Agent'}, inplace=True)
            if 'Team' in display_df.columns:
                display_df.rename(columns={'Team': 'Equipe Agent'}, inplace=True)

            cols_to_order = ['Date_d_création', 'Heure_création']
            if 'Nom Prénom Agent' in display_df.columns:
                cols_to_order.append('Nom Prénom Agent')
            if 'Equipe Agent' in display_df.columns:
                cols_to_order.append('Equipe Agent')

            remaining_cols = [col for col in display_df.columns if col not in cols_to_order and col != 'Hyp']
            display_df = display_df[cols_to_order + remaining_cols]

        # Format datetime
        if 'Date_d_création' in display_df.columns and pd.api.types.is_datetime64_any_dtype(display_df['Date_d_création']):
            display_df['Date_d_création'] = display_df['Date_d_création'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Format Heure_création for display if it exists and is not a datetime object
        if 'Heure_création' in display_df.columns and not pd.api.types.is_datetime64_any_dtype(display_df['Heure_création']):
            display_df['Heure_création'] = display_df['Heure_création'].astype(str) # Ensure it's string for display if not parsed as datetime
        
        # Display column counts
        st.markdown("<h3 style='color: #002a48;'>Nombre de valeurs par colonne:</h3>", unsafe_allow_html=True)
        # Use a more flexible column layout for counts
        num_cols = len(display_df.columns)
        num_cols_per_row = min(num_cols, 6) # Max 6 columns per row for display
        cols_for_counts = st.columns(num_cols_per_row)
        for i, col_name in enumerate(display_df.columns):
            with cols_for_counts[i % num_cols_per_row]:
                count = display_df[col_name].count()
                st.markdown(
                    f"<div style='text-align: center; font-weight: bold; font-size: 14px; color: #007bad;'>"
                    f"{col_name}<br>({count})</div>",
                    unsafe_allow_html=True
                )
        

        # Display dataframe
        st.markdown(
            """
            <style>
            .dataframe {
                font-weight: bold;
                font-size: 16px;
            }
            .dataframe th {
                font-size: 18px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.dataframe(
            display_df.style
                .background_gradient(cmap='Blues', subset=['Total'] if 'Total' in display_df.columns else [])
                .format({'Total': '{:.2f} €'}, na_rep="N/A"),
            use_container_width=True,
            height=500
        )

        # Download button
        csv = display_df.to_csv(index=False, sep=';').encode('utf-8')
        st.download_button(
            label="Télécharger les données filtrées",
            data=csv,
            file_name=f"logs_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )

    else:
        st.warning("Aucune donnée ne correspond aux critères sélectionnés. Veuillez ajuster vos filtres.")