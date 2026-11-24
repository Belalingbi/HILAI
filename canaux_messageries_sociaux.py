"""
canaux_messageries_sociaux.py — Préparation encadrée de communications (mails, messages, vocaux).

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop »
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from connecteurs_et_sauvegarde import executer_outil_local_encadre
from ia_fournisseur import executer_requete_ia
from securite_garde_fous import (
    assainir_nom_fichier,
    masquer_secrets,
    valider_chemin_confine,
)

DOSSIER_SORTIES = Path("sorties_a_valider")
DOSSIER_BROUILLONS_COM = DOSSIER_SORTIES / "communications_a_valider"

CANAUX_SUPPORTES = {
    "telegram": {"categorie": "reseau_social_messagerie", "protocole_type": "Bot API / connecteur encadré"},
    "slack": {"categorie": "reseau_social_messagerie", "protocole_type": "Webhook / API / connecteur encadré"},
    "facebook": {"categorie": "reseau_social", "protocole_type": "Graph API / connecteur encadré"},
    "messenger": {"categorie": "messagerie_sociale", "protocole_type": "Messenger Platform / connecteur encadré"},
    "instagram": {"categorie": "reseau_social", "protocole_type": "Instagram API / connecteur encadré"},
    "tiktok": {"categorie": "reseau_social", "protocole_type": "Content Posting API / connecteur encadré"},
    "youtube": {"categorie": "reseau_social_video", "protocole_type": "YouTube Data API / connecteur encadré"},
    "gmail": {"categorie": "messagerie_mail", "protocole_type": "Gmail API / IMAP-SMTP encadré"},
    "gmx": {"categorie": "messagerie_mail", "protocole_type": "IMAP / SMTP encadré"},
    "proton": {"categorie": "messagerie_mail", "protocole_type": "Bridge local / IMAP-SMTP encadré"},
    "microsoft": {"categorie": "messagerie_mail", "protocole_type": "Microsoft Graph / IMAP-SMTP encadré"},
}


def preparer_communication(
    canal: str,
    format_sortie: str,
    intention_steve: str,
    destinataire_ou_cible: str = "",
    ton: str = "clair, sobre et respectueux",
) -> dict[str, Any]:
    """
    Prépare un brouillon de mail, message texte ou message vocal pour un canal donné,
    sans aucun envoi automatique.
    """
    canal_norm = canal.strip().lower()
    format_norm = format_sortie.strip().lower()  # "mail", "message", "vocal"
    infos_canal = CANAUX_SUPPORTES.get(
        canal_norm,
        {"categorie": "canal_personnalise", "protocole_type": "Connecteur local encadré"},
    )

    instruction = (
        "Tu es l'assistant de communication du Studio IA de Belalingbi Steve.\n"
        "Règles absolues :\n"
        "- Tu prépares uniquement des BROUILLONS. Aucun envoi n'est déclenché sans accord explicite.\n"
        "- Adapte le format, le niveau de langue et la longueur aux standards du canal choisi.\n"
        "- Pour les messages vocaux, écris un script naturel, facile à lire à haute voix, "
        "avec indication du rythme et durée estimée en secondes.\n"
        "- Ne divulgue aucun secret, mot de passe ou identifiant dans le texte préparé.\n"
        "Réponds UNIQUEMENT avec un JSON valide :\n"
        "{\n"
        '  "objet_ou_titre": "Objet du mail ou titre du message",\n'
        '  "canal": "nom du canal",\n'
        '  "format": "mail | message | vocal",\n'
        '  "destinataire": "Destinataire ou public visé",\n'
        '  "texte_principal": "Corps complet du message",\n'
        '  "script_vocal": "Script oral si format=vocal, sinon chaîne vide",\n'
        '  "duree_estimee_sec": 0,\n'
        '  "points_de_vigilance": ["Point 1", "Point 2"]\n'
        "}"
    )

    dossier = executer_requete_ia(
        type_capacite="communication",
        system_instruction=instruction,
        demande_utilisateur=intention_steve,
        temperature=0.35,
        contexte_supplementaire={
            "canal": canal_norm,
            "format_sortie": format_norm,
            "destinataire_ou_cible": destinataire_ou_cible,
            "ton": ton,
            "infos_canal": infos_canal,
        },
    )

    dossier.setdefault("infos_canal", infos_canal)
    return dossier


def enregistrer_brouillon_communication(dossier_com: dict, confirme_steve: bool) -> Path | None:
    """
    Enregistre le brouillon dans 'sorties_a_valider/communications_a_valider/'
    UNIQUEMENT si confirme_steve est True.
    """
    if not confirme_steve:
        return None
    DOSSIER_BROUILLONS_COM.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    canal = assainir_nom_fichier(str(dossier_com.get("canal", "communication")), "canal")
    cible = valider_chemin_confine(DOSSIER_BROUILLONS_COM / f"{canal}_{stamp}.json", DOSSIER_SORTIES)
    cible.write_text(json.dumps(dossier_com, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return cible


def envoyer_communication_encadree(
    commande_envoi_locale: list[str],
    confirme_envoi_steve: bool,
) -> dict:
    """
    Exécute un script d'envoi externe (mail ou message) UNIQUEMENT si confirme_envoi_steve est True.
    """
    return executer_outil_local_encadre(
        nom_outil="envoi_canal_externe",
        commande_args=commande_envoi_locale,
        confirme_steve=confirme_envoi_steve,
    )
