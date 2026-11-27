"""
montage_video_studio.py — Moteur de montage vidéo autonome par instructions écrites
et connecteurs universels vers les plateformes de montage (Premiere Pro, DaVinci Resolve, CapCut, FFmpeg, EDL/XML).

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop » v2.0
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import json
import re
import shutil
import struct
import wave
from datetime import datetime
from pathlib import Path
from typing import Any

from connecteurs_et_sauvegarde import executer_outil_local_encadre
from fiabilite_studio import exiger_confirmation_steve
from generateur_media_infini import generer_image_procedurale
from ia_fournisseur import executer_requete_ia
from securite_garde_fous import (
    assainir_chaine_script,
    assainir_nom_fichier,
    echapper_xml_securise,
    ecrire_fichier_atomique,
    masquer_secrets,
    valider_chemin_confine,
)

DOSSIER_SORTIES = Path("sorties_a_valider")
DOSSIER_MONTAGES = DOSSIER_SORTIES / "montages"

PLATEFORMES_MONTAGE: dict[str, str] = {
    "ffmpeg_hilai": "Moteur autonome HILAI (FFmpeg)",
    "premiere_pro": "Adobe Premiere Pro (XML + ExtendScript)",
    "davinci_resolve": "DaVinci Resolve (Script Python + EDL)",
    "capcut": "CapCut / Éditeur Web (JSON)",
    "universel_edl_xml": "Export Universel (EDL / FCPXML / SRT)",
}


def _formater_timecode(secondes: float, fps: int = 30) -> str:
    sec_total = max(0.0, float(secondes))
    heures = int(sec_total // 3600)
    minutes = int((sec_total % 3600) // 60)
    secs = int(sec_total % 60)
    frames = int((sec_total - int(sec_total)) * fps) % fps
    return f"{heures:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"


def _formater_srt_time(secondes: float) -> str:
    ms_total = max(0, int(round(secondes * 1000)))
    heures = ms_total // 3600000
    minutes = (ms_total % 3600000) // 60000
    secs = (ms_total % 60000) // 1000
    ms = ms_total % 1000
    return f"{heures:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def analyser_instructions_montage(instruction: str, parametres: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Extrait automatiquement les spécifications de montage depuis une instruction écrite
    (durée, format, style, rythme, sous-titres, audio, FPS).
    """
    texte = (instruction or "").lower()
    params = parametres or {}

    # Durée détectée (ex: "45s", "2 min", "1m30")
    duree = float(params.get("duree_sec", 30))
    match_min = re.search(r"(\d+)\s*(?:min|minute|minutes|m)\b", texte)
    match_sec = re.search(r"(\d+)\s*(?:s|sec|seconde|secondes)\b", texte)
    if match_min and match_sec:
        duree = int(match_min.group(1)) * 60 + int(match_sec.group(1))
    elif match_min:
        duree = int(match_min.group(1)) * 60
    elif match_sec:
        duree = int(match_sec.group(1))
    duree = max(5.0, min(duree, 3600.0))

    # Format / Ratio
    ratio = "16:9"
    resolution = str(params.get("resolution", "1920x1080"))
    if any(k in texte for k in ("tiktok", "reels", "shorts", "vertical", "9:16")):
        ratio = "9:16"
        resolution = "1080x1920"
    elif any(k in texte for k in ("carré", "carre", "instagram", "1:1")):
        ratio = "1:1"
        resolution = "1080x1080"

    if "x" in resolution:
        try:
            w_str, h_str = resolution.lower().split("x", 1)
            largeur, hauteur = max(320, min(int(w_str), 3840)), max(240, min(int(h_str), 3840))
        except ValueError:
            largeur, hauteur = 1920, 1080
    else:
        largeur, hauteur = 1920, 1080

    # Style
    style = str(params.get("style", "Dynamique & Moderne"))
    if "cinéma" in texte or "cinema" in texte or "film" in texte:
        style = "Cinématique"
    elif "cyber" in texte or "tech" in texte or "néon" in texte:
        style = "Cyberpunk / Tech"
    elif "tuto" in texte or "éducatif" in texte or "formation" in texte:
        style = "Éducatif & Clair"
    elif "minimal" in texte or "sobre" in texte:
        style = "Minimaliste"

    fps = int(params.get("fps", 60 if "60" in texte else 30))
    fps = 60 if fps >= 50 else (24 if fps <= 25 else 30)

    avec_sous_titres = any(k in texte for k in ("sous-titre", "sous titre", "subtitle", "légende", "caption")) or True
    avec_musique = any(k in texte for k in ("musique", "rythm", "audio", "son", "bande")) or True
    transition = "glissement_dynamique" if "dynamique" in texte else "fondu_enchaine"

    return {
        "duree_totale_sec": duree,
        "ratio": ratio,
        "largeur": largeur,
        "hauteur": hauteur,
        "fps": fps,
        "style": style,
        "transition": transition,
        "sous_titres": avec_sous_titres,
        "normalisation_audio_lufs": -14.0 if avec_musique else -16.0,
    }


def inspecter_media_local(chemin_str: str) -> dict[str, Any]:
    """Inspecte un média local (image, audio WAV, vidéo) sans aucune exécution risquée."""
    chemin = Path(chemin_str)
    ext = chemin.suffix.lower()
    infos: dict[str, Any] = {
        "nom": assainir_nom_fichier(chemin.name),
        "chemin": str(chemin),
        "extension": ext,
        "existe": chemin.exists(),
        "type": "inconnu",
        "duree_sec": 5.0,
        "resolution": "1920x1080",
    }

    if ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}:
        infos["type"] = "image"
        infos["duree_sec"] = 4.0
        if chemin.exists() and ext == ".png":
            try:
                entete = chemin.read_bytes()[:24]
                if entete[:8] == b"\x89PNG\r\n\x1a\n":
                    w, h = struct.unpack(">II", entete[16:24])
                    infos["resolution"] = f"{w}x{h}"
            except Exception:
                pass
    elif ext in {".wav", ".mp3", ".ogg", ".m4a", ".flac"}:
        infos["type"] = "audio"
        infos["duree_sec"] = 30.0
        if chemin.exists() and ext == ".wav":
            try:
                with wave.open(str(chemin), "rb") as w:
                    frames = w.getnframes()
                    rate = w.getframerate() or 44100
                    infos["duree_sec"] = round(frames / rate, 2)
                    infos["sample_rate"] = rate
                    infos["channels"] = w.getnchannels()
            except Exception:
                pass
    elif ext in {".mp4", ".mov", ".mkv", ".avi", ".webm"}:
        infos["type"] = "video"
        infos["duree_sec"] = 12.0
    else:
        infos["type"] = "document"

    return infos


def _generer_pistes_timeline(
    instruction: str,
    specs: dict[str, Any],
    medias: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Construit les pistes temporelles de montage et les sous-titres synchronisés."""
    duree = specs["duree_totale_sec"]
    intro_fin = round(min(4.0, duree * 0.15), 2)
    outro_debut = round(max(intro_fin + 2.0, duree - min(5.0, duree * 0.18)), 2)

    visuels = [m for m in medias if m["type"] in {"video", "image"}]
    audios = [m for m in medias if m["type"] == "audio"]

    tracks: list[dict[str, Any]] = [
        {
            "piste": "V1 - Intro & Titre IA",
            "type": "video",
            "debut": 0.0,
            "fin": intro_fin,
            "label": "Accroche visuelle & Titre animé",
            "source": visuels[0]["nom"] if visuels else "intro_generee_hilai.png",
            "effet": f"{specs['style']} / Zoom-In + Titre",
            "couleur": "#38bdf8",
        }
    ]

    corps_duree = max(2.0, outro_debut - intro_fin)
    if visuels:
        nb_clips = len(visuels)
        seg = corps_duree / nb_clips
        for idx, med in enumerate(visuels):
            d_deb = round(intro_fin + idx * seg, 2)
            d_fin = round(intro_fin + (idx + 1) * seg, 2)
            tracks.append(
                {
                    "piste": "V2 - Rushes Assemblés",
                    "type": "video",
                    "debut": d_deb,
                    "fin": d_fin,
                    "label": f"Clip {idx + 1}: {med['nom']}",
                    "source": med["nom"],
                    "effet": f"Transition {specs['transition']} + Étalonnage",
                    "couleur": "#10b981",
                }
            )
    else:
        tracks.append(
            {
                "piste": "V2 - Rushes Synthétisés IA",
                "type": "video",
                "debut": intro_fin,
                "fin": outro_debut,
                "label": "Séquence principale générée par HILAI",
                "source": "sequence_principale_hilai.png",
                "effet": f"Mouvement caméra + {specs['transition']}",
                "couleur": "#10b981",
            }
        )

    tracks.append(
        {
            "piste": "V3 - Transitions & Outro",
            "type": "video",
            "debut": outro_debut,
            "fin": duree,
            "label": "Synthèse & Appel à l'action",
            "source": "outro_hilai.png",
            "effet": "Fondu de sortie + Logo",
            "couleur": "#a855f7",
        }
    )

    # Piste Sous-titres
    mots = [m for m in re.split(r"\s+", instruction.strip()) if m]
    resume_texte = " ".join(mots[:12]) or "Montage autonome HILAI Studio"
    sous_titres = [
        {"index": 1, "debut": 0.5, "fin": intro_fin, "texte": f"HILAI Studio — {resume_texte[:48]}"},
        {
            "index": 2,
            "debut": intro_fin,
            "fin": round((intro_fin + outro_debut) / 2, 2),
            "texte": "Séquence assemblée automatiquement selon vos instructions.",
        },
        {
            "index": 3,
            "debut": round((intro_fin + outro_debut) / 2, 2),
            "fin": outro_debut,
            "texte": f"Style {specs['style']} • Format {specs['ratio']} ({specs['fps']} FPS)",
        },
        {"index": 4, "debut": outro_debut, "fin": duree, "texte": "Validé par Belalingbi Steve — CyberAnonymat"},
    ]

    tracks.append(
        {
            "piste": "T1 - Sous-titres IA (.srt)",
            "type": "subtitles",
            "debut": 0.5,
            "fin": duree,
            "label": f"{len(sous_titres)} blocs synchronisés",
            "source": "sous_titres.srt",
            "effet": "Style lisible centré",
            "couleur": "#f59e0b",
        }
    )

    # Piste Audio
    tracks.append(
        {
            "piste": "A1 - Musique & Voix",
            "type": "audio",
            "debut": 0.0,
            "fin": duree,
            "label": f"Audio principal ({specs['normalisation_audio_lufs']} LUFS)",
            "source": audios[0]["nom"] if audios else "piste_audio_equilibree.wav",
            "effet": f"loudnorm=I={specs['normalisation_audio_lufs']}",
            "couleur": "#22c55e",
        }
    )

    return tracks, sous_titres


def _construire_srt(sous_titres: list[dict[str, Any]]) -> str:
    blocs = []
    for st in sous_titres:
        blocs.append(
            f"{st['index']}\n"
            f"{_formater_srt_time(st['debut'])} --> {_formater_srt_time(st['fin'])}\n"
            f"{masquer_secrets(st['texte'])}\n"
        )
    return "\n".join(blocs)


def _construire_edl_cmx3600(titre: str, specs: dict[str, Any], tracks: list[dict[str, Any]]) -> str:
    fps = specs["fps"]
    lignes = [f"TITLE: {masquer_secrets(titre).upper()[:60]}", "FCM: NON-DROP FRAME", ""]
    edit_num = 1
    for tr in tracks:
        if tr["type"] not in {"video", "audio"}:
            continue
        canal = "V" if tr["type"] == "video" else "A1"
        src_in = _formater_timecode(0.0, fps)
        src_out = _formater_timecode(max(0.5, tr["fin"] - tr["debut"]), fps)
        rec_in = _formater_timecode(tr["debut"], fps)
        rec_out = _formater_timecode(tr["fin"], fps)
        nom_reel = re.sub(r"[^A-Z0-9_]", "_", tr["source"].upper())[:16] or "CLIP"
        lignes.append(f"{edit_num:03d}  {nom_reel:<16} {canal:<4} C        {src_in} {src_out} {rec_in} {rec_out}")
        lignes.append(f"* FROM CLIP NAME: {masquer_secrets(tr['source'])}")
        edit_num += 1
    return "\n".join(lignes) + "\n"


def _construire_premiere_xml(titre: str, specs: dict[str, Any], tracks: list[dict[str, Any]]) -> str:
    fps = specs["fps"]
    total_frames = int(specs["duree_totale_sec"] * fps)
    titre_safe = echapper_xml_securise(titre)
    clips_xml = []
    for idx, tr in enumerate(tracks, start=1):
        if tr["type"] != "video":
            continue
        start_f = int(tr["debut"] * fps)
        end_f = max(start_f + 1, int(tr["fin"] * fps))
        nom_safe = echapper_xml_securise(tr["label"])
        src_safe = echapper_xml_securise(tr["source"])
        clips_xml.append(
            f"        <clipitem id=\"clipitem-{idx}\">\n"
            f"          <name>{nom_safe}</name>\n"
            f"          <duration>{end_f - start_f}</duration>\n"
            f"          <start>{start_f}</start>\n"
            f"          <end>{end_f}</end>\n"
            f"          <file id=\"file-{idx}\"><name>{src_safe}</name></file>\n"
            f"        </clipitem>"
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE xmeml>\n'
        '<xmeml version="5">\n'
        '  <sequence id="hilai-sequence-1">\n'
        f'    <name>{titre_safe}</name>\n'
        f'    <duration>{total_frames}</duration>\n'
        f'    <rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>\n'
        '    <media>\n'
        '      <video>\n'
        '        <format><samplecharacteristics>'
        f'<width>{specs["largeur"]}</width><height>{specs["hauteur"]}</height>'
        '</samplecharacteristics></format>\n'
        '        <track>\n'
        + "\n".join(clips_xml)
        + "\n        </track>\n"
        '      </video>\n'
        '    </media>\n'
        '  </sequence>\n'
        '</xmeml>\n'
    )


def _construire_fcpxml(titre: str, specs: dict[str, Any], tracks: list[dict[str, Any]]) -> str:
    fps = specs["fps"]
    titre_safe = echapper_xml_securise(titre)
    duree_s = int(specs["duree_totale_sec"])
    clips = []
    for tr in tracks:
        if tr["type"] != "video":
            continue
        d_s = max(1, int(round(tr["fin"] - tr["debut"])))
        off_s = int(round(tr["debut"]))
        clips.append(
            f'            <clip name="{echapper_xml_securise(tr["label"])}" '
            f'offset="{off_s}s" duration="{d_s}s" start="0s"/>'
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<fcpxml version="1.9">\n'
        '  <resources>\n'
        f'    <format id="r1" frameDuration="1/{fps}s" width="{specs["largeur"]}" height="{specs["hauteur"]}"/>\n'
        '  </resources>\n'
        '  <library>\n'
        '    <event name="HILAI Studio v2">\n'
        f'      <project name="{titre_safe}">\n'
        f'        <sequence format="r1" duration="{duree_s}s">\n'
        '          <spine>\n'
        + "\n".join(clips)
        + "\n          </spine>\n"
        '        </sequence>\n'
        '      </project>\n'
        '    </event>\n'
        '  </library>\n'
        '</fcpxml>\n'
    )


def _construire_premiere_jsx(titre: str, tracks: list[dict[str, Any]]) -> str:
    titre_js = assainir_chaine_script(titre)
    sources_js = assainir_chaine_script([tr["source"] for tr in tracks if tr["type"] in {"video", "audio"}])
    return (
        "// Script ExtendScript Adobe Premiere Pro généré par HILAI Studio v2.0\n"
        f"var nomProjet = {titre_js};\n"
        f"var mediasSources = {sources_js};\n"
        "if (app && app.project) {\n"
        "    app.project.createNewSequence(nomProjet, 'hilai_seq_01');\n"
        "    $.writeln('Séquence HILAI prête pour import : ' + nomProjet);\n"
        "}\n"
    )


def _construire_davinci_python(titre: str, specs: dict[str, Any], tracks: list[dict[str, Any]]) -> str:
    titre_py = assainir_chaine_script(titre)
    tracks_json = json.dumps(tracks, indent=2, ensure_ascii=False)
    return (
        '"""Script DaVinci Resolve API généré par HILAI Studio v2.0 (exécution manuelle dans DaVinci)."""\n'
        "import json\n\n"
        f"TITRE_PROJET = {titre_py}\n"
        f"FPS = {specs['fps']}\n"
        f"TIMELINE_SPEC = json.loads({assainir_chaine_script(tracks_json)})\n\n"
        "def creer_timeline_davinci(resolve_app):\n"
        "    pm = resolve_app.GetProjectManager()\n"
        "    projet = pm.GetCurrentProject() or pm.CreateProject(TITRE_PROJET)\n"
        "    media_pool = projet.GetMediaPool()\n"
        "    timeline = media_pool.CreateEmptyTimeline(TITRE_PROJET)\n"
        "    return {'projet': TITRE_PROJET, 'timeline': bool(timeline), 'pistes': len(TIMELINE_SPEC)}\n"
    )


def _construire_capcut_json(titre: str, specs: dict[str, Any], tracks: list[dict[str, Any]]) -> str:
    capcut_tracks = []
    for idx, tr in enumerate(tracks):
        capcut_tracks.append(
            {
                "id": f"track_{idx + 1}",
                "type": tr["type"],
                "segments": [
                    {
                        "material_name": masquer_secrets(tr["source"]),
                        "label": masquer_secrets(tr["label"]),
                        "target_timerange": {
                            "start": int(tr["debut"] * 1_000_000),
                            "duration": int(max(0.1, tr["fin"] - tr["debut"]) * 1_000_000),
                        },
                        "effect": tr["effet"],
                    }
                ],
            }
        )
    doc = {
        "name": masquer_secrets(titre),
        "platform": "CapCut / Web Editor",
        "canvas_config": {"width": specs["largeur"], "height": specs["hauteur"], "ratio": specs["ratio"]},
        "fps": specs["fps"],
        "duration": int(specs["duree_totale_sec"] * 1_000_000),
        "tracks": capcut_tracks,
    }
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def generer_export_plateforme(plan_montage: dict[str, Any], plateforme: str) -> dict[str, str]:
    """Génère les fichiers d'export adaptés à la plateforme cible (100% assainis)."""
    titre = plan_montage.get("titre", "Montage_HILAI")
    specs = plan_montage.get("parametres", {})
    tracks = plan_montage.get("timeline_tracks", [])
    sous_titres = plan_montage.get("sous_titres", [])
    srt_str = _construire_srt(sous_titres)

    fichiers: dict[str, str] = {
        "plan_montage.json": json.dumps(plan_montage, indent=2, ensure_ascii=False) + "\n",
        "sous_titres.srt": srt_str,
    }

    if "premiere" in plateforme.lower():
        fichiers["premiere_timeline.xml"] = _construire_premiere_xml(titre, specs, tracks)
        fichiers["premiere_assemblage.jsx"] = _construire_premiere_jsx(titre, tracks)
    elif "davinci" in plateforme.lower():
        fichiers["davinci_montage.py"] = _construire_davinci_python(titre, specs, tracks)
        fichiers["davinci_timeline.edl"] = _construire_edl_cmx3600(titre, specs, tracks)
        fichiers["davinci_timeline.fcpxml"] = _construire_fcpxml(titre, specs, tracks)
    elif "capcut" in plateforme.lower():
        fichiers["draft_content.json"] = _construire_capcut_json(titre, specs, tracks)
    elif "edl" in plateforme.lower() or "xml" in plateforme.lower() or "universel" in plateforme.lower():
        fichiers["timeline_universelle.edl"] = _construire_edl_cmx3600(titre, specs, tracks)
        fichiers["timeline_universelle.fcpxml"] = _construire_fcpxml(titre, specs, tracks)
        fichiers["premiere_compatible.xml"] = _construire_premiere_xml(titre, specs, tracks)
    else:
        # Moteur autonome FFmpeg + universel
        fichiers["timeline_universelle.edl"] = _construire_edl_cmx3600(titre, specs, tracks)

    return fichiers


def preparer_montage_video_autonome(
    instruction: str,
    pieces_jointes: list[str] | None = None,
    plateforme: str = "ffmpeg_hilai",
    parametres: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Prépare de manière autonome un montage vidéo complet à partir d'instructions écrites
    et des médias joints (sans modifier le disque tant que Steve n'a pas validé).
    """
    specs = analyser_instructions_montage(instruction, parametres)
    medias = [inspecter_media_local(p) for p in (pieces_jointes or [])]
    tracks, sous_titres = _generer_pistes_timeline(instruction, specs, medias)

    # Enrichissement optionnel via Gemini Cloud si disponible
    avis_ia = (
        f"Timeline autonome assemblée ({len(tracks)} pistes, {specs['duree_totale_sec']}s, "
        f"{specs['largeur']}x{specs['hauteur']} @ {specs['fps']}fps) prête pour {plateforme}."
    )
    ia_res = executer_requete_ia(
        type_capacite="atelier",
        system_instruction=(
            "Tu es le monteur vidéo autonome HILAI. Propose un découpage créatif concis en JSON "
            'avec les clés "titre" et "avis_ia".'
        ),
        demande_utilisateur=instruction or "Montage vidéo dynamique",
        contexte_supplementaire={"plateforme": plateforme, "specs": specs},
    )
    if ia_res.get("statut_securite") == "injection_neutralisee":
        return ia_res

    titre = f"Montage Autonome — {masquer_secrets((instruction or 'Projet Vidéo')[:45])}"
    plan = {
        "titre": titre,
        "resume": avis_ia,
        "plateforme_cible": PLATEFORMES_MONTAGE.get(plateforme, plateforme),
        "parametres": specs,
        "medias_sources": medias,
        "timeline_tracks": tracks,
        "sous_titres": sous_titres,
        "ffmpeg_disponible": bool(shutil.which("ffmpeg")),
        "points_validation": [
            "Vérifier l'enchaînement des pistes et des timecodes sur la timeline",
            "Valider les sous-titres synchronisés (.srt) et la normalisation -14 LUFS",
            "Confirmer l'export dans sorties_a_valider/montages/ (confirme_steve)",
        ],
        "fournisseur": ia_res.get("fournisseur", "local_autonome"),
    }
    plan["apercu_fichiers"] = list(generer_export_plateforme(plan, plateforme).keys())
    return plan


def preparer_connecteur_plateforme(plateforme: str, instruction: str, pieces_jointes: list[str] | None = None) -> dict[str, Any]:
    """Point d'entrée unifié du registre pour l'interaction avec les plateformes de montage."""
    return preparer_montage_video_autonome(
        instruction=instruction,
        pieces_jointes=pieces_jointes,
        plateforme=plateforme,
    )


def executer_et_exporter_montage(
    plan_montage: dict[str, Any],
    plateforme: str,
    confirme_steve: bool,
    lancer_rendu_ffmpeg: bool = False,
) -> dict[str, Any]:
    """
    Exporte le projet de montage et (optionnellement) lance le rendu MP4 via FFmpeg
    UNIQUEMENT si confirme_steve est strictement True.
    """
    exiger_confirmation_steve(confirme_steve, "export_montage_video")

    DOSSIER_MONTAGES.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = assainir_nom_fichier(plan_montage.get("titre", "montage"), "montage")[:35]
    dossier_projet = valider_chemin_confine(DOSSIER_MONTAGES / f"{slug}_{stamp}", DOSSIER_SORTIES)
    dossier_projet.mkdir(parents=True, exist_ok=True)

    fichiers = generer_export_plateforme(plan_montage, plateforme)
    chemins_ecrits: list[str] = []
    for nom_f, contenu in fichiers.items():
        cible = valider_chemin_confine(dossier_projet / assainir_nom_fichier(nom_f), DOSSIER_SORTIES)
        ecrire_fichier_atomique(cible, contenu)
        chemins_ecrits.append(str(cible))

    # Génération d'une vignette storyboard PNG (100% Python pur) dans le dossier projet
    vignette_bytes, _ = generer_image_procedurale(
        prompt=plan_montage.get("titre", "Montage HILAI"),
        style=plan_montage.get("parametres", {}).get("style", "Cinématique"),
        largeur=640,
        hauteur=360,
        seed=42,
    )
    vignette_path = valider_chemin_confine(dossier_projet / "storyboard_apercu.png", DOSSIER_SORTIES)
    ecrire_fichier_atomique(vignette_path, vignette_bytes)
    chemins_ecrits.append(str(vignette_path))

    rendu_ffmpeg = None
    if lancer_rendu_ffmpeg and shutil.which("ffmpeg"):
        video_out = valider_chemin_confine(dossier_projet / "rendu_hilai.mp4", DOSSIER_SORTIES)
        duree = int(min(30, plan_montage.get("parametres", {}).get("duree_totale_sec", 6)))
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(vignette_path),
            "-t", str(duree), "-vf", "scale=1280:720",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video_out),
        ]
        rendu_ffmpeg = executer_outil_local_encadre(
            nom_outil="ffmpeg_rendu_autonome",
            commande_args=cmd,
            confirme_steve=confirme_steve,
            timeout_sec=120,
        )
        if rendu_ffmpeg.get("statut") == "ok" and video_out.exists():
            chemins_ecrits.append(str(video_out))

    return {
        "dossier": str(dossier_projet),
        "fichiers": chemins_ecrits,
        "rendu_ffmpeg": rendu_ffmpeg,
    }
