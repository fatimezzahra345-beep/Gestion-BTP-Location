"""modules/attachements.py — Attachements Multi-Engins | LocationBTP"""
import streamlit as st, pandas as pd, calendar as cal_mod
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import controller as ctrl
from modules.ui_helpers import (render_page_header, _sec, _info, _warn,
                                _div, PRIMARY, GREEN, RED, ORANGE, GRAY_400)

def render():
    render_page_header("📎", "Attachements",
        "Un attachement par client — pointage de tous les engins ensemble")


    _div()

    tab_liste, tab_creer = st.tabs(["Liste des Attachements", "Créer un Attachement"])

    # ── LISTE ─────────────────────────────────────────────────────────────────
    with tab_liste:
        try:
            atts = ctrl.get_all_attachements()
        except Exception:
            atts = []
        if not atts:
            _info("Aucun attachement. Créez-en un via l'onglet 'Créer un Attachement'.")
        df_a = pd.DataFrame([{
                "N°":         a.get("numero",""),
                "Commande":   a.get("commande_numero","—"),
                "Client":     a.get("client",""),
                "Engins":     a.get("engin_nom",""),
                "Mois/Année": f"{a.get('mois',0):02d}/{a.get('annee',0)}",
                "Jours":      float(a.get("nb_jours_travailles", 0) or 0),
            } for a in atts])
        st.dataframe(df_a, width="stretch", hide_index=True, height=300)
        if atts:
            _div()
            att_map = {a["numero"]: a["id"] for a in atts}
            sel_att = st.selectbox("Télécharger PDF", ["—"]+list(att_map.keys()),
                                    key="sel_att")
            if sel_att != "—":
                att_d = ctrl.get_attachement_by_id(att_map[sel_att])
                if att_d:
                    try:
                        from pdf_generator import generer_attachement_pdf
                        pdf = generer_attachement_pdf(att_d)
                        st.download_button("Télécharger PDF Attachement", data=pdf,
                            file_name=f"Att_{sel_att}.pdf", mime="application/pdf",
                            width="stretch", key="dl_att")
                    except Exception as e:
                        st.error(str(e))

    # ── CRÉER ─────────────────────────────────────────────────────────────────
    with tab_creer:
        # Récupérer commandes disponibles
        # Uniquement les commandes (confirmées, livrées ou en attente)
        try:
            all_cmds = ctrl.get_all_commandes()
            cmds_att = [c for c in all_cmds
                        if c.get("statut","") == "livree"]
        except Exception:
            cmds_att = []

        if not cmds_att:
            _warn("Aucune commande livrée disponible. Marquez d'abord une commande comme livrée.")
            source_devis_id = None
            source_client   = ""
            source_engins   = []
        else:
            _sec("Sélectionner la commande")
            cmd_opts = {
                f"{c['numero']} — {c['client']} "
                f"({c.get('date_debut','').strftime('%d/%m/%Y') if c.get('date_debut') else ''}"
                f" → {c.get('date_fin','').strftime('%d/%m/%Y') if c.get('date_fin') else ''})": c
                for c in cmds_att
            }
            sel_cmd = st.selectbox("Commande *", list(cmd_opts.keys()), key="att_cmd")
            cmd_sel = cmd_opts.get(sel_cmd) or next(iter(cmd_opts.values()))
            source_devis_id = cmd_sel.get("devis_id")
            source_client   = cmd_sel.get("client","")
            source_engins   = cmd_sel.get("engins",[])

        if cmds_att:
         # Info client
         st.markdown(
            f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;'
            f'padding:12px 16px;margin:8px 0;font-size:13px;font-weight:600;color:#1D4ED8">'
            f'Client : {source_client}</div>',
            unsafe_allow_html=True)

        # Période
        _sec("Mois et projet")
        ca1, ca2, ca3 = st.columns(3)
        with ca1:
            mois_a  = st.number_input("Mois", 1, 12, date.today().month, key="att_mois")
        with ca2:
            annee_a = st.number_input("Année", 2020, 2035, date.today().year, key="att_annee")
        with ca3:
            projet_a = st.text_input("Chantier / Projet", key="att_proj")
        obs_a = st.text_area("Observations", key="att_obs")

        # ── Récupérer les engins de la commande ───────────────────────────────
        all_engs_db = ctrl.get_all_engins()
        eng_db_map  = {e.nom: e for e in all_engs_db}

        # Construire liste engins avec leurs objets DB
        engins_liste = []
        for e_info in source_engins:
            nom = e_info["nom"] if isinstance(e_info, dict) else str(e_info)
            eng_obj = eng_db_map.get(nom)
            if not eng_obj:
                # Try partial match
                eng_obj = next((e for e in all_engs_db if e.nom in nom or nom in e.nom), None)
            engins_liste.append({
                "nom":       nom,
                "engin_id":  eng_obj.id if eng_obj else None,
                "matricule": eng_obj.matricule if eng_obj else "",
                "prix":      eng_obj.prix_journalier if eng_obj else 0,
            })

        if not engins_liste:
            # Fallback — tous les engins disponibles
            engins_liste = [{
                "nom":      e.nom,
                "engin_id": e.id,
                "matricule":e.matricule,
                "prix":     e.prix_journalier,
            } for e in all_engs_db[:5]]

        # ── Tableau de pointage multi-engins ─────────────────────────────────
        nb_j_mois = cal_mod.monthrange(int(annee_a), int(mois_a))[1]
        _div()
        _sec(f"Pointage journalier — {mois_a:02d}/{annee_a} ({nb_j_mois} jours)")

        st.markdown(
            f'<div style="background:#ECFDF5;border:1px solid #A7F3D0;border-radius:8px;'
            f'padding:10px 14px;margin-bottom:12px;font-size:13px;color:#065F46">'
            f'✅ <b>{len(engins_liste)} engin(s)</b> dans cet attachement — '
            f'pointage commun pour tous</div>',
            unsafe_allow_html=True)

        with st.form("form_att_multi"):
            # Un tableau de saisie par engin
            jours_par_engin = {}  # {engin_idx: {jour: valeur}}

            for ei, eng in enumerate(engins_liste):
                st.markdown(
                    f'<div style="background:#F8FAFC;border-left:3px solid {PRIMARY};'
                    f'padding:8px 12px;border-radius:0 8px 8px 0;margin-bottom:6px;'
                    f'font-size:13px;font-weight:600;color:#1E3A5F">'
                    f'🚛 {eng["nom"]} — {eng["prix"]:,.0f} MAD/jr</div>',
                    unsafe_allow_html=True)

                jours_par_engin[ei] = {}
                cols_j = st.columns(7)
                for j in range(1, nb_j_mois + 1):
                    with cols_j[(j-1) % 7]:
                        st.markdown(
                            f"<div style='text-align:center;font-size:9px;"
                            f"color:#94A3B8'>J{j}</div>",
                            unsafe_allow_html=True)
                        # Seulement 0, 0.5 (demi-jour) ou 1 (journée complète)
                        v = st.number_input(
                            f"e{ei}_j{j}", 0.0, 1.0, 0.0, 0.5,
                            key=f"att_e{ei}_j{j}",
                            label_visibility="collapsed")
                        jours_par_engin[ei][j] = v

                # Total engin — uniquement en jours
                tot_jours_e = sum(jours_par_engin[ei].values())
                st.caption(f"→ Total : {tot_jours_e:.1f} jour(s)  |  1 = journée complète, 0.5 = demi-journée")
                st.markdown("<hr style='margin:8px 0;border-color:#F1F5F9'>",
                            unsafe_allow_html=True)

            if st.form_submit_button("Enregistrer l'Attachement",
                                      type="primary", width="stretch"):
                # Vérifier qu'au moins un jour est saisi
                total_global = sum(
                    sum(jours_par_engin[ei].values())
                    for ei in jours_par_engin
                )
                if total_global == 0:
                    st.error("Saisissez au moins une journée travaillée (1 = journée, 0.5 = demi-journée).")
                else:
                    with st.spinner("Enregistrement en cours..."):
                        try:
                            # Construire engins_jours — valeurs exactes en jours (0.5 ou 1)
                            engins_jours = []
                            for ei, eng in enumerate(engins_liste):
                                jours_detail = [
                                    (j, v, v)  # (jour, jours, jours) — pas d'heures
                                    for j, v in jours_par_engin[ei].items()
                                    if v > 0
                                ]
                                total_jours_engin = sum(v for v in jours_par_engin[ei].values() if v > 0)
                                engins_jours.append({
                                    "engin_id":         eng["engin_id"],
                                    "matricule":        eng["matricule"],
                                    "nom":              eng["nom"],
                                    "jours_detail":     jours_detail,
                                    "nb_jours":         total_jours_engin,        # float exact ex: 2.5
                                    "nb_jours_travailles": total_jours_engin,     # float exact
                                    "nb_heures_travaillees": total_jours_engin,   # idem pour éviter arrondi
                                })

                            att_id, att_num = ctrl.create_attachement_multi(
                                devis_id=source_devis_id,
                                engins_jours=engins_jours,
                                mois=int(mois_a), annee=int(annee_a),
                                projet=projet_a, observations=obs_a,
                            )
                            st.success(
                                f"✅ Attachement **{att_num}** créé avec succès !\n"
                                f"{len(engins_liste)} engin(s) — "
                                f"Allez dans Facturation pour créer la facture.")
                            st.balloons()
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Erreur : {ex}")