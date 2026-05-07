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

    tab_liste, tab_creer = st.tabs(["Liste des Attestations", "Créer une Attestation"])

    # ── LISTE ─────────────────────────────────────────────────────────────────
    with tab_liste:
        atts = ctrl.get_all_attestations()
        if not atts:
            _info("Aucune attestation générée.")
        else:
            df_att = pd.DataFrame([{
                "N° Attestation": a["numero"],
                "N° Facture":     a["facture_numero"],
                "Client":         a["client"],
                "Date":           a["date_emission"].strftime("%d/%m/%Y") if a.get("date_emission") else "—",
                "Retard (j)":     a["nb_jours_retard"],
                "Total (MAD)":    f"{a['montant_total']:,.2f}",
            } for a in atts])
            st.dataframe(df_att, width="stretch", hide_index=True)
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

        # Seulement factures avec échéance DÉPASSÉE et solde > 0
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
            st.markdown(f"""
            <div style="background:#ECFDF5;border-left:4px solid #10B981;
                        border-radius:0 10px 10px 0;padding:16px;margin-top:8px">
                <div style="font-size:15px;font-weight:700;color:#065F46">
                    ✅ Aucune facture en retard</div>
                <div style="font-size:13px;color:#047857;margin-top:4px">
                    Toutes les factures avec échéance sont à jour.<br>
                    Une facture apparaît ici uniquement quand sa date d'échéance
                    est dépassée et que le solde reste impayé.</div>
            </div>""", unsafe_allow_html=True)
            return

        # Afficher les factures en retard
        st.markdown(f"""
        <div style="background:#FEF2F2;border-left:4px solid #EF4444;
                    border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:16px">
            <b style="color:#991B1B">⚠️ {len(factures_retard)} facture(s) en retard</b>
            <div style="font-size:12px;color:#B91C1C;margin-top:4px">
                Ces factures ont dépassé leur date d'échéance</div>
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
        fi_r  = next(f for f in factures_retard if f["id"] == fo[sel_r])

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("💰 Solde restant", f"{fi_r['solde_restant']:,.2f} MAD")
        col_m2.metric("📅 Jours de retard", f"{fi_r['nb_jours_retard']} jours")
        col_m3.metric("📆 Échéance", fi_r["echeance"].strftime("%d/%m/%Y"))

        _div()
        _sec("Taux d'intérêt de retard — 100% personnalisable")

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            taux = st.number_input("Taux d'intérêt (%)",
                                    min_value=0.0, max_value=1000.0,
                                    value=1.5, step=0.1, key="att_taux",
                                    help="Entrez le taux. Si pas d'intérêts → mettez 0")
            periode = st.selectbox("Période du taux",
                                    ["Sans période (taux fixe)",
                                     "Journalier", "Hebdomadaire", "Mensuel"],
                                    index=3, key="att_periode")
        with col_t2:
            nb_j  = fi_r["nb_jours_retard"]
            solde = fi_r["solde_restant"]
            if periode == "Sans période (taux fixe)":
                # Taux fixe = calcul immédiat (pas besoin que le temps passe)
                nb_periodes   = 1
                periode_label = f"{taux}% (taux fixe)"
                interets_calc = round(solde * taux / 100, 2) if taux > 0 else 0
                total_calc    = round(solde + interets_calc, 2)
                calcul_info   = f"{taux}% × {solde:,.2f} MAD = {interets_calc:,.2f} MAD"
                show_interets = True
            else:
                # Taux avec période = les intérêts s'accumulent avec le temps
                # On affiche le taux mais PAS le calcul des intérêts
                # (le propriétaire les calculera lui-même selon la durée réelle)
                if periode == "Journalier":
                    periode_label = f"{taux}% par jour"
                    nb_periodes   = nb_j
                elif periode == "Hebdomadaire":
                    periode_label = f"{taux}% par semaine"
                    nb_periodes   = nb_j / 7
                else:  # Mensuel
                    periode_label = f"{taux}% par mois"
                    nb_periodes   = nb_j / 30
                interets_calc = 0  # Non calculé — dépend de la durée finale
                total_calc    = solde
                calcul_info   = f"Intérêts à calculer selon durée réelle ({nb_j} jours de retard)"
                show_interets = False

            if show_interets:
                st.markdown(f"""
                <div style="background:#FEF2F2;border-radius:8px;padding:14px 16px;
                            border-left:4px solid #EF4444;margin-top:4px">
                    <div style="font-size:12px;color:#991B1B;margin-bottom:4px">
                        {periode_label}</div>
                    <div style="font-size:13px;color:#7F1D1D">
                        Capital : <b>{solde:,.2f} MAD</b></div>
                    <div style="font-size:13px;color:#DC2626">
                        Intérêts : <b>+{interets_calc:,.2f} MAD</b></div>
                    <div style="font-size:16px;font-weight:800;color:#991B1B;margin-top:6px">
                        Total dû : {total_calc:,.2f} MAD</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#FFFBEB;border-radius:8px;padding:14px 16px;
                            border-left:4px solid #F59E0B;margin-top:4px">
                    <div style="font-size:12px;color:#92400E;margin-bottom:4px">
                        {periode_label}</div>
                    <div style="font-size:13px;color:#78350F">
                        Capital : <b>{solde:,.2f} MAD</b></div>
                    <div style="font-size:12px;color:#92400E;margin-top:4px">
                        ⏳ {calcul_info}</div>
                    <div style="font-size:12px;color:#92400E;margin-top:2px">
                        L'attestation mentionnera le taux sans calculer les intérêts.</div>
                </div>""", unsafe_allow_html=True)

        _div()
        notes_r = st.text_area(
            "📝 Texte libre à inclure dans l'attestation",
            placeholder="Ex: Malgré nos relances du ... la facture N°... reste impayée. "
                        "Nous vous mettons en demeure de régler sous 8 jours...",
            key="att_notes",
            height=120)

        if st.button("Générer l'Attestation de Retard", type="primary",
                      width="stretch", key="gen_att"):
            if taux == 0 and periode != "Aucun intérêt":
                st.warning("Le taux est à 0% — l'attestation sera générée sans intérêts.")
            try:
                # Passer le taux et la période au controller
                taux_label = f"{taux}% {periode}"
                aid2, anum2, _, cap, inter, tot = ctrl.create_attestation_retard(
                    fo[sel_r], taux, notes_r,
                    nb_periodes=nb_periodes, periode_label=taux_label)

                st.success(f"✅ Attestation **{anum2}** générée !")

                ad2 = ctrl.get_attestation_by_id(aid2)
                if ad2:
                    pdf2 = generer_attestation_retard_pdf(ad2)
                    col_dl2, col_em2 = st.columns(2)
                    with col_dl2:
                        st.download_button("Télécharger PDF", data=pdf2,
                            file_name=f"{anum2}.pdf", mime="application/pdf",
                            width="stretch", key="dl_new_att")
                    with col_em2:
                        try:
                            from database import SessionLocal
                            from models import AttestationRetard as ARM2
                            _s2 = SessionLocal()
                            _att2 = _s2.query(ARM2).filter(ARM2.id==aid2).first()
                            _e2 = _att2.facture.devis.client.email if _att2 and _att2.facture and _att2.facture.devis and _att2.facture.devis.client else ""
                            _n2 = _att2.facture.devis.client.nom_complet if _att2 and _att2.facture and _att2.facture.devis and _att2.facture.devis.client else ""
                            _s2.close()
                            if _e2:
                                if st.button(f"Envoyer par Email ({_e2})",
                                             key="btn_email_new_att",
                                             type="secondary", width="stretch"):
                                    from email_service import email_attestation_retard
                                    ok3, msg3 = email_attestation_retard(
                                        _n2, _e2, anum2, fi_r["numero"],
                                        cap, inter, tot, pdf2)
                                    if ok3: st.success(f"✅ Envoyé à {_e2}")
                                    else:   st.error(f"Erreur : {msg3}")
                            else:
                                st.caption("⚠️ Email client manquant")
                        except Exception:
                            pass
                st.rerun()
            except Exception as ex:
                st.error(f"Erreur : {ex}")