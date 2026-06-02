import re
from datetime import datetime

def extraire_donnees_resume(texte_resume, date_bulletin="2026-03-01"):
    """
    Analyse le texte brut du résumé de la BCEAO et en extrait
    les indicateurs clés sous forme de dictionnaires prêts pour Supabase.
    """
    donnees_normalisees = {
        "macro_environment": [],
        "interbank_market": [],
        "banking_sector_health": []
    }
    
    # -------------------------------------------------------------------------
    # 1. RECHERCHE DANS LE SECTEUR MACRO / RÉEL (Inflation, Matières Premières)
    # -------------------------------------------------------------------------
    
    # Extraction de l'inflation globale (Ex: "taux d'inflation, en glissement annuel, est ressorti à +0,1%")
    match_inflation = re.search(r"taux d'inflation.*?ressorti à\s+([+-]?\d+[\.,]\d+)", texte_resume, re.IGNORECASE)
    if match_inflation:
        valeur = float(match_inflation.group(1).replace(",", "."))
        donnees_normalisees["macro_environment"].append({
            "bulletin_date": date_bulletin,
            "country": "UMOA",
            "indicator_type": "INFLATION",
            "indicator_name": "Inflation Globale",
            "value_brute": valeur,
            "unit": "%"
        })

    # Extraction de l'inflation sous-jacente (Ex: "se situer à 1,1% en mars 2026")
    match_sous_jacente = re.search(r"inflation sous-jacente.*?se situer à\s+([+-]?\d+[\.,]\d+)", texte_resume, re.IGNORECASE)
    if match_sous_jacente:
        valeur = float(match_sous_jacente.group(1).replace(",", "."))
        donnees_normalisees["macro_environment"].append({
            "bulletin_date": date_bulletin,
            "country": "UMOA",
            "indicator_type": "INFLATION",
            "indicator_name": "Inflation Sous-jacente",
            "value_brute": valeur,
            "unit": "%"
        })

    # Extraction des variations de matières premières (Or, Pétrole, Cacao)
    # Exemple : "prix de l'or (+62,9%)"
    match_or = re.search(r"l'or\s+\(([+-]?\d+[\.,]\d+)%\)", texte_resume)
    if match_or:
        valeur_change = float(match_or.group(1).replace(",", "."))
        donnees_normalisees["macro_environment"].append({
            "bulletin_date": date_bulletin,
            "country": "GLOBAL",
            "indicator_type": "MATIERE_PREMIERE",
            "indicator_name": "Cours de l'Or (YOY)",
            "value_brute": valeur_change, # On stocke la variation car c'est l'info du résumé
            "unit": "%"
        })

    # -------------------------------------------------------------------------
    # 2. RECHERCHE DANS LE MARCHÉ MONÉTAIRE (Taux, Refinancements, Volumes)
    # -------------------------------------------------------------------------
    
    # Taux directeur minimum d'injection (Ex: "passé de 3,25% à 3,00%")
    match_taux_bceao = re.search(r"appels d'offres d'injection de liquidité est passé.*?à\s+([+-]?\d+[\.,]\d+)%", texte_resume)
    if match_taux_bceao:
        valeur = float(match_taux_bceao.group(1).replace(",", "."))
        donnees_normalisees["interbank_market"].append({
            "bulletin_date": date_bulletin,
            "institution": "BCEAO",
            "indicator_name": "Taux Minimum Soumission",
            "value_brute": valeur,
            "unit": "%"
        })

    # Volume interbancaire hebdomadaire (Ex: "ressorti à 834,3 milliards en mars 2026")
    match_vol_interbancaire = re.search(r"volume moyen hebdomadaire des opérations.*?ressorti à\s+([+-]?\d+[\.,]\d+)\s+milliards", texte_resume, re.IGNORECASE)
    if match_vol_interbancaire:
        valeur = float(match_vol_interbancaire.group(1).replace(",", "."))
        donnees_normalisees["interbank_market"].append({
            "bulletin_date": date_bulletin,
            "institution": "MARCHE_INTERBANCAIRE",
            "indicator_name": "Volume Moyen Hebdomadaire",
            "value_brute": valeur,
            "unit": "Milliards FCFA"
        })

    return donnees_normalisees

# Zone de test local du parser
if __name__ == "__main__":
    # On simule le texte que tu as extrait du bulletin
    texte_test = """
    Au niveau régional, la BCEAO a baissé de 25 points de base ses taux directeurs, pour compter du 16 mars 2026. Ainsi, le taux minimum de soumission aux appels d'offres d'injection de liquidité est passé de 3,25% à 3,00%.
    Au niveau du marché interbancaire, le volume moyen hebdomadaire des opérations est ressorti à 834,3 milliards en mars 2026.
    Le taux d'inflation, en glissement annuel, est ressorti à +0,1% en mars 2026. Le taux d'inflation sous-jacente s'est réduit pour se situer à 1,1% en mars 2026. Prix de l'or (+62,9%).
    """
    
    resultat = extraire_donnees_resume(texte_test)
    print("📊 RÉSULTAT DU PARSING DE TEST :")
    import json
    print(json.dumps(resultat, indent=4, ensure_ascii=False))
