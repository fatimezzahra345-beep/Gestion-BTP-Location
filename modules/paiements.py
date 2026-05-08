"""modules/paiements.py — Suivi paiements avec emails | LocationBTP"""
import streamlit as st, pandas as pd
from datetime import date
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import controller as ctrl
from modules.ui_helpers import (render_page_header, _sec, _info, _warn,
                                _err, _div, PRIMARY, GREEN, RED, ORANGE,
                                PURPLE, GRAY_400, GRAY_500, GRAY_900,
                                GRAY_200, BRUN, OR, VERT, ROUGE)


def render():
    import controller as ctrl
    render_page_header("", "Suivi des Paiements", "Vue consolidée des encaissements & créances")

    _div()

    paiements = ctrl.get_suivi_paiements()
    if not paiements:
        _info(" Aucune facture enregistrée.")

    total_fac = sum(p["montant_ttc"] for p in paiements)
    total_pay = sum(p["montant_paye"] for p in paiements)
    total_res = sum(p["solde_restant"] for p in paiements)
    retards = [p for p in paiements if p["nb_jours_retard"] > 0]
    total_retard = sum(p["solde_restant"] for p in retards)

    # KPI
    k1, k2, k3, k4 = st.columns(4)
    for col, (lbl, val, c) in zip([k1, k2, k3, k4], [
        ("Facturé Total", f"{total_fac:,.2f}", OR),
        ("Encaissé", f"{total_pay:,.2f}", VERT),
        ("Restant", f"{total_res:,.2f}", ROUGE),
        ("En Retard", f"{total_retard:,.2f}", ROUGE),
    ]):
        with col:
            st.markdown(f"""<div class="stat-card" style="border-top-color:{c};padding:14px 16px">
                <div class="stat-label">{lbl}</div>
                <div class="stat-value" style="font-size:22px;color:{c}">{val}</div>
                <div class="stat-sub">MAD</div>
            </div>""", unsafe_allow_html=True)

    _div()

    _sec("Détail de tous les paiements")
    ico = {"en_attente": "⏳", "partiel": "🔵", "paye": "✅", "retard": "🔴"}
    df_p = pd.DataFrame([{
        "N° Facture": p["numero"], "N° Devis": p["devis_numero"], "Client": p["client"],
        "Statut": ico.get(p["statut"], "•") + " " + p["statut"].upper(),
        "Échéance": p["echeance"].strftime("%d/%m/%Y") if p["echeance"] else "—",
        "TTC": f"{p['montant_ttc']:,.2f}", "Payé": f"{p['montant_paye']:,.2f}",
        "Restant": f"{p['solde_restant']:,.2f}",
    } for p in paiements])
    st.dataframe(df_p, width='stretch', hide_index=True, height=320)

    _div()
    _sec("Enregistrer un paiement")
    non_p = [p for p in paiements if p["statut"] != "paye"]
    if not non_p:
        st.success("🎉 Toutes les factures sont soldées !")
    else:
        fo = {f"{p['numero']} — {p['client']} ({p['solde_restant']:,.2f} MAD)": p["id"] for p in non_p}
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            sel_p = st.selectbox("Facture", list(fo.keys()), key="pay_sel2")
        fi_p = next((p for p in non_p if p["id"] == fo[sel_p]), non_p[0] if non_p else {})
        with c2:
            mnt = st.number_input("Montant (MAD)", 0.01, float(fi_p["solde_restant"]),
                                  float(fi_p["solde_restant"]), 100.0, key="pay_mnt2")
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Valider", type="primary", width='stretch', key="pay_btn2"):
                ctrl.enregistrer_paiement(fo[sel_p], mnt)
                st.success(f"✅ {mnt:,.2f} MAD enregistré !")
                st.rerun()

        # Bouton email confirmation paiement (manuel)
        try:
            from database import SessionLocal
            from models import Facture as _FM_c
            _sc = SessionLocal()
            _fc = _sc.query(_FM_c).filter(_FM_c.id == fo[sel_p]).first()
            _ec = _fc.devis.client.email if _fc and _fc.devis and _fc.devis.client else ""
            _nc = _fc.devis.client.nom_complet if _fc and _fc.devis and _fc.devis.client else ""
            _numc = _fc.numero
            _paYe = _fc.montant_paye;
            _soldeC = _fc.solde_restant
            _sc.close()
            if _ec:
                if st.button(f"Envoyer Confirmation par Email ({_ec})",
                             key="btn_email_conf_pay", type="secondary",
                             width="stretch"):
                    from email_service import email_confirmation_paiement
                    _ok_c, _msg_c = email_confirmation_paiement(
                        _nc, _ec, _numc, _paYe, _soldeC)
                    if _ok_c:
                        st.success(f"✅ Confirmation envoyée à {_ec}")
                    else:
                        st.error(f"Erreur : {_msg_c}")
            else:
                st.caption("⚠️ Email client manquant — ajoutez-le dans Clients")
        except Exception:
            pass


# ─── ATTESTATIONS DE RETARD ───────────────────────────────────────────────────

def render_attestations():
    import controller as ctrl
    from pdf_generator import generer_attestation_retard_pdf
    render_page_header("", "Attestations de Retard", "Génération des attestations avec intérêts")

    tab_liste, tab_creer = st.tabs(["Liste", "Creer"])

    with tab_liste:
        atts = ctrl.get_all_attestations()
        if not atts:
            _info(" Aucune attestation de retard.")
        else:
            df_att = pd.DataFrame([{
                "N° Att.": a["numero"], "N° Facture": a["facture_numero"], "Client": a["client"],
                "Date": a["date_emission"].strftime("%d/%m/%Y") if a["date_emission"] else "—",
                "Retard (j)": a["nb_jours_retard"], "Taux (%/mois)": a["taux_interet"],
                "Capital": f"{a['montant_capital']:,.2f}",
                "Intérêts": f"{a['montant_interets']:,.2f}",
                "Total": f"{a['montant_total']:,.2f}",
            } for a in atts])
            st.dataframe(df_att, width='stretch', hide_index=True)
            _div()
            am = {a["numero"]: a["id"] for a in atts}
            c1, c2 = st.columns([3, 1])
            with c1:
                sel_a = st.selectbox("Télécharger PDF", ["—"] + list(am.keys()))
            with c2:
                if sel_a != "—":
                    ad = ctrl.get_attestation_by_id(am[sel_a])
                    if ad:
                        try:
                            pdf = generer_attestation_retard_pdf(ad)
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.download_button("Telecharger PDF", data=pdf,
                                               file_name=f"Att_{sel_a}.pdf", mime="application/pdf", key="dl_att_r")
                        except Exception as e:
                            st.error(str(e))

    with tab_creer:
        paiements = ctrl.get_suivi_paiements()
        retards = [p for p in paiements if p["nb_jours_retard"] > 0 and p["statut"] != "paye"]
        if not retards:
            _ok("✅ Aucune facture en retard de paiement.")
            return
        fo = {f"{p['numero']} — {p['client']} — {p['nb_jours_retard']}j — {p['solde_restant']:,.2f} MAD": p["id"]
              for p in retards}
        sel_r = st.selectbox(" Facture en retard *", list(fo.keys()), key="att_fac_sel2")
        fi_r = next((p for p in retards if p["id"] == fo[sel_r]), retards[0] if retards else {})

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Solde Restant", f"{fi_r['solde_restant']:,.2f} MAD")
        c2.metric("📅 Jours de Retard", str(fi_r["nb_jours_retard"]))
        c3.metric("📆 Échéance", fi_r["echeance"].strftime("%d/%m/%Y") if fi_r["echeance"] else "—")

        _div()
        ca1, ca2 = st.columns(2)
        with ca1:
            taux = st.number_input("📈 Taux intérêt (%/mois)", 0.0, 20.0, 1.5, 0.1, key="att_taux2")
        with ca2:
            nm = fi_r["nb_jours_retard"] / 30
            interets_p = round(fi_r["solde_restant"] * taux / 100 * nm, 2)
            total_p = round(fi_r["solde_restant"] + interets_p, 2)
            st.markdown(f"""<div class="lux-danger">
                 Intérêts calculés : <b>{interets_p:,.2f} MAD</b><br>
                <b>Total dû : {total_p:,.2f} MAD</b>
            </div>""", unsafe_allow_html=True)
        notes_r = st.text_area("📝 Notes / Motif")
        if st.button("Generer l'Attestation", type="primary", width='stretch', key="gen_att2"):
            try:
                aid2, anum2, _, cap, inter, tot = ctrl.create_attestation_retard(fo[sel_r], taux, notes_r)
                st.success(f"✅ Attestation **{anum2}** — Total : {tot:,.2f} MAD")
                ad2 = ctrl.get_attestation_by_id(aid2)
                pdf = generer_attestation_retard_pdf(ad2)
                st.download_button("Telecharger PDF", data=pdf,
                                   file_name=f"Att_{anum2}.pdf", mime="application/pdf", key="new_att_dl2")
                # Bouton email attestation
                try:
                    from database import SessionLocal
                    from models import AttestationRetard as _ARM
                    _sa = SessionLocal()
                    _att = _sa.query(_ARM).filter(_ARM.id == aid2).first()
                    _e_att = _att.facture.devis.client.email if _att and _att.facture and _att.facture.devis and _att.facture.devis.client else ""
                    _n_att = _att.facture.devis.client.nom_complet if _att and _att.facture and _att.facture.devis and _att.facture.devis.client else ""
                    _fnum_att = _att.facture.numero if _att and _att.facture else ""
                    _sa.close()
                    if _e_att:
                        if st.button(f"Envoyer Attestation par Email ({_e_att})",
                                     key="btn_email_att", type="secondary"):
                            try:
                                from email_service import email_attestation_retard
                                _ok_att, _msg_att = email_attestation_retard(
                                    _n_att, _e_att, anum2, _fnum_att, cap, inter, tot, pdf)
                                if _ok_att:
                                    st.success(f"✅ Attestation envoyée à {_e_att}")
                                else:
                                    st.error(f"Erreur : {_msg_att}")
                            except Exception as _ex_att:
                                st.error(str(_ex_att))
                    else:
                        st.caption("⚠️ Email client manquant")
                except Exception:
                    pass
            except Exception as e:
                st.error(str(e))


# ─── CALENDRIER ───────────────────────────────────────────────────────────────

def render_calendrier():
    import controller as ctrl, matplotlib, matplotlib.pyplot as plt
    matplotlib.use("Agg")
    render_page_header("", "Calendrier des Locations", "Visualisation Gantt des réservations actives")

    events = ctrl.get_locations_calendrier()
    if not events:
        _info(" Aucune location active à afficher.")
        return

    df_ev = pd.DataFrame([{
        "N° Devis": e["devis"], "Client": e["client"], "Engin": e["engin"],
        "Début": e["debut"].strftime("%d/%m/%Y"), "Fin": e["fin"].strftime("%d/%m/%Y"),
        "Durée (j)": (e["fin"] - e["debut"]).days + 1,
        "Statut": e["statut"].upper(),
        "Montant (MAD)": f"{e['montant']:,.2f}",
    } for e in events])
    st.dataframe(df_ev, width='stretch', hide_index=True)


def render_admin():
    import controller as ctrl, platform
    render_page_header("", "Paramètres Administrateur", "Sécurité et configuration système")

    tab_mdp, tab_email, tab_info = st.tabs(["Changer le Mot de Passe", "Configuration Email", "Systeme"])

    with tab_mdp:
        _sec("Modification du mot de passe Admin")
        _info("Le mot de passe doit contenir au moins 8 caractères. Vous serez déconnecté après modification.")
        with st.form("form_pwd"):
            admin_u = ctrl.get_admin_username()
            st.markdown(f"**👤 Utilisateur :** `{admin_u}`");
            _div()
            p_act = st.text_input("🔒 Mot de passe actuel", type="password")
            p_new = st.text_input("🔑 Nouveau mot de passe", type="password")
            p_conf = st.text_input("🔑 Confirmer", type="password")
            if st.form_submit_button("Changer", type="primary", width='stretch'):
                if len(p_new) < 8:
                    st.error("⚠️ Au moins 8 caractères requis.")
                elif p_new != p_conf:
                    st.error("⚠️ Les mots de passe ne correspondent pas.")
                elif not ctrl.verifier_mot_de_passe(admin_u, p_act):
                    st.error("❌ Mot de passe actuel incorrect.")
                else:
                    ctrl.changer_mot_de_passe(admin_u, p_new)
                    st.success("✅ Mot de passe modifié. Reconnectez-vous.")
                    import time;
                    time.sleep(2)
                    st.session_state.authenticated = False;
                    st.rerun()

    with tab_email:
        _sec("Configuration Email SMTP")
        _info("Configurez votre compte Gmail pour envoyer des emails automatiques aux clients.")
        st.markdown("""
        <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;
                    padding:14px 18px;margin-bottom:16px;font-size:13px;color:#1E3A5F">
            <b>Guide Gmail :</b><br>
            1. myaccount.google.com → Securite → Validation en 2 etapes<br>
            2. Mots de passe des applications → Creer "LocationBTP"<br>
            3. Copiez le mot de passe a 16 caracteres ci-dessous
        </div>""", unsafe_allow_html=True)
        try:
            from email_service import get_email_config, save_email_config, tester_connexion_smtp
            cfg = get_email_config()
        except ImportError:
            cfg = {}
        with st.form("form_email_cfg"):
            ec1, ec2 = st.columns(2)
            with ec1:
                smtp_host = st.text_input("Serveur SMTP", value=cfg.get("smtp_host", "smtp.gmail.com"))
                email_from = st.text_input("Email expediteur *", value=cfg.get("email_from", ""))
                nom_exp = st.text_input("Nom affiche", value=cfg.get("nom_expediteur", "Wassime BTP"))
            with ec2:
                smtp_port = st.number_input("Port SMTP", value=int(cfg.get("smtp_port", 587)), min_value=1)
                password = st.text_input("Mot de passe application *", value=cfg.get("password", ""), type="password")
                active = st.checkbox("Activer envoi emails", value=bool(cfg.get("active", True)))
            cs, ct = st.columns(2)
            with cs: save_e = st.form_submit_button("Enregistrer", type="primary", width="stretch")
            with ct: test_e = st.form_submit_button("Tester connexion", width="stretch")
        if save_e:
            try:
                save_email_config(smtp_host, smtp_port, email_from, password, nom_exp, active)
                st.success("Configuration email enregistree !")
            except Exception as ex:
                st.error(str(ex))
        if test_e:
            try:
                ok, msg = tester_connexion_smtp(smtp_host, smtp_port, email_from, password)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
            except Exception as ex:
                st.error(str(ex))
        _div()
        _sec("Emails automatiques envoyes")
        for evt, desc in [
            ("Devis cree", "PDF devis joint"),
            ("Facture emise", "PDF facture joint"),
            ("Bon de Livraison", "PDF BL joint"),
            ("Relance paiement", "Factures en retard"),
            ("Confirmation paiement", "Apres encaissement"),
            ("Attestation retard", "PDF attestation joint"),
        ]:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #F1F5F9"><div><div style="font-size:13px;font-weight:600;color:#0F172A">{evt}</div><div style="font-size:11.5px;color:#94A3B8">{desc}</div></div><span style="font-size:11px;font-weight:700;color:#10B981;background:#ECFDF5;padding:3px 10px;border-radius:20px">Auto</span></div>',
                unsafe_allow_html=True)

    with tab_info:
        _sec("Informations système")
        from database import engine
        db_type = "PostgreSQL" if "postgresql" in str(engine.url) else "SQLite (local dev)"
        infos = [
            ("Application", "LocationBTP v2.0"),
            ("Entreprise", "Ste Wassime BTP"),
            ("Base de données", db_type),
            ("Python", platform.python_version()),
            ("Utilisateur", ctrl.get_admin_username()),
            ("Localisation", "Marrakech, Maroc"),
        ]
        cards_html = "".join([
            f'<div style="padding:12px;background:#FAF6F1;border-radius:10px">'
            f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#9B7B62">{lb}</div>'
            f'<div style="font-size:14px;font-weight:700;color:{BRUN};margin-top:4px">{vl}</div></div>'
            for lb, vl in infos
        ])
        st.markdown(f"""<div class="lux-card" style="padding:24px">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
                {cards_html}
            </div>
        </div>""", unsafe_allow_html=True)
        _div()
        _sec("Identifiants par défaut")
        st.markdown("""<div class="lux-info">
            <b>Username :</b> Admin &nbsp;|&nbsp; <b>Mot de passe par défaut :</b> Wassime2026<br>
             Changez ce mot de passe depuis l'onglet <b> Changer le Mot de Passe</b>.
        </div>""", unsafe_allow_html=True)


# ─── WIDGET DISPONIBILITÉ ENGINS ──────────────────────────────────────────────

def render_engins_dispo_widget():
    import controller as ctrl
    engins_d = ctrl.get_engins_disponibilite()
    if not engins_d: return
    cols = st.columns(3)
    for i, e in enumerate(engins_d):
        total = e["total"];
        dispo = e["disponibles"];
        loues = e["loues"];
        cmds = e["commandes_count"]
        c = "#DC2626" if dispo == 0 else "#92400E" if dispo < total else VERT
        with cols[i % 3]:
            st.markdown(f"""<div class="lux-card" style="border-top-color:{c};padding:14px">
                <div style="font-size:13px;font-weight:700;color:{BRUN}">{e["nom"]}</div>
                <div style="font-size:11px;color:#9B7B62;margin-bottom:10px">{e["matricule"]}</div>
                <div style="display:flex;gap:10px;text-align:center">
                    <div><div style="font-size:20px;font-weight:800;color:{VERT}">{dispo}</div>
                         <div style="font-size:10px;color:#9B7B62">Dispo</div></div>
                    <div><div style="font-size:20px;font-weight:800;color:{BRUN}">{loues}</div>
                         <div style="font-size:10px;color:#9B7B62">Loués</div></div>
                    <div><div style="font-size:20px;font-weight:800;color:{OR}">{cmds}</div>
                         <div style="font-size:10px;color:#9B7B62">Cmdés</div></div>
                    <div><div style="font-size:20px;font-weight:800;color:#888">{total}</div>
                         <div style="font-size:10px;color:#9B7B62">Total</div></div>
                </div>
                <div style="background:#F2E8DC;border-radius:4px;height:5px;margin-top:8px">
                    <div style="background:{c};width:{int(dispo / total * 100) if total else 0}%;
                                height:5px;border-radius:4px"></div>
                </div>
            </div>""", unsafe_allow_html=True)