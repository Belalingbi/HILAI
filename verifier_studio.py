"""
verifier_studio.py — Diagnostic d'environnement, de cybersécurité et de cohérence modulaire.

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop » v2.0
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import importlib
import importlib.util
import os
import py_compile
import shutil
import sys
from pathlib import Path

FICHIERS_STUDIO = [
    "securite_garde_fous.py",
    "parametres_studio.py",
    "ia_fournisseur.py",
    "fiabilite_studio.py",
    "connecteurs_et_sauvegarde.py",
    "generateur_media_infini.py",
    "montage_video_studio.py",
    "multimodal_capteurs.py",
    "studio_coeur.py",
    "studio_lanceur.py",
    "reconnaissance_photo_chanson.py",
    "mathematiques_geometrie.py",
    "canaux_messageries_sociaux.py",
    "marketing_seo_ads_bi.py",
    "registre_studio.py",
]

MODULES_OPTIONNELS = [
    "tkinter",
    "google.genai",
    "cv2",
    "PIL",
    "psutil",
    "sounddevice",
    "pyttsx3",
    "sympy",
    "openpyxl",
    "pptx",
    "reportlab",
]


def verifier_tout() -> dict:
    from ia_fournisseur import obtenir_mode_fournisseur
    from securite_garde_fous import executer_audit_securite_complet

    rapport = {
        "os": sys.platform,
        "python": sys.version.split()[0],
        "api_key_presente": bool(os.environ.get("GEMINI_API_KEY")),
        "mode_fournisseur": obtenir_mode_fournisseur(),
        "ffmpeg_present": bool(shutil.which("ffmpeg")),
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

    # 2. Audit complet du durcissement cybersécurité
    try:
        Path("sorties_a_valider").mkdir(exist_ok=True)
        rapport["durcissement_securite"] = executer_audit_securite_complet()
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
    print("     DIAGNOSTIC HILAI STUDIO v2.0 — BELALINGBI STEVE            ")
    print("     Projet CyberAnonymat — Human-in-the-Loop IA                ")
    print("================================================================")
    print(f"Système d'exploitation : {rapport['os']} | Python : {rapport['python']}")
    print(f"Mode d'intelligence   : {rapport['mode_fournisseur'].upper()}")
    print(f"GEMINI_API_KEY        : {'Détectée & Prête' if rapport['api_key_presente'] else 'Mode Local Autonome Actif'}")
    print(f"Moteur FFmpeg local   : {'Installé' if rapport.get('ffmpeg_present') else 'Absent (mode storyboard/timeline actif)'}")

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

    caps = rapport.get("capacites", {})
    print(f"\n[+] Registre des {len(caps)} capacités modulaires :")
    for cle, infos in caps.items():
        if isinstance(infos, dict):
            statut = "Opérationnelle [100%]" if infos.get("disponible") else "Indisponible"
            print(f"  • {cle:<26} ({infos.get('label', '')[:32]}) : {statut}")
        else:
            print(f"  • {cle} : {infos}")
    print("================================================================\n")


if __name__ == "__main__":
    afficher_rapport(verifier_tout())
