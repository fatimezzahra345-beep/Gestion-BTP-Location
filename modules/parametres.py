"""modules/parametres.py — Paramètres + Configuration Email | LocationBTP"""
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
    import controller as ctrl, platform
    render_page_header("", "Paramètres Administrateur","Sécurité et configuration système")

    tab_mdp, tab_email, tab_info = st.tabs(["Changer le Mot de Passe", "Configuration Email", "Systeme"])

    with tab_mdp:
        _sec("Modification du mot de passe Admin")
        _info("Le mot de passe doit contenir au moins 8 caractères. Vous serez déconnecté après modification.")
        with st.form("form_pwd"):
            admin_u=ctrl.get_admin_username()
            st.markdown(f"**👤 Utilisateur :** `{admin_u}`"); _div()
            p_act=st.text_input("🔒 Mot de passe actuel",type="password")
            p_new=st.text_input("🔑 Nouveau mot de passe",type="password")
            p_conf=st.text_input("🔑 Confirmer",type="password")
            if st.form_submit_button("Changer",type="primary",width='stretch'):
                if len(p_new)<8: st.error("⚠️ Au moins 8 caractères requis.")
                elif p_new!=p_conf: st.error("⚠️ Les mots de passe ne correspondent pas.")
                elif not ctrl.verifier_mot_de_passe(admin_u,p_act): st.error("❌ Mot de passe actuel incorrect.")
                else:
                    ctrl.changer_mot_de_passe(admin_u,p_new)
                    st.success("✅ Mot de passe modifié. Reconnectez-vous.")
                    import time; time.sleep(2)
                    st.session_state.authenticated=False; st.rerun()

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
                smtp_host = st.text_input("Serveur SMTP", value=cfg.get("smtp_host","smtp.gmail.com"))
                email_from= st.text_input("Email expediteur *", value=cfg.get("email_from",""))
                nom_exp   = st.text_input("Nom affiche", value=cfg.get("nom_expediteur","Wassime BTP"))
            with ec2:
                smtp_port = st.number_input("Port SMTP", value=int(cfg.get("smtp_port",587)), min_value=1)
                password  = st.text_input("Mot de passe application *", value=cfg.get("password",""), type="password")
                active    = st.checkbox("Activer envoi emails", value=bool(cfg.get("active",True)))
            cs, ct = st.columns(2)
            with cs: save_e = st.form_submit_button("Enregistrer", type="primary", width="stretch")
            with ct: test_e = st.form_submit_button("Tester connexion", width="stretch")
        if save_e:
            try:
                save_email_config(smtp_host, smtp_port, email_from, password, nom_exp, active)
                st.success("Configuration email enregistree !")
            except Exception as ex: st.error(str(ex))
        if test_e:
            try:
                ok, msg = tester_connexion_smtp(smtp_host, smtp_port, email_from, password)
                if ok: st.success(msg)
                else:  st.error(msg)
            except Exception as ex: st.error(str(ex))
        _div()
        _sec("Emails automatiques envoyes")
        for evt, desc in [
            ("Devis cree","PDF devis joint"),
            ("Facture emise","PDF facture joint"),
            ("Bon de Livraison","PDF BL joint"),
            ("Relance paiement","Factures en retard"),
            ("Confirmation paiement","Apres encaissement"),
            ("Attestation retard","PDF attestation joint"),
        ]:
            st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #F1F5F9"><div><div style="font-size:13px;font-weight:600;color:#0F172A">{evt}</div><div style="font-size:11.5px;color:#94A3B8">{desc}</div></div><span style="font-size:11px;font-weight:700;color:#10B981;background:#ECFDF5;padding:3px 10px;border-radius:20px">Auto</span></div>', unsafe_allow_html=True)

    with tab_info:
        _sec("Informations système")
        from database import engine
        db_type="PostgreSQL" if "postgresql" in str(engine.url) else "SQLite (local dev)"
        infos = [
            ("Application","LocationBTP v2.0"),
            ("Entreprise","Ste Wassime BTP"),
            ("Base de données",db_type),
            ("Python",platform.python_version()),
            ("Utilisateur",ctrl.get_admin_username()),
            ("Localisation","Marrakech, Maroc"),
        ]
        cards_html = "".join([
            f'<div style="padding:12px;background:#FAF6F1;border-radius:10px">'
            f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#9B7B62">{lb}</div>'
            f'<div style="font-size:14px;font-weight:700;color:{BRUN};margin-top:4px">{vl}</div></div>'
            for lb,vl in infos
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

        _div()
        _sec("🗑️ Réinitialisation des données")
        st.markdown("""
        <div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;
                    padding:16px;margin-bottom:12px">
            <div style="font-size:13px;font-weight:700;color:#991B1B;margin-bottom:6px">
                ⚠️ Attention — Action irréversible</div>
            <div style="font-size:12px;color:#B91C1C">
                Cette action supprime <b>toutes les données commerciales</b>
                (clients, devis, commandes, BL, attachements, factures, paiements, attestations).<br>
                La configuration email, le mot de passe et le parc d'engins sont <b>conservés</b>.
            </div>
        </div>""", unsafe_allow_html=True)

        confirm_text = st.text_input(
            "Tapez exactement  CONFIRMER  pour activer le bouton",
            key="reset_confirm",
            placeholder="CONFIRMER")

        btn_disabled = confirm_text.strip() != "CONFIRMER"

        if not btn_disabled:
            st.warning("⚠️ Le bouton est maintenant actif — cliquez pour réinitialiser.")

        if st.button("🗑️ Réinitialiser toutes les données",
                     type="secondary", width="stretch",
                     key="btn_reset",
                     disabled=btn_disabled):
            try:
                from database import engine
                from sqlalchemy import text
                with engine.connect() as conn:
                    for tbl in [
                        "attestations_retard",
                        "jours_attachement",
                        "attachements",
                        "factures",
                        "bons_livraison",
                        "lignes_commande",
                        "commandes",
                        "lignes_devis",
                        "devis",
                        "clients",
                    ]:
                        conn.execute(text(f"DELETE FROM {tbl}"))
                    conn.commit()
                ctrl.reset_quantites_engins()
                st.success("✅ Toutes les données ont été réinitialisées !")
                st.info("Le parc d'engins, la configuration email et le mot de passe sont conservés.")
                st.rerun()
            except Exception as ex:
                st.error(f"Erreur : {ex}")


# ─── WIDGET DISPONIBILITÉ ENGINS ──────────────────────────────────────────────