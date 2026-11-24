# Guide de Contribution — HILAI

Merci pour votre intérêt à contribuer à **HILAI (Human-in-the-Loop Artificial Intelligence)** !

---

## 1. Philosophie du Projet

HILAI repose sur une règle éthique et technique inaltérable : **l'humain conserve le pouvoir décisionnel suprême**.
Toute contribution doit scrupuleusement respecter :
- Le durcissement cybersécurité (défense en profondeur).
- L'absence de commandes bloquantes ou non validées.
- La compatibilité multiplateforme (Windows & Linux).
- La compatibilité avec le **Mode Local Autonome** (zéro plantage en cas d'absence d'Internet ou de clé API).

---

## 2. Processus de Développement

1. **Forkez** le projet : [https://github.com/Belalingbi/HILAI](https://github.com/Belalingbi/HILAI)
2. Créez votre branche thématique : `git checkout -b feature/amelioration-securite`
3. Installez les dépendances de développement :
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
4. Exécutez les tests et l'audit de sécurité :
   ```bash
   pytest -v
   python verifier_studio.py
   ```
5. Validez que **100% des tests réussissent**.
6. Commitez vos modifications avec des messages clairs :
   ```bash
   git commit -m "feat(security): renforcement des filtres de commandes"
   ```
7. Poussez vers votre fork et ouvrez une **Pull Request**.

---

## 3. Lignes Rouges Inviolables

- **Interdiction de `eval()`** sur des entrées utilisateurs.
- **Interdiction de `shell=True`** dans les appels `subprocess`.
- **Aucune écriture hors de `sorties_a_valider/` ou `sauvegardes_studio/`**.
- **Aucun commit contenant des secrets réels ou clés API** (utilisez `.env.example`).
