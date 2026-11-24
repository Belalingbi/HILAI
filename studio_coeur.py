"""
studio_coeur.py — Cœur unifié, orchestration des 4 ateliers et génération de livrables validés.

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop »
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import json
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from fiabilite_studio import exiger_confirmation_steve
from ia_fournisseur import executer_requete_ia, obtenir_mode_fournisseur
from securite_garde_fous import (
    assainir_nom_fichier,
    masquer_secrets,
    valider_chemin_confine,
    valider_identifiant_sql,
)

DOSSIER_SORTIES = Path("sorties_a_valider")
DOSSIER_WEB = DOSSIER_SORTIES / "brouillon_site_web"
DOSSIER_CODE = DOSSIER_SORTIES / "brouillon_code"
DOSSIER_VIDEO = DOSSIER_SORTIES / "brouillon_video_photo"

FICHIER_REGLES = Path("regles_decision.json")
FICHIER_MEMOIRE = Path("memoire_preferences.json")
NB_JOURS_HISTORIQUE = 5
MAX_CHARS_JOURNAL = 2500

ATELIERS = {
    "1": (
        "documents_donnees_bureautique",
        "Documents, Bureautique & Bases de données (.xlsx, .pptx, .pdf, .db)",
    ),
    "2": (
        "recherche_connaissance_conseil",
        "Recherche, Connaissance & Conseil (analyse, repères, orientations)",
    ),
    "3": (
        "visuel_design_musique",
        "Visuel, Design & Musique (brouillon encadré : logos, photos, designs, musique)",
    ),
    "4": (
        "langue_voix_appel",
        "Langue, Voix, Traduction & Appel direct (préparation encadrée)",
    ),
}

INSTRUCTIONS_ATELIERS = {
    "documents_donnees_bureautique": (
        "Tu prépares des structures Excel (.xlsx), présentations (.pptx), "
        "documents PDF (.pdf) et bases SQLite (.db) soumises à validation de Steve."
    ),
    "recherche_connaissance_conseil": (
        "Tu analyses des sujets, distingues faits et hypothèses, et proposes des options "
        "argumentées sans jamais décider à la place de Steve."
    ),
    "visuel_design_musique": (
        "Tu travailles en mode BROUILLON ENCADRÉ pour identités/logos, images, designs "
        "et musique : pistes, briefs et points de vigilance avant validation."
    ),
    "langue_voix_appel": (
        "Tu prépares traductions, lectures multilingues et trames d'échange/appel "
        "sans action externe ni archivage sans accord de Steve."
    ),
}


def charger_json(chemin: Path, defaut: dict) -> dict:
    if not chemin.exists():
        chemin.write_text(
            json.dumps(defaut, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return defaut
    return json.loads(chemin.read_text(encoding="utf-8"))


def sauvegarder_json(chemin: Path, donnees: dict) -> None:
    chemin.write_text(
        json.dumps(donnees, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def nettoyer_nom(texte: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", texte.strip().lower()).strip("_")
    return slug[:50] or "element_studio"


# --- Relecture journaux & sorties validées ---

def lire_journal_jour(date_str: str | None = None) -> str:
    jour = date_str or datetime.now().strftime("%Y-%m-%d")
    chemin = Path(f"journal_{jour}.md")
    if not chemin.exists():
        return f"Aucune entrée dans journal_{jour}.md pour le moment."
    return masquer_secrets(chemin.read_text(encoding="utf-8"))


def lire_historique_journaux(date_reference: str | None = None, limite_jours: int = NB_JOURS_HISTORIQUE) -> str:
    ref = date_reference or datetime.now().strftime("%Y-%m-%d")
    fichiers = sorted(Path(".").glob("journal_????-??-??.md"), reverse=True)
    blocs = []
    for f in fichiers:
        d = f.stem.replace("journal_", "")
        if d >= ref:
            continue
        texte = f.read_text(encoding="utf-8").strip()
        if not texte:
            continue
        if len(texte) > MAX_CHARS_JOURNAL:
            texte = "[...extrait récent...]\n" + texte[-MAX_CHARS_JOURNAL:]
        blocs.append(f"### {d}\n{masquer_secrets(texte)}")
        if len(blocs) >= limite_jours:
            break
    if not blocs:
        return "Aucun journal des jours précédents disponible."
    blocs.reverse()
    return "\n\n".join(blocs)


def lister_sorties_validees() -> list[Path]:
    if not DOSSIER_SORTIES.exists():
        return []
    return sorted(
        [p for p in DOSSIER_SORTIES.rglob("*") if p.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


# --- Préparation ateliers, Web, Code, Vidéo ---

def preparer_proposition_atelier(atelier_cle: str, demande_steve: str) -> dict:
    regles = charger_json(FICHIER_REGLES, {"validation_humaine_obligatoire": True})
    memoire = charger_json(FICHIER_MEMOIRE, {"utilisateur": "Belalingbi Steve"})
    instruction = (
        f"{INSTRUCTIONS_ATELIERS.get(atelier_cle, INSTRUCTIONS_ATELIERS['recherche_connaissance_conseil'])}\n"
        "RÈGLE ABSOLUE : Tu ne prends JAMAIS de décision finale à la place de Steve "
        "et tu n'écris aucune sortie finale sans sa validation explicite.\n"
        "Réponds UNIQUEMENT avec un objet JSON valide :\n"
        "{\n"
        '  "titre": "Titre court",\n'
        '  "analyse_rapide": "Éclairage concis",\n'
        '  "options": ["Option 1...", "Option 2..."],\n'
        '  "avis_ia": "Recommandation non décisionnaire",\n'
        '  "proposition_detaillee": "Contenu prêt à être validé"\n'
        "}\n"
        f"Règles : {json.dumps(regles, ensure_ascii=False)}\n"
        f"Mémoire : {json.dumps(memoire, ensure_ascii=False)}"
    )
    return executer_requete_ia(
        type_capacite="atelier",
        system_instruction=instruction,
        demande_utilisateur=demande_steve,
        temperature=0.4,
        contexte_supplementaire={"atelier_cle": atelier_cle},
    )


def preparer_site_web(demande_steve: str) -> dict:
    instruction = (
        "Tu es l'architecte web du Studio IA de Belalingbi Steve.\n"
        "Prépare une proposition complète de site internet (HTML sémantique, CSS responsive, JS léger) "
        "en mode BROUILLON À VALIDER.\n"
        "Réponds UNIQUEMENT avec un JSON valide :\n"
        "{\n"
        '  "nom_projet": "site_brouillon",\n'
        '  "resume_architecture": "Structure et choix visuels",\n'
        '  "index_html": "Code HTML complet",\n'
        '  "styles_css": "Code CSS complet",\n'
        '  "script_js": "Code JS complet",\n'
        '  "points_validation": ["Point 1", "Point 2"]\n'
        "}"
    )
    return executer_requete_ia(
        type_capacite="site_web",
        system_instruction=instruction,
        demande_utilisateur=demande_steve,
        temperature=0.35,
    )


def preparer_code(demande_steve: str) -> dict:
    instruction = (
        "Tu es l'ingénieur logiciel du Studio IA de Belalingbi Steve.\n"
        "Produis un code clair, maintenable et sécurisé, avec explication et tests locaux.\n"
        "Réponds UNIQUEMENT avec un JSON valide :\n"
        "{\n"
        '  "titre_module": "Titre court",\n'
        '  "langage": "python | javascript | html_css | sql | bash",\n'
        '  "nom_fichier": "module_studio.py",\n'
        '  "code": "Code source complet",\n'
        '  "explication_technique": "Choix techniques et limites",\n'
        '  "commandes_test": "Comment tester en local"\n'
        "}"
    )
    return executer_requete_ia(
        type_capacite="code",
        system_instruction=instruction,
        demande_utilisateur=demande_steve,
        temperature=0.25,
    )


def preparer_fiche_video(photo_source: str, demande_steve: str) -> dict:
    instruction = (
        "Tu es le réalisateur visuel & vidéo du Studio IA de Belalingbi Steve.\n"
        "Prépare un dossier de génération vidéo à partir d'une photo source (mouvement caméra, "
        "animation, durée, format, prompt détaillé et points de vigilance de cohérence).\n"
        "Réponds UNIQUEMENT avec un JSON valide :\n"
        "{\n"
        '  "titre_sequence": "Titre court",\n'
        '  "photo_source": "chemin de la photo",\n'
        '  "prompt_video_detaille": "Description du mouvement et de la scène",\n'
        '  "parametres_suggeres": {"duree_sec": 6, "format": "16:9", "mouvement_camera": "travelling lent"},\n'
        '  "vigilance_coherence": "Points à vérifier sur le rendu"\n'
        "}"
    )
    return executer_requete_ia(
        type_capacite="video_photo",
        system_instruction=instruction,
        demande_utilisateur=demande_steve,
        temperature=0.4,
        contexte_supplementaire={"photo_source": photo_source},
    )


# --- Écriture & génération locale uniquement après confirmation explicite ---

def enregistrer_brouillon_web_valide(dossier_web: dict, confirme_steve: bool) -> Path | None:
    if not confirme_steve:
        return None
    DOSSIER_WEB.mkdir(parents=True, exist_ok=True)
    valider_chemin_confine(DOSSIER_WEB, DOSSIER_SORTIES)

    (DOSSIER_WEB / "index.html").write_text(dossier_web.get("index_html", ""), encoding="utf-8")
    (DOSSIER_WEB / "styles.css").write_text(dossier_web.get("styles_css", ""), encoding="utf-8")
    (DOSSIER_WEB / "app.js").write_text(dossier_web.get("script_js", ""), encoding="utf-8")
    (DOSSIER_WEB / "brief_site.json").write_text(
        json.dumps(dossier_web, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return DOSSIER_WEB


def enregistrer_brouillon_code_valide(dossier_code: dict, confirme_steve: bool) -> Path | None:
    if not confirme_steve:
        return None
    DOSSIER_CODE.mkdir(parents=True, exist_ok=True)

    nom_brut = dossier_code.get("nom_fichier", "module_studio.py")
    nom_sain = assainir_nom_fichier(nom_brut, "module_studio.py")
    cible = valider_chemin_confine(DOSSIER_CODE / nom_sain, DOSSIER_SORTIES)

    code = masquer_secrets(dossier_code.get("code", ""))
    cible.write_text(code, encoding="utf-8")

    meta_cible = DOSSIER_CODE / f"{nom_sain}.meta.json"
    meta_cible.write_text(
        json.dumps(dossier_code, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return cible


def enregistrer_fiche_video_validee(dossier_video: dict, confirme_steve: bool) -> Path | None:
    if not confirme_steve:
        return None
    DOSSIER_VIDEO.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cible = valider_chemin_confine(DOSSIER_VIDEO / f"fiche_video_{stamp}.json", DOSSIER_SORTIES)
    cible.write_text(
        json.dumps(dossier_video, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return cible


def generer_fichier_binaire(
    format_cible: str,
    titre: str,
    contenu_texte: str,
    confirme_steve: bool,
) -> Path | None:
    if not confirme_steve:
        return None
    DOSSIER_SORTIES.mkdir(parents=True, exist_ok=True)
    maintenant = datetime.now()
    date_str = maintenant.strftime("%Y-%m-%d")
    heure_str = maintenant.strftime("%H-%M")
    fmt = format_cible.lower().lstrip(".")

    nom_base = f"{date_str}_{heure_str}_{nettoyer_nom(titre)}"
    base = valider_chemin_confine(DOSSIER_SORTIES / nom_base, DOSSIER_SORTIES)
    lignes = [l.strip() for l in contenu_texte.splitlines() if l.strip()] or [titre]

    if fmt == "xlsx":
        try:
            import openpyxl
            chemin = base.with_suffix(".xlsx")
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Sortie_Studio"
            ws.append(["Titre", "Date", "Heure", "Ligne"])
            for l in lignes:
                ws.append([titre, date_str, heure_str, l])
            wb.save(chemin)
            return chemin
        except ImportError:
            # Fallback CSV si openpyxl n'est pas encore installé
            chemin = base.with_suffix(".csv")
            lignes_csv = ["Titre,Date,Heure,Ligne"] + [f'"{titre}","{date_str}","{heure_str}","{l}"' for l in lignes]
            chemin.write_text("\n".join(lignes_csv), encoding="utf-8")
            return chemin

    if fmt == "pptx":
        try:
            from pptx import Presentation
            chemin = base.with_suffix(".pptx")
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = titre
            slide.placeholders[1].text = "\n".join(lignes[:8])
            prs.save(chemin)
            return chemin
        except ImportError:
            chemin = base.with_suffix(".txt")
            chemin.write_text(f"PRÉSENTATION : {titre}\n\n" + "\n".join(lignes), encoding="utf-8")
            return chemin

    if fmt == "pdf":
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            chemin = base.with_suffix(".pdf")
            c = canvas.Canvas(str(chemin), pagesize=A4)
            _, h = A4
            y = h - 50
            c.setFont("Helvetica-Bold", 14)
            c.drawString(45, y, titre[:90])
            y -= 28
            c.setFont("Helvetica", 10)
            for l in lignes:
                if y < 50:
                    c.showPage()
                    y = h - 50
                    c.setFont("Helvetica", 10)
                c.drawString(45, y, l[:105])
                y -= 16
            c.save()
            return chemin
        except ImportError:
            chemin = base.with_suffix(".txt")
            chemin.write_text(f"DOCUMENT PDF (FORMAT TEXTE) : {titre}\n\n" + "\n".join(lignes), encoding="utf-8")
            return chemin

    if fmt == "db":
        chemin = base.with_suffix(".db")
        nom_table = valider_identifiant_sql("sorties_validees")
        conn = sqlite3.connect(chemin)
        try:
            cur = conn.cursor()
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {nom_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_creation TEXT NOT NULL,
                    heure_creation TEXT NOT NULL,
                    titre TEXT NOT NULL,
                    contenu TEXT NOT NULL
                )
                """
            )
            # Requête paramétrée anti-injection SQL
            cur.execute(
                f"INSERT INTO {nom_table} (date_creation, heure_creation, titre, contenu) VALUES (?, ?, ?, ?)",
                (date_str, heure_str, titre, "\n".join(lignes)),
            )
            conn.commit()
        finally:
            conn.close()
        return chemin

    raise ValueError(f"Format non supporté : {format_cible}")


def enregistrer_validation_et_sortie(
    atelier_cle: str,
    demande_steve: str,
    dossier: dict,
    decision_steve: str,
    justification_steve: str,
    valider_dans_sorties: bool,
) -> tuple[str, str]:
    maintenant = datetime.now()
    date_str = maintenant.strftime("%Y-%m-%d")
    heure_str = maintenant.strftime("%H:%M")

    titre = dossier.get("titre", "Proposition du studio")
    avis = dossier.get("avis_ia", "")
    contenu = dossier.get("proposition_detaillee") or dossier.get("analyse_rapide", "")

    demande_propre = masquer_secrets(demande_steve)
    titre_propre = masquer_secrets(titre)
    avis_propre = masquer_secrets(avis)
    contenu_propre = masquer_secrets(contenu)

    etat_sortie = "Non enregistrée dans sorties_a_valider/."
    if valider_dans_sorties:
        DOSSIER_SORTIES.mkdir(parents=True, exist_ok=True)
        nom_brut = f"{date_str}_{heure_str.replace(':', '-')}_{atelier_cle}_{nettoyer_nom(titre)}.md"
        nom_sain = assainir_nom_fichier(nom_brut)
        chemin_sortie = valider_chemin_confine(DOSSIER_SORTIES / nom_sain, DOSSIER_SORTIES)

        entete = (
            f"# {titre_propre}\n\n"
            f"- Date : {date_str} {heure_str}\n"
            f"- Atelier : `{atelier_cle}`\n"
            f"- Décision de Belalingbi Steve : {decision_steve or 'Non précisée'}\n"
            f"- Statut : Validé explicitement par Belalingbi Steve\n\n---\n\n"
        )
        chemin_sortie.write_text(entete + contenu_propre.strip() + "\n", encoding="utf-8")
        etat_sortie = f"Enregistrée dans `{chemin_sortie}`"

    journal = Path(f"journal_{date_str}.md")
    if not journal.exists():
        journal.write_text(f"# Journal IA — {date_str}\n\n", encoding="utf-8")

    entree = (
        f"## [{heure_str}] {atelier_cle} — {demande_propre}\n"
        f"- **Objet** : {titre_propre}\n"
        f"- **Avis IA** : {avis_propre}\n"
        f"- **Décision de Belalingbi Steve** : {decision_steve or 'Non précisée'}\n"
        f"- **Justification** : {justification_steve or 'Non précisée'}\n"
        f"- **Sortie** : {etat_sortie}\n"
    )
    with journal.open("a", encoding="utf-8") as f:
        f.write(entree + "\n")

    if justification_steve:
        memoire = charger_json(FICHIER_MEMOIRE, {"utilisateur": "Belalingbi Steve", "decisions": []})
        memoire.setdefault("decisions", []).append(
            f"{date_str} {heure_str} [{atelier_cle}] : {decision_steve} ({justification_steve})"
        )
        sauvegarder_json(FICHIER_MEMOIRE, memoire)

    return f"journal_{date_str}.md", etat_sortie
