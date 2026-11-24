import argparse
import json
import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

from connecteurs_et_sauvegarde import sauvegarder_snapshot_studio
from fiabilite_studio import lire_aperçu_sortie_securise
from registre_studio import (
    CAPACITES_ENREGISTREES,
    executer_capacite,
)
from studio_coeur import (
    ATELIERS,
    enregistrer_brouillon_code_valide,
    enregistrer_brouillon_web_valide,
    enregistrer_fiche_video_validee,
    enregistrer_validation_et_sortie,
    generer_fichier_binaire,
    lire_historique_journaux,
    lire_journal_jour,
    lister_sorties_validees,
)
from verifier_studio import verifier_tout


def _construire_kwargs_capacite(
    capacite: str,
    demande: str,
    atelier_slug: str,
    photo_ou_cible: str,
    domaine_ou_canal: str,
    format_com: str,
) -> dict:
    if capacite == "atelier":
        return {"atelier_cle": atelier_slug, "demande_steve": demande}
    if capacite == "site_web":
        return {"demande_steve": demande}
    if capacite == "code":
        return {"demande_steve": demande}
    if capacite == "video_photo":
        return {"photo_source": photo_ou_cible or "photo_source.jpg", "demande_steve": demande}
    if capacite == "reconnaissance_photo":
        return {
            "chemin_photo_str": photo_ou_cible or "photo_source.jpg",
            "question_complementaire": demande,
        }
    if capacite == "reconnaissance_chanson":
        return {"indices_ou_fichier": demande or photo_ou_cible}
    if capacite == "maths_geometrie":
        return {"enonce_steve": demande, "domaine": domaine_ou_canal or "auto"}
    if capacite == "communication":
        return {
            "canal": domaine_ou_canal or "gmail",
            "format_sortie": format_com or "mail",
            "intention_steve": demande,
            "destinataire_ou_cible": photo_ou_cible,
        }
    if capacite == "marketing_bi":
        return {
            "domaine": domaine_ou_canal or "seo",
            "objectif_steve": demande,
            "contexte_ou_donnees": photo_ou_cible,
        }
    raise ValueError(f"Capacité non gérée : {capacite}")


def _enregistrer_resultat_normalise(
    resultat_norm: dict,
    atelier_slug: str,
    demande: str,
    decision: str,
    justification: str,
    valider_sortie: bool,
) -> list[str]:
    messages: list[str] = []
    capacite = resultat_norm.get("capacite", "atelier")
    brut = resultat_norm.get("donnee_brute", {})
    chemin_specifique = None

    if capacite == "site_web" and valider_sortie:
        chemin_specifique = enregistrer_brouillon_web_valide(brut, True)
        messages.append(f"Brouillon web enregistré : {chemin_specifique}")
    elif capacite == "code" and valider_sortie:
        chemin_specifique = enregistrer_brouillon_code_valide(brut, True)
        messages.append(f"Module code enregistré : {chemin_specifique}")
    elif capacite == "video_photo" and valider_sortie:
        chemin_specifique = enregistrer_fiche_video_validee(brut, True)
        messages.append(f"Fiche vidéo enregistrée : {chemin_specifique}")
    elif capacite == "reconnaissance_photo" and valider_sortie:
        from reconnaissance_photo_chanson import enregistrer_reconnaissance_validee
        chemin_specifique = enregistrer_reconnaissance_validee(brut, "photo", True)
        messages.append(f"Reconnaissance photo enregistrée : {chemin_specifique}")
    elif capacite == "reconnaissance_chanson" and valider_sortie:
        from reconnaissance_photo_chanson import enregistrer_reconnaissance_validee
        chemin_specifique = enregistrer_reconnaissance_validee(brut, "chanson", True)
        messages.append(f"Reconnaissance chanson enregistrée : {chemin_specifique}")
    elif capacite == "maths_geometrie" and valider_sortie:
        from mathematiques_geometrie import enregistrer_resolution_validee
        chemin_specifique = enregistrer_resolution_validee(brut, True)
        messages.append(f"Résolution maths/géométrie enregistrée : {chemin_specifique}")
    elif capacite == "communication" and valider_sortie:
        from canaux_messageries_sociaux import enregistrer_brouillon_communication
        chemin_specifique = enregistrer_brouillon_communication(brut, True)
        messages.append(f"Brouillon communication enregistré : {chemin_specifique}")
    elif capacite == "marketing_bi" and valider_sortie:
        from marketing_seo_ads_bi import enregistrer_dossier_marketing_valide
        chemin_specifique = enregistrer_dossier_marketing_valide(brut, True)
        messages.append(f"Dossier marketing/BI enregistré : {chemin_specifique}")

    # Traçabilité obligatoire dans le journal quotidien & mémoire multi-jours
    dossier_journal = {
        "titre": resultat_norm.get("titre", f"Proposition — {capacite}"),
        "avis_ia": resultat_norm.get("resume", ""),
        "proposition_detaillee": (
            f"Fichier créé : {chemin_specifique}\n\n" + str(resultat_norm.get("contenu_principal", ""))
            if chemin_specifique else str(resultat_norm.get("contenu_principal", ""))
        ),
    }
    journal_nom, etat_sortie = enregistrer_validation_et_sortie(
        atelier_cle=atelier_slug if capacite == "atelier" else capacite,
        demande_steve=demande,
        dossier=dossier_journal,
        decision_steve=decision,
        justification_steve=justification,
        valider_dans_sorties=(valider_sortie and capacite == "atelier"),
    )
    messages.append(f"Journal quotidien : {journal_nom}")
    if capacite == "atelier":
        messages.append(etat_sortie)
    elif chemin_specifique:
        messages.append(f"Statut fichier : {chemin_specifique}")

    return messages


def executer_cli() -> None:
    from verifier_studio import afficher_rapport

    print("\n=== STUDIO IA MODULAIRE — CLI FINAL (WINDOWS / LINUX) ===")
    cles = list(CAPACITES_ENREGISTREES.keys())
    for idx, cle in enumerate(cles, start=1):
        print(f"  {idx}. {CAPACITES_ENREGISTREES[cle]['label']} ({cle})")
    print(f"  {len(cles) + 1}. Relire journal & sorties validées")
    print(f"  {len(cles) + 2}. Lancer le diagnostic local")

    choix_raw = input(f"Choix [1-{len(cles) + 2}, défaut=1] : ").strip()
    try:
        choix = int(choix_raw) if choix_raw else 1
    except ValueError:
        choix = 1

    if choix == len(cles) + 1:
        print("\n--- JOURNAL DU JOUR ---")
        print(lire_journal_jour())
        print("\n--- SORTIES DANS sorties_a_valider/ ---")
        for p in lister_sorties_validees():
            print(f"  - {p}")
        return

    if choix == len(cles) + 2:
        afficher_rapport(verifier_tout())
        return

    capacite = cles[choix - 1] if 1 <= choix <= len(cles) else "atelier"
    atelier_slug = "recherche_connaissance_conseil"
    if capacite == "atelier":
        for k, (_, lib) in ATELIERS.items():
            print(f"    {k}. {lib}")
        sel_at = input("Atelier [1-4, défaut=2] : ").strip()
        atelier_slug = ATELIERS.get(sel_at, ATELIERS["2"])[0]

    photo_ou_cible = ""
    if capacite in {"video_photo", "reconnaissance_photo", "communication", "marketing_bi"}:
        photo_ou_cible = input("Photo source / cible / contexte (optionnel) : ").strip()

    domaine_ou_canal = ""
    if capacite in {"maths_geometrie", "communication", "marketing_bi"}:
        domaine_ou_canal = input(
            "Domaine ou canal (ex. seo, google_ads, power_bi, gmail, telegram, auto) : "
        ).strip()

    format_com = "mail"
    if capacite == "communication":
        format_com = input("Format communication [mail / message / vocal, défaut=mail] : ").strip() or "mail"

    demande = input("Steve, quelle est ta demande ou instruction ? ").strip()
    if not demande and not photo_ou_cible:
        print("Entrée vide : opération annulée.")
        return

    print("Préparation en cours...")
    kwargs = _construire_kwargs_capacite(
        capacite=capacite,
        demande=demande,
        atelier_slug=atelier_slug,
        photo_ou_cible=photo_ou_cible,
        domaine_ou_canal=domaine_ou_canal,
        format_com=format_com,
    )
    res_norm = executer_capacite(capacite, **kwargs)

    print(f"\n=== {res_norm['titre']} ===")
    print(f"Résumé : {res_norm['resume']}\n")
    print(res_norm["contenu_principal"])
    print("\nPoints de validation suggérés :")
    for pt in res_norm["points_validation"]:
        print(f"  * {pt}")

    decision = input("\nSteve, quelle décision retiens-tu ? ").strip()
    justification = input("Justification (optionnelle) : ").strip()
    conf = input("Valider et enregistrer dans 'sorties_a_valider/' (oui/non) ? ").strip().lower()
    valider = conf in {"oui", "o", "yes", "y"}

    msgs = _enregistrer_resultat_normalise(
        resultat_norm=res_norm,
        atelier_slug=atelier_slug,
        demande=demande,
        decision=decision,
        justification=justification,
        valider_sortie=valider,
    )
    for m in msgs:
        print(f"  -> {m}")


class ApplicationStudioGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Studio IA Modulaire — Belalingbi Steve (CLI & GUI)")
        self.root.geometry("980x840")

        self.dernier_resultat_norm: dict | None = None
        self.dernier_atelier_slug: str = "recherche_connaissance_conseil"
        self.derniere_demande: str = ""
        self.chemins_sorties: list[Path] = []
        self.occupe = False
        self.boutons_action: list[ttk.Button] = []

        self.var_statut = tk.StringVar(
            value="Prêt — L'IA prépare et conseille, Steve décide et valide."
        )

        onglets = ttk.Notebook(root)
        onglets.pack(fill="both", expand=True, padx=10, pady=10)

        self.onglet_principal = ttk.Frame(onglets, padding=12)
        self.onglet_relecture = ttk.Frame(onglets, padding=12)
        onglets.add(self.onglet_principal, text="Studio & Validation")
        onglets.add(self.onglet_relecture, text="Relecture, Snapshot & Diagnostic")

        self._construire_onglet_principal(self.onglet_principal)
        self._construire_onglet_relecture(self.onglet_relecture)

        barre = ttk.Frame(root, padding=(12, 4))
        barre.pack(fill="x")
        ttk.Label(barre, textvariable=self.var_statut).pack(side="left")

    def _construire_onglet_principal(self, parent: ttk.Frame) -> None:
        ligne_cap = ttk.Frame(parent)
        ligne_cap.pack(fill="x", pady=(0, 6))
        ttk.Label(ligne_cap, text="Capacité :").pack(side="left", padx=(0, 6))

        self.labels_to_cap = {
            f"{meta['label']} [{cle}]": cle for cle, meta in CAPACITES_ENREGISTREES.items()
        }
        self.combo_capacite = ttk.Combobox(
            ligne_cap, values=list(self.labels_to_cap.keys()), state="readonly", width=65
        )
        self.combo_capacite.current(0)
        self.combo_capacite.pack(side="left", fill="x", expand=True)

        ligne_at = ttk.Frame(parent)
        ligne_at.pack(fill="x", pady=(0, 6))
        ttk.Label(ligne_at, text="Atelier (si mode atelier) :").pack(side="left", padx=(0, 6))
        self.libelles_to_slug = {lib: slug for _, (slug, lib) in ATELIERS.items()}
        self.combo_atelier = ttk.Combobox(
            ligne_at, values=list(self.libelles_to_slug.keys()), state="readonly", width=65
        )
        self.combo_atelier.current(1)
        self.combo_atelier.pack(side="left", fill="x", expand=True)

        ligne_opts = ttk.Frame(parent)
        ligne_opts.pack(fill="x", pady=(0, 6))
        ttk.Label(ligne_opts, text="Photo / Cible / Contexte :").pack(side="left", padx=(0, 4))
        self.entree_cible = ttk.Entry(ligne_opts, width=28)
        self.entree_cible.pack(side="left", padx=(0, 10))

        ttk.Label(ligne_opts, text="Domaine / Canal :").pack(side="left", padx=(0, 4))
        self.entree_domaine = ttk.Entry(ligne_opts, width=18)
        self.entree_domaine.pack(side="left", padx=(0, 10))

        ttk.Label(ligne_opts, text="Format com :").pack(side="left", padx=(0, 4))
        self.combo_format_com = ttk.Combobox(
            ligne_opts, values=["mail", "message", "vocal"], state="readonly", width=9
        )
        self.combo_format_com.current(0)
        self.combo_format_com.pack(side="left")

        ttk.Label(parent, text="Ta demande / énoncé / instruction :").pack(anchor="w")
        self.txt_demande = scrolledtext.ScrolledText(parent, height=4, wrap="word")
        self.txt_demande.pack(fill="x", pady=(3, 6))

        self.btn_preparer = ttk.Button(
            parent, text="Préparer le brouillon", command=self.lancer_preparation_async
        )
        self.btn_preparer.pack(anchor="w", pady=(0, 6))
        self.boutons_action.append(self.btn_preparer)

        ttk.Label(parent, text="Proposition préparée (en attente de ta validation) :").pack(anchor="w")
        self.txt_resultat = scrolledtext.ScrolledText(parent, height=13, wrap="word")
        self.txt_resultat.pack(fill="both", expand=True, pady=(3, 8))

        ttk.Label(parent, text="Ta décision :").pack(anchor="w")
        self.entree_decision = ttk.Entry(parent)
        self.entree_decision.pack(fill="x", pady=(2, 5))

        ttk.Label(parent, text="Justification / note mémoire (optionnel) :").pack(anchor="w")
        self.entree_justification = ttk.Entry(parent)
        self.entree_justification.pack(fill="x", pady=(2, 6))

        ligne_val = ttk.Frame(parent)
        ligne_val.pack(fill="x", pady=(0, 4))

        self.var_valider_sortie = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            ligne_val,
            text="Je valide explicitement l'enregistrement dans 'sorties_a_valider/'",
            variable=self.var_valider_sortie,
        ).pack(side="left", padx=(0, 14))

        ttk.Label(ligne_val, text="Export binaire :").pack(side="left", padx=(0, 4))
        self.combo_binaire = ttk.Combobox(
            ligne_val, values=["aucun", "xlsx", "pptx", "pdf", "db"], state="readonly", width=8
        )
        self.combo_binaire.current(0)
        self.combo_binaire.pack(side="left")

        self.btn_enregistrer = ttk.Button(
            parent,
            text="Enregistrer ma décision et le journal",
            command=self.enregistrer_decision,
        )
        self.btn_enregistrer.pack(anchor="w", pady=(4, 0))
        self.boutons_action.append(self.btn_enregistrer)

    def _construire_onglet_relecture(self, parent: ttk.Frame) -> None:
        barre_top = ttk.Frame(parent)
        barre_top.pack(fill="x", pady=(0, 8))

        btn_act = ttk.Button(barre_top, text="Actualiser", command=self.actualiser_relecture)
        btn_act.pack(side="left", padx=(0, 8))
        self.boutons_action.append(btn_act)

        btn_diag = ttk.Button(barre_top, text="Diagnostic local", command=self.afficher_diagnostic)
        btn_diag.pack(side="left", padx=(0, 8))
        self.boutons_action.append(btn_diag)

        btn_snap = ttk.Button(barre_top, text="Snapshot studio", command=self.faire_snapshot)
        btn_snap.pack(side="left")
        self.boutons_action.append(btn_snap)

        ttk.Label(parent, text="Fichiers dans 'sorties_a_valider/' (clique pour aperçu) :").pack(
            anchor="w"
        )
        self.liste_sorties = tk.Listbox(parent, height=6, exportselection=False)
        self.liste_sorties.pack(fill="x", pady=(3, 8))
        self.liste_sorties.bind("<<ListboxSelect>>", self.apercevoir_sortie_selectionnee)

        ttk.Label(parent, text="Aperçu du fichier sélectionné / journaux & rapports :").pack(anchor="w")
        self.txt_relecture = scrolledtext.ScrolledText(parent, height=18, wrap="word")
        self.txt_relecture.pack(fill="both", expand=True, pady=(3, 0))
        self.actualiser_relecture()

    def _definir_etat(self, actif: bool, msg: str) -> None:
        self.occupe = actif
        self.var_statut.set(msg)
        etat_btn = ["disabled"] if actif else ["!disabled"]
        for btn in self.boutons_action:
            btn.state(etat_btn)

    def lancer_preparation_async(self) -> None:
        if self.occupe:
            return
        demande = self.txt_demande.get("1.0", "end").strip()
        cible = self.entree_cible.get().strip()
        if not demande and not cible:
            messagebox.showwarning("Champ vide", "Saisis une demande ou une cible/photo.")
            return

        capacite = self.labels_to_cap.get(self.combo_capacite.get(), "atelier")
        atelier_slug = self.libelles_to_slug.get(
            self.combo_atelier.get(), "recherche_connaissance_conseil"
        )
        domaine = self.entree_domaine.get().strip()
        fmt_com = self.combo_format_com.get()

        self._definir_etat(True, f"En préparation ({capacite})... merci de patienter.")

        def _travail() -> None:
            try:
                kwargs = _construire_kwargs_capacite(
                    capacite=capacite,
                    demande=demande,
                    atelier_slug=atelier_slug,
                    photo_ou_cible=cible,
                    domaine_ou_canal=domaine,
                    format_com=fmt_com,
                )
                res_norm = executer_capacite(capacite, **kwargs)
                self.root.after(0, self._afficher_resultat, atelier_slug, demande, res_norm)
            except Exception as exc:
                self.root.after(0, self._afficher_erreur, str(exc))

        threading.Thread(target=_travail, daemon=True).start()

    def _afficher_resultat(self, atelier_slug: str, demande: str, res_norm: dict) -> None:
        self.dernier_atelier_slug = atelier_slug
        self.derniere_demande = demande
        self.dernier_resultat_norm = res_norm

        pts = "\n".join(f"- {p}" for p in res_norm.get("points_validation", []))
        rendu = (
            f"Titre : {res_norm.get('titre', '')}\n"
            f"Capacité : {res_norm.get('capacite', '')}\n\n"
            f"Résumé :\n{res_norm.get('resume', '')}\n\n"
            f"Contenu :\n{res_norm.get('contenu_principal', '')}\n\n"
            f"Points de validation suggérés :\n{pts}"
        )
        self.txt_resultat.delete("1.0", "end")
        self.txt_resultat.insert("1.0", rendu)
        self._definir_etat(False, "Brouillon prêt — en attente de ta décision et validation.")

    def _afficher_erreur(self, msg: str) -> None:
        self._definir_etat(False, "Erreur lors de la préparation.")
        messagebox.showerror("Erreur", msg)

    def enregistrer_decision(self) -> None:
        if self.occupe:
            return
        if not self.dernier_resultat_norm:
            messagebox.showwarning("Aucune proposition", "Prépare d'abord un brouillon.")
            return

        decision = self.entree_decision.get().strip()
        justification = self.entree_justification.get().strip()
        valider_sortie = self.var_valider_sortie.get()
        fmt_bin = self.combo_binaire.get()

        self._definir_etat(True, "Enregistrement en cours...")
        try:
            messages = _enregistrer_resultat_normalise(
                resultat_norm=self.dernier_resultat_norm,
                atelier_slug=self.dernier_atelier_slug,
                demande=self.derniere_demande,
                decision=decision,
                justification=justification,
                valider_sortie=valider_sortie,
            )

            if fmt_bin in {"xlsx", "pptx", "pdf", "db"}:
                conf = messagebox.askyesno(
                    "Confirmation explicite",
                    f"Steve, confirmes-tu la création du fichier .{fmt_bin} dans 'sorties_a_valider/' ?",
                )
                if conf:
                    try:
                        cree = generer_fichier_binaire(
                            fmt_bin,
                            self.dernier_resultat_norm.get("titre", "Sortie_Studio"),
                            self.dernier_resultat_norm.get("contenu_principal", ""),
                            True,
                        )
                        messages.append(f"Fichier binaire créé : {cree}")
                    except Exception as exc:
                        messages.append(f"Erreur binaire : {exc}")

            self.var_valider_sortie.set(False)
            self.combo_binaire.current(0)
            self.actualiser_relecture()
            messagebox.showinfo("Enregistrement terminé", "\n".join(messages))
        except Exception as exc:
            messagebox.showerror("Erreur d'enregistrement", str(exc))
        finally:
            self._definir_etat(False, "Prêt — décision traitée.")

    def actualiser_relecture(self) -> None:
        self.liste_sorties.delete(0, "end")
        self.chemins_sorties = lister_sorties_validees()
        for p in self.chemins_sorties:
            self.liste_sorties.insert("end", str(p))

        texte = (
            "=== JOURNAL DU JOUR ===\n"
            + lire_journal_jour()
            + "\n\n=== HISTORIQUE RÉCENT ===\n"
            + lire_historique_journaux()
        )
        self.txt_relecture.delete("1.0", "end")
        self.txt_relecture.insert("1.0", texte)

    def apercevoir_sortie_selectionnee(self, _event: tk.Event | None = None) -> None:
        selection = self.liste_sorties.curselection()
        if not selection:
            return
        index = selection[0]
        if index < 0 or index >= len(self.chemins_sorties):
            return
        chemin = self.chemins_sorties[index]
        try:
            apercu = lire_aperçu_sortie_securise(chemin)
        except Exception as exc:
            apercu = f"Impossible d'afficher l'aperçu : {exc}"

        self.txt_relecture.delete("1.0", "end")
        self.txt_relecture.insert("1.0", f"=== APERÇU : {chemin} ===\n\n{apercu}")

    def afficher_diagnostic(self) -> None:
        if self.occupe:
            return
        self._definir_etat(True, "Diagnostic en cours...")
        try:
            rapport = verifier_tout()
            self.txt_relecture.delete("1.0", "end")
            self.txt_relecture.insert("1.0", json.dumps(rapport, indent=2, ensure_ascii=False))
        finally:
            self._definir_etat(False, "Diagnostic affiché.")

    def faire_snapshot(self) -> None:
        if self.occupe:
            return
        ok = messagebox.askyesno(
            "Sauvegarde snapshot",
            "Steve, confirmes-tu la création d'un snapshot horodaté dans 'sauvegardes_studio/' ?",
        )
        if not ok:
            return
        self._definir_etat(True, "Création du snapshot...")
        try:
            cible = sauvegarder_snapshot_studio(True)
            self.actualiser_relecture()
            messagebox.showinfo("Snapshot créé", f"Dossier : {cible}")
        finally:
            self._definir_etat(False, "Snapshot terminé.")


def executer_gui() -> None:
    root = tk.Tk()
    ApplicationStudioGUI(root)
    root.mainloop()


def executer_demo_automatique() -> None:
    """Exécute un tour complet de validation automatique sans prompt bloquant."""
    print("\n========================================================")
    print("      DÉMONSTRATION AUTOMATISÉE DU STUDIO IA HILAI       ")
    print("========================================================")
    for cap in ["atelier", "site_web", "code", "maths_geometrie", "marketing_bi"]:
        kwargs = _construire_kwargs_capacite(
            capacite=cap,
            demande="Démonstration automatique des capacités HILAI",
            atelier_slug="recherche_connaissance_conseil",
            photo_ou_cible="contexte_demo",
            domaine_ou_canal="seo" if cap == "marketing_bi" else "2+3*4",
            format_com="mail",
        )
        res = executer_capacite(cap, **kwargs)
        print(f"[OK] Capacité '{cap:<16}' -> {res['titre'][:50]}")

    print("\n[+] Test de traçabilité et validation Human-in-the-Loop...")
    msgs = _enregistrer_resultat_normalise(
        resultat_norm=res,
        atelier_slug="recherche_connaissance_conseil",
        demande="Test validation démo HILAI",
        decision="Validation explicite en mode démonstration",
        justification="Vérification de l'intégrité de la boucle Human-in-the-Loop",
        valider_sortie=True,
    )
    for m in msgs:
        print(f"  -> {m}")
    print("\n[+] Démonstration achevée avec succès. Système 100% prêt.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Studio IA Modulaire HILAI — Belalingbi Steve")
    parser.add_argument("--cli", action="store_true", help="Forcer le mode ligne de commande")
    parser.add_argument("--diag", action="store_true", help="Afficher le rapport de diagnostic de sécurité")
    parser.add_argument("--demo", action="store_true", help="Lancer un cycle de démonstration automatisé")
    args = parser.parse_args()

    if args.diag:
        from verifier_studio import afficher_rapport
        afficher_rapport(verifier_tout())
        return

    if args.demo:
        executer_demo_automatique()
        return

    sans_gui = (
        sys.platform.startswith("linux")
        and not os.environ.get("DISPLAY")
        and not os.environ.get("WAYLAND_DISPLAY")
    )
    if args.cli or sans_gui:
        executer_cli()
    else:
        executer_gui()


if __name__ == "__main__":
    main()