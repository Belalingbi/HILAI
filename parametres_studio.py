"""
parametres_studio.py — Gestion des paramètres, thèmes ergonomiques et préférences sécurisées HILAI v2.0.

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop »
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import json
import os
import re
from pathlib import Path
from typing import Any

from fiabilite_studio import exiger_confirmation_steve
from securite_garde_fous import (
    ecrire_fichier_atomique,
    masquer_secrets,
    valider_configuration_studio,
    valider_couleur_hex,
)

FICHIER_CONFIG_STUDIO = Path("config_studio.json")

THEMES_PREDEFINIS: dict[str, dict[str, str]] = {
    "CyberMidnight Dark": {
        "bg_main": "#0f172a",
        "bg_panel": "#1e293b",
        "bg_input": "#0b1120",
        "fg_text": "#f8fafc",
        "fg_muted": "#94a3b8",
        "accent": "#38bdf8",
        "accent_green": "#10b981",
        "accent_red": "#ef4444",
        "accent_amber": "#f59e0b",
        "border": "#334155",
    },
    "CyberAnonymat Matrix": {
        "bg_main": "#050d0f",
        "bg_panel": "#0b1a1f",
        "bg_input": "#03090b",
        "fg_text": "#ecfdf5",
        "fg_muted": "#6ee7b7",
        "accent": "#10b981",
        "accent_green": "#22c55e",
        "accent_red": "#f43f5e",
        "accent_amber": "#fbbf24",
        "border": "#134e4a",
    },
    "Obsidian Studio Pro": {
        "bg_main": "#111827",
        "bg_panel": "#1f2937",
        "bg_input": "#090d16",
        "fg_text": "#f9fafb",
        "fg_muted": "#9ca3af",
        "accent": "#a855f7",
        "accent_green": "#10b981",
        "accent_red": "#ef4444",
        "accent_amber": "#f59e0b",
        "border": "#374151",
    },
    "Deep Indigo Cinema": {
        "bg_main": "#0e0c1f",
        "bg_panel": "#1b1838",
        "bg_input": "#080614",
        "fg_text": "#f5f3ff",
        "fg_muted": "#a5b4fc",
        "accent": "#f59e0b",
        "accent_green": "#34d399",
        "accent_red": "#fb7185",
        "accent_amber": "#fbbf24",
        "border": "#312e81",
    },
    "Clair Ergonomique": {
        "bg_main": "#f1f5f9",
        "bg_panel": "#ffffff",
        "bg_input": "#e2e8f0",
        "fg_text": "#0f172a",
        "fg_muted": "#475569",
        "accent": "#0284c7",
        "accent_green": "#059669",
        "accent_red": "#dc2626",
        "accent_amber": "#d97706",
        "border": "#cbd5e1",
    },
}

CONFIG_DEFAUT: dict[str, Any] = {
    "proprietaire": "Belalingbi Steve",
    "theme": "CyberMidnight Dark",
    "couleurs": dict(THEMES_PREDEFINIS["CyberMidnight Dark"]),
    "mode_ia": "hybride",  # hybride | local_autonome | gemini_cloud
    "modele_gemini": "gemini-2.5-flash",
    "reponse_vocale_active": True,
    "camera_auto_analyse": True,
    "camera_fps": 20,
    "intervalle_generation_sec": 2.0,
    "quota_flux_infini_mo": 256,
    "max_tampon_infini": 30,
    "taille_max_piece_jointe_mo": 250,
    "securite_stricte": True,
    "langue_interface": "fr",
    "plateforme_montage_defaut": "ffmpeg_hilai",
}


def obtenir_config_defaut() -> dict[str, Any]:
    copie = dict(CONFIG_DEFAUT)
    copie["couleurs"] = dict(CONFIG_DEFAUT["couleurs"])
    return copie


def assainir_config(config: dict[str, Any]) -> dict[str, Any]:
    """Assainit la configuration et garantit qu'aucun secret n'est persisté dans config_studio.json."""
    propre = obtenir_config_defaut()
    if not isinstance(config, dict):
        return propre

    for cle in propre:
        if cle == "couleurs":
            continue
        if cle in config and config[cle] is not None:
            propre[cle] = config[cle]

    # Validation stricte des couleurs hexadécimales
    couleurs_brutes = config.get("couleurs", {})
    if isinstance(couleurs_brutes, dict):
        couleurs_saines = dict(propre["couleurs"])
        for k, defaut_hex in propre["couleurs"].items():
            couleurs_saines[k] = valider_couleur_hex(couleurs_brutes.get(k, defaut_hex), defaut_hex)
        propre["couleurs"] = couleurs_saines

    # Bornage des valeurs numériques contre les abus
    propre["camera_fps"] = max(5, min(int(propre.get("camera_fps", 20)), 60))
    propre["intervalle_generation_sec"] = max(0.5, min(float(propre.get("intervalle_generation_sec", 2.0)), 60.0))
    propre["quota_flux_infini_mo"] = max(16, min(int(propre.get("quota_flux_infini_mo", 256)), 2048))
    propre["max_tampon_infini"] = max(5, min(int(propre.get("max_tampon_infini", 30)), 200))
    propre["taille_max_piece_jointe_mo"] = max(1, min(int(propre.get("taille_max_piece_jointe_mo", 250)), 2048))
    propre["securite_stricte"] = True  # Verrouillé actif pour le durcissement
    propre["proprietaire"] = masquer_secrets(str(propre.get("proprietaire", "Belalingbi Steve")))[:80]

    # Suppression explicite de toute clé sensible qui aurait pu être injectée
    for cle_interdite in ("gemini_api_key", "api_key", "token", "secret", "password"):
        propre.pop(cle_interdite, None)

    return propre


def charger_configuration_studio(chemin: Path = FICHIER_CONFIG_STUDIO) -> dict[str, Any]:
    """Charge la configuration studio depuis le disque ou renvoie les valeurs par défaut."""
    if not chemin.exists():
        return obtenir_config_defaut()
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
        assaini = assainir_config(donnees)
        if not valider_configuration_studio(assaini):
            return obtenir_config_defaut()
        return assaini
    except Exception:
        return obtenir_config_defaut()


def sauvegarder_configuration_studio(
    config: dict[str, Any],
    confirme_steve: bool = True,
    chemin: Path = FICHIER_CONFIG_STUDIO,
) -> Path:
    """Sauvegarde la configuration de manière atomique et validée."""
    exiger_confirmation_steve(confirme_steve, "sauvegarde_parametres_studio")
    assaini = assainir_config(config)
    if not valider_configuration_studio(assaini):
        raise ValueError("Configuration invalide détectée lors de la validation de schéma.")
    ecrire_fichier_atomique(chemin, json.dumps(assaini, indent=2, ensure_ascii=False) + "\n")
    return chemin


def appliquer_theme(
    config: dict[str, Any],
    nom_theme: str,
    couleurs_perso: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Applique un thème prédéfini ou personnalisé à la configuration."""
    nouvelle = assainir_config(config)
    if nom_theme in THEMES_PREDEFINIS:
        nouvelle["theme"] = nom_theme
        nouvelle["couleurs"] = dict(THEMES_PREDEFINIS[nom_theme])
    elif nom_theme == "Personnalisé" and couleurs_perso:
        nouvelle["theme"] = "Personnalisé"
        for k, v in couleurs_perso.items():
            if k in nouvelle["couleurs"]:
                nouvelle["couleurs"][k] = valider_couleur_hex(v, nouvelle["couleurs"][k])
    return nouvelle


def enregistrer_cle_env_securisee(
    cle_gemini: str,
    modele: str = "gemini-2.5-flash",
    confirme_steve: bool = False,
    chemin_env: Path = Path(".env"),
) -> bool:
    """
    Met à jour la clé GEMINI_API_KEY dans le fichier .env local (protégé par .gitignore),
    UNIQUEMENT si confirme_steve est strictement True.
    """
    exiger_confirmation_steve(confirme_steve, "enregistrement_cle_api_env")

    cle_propre = cle_gemini.strip()
    if not cle_propre or re.search(r"[\r\n\x00]", cle_propre):
        raise ValueError("Format de clé API invalide.")
    modele_propre = re.sub(r"[^a-zA-Z0-9.\-_]", "", modele.strip()) or "gemini-2.5-flash"

    lignes_existantes: list[str] = []
    if chemin_env.exists():
        lignes_existantes = chemin_env.read_text(encoding="utf-8", errors="replace").splitlines()

    nouvelles_lignes: list[str] = []
    cle_maj = False
    modele_maj = False
    for ligne in lignes_existantes:
        if ligne.startswith("GEMINI_API_KEY="):
            nouvelles_lignes.append(f"GEMINI_API_KEY={cle_propre}")
            cle_maj = True
        elif ligne.startswith("GEMINI_MODEL="):
            nouvelles_lignes.append(f"GEMINI_MODEL={modele_propre}")
            modele_maj = True
        else:
            nouvelles_lignes.append(ligne)

    if not cle_maj:
        nouvelles_lignes.append(f"GEMINI_API_KEY={cle_propre}")
    if not modele_maj:
        nouvelles_lignes.append(f"GEMINI_MODEL={modele_propre}")

    ecrire_fichier_atomique(chemin_env, "\n".join(nouvelles_lignes) + "\n")
    os.environ["GEMINI_API_KEY"] = cle_propre
    os.environ["GEMINI_MODEL"] = modele_propre
    return True
