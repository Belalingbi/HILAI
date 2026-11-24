"""
reconnaissance_photo_chanson.py — Reconnaissance multimodale d'images et identification musicale assistée.

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop »
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import json
import mimetypes
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from connecteurs_et_sauvegarde import executer_outil_local_encadre
from ia_fournisseur import est_gemini_disponible, executer_requete_ia
from securite_garde_fous import (
    assainir_nom_fichier,
    masquer_secrets,
    valider_chemin_confine,
)

DOSSIER_SORTIES = Path("sorties_a_valider")
DOSSIER_RECONNAISSANCE = DOSSIER_SORTIES / "reconnaissances"


def _deviner_mime(chemin_photo: Path) -> str:
    mime, _ = mimetypes.guess_type(str(chemin_photo))
    if mime and mime.startswith("image/"):
        return mime
    ext = chemin_photo.suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(ext, "image/jpeg")


def reconnaitre_photo(chemin_photo_str: str, question_complementaire: str = "") -> dict[str, Any]:
    """
    Analyse une image locale et retourne une fiche structurée (brouillon à valider).
    Ne modifie aucun fichier sur le disque.
    """
    chemin = Path(chemin_photo_str)
    if not chemin.exists() or not chemin.is_file():
        # Fallback élégant si l'image test n'est pas encore présente
        return {
            "resume_visuel": f"Fichier spécifié : '{chemin.name}' (non trouvé sur le disque local).",
            "elements_identifies": ["Fichier absent"],
            "niveau_certitude": "faible",
            "points_incertains_ou_vigilance": "Vérifier le chemin du fichier image avant l'analyse.",
            "fichier_source": str(chemin),
            "fournisseur": "local_autonome",
        }

    instruction = (
        "Tu es l'analyste visuel du Studio IA de Belalingbi Steve.\n"
        "Analyse l'image fournie avec rigueur : distingue clairement ce qui est visible "
        "avec certitude de ce qui reste hypothétique ou incertain. Ne fabrique jamais de "
        "nom, date, lieu ou identité précise si l'image ne permet pas de l'affirmer.\n"
        "Réponds UNIQUEMENT avec un objet JSON valide :\n"
        "{\n"
        '  "resume_visuel": "Description claire de la scène ou du sujet",\n'
        '  "elements_identifies": ["Élément 1", "Élément 2"],\n'
        '  "texte_detecte": "Texte visible dans l\'image ou néant",\n'
        '  "niveau_certitude": "élevé | moyen | faible",\n'
        '  "points_incertains_ou_vigilance": "Ce qui demande vérification humaine"\n'
        "}"
    )

    if est_gemini_disponible():
        try:
            from google import genai
            from google.genai import types

            octets_image = chemin.read_bytes()
            mime_type = _deviner_mime(chemin)
            client = genai.Client()
            contenu = [
                types.Part.from_bytes(data=octets_image, mime_type=mime_type),
                question_complementaire.strip()
                or "Identifie et décris précisément cette image pour validation de Belalingbi Steve.",
            ]
            rep = client.models.generate_content(
                model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=contenu,
                config=types.GenerateContentConfig(
                    system_instruction=instruction,
                    response_mime_type="application/json",
                    temperature=0.25,
                ),
            )
            resultat = json.loads(masquer_secrets(rep.text or "{}"))
            resultat["fichier_source"] = str(chemin)
            resultat["fournisseur"] = "gemini_cloud"
            return resultat
        except Exception:
            pass

    # Mode autonome local
    return executer_requete_ia(
        type_capacite="reconnaissance_photo",
        system_instruction=instruction,
        demande_utilisateur=chemin_photo_str,
        contexte_supplementaire={
            "chemin_photo_str": chemin_photo_str,
            "question_complementaire": question_complementaire,
        },
    )


def reconnaitre_chanson(
    indices_ou_fichier: str,
    commande_outil_audio_locale: list[str] | None = None,
    confirme_execution_locale: bool = False,
) -> dict[str, Any]:
    """
    Prépare l'identification d'une chanson à partir d'indices (paroles, ambiance, fichier)
    et, optionnellement, exécute un outil local d'empreinte/analyse audio UNIQUEMENT si
    confirme_execution_locale est True.
    """
    sortie_outil = None
    if commande_outil_audio_locale:
        sortie_outil = executer_outil_local_encadre(
            nom_outil="reconnaissance_chanson_locale",
            commande_args=commande_outil_audio_locale,
            confirme_steve=confirme_execution_locale,
        )

    instruction = (
        "Tu es l'assistant musical du Studio IA de Belalingbi Steve.\n"
        "À partir des indices fournis (paroles, style, contexte, nom de fichier), "
        "propose d'éventuelles pistes de chansons ou critères de recherche en précisant "
        "toujours le niveau de certitude. N'affirme jamais une correspondance certaine "
        "sans empreinte audio vérifiée ou correspondance exacte indiscutable.\n"
        "Réponds UNIQUEMENT avec un JSON valide."
    )

    pistes = executer_requete_ia(
        type_capacite="reconnaissance_chanson",
        system_instruction=instruction,
        demande_utilisateur=indices_ou_fichier,
    )

    return {
        "entree": indices_ou_fichier,
        "analyse_indices": pistes,
        "execution_outil_local": sortie_outil,
        "statut": "Brouillon d'identification prêt — validation de Steve requise avant archivage",
        "fournisseur": pistes.get("fournisseur", "hybride"),
    }


def enregistrer_reconnaissance_validee(payload: dict, type_reconnaissance: str, confirme_steve: bool) -> Path | None:
    """
    Enregistre le résultat dans 'sorties_a_valider/reconnaissances/' UNIQUEMENT si confirme_steve est True.
    """
    if not confirme_steve:
        return None
    DOSSIER_RECONNAISSANCE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    type_sain = assainir_nom_fichier(type_reconnaissance, "reconnaissance")
    cible = valider_chemin_confine(DOSSIER_RECONNAISSANCE / f"{type_sain}_{stamp}.json", DOSSIER_SORTIES)
    cible.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return cible
