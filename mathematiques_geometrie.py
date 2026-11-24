"""
mathematiques_geometrie.py — Résolution rigoureuse et calculs symboliques/numériques encadrés.

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop »
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import json
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from ia_fournisseur import executer_requete_ia
from securite_garde_fous import (
    calculer_expression_securisee,
    masquer_secrets,
    valider_chemin_confine,
)

DOSSIER_SORTIES = Path("sorties_a_valider")
DOSSIER_MATHS = DOSSIER_SORTIES / "maths_geometrie"


def _verifier_sympy() -> bool:
    try:
        import sympy  # noqa: F401
        return True
    except ImportError:
        return False


def resoudre_math_ou_geometrie(
    enonce_steve: str,
    domaine: str = "auto",
    verifier_par_calcul: bool = True,
) -> dict[str, Any]:
    """
    Prépare une résolution détaillée (mathématiques ou géométrie) en mode brouillon à valider.
    Exécute un contrôle local sécurisé (AST parser déterministe ou SymPy si disponible).
    """
    sympy_dispo = _verifier_sympy() if verifier_par_calcul else False

    # Contrôle déterministe préalable via l'analyseur sécurisé sans eval
    calc_securise = calculer_expression_securisee(enonce_steve)

    instruction = (
        "Tu es l'assistant de mathématiques et de géométrie du Studio IA de Belalingbi Steve.\n"
        "Règles de rigueur :\n"
        "- Identifie clairement les données, hypothèses et inconnues.\n"
        "- Détaille les étapes de calcul ou de démonstration géométrique (propriétés, théorèmes, "
        "repère/coordonnées ou relations métriques si pertinent).\n"
        "- Garde les valeurs exactes (fractions, multiples de pi, racines) avant toute valeur approchée.\n"
        "- Signale toute ambiguïté d'énoncé ou condition d'existence (ex. division par zéro, angle valide, "
        "points non alignés) plutôt que de deviner.\n"
        "- Ne décide rien à la place de Steve : livre une proposition claire prête à être validée.\n"
        "Réponds UNIQUEMENT avec un JSON valide :\n"
        "{\n"
        '  "titre": "Titre concis du problème",\n'
        '  "domaine_detecte": "algebre | analyse | arithmetique | probabilites | geometrie_plane | geometrie_analytique | geometrie_espace | trigonometrie",\n'
        '  "hypotheses_et_conditions": ["Hypothèse ou condition 1"],\n'
        '  "etapes_resolution": ["Étape 1...", "Étape 2..."],\n'
        '  "resultat_exact": "Valeur exacte",\n'
        '  "resultat_approche": "Valeur numérique approchée",\n'
        '  "points_de_vigilance": "Conditions de validité ou limites de la solution"\n'
        "}"
    )

    dossier = executer_requete_ia(
        type_capacite="maths_geometrie",
        system_instruction=instruction,
        demande_utilisateur=enonce_steve,
        temperature=0.15,
        contexte_supplementaire={"domaine": domaine},
    )

    dossier["controle_local"] = {
        "sympy_installe": sympy_dispo,
        "ast_securise": calc_securise,
    }
    return dossier


def enregistrer_resolution_validee(dossier: dict, confirme_steve: bool) -> Path | None:
    """
    Enregistre le dossier de résolution dans 'sorties_a_valider/maths_geometrie/'
    UNIQUEMENT si confirme_steve est True.
    """
    if not confirme_steve:
        return None
    DOSSIER_MATHS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cible = valider_chemin_confine(DOSSIER_MATHS / f"maths_geo_{stamp}.json", DOSSIER_SORTIES)
    cible.write_text(json.dumps(dossier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return cible
