"""
fiabilite_studio.py — Module de fiabilité, validation stricte et lecture sécurisée des sorties.

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop »
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import json
import re
from pathlib import Path
from typing import Any

from securite_garde_fous import masquer_secrets, valider_chemin_confine


def exiger_confirmation_steve(confirme_steve: bool, action: str) -> None:
    """
    Garde-fou décisionnel déterministe absolu :
    Lève une PermissionError si confirme_steve n'est pas strictement True.
    """
    if confirme_steve is not True:
        raise PermissionError(
            f"Action refusée ({action}) : validation explicite de Belalingbi Steve requise."
        )


def parser_json_robuste(texte_brut: str | None) -> dict[str, Any]:
    """
    Parseur JSON tolérant et résilient face aux formats Markdown et réponses tronquées du LLM.
    """
    if not texte_brut:
        return {}
    nettoye = str(texte_brut).strip()
    if nettoye.startswith("```"):
        nettoye = re.sub(r"^```(?:json)?\s*", "", nettoye)
        nettoye = re.sub(r"\s*```$", "", nettoye)
    try:
        donnee = json.loads(nettoye)
        return donnee if isinstance(donnee, dict) else {"valeur": donnee}
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", nettoye, flags=re.DOTALL)
        if match:
            try:
                donnee = json.loads(match.group(0))
                return donnee if isinstance(donnee, dict) else {"valeur": donnee}
            except json.JSONDecodeError:
                pass
        return {"texte_brut": texte_brut}


def lire_aperçu_sortie_securise(chemin_fichier: Path | str, max_caracteres: int = 8000) -> str:
    """
    Lit de manière sécurisée un aperçu de fichier en confinant l'accès au dossier 'sorties_a_valider'.
    Empêche les attaques par Path Traversal et masque les secrets éventuels.
    """
    base = Path("sorties_a_valider")
    base.mkdir(parents=True, exist_ok=True)

    try:
        cible = valider_chemin_confine(chemin_fichier, base)
    except ValueError as e:
        raise ValueError(f"Accès refusé : {e}")

    if not cible.exists() or not cible.is_file():
        return "Fichier introuvable."

    if cible.suffix.lower() in {".xlsx", ".pptx", ".pdf", ".db"}:
        return (
            f"Fichier binaire : {cible.name}\n"
            f"Taille : {cible.stat().st_size} octets\n"
            "Aperçu texte non applicable : ouvrir avec l'application adaptée après validation."
        )

    texte = cible.read_text(encoding="utf-8", errors="replace")
    # Masquage automatique des secrets
    texte_securise = masquer_secrets(texte)

    if len(texte_securise) > max_caracteres:
        return texte_securise[:max_caracteres] + "\n\n[...contenu tronqué pour l'aperçu...]"
    return texte_securise
