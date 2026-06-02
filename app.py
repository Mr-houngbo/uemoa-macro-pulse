import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
# Importation de nos modules du Sprint 1 et 3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from supabase_client import SupabaseClient
from scripts.pdf_parser import extraire_donnees_resume
from scripts.bulk_insert import alimenter_base_de_donnees

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="UEMOA Macro-Pulse", page_icon="📊", layout="wide")

# Initialisation du client Supabase
@st.cache_resource # Permet d'éviter de reconnecter à chaque clic
def get_db_client():
    return SupabaseClient()

try:
    db = get_db_client()
except Exception as e:
    st.error(f"Erreur de connexion à la base de données : {e}")
    st.stop()

# 2. BARRE LATÉRALE (SIDEBAR) - NAVIGATION PRINCIPALE
st.sidebar.title("🎛️ Terminal UEMOA")
st.sidebar.write("Pilote ton portefeuille par la macroéconomie.")
page = st.sidebar.radio("Navigation", ["📈 Dashboard Investisseur", "📥 Ingestion Documentaire"])

# =========================================================================
# PAGE 1 : DASHBOARD INVESTISSEUR (VISUALISATION)
# =========================================================================
if page == "📈 Dashboard Investisseur":
    st.title("📊 UEMOA Macro-Pulse Dashboard")
    st.caption("Données d'aide à la décision d'investissement — Zone UMOA")
    
    # Récupération des données en temps réel depuis Supabase
    try:
        res_macro = db.table("macro_environment").select("*").execute()
        res_money = db.table("interbank_market").select("*").execute()
        
        df_macro = pd.DataFrame(res_macro.data)
        df_money = pd.DataFrame(res_money.data)
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        st.stop()

    # Si la base est vide, on affiche un message d'attente
    if df_macro.empty or df_money.empty:
        st.info("👋 Bienvenue ! Ta base de données est prête mais vide. Va sur l'onglet 'Ingestion Documentaire' pour charger ton premier bulletin.")
    else:
        # Découpage de l'écran en 3 onglets thématiques
        tab1, tab2, tab3 = st.tabs(["💧 Liquidité & Marché Monétaire", "🛒 Inflation & Secteur Réel", "🏦 Santé Bancaire"])
        
        # --- ONGLET 1 : LIQUIDITÉ ---
        with tab1:
            st.subheader("Analyse de la Liquidité Régionale")
            
            # Exemple de KPI Cards dynamiques
            col1, col2 = st.columns(2)
            with col1:
                # On cherche le volume interbancaire
                vol_row = df_money[df_money['indicator_name'] == 'Volume Moyen Hebdomadaire']
                if not vol_row.empty:
                    st.metric(label="Volume Moyen Hebdomadaire Interbancaire", value=f"{vol_row.iloc[-1]['value_brute']} Mrds FCFA")
            with col2:
                taux_row = df_money[df_money['indicator_name'] == 'Taux Minimum Soumission']
                if not taux_row.empty:
                    st.metric(label="Taux Directeur BCEAO (Minimum Soumission)", value=f"{taux_row.iloc[-1]['value_brute']} %", delta="-0.25 %")

            st.write("---")
            st.markdown("**Évolution des Taux et Volumes** (Les graphiques se construiront au fil des mois cumulés)")
            # Graphique interactif Plotly
            fig_vol = px.line(df_money, x='bulletin_date', y='value_brute', color='indicator_name', 
                              title="Historique des Métriques du Marché Monétaire", markers=True)
            st.plotly_chart(fig_vol, use_container_width=True)

        # --- ONGLET 2 : INFLATION & SECTEUR RÉEL ---
        with tab2:
            st.subheader("Indicateurs de Prix et Matières Premières")
            
            # Affichage sous forme de tableau propre pour le moment
            st.dataframe(df_macro, use_container_width=True)
            
            # Graphique de l'inflation
            df_inf = df_macro[df_macro['indicator_type'] == 'INFLATION']
            if not df_inf.empty:
                fig_inf = px.bar(df_inf, x='indicator_name', y='value_brute', text_auto=True,
                                 title="Niveau de l'Inflation ce mois-ci", color='indicator_name')
                st.plotly_chart(fig_inf, use_container_width=True)

        # --- ONGLET 3 : SANTÉ BANCAIRE ---
        with tab3:
            st.subheader("Risques Systémiques & Crédits")
            st.info("Ces métriques seront extraites des sections approfondies du bulletin lors du prochain sprint.")

# =========================================================================
# PAGE 2 : INGESTION DOCUMENTAIRE (TON MODULE DE TÉLÉVERSEMENT)
# =========================================================================
elif page == "📥 Ingestion Documentaire":
    st.title("📥 Centre d'Ingestion Autopilot")
    st.write("Ajoute un nouveau rapport mensuel de la BCEAO pour mettre à jour tes graphiques instantanément.")
    
    st.warning("⚠️ Pour le moment, cette interface simule l'extraction depuis le texte du résumé. Au Sprint 5, elle lira directement ton vrai fichier PDF.")

    # 1. Sélection de la date du rapport
    date_bulletin = st.date_input("Date d'application du bulletin (En général le 1er du mois)", datetime(2026, 3, 1))
    
    # 2. Zone de texte ou téléversement
    st.markdown("### Copie le texte du Résumé officiel ci-dessous :")
    texte_bceao = st.text_area("Texte du Bulletin", height=250, placeholder="Colle le paragraphe du résumé ici...")
    
    # 3. Bouton d'action
    if st.button("🚀 Lancer l'Analyse et l'Ingestion", use_container_width=True):
        if not texte_bceao.strip():
            st.error("Veuillez coller du texte avant de lancer l'analyse.")
        else:
            with st.spinner("🤖 L'IA analyse le texte, extrait les indicateurs et met à jour Supabase..."):
                try:
                    # Étape A : Parsing
                    donnees_triees = extraire_donnees_resume(texte_bceao, date_bulletin=date_bulletin.isoformat())
                    
                    # Étape B : Injection
                    alimenter_base_de_donnees(donnees_triees)
                    
                    st.success("🎉 Données extraites et injectées avec succès dans ton Cloud ! Retourne sur le Dashboard pour voir le résultat.")
                    st.balloons() # Petite animation de célébration
                    
                except Exception as e:
                    st.error(f"Une erreur est survenue pendant le traitement : {e}")

