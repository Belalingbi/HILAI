# TRD — Studio IA Modulaire « Human-in-the-Loop » (HIL)

- **Référentiel technique** : Python 3.x, `google-genai`, `pathlib`, `tkinter`, `sqlite3`, modules spécialisés (`studio_coeur.py`, `studio_lanceur.py`, `registre_studio.py`, `fiabilite_studio.py`, `verifier_studio.py`, `connecteurs_et_sauvegarde.py`, etc.)[cite: 1]
- **Cibles OS** : Windows et Linux (CLI & GUI)[cite: 1]
- **Focus** : Architecture technique, sécurité, cybersécurité, durcissement applicatif et résilience aux attaques

---

## 1. Architecture technique et flux de données

### 1.1 Structure des composants
- **Cœur & orchestration** : `studio_coeur.py` (4 ateliers, génération Web/Code/Vidéo, exports binaires `.xlsx`/`.pptx`/`.pdf`/`.db`, lecture journaux/sorties, journalisation et mise à jour mémoire)[cite: 1].
- **Registre & normalisation** : `registre_studio.py` (enregistrement centralisé des capacités, adaptation d'arguments, normalisation des sorties via `normaliser_resultat`)[cite: 1].
- **Fiabilité & garde-fous** : `fiabilite_studio.py` (`exiger_confirmation_steve`, `parser_json_robuste`, `lire_aperçu_sortie_securise`)[cite: 1].
- **Exécution encadrée & sauvegarde** : `connecteurs_et_sauvegarde.py` (`executer_outil_local_encadre`, `sauvegarder_snapshot_studio`)[cite: 1].
- **Modules métiers** : `reconnaissance_photo_chanson.py`, `mathematiques_geometrie.py`, `canaux_messageries_sociaux.py`, `marketing_seo_ads_bi.py`[cite: 1].
- **Interfaces & diagnostic** : `studio_lanceur.py` (CLI + GUI `ttk`/`tkinter` threadé) et `verifier_studio.py`[cite: 1].

### 1.2 Flux d'exécution type
1. Chargement de l'environnement (`GEMINI_API_KEY`) et des fichiers locaux (`regles_decision.json`, `memoire_preferences.json`, `journal_YYYY-MM-DD.md`, historique multi-jours)[cite: 1].
2. Routage vers la capacité/atelier choisi et appel LLM (`gemini-2.5-flash` via `google.genai.Client`) avec prompt système verrouillé[cite: 1].
3. Extraction et normalisation JSON tolérante (`parser_json_robuste`), présentation de l'analyse, des options, de l'avis et du brouillon[cite: 1].
4. Collecte de la décision et de la justification de Steve + confirmation explicite (`bool` / `oui`) avant toute écriture disque, export binaire, snapshot ou appel de sous-processus[cite: 1].

---

## 2. Modèle de menaces et protections contre les cyberattaques

| Menace / Vecteur d'attaque | Impact potentiel | Contre-mesures et protections requises |
| :--- | :--- | :--- |
| **Prompt Injection (directe ou indirecte via journaux, exports CSV/GA4/Ads, OCR photo, pages/textes)** | Tentative de faire contourner la règle Human-in-the-Loop, exfiltrer des données ou forcer une action/écriture non désirée | Maintenir l'autorité de validation dans le **code déterministe** (`confirme_steve is True`) et non uniquement dans le prompt LLM ; traiter les contenus externes/journaux comme des données non fiables ; exiger une confirmation explicite avant toute écriture ou exécution[cite: 1]. |
| **Path Traversal (traversée de répertoire dans les noms de fichiers ou aperçus)** | Lecture ou écriture de fichiers arbitraires hors de `sorties_a_valider/` ou `sauvegardes_studio/` | Résoudre les chemins avec `.resolve()` et vérifier l'appartenance stricte au répertoire autorisé (`base in cible.parents`) ; assainir les noms de fichiers (`nettoyer_nom` / `Path(...).name`)[cite: 1]. |
| **Command Injection / Exécution arbitraire de commandes** | Exécution de commandes shell non prévues ou dangereuses via `subprocess` | Interdire `shell=True` ; exiger `commande_args` sous forme de liste explicite d'arguments (jamais une chaîne shell interprétée) ; imposer `exiger_confirmation_steve(confirme_steve, ...)` et un `timeout`[cite: 1]. |
| **Évaluation de code / expressions non sûres (`eval` / `sympify`)** | Exécution de code Python arbitraire ou déni de service (DoS) calculatoire via une expression mathématique piégée | Éviter `eval()` sur des entrées libres ; restreindre strictement les symboles/fonctions autorisées, borner la longueur/complexité des expressions et isoler les calculs locaux[cite: 1]. |
| **Exposition de secrets / clés API / jetons** | Fuite de `GEMINI_API_KEY`, clés SMTP/IMAP, tokens réseaux sociaux/Ads dans le code, les journaux ou les snapshots | Lire les clés via variables d'environnement ou coffre/fichier local exclu du versioning (`.env` / permissions restreintes) ; ne jamais écrire de secrets dans `journal_*.md`, `memoire_preferences.json` ou `sorties_a_valider/`[cite: 1]. |
| **Empoisonnement de mémoire (`memoire_preferences.json`)** | Altération des critères, lignes rouges ou principes appris | N'ajouter à `principes_appris` / `journal_decisions` que les éléments explicitement validés par Steve ; conserver des sauvegardes snapshot horodatées pour restauration[cite: 1]. |
| **Déni de service local / blocage GUI ou saturation disque** | Gel de l'interface graphique, épuisement mémoire sur gros journaux ou fichiers binaires | Exécuter les appels réseau/E/S lourds dans des threads dédiés en désactivant les boutons d'action pendant le traitement ; tronquer l'historique injecté (`MAX_CHARS_JOURNAL`) et borner l'aperçu (`max_caracteres`)[cite: 1]. |

---

## 3. Durcissement applicatif (*Hardening*) et bonnes pratiques d'ingénierie

### 3.1 Hardening du code et des entrées/sorties
- **Validation booléenne stricte** : toute fonction d'écriture ou d'exécution (`enregistrer_brouillon_*`, `generer_fichier_binaire`, `executer_outil_local_encadre`, `sauvegarder_snapshot_studio`) doit vérifier `confirme_steve is True` avant toute mutation du système de fichiers ou appel système[cite: 1].
- **Encodage explicite et gestion des erreurs** : ouvrir/écrire tous les fichiers texte/JSON/Markdown en `encoding="utf-8"`, gérer proprement les exceptions (`ImportError`, `json.JSONDecodeError`, `FileNotFoundError`, `TimeoutExpired`) sans faire planter l'application ni exposer de traces sensibles à l'utilisateur final[cite: 1].
- **Parsing JSON défensif** : utiliser `parser_json_robuste` pour nettoyer les blocs Markdown (` ```json `) et extraire l'objet JSON de manière sûre, avec repli structuré si le modèle renvoie du texte brut[cite: 1].
- **Requêtes paramétrées SQLite** : utiliser systématiquement des paramètres liés (`?`) pour l'insertion de données dans SQLite et valider/assainir les identifiants de tables/colonnes[cite: 1].

### 3.2 Hardening de l'environnement et du poste (Windows & Linux)
- **Principe du moindre privilège** : exécuter le studio sous un compte utilisateur standard (sans privilèges administrateur/root) et restreindre les permissions des dossiers contenant les secrets, journaux et snapshots[cite: 1].
- **Dépendances maîtrisées** : n'installer que les paquets nécessaires (`google-genai`, et optionnellement `sympy`, `openpyxl`, `python-pptx`, `reportlab`, `python3-tk` sous Linux) et vérifier leur intégrité avant exécution[cite: 1].
- **Hygiène des canaux externes & APIs** : pour les messageries (Gmail, GMX, Proton, Microsoft) et réseaux/régies (Telegram, Slack, Meta, Google Ads, GA4, Power BI), utiliser des jetons/identifiants à portée minimale, révocables, stockés hors code source, et conserver un double contrôle humain sur toute action externe ou budgétaire[cite: 1].

---

## 4. Plan de tests de sécurité et de non-régression

1. **Tests de garde-fou (Negative Tests)** : vérifier qu'un appel avec `confirme_steve=False` lève une exception ou retourne `None` / statut `annule` sans créer ni modifier aucun fichier.
2. **Tests de confinement de chemin** : vérifier que `lire_aperçu_sortie_securise` rejette les chemins relatifs ou absolus ciblant l'extérieur de `sorties_a_valider/` (ex. `../regles_decision.json` ou `/etc/passwd`).
3. **Tests de robustesse LLM / JSON** : soumettre des réponses simulées malformées, entourées de ` ```json ` ou tronquées à `parser_json_robuste` et vérifier l'absence d'exception non gérée.
4. **Tests de non-blocage GUI & diagnostic** : exécuter `verifier_studio.py` et tester le lancement GUI/CLI sous Windows et Linux en vérifiant la désactivation des boutons pendant l'exécution asynchrone.