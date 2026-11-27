"""
test_registre_et_capacites.py — Tests de l'exécution et de la normalisation de toutes les capacités v2.0 du registre.
"""

import pytest
from registre_studio import CAPACITES_ENREGISTREES, executer_capacite, verifier_disponibilite_capacites
from studio_lanceur import _construire_kwargs_capacite


class TestRegistreCapacites:
    def test_toutes_capacites_disponibles(self):
        dispo = verifier_disponibilite_capacites()
        assert len(dispo) == len(CAPACITES_ENREGISTREES)
        assert len(dispo) >= 14
        for cle, info in dispo.items():
            assert info["disponible"] is True, f"Capacité '{cle}' indisponible : {info.get('erreur')}"

    def test_execution_capacite_atelier(self):
        kwargs = _construire_kwargs_capacite("atelier", "Test atelier", "recherche_connaissance_conseil", "", "", "")
        res = executer_capacite("atelier", **kwargs)
        assert "titre" in res
        assert "resume" in res
        assert "points_validation" in res

    def test_execution_capacite_montage_video_autonome(self):
        kwargs = _construire_kwargs_capacite(
            "montage_video_autonome",
            "Monte une vidéo dynamique de 45s avec sous-titres",
            "", "", "", "",
            plateforme_montage="premiere_pro",
        )
        res = executer_capacite("montage_video_autonome", **kwargs)
        assert "timeline_tracks" in res["donnee_brute"]
        assert len(res["donnee_brute"]["timeline_tracks"]) >= 4

    def test_execution_capacite_generation_images_infinie(self):
        kwargs = _construire_kwargs_capacite("generation_images_infinie", "Ville cyber", "", "", "", "")
        res = executer_capacite("generation_images_infinie", **kwargs)
        assert res["donnee_brute"]["image_png_bytes"].startswith(b"\x89PNG\r\n\x1a\n")

    def test_execution_capacite_generation_videos_infinie(self):
        kwargs = _construire_kwargs_capacite("generation_videos_infinie", "Travelling futuriste", "", "", "", "")
        res = executer_capacite("generation_videos_infinie", **kwargs)
        assert len(res["donnee_brute"]["sequence_video"]["frames_png"]) >= 2

    def test_execution_capacite_conversation_multimodale(self):
        kwargs = _construire_kwargs_capacite("conversation_multimodale", "Analyse ce projet", "", "", "", "")
        res = executer_capacite("conversation_multimodale", **kwargs)
        assert "titre" in res
        assert "contenu_principal" in res

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
