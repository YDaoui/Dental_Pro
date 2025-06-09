import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

# Define logs_page1 to accept staff_df
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

def logs_page1(logs_df, staff_df, start_date, end_date):
    # --- Pre-process staff_df to create 'Nom Prénom' once ---
    if 'NOM' in staff_df.columns and 'PRENOM' in staff_df.columns:
        staff_df['Nom Prénom'] = staff_df['NOM'] + ' ' + staff_df['PRENOM']
    else:
        st.warning("Colonnes 'NOM' et/ou 'PRENOM' non trouvées dans les données du personnel. Le filtre Agent pourrait ne pas fonctionner comme prévu.")
        staff_df['Nom Prénom'] = staff_df['Hyp'] # Fallback for display if names aren't available

    # Centered Main Title with improved styling
    col1, col2 = st.columns([2, 2])
    with col1:
        st.markdown(
            "<h1 style='text-align: left; color: #002a48; margin-bottom: 0;'>Logs Dashboard</h1>",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            "<h1 style='text-align: right; color: #00afe1; margin-bottom: 0;'>Analyse des Logs</h1>",
            unsafe_allow_html=True
        )

    col1_f, col2_f, col3_f, col4_f = st.columns(4)

    with col1_f:
        segment_filter = st.selectbox(
            "Segment",
            ['Tous'] + sorted(logs_df['Segment'].dropna().unique()),
            key='log_segment_filter'
        )
        sous_motif_filter = st.selectbox(
            "Sous-motif",
            ['Tous'] + sorted(logs_df['Sous_motif'].dropna().unique()),
            key='log_sous_motif_filter'
        )

    with col2_f:
        canal_filter = st.selectbox(
            "Canal",
            ['Tous'] + sorted(logs_df['Canal'].dropna().unique()),
            key='log_canal_filter'
        )
        direction_filter = st.selectbox(
            "Direction",
            ['Tous'] + sorted(logs_df['Direction'].dropna().unique()),
            key='log_direction_filter'
        )

    with col3_f:
        statut_bp_filter = st.selectbox(
            "Statut BP",
            ['Tous'] + sorted(logs_df['Statut_BP'].dropna().unique()),
            key='log_statut_bp_filter'
        )
        mode_facturation_filter = st.selectbox(
            "Mode de facturation",
            ['Tous'] + sorted(logs_df['Mode_facturation'].dropna().unique()),
            key='log_mode_facturation_filter'
        )

    with col4_f:
        equipe_filter = st.selectbox(
            "Equipe",
            ['Tous'] + sorted(staff_df['Team'].dropna().unique()) if 'Team' in staff_df.columns else ['Tous'],
            key='log_equipe_filter'
        )

        agents_for_dropdown = ['Tous']
        if equipe_filter != 'Tous':
            filtered_staff_for_dropdown = staff_df[staff_df['Team'] == equipe_filter]
            if 'Nom Prénom' in filtered_staff_for_dropdown.columns:
                agents_for_dropdown += sorted(filtered_staff_for_dropdown['Nom Prénom'].dropna().unique())
            elif 'Hyp' in filtered_staff_for_dropdown.columns:
                agents_for_dropdown += sorted(filtered_staff_for_dropdown['Hyp'].dropna().unique())
        else:
            if 'Nom Prénom' in staff_df.columns:
                agents_for_dropdown += sorted(staff_df['Nom Prénom'].dropna().unique())
            elif 'Hyp' in staff_df.columns:
                agents_for_dropdown += sorted(staff_df['Hyp'].dropna().unique())

        agent_filter = st.selectbox(
            "Agent (Nom et Prénom)",
            agents_for_dropdown,
            key='log_agent_filter'
        )

    # --- Apply filters ---
    with st.spinner("Application des filtres..."):
        filtered_logs = logs_df.copy()

        if 'Date_d_création' in filtered_logs.columns:
            filtered_logs['Date_d_création'] = pd.to_datetime(filtered_logs['Date_d_création'])
            filtered_logs = filtered_logs[
                (filtered_logs['Date_d_création'] >= pd.to_datetime(start_date)) &
                (filtered_logs['Date_d_création'] <= pd.to_datetime(end_date))
            ]

        if segment_filter != 'Tous':
            filtered_logs = filtered_logs[filtered_logs['Segment'] == segment_filter]
        if sous_motif_filter != 'Tous':
            filtered_logs = filtered_logs[filtered_logs['Sous_motif'] == sous_motif_filter]
        if canal_filter != 'Tous':
            filtered_logs = filtered_logs[filtered_logs['Canal'] == canal_filter]
        if direction_filter != 'Tous':
            filtered_logs = filtered_logs[filtered_logs['Direction'] == direction_filter]
        if statut_bp_filter != 'Tous':
            filtered_logs = filtered_logs[filtered_logs['Statut_BP'] == statut_bp_filter]
        if mode_facturation_filter != 'Tous':
            filtered_logs = filtered_logs[filtered_logs['Mode_facturation'] == mode_facturation_filter]

        if 'Hyp' in logs_df.columns and not staff_df.empty:
            temp_staff_df = staff_df.copy()

            if equipe_filter != 'Tous':
                temp_staff_df = temp_staff_df[temp_staff_df['Team'] == equipe_filter]

            if agent_filter != 'Tous':
                if 'Nom Prénom' in temp_staff_df.columns and agent_filter in temp_staff_df['Nom Prénom'].unique():
                    temp_staff_df = temp_staff_df[temp_staff_df['Nom Prénom'] == agent_filter]
                elif 'Hyp' in temp_staff_df.columns and agent_filter in temp_staff_df['Hyp'].unique():
                    temp_staff_df = temp_staff_df[temp_staff_df['Hyp'] == agent_filter]

            if 'Hyp' in temp_staff_df.columns:
                filtered_logs = filtered_logs[filtered_logs['Hyp'].isin(temp_staff_df['Hyp'])]
            else:
                st.warning("La colonne 'Hyp' est manquante dans les données du personnel, le filtrage par agent/équipe sera limité.")

    if not filtered_logs.empty:
        # --- Enhanced KPIs Section ---
        st.markdown("<h2 style='text-align: center; color: #002a48;'>Indicateurs Clés</h2>", unsafe_allow_html=True)
        col1_kpi, col2_kpi, col3_kpi, col4_kpi = st.columns(4)

        total_logs = len(filtered_logs)
        unique_clients = filtered_logs['BP_Logs'].nunique() if 'BP_Logs' in filtered_logs.columns else 0
        avg_logs_per_client = round(total_logs / unique_clients, 2) if unique_clients > 0 else 0

        unique_clients_percentage = (unique_clients / total_logs * 100) if total_logs > 0 else 0
        avg_logs_per_client_percentage = (avg_logs_per_client / total_logs * 100) if total_logs > 0 else 0

        quality_of_service_value = "N/A"
        if 'Statut_BP' in filtered_logs.columns and total_logs > 0:
            successful_logs_count = filtered_logs[filtered_logs['Statut_BP'].isin(['Validé', 'Terminé'])].shape[0]
            quality_of_service_value = (successful_logs_count / total_logs) * 100
            quality_of_service_value = f"{quality_of_service_value:.2f}%"

        incomming_percent = 0.0
        outcomming_percent = 0.0
        if 'Direction' in filtered_logs.columns and total_logs > 0:
            incomming_count = filtered_logs[filtered_logs['Direction'] == 'InComming'].shape[0]
            outcomming_count = filtered_logs[filtered_logs['Direction'] == 'OutComming'].shape[0]
            incomming_percent = (incomming_count / total_logs) * 100
            outcomming_percent = (outcomming_count / total_logs) * 100

        combined_quality_direction_value = f"<span style='color:blue;'>In: {incomming_percent:.2f}%</span> / " \
                                         f"<span style='color:blue;'>Out: {outcomming_percent:.2f}%</span>"

        def kpi_card_html(column, title, value_html, color, icon_name):
            column.markdown(f"""
                <div style="
                    padding: 20px;
                    background: linear-gradient(145deg, {color} 0%, {color}CC 100%);
                    border-radius: 12px;
                    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
                    height: 140px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    border-left: 8px solid {color}EE;
                    position: relative;
                    overflow: hidden;
                    color: white;
                    ">
                    <div style="position: absolute; right: 20px; top: 20px; opacity: 0.3;">
                        <i class="fas fa-{icon_name}" style="font-size: 65px;"></i>
                    </div>
                    <h3 style="color: white; margin: 0 0 10px 0; font-size: 24px; font-weight: 600;">{title}</h3>
                    <p style="font-size: 42px; color: white; font-weight: 700; margin: 0;">{value_html}</p>
                </div>
            """, unsafe_allow_html=True)

        kpi_card_html(col1_kpi, "Total Logs", f"{total_logs:,}", "#1a535c", "file-alt")
        kpi_card_html(col2_kpi, "Clients Uniques",
                                f"{unique_clients:,} <span style='font-size: 20px;'>({unique_clients_percentage:.2f}%)</span>",
                                "#4ecdc4", "users")
        kpi_card_html(col3_kpi, "Moyenne Logs/Client",
                                f"{avg_logs_per_client:.2f} <span style='font-size: 20px;'>({avg_logs_per_client_percentage:.2f}%)</span>",
                                "#fcd25b", "chart-line")
        kpi_card_html(col4_kpi, "Qualité de Services", combined_quality_direction_value, "#ff6b6b", "exchange-alt")

        st.markdown("<h2 style='text-align: center; color: #002a48;'>Analyses Principales</h2>", unsafe_allow_html=True)

        # Simplified common layout configuration
        common_layout = {
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'hovermode': 'x unified',
            'font': {'size': 14, 'color': '#333'},
            'xaxis': {
                'showgrid': True,
                'gridcolor': '#e0e0e0',
                'linecolor': 'black',
                'linewidth': 1
            },
            'yaxis': {
                'showgrid': True,
                'gridcolor': '#e0e0e0',
                'linecolor': 'black',
                'linewidth': 1
            }
        }

        # First row of charts
        col1_g, col2_g, col3_g = st.columns(3)

        with col1_g:
            st.markdown("<h3 style='color: #007bad;'>Volume de Logs par Mois</h3>", unsafe_allow_html=True)
            logs_per_period = filtered_logs.copy()
            logs_per_period['Mois'] = logs_per_period['Date_d_création'].dt.to_period('M')
            monthly_data = logs_per_period.groupby('Mois').size().reset_index(name='Count')
            monthly_data['Mois_dt'] = monthly_data['Mois'].dt.to_timestamp()
            monthly_data = monthly_data.sort_values('Mois_dt')
            monthly_data['Mois_Nom'] = monthly_data['Mois_dt'].dt.strftime('%B %Y').apply(lambda x: x.replace(
                'January', 'Janvier').replace('February', 'Février').replace('March', 'Mars').replace('April', 'Avril').replace('May', 'Mai').replace('June', 'Juin').replace('July', 'Juillet').replace('August', 'Août').replace('September', 'Septembre').replace('October', 'Octobre').replace('November', 'Novembre').replace('December', 'Décembre')
            )

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
                textfont=dict(size=14, color='black', family='Arial'),
                fill='tozeroy',
                fillcolor='rgba(78, 205, 196, 0.2)'
            )
            fig_month.update_layout(**common_layout)
            fig_month.update_xaxes(title="Mois")
            fig_month.update_yaxes(title="Nombre de Logs")
            st.plotly_chart(fig_month, use_container_width=True)

        with col2_g:
            st.markdown("<h3 style='color: #007bad;'>Distribution Horaire des Logs (8H à 23H)</h3>", unsafe_allow_html=True)
            if 'Heure_création' in filtered_logs.columns:
                filtered_logs['Heure'] = pd.to_datetime(filtered_logs['Heure_création'], format='%H:%M:%S.%f').dt.hour
            else:
                filtered_logs['Heure'] = filtered_logs['Date_d_création'].dt.hour

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
                textfont=dict(size=14, color='black', family='Arial'),
                fill='tozeroy',
                fillcolor='rgba(252, 210, 91, 0.2)'
            )
            fig_hour.update_layout(**common_layout)
            fig_hour.update_xaxes(title="Heure (H)", tickvals=list(range(8, 24, 1)))
            fig_hour.update_yaxes(title="Nombre de Logs")
            st.plotly_chart(fig_hour, use_container_width=True)

        with col3_g:
            st.markdown("<h3 style='color: #007bad;'>Volume de Logs par Jour</h3>", unsafe_allow_html=True)
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
                textfont=dict(size=14, color='black', family='Arial'),
                fill='tozeroy',
                fillcolor='rgba(255, 107, 107, 0.2)'
            )
            fig_day.update_layout(**common_layout)
            fig_day.update_xaxes(title="Jour")
            fig_day.update_yaxes(title="Nombre de Logs")
            st.plotly_chart(fig_day, use_container_width=True)

        col1_b, col2_b, col3_b, col4_b = st.columns(4)

        with col1_b:
            st.markdown("<h3 style='color: #007bad;'>Répartition par Segment</h3>", unsafe_allow_html=True)
            segment_data = filtered_logs.groupby('Segment').size().reset_index(name='Count')
            fig_segment = px.bar(segment_data, x='Count', y='Segment',
                                 orientation='h',
                                 color='Count',
                                 color_continuous_scale='Blues',
                                 text='Count')
            fig_segment.update_traces(
                texttemplate='%{text:,}',
                textposition='outside',
                textfont=dict(size=14)
            )
            fig_segment.update_layout(**common_layout, showlegend=False)
            st.plotly_chart(fig_segment, use_container_width=True)

        with col2_b:
            st.markdown("<h3 style='color: #007bad;'>Logs par Canal</h3>", unsafe_allow_html=True)
            canal_data = filtered_logs.groupby('Canal').size().reset_index(name='Count')
            fig_canal = px.bar(canal_data, x='Count', y='Canal',
                                 orientation='h',
                                 color='Count',
                                 color_continuous_scale='Blues',
                                 text='Count')
            fig_canal.update_traces(
                texttemplate='%{text:,}',
                textposition='outside',
                textfont=dict(size=14)
            )
            fig_canal.update_layout(**common_layout, showlegend=False)
            st.plotly_chart(fig_canal, use_container_width=True)

        with col3_b:
            st.markdown("<h3 style='color: #007bad;'>Top 10 Sous-motifs</h3>", unsafe_allow_html=True)
            sous_motif_data = filtered_logs.groupby('Sous_motif').size().reset_index(name='Count')
            top_motifs = sous_motif_data.sort_values('Count', ascending=False).head(10)
            fig_motif = px.bar(top_motifs, x='Count', y='Sous_motif',
                                 orientation='h',
                                 color='Count',
                                 color_continuous_scale='Blues',
                                 text='Count')
            fig_motif.update_traces(
                texttemplate='%{text:,}',
                textposition='outside',
                textfont=dict(size=14)
            )
            fig_motif.update_layout(**common_layout, showlegend=False)
            st.plotly_chart(fig_motif, use_container_width=True)

        with col4_b:
            st.markdown("<h3 style='color: #007bad;'>Mode de Facturation</h3>", unsafe_allow_html=True)
            facturation_data = filtered_logs.groupby('Mode_facturation').size().reset_index(name='Count')
            fig_facturation = px.bar(facturation_data, x='Count', y='Mode_facturation',
                                         orientation='h',
                                         color='Count',
                                         color_continuous_scale='Blues',
                                         text='Count')
            fig_facturation.update_traces(
                texttemplate='%{text:,}',
                textposition='outside',
                textfont=dict(size=14)
            )
            fig_facturation.update_layout(**common_layout, showlegend=False)
            st.plotly_chart(fig_facturation, use_container_width=True)

        st.markdown("<h2 style='text-align: center; color: #002a48;'>Détails des Logs</h2>", unsafe_allow_html=True)

        display_cols = [
            'Date_d_création', 'Heure_création', 'Segment', 'Canal',
            'Sous_motif', 'Statut_BP', 'Offre', 'Mode_facturation',
            'Anciennete_client', 'Total', 'Hyp'
        ]

        available_cols = [col for col in display_cols if col in filtered_logs.columns]
        display_df = filtered_logs[available_cols].copy()

        if 'Hyp' in display_df.columns and 'Hyp' in staff_df.columns:
            display_df = display_df.merge(staff_df[['Hyp', 'Nom Prénom', 'Team']], on='Hyp', how='left')
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
        else:
            st.warning("Could not merge staff data for 'Nom Prénom Agent' or 'Equipe Agent' due to missing 'Hyp' column in logs_df or staff_df.")
            if 'Hyp' in display_df.columns:
                display_df.drop(columns=['Hyp'], inplace=True)

        if 'Date_d_création' in display_df.columns:
            display_df['Date_d_création'] = display_df['Date_d_création'].dt.strftime('%Y-%m-%d %H:%M:%S')

        st.markdown("<h3 style='color: #002a48;'>Nombre de valeurs par colonne:</h3>", unsafe_allow_html=True)
        cols_for_counts = st.columns(len(display_df.columns))
        for i, col_name in enumerate(display_df.columns):
            with cols_for_counts[i]:
                count = display_df[col_name].count()
                st.markdown(
                    f"<div style='text-align: center; font-weight: bold; font-size: 14px; color: #007bad;'>"
                    f"{col_name}<br>({count})</div>",
                    unsafe_allow_html=True
                )
        
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

        csv = display_df.to_csv(index=False, sep=';').encode('utf-8')
        st.download_button(
            label="Télécharger les données filtrées",
            data=csv,
            file_name=f"logs_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )

    else:
        st.warning("Aucune donnée ne correspond aux critères sélectionnés. Veuillez ajuster vos filtres.")