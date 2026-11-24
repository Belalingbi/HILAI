"""
test_registre_et_capacites.py — Tests de l'exécution et de la normalisation des 9 capacités du registre.
"""

import pytest
from registre_studio import CAPACITES_ENREGISTREES, executer_capacite, verifier_disponibilite_capacites
from studio_lanceur import _construire_kwargs_capacite


class TestRegistreCapacites:
    def test_toutes_capacites_disponibles(self):
        dispo = verifier_disponibilite_capacites()
        assert len(dispo) == 9
        for cle, info in dispo.items():
            assert info["disponible"] is True, f"Capacité '{cle}' indisponible : {info.get('erreur')}"

    def test_execution_capacite_atelier(self):
        kwargs = _construire_kwargs_capacite("atelier", "Test atelier", "recherche_connaissance_conseil", "", "", "")
        res = executer_capacite("atelier", **kwargs)
        assert "titre" in res
        assert "resume" in res
        assert "points_validation" in res

    def test_execution_capacite_site_web(self):
        kwargs = _construire_kwargs_capacite("site_web", "Site vitrine HILAI", "", "", "", "")
        res = executer_capacite("site_web", **kwargs)
        assert "titre" in res
        assert "HTML" in res["contenu_principal"] or "index_html" in str(res["donnee_brute"])

    def test_execution_capacite_code(self):
        kwargs = _construire_kwargs_capacite("code", "Calculateur de hash sha256", "", "", "", "")
        res = executer_capacite("code", **kwargs)
        assert "titre" in res
        assert "code" in res["donnee_brute"]

    def test_execution_capacite_maths(self):
        kwargs = _construire_kwargs_capacite("maths_geometrie", "5 * 6 + 10", "", "", "auto", "")
        res = executer_capacite("maths_geometrie", **kwargs)
        assert "titre" in res
        assert "40" in res["contenu_principal"] or res["donnee_brute"].get("resultat_exact") == "40"

    def test_execution_capacite_marketing(self):
        kwargs = _construire_kwargs_capacite("marketing_bi", "Campagne SEO internationale", "", "", "seo", "")
        res = executer_capacite("marketing_bi", **kwargs)
        assert "titre" in res
        assert "recommandations_actionnables" in res["donnee_brute"]

    def test_rejet_capacite_inconnue(self):
        with pytest.raises(ValueError):
            executer_capacite("capacite_inexistante")
