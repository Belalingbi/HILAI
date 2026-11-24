"""
marketing_seo_ads_bi.py — Préparation encadrée Marketing, SEO, Ads & Business Intelligence.

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop »
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from ia_fournisseur import executer_requete_ia
from securite_garde_fous import (
    assainir_nom_fichier,
    masquer_secrets,
    valider_chemin_confine,
)

DOSSIER_SORTIES = Path("sorties_a_valider")
DOSSIER_MARKETING = DOSSIER_SORTIES / "marketing_seo_ads_bi"

DOMAINES_MARKETING = {
    "marketing_strategie": "Positionnement, persona, proposition de valeur, tunnel et plan d'action",
    "seo": "Recherche d'intentions/mots-clés, maillage interne, balises title/meta, structure éditoriale et technique",
    "google_ads": "Structure campagnes/groupes d'annonces, mots-clés, mots-clés négatifs, titres/descriptions RSA et extensions",
    "facebook_ads": "Campagnes Meta Ads, audiences/ciblages, angles visuels/vidéo, accroches et tests créatifs",
    "google_analytics": "Lecture GA4, événements clés, conversions, entonnoirs d'acquisition et contrôle qualité des données",
    "power_bi": "Modélisation de données, mesures DAX, indicateurs (KPI), structure de pages et gouvernance visuelle",
}


def preparer_dossier_marketing_bi(
    domaine: str,
    objectif_steve: str,
    contexte_ou_donnees: str = "",
) -> dict[str, Any]:
    """
    Prépare un brouillon structuré pour le marketing, le SEO, Google Ads, Facebook Ads,
    Google Analytics ou Power BI, sans aucune publication ni modification externe.
    """
    domaine_norm = domaine.strip().lower()
    description_domaine = DOMAINES_MARKETING.get(
        domaine_norm,
        "Analyse marketing, acquisition, mesure d'audience et reporting décisionnel",
    )

    instruction = (
        "Tu es le spécialiste Marketing, SEO, Ads & Business Intelligence du Studio IA "
        "de Belalingbi Steve.\n"
        "Règles de rigueur :\n"
        "- Livre une proposition structurée, concrète et actionnable en mode BROUILLON.\n"
        "- Distingue clairement les recommandations basées sur des données fournies de celles "
        "qui sont des hypothèses de travail à tester.\n"
        "- N'invente jamais de chiffres de performance réels, de résultats garantis ou de "
        "données issues d'un compte si elles n'ont pas été fournies.\n"
        "- Pour Google Ads et Facebook Ads, rappelle toujours les points de contrôle budgétaire "
        "et de ciblage avant toute activation.\n"
        "- Pour Google Analytics et Power BI, précise les dimensions, métriques, formules/mesures "
        "DAX ou événements nécessaires.\n"
        "Réponds UNIQUEMENT avec un JSON valide :\n"
        "{\n"
        '  "titre": "Titre du plan d\'action ou du dossier",\n'
        '  "domaine": "nom du domaine",\n'
        '  "diagnostic_et_hypotheses": ["Constat ou hypothèse 1", "Constat 2"],\n'
        '  "recommandations_actionnables": ["Action 1", "Action 2"],\n'
        '  "kpi_ou_mesures": [{"indicateur": "Nom", "formule_ou_cible": "Détail"}],\n'
        '  "vigilance_budget_et_donnees": "Rappels de contrôle avant toute décision"\n'
        "}"
    )

    dossier = executer_requete_ia(
        type_capacite="marketing_bi",
        system_instruction=instruction,
        demande_utilisateur=objectif_steve,
        temperature=0.35,
        contexte_supplementaire={
            "domaine": domaine_norm,
            "description_domaine": description_domaine,
            "contexte_ou_donnees": contexte_ou_donnees,
        },
    )

    dossier.setdefault("description_domaine", description_domaine)
    return dossier


def enregistrer_dossier_marketing_valide(dossier: dict, confirme_steve: bool) -> Path | None:
    """
    Enregistre le dossier marketing/BI dans 'sorties_a_valider/marketing_seo_ads_bi/'
    UNIQUEMENT si confirme_steve est True.
    """
    if not confirme_steve:
        return None
    DOSSIER_MARKETING.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dom = assainir_nom_fichier(str(dossier.get("domaine", "marketing")), "marketing")
    cible = valider_chemin_confine(DOSSIER_MARKETING / f"{dom}_{stamp}.json", DOSSIER_SORTIES)
    cible.write_text(json.dumps(dossier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return cible
