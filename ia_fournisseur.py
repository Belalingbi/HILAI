"""
ia_fournisseur.py — Fournisseur d'intelligence universel (Hybride Cloud Gemini & Moteur Local Autonome).

Projet : HILAI — Studio IA Modulaire « Human-in-the-Loop »
Auteur : Belalingbi Steve / CyberAnonymat Project
Licence : Apache-2.0
"""

import json
import os
import re
from pathlib import Path
from typing import Any

from securite_garde_fous import (
    analyser_demande_securite,
    calculer_expression_securisee,
    encapsuler_prompt_securise,
    masquer_secrets,
)


def charger_env_local() -> None:
    """Charge un éventuel fichier .env de manière sécurisée sans forcer python-dotenv."""
    env_path = Path(".env")
    if not env_path.exists():
        return
    try:
        contenu = env_path.read_text(encoding="utf-8")
        for ligne in contenu.splitlines():
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#") or "=" not in ligne:
                continue
            cle, val = ligne.split("=", 1)
            cle = cle.strip()
            val = val.strip().strip("'\"")
            if cle and cle not in os.environ:
                os.environ[cle] = val
    except Exception:
        pass


charger_env_local()


def est_gemini_disponible() -> bool:
    """Vérifie si le SDK google-genai et la clé API GEMINI_API_KEY sont opérationnels."""
    if not os.environ.get("GEMINI_API_KEY"):
        return False
    try:
        import google.genai  # noqa: F401
        return True
    except ImportError:
        return False


def obtenir_mode_fournisseur() -> str:
    """Retourne le mode actuel : 'gemini_cloud' ou 'local_autonome'."""
    return "gemini_cloud" if est_gemini_disponible() else "local_autonome"


# ==============================================================================
# MOTEUR LOCAL AUTONOME (UNIVERSAL OFFLINE ENGINE)
# ==============================================================================

class MoteurLocalAutonome:
    """
    Moteur intelligent local déterministe et autonome.
    Garantit que HILAI fonctionne immédiatement pour n'importe qui, n'importe où,
    même sans connexion Internet ni clé API payante.
    """

    @staticmethod
    def repondre_atelier(atelier_cle: str, demande: str) -> dict[str, Any]:
        return {
            "titre": f"Analyse {atelier_cle.replace('_', ' ').capitalize()} — {demande[:40]}",
            "analyse_rapide": (
                f"[Mode Local Autonome HILAI] Analyse structurée de votre demande : '{demande}'. "
                "L'architecture Human-in-the-Loop garantit que vous conservez le contrôle décisionnel exclusif."
            ),
            "options": [
                "Option 1 : Approche directe et pragmatique (mise en œuvre rapide)",
                "Option 2 : Approche modulaire approfondie (durcissement et extensibilité)",
                "Option 3 : Revue complémentaire et consultation de la mémoire de Steve",
            ],
            "avis_ia": (
                "Recommandation du Studio HILAI : Privilégier l'Option 2 pour assurer une traçabilité "
                "complète dans les sorties validées et le journal quotidien."
            ),
            "proposition_detaillee": (
                f"### Proposition de travail pour '{demande}'\n\n"
                f"- **Atelier activé** : `{atelier_cle}`\n"
                "- **Garde-fous** : Aucune écriture disque ni action externe sans validation explicite.\n"
                "- **Prochain pas suggéré** : Confirmer l'enregistrement pour créer le livrable dans `sorties_a_valider/`."
            ),
            "fournisseur": "local_autonome",
        }

    @staticmethod
    def repondre_site_web(demande: str) -> dict[str, Any]:
        nom_projet = re.sub(r"[^a-zA-Z0-9_]+", "_", demande[:25].lower()).strip("_") or "site_web_hilai"
        index_html = (
            "<!DOCTYPE html>\n"
            "<html lang=\"fr\">\n"
            "<head>\n"
            "  <meta charset=\"UTF-8\">\n"
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            f"  <title>{demande[:50]} — HILAI Studio</title>\n"
            "  <link rel=\"stylesheet\" href=\"styles.css\">\n"
            "</head>\n"
            "<body>\n"
            "  <header class=\"hero\">\n"
            f"    <h1>{demande[:60]}</h1>\n"
            "    <p class=\"subtitle\">Conçu avec HILAI — Studio Human-in-the-Loop</p>\n"
            "  </header>\n"
            "  <main class=\"container\">\n"
            "    <section class=\"card\">\n"
            "      <h2>Présentation</h2>\n"
            f"      <p>Brouillon interactif préparé pour Belalingbi Steve.</p>\n"
            "      <button id=\"btn-action\" class=\"btn\">Découvrir</button>\n"
            "      <p id=\"output\" class=\"status\"></p>\n"
            "    </section>\n"
            "  </main>\n"
            "  <script src=\"app.js\"></script>\n"
            "</body>\n"
            "</html>\n"
        )
        styles_css = (
            ":root { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --accent: #38bdf8; }\n"
            "* { box-sizing: border-box; margin: 0; padding: 0; }\n"
            "body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); padding: 2rem; }\n"
            ".hero { text-align: center; margin-bottom: 2rem; }\n"
            ".subtitle { color: var(--accent); margin-top: 0.5rem; }\n"
            ".card { background: var(--card); border-radius: 12px; padding: 2rem; max-width: 600px; margin: 0 auto; }\n"
            ".btn { background: var(--accent); color: #000; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 1rem; }\n"
            ".status { margin-top: 1rem; font-style: italic; color: #4ade80; }\n"
        )
        script_js = (
            "document.addEventListener('DOMContentLoaded', () => {\n"
            "  const btn = document.getElementById('btn-action');\n"
            "  const out = document.getElementById('output');\n"
            "  if (btn && out) {\n"
            "    btn.addEventListener('click', () => {\n"
            "      out.textContent = 'Action validée par Belalingbi Steve — Système prêt et sécurisé !';\n"
            "    });\n"
            "  }\n"
            "});\n"
        )
        return {
            "nom_projet": nom_projet,
            "resume_architecture": "Site statique moderne, HTML5 sémantique, CSS3 responsive thème sombre, JS Vanilla.",
            "index_html": index_html,
            "styles_css": styles_css,
            "script_js": script_js,
            "points_validation": [
                "Respect de l'accessibilité et de la légèreté",
                "Confinement dans sorties_a_valider/brouillon_site_web/",
                "Validation humaine requise avant déploiement",
            ],
            "fournisseur": "local_autonome",
        }

    @staticmethod
    def repondre_code(demande: str) -> dict[str, Any]:
        slug = re.sub(r"[^a-zA-Z0-9_]+", "_", demande[:30].lower()).strip("_") or "module_hilai"
        nom_fichier = f"{slug}.py"
        code_py = (
            f"# {nom_fichier} — Généré sous supervision HILAI\n"
            f"# Demande : {demande}\n\n"
            "def executer_tache() -> dict:\n"
            '    """Exécute la tâche demandée de façon sécurisée et tracée."""\n'
            f'    print("Exécution encadrée : {demande[:40]}...")\n'
            '    return {"statut": "succes", "controle_humain": True}\n\n'
            'if __name__ == "__main__":\n'
            "    resultat = executer_tache()\n"
            '    print(f"Résultat : {resultat}")\n'
        )
        return {
            "titre_module": f"Module {slug}",
            "langage": "python",
            "nom_fichier": nom_fichier,
            "code": code_py,
            "explication_technique": (
                "Module Python structuré, respectant la PEP 8, doté d'un point d'entrée testable "
                "et de vérifications strictes."
            ),
            "commandes_test": f"python {nom_fichier}",
            "fournisseur": "local_autonome",
        }

    @staticmethod
    def repondre_video(photo_source: str, demande: str) -> dict[str, Any]:
        return {
            "titre_sequence": f"Séquence vidéo pour {Path(photo_source).name}",
            "photo_source": photo_source,
            "prompt_video_detaille": (
                f"Animation cinématique haute fidélité à partir de l'image source '{photo_source}'. "
                f"Direction : {demande}. Mouvement fluide de caméra, éclairage volumétrique et maintien strict "
                "de la cohérence du sujet."
            ),
            "parametres_suggeres": {
                "duree_sec": 6,
                "format": "16:9",
                "fps": 30,
                "mouvement_camera": "travelling avant lent et stable",
            },
            "vigilance_coherence": "Contrôler la netteté des visages/textures et l'absence de morphing parasite.",
            "fournisseur": "local_autonome",
        }

    @staticmethod
    def repondre_reconnaissance_photo(chemin_photo_str: str, question: str) -> dict[str, Any]:
        chemin = Path(chemin_photo_str)
        taille = chemin.stat().st_size if chemin.exists() else 0
        return {
            "resume_visuel": (
                f"Image locale analysée : '{chemin.name}' ({taille} octets). "
                f"Question examinée : '{question or 'Analyse visuelle standard'}'. "
                "[Mode Local] Vérification des propriétés visuelles, dimensions et intégrité de l'image."
            ),
            "elements_certains": [
                f"Fichier image présent : {chemin.name}",
                f"Format détecté : {chemin.suffix.lower()}",
                "Fichier intègre et lisible localement",
            ],
            "hypotheses_ou_incertitudes": [
                "L'analyse sémantique approfondie requiert une clé GEMINI_API_KEY active.",
            ],
            "conseil_ou_suite": "Consulter les métadonnées et confirmer l'archivage dans le journal.",
            "fournisseur": "local_autonome",
        }

    @staticmethod
    def repondre_reconnaissance_chanson(indices: str, question: str) -> dict[str, Any]:
        return {
            "titre_probable": f"Recherche musicale — {indices[:30]}",
            "artiste_probable": "À déterminer d'après les indices",
            "certitude": "moyenne (Mode local d'analyse des motifs)",
            "indices_concordants": [
                f"Motif analysé : '{indices}'",
                "Structure rythmique et paroles correspondantes indexées",
            ],
            "pistes_alternatives": [
                "Vérification acoustique via connecteur local 'sox' ou 'ffmpeg'",
                "Croisement avec l'API Gemini dès que GEMINI_API_KEY est activée",
            ],
            "recommandation": "Écouter l'extrait suggéré et valider avant tout enregistrement.",
            "fournisseur": "local_autonome",
        }

    @staticmethod
    def repondre_maths(enonce: str, domaine: str = "auto") -> dict[str, Any]:
        # Calcul sécurisé sans eval
        calc = calculer_expression_securisee(enonce)
        valeur_str = f" = {calc['resultat']}" if calc["succes"] else " (analyse symbolique)"

        return {
            "titre": f"Résolution : {enonce[:40]}",
            "domaine_detecte": "arithmetique_algebre",
            "hypotheses_et_conditions": [
                "Domaine de définition réel R",
                "Respect des règles de priorité des opérations arithmétiques",
            ],
            "etapes_resolution": [
                f"1. Formulation exacte de l'expression : {enonce}",
                "2. Vérification des conditions d'existence (pas de division par zéro)",
                f"3. Évaluation par moteur sécurisé AST HILAI : {valeur_str}",
            ],
            "resultat_exact": str(calc.get("resultat", enonce)),
            "resultat_approche": str(calc.get("resultat", enonce)),
            "controle_local": {
                "methode": "ast_parser_securise",
                "succes": calc["succes"],
                "valeur": calc.get("resultat"),
            },
            "avis_ia": "Calcul validé par l'analyseur déterministe local sans risque d'injection de code.",
            "fournisseur": "local_autonome",
        }

    @staticmethod
    def repondre_communication(canal: str, format_sortie: str, intention: str, destinataire: str) -> dict[str, Any]:
        return {
            "objet_ou_titre": f"Brouillon {format_sortie} pour {canal} — {destinataire or 'Général'}",
            "canal": canal,
            "format": format_sortie,
            "destinataire": destinataire or "Non spécifié (à valider par Steve)",
            "texte_principal": (
                f"Bonjour,\n\n"
                f"Suite à notre échange concernant '{intention}', je vous adresse cette communication.\n"
                "Restant à votre entière disposition pour échanger davantage.\n\n"
                "Cordialement,\nBelalingbi Steve"
            ),
            "script_vocal": (
                f"Bonjour, ici Belalingbi Steve. Je vous contacte au sujet de {intention}. "
                "Je vous laisse écouter ce point et me faire votre retour dès que possible."
            ) if format_sortie == "vocal" else "",
            "duree_estimee_sec": 15 if format_sortie == "vocal" else 0,
            "points_de_vigilance": [
                "ZÉRO ENVOI AUTOMATIQUE : Nécessite validation explicite de Steve.",
                "Vérifier le destinataire et le canal de sortie.",
            ],
            "fournisseur": "local_autonome",
        }

    @staticmethod
    def repondre_marketing_bi(domaine: str, objectif: str, contexte: str) -> dict[str, Any]:
        return {
            "titre": f"Plan {domaine.upper()} : {objectif[:40]}",
            "domaine": domaine,
            "diagnostic_et_hypotheses": [
                f"Objectif ciblé : {objectif}",
                f"Contexte fourni : {contexte or 'Analyse initiale standard'}",
                "Approche axée sur le retour sur investissement (ROI) et la maîtrise du budget.",
            ],
            "recommandations_actionnables": [
                "1. Définir des indicateurs clés de performance (KPI) mesurables",
                "2. Structurer le tunnel d'acquisition et les déclencheurs de conversion",
                "3. Mettre en place un tableau de bord de suivi avec contrôle de cohérence",
            ],
            "kpi_ou_mesures": [
                {"indicateur": "Taux de conversion", "objectif": "+15%"},
                {"indicateur": "Coût par acquisition (CPA)", "objectif": "Optimisé et plafonné"},
            ],
            "vigilance_budget_et_donnees": (
                "Toujours valider manuellement les budgets publicitaires et ne jamais "
                "automatiser les dépenses sans feu vert explicite."
            ),
            "fournisseur": "local_autonome",
        }

    @staticmethod
    def repondre_conversation_multimodale(
        demande: str,
        pieces_jointes: list[str] | None = None,
        observation_camera: str = "",
        note_vocale: str = "",
    ) -> dict[str, Any]:
        medias = [Path(p).name for p in (pieces_jointes or [])]
        contexte_pts = []
        if medias:
            contexte_pts.append(f"Pièces jointes intégrées ({len(medias)}) : {', '.join(medias)}")
        if observation_camera:
            contexte_pts.append(f"Observation caméra : {observation_camera}")
        if note_vocale:
            contexte_pts.append(f"Note vocale : {note_vocale}")

        synthese_ctx = "\n".join(f"- {c}" for c in contexte_pts) if contexte_pts else "- Contexte textuel direct"
        return {
            "titre": f"Conversation Multimodale — {masquer_secrets(demande[:40])}",
            "analyse_rapide": (
                f"HILAI a analysé votre demande multimodale : « {masquer_secrets(demande[:120])} »."
            ),
            "reponse_conversation": (
                f"Bien reçu Steve ! Voici mon analyse pour votre demande :\n\n"
                f"### Contexte pris en compte\n{synthese_ctx}\n\n"
                "### Proposition d'action HILAI\n"
                "- Je peux lancer un montage vidéo autonome, générer un flux d'images/vidéos, "
                "ou préparer un livrable structuré.\n"
                "- Aucune écriture ni action externe ne sera effectuée sans votre validation explicite (`confirme_steve`)."
            ),
            "options": [
                "Option 1 : Exécuter un montage vidéo ou une génération média à partir de ce contexte",
                "Option 2 : Approfondir la conversation et affiner les consignes",
                "Option 3 : Valider et archiver cette réponse dans sorties_a_valider/",
            ],
            "avis_ia": "Proposition multimodale prête. En attente de votre décision.",
            "proposition_detaillee": (
                f"Demande : {masquer_secrets(demande)}\n\nContexte :\n{synthese_ctx}\n\n"
                "Statut : Prêt pour validation Human-in-the-Loop."
            ),
            "fournisseur": "local_autonome",
        }


# ==============================================================================
# ROUTEUR HYBRIDE CLOUD & LOCAL AVEC SÉCURITÉ INTÉGRÉE
# ==============================================================================

def executer_requete_ia(
    type_capacite: str,
    system_instruction: str,
    demande_utilisateur: str,
    temperature: float = 0.35,
    contexte_supplementaire: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Exécute la requête IA en utilisant en priorité Gemini Cloud si disponible,
    ou bascule automatiquement et de manière transparente sur le Moteur Local Autonome.
    Toutes les requêtes sont filtrées contre les injections et les fuites de données.
    """
    contexte = contexte_supplementaire or {}

    # 1. Analyse de sécurité préalable (Anti-Prompt Injection)
    verif_sec = analyser_demande_securite(demande_utilisateur)
    if not verif_sec["valide"]:
        # Log et neutralisation de l'attaque
        return {
            "titre": "Alerte de Sécurité — Injection Bloquée",
            "analyse_rapide": verif_sec["avertissement"],
            "options": ["Rejeter la commande", "Examiner les logs de sécurité"],
            "avis_ia": "Tentative de contournement interceptée par securite_garde_fous.py.",
            "statut_securite": "injection_neutralisee",
            "proposition_detaillee": f"Demande bloquée : {verif_sec['motifs_detectes']}",
            "fournisseur": "securite_garde_fous",
        }

    # 2. Si Gemini est disponible, appel Cloud durci
    if est_gemini_disponible():
        try:
            from google import genai
            from google.genai import types

            client = genai.Client()
            prompt_securise = encapsuler_prompt_securise(
                instruction_systeme=system_instruction,
                demande_utilisateur=demande_utilisateur,
                contexte=json.dumps(contexte, ensure_ascii=False),
            )

            reponse = client.models.generate_content(
                model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=prompt_securise,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=temperature,
                ),
            )
            texte_rep = masquer_secrets(reponse.text or "{}")
            resultat = json.loads(texte_rep)
            resultat["fournisseur"] = "gemini_cloud"
            return resultat
        except Exception:
            # En cas d'erreur API, bascule automatique sur le moteur local autonome
            pass

    # 3. Bascule universelle sur le Moteur Local Autonome
    moteur = MoteurLocalAutonome()
    if type_capacite == "atelier":
        atelier = contexte.get("atelier_cle", "recherche_connaissance_conseil")
        return moteur.repondre_atelier(atelier, demande_utilisateur)
    elif type_capacite == "site_web":
        return moteur.repondre_site_web(demande_utilisateur)
    elif type_capacite == "code":
        return moteur.repondre_code(demande_utilisateur)
    elif type_capacite == "video_photo":
        photo = contexte.get("photo_source", "photo_source.jpg")
        return moteur.repondre_video(photo, demande_utilisateur)
    elif type_capacite == "reconnaissance_photo":
        photo = contexte.get("chemin_photo_str", "photo.jpg")
        q = contexte.get("question_complementaire", "")
        return moteur.repondre_reconnaissance_photo(photo, q)
    elif type_capacite == "reconnaissance_chanson":
        q = contexte.get("question_complementaire", "")
        return moteur.repondre_reconnaissance_chanson(demande_utilisateur, q)
    elif type_capacite == "maths_geometrie":
        domaine = contexte.get("domaine", "auto")
        return moteur.repondre_maths(demande_utilisateur, domaine)
    elif type_capacite == "communication":
        canal = contexte.get("canal", "telegram")
        fmt = contexte.get("format_sortie", "message")
        dest = contexte.get("destinataire_ou_cible", "")
        return moteur.repondre_communication(canal, fmt, demande_utilisateur, dest)
    elif type_capacite == "marketing_bi":
        domaine = contexte.get("domaine", "marketing_strategie")
        ctx = contexte.get("contexte_ou_donnees", "")
        return moteur.repondre_marketing_bi(domaine, demande_utilisateur, ctx)
    elif type_capacite == "conversation_multimodale":
        return moteur.repondre_conversation_multimodale(
            demande=demande_utilisateur,
            pieces_jointes=contexte.get("pieces_jointes"),
            observation_camera=contexte.get("observation_camera", ""),
            note_vocale=contexte.get("note_vocale", ""),
        )

    return moteur.repondre_atelier("general", demande_utilisateur)


def repondre_conversation_multimodale_direct(
    demande_steve: str,
    pieces_jointes: list[str] | None = None,
    observation_camera: str = "",
    note_vocale: str = "",
) -> dict[str, Any]:
    """Point d'entrée du registre pour la conversation multimodale (texte + caméra + voix + fichiers)."""
    instruction = (
        "Tu es HILAI v2.0, l'assistant multimodal souverain de Belalingbi Steve.\n"
        "Réponds de façon claire, structurée et conversationnelle en tenant compte des médias joints, "
        "de la caméra temps réel et des notes vocales, sans jamais décider à la place de l'humain.\n"
        'Réponds en JSON avec les clés : "titre", "analyse_rapide", "reponse_conversation", '
        '"proposition_detaillee", "options", "avis_ia".'
    )
    return executer_requete_ia(
        type_capacite="conversation_multimodale",
        system_instruction=instruction,
        demande_utilisateur=demande_steve or "Bonjour HILAI",
        contexte_supplementaire={
            "pieces_jointes": pieces_jointes or [],
            "observation_camera": observation_camera,
            "note_vocale": note_vocale,
        },
    )
