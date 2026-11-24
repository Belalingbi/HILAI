"""
connecteurs_et_sauvegarde.py — Connecteurs locaux durcis et sauvegarde snapshot horodatée.

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop »
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from fiabilite_studio import exiger_confirmation_steve
from securite_garde_fous import (
    masquer_secrets,
    valider_chemin_confine,
    valider_commande_securisee,
)


def executer_outil_local_encadre(
    nom_outil: str,
    commande_args: list[str],
    confirme_steve: bool,
    timeout_sec: int = 120,
) -> dict:
    """
    Exécute un outil local ou script externe (ex. moteur voix, image, vidéo, appel)
    UNIQUEMENT si confirme_steve est strictement True, avec validation de sécurité anti-injection.
    """
    if not confirme_steve:
        return {
            "statut": "annule",
            "outil": nom_outil,
            "message": "Exécution bloquée : confirmation explicite de Belalingbi Steve non donnée.",
        }

    # Validation de sécurité stricte anti-injection de commande
    try:
        args_valides = valider_commande_securisee(commande_args)
    except Exception as exc:
        return {
            "statut": "bloque_securite",
            "outil": nom_outil,
            "erreur": f"Garde-fou cybersécurité : {exc}",
        }

    try:
        proc = subprocess.run(
            args_valides,
            shell=False,  # INTERDICTION ABSOLUE de shell=True
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        sortie_filtree = masquer_secrets(proc.stdout[-2000:])
        erreur_filtree = masquer_secrets(proc.stderr[-2000:])

        return {
            "statut": "ok" if proc.returncode == 0 else "erreur",
            "outil": nom_outil,
            "code_retour": proc.returncode,
            "sortie": sortie_filtree,
            "erreur": erreur_filtree,
        }
    except subprocess.TimeoutExpired:
        return {
            "statut": "timeout",
            "outil": nom_outil,
            "erreur": f"Délai d'exécution dépassé ({timeout_sec}s). Processus interrompu.",
        }
    except Exception as exc:
        return {
            "statut": "erreur_execution",
            "outil": nom_outil,
            "erreur": f"Erreur système : {exc}",
        }


def sauvegarder_snapshot_studio(
    confirme_steve: bool,
    dossier_sauvegardes: Path | str = Path("sauvegardes_studio"),
) -> Path | None:
    """
    Copie les fichiers de configuration, journaux et sorties validées dans un dossier horodaté
    sans jamais supprimer ni écraser les validations existantes.
    """
    if not confirme_steve:
        return None

    racine_sauvegardes = Path(dossier_sauvegardes)
    racine_sauvegardes.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cible = racine_sauvegardes / f"snapshot_{stamp}"

    # Confinement strict
    cible = valider_chemin_confine(cible, racine_sauvegardes)
    cible.mkdir(parents=True, exist_ok=True)

    for fichier in [Path("regles_decision.json"), Path("memoire_preferences.json"), *Path(".").glob("journal_*.md")]:
        if fichier.exists():
            shutil.copy2(fichier, cible / fichier.name)

    dossier_sorties = Path("sorties_a_valider")
    if dossier_sorties.exists():
        shutil.copytree(dossier_sorties, cible / dossier_sorties.name, dirs_exist_ok=True)

    manifeste = {
        "date_sauvegarde": datetime.now().isoformat(timespec="seconds"),
        "utilisateur": "Belalingbi Steve",
        "elements_copies": [p.name for p in cible.iterdir()],
        "securite": "Vérifié & Confiné",
    }
    (cible / "manifeste_sauvegarde.json").write_text(
        json.dumps(manifeste, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return cible
