"""modules/attestations.py — Attestations de Retard | LocationBTP"""
import streamlit as st, pandas as pd
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import controller as ctrl
from modules.ui_helpers import (render_page_header, _sec, _info, _warn,
                                _div, PRIMARY, GREEN, RED, ORANGE, GRAY_400)


def render():
    from pdf_generator import generer_attestation_retard_pdf
    render_page_header("⚠️", "Attestations de Retard",
                        "Uniquement les factures dont l'échéance est dépassée")


    _div()

    tab_liste, tab_creer = st.tabs(["Liste des Attestations", "Créer une Attestation"])

    # ── LISTE ─────────────────────────────────────────────────────────────────
    with tab_liste:
        atts = ctrl.get_all_attestations()
        if not atts:
            _info("Aucune attestation générée.")
        df_att = pd.DataFrame([{
            "N° Attestation": a["numero"],
            "N° Facture":     a["facture_numero"],
            "Client":         a["client"],
            "Date":           a["date_emission"].strftime("%d/%m/%Y") if a.get("date_emission") else "—",
            "Retard (j)":     a["nb_jours_retard"],
            "Total (MAD)":    f"{a['montant_total']:,.2f}",
        } for a in atts])
        st.dataframe(df_att, width="stretch", hide_index=True)
        if atts:
            _div()
            am = {f"{a['numero']} — {a['client']}": a["id"] for a in atts}
            sel_a = st.selectbox("Sélectionner pour PDF / Email",
                                  ["—"] + list(am.keys()), key="att_pdf_sel")
            if sel_a != "—":
                ad = ctrl.get_attestation_by_id(am[sel_a])
                if ad:
                    col_dl, col_em = st.columns(2)
                    try:
                        pdf = generer_attestation_retard_pdf(ad)
                        with col_dl:
                            st.download_button("Télécharger PDF", data=pdf,
                                file_name=f"Att_{sel_a.split(' — ')[0]}.pdf",
                                mime="application/pdf", width="stretch",
                                key="dl_att_r")
                        with col_em:
                            try:
                                from database import SessionLocal
                                from models import AttestationRetard as ARM
                                _sa = SessionLocal()
                                _att = _sa.query(ARM).filter(ARM.id==am[sel_a]).first()
                                _e = _att.facture.devis.client.email if _att and _att.facture and _att.facture.devis and _att.facture.devis.client else ""
                                _n = _att.facture.devis.client.nom_complet if _att and _att.facture and _att.facture.devis and _att.facture.devis.client else ""
                                _fnum = _att.facture.numero if _att and _att.facture else ""
                                _sa.close()
                                if _e:
                                    if st.button("Envoyer par Email", key="btn_email_att",
                                                 type="secondary", width="stretch"):
                                        from email_service import email_attestation_retard
                                        ok2, msg2 = email_attestation_retard(
                                            _n, _e, ad["numero"], _fnum,
                                            ad["montant_capital"], ad["montant_interets"],
                                            ad["montant_total"], pdf)
                                        if ok2: st.success(f"✅ Envoyé à {_e}")
                                        else:   st.error(f"Erreur : {msg2}")
                                    st.caption(f"→ {_e}")
                                else:
                                    st.warning("⚠️ Email client manquant")
                            except Exception:
                                pass
                    except Exception as e:
                        st.error(str(e))

    # ── CRÉER ─────────────────────────────────────────────────────────────────
    with tab_creer:
        today = date.today()
        try:
            toutes = ctrl.get_all_factures()
            factures_retard = []
            for f in toutes:
                ech = f.get("echeance")
                solde = float(f.get("solde_restant", 0) or 0)
                if ech and ech < today and solde > 0 and f.get("statut") != "paye":
                    nb_jours = (today - ech).days
                    factures_retard.append({**f, "nb_jours_retard": nb_jours})
            factures_retard.sort(key=lambda x: x["nb_jours_retard"], reverse=True)
        except Exception as ex:
            factures_retard = []
            st.error(f"Erreur : {ex}")

        if not factures_retard:
            st.markdown("""
            <div style="background:#ECFDF5;border-left:4px solid #10B981;
                        border-radius:0 10px 10px 0;padding:16px;margin-top:8px">
                <div style="font-size:15px;font-weight:700;color:#065F46">
                    ✅ Aucune facture en retard</div>
                <div style="font-size:13px;color:#047857;margin-top:4px">
                    Une facture apparaît ici uniquement quand sa date d'échéance
                    est dépassée et que le solde reste impayé.</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#FEF2F2;border-left:4px solid #EF4444;
                        border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:16px">
                <b style="color:#991B1B">⚠️ {len(factures_retard)} facture(s) en retard</b>
            </div>""", unsafe_allow_html=True)

            _sec("Sélectionner la facture")
            fo = {}
            for f in factures_retard:
                ech_str = f["echeance"].strftime("%d/%m/%Y")
                label = (f"⚠️ {f['numero']} — {f['client']} — "
                         f"Échéance: {ech_str} — "
                         f"{f['nb_jours_retard']} jours — "
                         f"Solde: {f['solde_restant']:,.2f} MAD")
                fo[label] = f["id"]

            sel_r = st.selectbox("Facture en retard *", list(fo.keys()), key="att_fac_sel")
            fi_r  = next((f for f in factures_retard if f["id"] == fo.get(sel_r)), None)
            if not fi_r and factures_retard:
                fi_r = factures_retard[0]

            if fi_r:
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("💰 Solde restant", f"{fi_r.get('solde_restant',0):,.2f} MAD")
                col_m2.metric("📅 Jours de retard", f"{fi_r.get('nb_jours_retard',0)} jours")
                col_m3.metric("📆 Échéance", fi_r["echeance"].strftime("%d/%m/%Y") if fi_r.get("echeance") else "—")

                _div()
                nb_j  = fi_r.get("nb_jours_retard", 0)
                solde = fi_r.get("solde_restant", 0)
                taux = 0.0
                nb_periodes = 1
                periode_label = ""
                notes_r = st.text_area(
                    "📝 Texte libre à inclure dans l'attestation",
                    placeholder="Ex: Malgré nos relances...",
                    key="att_notes", height=120)

                if st.button("Générer l'Attestation de Retard", type="primary",
                              width="stretch", key="gen_att"):
                    try:
                        taux_label = f"{taux}% fixe"
                        aid2, anum2, _, cap, inter, tot = ctrl.create_attestation_retard(
                            fo[sel_r], taux, notes_r,
                            nb_periodes=nb_periodes, periode_label=taux_label)
                        st.success(f"✅ Attestation **{anum2}** générée !")
                        ad2 = ctrl.get_attestation_by_id(aid2)
                        if ad2:
                            pdf2 = generer_attestation_retard_pdf(ad2)
                            st.download_button("Télécharger PDF", data=pdf2,
                                file_name=f"{anum2}.pdf", mime="application/pdf",
                                width="stretch", key="dl_new_att")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Erreur : {ex}")