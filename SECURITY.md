# Politique de Cybersécurité & Durcissement — HILAI

> **Projet** : HILAI — Studio IA Modulaire « Human-in-the-Loop »  
> **Auteur** : Belalingbi Steve (CyberAnonymat Project)  
> **Contact Sécurité** : `belalingbi@gmail.com` / `cyberanaonymat@gmail.com`  

---

## 1. Engagement de Sécurité

La sécurité, la confidentialité des données et la souveraineté décisionnelle sont les piliers fondamentaux de l'architecture **HILAI**. Contrairement aux agents IA conventionnels qui effectuent des actions autonomes incontrôlées, HILAI applique le principe de **Zéro Action Non Validée** :

- **Aucun envoi de message ou mail** sans accord humain explicite (`confirme_steve is True`).
- **Aucune écriture disque de livrable final** sans validation préalable dans `sorties_a_valider/`.
- **Aucune modification de mémoire** silencieuse ou non tracée.
- **Aucun appel système ou commande externe** sans confinement strict et sans confirmation.

---

## 2. Matrice des Menaces & Contre-Mesures de Durcissement

| Vecteur d'Attaque | Risque Potentiel | Contre-Mesure Implémentée dans HILAI |
| :--- | :--- | :--- |
| **Prompt Injection** | Tentative de forcer l'IA à ignorer la validation ou exfiltrer des données | **Garde-fou déterministe en code** (`confirme_steve is True`). Détection par regex d'évasion, encapsulation dans `<untrusted_input>` et neutralisation automatique par `securite_garde_fous.py`. |
| **Path Traversal** | Écriture ou lecture de fichiers arbitraires hors du dossier autorisé (`../../etc/passwd`) | Résolution canonique `.resolve()`, vérification stricte de parenté via `valider_chemin_confine()`, assainissement des noms de fichiers (`assainir_nom_fichier`) et rejet des caractères nuls. |
| **Command Injection** | Exécution de commandes arbitraires via sous-processus | **Interdiction absolue de `shell=True`**. Arguments passés sous forme de liste `list[str]`, filtrage des métalangages shell (`;`, `\|`, `` ` ``, `$`), validation contre liste blanche (`valider_commande_securisee`) et timeout d'exécution. |
| **Exposition de Secrets** | Fuite de clés API (`AIza...`, jetons, mots de passe) dans les logs ou le journal | Masquage systématique par regex (`masquer_secrets`) de toutes les clés API, jetons JWT et mots de passe avant journalisation ou affichage. |
| **Exécution Arbitraire de Code (Eval)** | Exécution de code malveillant via des équations piégées (`eval()`) | **Bannissement de `eval()`**. Évaluation arithmétique déterministe via l'arbre syntaxique abstrait (`ast.parse`) et limitation stricte de complexité (anti-déni de service calculatoire). |
| **Injection SQL** | Injection de requêtes malveillantes dans les exports de bases de données | Validation stricte des identifiants (`valider_identifiant_sql`) et utilisation systématique de requêtes paramétrées SQLite (`?`). |
| **Empoisonnement de Mémoire** | Altération malveillante des règles et des leçons apprises | Vérification du schéma (`verifier_integrite_memoire`) et sauvegardes snapshot horodatées automatiques (`sauvegarder_snapshot_studio`). |

---

## 3. Signalement de Vulnérabilité (Coordinated Disclosure)

Si vous découvrez une faille de sécurité ou un moyen de contourner les garde-fous de HILAI :

1. **Ne pas ouvrir d'Issue publique sur GitHub**.
2. Envoyez immédiatement un rapport détaillé par courriel chiffré à `belalingbi@gmail.com` ou `cyberanaonymat@gmail.com`.
3. Indiquez la méthodologie de reproduction (PoC), l'impact estimé et vos suggestions de remédiation.
4. Une réponse vous sera apportée sous 48 heures ouvrées.
