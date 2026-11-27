# Politique de Cybersécurité & Durcissement — HILAI v2.0

> **Projet** : HILAI — Studio IA Modulaire « Human-in-the-Loop » v2.0  
> **Auteur** : Belalingbi Steve (CyberAnonymat Project)  
> **Contact Sécurité** : `belalingbi@gmail.com` / `cyberanaonymat@gmail.com`  

---

## 1. Engagement de Sécurité

La sécurité, la confidentialité des données et la souveraineté décisionnelle sont les piliers fondamentaux de l'architecture **HILAI**. Contrairement aux agents IA conventionnels qui effectuent des actions autonomes incontrôlées, HILAI applique le principe de **Zéro Action Non Validée** :

- **Aucun envoi de message ou mail** sans accord humain explicite (`confirme_steve is True`).
- **Aucune écriture disque de livrable final ou d'export montage** sans validation préalable dans `sorties_a_valider/`.
- **Aucune modification de mémoire ou de configuration critique** silencieuse ou non tracée.
- **Aucun appel système ou commande externe (FFmpeg, Python, etc.)** sans confinement strict, liste blanche et confirmation.
- **Contrôle matériel transparent** : la caméra et le microphone ne s'activent jamais sans action explicite de l'utilisateur et indicateur visuel permanent.

---

## 2. Matrice des Menaces & Contre-Mesures de Durcissement (v2.0)

| Vecteur d'Attaque | Risque Potentiel | Contre-Mesure Implémentée dans HILAI |
| :--- | :--- | :--- |
| **Prompt Injection & XML Breakout** | Tentative de forcer l'IA à ignorer la validation, exfiltrer des données ou fermer `</untrusted_input>` | **Garde-fou déterministe en code** (`confirme_steve is True`). Détection FR/EN par regex, neutralisation des balises `<untrusted_input>` et octets nuls, encapsulation XML étanche (`securite_garde_fous.py`). |
| **Path Traversal** | Écriture ou lecture de fichiers arbitraires hors du dossier autorisé (`../../etc/passwd`) | Résolution canonique `.resolve()`, vérification stricte de parenté via `valider_chemin_confine()`, assainissement des noms de fichiers (`assainir_nom_fichier`), écritures atomiques (`ecrire_fichier_atomique`). |
| **Pièces Jointes Piégées / Polyglottes** | Import d'un exécutable (`.exe`, `.bat`, `.ps1`) déguisé en image ou média | `valider_piece_jointe_securisee()` : liste noire d'exécutables, liste blanche multimodale, contrôle des **octets magiques** (PNG/JPEG/WAV/PDF/MZ/ELF), limite de taille configurable et empreinte SHA-256. |
| **Command Injection** | Exécution de commandes arbitraires via FFmpeg ou sous-processus | **Interdiction absolue de `shell=True`**. Arguments en `list[str]`, filtrage des métalangages shell (`;`, `\|`, `` ` ``, `$`, retours chariot), liste blanche (`valider_commande_securisee`) et timeout. |
| **XML / Script Injection (Montages)** | Injection XSS/XXE dans Premiere Pro XML / FCPXML ou exécution de code dans ExtendScript `.jsx` / DaVinci `.py` | Échappement XML strict (`echapper_xml_securise`) et encodage JSON sécurisé des littéraux (`assainir_chaine_script`) avant tout export. |
| **Exposition de Secrets** | Fuite de clés API (`AIza...`, `sk-...`, `ghp_`, `AKIA...`, JWT, clés privées PEM, URLs avec identifiants) | Masquage systématique par regex (`masquer_secrets`) avant journalisation, affichage ou sauvegarde ; exclusion stricte des secrets dans `config_studio.json`. |
| **Déni de Service (DoS) Flux Infini** | Saturation RAM ou disque par génération continue incontrôlée | `ControleurQuotaRessources` : tampon circulaire borné et quota disque strict par session ; validation humaine requise avant écriture disque définitive. |
| **Exécution Arbitraire de Code (Eval)** | Exécution de code malveillant via des équations piégées (`eval()`) | **Bannissement de `eval()`**. Analyseur arithmétique AST pur (`ast.parse`) avec plafonnement de complexité. |
| **Injection SQL** | Injection dans les exports de bases SQLite locales | Validation stricte des identifiants (`valider_identifiant_sql`) et requêtes paramétrées SQLite (`?`). |

---

## 3. Signalement de Vulnérabilité (Coordinated Disclosure)

Si vous découvrez une faille de sécurité ou un moyen de contourner les garde-fous de HILAI :

1. **Ne pas ouvrir d'Issue publique sur GitHub**.
2. Envoyez immédiatement un rapport détaillé par courriel chiffré à `belalingbi@gmail.com` ou `cyberanaonymat@gmail.com`.
3. Indiquez la méthodologie de reproduction (PoC), l'impact estimé et vos suggestions de remédiation.
4. Une réponse vous sera apportée sous 48 heures ouvrées.
