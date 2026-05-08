"""modules/facturation.py — Facturation depuis Attachement uniquement | LocationBTP"""
import streamlit as st, pandas as pd
from datetime import date, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import controller as ctrl
from modules.ui_helpers import (render_page_header, _sec, _info, _warn,
                                _div, PRIMARY, GREEN, RED, ORANGE, GRAY_400)

def render():
    render_page_header("💰", "Facturation",
        "Factures générées depuis les attachements validés")


    _div()

    tab_liste, tab_att = st.tabs([
        "Liste des Factures", "Créer depuis Attachement"
    ])

    # ── LISTE ─────────────────────────────────────────────────────────────────
    with tab_liste:
        try:
            factures = ctrl.get_all_factures()
        except Exception:
            factures = []

        if not factures:
            _info("Aucune facture. Créez-en une depuis un attachement.")

        df_f = pd.DataFrame([{
            "N° Facture": f["numero"],
            "Client":     f["client"],
            "Échéance":   f["echeance"].strftime("%d/%m/%Y") if f.get("echeance") else "—",
            "TTC (MAD)":  f"{f['montant_ttc']:,.2f}",
        } for f in factures])
        st.dataframe(df_f, width="stretch", hide_index=True, height=300)

        _div()
        _sec("Télécharger / Envoyer une Facture")
        all_map = {f["numero"]: f["id"] for f in factures}
        sel_pdf = st.selectbox("Sélectionner", ["—"]+list(all_map.keys()), key="sel_fac_pdf")

        if sel_pdf != "—":
            fd = ctrl.get_facture_details_complets(all_map[sel_pdf])
            if fd:
                try:
                    from pdf_generator import generer_facture_pdf
                    # Enrichir fd avec nb_jours depuis l'attachement lié
                    try:
                        _att_num = fd.get("attachement_numero","")
                        if _att_num:
                            _all_atts = ctrl.get_all_attachements()
                            _att_lié = next((a for a in _all_atts if a.get("numero") == _att_num), None)
                            if _att_lié:
                                fd["nb_jours_travailles"] = _att_lié.get("nb_jours_travailles") or _att_lié.get("nb_jours") or 0
                    except Exception:
                        pass
                    pdf = generer_facture_pdf(fd)
                    col_dl, col_em = st.columns(2)
                    with col_dl:
                        st.download_button("Télécharger PDF", data=pdf,
                            file_name=f"Fac_{sel_pdf}.pdf",
                            mime="application/pdf", width="stretch", key="fac_dl")
                    with col_em:
                        _fac_email = fd.get("client_email","")
                        _fac_nom   = fd.get("client_nom","")
                        if _fac_email:
                            if st.button("Envoyer par Email", key="btn_email_fac",
                                         type="secondary", width="stretch",
                                         help=f"Envoyer à {_fac_email}"):
                                from email_service import email_facture
                                _ech = fd["echeance"].strftime("%d/%m/%Y") if fd.get("echeance") else ""
                                ok, msg = email_facture(_fac_nom, _fac_email,
                                    fd["numero"], (fd.get("devis") or {}).get("numero",""),
                                    fd["montant_ttc"], _ech, pdf)
                                if ok: st.success(f"✅ Facture envoyée à {_fac_email}")
                                else:  st.error(f"Erreur : {msg}")
                            st.caption(f"→ {_fac_email}")
                        else:
                            st.warning("⚠️ Email client manquant")
                except Exception as e:
                    st.error(str(e))

    # ── DEPUIS ATTACHEMENT ────────────────────────────────────────────────────
    with tab_att:
        _sec("Créer une facture depuis un attachement")

        try:
            atts = ctrl.get_all_attachements()
            atts_dispo = [a for a in atts if not a.get("facture_id")]
        except Exception:
            atts_dispo = []

        if not atts_dispo:
            _warn("Aucun attachement disponible (tous déjà facturés ou aucun créé).")
            return

        # Liste : seulement N° ATT — Client (sans nom d'engin)
        att_opts = {
            f"{a['numero']} — {a.get('client','')} — {a.get('mois',0):02d}/{a.get('annee',0)}": a["id"]
            for a in atts_dispo}
        sel_att_f = st.selectbox("Sélectionner l'attachement", list(att_opts.keys()), key="fac_att_sel")
        att_id_f  = att_opts[sel_att_f]

        # Afficher le détail de l'attachement
        att_detail = ctrl.get_attachement_by_id(att_id_f) if att_id_f else None
        if att_detail:
            # Récupérer les jours par engin depuis la DB
            try:
                from database import SessionLocal as _SL
                from sqlalchemy import text as _text
                _s = _SL()
                _rows = _s.execute(
                    _text("SELECT engin_id, matricule_engin, SUM(jours_travail) as jt "
                          "FROM jours_attachement WHERE attachement_id = :aid "
                          "GROUP BY engin_id, matricule_engin"),
                    {"aid": att_id_f}
                ).fetchall()
                # Fallback si jours_travail vide
                if not _rows or all(r[2] is None or float(r[2] or 0) == 0 for r in _rows):
                    _rows = _s.execute(
                        _text("SELECT engin_id, matricule_engin, SUM(heures) as jt "
                              "FROM jours_attachement WHERE attachement_id = :aid "
                              "GROUP BY engin_id, matricule_engin"),
                        {"aid": att_id_f}
                    ).fetchall()
                _s.close()
                jours_par_engin_preview = {(r[0], r[1] or ""): float(r[2] or 0) for r in _rows}
            except Exception:
                jours_par_engin_preview = {}

            # Calculer HT depuis chaque engin individuellement
            devis_lignes = att_detail.get("devis", {}).get("lignes", [])
            ht_calc = 0
            lignes_preview = []
            if jours_par_engin_preview and devis_lignes:
                from database import SessionLocal as _SL2
                from models import Engin as _EngM
                _s2 = _SL2()
                for (eid, mat), nb_j_eng in jours_par_engin_preview.items():
                    if nb_j_eng <= 0:
                        continue
                    _eng = _s2.query(_EngM).filter(_EngM.id == eid).first() if eid else None
                    if not _eng and mat:
                        _eng = _s2.query(_EngM).filter(_EngM.matricule == mat).first()
                    prix_eng = _eng.prix_journalier if _eng else 0
                    nom_eng  = _eng.nom if _eng else (mat or "Engin")
                    mont_eng = round(nb_j_eng * prix_eng, 2)
                    ht_calc += mont_eng
                    lignes_preview.append((nom_eng, nb_j_eng, prix_eng, mont_eng))
                _s2.close()
            else:
                # Fallback simple
                nb_j = att_detail.get("nb_jours_travailles") or 0
                prix_j = att_detail.get("prix_journalier", 0) or 0
                if not prix_j and devis_lignes:
                    prix_j = devis_lignes[0].get("prix_unitaire", 0) or 0
                ht_calc = round(nb_j * prix_j, 2)
                lignes_preview = [("Engin", nb_j, prix_j, ht_calc)]

            # Affichage
            detail_html = "".join(
                f"→ {nom} : {nj} jr × {px:,.0f} MAD = <b>{mt:,.2f} MAD</b><br>"
                for nom, nj, px, mt in lignes_preview
            )
            st.markdown(f"""
            <div style="background:#ECFDF5;border:1px solid #A7F3D0;border-radius:10px;
                        padding:14px;margin-bottom:16px">
                <div style="font-size:13px;font-weight:600;color:#065F46">
                    Calcul automatique depuis l'attachement
                </div>
                <div style="font-size:12px;color:#047857;margin-top:6px">
                    {detail_html}
                    <b>Montant HT total : {ht_calc:,.2f} MAD</b>
                </div>
            </div>""", unsafe_allow_html=True)

        _div()
        tva_f   = st.number_input("TVA (%)", 0.0, 100.0, 20.0, 5.0, key="fac_tva_att")
        ech_j_f = st.number_input("Délai de paiement (jours)", 0, 365, 30, key="fac_ech_att")

        # Aperçu calcul final
        if att_detail:
            tva_preview = round(ht_calc * tva_f / 100, 2)
            ttc_preview = round(ht_calc + tva_preview, 2)
            st.markdown(f"""
            <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;
                        padding:12px;margin-bottom:8px">
                <div style="font-size:12px;color:#1E40AF">
                    ✅ <b>Total :</b>
                    HT = <b>{ht_calc:,.2f} MAD</b> |
                    TVA {tva_f:.0f}% = <b>{tva_preview:,.2f} MAD</b> |
                    TTC = <b>{ttc_preview:,.2f} MAD</b>
                </div>
            </div>""", unsafe_allow_html=True)

        if st.button("Créer la Facture depuis Attachement", type="primary",
                      width="stretch", key="fac_from_att"):
            try:
                from controller import create_facture_from_attachement
                from datetime import date, timedelta
                date_ech = date.today() + timedelta(days=int(ech_j_f))

                result = create_facture_from_attachement(
                    att_id_f, tva_taux=tva_f, date_echeance=date_ech)

                if isinstance(result, tuple) and len(result) >= 5:
                    fac_id     = result[0]
                    fac_num    = result[1]
                    ht         = result[2]
                    tva        = result[3]
                    ttc        = result[4]
                    lignes_att = result[5] if len(result) > 5 else []
                else:
                    fac_id = result; fac_num = "FAC"
                    ht = ht_calc
                    tva = round(ht_calc * tva_f / 100, 2)
                    ttc = round(ht_calc + tva, 2)
                    lignes_att = []

                # Afficher détail par engin
                st.success(f"✅ Facture **{fac_num}** créée avec succès !")

                # Les lignes viennent du controller avec jours/prix/montant corrects par engin
                # Si vides, reconstruire depuis lignes_preview calculées plus haut
                if not lignes_att and lignes_preview:
                    lignes_att = [{
                        "designation": f"LOCATION {nom.upper()}",
                        "qte":     nj,
                        "prix":    px,
                        "montant": mt,
                    } for nom, nj, px, mt in lignes_preview]

                # ── Mettre à jour le statut du BL lié → "livre" ──────────────
                try:
                    from database import SessionLocal
                    from models import BonLivraison as BLM, Attachement as ATM
                    _s_bl = SessionLocal()
                    # Trouver l'attachement → devis → BL lié
                    _att_obj = _s_bl.query(ATM).filter(ATM.id == att_id_f).first()
                    if _att_obj and _att_obj.devis_id:
                        _bl_obj = _s_bl.query(BLM).filter(
                            BLM.devis_id == _att_obj.devis_id).first()
                        if _bl_obj:
                            _bl_obj.statut = "livre"
                            _s_bl.commit()
                    _s_bl.close()
                except Exception:
                    pass  # Ne pas bloquer si le BL n'existe pas

                if lignes_att:
                    df_l = pd.DataFrame([{
                        "Engin":       l["designation"],
                        "Jours":       f"{l['qte']:.2f}",
                        "Prix/jr":     f"{l['prix']:,.2f} MAD",
                        "Montant":     f"{l['montant']:,.2f} MAD",
                    } for l in lignes_att])
                    st.dataframe(df_l, width="stretch", hide_index=True)
                st.markdown(
                    f"**HT : {ht:,.2f} MAD** | "
                    f"**TVA {tva_f:.0f}% : {tva:,.2f} MAD** | "
                    f"**TTC : {ttc:,.2f} MAD**")
                st.info("La facture est maintenant dans **Suivi des Paiements**.")
                st.rerun()
            except Exception as ex:
                st.error(f"Erreur : {ex}")