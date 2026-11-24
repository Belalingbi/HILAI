"""
test_fiabilite_et_human_in_the_loop.py — Tests des garde-fous de décision et de la fiabilité des sorties.
"""

import pytest
from pathlib import Path

from fiabilite_studio import exiger_confirmation_steve, parser_json_robuste
from studio_coeur import (
    enregistrer_brouillon_code_valide,
    enregistrer_brouillon_web_valide,
    enregistrer_fiche_video_validee,
    generer_fichier_binaire,
)


class TestGardeFousDecisionnels:
    def test_refus_si_non_confirme(self):
        with pytest.raises(PermissionError) as exc_info:
            exiger_confirmation_steve(False, "action_critique")
        assert "validation explicite de Belalingbi Steve requise" in str(exc_info.value)

    def test_refus_si_confirme_non_booleen_strict(self):
        # Sécurité : seule la valeur booléenne True stricte est admise
        with pytest.raises(PermissionError):
            exiger_confirmation_steve("oui", "action")  # type: ignore
        with pytest.raises(PermissionError):
            exiger_confirmation_steve(1, "action")  # type: ignore
        with pytest.raises(PermissionError):
            exiger_confirmation_steve(None, "action")  # type: ignore

    def test_autorisation_si_confirme_vrai(self):
        # Ne doit pas lever d'exception
        exiger_confirmation_steve(True, "action_autorisee")


class TestEcritureZeroSansValidation:
    def test_aucun_fichier_cree_sans_accord_web(self):
        dossier = {"index_html": "<h1>Test</h1>"}
        res = enregistrer_brouillon_web_valide(dossier, confirme_steve=False)
        assert res is None

    def test_aucun_fichier_cree_sans_accord_code(self):
        dossier = {"code": "print('hello')", "nom_fichier": "test_unitaire.py"}
        res = enregistrer_brouillon_code_valide(dossier, confirme_steve=False)
        assert res is None

    def test_aucun_fichier_cree_sans_accord_video(self):
        dossier = {"titre_sequence": "Video Test"}
        res = enregistrer_fiche_video_validee(dossier, confirme_steve=False)
        assert res is None

    def test_aucun_binaire_cree_sans_accord(self):
        res = generer_fichier_binaire("db", "Titre", "Contenu", confirme_steve=False)
        assert res is None


class TestParseurJsonRobuste:
    def test_parsing_json_simple(self):
        texte = '{"cle": "valeur", "nombre": 42}'
        res = parser_json_robuste(texte)
        assert res.get("cle") == "valeur"
        assert res.get("nombre") == 42

    def test_parsing_json_avec_bloc_markdown(self):
        texte = '```json\n{"statut": "succes"}\n```'
        res = parser_json_robuste(texte)
        assert res.get("statut") == "succes"

    def test_parsing_texte_brut_sans_crash(self):
        texte = "Ceci est une reponse texte sans JSON."
        res = parser_json_robuste(texte)
        assert res.get("texte_brut") == texte or "valeur" in res
