# TRD — Studio IA Modulaire (CLI & GUI) v2.0

## 1. Architecture générale
Le système repose sur une architecture **hybride (Local / Cloud)** exposant une double interface :
- **CLI** : exécution en ligne de commande, automatisation scriptée, inspection et déclenchement des mêmes pipelines et règles de validation[cite: 7, 12].
- **GUI** : interface graphique de bureau organisée autour de deux vues principales (*Atelier & Validation* ; *Relecture, Snapshot & Diagnostic*) et d'une grille à trois colonnes sur l'onglet principal[cite: 7, 12].

## 2. Composants fonctionnels et modules techniques

### 2.1 Module Configuration & Orchestration d'Ateliers
- Chargement des profils de **Capacité** et d'**Atelier** (ex. *Atelier standard (1 à 4) [atelier]*, *Recherche, Connaissance & Conseil*)[cite: 7, 12].
- Normalisation des métadonnées de contexte : `target_context` (*Photo / Cible / Context*), `domain_channel` (*Domaine / Canal*) et `com_format` (*Format com*, ex. `mail`)[cite: 7, 12].
- Gestion de la liste des **Projets récents** (métadonnées, miniature/aperçu, horodatage, chemin).

### 2.2 Module Ingestion Multimodale (Fichiers, Audio, Vision)
- **Gestionnaire de pièces jointes** : file d'attente supportant l'ajout, la prévisualisation/lecture et la suppression d'assets locaux (vidéo `.mp4`, audio `.mp3`, image `.png`, etc.) avec vérification d'intégrité et taille[cite: 12].
- **Pipeline Vision / Caméra** : capture ou flux vidéo/image local soumis à une passe d'analyse optionnelle (*Activer Caméra / Analyse*)[cite: 12].
- **Pipeline Audio / Note Vocale** : enregistrement micro (*Enregistrer Note Vocale*), stockage temporaire et transcription/injection dans le contexte de demande[cite: 12].

### 2.3 Moteur de Préparation de Brouillon (IA)
- Déclenché explicitement par l'action **Préparer le brouillon**[cite: 7, 12].
- Agrège l'instruction textuelle, les métadonnées d'atelier, les références de fichiers et les sorties audio/vision pour produire une **proposition structurée** en état `PENDING_VALIDATION`[cite: 7, 12].
- N'écrit pas dans `sorties_a_valider/` tant que le sas de validation humaine n'est pas franchi[cite: 7, 12].

### 2.4 Sas de Validation Humaine, Persistance et Export
- Champs requis/supportés :
  - `decision` (*Ta décision*)[cite: 7, 12]
  - `justification` (*Justification / note mémoire (optionnel)*)[cite: 7, 12]
  - `binary_export` (*Export binaire*, valeur par défaut `aucun`)[cite: 7, 12]
  - `explicit_validation_sorties` (booléen contrôlé par la case *Je valide explicitement l'enregistrement dans 'sorties_a_valider/'*)[cite: 7, 12]
- **Règle métier critique** : l'enregistrement vers `sorties_a_valider/` et la génération d'un export binaire ou d'un projet final (*Valider & Exporter le projet final*) sont bloqués si `explicit_validation_sorties == false`[cite: 7, 12].
- **Journalisation** : écriture atomique d'une entrée de journal (horodatage, atelier, décision, justification, fichiers liés, statut d'export) lors de *Enregistrer ma décision et le journal* et mise à jour de *Logs & Événements*[cite: 7, 12].

### 2.5 Module Relecture, Snapshot, Diagnostic & Télémétrie
- **Relecture** : consultation filtrable des sorties validées dans `sorties_a_valider/` et de l'historique des décisions[cite: 7, 12].
- **Snapshot** : création et restauration d'instantanés d'état (configuration, brouillons, métadonnées de session)[cite: 7, 12].
- **Diagnostic & Statut Système** : surveillance des ressources locales (*GPU/Mem load*), vérification de la connectivité Local/Cloud et génération de rapports de diagnostic[cite: 12].

## 3. Structure des données et arborescence type
```text
studio-ia-modulaire/
├── cli/
├── gui/
├── ateliers/               # Définitions des capacités et ateliers
├── sorties_a_valider/      # Cible soumise à validation humaine explicite
├── snapshots/              # États sauvegardés pour relecture/restauration
├── logs/                   # Journaux d'événements et décisions humaines
└── config/                 # Paramètres hybrides (Local/Cloud) et profils