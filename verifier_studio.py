"""
verifier_studio.py — Diagnostic d'environnement, de cybersécurité et de cohérence modulaire.

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop »
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import importlib
import importlib.util
import os
import py_compile
import sys
from pathlib import Path

FICHIERS_STUDIO = [
    "securite_garde_fous.py",
    "ia_fournisseur.py",
    "fiabilite_studio.py",
    "connecteurs_et_sauvegarde.py",
    "studio_coeur.py",
    "studio_lanceur.py",
    "reconnaissance_photo_chanson.py",
    "mathematiques_geometrie.py",
    "canaux_messageries_sociaux.py",
    "marketing_seo_ads_bi.py",
    "registre_studio.py",
]

MODULES_OPTIONNELS = ["tkinter", "google.genai", "sympy", "openpyxl", "pptx", "reportlab"]


def verifier_tout() -> dict:
    from ia_fournisseur import obtenir_mode_fournisseur
    from securite_garde_fous import (
        calculer_expression_securisee,
        masquer_secrets,
        valider_chemin_confine,
        valider_commande_securisee,
    )

    rapport = {
        "os": sys.platform,
        "python": sys.version.split()[0],
        "api_key_presente": bool(os.environ.get("GEMINI_API_KEY")),
        "mode_fournisseur": obtenir_mode_fournisseur(),
        "syntaxe_fichiers": {},
        "durcissement_securite": {},
        "dependances_optionnelles": {},
        "capacites": {},
    }

    # 1. Vérification de la syntaxe des modules
    for nom in FICHIERS_STUDIO:
        chemin = Path(nom)
        if not chemin.exists():
            rapport["syntaxe_fichiers"][nom] = "absent"
            continue
        try:
            py_compile.compile(str(chemin), doraise=True)
            rapport["syntaxe_fichiers"][nom] = "ok"
        except py_compile.PyCompileError as exc:
            rapport["syntaxe_fichiers"][nom] = f"erreur_syntaxe: {exc.msg}"

    # 2. Audit du durcissement cybersécurité
    try:
        # Test Path Traversal
        Path("sorties_a_valider").mkdir(exist_ok=True)
        valider_chemin_confine("sorties_a_valider/test.txt", "sorties_a_valider")
        try:
            valider_chemin_confine("../test_traversal.txt", "sorties_a_valider")
            rapport["durcissement_securite"]["anti_path_traversal"] = "échec"
        except ValueError:
            rapport["durcissement_securite"]["anti_path_traversal"] = "actif (traversée bloquée)"

        # Test Command Injection
        valider_commande_securisee(["python", "--version"])
        try:
            valider_commande_securisee(["python", "test.py; rm -rf /"])
            rapport["durcissement_securite"]["anti_command_injection"] = "échec"
        except ValueError:
            rapport["durcissement_securite"]["anti_command_injection"] = "actif (métalangage bloqué)"

        # Test Masquage de secrets
        secret_test = masquer_secrets("Clé : AIzaSyD12345678901234567890123456789012")
        if "[SECRET_GEMINI_API_KEY_MASQUÉ]" in secret_test:
            rapport["durcissement_securite"]["masquage_secrets"] = "actif (auto-redaction)"
        else:
            rapport["durcissement_securite"]["masquage_secrets"] = "échec"

        # Test Calculateur AST sans eval
        res_calc = calculer_expression_securisee("2 + 3 * 4")
        if res_calc["succes"] and res_calc["resultat"] == 14:
            rapport["durcissement_securite"]["calcul_ast_sans_eval"] = "actif (sécurisé)"
        else:
            rapport["durcissement_securite"]["calcul_ast_sans_eval"] = "échec"

    except Exception as exc:
        rapport["durcissement_securite"]["erreur"] = str(exc)

    # 3. Dépendances
    for mod in MODULES_OPTIONNELS:
        try:
            rapport["dependances_optionnelles"][mod] = importlib.util.find_spec(mod) is not None
        except (ModuleNotFoundError, ValueError):
            rapport["dependances_optionnelles"][mod] = False

    # 4. Capacités
    if Path("registre_studio.py").exists():
        try:
            reg = importlib.import_module("registre_studio")
            if hasattr(reg, "verifier_disponibilite_capacites"):
                rapport["capacites"] = reg.verifier_disponibilite_capacites()
        except Exception as exc:
            rapport["capacites"] = {"erreur": str(exc)}

    return rapport


def afficher_rapport(rapport: dict) -> None:
    print("================================================================")
    print("       DIAGNOSTIC HILAI STUDIO — BELALINGBI STEVE               ")
    print("       Projet CyberAnonymat — Human-in-the-Loop IA              ")
    print("================================================================")
    print(f"Système d'exploitation : {rapport['os']} | Python : {rapport['python']}")
    print(f"Mode d'intelligence   : {rapport['mode_fournisseur'].upper()}")
    print(f"GEMINI_API_KEY        : {'Détectée & Prête' if rapport['api_key_presente'] else 'Mode Local Autonome Actif'}")

    print("\n[+] Durcissement Cybersécurité & Garde-fous :")
    for mecanisme, statut in rapport["durcissement_securite"].items():
        print(f"  • {mecanisme:<25} : {statut}")

    print("\n[+] Intégrité des modules & Syntaxe :")
    for nom, etat in rapport["syntaxe_fichiers"].items():
        print(f"  • {nom:<32} : {etat}")

    print("\n[+] Dépendances d'environnement :")
    for mod, dispo in rapport["dependances_optionnelles"].items():
        etat_str = "Installé" if dispo else "Non installé (fallback automatique)"
        print(f"  • {mod:<25} : {etat_str}")

    print("\n[+] Registre des 9 capacités modulaires :")
    for cle, infos in rapport.get("capacites", {}).items():
        if isinstance(infos, dict):
            statut = "Opérationnelle [100%]" if infos.get("disponible") else "Indisponible"
            print(f"  • {cle:<22} ({infos.get('label', '')[:35]}) : {statut}")
        else:
            print(f"  • {cle} : {infos}")
    print("================================================================\n")


if __name__ == "__main__":
    afficher_rapport(verifier_tout())
