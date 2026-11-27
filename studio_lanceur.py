"""
studio_lanceur.py — Lanceur unifié CLI & GUI Ergonomique v2.0 pour HILAI Studio.

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop » v2.0
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import argparse
import base64
import json
import os
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, scrolledtext, ttk
from typing import Any

from connecteurs_et_sauvegarde import sauvegarder_snapshot_studio
from fiabilite_studio import lire_aperçu_sortie_securise
from generateur_media_infini import (
    STYLES_VISUELS,
    ControleurFluxInfini,
    generer_image_procedurale,
)
from ia_fournisseur import obtenir_mode_fournisseur
from montage_video_studio import (
    PLATEFORMES_MONTAGE,
    executer_et_exporter_montage,
)
from multimodal_capteurs import (
    OPENCV_DISPONIBLE,
    PILLOW_DISPONIBLE,
    AnalyseurVisionCamera,
    EnregistreurVocalStudio,
    SyntheseVocaleStudio,
    obtenir_metriques_systeme,
)
from parametres_studio import (
    THEMES_PREDEFINIS,
    appliquer_theme,
    charger_configuration_studio,
    enregistrer_cle_env_securisee,
    obtenir_config_defaut,
    sauvegarder_configuration_studio,
)
from registre_studio import (
    CAPACITES_ENREGISTREES,
    executer_capacite,
)
from securite_garde_fous import (
    analyser_demande_securite,
    masquer_secrets,
    valider_piece_jointe_securisee,
)
from studio_coeur import (
    ATELIERS,
    enregistrer_brouillon_code_valide,
    enregistrer_brouillon_web_valide,
    enregistrer_fiche_video_validee,
    enregistrer_validation_et_sortie,
    generer_fichier_binaire,
    lire_historique_journaux,
    lire_journal_jour,
    lister_sorties_validees,
)
from verifier_studio import verifier_tout


def _construire_kwargs_capacite(
    capacite: str,
    demande: str,
    atelier_slug: str,
    photo_ou_cible: str,
    domaine_ou_canal: str,
    format_com: str,
    pieces_jointes: list[str] | None = None,
    plateforme_montage: str = "ffmpeg_hilai",
    parametres_media: dict[str, Any] | None = None,
    observation_camera: str = "",
    note_vocale: str = "",
) -> dict[str, Any]:
    params = parametres_media or {}
    if capacite == "atelier":
        return {"atelier_cle": atelier_slug, "demande_steve": demande}
    if capacite == "montage_video_autonome":
        return {
            "instruction": demande or "Montage vidéo dynamique avec sous-titres et transitions",
            "pieces_jointes": pieces_jointes or [],
            "plateforme": plateforme_montage,
            "parametres": params,
        }
    if capacite == "connecteur_plateformes":
        return {
            "plateforme": plateforme_montage,
            "instruction": demande or "Export timeline multi-pistes vers plateforme de montage",
            "pieces_jointes": pieces_jointes or [],
        }
    if capacite == "generation_images_infinie":
        return {
            "prompt": demande or "Visuel futuriste HILAI",
            "style": params.get("style", "Cyberpunk / Néon"),
            "resolution": params.get("resolution", "512x512"),
        }
    if capacite == "generation_videos_infinie":
        return {
            "prompt": demande or "Séquence vidéo dynamique HILAI",
            "style": params.get("style", "Cinématique / Studio"),
            "duree_sec": int(params.get("duree_sec", 6)),
        }
    if capacite == "conversation_multimodale":
        return {
            "demande_steve": demande or "Analyse la situation et propose les meilleures options.",
            "pieces_jointes": pieces_jointes or [],
            "observation_camera": observation_camera,
            "note_vocale": note_vocale,
        }
    if capacite == "site_web":
        return {"demande_steve": demande}
    if capacite == "code":
        return {"demande_steve": demande}
    if capacite == "video_photo":
        return {"photo_source": photo_ou_cible or "photo_source.jpg", "demande_steve": demande}
    if capacite == "reconnaissance_photo":
        return {
            "chemin_photo_str": photo_ou_cible or "photo_source.jpg",
            "question_complementaire": demande,
        }
    if capacite == "reconnaissance_chanson":
        return {"indices_ou_fichier": demande or photo_ou_cible}
    if capacite == "maths_geometrie":
        return {"enonce_steve": demande, "domaine": domaine_ou_canal or "auto"}
    if capacite == "communication":
        return {
            "canal": domaine_ou_canal or "gmail",
            "format_sortie": format_com or "mail",
            "intention_steve": demande,
            "destinataire_ou_cible": photo_ou_cible,
        }
    if capacite == "marketing_bi":
        return {
            "domaine": domaine_ou_canal or "seo",
            "objectif_steve": demande,
            "contexte_ou_donnees": photo_ou_cible,
        }
    raise ValueError(f"Capacité non gérée : {capacite}")


def _enregistrer_resultat_normalise(
    resultat_norm: dict,
    atelier_slug: str,
    demande: str,
    decision: str,
    justification: str,
    valider_sortie: bool,
    plateforme_montage: str = "ffmpeg_hilai",
    lancer_rendu_ffmpeg: bool = False,
) -> list[str]:
    messages: list[str] = []
    capacite = resultat_norm.get("capacite", "atelier")
    brut = resultat_norm.get("donnee_brute", {})
    chemin_specifique: Path | str | None = None

    if capacite in {"montage_video_autonome", "connecteur_plateformes"} and valider_sortie:
        res_montage = executer_et_exporter_montage(
            plan_montage=brut,
            plateforme=plateforme_montage,
            confirme_steve=True,
            lancer_rendu_ffmpeg=lancer_rendu_ffmpeg,
        )
        chemin_specifique = Path(res_montage["dossier"])
        messages.append(
            f"Montage exporté ({len(res_montage['fichiers'])} fichier(s)) : {chemin_specifique}"
        )
    elif capacite == "site_web" and valider_sortie:
        chemin_specifique = enregistrer_brouillon_web_valide(brut, True)
        messages.append(f"Brouillon web enregistré : {chemin_specifique}")
    elif capacite == "code" and valider_sortie:
        chemin_specifique = enregistrer_brouillon_code_valide(brut, True)
        messages.append(f"Module code enregistré : {chemin_specifique}")
    elif capacite == "video_photo" and valider_sortie:
        chemin_specifique = enregistrer_fiche_video_validee(brut, True)
        messages.append(f"Fiche vidéo enregistrée : {chemin_specifique}")
    elif capacite == "reconnaissance_photo" and valider_sortie:
        from reconnaissance_photo_chanson import enregistrer_reconnaissance_validee
        chemin_specifique = enregistrer_reconnaissance_validee(brut, "photo", True)
        messages.append(f"Reconnaissance photo enregistrée : {chemin_specifique}")
    elif capacite == "reconnaissance_chanson" and valider_sortie:
        from reconnaissance_photo_chanson import enregistrer_reconnaissance_validee
        chemin_specifique = enregistrer_reconnaissance_validee(brut, "chanson", True)
        messages.append(f"Reconnaissance chanson enregistrée : {chemin_specifique}")
    elif capacite == "maths_geometrie" and valider_sortie:
        from mathematiques_geometrie import enregistrer_resolution_validee
        chemin_specifique = enregistrer_resolution_validee(brut, True)
        messages.append(f"Résolution maths/géométrie enregistrée : {chemin_specifique}")
    elif capacite == "communication" and valider_sortie:
        from canaux_messageries_sociaux import enregistrer_brouillon_communication
        chemin_specifique = enregistrer_brouillon_communication(brut, True)
        messages.append(f"Brouillon communication enregistré : {chemin_specifique}")
    elif capacite == "marketing_bi" and valider_sortie:
        from marketing_seo_ads_bi import enregistrer_dossier_marketing_valide
        chemin_specifique = enregistrer_dossier_marketing_valide(brut, True)
        messages.append(f"Dossier marketing/BI enregistré : {chemin_specifique}")

    # Traçabilité obligatoire dans le journal quotidien & mémoire multi-jours
    dossier_journal = {
        "titre": resultat_norm.get("titre", f"Proposition — {capacite}"),
        "avis_ia": resultat_norm.get("resume", ""),
        "proposition_detaillee": (
            f"Fichier créé : {chemin_specifique}\n\n" + str(resultat_norm.get("contenu_principal", ""))
            if chemin_specifique else str(resultat_norm.get("contenu_principal", ""))
        ),
    }
    journal_nom, etat_sortie = enregistrer_validation_et_sortie(
        atelier_cle=atelier_slug if capacite == "atelier" else capacite,
        demande_steve=demande,
        dossier=dossier_journal,
        decision_steve=decision,
        justification_steve=justification,
        valider_dans_sorties=(
            valider_sortie
            and capacite in {"atelier", "generation_images_infinie", "generation_videos_infinie", "conversation_multimodale"}
        ),
    )
    messages.append(f"Journal quotidien : {journal_nom}")
    if not chemin_specifique:
        messages.append(etat_sortie)
    else:
        messages.append(f"Statut fichier : {chemin_specifique}")

    return messages


def executer_cli() -> None:
    from verifier_studio import afficher_rapport

    print("\n=== HILAI STUDIO v2.0 — CLI UNIVERSEL (WINDOWS / LINUX / MACOS) ===")
    cles = list(CAPACITES_ENREGISTREES.keys())
    for idx, cle in enumerate(cles, start=1):
        print(f"  {idx:2d}. {CAPACITES_ENREGISTREES[cle]['label']} ({cle})")
    print(f"  {len(cles) + 1:2d}. Relire journal & sorties validées")
    print(f"  {len(cles) + 2:2d}. Lancer le diagnostic sécurité & modules")

    choix_raw = input(f"Choix [1-{len(cles) + 2}, défaut=1] : ").strip()
    try:
        choix = int(choix_raw) if choix_raw else 1
    except ValueError:
        choix = 1

    if choix == len(cles) + 1:
        print("\n--- JOURNAL DU JOUR ---")
        print(lire_journal_jour())
        print("\n--- SORTIES DANS sorties_a_valider/ ---")
        for p in lister_sorties_validees():
            print(f"  - {p}")
        return

    if choix == len(cles) + 2:
        afficher_rapport(verifier_tout())
        return

    capacite = cles[choix - 1] if 1 <= choix <= len(cles) else "atelier"
    atelier_slug = "recherche_connaissance_conseil"
    if capacite == "atelier":
        for k, (_, lib) in ATELIERS.items():
            print(f"    {k}. {lib}")
        sel_at = input("Atelier [1-4, défaut=2] : ").strip()
        atelier_slug = ATELIERS.get(sel_at, ATELIERS["2"])[0]

    plateforme_montage = "ffmpeg_hilai"
    if capacite in {"montage_video_autonome", "connecteur_plateformes"}:
        print("Plateformes disponibles :", ", ".join(PLATEFORMES_MONTAGE.keys()))
        plateforme_montage = input("Plateforme cible [défaut=ffmpeg_hilai] : ").strip() or "ffmpeg_hilai"

    photo_ou_cible = ""
    if capacite in {"video_photo", "reconnaissance_photo", "communication", "marketing_bi"}:
        photo_ou_cible = input("Photo source / cible / contexte (optionnel) : ").strip()

    domaine_ou_canal = ""
    if capacite in {"maths_geometrie", "communication", "marketing_bi"}:
        domaine_ou_canal = input(
            "Domaine ou canal (ex. seo, google_ads, power_bi, gmail, telegram, auto) : "
        ).strip()

    format_com = "mail"
    if capacite == "communication":
        format_com = input("Format communication [mail / message / vocal, défaut=mail] : ").strip() or "mail"

    demande = input("Steve, quelle est ta demande ou instruction ? ").strip()
    if not demande and not photo_ou_cible:
        print("Entrée vide : opération annulée.")
        return

    print("Préparation en cours...")
    kwargs = _construire_kwargs_capacite(
        capacite=capacite,
        demande=demande,
        atelier_slug=atelier_slug,
        photo_ou_cible=photo_ou_cible,
        domaine_ou_canal=domaine_ou_canal,
        format_com=format_com,
        plateforme_montage=plateforme_montage,
    )
    res_norm = executer_capacite(capacite, **kwargs)

    print(f"\n=== {res_norm['titre']} ===")
    print(f"Résumé : {res_norm['resume']}\n")
    print(res_norm["contenu_principal"])
    print("\nPoints de validation suggérés :")
    for pt in res_norm["points_validation"]:
        print(f"  * {pt}")

    decision = input("\nSteve, quelle décision retiens-tu ? ").strip()
    justification = input("Justification (optionnelle) : ").strip()
    conf = input("Valider et enregistrer dans 'sorties_a_valider/' (oui/non) ? ").strip().lower()
    valider = conf in {"oui", "o", "yes", "y"}

    msgs = _enregistrer_resultat_normalise(
        resultat_norm=res_norm,
        atelier_slug=atelier_slug,
        demande=demande,
        decision=decision,
        justification=justification,
        valider_sortie=valider,
        plateforme_montage=plateforme_montage,
    )
    for m in msgs:
        print(f"  -> {m}")


# ==============================================================================
# FENÊTRE PARAMÈTRES, COULEURS & SÉCURITÉ (MENU PARAMÈTRE COMPLET)
# ==============================================================================

class FenetreParametresHILAI(tk.Toplevel):
    """Dialogue ergonomique de gestion des réglages, couleurs d'interface, IA et sécurité."""

    def __init__(self, parent_app: "ApplicationStudioGUI") -> None:
        super().__init__(parent_app.root)
        self.app = parent_app
        self.config_locale = charger_configuration_studio()
        self.couleurs_edit = dict(self.config_locale["couleurs"])

        self.title("⚙️ Paramètres HILAI Studio v2.0 — Couleurs, IA & Cybersécurité")
        self.geometry("680x640")
        self.resizable(False, False)
        self.transient(parent_app.root)
        self.grab_set()

        c = self.app.couleurs
        self.configure(bg=c["bg_main"])

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        tab_apparence = ttk.Frame(notebook, padding=12)
        tab_ia = ttk.Frame(notebook, padding=12)
        tab_secu = ttk.Frame(notebook, padding=12)

        notebook.add(tab_apparence, text="🎨 Couleurs & Interface")
        notebook.add(tab_ia, text="🤖 IA, Voix & Caméra")
        notebook.add(tab_secu, text="🛡️ Cybersécurité & Quotas")

        self._construire_tab_apparence(tab_apparence)
        self._construire_tab_ia(tab_ia)
        self._construire_tab_secu(tab_secu)

        barre_bas = tk.Frame(self, bg=c["bg_main"])
        barre_bas.pack(fill=tk.X, padx=12, pady=(0, 12))

        tk.Button(
            barre_bas, text="Réinitialiser défaut", bg="#475569", fg="white",
            relief=tk.FLAT, padx=12, pady=6, command=self._reinitialiser
        ).pack(side=tk.LEFT)

        tk.Button(
            barre_bas, text="Annuler", bg="#334155", fg="white",
            relief=tk.FLAT, padx=12, pady=6, command=self.destroy
        ).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(
            barre_bas, text="💾 Appliquer & Sauvegarder", bg=c["accent_green"], fg="#0f172a",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=14, pady=6, command=self._sauvegarder
        ).pack(side=tk.RIGHT)

    def _construire_tab_apparence(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Thème prédéfini de l'interface :", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.var_theme = tk.StringVar(value=self.config_locale.get("theme", "CyberMidnight Dark"))
        themes = list(THEMES_PREDEFINIS.keys()) + ["Personnalisé"]
        combo_theme = ttk.Combobox(parent, textvariable=self.var_theme, values=themes, state="readonly", width=36)
        combo_theme.pack(anchor=tk.W, pady=(4, 12))
        combo_theme.bind("<<ComboboxSelected>>", self._on_theme_change)

        ttk.Label(parent, text="Personnalisation fine des couleurs :", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(4, 6))

        champs = [
            ("bg_main", "Arrière-plan principal"),
            ("bg_panel", "Fond des panneaux"),
            ("bg_input", "Zone de saisie & logs"),
            ("fg_text", "Couleur du texte"),
            ("accent", "Couleur d'accentuation"),
            ("accent_green", "Bouton de validation"),
        ]
        self.boutons_couleurs: dict[str, tk.Button] = {}
        for cle, libelle in champs:
            row = ttk.Frame(parent)
            row.pack(fill=tk.X, pady=3)
            ttk.Label(row, text=libelle, width=28).pack(side=tk.LEFT)
            hex_val = self.couleurs_edit.get(cle, "#38bdf8")
            btn = tk.Button(
                row, text=hex_val, bg=hex_val, fg="#000000" if cle != "bg_input" else "#ffffff",
                width=14, relief=tk.FLAT, command=lambda k=cle: self._choisir_couleur(k)
            )
            btn.pack(side=tk.LEFT, padx=8)
            self.boutons_couleurs[cle] = btn

        ttk.Label(parent, text="Nom de l'opérateur / décideur :", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(14, 4))
        self.var_proprio = tk.StringVar(value=self.config_locale.get("proprietaire", "Belalingbi Steve"))
        ttk.Entry(parent, textvariable=self.var_proprio, width=40).pack(anchor=tk.W)

    def _on_theme_change(self, _event: tk.Event | None = None) -> None:
        nom = self.var_theme.get()
        if nom in THEMES_PREDEFINIS:
            self.couleurs_edit = dict(THEMES_PREDEFINIS[nom])
            for cle, btn in self.boutons_couleurs.items():
                val = self.couleurs_edit.get(cle, "#38bdf8")
                btn.config(text=val, bg=val)

    def _choisir_couleur(self, cle: str) -> None:
        _, hex_code = colorchooser.askcolor(color=self.couleurs_edit.get(cle, "#38bdf8"), title=f"Choisir {cle}")
        if hex_code:
            self.var_theme.set("Personnalisé")
            self.couleurs_edit[cle] = hex_code
            self.boutons_couleurs[cle].config(text=hex_code, bg=hex_code)

    def _construire_tab_ia(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Mode d'exécution IA :", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.var_mode_ia = tk.StringVar(value=self.config_locale.get("mode_ia", "hybride"))
        ttk.Combobox(
            parent, textvariable=self.var_mode_ia,
            values=["hybride", "local_autonome", "gemini_cloud"], state="readonly", width=30
        ).pack(anchor=tk.W, pady=(4, 10))

        ttk.Label(parent, text="Modèle Gemini Cloud (si clé configurée) :", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.var_modele = tk.StringVar(value=self.config_locale.get("modele_gemini", "gemini-2.5-flash"))
        ttk.Combobox(
            parent, textvariable=self.var_modele,
            values=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"], width=30
        ).pack(anchor=tk.W, pady=(4, 10))

        ttk.Label(parent, text="Clé API Gemini (.env local uniquement, jamais partagée) :", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.var_cle_api = tk.StringVar(value="")
        ttk.Entry(parent, textvariable=self.var_cle_api, show="*", width=44).pack(anchor=tk.W, pady=(4, 4))
        ttk.Label(parent, text="(Laissez vide pour conserver la configuration actuelle ou rester en mode local autonome)").pack(anchor=tk.W, pady=(0, 10))

        self.var_tts = tk.BooleanVar(value=bool(self.config_locale.get("reponse_vocale_active", True)))
        ttk.Checkbutton(parent, text="Activer la réponse vocale IA par défaut", variable=self.var_tts).pack(anchor=tk.W, pady=3)

        self.var_cam_auto = tk.BooleanVar(value=bool(self.config_locale.get("camera_auto_analyse", True)))
        ttk.Checkbutton(parent, text="Activer l'analyse & prise de décision caméra auto", variable=self.var_cam_auto).pack(anchor=tk.W, pady=3)

        row_fps = ttk.Frame(parent)
        row_fps.pack(fill=tk.X, pady=(10, 4))
        ttk.Label(row_fps, text="Intervalle génération infinie (sec) :", width=32).pack(side=tk.LEFT)
        self.var_intervalle = tk.DoubleVar(value=float(self.config_locale.get("intervalle_generation_sec", 2.0)))
        ttk.Spinbox(row_fps, from_=0.5, to=30.0, increment=0.5, textvariable=self.var_intervalle, width=8).pack(side=tk.LEFT)

    def _construire_tab_secu(self, parent: ttk.Frame) -> None:
        ttk.Label(
            parent,
            text="🛡️ Durcissement Cybersécurité & Garde-fous Human-in-the-Loop",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W, pady=(0, 8))

        regles = [
            "• Sas de validation humaine (confirme_steve is True) : VERROUILLÉ ACTIF",
            "• Anti-Prompt Injection & balises <untrusted_input> : ACTIF",
            "• Anti-Path Traversal & confinement canonique sorties_a_valider/ : ACTIF",
            "• Anti-Command Injection (shell=False + liste blanche FFmpeg/Python) : ACTIF",
            "• Inspection octets magiques & blocage exécutables (.exe/.bat/.ps1) : ACTIF",
            "• Scrubber automatique de clés API, JWT et secrets : ACTIF",
        ]
        for r in regles:
            ttk.Label(parent, text=r).pack(anchor=tk.W, pady=2)

        row_pj = ttk.Frame(parent)
        row_pj.pack(fill=tk.X, pady=(14, 4))
        ttk.Label(row_pj, text="Taille max d'une pièce jointe (Mo) :", width=34).pack(side=tk.LEFT)
        self.var_max_pj = tk.IntVar(value=int(self.config_locale.get("taille_max_piece_jointe_mo", 250)))
        ttk.Spinbox(row_pj, from_=5, to=2048, increment=10, textvariable=self.var_max_pj, width=8).pack(side=tk.LEFT)

        row_q = ttk.Frame(parent)
        row_q.pack(fill=tk.X, pady=4)
        ttk.Label(row_q, text="Quota tampon flux infini (Mo) :", width=34).pack(side=tk.LEFT)
        self.var_quota = tk.IntVar(value=int(self.config_locale.get("quota_flux_infini_mo", 256)))
        ttk.Spinbox(row_q, from_=32, to=2048, increment=32, textvariable=self.var_quota, width=8).pack(side=tk.LEFT)

    def _reinitialiser(self) -> None:
        defaut = obtenir_config_defaut()
        self.var_theme.set(defaut["theme"])
        self.couleurs_edit = dict(defaut["couleurs"])
        self._on_theme_change()

    def _sauvegarder(self) -> None:
        nouvelle_cfg = dict(self.config_locale)
        nouvelle_cfg["proprietaire"] = self.var_proprio.get().strip() or "Belalingbi Steve"
        nouvelle_cfg["mode_ia"] = self.var_mode_ia.get()
        nouvelle_cfg["modele_gemini"] = self.var_modele.get().strip() or "gemini-2.5-flash"
        nouvelle_cfg["reponse_vocale_active"] = self.var_tts.get()
        nouvelle_cfg["camera_auto_analyse"] = self.var_cam_auto.get()
        nouvelle_cfg["intervalle_generation_sec"] = float(self.var_intervalle.get())
        nouvelle_cfg["taille_max_piece_jointe_mo"] = int(self.var_max_pj.get())
        nouvelle_cfg["quota_flux_infini_mo"] = int(self.var_quota.get())
        nouvelle_cfg = appliquer_theme(nouvelle_cfg, self.var_theme.get(), self.couleurs_edit)

        cle_api = self.var_cle_api.get().strip()
        if cle_api:
            ok_cle = messagebox.askyesno(
                "Confirmation clé API",
                "Confirmes-tu l'enregistrement local de la clé GEMINI_API_KEY dans '.env' ?",
                parent=self,
            )
            if ok_cle:
                enregistrer_cle_env_securisee(cle_api, nouvelle_cfg["modele_gemini"], confirme_steve=True)

        sauvegarder_configuration_studio(nouvelle_cfg, confirme_steve=True)
        self.app.recharger_configuration_et_theme(nouvelle_cfg)
        self.destroy()


# ==============================================================================
# INTERFACE GRAPHIQUE PRINCIPALE — HILAI STUDIO v2.0 ERGONOMIQUE
# ==============================================================================

class ApplicationStudioGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config_studio = charger_configuration_studio()
        self.couleurs = dict(self.config_studio["couleurs"])

        self.root.title("HILAI Studio v2.0 — IA Universelle, Montage Autonome & Contrôle Humain")
        self.root.geometry("1420x880")
        self.root.minsize(1160, 740)
        self.root.configure(bg=self.couleurs["bg_main"])

        # États & Moteurs
        self.dernier_resultat_norm: dict[str, Any] | None = None
        self.dernier_atelier_slug: str = "recherche_connaissance_conseil"
        self.derniere_demande: str = ""
        self.chemins_sorties: list[Path] = []
        self.pieces_jointes: list[str] = []
        self.pieces_jointes_meta: list[dict[str, Any]] = []
        self.occupe = False
        self.boutons_action: list[tk.Widget] = []

        self.enregistreur_vocal = EnregistreurVocalStudio()
        self.synthese_vocale = SyntheseVocaleStudio()
        self.analyseur_vision = AnalyseurVisionCamera()
        self.flux_infini = ControleurFluxInfini(
            max_tampon=int(self.config_studio.get("max_tampon_infini", 30)),
            quota_mo=float(self.config_studio.get("quota_flux_infini_mo", 256)),
        )

        self.camera_active = False
        self.cap: Any = None
        self.cam_step = 0
        self.derniere_observation_cam = ""
        self.derniere_note_vocale = ""
        self.plateforme_selectionnee = self.config_studio.get("plateforme_montage_defaut", "ffmpeg_hilai")

        self.frames_apercu: list[bytes] = []
        self.index_frame_apercu = 0
        self.lecture_apercu_active = False
        self.miniatures_refs: list[tk.PhotoImage] = []
        self.img_apercu_ref: tk.PhotoImage | None = None

        self.var_statut = tk.StringVar(
            value=f"Prêt — L'IA prépare et conseille, {self.config_studio['proprietaire']} décide et valide."
        )

        self._configurer_styles()
        self._construire_interface()
        self._rafraichir_apercu_initial()
        self._planifier_rafraichissement_sante()

    def _configurer_styles(self) -> None:
        c = self.couleurs
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=c["bg_main"])
        style.configure("Panel.TFrame", background=c["bg_panel"])
        style.configure("TNotebook", background=c["bg_main"], borderwidth=0)
        style.configure("TNotebook.Tab", background=c["bg_panel"], foreground=c["fg_muted"], padding=(14, 6), font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", c["bg_input"])], foreground=[("selected", c["accent"])])
        style.configure("TLabel", background=c["bg_panel"], foreground=c["fg_text"], font=("Segoe UI", 9))
        style.configure("Header.TLabel", background=c["bg_main"], foreground=c["accent"], font=("Segoe UI", 13, "bold"))
        style.configure("Section.TLabel", background=c["bg_panel"], foreground=c["accent"], font=("Segoe UI", 9, "bold"))
        style.configure("TCheckbutton", background=c["bg_panel"], foreground=c["fg_text"], font=("Segoe UI", 9))
        style.configure("TCombobox", fieldbackground=c["bg_input"], background=c["bg_panel"], foreground=c["fg_text"])

    def _construire_interface(self) -> None:
        c = self.couleurs

        # --- BARRE SUPÉRIEURE ---
        self.top_bar = tk.Frame(self.root, bg=c["bg_main"], padx=14, pady=8)
        self.top_bar.pack(fill=tk.X)

        self.lbl_titre_app = tk.Label(
            self.top_bar,
            text="🛡️ HILAI STUDIO v2.0 — IA Multimodale, Montage Autonome & Contrôle Humain",
            bg=c["bg_main"], fg=c["accent"], font=("Segoe UI", 12, "bold"),
        )
        self.lbl_titre_app.pack(side=tk.LEFT)

        btn_params = tk.Button(
            self.top_bar,
            text="⚙️ Paramètres & Couleurs",
            bg=c["bg_panel"], fg=c["fg_text"],
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=4,
            command=self.ouvrir_parametres,
        )
        btn_params.pack(side=tk.RIGHT, padx=(8, 0))

        mode_txt = "Gemini Cloud + Local" if obtenir_mode_fournisseur() == "gemini_cloud" else "Moteur Local Autonome"
        self.lbl_badge_secu = tk.Label(
            self.top_bar,
            text=f"Mode : {mode_txt} | Garde-fous Cyber : ACTIFS",
            bg=c["bg_main"], fg=c["accent_green"], font=("Segoe UI", 9, "bold"),
        )
        self.lbl_badge_secu.pack(side=tk.RIGHT, padx=8)

        # --- ONGLETS PRINCIPAUX ---
        self.onglets = ttk.Notebook(self.root)
        self.onglets.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))

        self.onglet_studio = ttk.Frame(self.onglets, padding=6)
        self.onglet_relecture = ttk.Frame(self.onglets, padding=10)
        self.onglets.add(self.onglet_studio, text="🎬 Atelier, Montage & Multimodal")
        self.onglets.add(self.onglet_relecture, text="🔍 Relecture, Snapshot & Diagnostic")

        self._construire_onglet_studio(self.onglet_studio)
        self._construire_onglet_relecture(self.onglet_relecture)

        # --- BARRE D'ÉTAT BASSE ---
        barre_statut = tk.Frame(self.root, bg=c["bg_main"], padx=14, pady=3)
        barre_statut.pack(fill=tk.X)
        tk.Label(
            barre_statut, textvariable=self.var_statut, bg=c["bg_main"], fg=c["fg_muted"], font=("Segoe UI", 9)
        ).pack(side=tk.LEFT)
        tk.Label(
            barre_statut, text="CyberAnonymat Project • https://github.com/Belalingbi/",
            bg=c["bg_main"], fg=c["fg_muted"], font=("Segoe UI", 8)
        ).pack(side=tk.RIGHT)

    def _construire_onglet_studio(self, parent: ttk.Frame) -> None:
        c = self.couleurs

        # Grille principale 3 colonnes + Sas humain en bas
        corps = ttk.Frame(parent)
        corps.pack(fill=tk.BOTH, expand=True)

        # =====================================================================
        # COLONNE GAUCHE : Caméra Temps Réel + Enregistrement Vocal + Pièces Jointes
        # =====================================================================
        col_g = tk.Frame(corps, bg=c["bg_panel"], padx=10, pady=10, width=340)
        col_g.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        col_g.pack_propagate(False)

        tk.Label(col_g, text="📷 VISION & DÉCISION CAMÉRA TEMPS RÉEL", bg=c["bg_panel"], fg=c["accent"], font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)

        self.zone_camera = tk.Label(
            col_g,
            text="Caméra en veille\nCliquez « Activer Caméra IA »\npour interaction temps réel",
            bg=c["bg_input"], fg=c["fg_muted"], width=42, height=10, relief=tk.FLAT,
        )
        self.zone_camera.pack(fill=tk.X, pady=(6, 6))

        cam_ctrl = tk.Frame(col_g, bg=c["bg_panel"])
        cam_ctrl.pack(fill=tk.X, pady=(0, 6))

        self.btn_camera = tk.Button(
            cam_ctrl, text="▶ Activer Caméra IA", bg=c["accent"], fg="#0f172a",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, pady=4, command=self.basculer_camera,
        )
        self.btn_camera.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.var_cam_auto = tk.BooleanVar(value=bool(self.config_studio.get("camera_auto_analyse", True)))
        ttk.Checkbutton(cam_ctrl, text="Analyse & Parole", variable=self.var_cam_auto).pack(side=tk.RIGHT)

        self.lbl_vision_obs = tk.Label(
            col_g, text="Observation IA : En attente du flux vidéo...",
            bg=c["bg_input"], fg=c["fg_text"], anchor="w", justify=tk.LEFT,
            wraplength=310, padx=8, pady=6, font=("Segoe UI", 8),
        )
        self.lbl_vision_obs.pack(fill=tk.X, pady=(0, 10))

        # Audio / Voix
        tk.Label(col_g, text="🎙️ CONVERSATION & ENREGISTREMENT VOCAL", bg=c["bg_panel"], fg=c["accent"], font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        vocal_bar = tk.Frame(col_g, bg=c["bg_panel"])
        vocal_bar.pack(fill=tk.X, pady=(6, 10))

        self.btn_enregistrer = tk.Button(
            vocal_bar, text="⏺ Enregistrer la voix", bg=c["accent_red"], fg="white",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, pady=6, command=self.basculer_enregistrement_vocal,
        )
        self.btn_enregistrer.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.var_reponse_vocale = tk.BooleanVar(value=bool(self.config_studio.get("reponse_vocale_active", True)))
        ttk.Checkbutton(vocal_bar, text="Réponse vocale", variable=self.var_reponse_vocale).pack(side=tk.RIGHT)

        # Pièces Jointes & Import de Fichiers
        tk.Label(col_g, text="📎 PIÈCES JOINTES & IMPORT DE FICHIERS", bg=c["bg_panel"], fg=c["accent"], font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        pj_bar = tk.Frame(col_g, bg=c["bg_panel"])
        pj_bar.pack(fill=tk.X, pady=(6, 4))

        tk.Button(
            pj_bar, text="+ Importer (Image/Vocal/Vidéo/Doc)", bg=c["border"], fg=c["fg_text"],
            font=("Segoe UI", 8, "bold"), relief=tk.FLAT, pady=5, command=self.ajouter_pieces_jointes,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        tk.Button(
            pj_bar, text="Retirer", bg=c["bg_input"], fg=c["fg_text"],
            font=("Segoe UI", 8), relief=tk.FLAT, pady=5, command=self.retirer_piece_jointe,
        ).pack(side=tk.LEFT, padx=(0, 4))

        tk.Button(
            pj_bar, text="Vider", bg=c["bg_input"], fg=c["fg_muted"],
            font=("Segoe UI", 8), relief=tk.FLAT, pady=5, command=self.vider_pieces_jointes,
        ).pack(side=tk.RIGHT)

        self.liste_pj = tk.Listbox(
            col_g, bg=c["bg_input"], fg=c["fg_text"], selectbackground=c["accent"],
            relief=tk.FLAT, font=("Segoe UI", 8), height=8,
        )
        self.liste_pj.pack(fill=tk.BOTH, expand=True)

        # =====================================================================
        # COLONNE DROITE : Modules, Plateformes de Montage, Paramètres & Santé
        # =====================================================================
        col_d = tk.Frame(corps, bg=c["bg_panel"], padx=10, pady=10, width=330)
        col_d.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        col_d.pack_propagate(False)

        tk.Label(col_d, text="🧠 CAPACITÉ & AUTONOMIE IA", bg=c["bg_panel"], fg=c["accent"], font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)

        self.labels_to_cap = {
            f"{meta['label']} [{cle}]": cle for cle, meta in CAPACITES_ENREGISTREES.items()
        }
        self.combo_capacite = ttk.Combobox(
            col_d, values=list(self.labels_to_cap.keys()), state="readonly", width=40
        )
        self.combo_capacite.current(1)  # Montage vidéo autonome par défaut
        self.combo_capacite.pack(fill=tk.X, pady=(4, 6))

        # Cadrage Atelier / Contexte
        tk.Label(col_d, text="Atelier / Domaine / Cible :", bg=c["bg_panel"], fg=c["fg_muted"], font=("Segoe UI", 8)).pack(anchor=tk.W)
        self.libelles_to_slug = {lib: slug for _, (slug, lib) in ATELIERS.items()}
        self.combo_atelier = ttk.Combobox(col_d, values=list(self.libelles_to_slug.keys()), state="readonly")
        self.combo_atelier.current(1)
        self.combo_atelier.pack(fill=tk.X, pady=(2, 4))

        cadrage_row = tk.Frame(col_d, bg=c["bg_panel"])
        cadrage_row.pack(fill=tk.X, pady=(0, 8))
        self.entree_cible = ttk.Entry(cadrage_row, width=14)
        self.entree_cible.insert(0, "")
        self.entree_cible.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.entree_domaine = ttk.Entry(cadrage_row, width=11)
        self.entree_domaine.pack(side=tk.LEFT, padx=(0, 4))
        self.combo_format_com = ttk.Combobox(cadrage_row, values=["mail", "message", "vocal"], state="readonly", width=7)
        self.combo_format_com.current(0)
        self.combo_format_com.pack(side=tk.RIGHT)

        # Connecteur Plateformes de Montage
        tk.Label(col_d, text="🔌 CONNECTEUR PLATEFORMES DE MONTAGE", bg=c["bg_panel"], fg=c["accent"], font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(4, 4))

        plat_grid = tk.Frame(col_d, bg=c["bg_panel"])
        plat_grid.pack(fill=tk.X, pady=(0, 4))
        self.boutons_plateformes: dict[str, tk.Button] = {}
        plat_boutons = [
            ("premiere_pro", "Pr Premiere"),
            ("davinci_resolve", "DaVinci"),
            ("capcut", "CapCut"),
            ("ffmpeg_hilai", "FFmpeg IA"),
            ("universel_edl_xml", "EDL/XML"),
        ]
        for idx, (cle_p, txt_p) in enumerate(plat_boutons):
            b = tk.Button(
                plat_grid, text=txt_p, bg=c["bg_input"], fg=c["fg_text"],
                font=("Segoe UI", 8, "bold"), relief=tk.FLAT, pady=4,
                command=lambda p=cle_p: self.selectionner_plateforme(p),
            )
            b.grid(row=idx // 3, column=idx % 3, sticky="ew", padx=2, pady=2)
            self.boutons_plateformes[cle_p] = b
        for col_i in range(3):
            plat_grid.columnconfigure(col_i, weight=1)

        self.lbl_plateforme_statut = tk.Label(
            col_d, text="", bg=c["bg_panel"], fg=c["accent_green"], font=("Segoe UI", 8, "bold"),
        )
        self.lbl_plateforme_statut.pack(anchor=tk.W, pady=(0, 8))
        self.selectionner_plateforme(self.plateforme_selectionnee)

        # Paramètres Génération Infinie & Montage
        tk.Label(col_d, text="🎨 PARAMÈTRES DE GÉNÉRATION & MONTAGE", bg=c["bg_panel"], fg=c["accent"], font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)

        p_frame = tk.Frame(col_d, bg=c["bg_panel"])
        p_frame.pack(fill=tk.X, pady=(4, 6))

        tk.Label(p_frame, text="Style :", bg=c["bg_panel"], fg=c["fg_text"], font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w", pady=2)
        self.combo_style = ttk.Combobox(p_frame, values=STYLES_VISUELS, state="readonly", width=22)
        self.combo_style.current(0)
        self.combo_style.grid(row=0, column=1, sticky="ew", pady=2, padx=(6, 0))

        tk.Label(p_frame, text="Durée (s) :", bg=c["bg_panel"], fg=c["fg_text"], font=("Segoe UI", 8)).grid(row=1, column=0, sticky="w", pady=2)
        self.var_duree_video = tk.IntVar(value=45)
        ttk.Spinbox(p_frame, from_=5, to=600, increment=5, textvariable=self.var_duree_video, width=10).grid(row=1, column=1, sticky="w", pady=2, padx=(6, 0))

        tk.Label(p_frame, text="Résolution :", bg=c["bg_panel"], fg=c["fg_text"], font=("Segoe UI", 8)).grid(row=2, column=0, sticky="w", pady=2)
        self.combo_resolution = ttk.Combobox(p_frame, values=["1920x1080", "1080x1920", "1080x1080", "512x512"], state="readonly", width=16)
        self.combo_resolution.current(0)
        self.combo_resolution.grid(row=2, column=1, sticky="w", pady=2, padx=(6, 0))
        p_frame.columnconfigure(1, weight=1)

        self.btn_infini_droit = tk.Button(
            col_d, text="♾️ Démarrer Flux Infini (Images / Vidéo)", bg=c["accent_amber"], fg="#0f172a",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, pady=6, command=self.basculer_generation_infinie,
        )
        self.btn_infini_droit.pack(fill=tk.X, pady=(4, 10))

        # Statut Système & Santé
        tk.Label(col_d, text="📊 STATUT SYSTÈME & SANTÉ CYBER", bg=c["bg_panel"], fg=c["accent"], font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        sante_box = tk.Frame(col_d, bg=c["bg_input"], padx=8, pady=8)
        sante_box.pack(fill=tk.X, pady=(4, 0))

        self.lbl_cpu = tk.Label(sante_box, text="CPU : --%", bg=c["bg_input"], fg=c["fg_text"], font=("Segoe UI", 8))
        self.lbl_cpu.pack(anchor=tk.W)
        self.prog_cpu = ttk.Progressbar(sante_box, maximum=100)
        self.prog_cpu.pack(fill=tk.X, pady=(1, 4))

        self.lbl_mem = tk.Label(sante_box, text="Mémoire RAM : --%", bg=c["bg_input"], fg=c["fg_text"], font=("Segoe UI", 8))
        self.lbl_mem.pack(anchor=tk.W)
        self.prog_mem = ttk.Progressbar(sante_box, maximum=100)
        self.prog_mem.pack(fill=tk.X, pady=(1, 4))

        self.lbl_tampon_infini = tk.Label(
            sante_box, text="Flux infini tampon : 0 élément(s) en attente",
            bg=c["bg_input"], fg=c["fg_muted"], font=("Segoe UI", 8),
        )
        self.lbl_tampon_infini.pack(anchor=tk.W, pady=(2, 0))

        # =====================================================================
        # COLONNE CENTRALE : Miniatures + Timeline + Aperçu + Conversation + Prompt
        # =====================================================================
        col_c = tk.Frame(corps, bg=c["bg_panel"], padx=10, pady=10)
        col_c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bandeau Projets / Générations récentes
        tk.Label(col_c, text="🎞️ PROJETS & GÉNÉRATIONS RÉCENTES (CLIQUEZ POUR APERÇU)", bg=c["bg_panel"], fg=c["accent"], font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        self.bandeau_miniatures = tk.Frame(col_c, bg=c["bg_input"], height=58)
        self.bandeau_miniatures.pack(fill=tk.X, pady=(4, 8))
        self.bandeau_miniatures.pack_propagate(False)

        # Zone Timeline + Project Preview
        haut_centre = tk.Frame(col_c, bg=c["bg_panel"])
        haut_centre.pack(fill=tk.X, pady=(0, 8))

        # Timeline
        tl_box = tk.Frame(haut_centre, bg=c["bg_input"], padx=6, pady=6)
        tl_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        tk.Label(tl_box, text="⏱️ TIMELINE DE MONTAGE IA AUTONOME", bg=c["bg_input"], fg=c["accent"], font=("Segoe UI", 8, "bold")).pack(anchor=tk.W)
        self.canvas_timeline = tk.Canvas(tl_box, bg="#070d19", height=136, highlightthickness=0)
        self.canvas_timeline.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self._dessiner_timeline_vide()

        # Project Preview
        prev_box = tk.Frame(haut_centre, bg=c["bg_input"], padx=6, pady=6, width=255)
        prev_box.pack(side=tk.RIGHT, fill=tk.Y)
        prev_box.pack_propagate(False)
        tk.Label(prev_box, text="📺 APERÇU PROJET / MÉDIA", bg=c["bg_input"], fg=c["accent"], font=("Segoe UI", 8, "bold")).pack(anchor=tk.W)
        self.lbl_apercu_media = tk.Label(prev_box, bg="#020617", fg=c["fg_muted"], text="Aperçu prêt", width=30, height=7)
        self.lbl_apercu_media.pack(fill=tk.BOTH, expand=True, pady=(4, 4))

        prev_ctrls = tk.Frame(prev_box, bg=c["bg_input"])
        prev_ctrls.pack(fill=tk.X)
        self.btn_play_prev = tk.Button(
            prev_ctrls, text="▶ Lire / Pause Séquence", bg=c["border"], fg=c["fg_text"],
            font=("Segoe UI", 8), relief=tk.FLAT, command=self.basculer_lecture_apercu,
        )
        self.btn_play_prev.pack(fill=tk.X)

        # Fil Conversation & Logs
        tk.Label(col_c, text="💬 CONVERSATION MULTIMODALE, PROPOSITION IA & LOGS", bg=c["bg_panel"], fg=c["accent"], font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        self.txt_console = scrolledtext.ScrolledText(
            col_c, bg=c["bg_input"], fg=c["fg_text"], insertbackground=c["fg_text"],
            relief=tk.FLAT, wrap=tk.WORD, font=("Consolas", 9), height=11, padx=8, pady=6,
        )
        self.txt_console.pack(fill=tk.BOTH, expand=True, pady=(4, 8))
        self._journaliser(
            "HILAI Studio v2.0 initialisé. Joignez vos médias, activez la caméra/voix ou tapez "
            "vos instructions ci-dessous. Toutes les actions critiques restent sous votre contrôle."
        )

        # Barre d'instructions avec bouton Pièce Jointe rapide + Prompt + Envoyer + Flux Infini
        saisie_box = tk.Frame(col_c, bg=c["bg_panel"])
        saisie_box.pack(fill=tk.X)

        tk.Button(
            saisie_box, text="📎", bg=c["border"], fg=c["fg_text"],
            font=("Segoe UI", 13, "bold"), relief=tk.FLAT, width=3, command=self.ajouter_pieces_jointes,
        ).pack(side=tk.LEFT, padx=(0, 6), fill=tk.Y)

        self.txt_demande = tk.Text(
            saisie_box, bg=c["bg_input"], fg=c["fg_text"], insertbackground=c["fg_text"],
            height=3, relief=tk.FLAT, wrap=tk.WORD, font=("Segoe UI", 10), padx=8, pady=6,
        )
        self.txt_demande.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.txt_demande.insert(
            "1.0",
            "Monte une vidéo dynamique de 45s avec sous-titres, transitions fluides et musique rythmée.",
        )

        btns_prompt = tk.Frame(saisie_box, bg=c["bg_panel"])
        btns_prompt.pack(side=tk.RIGHT, fill=tk.Y)

        self.btn_preparer = tk.Button(
            btns_prompt, text="▶ Exécuter / Préparer", bg=c["accent"], fg="#0f172a",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=12, pady=5,
            command=self.lancer_preparation_async,
        )
        self.btn_preparer.pack(fill=tk.X, pady=(0, 4))
        self.boutons_action.append(self.btn_preparer)

        self.btn_infini_centre = tk.Button(
            btns_prompt, text="♾️ Flux Infini", bg=c["accent_amber"], fg="#0f172a",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=12, pady=5,
            command=self.basculer_generation_infinie,
        )
        self.btn_infini_centre.pack(fill=tk.X)

        # =====================================================================
        # BARRE BASSE : SAS DE VALIDATION HUMAN-IN-THE-LOOP
        # =====================================================================
        sas_box = tk.Frame(parent, bg=c["bg_panel"], padx=10, pady=8)
        sas_box.pack(fill=tk.X, pady=(8, 0))

        row_dec = tk.Frame(sas_box, bg=c["bg_panel"])
        row_dec.pack(fill=tk.X, pady=(0, 6))

        tk.Label(row_dec, text="Ta décision :", bg=c["bg_panel"], fg=c["fg_text"], font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.entree_decision = ttk.Entry(row_dec, width=28)
        self.entree_decision.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        tk.Label(row_dec, text="Justification / note mémoire :", bg=c["bg_panel"], fg=c["fg_muted"], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.entree_justification = ttk.Entry(row_dec, width=32)
        self.entree_justification.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        tk.Label(row_dec, text="Export binaire :", bg=c["bg_panel"], fg=c["fg_muted"], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.combo_binaire = ttk.Combobox(row_dec, values=["aucun", "xlsx", "pptx", "pdf", "db"], state="readonly", width=7)
        self.combo_binaire.current(0)
        self.combo_binaire.pack(side=tk.RIGHT)

        row_val = tk.Frame(sas_box, bg=c["bg_panel"])
        row_val.pack(fill=tk.X)

        self.var_valider_sortie = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            row_val,
            text="Je valide explicitement l'écriture et l'export dans 'sorties_a_valider/' (confirme_steve)",
            variable=self.var_valider_sortie,
        ).pack(side=tk.LEFT)

        self.var_lancer_ffmpeg = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            row_val,
            text="Rendu MP4 FFmpeg (si installé)",
            variable=self.var_lancer_ffmpeg,
        ).pack(side=tk.LEFT, padx=(14, 0))

        self.btn_enregistrer = tk.Button(
            row_val, text="💾 Valider & Exporter le projet final", bg=c["accent_green"], fg="#0f172a",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=14, pady=6,
            command=self.enregistrer_decision,
        )
        self.btn_enregistrer.pack(side=tk.RIGHT)
        self.boutons_action.append(self.btn_enregistrer)

    def _construire_onglet_relecture(self, parent: ttk.Frame) -> None:
        c = self.couleurs
        barre_top = ttk.Frame(parent)
        barre_top.pack(fill="x", pady=(0, 8))

        btn_act = ttk.Button(barre_top, text="Actualiser", command=self.actualiser_relecture)
        btn_act.pack(side="left", padx=(0, 8))
        self.boutons_action.append(btn_act)

        btn_diag = ttk.Button(barre_top, text="Diagnostic Cybersécurité & Modules", command=self.afficher_diagnostic)
        btn_diag.pack(side="left", padx=(0, 8))
        self.boutons_action.append(btn_diag)

        btn_snap = ttk.Button(barre_top, text="Créer Snapshot Studio", command=self.faire_snapshot)
        btn_snap.pack(side="left")
        self.boutons_action.append(btn_snap)

        ttk.Label(parent, text="Fichiers validés dans 'sorties_a_valider/' (cliquez pour aperçu) :").pack(anchor="w")
        self.liste_sorties = tk.Listbox(
            parent, height=7, exportselection=False,
            bg=c["bg_input"], fg=c["fg_text"], selectbackground=c["accent"], relief=tk.FLAT,
        )
        self.liste_sorties.pack(fill="x", pady=(4, 8))
        self.liste_sorties.bind("<<ListboxSelect>>", self.apercevoir_sortie_selectionnee)

        ttk.Label(parent, text="Aperçu du fichier sélectionné / journaux & diagnostic :").pack(anchor="w")
        self.txt_relecture = scrolledtext.ScrolledText(
            parent, height=18, wrap="word",
            bg=c["bg_input"], fg=c["fg_text"], relief=tk.FLAT, font=("Consolas", 9),
        )
        self.txt_relecture.pack(fill="both", expand=True, pady=(4, 0))
        self.actualiser_relecture()

    # =========================================================================
    # THÈME, PARAMÈTRES & JOURNALISATION
    # =========================================================================

    def _journaliser(self, texte: str) -> None:
        horodatage = datetime.now().strftime("%H:%M:%S")
        propre = masquer_secrets(str(texte))
        self.txt_console.insert(tk.END, f"[{horodatage}] {propre}\n")
        self.txt_console.see(tk.END)

    def ouvrir_parametres(self) -> None:
        FenetreParametresHILAI(self)

    def recharger_configuration_et_theme(self, nouvelle_cfg: dict[str, Any]) -> None:
        self.config_studio = nouvelle_cfg
        self.couleurs = dict(nouvelle_cfg["couleurs"])
        self.var_reponse_vocale.set(bool(nouvelle_cfg.get("reponse_vocale_active", True)))
        self.var_cam_auto.set(bool(nouvelle_cfg.get("camera_auto_analyse", True)))
        self._appliquer_couleurs_recursif(self.root)
        self._configurer_styles()
        self._journaliser(f"🎨 Paramètres mis à jour (Thème : {nouvelle_cfg.get('theme')}).")

    def _appliquer_couleurs_recursif(self, widget: tk.Widget) -> None:
        c = self.couleurs
        try:
            if isinstance(widget, (tk.Tk, tk.Toplevel)):
                widget.configure(bg=c["bg_main"])
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=c["bg_panel"])
            elif isinstance(widget, tk.Text):
                widget.configure(bg=c["bg_input"], fg=c["fg_text"], insertbackground=c["fg_text"])
            elif isinstance(widget, tk.Listbox):
                widget.configure(bg=c["bg_input"], fg=c["fg_text"], selectbackground=c["accent"])
        except Exception:
            pass
        for child in widget.winfo_children():
            self._appliquer_couleurs_recursif(child)

    def _planifier_rafraichissement_sante(self) -> None:
        metriques = obtenir_metriques_systeme()
        self.lbl_cpu.config(text=f"CPU : {metriques['cpu_pct']}% | Disque utilisé : {metriques['disk_pct']}%")
        self.prog_cpu["value"] = metriques["cpu_pct"]
        self.lbl_mem.config(text=f"Mémoire RAM : {metriques['mem_pct']}%")
        self.prog_mem["value"] = metriques["mem_pct"]
        self.root.after(4000, self._planifier_rafraichissement_sante)

    # =========================================================================
    # CAMÉRA TEMPS RÉEL, VOIX & PIÈCES JOINTES
    # =========================================================================

    def ajouter_pieces_jointes(self) -> None:
        fichiers = filedialog.askopenfilenames(
            title="Importer des fichiers (Images, Vocaux, Vidéos, Documents)",
            filetypes=[
                ("Tous médias supportés", "*.png *.jpg *.jpeg *.webp *.bmp *.gif *.mp3 *.wav *.ogg *.m4a *.mp4 *.mov *.mkv *.txt *.md *.pdf *.json"),
                ("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.gif"),
                ("Audio / Vocal", "*.mp3 *.wav *.ogg *.m4a *.flac"),
                ("Vidéos", "*.mp4 *.mov *.mkv *.avi *.webm"),
                ("Documents & Code", "*.txt *.md *.pdf *.json *.csv *.py *.html"),
            ],
        )
        max_mo = float(self.config_studio.get("taille_max_piece_jointe_mo", 250))
        ajoutes = 0
        for f in fichiers:
            if f in self.pieces_jointes:
                continue
            try:
                meta = valider_piece_jointe_securisee(f, taille_max_mo=max_mo)
                self.pieces_jointes.append(meta["chemin"])
                self.pieces_jointes_meta.append(meta)
                taille_ko = max(1, meta["taille_octets"] // 1024)
                icone = {"image": "🖼️", "audio": "🎵", "video": "🎬", "document": "📄", "code": "💻"}.get(meta["categorie"], "📎")
                self.liste_pj.insert(tk.END, f"{icone} {meta['nom']} ({taille_ko} Ko)")
                ajoutes += 1
                if meta["categorie"] == "image" and not self.entree_cible.get().strip():
                    self.entree_cible.insert(0, meta["chemin"])
                if meta["extension"] == ".png":
                    try:
                        self._afficher_png_dans_apercu(Path(meta["chemin"]).read_bytes(), f"Import : {meta['nom']}")
                    except Exception:
                        pass
            except Exception as exc:
                messagebox.showerror("Garde-fou Pièce Jointe", f"Fichier bloqué par la sécurité :\n{exc}")
                self._journaliser(f"🛡️ Pièce jointe bloquée : {exc}")

        if ajoutes:
            self._journaliser(f"📎 {ajoutes} pièce(s) jointe(s) validée(s) et ajoutée(s) au contexte IA.")

    def retirer_piece_jointe(self) -> None:
        sel = self.liste_pj.curselection()
        if not sel:
            return
        idx = sel[0]
        self.liste_pj.delete(idx)
        if 0 <= idx < len(self.pieces_jointes):
            nom = Path(self.pieces_jointes.pop(idx)).name
            if idx < len(self.pieces_jointes_meta):
                self.pieces_jointes_meta.pop(idx)
            self._journaliser(f"🗑️ Pièce jointe retirée : {nom}")

    def vider_pieces_jointes(self) -> None:
        self.pieces_jointes.clear()
        self.pieces_jointes_meta.clear()
        self.liste_pj.delete(0, tk.END)
        self._journaliser("🗑️ File des pièces jointes vidée.")

    def basculer_enregistrement_vocal(self) -> None:
        if not self.enregistreur_vocal.en_cours:
            res = self.enregistreur_vocal.demarrer()
            self.btn_enregistrer.config(text="⏹ Arrêter & Envoyer vocal", bg="#991b1b")
            self._journaliser(f"🎙️ Enregistrement vocal démarré ({res.get('mode')})... Parlez maintenant.")
        else:
            res = self.enregistreur_vocal.arreter()
            self.btn_enregistrer.config(text="⏺ Enregistrer la voix", bg=self.couleurs["accent_red"])
            chemin = res.get("fichier", "")
            nom = res.get("nom", "vocal.wav")
            if chemin and Path(chemin).exists():
                self.pieces_jointes.append(chemin)
                self.liste_pj.insert(tk.END, f"🎙️ {nom} ({res.get('duree_sec')}s)")
            self.derniere_note_vocale = f"Note vocale {nom} ({res.get('duree_sec')}s, mode {res.get('mode')})"
            self._journaliser(f"✅ Note vocale capturée : {nom} ({res.get('duree_sec')}s).")

            if self.var_reponse_vocale.get():
                msg_ia = "Note vocale bien reçue Steve. Je suis prêt à traiter votre demande."
                self.synthese_vocale.parler(msg_ia, actif=True)
                self._journaliser(f"🔊 HILAI (voix) : « {msg_ia} »")

    def basculer_camera(self) -> None:
        if not self.camera_active:
            if OPENCV_DISPONIBLE and PILLOW_DISPONIBLE:
                import cv2  # type: ignore
                self.cap = cv2.VideoCapture(0)
                if not self.cap or not self.cap.isOpened():
                    self.cap = None
                    self._journaliser("📷 Webcam matérielle indisponible — bascule sur Vision Temps Réel simulée.")
            else:
                self.cap = None
                self._journaliser("📷 Mode Vision Temps Réel logique actif (installez opencv-python pillow pour webcam directe).")

            self.camera_active = True
            self.btn_camera.config(text="⏹ Couper Caméra IA", bg=self.couleurs["accent_red"], fg="white")
            self._boucle_camera()
        else:
            self.camera_active = False
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None
            self.btn_camera.config(text="▶ Activer Caméra IA", bg=self.couleurs["accent"], fg="#0f172a")
            self.zone_camera.config(image="", text="Caméra arrêtée")
            self.lbl_vision_obs.config(text="Observation IA : Flux caméra interrompu.")

    def _boucle_camera(self) -> None:
        if not self.camera_active:
            return
        self.cam_step += 1

        if self.cap is not None and OPENCV_DISPONIBLE and PILLOW_DISPONIBLE:
            import cv2  # type: ignore
            from PIL import Image, ImageTk  # type: ignore
            ret, frame = self.cap.read()
            if ret:
                diag = self.analyseur_vision.analyser_frame_opencv(frame)
                for (x, y, w, h) in diag.get("boites_visages", []):
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (56, 189, 248), 2)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb).resize((316, 175))
                imgtk = ImageTk.PhotoImage(image=img)
                self.zone_camera.imgtk = imgtk
                self.zone_camera.config(image=imgtk, text="")
            else:
                diag = self.analyseur_vision.analyser_simulation(self.cam_step)
        else:
            diag = self.analyseur_vision.analyser_simulation(self.cam_step)
            if self.cam_step % 4 == 1:
                png_bytes = self.analyseur_vision.generer_apercu_simulation_png(316, 165, self.cam_step)
                imgtk = tk.PhotoImage(data=base64.b64encode(png_bytes).decode("ascii"))
                self.zone_camera.imgtk = imgtk
                self.zone_camera.config(image=imgtk, text="")

        if self.var_cam_auto.get() and self.cam_step % 15 == 1:
            txt_obs = f"[{diag['horodatage']}] {diag['observation']}\nDécision : {diag['decision_proposee']}"
            self.derniere_observation_cam = txt_obs
            self.lbl_vision_obs.config(text=txt_obs)
            if self.var_reponse_vocale.get() and self.cam_step == 1:
                self.synthese_vocale.parler(diag["observation"], actif=True)

        fps = max(5, int(self.config_studio.get("camera_fps", 20)))
        self.root.after(max(40, int(1000 / fps)), self._boucle_camera)

    # =========================================================================
    # PLATEFORMES DE MONTAGE, TIMELINE & APERÇU VISUEL
    # =========================================================================

    def selectionner_plateforme(self, cle_plateforme: str) -> None:
        self.plateforme_selectionnee = cle_plateforme
        c = self.couleurs
        for cle, btn in self.boutons_plateformes.items():
            if cle == cle_plateforme:
                btn.config(bg=c["accent"], fg="#0f172a")
            else:
                btn.config(bg=c["bg_input"], fg=c["fg_text"])
        lib = PLATEFORMES_MONTAGE.get(cle_plateforme, cle_plateforme)
        self.lbl_plateforme_statut.config(text=f"Connecté : {lib}")

    def _dessiner_timeline_vide(self) -> None:
        cv = self.canvas_timeline
        cv.delete("all")
        cv.create_text(
            230, 68,
            text="Sélectionnez « Montage vidéo autonome » et cliquez Exécuter\npour générer la timeline multi-pistes interactive.",
            fill="#64748b", font=("Segoe UI", 9), justify=tk.CENTER,
        )

    def _dessiner_timeline_montage(self, plan: dict[str, Any]) -> None:
        cv = self.canvas_timeline
        cv.delete("all")
        w = max(420, cv.winfo_width() or 520)
        duree_tot = max(1.0, float(plan.get("parametres", {}).get("duree_totale_sec", 30.0)))
        tracks = plan.get("timeline_tracks", [])

        # Règle temporelle
        marge_g = 115
        zone_w = max(180, w - marge_g - 15)
        cv.create_line(marge_g, 18, marge_g + zone_w, 18, fill="#334155")
        for i in range(6):
            t_sec = round((duree_tot * i) / 5.0, 1)
            x = marge_g + (zone_w * i) / 5.0
            cv.create_line(x, 12, x, 22, fill="#64748b")
            cv.create_text(x, 8, text=f"{t_sec}s", fill="#94a3b8", font=("Segoe UI", 7))

        # Pistes
        y0 = 26
        h_piste = 20
        for idx, tr in enumerate(tracks[:5]):
            y = y0 + idx * (h_piste + 3)
            cv.create_text(4, y + h_piste // 2, anchor="w", text=tr.get("piste", f"P{idx}")[:16], fill="#cbd5e1", font=("Segoe UI", 7, "bold"))
            x1 = marge_g + (tr.get("debut", 0.0) / duree_tot) * zone_w
            x2 = max(x1 + 16, marge_g + (tr.get("fin", duree_tot) / duree_tot) * zone_w)
            col = tr.get("couleur", "#38bdf8")
            cv.create_rectangle(x1, y, x2, y + h_piste, fill=col, outline="#0f172a")
            cv.create_text(x1 + 5, y + h_piste // 2, anchor="w", text=tr.get("label", "")[:24], fill="#0f172a", font=("Segoe UI", 7, "bold"))

    def _rafraichir_apercu_initial(self) -> None:
        png_bytes, _ = generer_image_procedurale("HILAI Studio v2.0", "Cyberpunk / Néon", largeur=235, hauteur=120, seed=7)
        self._afficher_png_dans_apercu(png_bytes, "HILAI v2.0 Prêt")

    def _afficher_png_dans_apercu(self, png_bytes: bytes, legende: str = "") -> None:
        try:
            imgtk = tk.PhotoImage(data=base64.b64encode(png_bytes).decode("ascii"))
            self.img_apercu_ref = imgtk
            self.lbl_apercu_media.config(image=imgtk, text="")
            if legende:
                self.var_statut.set(legende)
        except Exception:
            pass

    def _ajouter_miniature_recente(self, png_bytes: bytes, titre: str) -> None:
        try:
            imgtk = tk.PhotoImage(data=base64.b64encode(png_bytes).decode("ascii")).subsample(3, 3)
            self.miniatures_refs.append(imgtk)
            if len(self.miniatures_refs) > 8:
                self.miniatures_refs.pop(0)
            for child in self.bandeau_miniatures.winfo_children()[: max(0, len(self.bandeau_miniatures.winfo_children()) - 7)]:
                child.destroy()

            btn = tk.Button(
                self.bandeau_miniatures, image=imgtk, relief=tk.FLAT, bg=self.couleurs["bg_panel"],
                command=lambda b=png_bytes, t=titre: self._afficher_png_dans_apercu(b, t),
            )
            btn.pack(side=tk.LEFT, padx=3, pady=3)
        except Exception:
            pass

    def basculer_lecture_apercu(self) -> None:
        if not self.frames_apercu:
            self._journaliser("ℹ️ Aucune séquence multi-frames chargée pour lecture.")
            return
        self.lecture_apercu_active = not self.lecture_apercu_active
        if self.lecture_apercu_active:
            self._animer_sequence_apercu()

    def _animer_sequence_apercu(self) -> None:
        if not self.lecture_apercu_active or not self.frames_apercu:
            return
        frame = self.frames_apercu[self.index_frame_apercu % len(self.frames_apercu)]
        self._afficher_png_dans_apercu(frame)
        self.index_frame_apercu += 1
        self.root.after(140, self._animer_sequence_apercu)

    # =========================================================================
    # EXÉCUTION IA & FLUX INFINI IMAGES / VIDÉOS
    # =========================================================================

    def _definir_etat(self, actif: bool, msg: str) -> None:
        self.occupe = actif
        self.var_statut.set(msg)
        etat = tk.DISABLED if actif else tk.NORMAL
        for btn in self.boutons_action:
            try:
                btn.config(state=etat)
            except Exception:
                pass

    def lancer_preparation_async(self) -> None:
        if self.occupe:
            return
        demande = self.txt_demande.get("1.0", tk.END).strip()
        cible = self.entree_cible.get().strip()
        if not demande and not cible and not self.pieces_jointes:
            messagebox.showwarning("Entrée vide", "Saisissez une instruction, joignez un fichier ou enregistrez une note vocale.")
            return

        verif_sec = analyser_demande_securite(demande)
        if not verif_sec["valide"]:
            self._journaliser(f"🛡️ ALERTE CYBERSÉCURITÉ : {verif_sec['avertissement']}")
            messagebox.showwarning("Bouclier Cybersécurité HILAI", verif_sec["avertissement"])
            return

        capacite = self.labels_to_cap.get(self.combo_capacite.get(), "atelier")
        atelier_slug = self.libelles_to_slug.get(self.combo_atelier.get(), "recherche_connaissance_conseil")
        domaine = self.entree_domaine.get().strip()
        fmt_com = self.combo_format_com.get()
        params_media = {
            "style": self.combo_style.get(),
            "duree_sec": int(self.var_duree_video.get()),
            "resolution": self.combo_resolution.get(),
        }

        self._journaliser(f"👤 Steve : {demande or '(Action sur médias joints)'}")
        self._definir_etat(True, f"Préparation IA ({capacite}) en cours...")

        def _travail() -> None:
            try:
                kwargs = _construire_kwargs_capacite(
                    capacite=capacite,
                    demande=demande,
                    atelier_slug=atelier_slug,
                    photo_ou_cible=cible,
                    domaine_ou_canal=domaine,
                    format_com=fmt_com,
                    pieces_jointes=list(self.pieces_jointes),
                    plateforme_montage=self.plateforme_selectionnee,
                    parametres_media=params_media,
                    observation_camera=self.derniere_observation_cam,
                    note_vocale=self.derniere_note_vocale,
                )
                res_norm = executer_capacite(capacite, **kwargs)
                self.root.after(0, self._afficher_resultat, atelier_slug, demande, res_norm)
            except Exception as exc:
                self.root.after(0, self._afficher_erreur, str(exc))

        threading.Thread(target=_travail, daemon=True).start()

    def _afficher_resultat(self, atelier_slug: str, demande: str, res_norm: dict[str, Any]) -> None:
        self.dernier_atelier_slug = atelier_slug
        self.derniere_demande = demande
        self.dernier_resultat_norm = res_norm

        brut = res_norm.get("donnee_brute", {})
        if "timeline_tracks" in brut:
            self._dessiner_timeline_montage(brut)
        if "image_png_bytes" in brut:
            self.frames_apercu = []
            self._afficher_png_dans_apercu(brut["image_png_bytes"], res_norm.get("titre", ""))
            self._ajouter_miniature_recente(brut["image_png_bytes"], res_norm.get("titre", ""))
        elif "sequence_video" in brut and brut["sequence_video"].get("frames_png"):
            self.frames_apercu = brut["sequence_video"]["frames_png"]
            self.index_frame_apercu = 0
            self.lecture_apercu_active = True
            self._animer_sequence_apercu()
            self._ajouter_miniature_recente(self.frames_apercu[0], res_norm.get("titre", ""))

        pts = "\n".join(f"  * {p}" for p in res_norm.get("points_validation", []))
        self._journaliser(
            f"🤖 HILAI [{res_norm.get('capacite')}] — {res_norm.get('titre')}\n"
            f"Résumé : {res_norm.get('resume')}\n\n"
            f"{res_norm.get('contenu_principal')}\n\n"
            f"Points de validation :\n{pts}\n"
            + "-" * 60
        )
        if self.var_reponse_vocale.get():
            self.synthese_vocale.parler(res_norm.get("resume", "Proposition prête."), actif=True)

        self._definir_etat(False, "Proposition prête — en attente de ta validation explicite.")

    def _afficher_erreur(self, msg: str) -> None:
        self._definir_etat(False, "Erreur lors de la préparation.")
        self._journaliser(f"❌ Erreur : {msg}")
        messagebox.showerror("Erreur", msg)

    def basculer_generation_infinie(self) -> None:
        if not self.flux_infini.actif:
            cap = self.labels_to_cap.get(self.combo_capacite.get(), "")
            mode = "video" if "video" in cap else "image"
            prompt = self.txt_demande.get("1.0", tk.END).strip() or "Création générative HILAI"
            style = self.combo_style.get()
            intervalle = float(self.config_studio.get("intervalle_generation_sec", 2.0))

            self.btn_infini_centre.config(text="⏹ Stop Infini", bg=self.couleurs["accent_red"], fg="white")
            self.btn_infini_droit.config(text="⏹ Arrêter Flux Infini", bg=self.couleurs["accent_red"], fg="white")
            self._journaliser(f"♾️ Flux Infini démarré (mode={mode}, style={style})...")

            def _on_elem(elem: dict[str, Any]) -> None:
                self.root.after(0, self._traiter_nouvel_element_infini, elem)

            def _on_lim(msg: str) -> None:
                self.root.after(0, lambda: self._journaliser(f"🛡️ {msg}"))
                self.root.after(0, self.basculer_generation_infinie)

            self.flux_infini.demarrer(
                mode=mode, prompt=prompt, style=style, intervalle_sec=intervalle,
                on_nouvel_element=_on_elem, on_limite=_on_lim,
            )
        else:
            total = self.flux_infini.arreter()
            self.btn_infini_centre.config(text="♾️ Flux Infini", bg=self.couleurs["accent_amber"], fg="#0f172a")
            self.btn_infini_droit.config(text="♾️ Démarrer Flux Infini (Images / Vidéo)", bg=self.couleurs["accent_amber"], fg="#0f172a")
            self._journaliser(f"⏹ Flux infini arrêté ({total} élément(s) dans le tampon sécurisé).")

    def _traiter_nouvel_element_infini(self, elem: dict[str, Any]) -> None:
        nb = len(self.flux_infini.lister_elements())
        self.lbl_tampon_infini.config(text=f"Flux infini tampon : {nb} élément(s) prêts à valider")
        self._afficher_png_dans_apercu(elem["preview_png"], f"Flux Infini #{elem['id']} ({elem['type']})")
        self._ajouter_miniature_recente(elem["preview_png"], f"#{elem['id']}")
        if elem["type"] == "video":
            self.frames_apercu = elem["frames_png"]
        self._journaliser(f"✨ [Flux Infini #{elem['id']}] {elem['type']} généré(e) — en attente de validation.")

    # =========================================================================
    # VALIDATION HUMAN-IN-THE-LOOP, RELECTURE, SNAPSHOT & DIAGNOSTIC
    # =========================================================================

    def enregistrer_decision(self) -> None:
        if self.occupe:
            return
        valider_sortie = self.var_valider_sortie.get()
        tampon_infini = self.flux_infini.lister_elements()

        if not self.dernier_resultat_norm and not tampon_infini:
            messagebox.showwarning("Aucune proposition", "Prépare d'abord un brouillon ou génère un média.")
            return

        if not valider_sortie and not self.entree_decision.get().strip():
            messagebox.showwarning(
                "Garde-fou Human-in-the-Loop",
                "Saisis une décision ou coche la case de validation explicite (confirme_steve) pour exporter.",
            )
            return

        decision = self.entree_decision.get().strip() or "Validé via Studio HILAI v2.0"
        justification = self.entree_justification.get().strip()
        fmt_bin = self.combo_binaire.get()

        self._definir_etat(True, "Enregistrement sécurisé en cours...")
        try:
            messages: list[str] = []
            if self.dernier_resultat_norm:
                messages.extend(
                    _enregistrer_resultat_normalise(
                        resultat_norm=self.dernier_resultat_norm,
                        atelier_slug=self.dernier_atelier_slug,
                        demande=self.derniere_demande,
                        decision=decision,
                        justification=justification,
                        valider_sortie=valider_sortie,
                        plateforme_montage=self.plateforme_selectionnee,
                        lancer_rendu_ffmpeg=self.var_lancer_ffmpeg.get(),
                    )
                )

            if valider_sortie and tampon_infini:
                ecrits_inf = self.flux_infini.exporter_tampon_valide(confirme_steve=True)
                messages.append(f"Médias flux infini exportés ({len(ecrits_inf)}) dans sorties_a_valider/generations_infinies/")

            if fmt_bin in {"xlsx", "pptx", "pdf", "db"} and self.dernier_resultat_norm:
                conf = messagebox.askyesno(
                    "Confirmation explicite",
                    f"Steve, confirmes-tu la création du fichier .{fmt_bin} dans 'sorties_a_valider/' ?",
                )
                if conf:
                    cree = generer_fichier_binaire(
                        fmt_bin,
                        self.dernier_resultat_norm.get("titre", "Sortie_Studio"),
                        self.dernier_resultat_norm.get("contenu_principal", ""),
                        True,
                    )
                    messages.append(f"Fichier binaire créé : {cree}")

            self.var_valider_sortie.set(False)
            self.combo_binaire.current(0)
            self.actualiser_relecture()
            self._journaliser("💾 Export Human-in-the-Loop terminé :\n  " + "\n  ".join(messages))
            messagebox.showinfo("Validation & Export terminés", "\n".join(messages))
        except Exception as exc:
            messagebox.showerror("Erreur d'enregistrement", str(exc))
        finally:
            self._definir_etat(False, "Prêt — décision enregistrée.")

    def actualiser_relecture(self) -> None:
        self.liste_sorties.delete(0, "end")
        self.chemins_sorties = lister_sorties_validees()
        for p in self.chemins_sorties:
            self.liste_sorties.insert("end", str(p))

        texte = (
            "=== JOURNAL DU JOUR ===\n"
            + lire_journal_jour()
            + "\n\n=== HISTORIQUE RÉCENT ===\n"
            + lire_historique_journaux()
        )
        self.txt_relecture.delete("1.0", "end")
        self.txt_relecture.insert("1.0", texte)

    def apercevoir_sortie_selectionnee(self, _event: tk.Event | None = None) -> None:
        selection = self.liste_sorties.curselection()
        if not selection:
            return
        index = selection[0]
        if index < 0 or index >= len(self.chemins_sorties):
            return
        chemin = self.chemins_sorties[index]
        try:
            apercu = lire_aperçu_sortie_securise(chemin)
        except Exception as exc:
            apercu = f"Impossible d'afficher l'aperçu : {exc}"

        self.txt_relecture.delete("1.0", "end")
        self.txt_relecture.insert("1.0", f"=== APERÇU : {chemin} ===\n\n{apercu}")

    def afficher_diagnostic(self) -> None:
        if self.occupe:
            return
        self._definir_etat(True, "Diagnostic cybersécurité en cours...")
        try:
            rapport = verifier_tout()
            self.txt_relecture.delete("1.0", "end")
            self.txt_relecture.insert("1.0", json.dumps(rapport, indent=2, ensure_ascii=False))
        finally:
            self._definir_etat(False, "Diagnostic affiché.")

    def faire_snapshot(self) -> None:
        if self.occupe:
            return
        ok = messagebox.askyesno(
            "Sauvegarde snapshot",
            "Steve, confirmes-tu la création d'un snapshot horodaté dans 'sauvegardes_studio/' ?",
        )
        if not ok:
            return
        self._definir_etat(True, "Création du snapshot...")
        try:
            cible = sauvegarder_snapshot_studio(True)
            self.actualiser_relecture()
            messagebox.showinfo("Snapshot créé", f"Dossier : {cible}")
        finally:
            self._definir_etat(False, "Snapshot terminé.")


def executer_gui() -> None:
    root = tk.Tk()
    ApplicationStudioGUI(root)
    root.mainloop()


def executer_demo_automatique() -> None:
    """Exécute un tour complet de validation automatique v2.0 sans prompt bloquant."""
    print("\n========================================================")
    print("    DÉMONSTRATION AUTOMATISÉE HILAI STUDIO v2.0          ")
    print("========================================================")
    tests_demo = [
        ("atelier", "Démonstration atelier HILAI"),
        ("montage_video_autonome", "Monte une vidéo dynamique de 45s avec sous-titres et musique"),
        ("connecteur_plateformes", "Prépare un export timeline pour Premiere Pro et DaVinci"),
        ("generation_images_infinie", "Paysage cyber futuriste néon"),
        ("generation_videos_infinie", "Animation caméra studio 3D"),
        ("conversation_multimodale", "Analyse le projet et propose les prochaines étapes"),
        ("site_web", "Site vitrine universel HILAI"),
        ("code", "Utilitaire Python de hachage SHA-256"),
        ("maths_geometrie", "2+3*4"),
        ("marketing_bi", "Stratégie SEO & lancement GitHub"),
    ]
    dernier_res = None
    for cap, dem in tests_demo:
        kwargs = _construire_kwargs_capacite(
            capacite=cap,
            demande=dem,
            atelier_slug="recherche_connaissance_conseil",
            photo_ou_cible="contexte_demo",
            domaine_ou_canal="seo" if cap == "marketing_bi" else "auto",
            format_com="mail",
            plateforme_montage="premiere_pro",
        )
        dernier_res = executer_capacite(cap, **kwargs)
        print(f"[OK] Capacité '{cap:<26}' -> {dernier_res['titre'][:48]}")

    print("\n[+] Test de traçabilité et validation Human-in-the-Loop...")
    if dernier_res:
        msgs = _enregistrer_resultat_normalise(
            resultat_norm=dernier_res,
            atelier_slug="recherche_connaissance_conseil",
            demande="Test validation démo HILAI v2.0",
            decision="Validation explicite en mode démonstration",
            justification="Vérification de l'intégrité v2.0 Human-in-the-Loop",
            valider_sortie=True,
        )
        for m in msgs:
            print(f"  -> {m}")
    print("\n[+] Démonstration v2.0 achevée avec succès. Système 100% prêt.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="HILAI Studio Modulaire v2.0 — Belalingbi Steve")
    parser.add_argument("--cli", action="store_true", help="Forcer le mode ligne de commande")
    parser.add_argument("--diag", action="store_true", help="Afficher le rapport de diagnostic de sécurité")
    parser.add_argument("--demo", action="store_true", help="Lancer un cycle de démonstration automatisé")
    args = parser.parse_args()

    if args.diag:
        from verifier_studio import afficher_rapport
        afficher_rapport(verifier_tout())
        return

    if args.demo:
        executer_demo_automatique()
        return

    sans_gui = (
        sys.platform.startswith("linux")
        and not os.environ.get("DISPLAY")
        and not os.environ.get("WAYLAND_DISPLAY")
    )
    if args.cli or sans_gui:
        executer_cli()
    else:
        executer_gui()


if __name__ == "__main__":
    main()
