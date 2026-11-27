# PRD — Studio IA Modulaire (CLI & GUI) v2.0

## 1. Vision et objectif produit
**Studio IA Modulaire** est un environnement de travail hybride (CLI et interface graphique) conçu pour **Belalingbi Steve**. Le principe fondamental du produit est le contrôle humain strict (*Human-in-the-Loop*) : **l'IA prépare, analyse et conseille ; l'utilisateur décide, justifie et valide explicitement** avant toute persistance ou export final dans `sorties_a_valider/`.

La version **v2.0** unifie l'approche modulaire orientée *Ateliers* et *Validation* avec des capacités multimodales (vision/caméra, note vocale, pièces jointes médias) et un suivi d'exécution (aperçu des projets récents, journalisation des événements et statut système)[cite: 7, 12].

## 2. Utilisateur cible et cas d'usage principaux
- **Utilisateur principal** : Belalingbi Steve (opérateur / créateur / décideur)[cite: 7, 12].
- **Cas d'usage clés** :
  1. Structurer une demande selon une **Capacité** (ex. *Atelier standard (1 à 4) [atelier]*) et un **Atelier** spécialisé (ex. *Recherche, Connaissance & Conseil*) avec contexte cible, domaine/canal et format de communication (ex. *mail*)[cite: 7, 12].
  2. Enrichir une demande avec des **fichiers et attachements** (vidéo, audio, visuels, documents) ainsi que des **contrôles audio et vision** (capture/analyse caméra, enregistrement de note vocale).
  3. Générer une **proposition préparée** en attente de validation, sans action automatique irréversible[cite: 7, 12].
  4. Consigner une **décision humaine**, une **justification / note mémoire** (optionnelle), un **export binaire** (`aucun` ou format défini), et cocher la **validation explicite** pour enregistrer dans `sorties_a_valider/`[cite: 7, 12].
  5. Auditer l'activité via l'onglet **Relecture, Snapshot & Diagnostic**, les **Logs & Événements** et les **Projets récents**[cite: 7, 12].

## 3. Périmètre fonctionnel (Fonctionnalités clés)

### 3.1 Navigation et organisation de l'espace de travail
- Barre de titre dédiée (*Studio IA Modulaire — Belalingbi Steve (CLI & GUI) v2.0*) et accès aux options/paramètres[cite: 12].
- Deux onglets principaux :
  - **Atelier & Validation** : espace actif de préparation, d'enrichissement multimodal et de validation[cite: 7, 12].
  - **Relecture, Snapshot & Diagnostic** : consultation des sorties enregistrées, journaux, instantanés (*snapshots*) et diagnostic système[cite: 7, 12].

### 3.2 Configuration du studio & saisie de la demande
- Sélecteur de **Capacité** et d'**Atelier**[cite: 7, 12].
- Champs de cadrage : *Photo / Cible / Context*, *Domaine / Canal* et *Format com*[cite: 7, 12].
- Zone de saisie de la demande (*Ta demande / énoncé / instruction*) et bouton **Préparer le brouillon**[cite: 7, 12].
- Bandeau d'aperçu des **Projets récents** pour reprise rapide[cite: 12].

### 3.3 Entrées multimodales et gestion des fichiers
- **Fichiers & Attachements** : file d'attente interactive permettant d'ajouter des fichiers (`+ Ajouter Fichier / Attachement`), d'apercevoir/lire les médias (ex. `.mp4`, `.mp3`, `.png`) et de gérer la file[cite: 12].
- **Contrôles Audio & Vision** : actions *Activer Caméra / Analyse* et *Enregistrer Note Vocale* alimentant le contexte de préparation[cite: 12].

### 3.4 Proposition IA, Sas de Validation Humaine et Journalisation
- Zone **Proposition préparée (en attente de ta validation)** affichant le brouillon structuré produit par l'IA[cite: 7, 12].
- Bloc **Validation Humaine (Sas)** comprenant :
  - Champ **Ta décision**[cite: 7, 12].
  - Champ **Justification / note mémoire (optionnel)**[cite: 7, 12].
  - Sélecteur **Export binaire** (par défaut : `aucun`)[cite: 7, 12].
  - Case à cocher obligatoire pour l'enregistrement dans `sorties_a_valider/` (*Je valide explicitement l'enregistrement dans 'sorties_a_valider/'*)[cite: 7, 12].
  - Bouton **Enregistrer ma décision et le journal**[cite: 7, 12].
- Bloc **Statut Système & IA** : indication du mode d'exécution (ex. *Hybride (Local/Cloud)*), jauges de charge *GPU/Mem load* et action *Valider & Exporter le projet final*[cite: 12].
- Flux **Logs & Événements** : traçabilité des instructions, validations et réponses/événements du studio[cite: 12].

## 4. Exigences non fonctionnelles et garde-fous
- **Souveraineté et non-automatisation critique** : aucune écriture dans `sorties_a_valider/` ni export final sans validation humaine explicite[cite: 7, 12].
- **Ergonomie et lisibilité** : interface sombre contrastée, répartition claire en zones fonctionnelles (configuration/médias à gauche, demande/brouillon/logs au centre, validation/statut à droite) et compatibilité CLI/GUI[cite: 7, 12].
- **Traçabilité** : chaque décision humaine doit pouvoir être associée à un journal d'audit et une note mémoire[cite: 7, 12].

## 5. Critères de succès (KPIs)
- **100 %** des éléments enregistrés dans `sorties_a_valider/` résultent d'une validation explicite de l'utilisateur[cite: 7, 12].
- Réduction du temps de passage entre la saisie d'une demande multimodale, la préparation d'un brouillon et la prise de décision[cite: 7, 12].
- Accès instantané aux journaux, snapshots et diagnostics en cas d'anomalie ou de reprise de travail[cite: 7, 12].