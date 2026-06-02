import os
import sys
from datetime import datetime
# On importe nos propres modules créés dans les étapes précédentes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import SupabaseClient
from scripts.pdf_parser import extraire_donnees_resume

def alimenter_base_de_donnees(donnees_triees):
    """
    Prend le dictionnaire de données et insère chaque catégorie
    dans sa table respective sur Supabase.
    """
    # Initialisation de notre client Supabase
    try:
        db = SupabaseClient()
    except Exception as e:
        print(f"❌ Impossible d'initialiser le client Supabase : {e}")
        return

    print("\n🚀 Démarrage de l'injection des données sur le Cloud...")

    # 1. Insertion dans la table MACRO_ENVIRONMENT
    donnees_macro = donnees_triees.get("macro_environment", [])
    if donnees_macro:
        print(f"📡 Envoi de {len(donnees_macro)} indicateurs macroéconomiques...")
        try:
            # .insert() peut prendre une liste complète de dictionnaires d'un coup !
            reponse = db.table("macro_environment").insert(donnees_macro)
            if reponse.data:
                print("✅ Table 'macro_environment' mise à jour avec succès !")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion macro : {e}")
    else:
        print("ℹ️ Aucun indicateur macro à insérer.")

    # 2. Insertion dans la table INTERBANK_MARKET
    donnees_monetaire = donnees_triees.get("interbank_market", [])
    if donnees_monetaire:
        print(f"📡 Envoi de {len(donnees_monetaire)} indicateurs monétaires...")
        try:
            reponse = db.table("interbank_market").insert(donnees_monetaire)
            if reponse.data:
                print("✅ Table 'interbank_market' mise à jour avec succès !")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion monétaire : {e}")
    else:
        print("ℹ️ Aucun indicateur monétaire à insérer.")

    # 3. Insertion dans la table BANKING_SECTOR_HEALTH
    donnees_banque = donnees_triees.get("banking_sector_health", [])
    if donnees_banque:
        print(f"📡 Envoi de {len(donnees_banque)} indicateurs bancaires...")
        try:
            reponse = db.table("banking_sector_health").insert(donnees_banque)
            if reponse.data:
                print("✅ Table 'banking_sector_health' mise à jour avec succès !")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion bancaire : {e}")
    else:
        print("ℹ️ Aucun indicateur bancaire détecté dans ce lot.")


if __name__ == "__main__":
    print("============================================================")
    # Le texte complet de Mars 2026 que tu as découvert
    texte_bulletin_mars_2026 = """
    Les cours mondiaux du pétrole brut ont rebondi de 35,5% en mars 2026. De même, les prix de l'or (+62,9%) et du coton (+2,0%) ont augmenté.
    Au niveau régional, la BCEAO a baissé de 25 points de base ses taux directeurs, pour compter du 16 mars 2026. Ainsi, le taux minimum de soumission aux appels d'offres d'injection de liquidité est passé de 3,25% à 3,00%.
    Au niveau du marché interbancaire, le volume moyen hebdomadaire des opérations est ressorti à 834,3 milliards en mars 2026.
    Le taux d'inflation, en glissement annuel, est ressorti à +0,1% en mars 2026. Le taux d'inflation sous-jacente s'est réduit pour se situer à 1,1% en mars 2026.
    """
    
    print("📝 Phase 1 : Extraction du texte de Mars 2026...")
    # On appelle notre parser pour transformer le texte en dictionnaire
    donnees_extraites = extraire_donnees_resume(texte_bulletin_mars_2026, date_bulletin="2026-03-01")
    
    print("📝 Phase 2 : Transmission des données triées...")
    # On envoie le dictionnaire à notre fonction d'alimentation cloud
    alimenter_base_de_donnees(donnees_extraites)
    print("============================================================")
