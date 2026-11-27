"""
registre_studio.py — Registre central des capacités modulaires de HILAI Studio v2.0.

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop »
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import importlib
import json
from typing import Any

from fiabilite_studio import parser_json_robuste


CAPACITES_ENREGISTREES = {
    "atelier": {
        "label": "Atelier standard (1 à 4)",
        "module": "studio_coeur",
        "fonction": "preparer_proposition_atelier",
    },
    "montage_video_autonome": {
        "label": "Montage vidéo autonome (instructions écrites)",
        "module": "montage_video_studio",
        "fonction": "preparer_montage_video_autonome",
    },
    "connecteur_plateformes": {
        "label": "Connecteur plateformes montage (Premiere/DaVinci/CapCut/FFmpeg)",
        "module": "montage_video_studio",
        "fonction": "preparer_connecteur_plateforme",
    },
    "generation_images_infinie": {
        "label": "Génération d'images infinie (flux continu)",
        "module": "generateur_media_infini",
        "fonction": "preparer_lot_generation_images",
    },
    "generation_videos_infinie": {
        "label": "Génération de vidéos infinie (séquences continues)",
        "module": "generateur_media_infini",
        "fonction": "preparer_lot_generation_videos",
    },
    "conversation_multimodale": {
        "label": "Conversation multimodale & décisionnelle (Voix/Caméra/Médias)",
        "module": "ia_fournisseur",
        "fonction": "repondre_conversation_multimodale_direct",
    },
    "site_web": {
        "label": "Création de site internet",
        "module": "studio_coeur",
        "fonction": "preparer_site_web",
    },
    "code": {
        "label": "Génération de code de programmation",
        "module": "studio_coeur",
        "fonction": "preparer_code",
    },
    "video_photo": {
        "label": "Préparation vidéo depuis photo",
        "module": "studio_coeur",
        "fonction": "preparer_fiche_video",
    },
    "reconnaissance_photo": {
        "label": "Reconnaissance de photo",
        "module": "reconnaissance_photo_chanson",
        "fonction": "reconnaitre_photo",
    },
    "reconnaissance_chanson": {
        "label": "Reconnaissance de chanson",
        "module": "reconnaissance_photo_chanson",
        "fonction": "reconnaitre_chanson",
    },
    "maths_geometrie": {
        "label": "Mathématiques & Géométrie",
        "module": "mathematiques_geometrie",
        "fonction": "resoudre_math_ou_geometrie",
    },
    "communication": {
        "label": "Réseaux sociaux, Messageries & Vocaux",
        "module": "canaux_messageries_sociaux",
        "fonction": "preparer_communication",
    },
    "marketing_bi": {
        "label": "Marketing, SEO, Ads, Analytics & Power BI",
        "module": "marketing_seo_ads_bi",
        "fonction": "preparer_dossier_marketing_bi",
    },
}


def verifier_disponibilite_capacites() -> dict[str, dict[str, Any]]:
    etat: dict[str, dict[str, Any]] = {}
    for cle, meta in CAPACITES_ENREGISTREES.items():
        nom_mod = meta["module"]
        nom_fn = meta["fonction"]
        try:
            mod = importlib.import_module(nom_mod)
            fn_ok = hasattr(mod, nom_fn) and callable(getattr(mod, nom_fn))
            etat[cle] = {
                "label": meta["label"],
                "disponible": fn_ok,
                "module": nom_mod,
                "fonction": nom_fn,
            }
        except Exception as exc:
            etat[cle] = {
                "label": meta["label"],
                "disponible": False,
                "module": nom_mod,
                "fonction": nom_fn,
                "erreur": str(exc),
            }
    return etat


def _adapter_kwargs(capacite: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    copie = dict(kwargs)
    if capacite == "video_photo":
        if "photo_source" not in copie and "chemin_photo" in copie:
            copie["photo_source"] = copie.pop("chemin_photo")
        copie.setdefault("photo_source", "photo_source.jpg")
        copie.setdefault("demande_steve", "")
    elif capacite == "reconnaissance_photo":
        if "chemin_photo_str" not in copie and "chemin_photo" in copie:
            copie["chemin_photo_str"] = copie.pop("chemin_photo")
    elif capacite == "montage_video_autonome":
        copie.setdefault("instruction", copie.pop("demande_steve", "Montage vidéo dynamique"))
        copie.setdefault("pieces_jointes", [])
        copie.setdefault("plateforme", "ffmpeg_hilai")
    elif capacite == "connecteur_plateformes":
        copie.setdefault("plateforme", "premiere_pro")
        copie.setdefault("instruction", copie.pop("demande_steve", "Export timeline"))
        copie.setdefault("pieces_jointes", [])
    elif capacite == "generation_images_infinie":
        copie.setdefault("prompt", copie.pop("demande_steve", "Création visuelle HILAI"))
    elif capacite == "generation_videos_infinie":
        copie.setdefault("prompt", copie.pop("demande_steve", "Séquence vidéo HILAI"))
    elif capacite == "conversation_multimodale":
        copie.setdefault("demande_steve", copie.pop("instruction", "Bonjour HILAI"))
    return copie


def normaliser_resultat(capacite: str, brut: Any) -> dict[str, Any]:
    if isinstance(brut, str):
        brut = parser_json_robuste(brut)
    elif not isinstance(brut, dict):
        brut = {"valeur": brut}

    titre = (
        brut.get("titre")
        or brut.get("titre_module")
        or brut.get("nom_projet")
        or brut.get("titre_sequence")
        or brut.get("objet_ou_titre")
        or f"Proposition — {capacite}"
    )

    resume = (
        brut.get("resume")
        or brut.get("analyse_rapide")
        or brut.get("resume_architecture")
        or brut.get("explication_technique")
        or brut.get("resume_visuel")
        or brut.get("resultat_exact")
        or brut.get("statut")
        or "Brouillon préparé pour validation de Belalingbi Steve."
    )

    if "timeline_tracks" in brut:
        pistes_txt = "\n".join(
            f"  [{t['debut']:.1f}s -> {t['fin']:.1f}s] {t['piste']} : {t['label']} ({t['effet']})"
            for t in brut.get("timeline_tracks", [])
        )
        fichiers_txt = ", ".join(brut.get("apercu_fichiers", []))
        contenu = (
            f"Plateforme cible : {brut.get('plateforme_cible', '')}\n"
            f"Paramètres : {json.dumps(brut.get('parametres', {}), ensure_ascii=False)}\n\n"
            f"Timeline autonome générée :\n{pistes_txt}\n\n"
            f"Fichiers d'export préparés : {fichiers_txt}"
        )
    elif "reponse_conversation" in brut:
        contenu = str(brut["reponse_conversation"])
    elif "proposition_detaillee" in brut:
        contenu = str(brut["proposition_detaillee"])
    elif "code" in brut:
        contenu = (
            f"Fichier : {brut.get('nom_fichier', 'module')}\n"
            f"Tests : {brut.get('commandes_test', '')}\n\n"
            f"{brut['code']}"
        )
    elif "index_html" in brut:
        contenu = (
            f"Architecture :\n{brut.get('resume_architecture', '')}\n\n"
            f"HTML :\n{brut['index_html']}"
        )
    elif "prompt_video_detaille" in brut:
        contenu = (
            f"Photo : {brut.get('photo_source', '')}\n"
            f"Paramètres : {json.dumps(brut.get('parametres_suggeres', {}), ensure_ascii=False)}\n"
            f"Prompt vidéo :\n{brut['prompt_video_detaille']}\n"
            f"Vigilance : {brut.get('vigilance_coherence', '')}"
        )
    elif "elements_identifies" in brut:
        contenu = (
            f"Résumé : {brut.get('resume_visuel', '')}\n"
            f"Éléments : {', '.join(brut.get('elements_identifies', []))}\n"
            f"Texte détecté : {brut.get('texte_detecte', '')}\n"
            f"Certitude : {brut.get('niveau_certitude', '')}\n"
            f"Vigilance : {brut.get('points_incertains_ou_vigilance', '')}"
        )
    elif "etapes_resolution" in brut:
        etapes = "\n".join(f"- {e}" for e in brut.get("etapes_resolution", []))
        contenu = (
            f"Domaine : {brut.get('domaine_detecte', '')}\n"
            f"Étapes :\n{etapes}\n\n"
            f"Résultat exact : {brut.get('resultat_exact', '')}\n"
            f"Valeur approchée : {brut.get('valeur_approchee', '')}\n"
            f"Vigilance : {brut.get('verification_et_vigilance', '')}"
        )
    elif "brouillon_texte" in brut:
        contenu = (
            f"Canal : {brut.get('canal', '')} ({brut.get('format', '')})\n"
            f"Objet/Titre : {brut.get('objet_ou_titre', '')}\n\n"
            f"Texte :\n{brut['brouillon_texte']}\n\n"
            f"Script vocal :\n{brut.get('script_vocal', '')}"
        )
    elif "livrable_detaille" in brut:
        contenu = str(brut["livrable_detaille"])
    else:
        contenu = json.dumps(
            {k: v for k, v in brut.items() if k not in {"image_png_bytes", "sequence_video"}},
            indent=2,
            ensure_ascii=False,
        )

    points_val = (
        brut.get("points_validation")
        or brut.get("points_validation_humaine")
        or brut.get("points_verification_avant_envoi")
        or ["Validation explicite de Belalingbi Steve avant archivage ou exécution"]
    )

    return {
        "capacite": capacite,
        "titre": str(titre),
        "resume": str(resume),
        "contenu_principal": contenu,
        "points_validation": list(points_val) if isinstance(points_val, list) else [str(points_val)],
        "donnee_brute": brut,
    }


def executer_capacite(capacite: str, **kwargs: Any) -> dict[str, Any]:
    if capacite not in CAPACITES_ENREGISTREES:
        raise ValueError(f"Capacité inconnue : {capacite}")

    meta = CAPACITES_ENREGISTREES[capacite]
    mod = importlib.import_module(meta["module"])
    fn = getattr(mod, meta["fonction"])
    kwargs_adaptes = _adapter_kwargs(capacite, kwargs)
    brut = fn(**kwargs_adaptes)
    return normaliser_resultat(capacite, brut)
