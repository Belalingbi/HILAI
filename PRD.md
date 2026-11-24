# PRD — Studio IA Modulaire « Human-in-the-Loop » (HIL)

- **Propriétaire & Décideur final** : Belalingbi Steve[cite: 1]
- **Version** : 1.0 (Consolidation post-V1→V5, `studio_coeur.py`, `studio_lanceur.py`, `registre_studio.py` & extensions)[cite: 1]
- **Date** : 22 novembre 2026[cite: 1]
- **Statut** : Spécification produit & sécurité

---

## 1. Vision et proposition de valeur

Le **Studio IA Modulaire (HIL)** est un compagnon collaboratif personnel, de projet et de création multiplateforme (Windows & Linux, CLI et GUI) conçu selon une architecture **Human-in-the-Loop** combinée à un **apprentissage continu structuré**[cite: 1].

- **Rôle de l'IA** : analyser, structurer, proposer des options, formuler un avis argumenté, préparer des brouillons et des livrables[cite: 1].
- **Rôle de Belalingbi Steve** : garder le contrôle exclusif sur la prise de décision, la validation des leçons mémorisées, l'écriture/archivage dans `sorties_a_valider/`, la génération de fichiers locaux et toute action externe ou engageante[cite: 1].
- **Apprentissage progressif et maîtrisé** : capitalisation quotidienne via un journal daté (`journal_YYYY-MM-DD.md`), une mémoire de préférences/décisions (`memoire_preferences.json`) et un historique multi-jours, sans modification non validée[cite: 1].

---

## 2. Périmètre fonctionnel et modules

### 2.1 Noyau collaboratif, mémoire et garde-fou décisionnel
- **Règles de décision (`regles_decision.json`)** : séparation explicite entre ce que l'IA peut préparer seule et ce qui exige impérativement l'accord de Steve[cite: 1].
- **Charte et mémoire (`memoire_preferences.json`)** : style de communication, critères de décision (utilité concrète, maîtrise/sécurité, clarté/simplicité), lignes rouges absolues, principes appris et journal des décisions[cite: 1].
- **Journal quotidien & mémoire multi-jours** : traçabilité horodatée des demandes, propositions, décisions, justifications et bilans du soir, avec relecture multi-jours[cite: 1].
- **Zone de revue (`sorties_a_valider/`)** : aucun fichier final ou brouillon archivé n'est écrit sans confirmation explicite de l'utilisateur[cite: 1].

### 2.2 Les 4 ateliers principaux du studio
1. **Documents, Bureautique & Bases de données** : préparation et génération encadrée de fichiers `.xlsx`, `.pptx`, `.pdf` et bases locales SQLite (`.db`)[cite: 1].
2. **Recherche, Connaissance & Conseil** : exploration structurée, distinction faits/hypothèses et recommandations non décisionnaires[cite: 1].
3. **Visuel, Design & Musique** : mode brouillon encadré pour concepts d'identité/logos, images/photos, retouches/designs et trames musicales[cite: 1].
4. **Langue, Voix, Traduction & Appel direct** : compréhension/lecture multilingue, traduction fidèle, transcription, synthèse vocale et préparation d'échanges/appels sans action externe automatique[cite: 1].

### 2.3 Extensions spécialisées unifiées via `registre_studio.py`
- **Création de sites internet** : génération de brouillons web (`index.html`, `styles.css`, `app.js`) dans `sorties_a_valider/brouillon_site_web/` après validation[cite: 1].
- **Génération de code de programmation** : production de modules commentés, explications techniques et commandes de test locales dans `sorties_a_valider/brouillon_code/` après accord[cite: 1].
- **Préparation vidéo depuis photo** : structuration de briefs, mouvements caméra, paramètres et points de vigilance dans `sorties_a_valider/brouillon_video_photo/`[cite: 1].
- **Reconnaissance de photo et de chanson** : analyse multimodale d'images locales et structuration d'indices/outils locaux pour l'identification musicale[cite: 1].
- **Mathématiques & Géométrie** : résolution étape par étape, valeurs exactes vs approchées, conditions d'existence et vérification locale[cite: 1].
- **Réseaux sociaux, Messageries & Vocaux** : préparation de brouillons (mails, messages, scripts vocaux) pour Telegram, Slack, Facebook, Messenger, Instagram, TikTok, YouTube, Gmail, GMX, Proton, Microsoft, sans envoi automatique[cite: 1].
- **Marketing, SEO, Ads, Analytics & Power BI** : préparation de stratégies, SEO, campagnes Google Ads / Meta Ads, lecture GA4 et modèles/mesures Power BI[cite: 1].

### 2.4 Interfaces, diagnostic et sauvegarde
- **Interfaces CLI et GUI (`studio_lanceur.py`)** : compatibilité Windows et Linux, interface graphique non bloquante (threads) et onglet de relecture/aperçu[cite: 1].
- **Diagnostic (`verifier_studio.py`) & Snapshot (`connecteurs_et_sauvegarde.py`)** : contrôle de l'environnement et sauvegardes horodatées dans `sauvegardes_studio/` sur confirmation[cite: 1].

---

## 3. Exigences de sécurité, cybersécurité et durcissement (Produit)

- **Zéro action autonome engageante** : aucune publication, envoi de mail/message, initiation d'appel, dépense publicitaire, modification de configuration critique ou écriture de livrable sans validation humaine explicite[cite: 1].
- **Confidentialité des données personnelles et professionnelles** : les journaux, chartes, brouillons, exports marketing/BI et communications peuvent contenir des données sensibles ; ils doivent rester protégés localement et ne jamais exposer de secrets dans les logs ou artefacts générés[cite: 1].
- **Intégrité de la mémoire et anti-empoisonnement** : les mises à jour de `memoire_preferences.json` ne doivent pas être altérées silencieusement par des entrées malveillantes ou non validées[cite: 1].
- **Maîtrise des exécutions locales et canaux externes** : tout lancement d'outil local ou de script d'envoi/publication doit être explicitement confirmé, borné dans le temps et isolé[cite: 1].
- **Transparence et non-fabrication** : signaler clairement les incertitudes, limites d'outils ou données manquantes plutôt que d'inventer des faits ou des métriques[cite: 1].

---

## 4. Scénarios d'acceptation (Critères de succès)

1. **Verrouillage décisionnel** : si l'utilisateur refuse (`non` / case non cochée) l'enregistrement d'une sortie ou l'exécution d'un outil, aucun fichier n'est créé dans `sorties_a_valider/` et aucune commande externe n'est exécutée[cite: 1].
2. **Traçabilité complète** : chaque tour de boucle est journalisé dans `journal_YYYY-MM-DD.md` avec l'horodatage, la demande, l'avis de l'IA, la décision de Steve et l'état réel de la sortie[cite: 1].
3. **Résilience d'interface** : sous Windows et Linux, une préparation longue ne fige pas l'interface graphique et les erreurs sont affichées proprement sans révéler de secrets[cite: 1].
4. **Confinement des accès** : la relecture d'un fichier de sortie refuse tout chemin sortant de `sorties_a_valider/`[cite: 1].