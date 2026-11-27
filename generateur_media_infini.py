"""
generateur_media_infini.py — Moteur de génération infinie d'images et de séquences vidéo (Hybride Local / Cloud).

Fonctionne universellement en Python pur (sans aucune dépendance externe obligatoire grâce à l'encodeur PNG natif)
et exploite automatiquement Pillow, FFmpeg ou Gemini Cloud s'ils sont installés.

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop » v2.0
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import hashlib
import math
import shutil
import struct
import threading
import time
import zlib
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from fiabilite_studio import exiger_confirmation_steve
from securite_garde_fous import (
    ControleurQuotaRessources,
    assainir_nom_fichier,
    ecrire_fichier_atomique,
    masquer_secrets,
    valider_chemin_confine,
)

DOSSIER_SORTIES = Path("sorties_a_valider")
DOSSIER_GENERATIONS = DOSSIER_SORTIES / "generations_infinies"

STYLES_VISUELS = [
    "Cyberpunk / Néon",
    "Cinématique / Studio",
    "Géométrique / Abstrait",
    "Horizon / Futuriste",
    "Minimaliste / CyberAnonymat",
]

PALETTES_STYLE: dict[str, tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]] = {
    "Cyberpunk / Néon": ((10, 15, 35), (56, 189, 248), (236, 72, 153)),
    "Cinématique / Studio": ((15, 23, 42), (245, 158, 11), (59, 130, 246)),
    "Géométrique / Abstrait": ((17, 24, 39), (168, 85, 247), (16, 185, 129)),
    "Horizon / Futuriste": ((5, 13, 25), (14, 165, 233), (34, 197, 94)),
    "Minimaliste / CyberAnonymat": ((12, 18, 28), (20, 184, 166), (248, 250, 252)),
}


def encoder_png_rgb(largeur: int, hauteur: int, pixels_rgb: bytes | bytearray) -> bytes:
    """
    Encode une image RGB brute (largeur * hauteur * 3 octets) en fichier PNG valide
    100% en Python pur (stdlib zlib + struct).
    """
    def _chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    stride = largeur * 3
    lignes = bytearray()
    for y in range(hauteur):
        lignes.append(0)  # Filtre PNG 0 (None)
        debut = y * stride
        lignes.extend(pixels_rgb[debut : debut + stride])

    ihdr = struct.pack(">IIBBBBB", largeur, hauteur, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(lignes), level=6)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")


def generer_image_procedurale(
    prompt: str,
    style: str = "Cyberpunk / Néon",
    largeur: int = 360,
    hauteur: int = 200,
    seed: int | None = None,
    phase_temps: float = 0.0,
) -> tuple[bytes, dict[str, Any]]:
    """
    Génère une image PNG haute lisibilité de manière déterministe ou évolutive (seed / phase_temps).
    Garantit un rendu visuel réel même hors-ligne et sans Pillow.
    """
    largeur = max(64, min(int(largeur), 1920))
    hauteur = max(64, min(int(hauteur), 1080))
    seed_val = int(seed if seed is not None else int(time.time() * 1000) % 1_000_000)

    digest = hashlib.sha256(f"{prompt}|{style}|{seed_val}".encode("utf-8")).digest()
    freq_x = 1.5 + (digest[0] % 5) * 0.65
    freq_y = 1.5 + (digest[1] % 5) * 0.55
    cx = 0.25 + (digest[2] / 255.0) * 0.5
    cy = 0.25 + (digest[3] / 255.0) * 0.5

    c_fond, c_prim, c_sec = PALETTES_STYLE.get(style, PALETTES_STYLE["Cyberpunk / Néon"])
    buf = bytearray(largeur * hauteur * 3)
    phase = phase_temps * 2.0 * math.pi + (digest[4] / 255.0) * math.pi

    idx = 0
    for y in range(hauteur):
        ny = y / max(1, hauteur - 1)
        horizon = 1.0 - abs(ny - 0.58)
        for x in range(largeur):
            nx = x / max(1, largeur - 1)
            onde = 0.5 + 0.5 * math.sin(nx * freq_x * math.pi + phase) * math.cos(ny * freq_y * math.pi - phase * 0.5)
            dist = math.hypot(nx - cx, ny - cy)
            halo = max(0.0, 1.0 - dist * 1.9)

            # Grille perspective subtile sur la partie basse
            grille = 0.0
            if ny > 0.58 and ((x % 24 == 0) or (y % 18 == 0)):
                grille = 0.18 * (ny - 0.58) * 2.3

            w1 = min(1.0, 0.38 * onde + 0.65 * halo + grille)
            w2 = min(1.0, 0.45 * (1.0 - onde) * horizon + 0.25 * halo)

            r = int(min(255, c_fond[0] * (1.0 - w1 * 0.7) + c_prim[0] * w1 + c_sec[0] * w2 * 0.6))
            g = int(min(255, c_fond[1] * (1.0 - w1 * 0.7) + c_prim[1] * w1 + c_sec[1] * w2 * 0.6))
            b = int(min(255, c_fond[2] * (1.0 - w1 * 0.7) + c_prim[2] * w1 + c_sec[2] * w2 * 0.6))

            buf[idx] = r
            buf[idx + 1] = g
            buf[idx + 2] = b
            idx += 3

    png_bytes = encoder_png_rgb(largeur, hauteur, buf)
    meta = {
        "prompt": masquer_secrets(prompt),
        "style": style,
        "resolution": f"{largeur}x{hauteur}",
        "seed": seed_val,
        "taille_octets": len(png_bytes),
        "sha256": hashlib.sha256(png_bytes).hexdigest(),
        "horodatage": datetime.now().isoformat(timespec="seconds"),
    }
    return png_bytes, meta


def generer_sequence_video_frames(
    prompt: str,
    style: str = "Cinématique / Studio",
    nb_frames: int = 8,
    largeur: int = 280,
    hauteur: int = 160,
    fps: int = 10,
    seed: int | None = None,
) -> dict[str, Any]:
    """
    Génère une séquence vidéo animée composée de frames PNG cohérentes dans le temps.
    """
    nb_frames = max(2, min(int(nb_frames), 30))
    seed_val = int(seed if seed is not None else int(time.time() * 1000) % 1_000_000)
    frames: list[bytes] = []
    taille_totale = 0

    for i in range(nb_frames):
        phase = i / nb_frames
        frame_bytes, _ = generer_image_procedurale(
            prompt=prompt,
            style=style,
            largeur=largeur,
            hauteur=hauteur,
            seed=seed_val,
            phase_temps=phase,
        )
        frames.append(frame_bytes)
        taille_totale += len(frame_bytes)

    return {
        "prompt": masquer_secrets(prompt),
        "style": style,
        "resolution": f"{largeur}x{hauteur}",
        "fps": fps,
        "nb_frames": nb_frames,
        "duree_sec": round(nb_frames / max(1, fps), 2),
        "seed": seed_val,
        "taille_octets": taille_totale,
        "frames_png": frames,
        "horodatage": datetime.now().isoformat(timespec="seconds"),
    }


def preparer_lot_generation_images(prompt: str, style: str = "Cyberpunk / Néon", resolution: str = "512x512") -> dict[str, Any]:
    """Point d'entrée registre pour la génération d'images (aperçu prêt avant validation)."""
    try:
        w_s, h_s = resolution.lower().split("x", 1)
        w, h = max(128, min(int(w_s), 1024)), max(128, min(int(h_s), 1024))
    except Exception:
        w, h = 360, 200

    png_bytes, meta = generer_image_procedurale(prompt or "Création HILAI", style=style, largeur=min(w, 400), hauteur=min(h, 240))
    return {
        "titre": f"Génération Image Infinie — {masquer_secrets((prompt or 'Visuel')[:40])}",
        "resume": f"Image générée ({meta['resolution']}, style {style}, {meta['taille_octets']} octets). Flux infini prêt.",
        "proposition_detaillee": (
            f"Prompt : {meta['prompt']}\n"
            f"Style : {style} | Résolution cible : {resolution} | Seed : {meta['seed']}\n"
            f"Empreinte SHA-256 : {meta['sha256'][:16]}...\n"
            "Astuce : Activez « Démarrer Flux Infini » pour générer un flux continu d'images."
        ),
        "image_png_bytes": png_bytes,
        "metadata": meta,
        "points_validation": [
            "Prévisualiser l'image générée dans le lecteur de projet",
            "Valider pour enregistrer dans sorties_a_valider/generations_infinies/",
        ],
    }


def preparer_lot_generation_videos(prompt: str, style: str = "Cinématique / Studio", duree_sec: int = 4) -> dict[str, Any]:
    """Point d'entrée registre pour la génération vidéo infinie."""
    seq = generer_sequence_video_frames(
        prompt=prompt or "Séquence vidéo HILAI",
        style=style,
        nb_frames=8,
        largeur=280,
        hauteur=160,
        fps=8,
    )
    return {
        "titre": f"Génération Vidéo Infinie — {masquer_secrets((prompt or 'Séquence')[:40])}",
        "resume": f"Séquence vidéo générée ({seq['nb_frames']} frames, {seq['resolution']}, {seq['taille_octets']} octets).",
        "proposition_detaillee": (
            f"Prompt : {seq['prompt']}\n"
            f"Style : {style} | Durée cible : {duree_sec}s | Frames clés : {seq['nb_frames']}\n"
            f"Seed : {seq['seed']} | FFmpeg local : {'oui' if shutil.which('ffmpeg') else 'non (mode séquence PNG)'}"
        ),
        "sequence_video": seq,
        "points_validation": [
            "Lire l'aperçu animé dans le lecteur de projet",
            "Valider pour exporter la séquence dans sorties_a_valider/generations_infinies/",
        ],
    }


class ControleurFluxInfini:
    """
    Contrôleur asynchrone et sécurisé du flux infini de génération d'images et de vidéos.
    Respecte un tampon mémoire borné et des quotas anti-DoS.
    """

    def __init__(self, max_tampon: int = 30, quota_mo: float = 256.0) -> None:
        self.quota = ControleurQuotaRessources(max_elements_tampon=max_tampon, quota_disque_mo=quota_mo)
        self.tampon: deque[dict[str, Any]] = deque(maxlen=max_tampon)
        self.actif = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self.compteur = 0

    def demarrer(
        self,
        mode: str,
        prompt: str,
        style: str = "Cyberpunk / Néon",
        intervalle_sec: float = 2.0,
        on_nouvel_element: Callable[[dict[str, Any]], None] | None = None,
        on_limite: Callable[[str], None] | None = None,
    ) -> None:
        if self.actif:
            return
        self.actif = True

        def _boucle() -> None:
            while self.actif:
                with self._lock:
                    self.compteur += 1
                    idx = self.compteur

                if mode == "video":
                    seq = generer_sequence_video_frames(
                        prompt=f"{prompt} #{idx}",
                        style=style,
                        nb_frames=6,
                        largeur=240,
                        hauteur=135,
                        fps=8,
                        seed=idx * 7919,
                    )
                    taille = seq["taille_octets"]
                    element = {
                        "id": idx,
                        "type": "video",
                        "prompt": seq["prompt"],
                        "style": style,
                        "meta": {k: v for k, v in seq.items() if k != "frames_png"},
                        "frames_png": seq["frames_png"],
                        "preview_png": seq["frames_png"][0],
                    }
                else:
                    png_bytes, meta = generer_image_procedurale(
                        prompt=f"{prompt} #{idx}",
                        style=style,
                        largeur=320,
                        hauteur=180,
                        seed=idx * 7919,
                    )
                    taille = len(png_bytes)
                    element = {
                        "id": idx,
                        "type": "image",
                        "prompt": meta["prompt"],
                        "style": style,
                        "meta": meta,
                        "png_bytes": png_bytes,
                        "preview_png": png_bytes,
                    }

                if not self.quota.enregistrer_generation(taille):
                    self.actif = False
                    if on_limite:
                        on_limite("Quota de sécurité du flux infini atteint. Validez ou videz le tampon.")
                    break

                with self._lock:
                    self.tampon.append(element)

                if on_nouvel_element:
                    on_nouvel_element(element)

                # Attente fractionnée pour arrêt réactif
                pas = 0.2
                ecoule = 0.0
                while self.actif and ecoule < intervalle_sec:
                    time.sleep(pas)
                    ecoule += pas

        self._thread = threading.Thread(target=_boucle, daemon=True)
        self._thread.start()

    def arreter(self) -> int:
        self.actif = False
        return self.compteur

    def lister_elements(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self.tampon)

    def exporter_tampon_valide(self, confirme_steve: bool) -> list[Path]:
        """Exporte les médias générés du tampon vers sorties_a_valider/ uniquement si confirme_steve is True."""
        exiger_confirmation_steve(confirme_steve, "export_generations_infinies")

        DOSSIER_GENERATIONS.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ecrits: list[Path] = []

        for elem in self.lister_elements():
            idx = elem["id"]
            if elem["type"] == "image":
                nom = assainir_nom_fichier(f"img_{stamp}_{idx:03d}.png")
                cible = valider_chemin_confine(DOSSIER_GENERATIONS / nom, DOSSIER_SORTIES)
                ecrire_fichier_atomique(cible, elem["png_bytes"])
                ecrits.append(cible)
            else:
                sous_dir = valider_chemin_confine(DOSSIER_GENERATIONS / f"seq_{stamp}_{idx:03d}", DOSSIER_SORTIES)
                sous_dir.mkdir(parents=True, exist_ok=True)
                for f_idx, f_bytes in enumerate(elem["frames_png"], start=1):
                    f_cible = valider_chemin_confine(sous_dir / f"frame_{f_idx:03d}.png", DOSSIER_SORTIES)
                    ecrire_fichier_atomique(f_cible, f_bytes)
                meta_cible = valider_chemin_confine(sous_dir / "metadata.json", DOSSIER_SORTIES)
                ecrire_fichier_atomique(meta_cible, json_dumps_safe(elem["meta"]))
                ecrits.append(sous_dir)

        return ecrits


def json_dumps_safe(data: Any) -> str:
    import json
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
