"""pages/clients.py — Gestion des Clients | LocationBTP"""
import streamlit as st, pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import controller as ctrl
from modules.ui_helpers import (render_page_header, _sec, _info, _warn,
                               _div, PRIMARY, GREEN, RED, ORANGE, GRAY_400)

def render():
    render_page_header("👥", "Clients", "Gestion du portefeuille clients")


    _div()


    tab_liste, tab_ajouter, tab_modifier = st.tabs([
        "Liste des Clients", "Nouveau Client", "Modifier un Client"
    ])

    with tab_liste:
        clients = ctrl.get_all_clients()
        if not clients:
            _info("Aucun client. Ajoutez votre premier client dans l'onglet \"Nouveau Client\".")
        sans_email = [c for c in clients if not c.email]
        if sans_email:
            nb = len(sans_email); noms = " · ".join([c.nom_complet for c in sans_email[:5]])
            st.markdown(
                f'<div style="background:#FFFBEB;border-left:4px solid {ORANGE};'
                f'border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:12px">'
                f'<b style="color:#92400E">⚠️ {nb} client(s) sans email</b>'
                f'<div style="font-size:12px;color:#B45309;margin-top:4px">{noms}</div>'
                f'<div style="font-size:11px;color:#92400E;margin-top:4px">'
                f'→ Onglet "Modifier un Client" pour ajouter les emails</div></div>',
                unsafe_allow_html=True)
        search = st.text_input("Rechercher", placeholder="Nom, société, ICE…", key="cli_search")
        filtres = [c for c in clients if not search
                   or search.lower() in (c.nom_complet or "").lower()
                   or search.lower() in (c.email or "").lower()]
        c1, c2 = st.columns(2)
        c1.metric("Total Clients", len(clients))
        c2.metric("Résultats", len(filtres))
        df = pd.DataFrame([{
            "Nom / Société": c.nom_complet,
            "Téléphone":     c.telephone or "—",
            "Email":         ("✅ " + c.email) if c.email else "❌ Manquant",
            "ICE":           c.ice or "—",
            "Lieu / Adresse": (c.adresse or "—")[:40],
        } for c in filtres])
        st.dataframe(df, width="stretch", hide_index=True, height=320)
        _div()
        _sec("Supprimer un client")
        c_ids = {c.nom_complet: c.id for c in clients}
        cs, cb = st.columns([3, 1])
        with cs: sel = st.selectbox("Sélectionner", ["—"] + list(c_ids.keys()), key="del_cli")
        with cb:
            st.markdown("<br>", unsafe_allow_html=True)
            if sel != "—" and st.button("Supprimer", type="secondary", width="stretch"):
                ctrl.delete_client(c_ids[sel]); st.success(f"{sel} supprimé."); st.rerun()

    with tab_ajouter:
        _sec("Informations du nouveau client")
        with st.form("form_cli_new"):
            c1, c2 = st.columns(2)
            with c1:
                nom = st.text_input("Nom *"); prenom = st.text_input("Prénom")
                societe = st.text_input("Société")
            with c2:
                ice = st.text_input("ICE"); tel = st.text_input("Téléphone")
                email = st.text_input("Email *", placeholder="contact@societe.ma",
                                       help="Obligatoire pour l'envoi automatique des documents")
            adresse = st.text_area("Lieu / Adresse du chantier *",
                                   placeholder="Ville, quartier, rue... ex: Marrakech, Guéliz, Rue Ibn Sina")
            if st.form_submit_button("Enregistrer le client", type="primary", width="stretch"):
                if not nom.strip():
                    st.error("Le nom est obligatoire.")
                else:
                    ctrl.create_client(nom=nom, prenom=prenom, societe=societe,
                                       ice=ice, telephone=tel, email=email, adresse=adresse)
                    if not email:
                        st.warning(f"Client ajouté — pensez à ajouter son email !")
                    else:
                        st.success(f"Client {societe or nom} ajouté !")
                    st.rerun()

    with tab_modifier:
        clients_m = ctrl.get_all_clients()
        if not clients_m:
            _info("Aucun client à modifier."); return
        cli_map = {f"{c.nom_complet}{'  ⚠️' if not c.email else ''}": c for c in clients_m}
        sel_c = st.selectbox("Sélectionner le client", list(cli_map.keys()), key="mod_cli")
        cli = cli_map[sel_c]
        if cli.email:
            st.markdown(f'<div style="background:#ECFDF5;border-left:4px solid {GREEN};'
                        f'border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:12px;'
                        f'font-size:13px;color:#065F46">✅ Email : <b>{cli.email}</b></div>',
                        unsafe_allow_html=True)
        else:
            _warn("⚠️ Aucun email — Les emails automatiques ne seront PAS envoyés.")
        with st.form(f"form_mod_cli_{cli.id}"):
            mc1, mc2 = st.columns(2)
            with mc1:
                new_nom = st.text_input("Nom *", value=cli.nom)
                new_prenom = st.text_input("Prénom", value=cli.prenom or "")
                new_societe = st.text_input("Société", value=cli.societe or "")
            with mc2:
                new_ice = st.text_input("ICE", value=cli.ice or "")
                new_tel = st.text_input("Téléphone", value=cli.telephone or "")
                new_email = st.text_input("Email *", value=cli.email or "",
                                           placeholder="contact@societe.ma")
            new_adresse = st.text_area("Lieu / Adresse du chantier", value=cli.adresse or "",
                                       placeholder="Ville, quartier, rue...")
            if st.form_submit_button("Enregistrer les modifications", type="primary", width="stretch"):
                if not new_nom.strip():
                    st.error("Le nom est obligatoire.")
                else:
                    ctrl.update_client(cli.id, nom=new_nom, prenom=new_prenom,
                                       societe=new_societe, ice=new_ice,
                                       telephone=new_tel, email=new_email, adresse=new_adresse)
                    st.success("Client mis à jour !"); st.rerun()
        if cli.email:
            _div(); _sec("Tester l'envoi d'email")
            if st.button(f"Envoyer un email de test à {cli.email}", key="test_email_cli"):
                try:
                    from email_service import envoyer_email
                    ok, msg = envoyer_email(cli.email, "Test LocationBTP — Wassime BTP",
                        f"<div style='font-family:sans-serif;padding:20px'><h2>Test</h2>"
                        f"<p>Bonjour <b>{cli.nom_complet}</b>, la configuration email fonctionne !</p></div>")
                    if ok: st.success(f"✅ Email de test envoyé à {cli.email} !")
                    else:  st.error(f"Erreur : {msg}")
                except Exception as ex: st.error(str(ex))