"""pages/devis.py — Devis avec bouton Transformer en Commande | LocationBTP"""
import streamlit as st, pandas as pd
from datetime import date, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import controller as ctrl
from modules.ui_helpers import (render_page_header, _sec, _info, _warn,
                               _err, _div, PRIMARY, GREEN, RED, ORANGE,
                               GRAY_400, GRAY_900)

def render():
    render_page_header("📝", "Devis",
        "Créez un devis → Validez → Transformez en Commande")

    tab_liste, tab_nouveau = st.tabs(["Liste des Devis", "Nouveau Devis"])

    # ── LISTE & ACTIONS ────────────────────────────────────────────────────────
    with tab_liste:
        devis_list = ctrl.get_all_devis()
        if not devis_list:
            _info("Aucun devis. Créez votre premier devis.")

        # Filtres
        statuts = ["Tous","brouillon","valide","facture","annule"]
        col_f, col_s = st.columns([2, 3])
        with col_f:
            fil = st.selectbox("Filtrer par statut", statuts, key="dev_fil")
        with col_s:
            search = st.text_input("Rechercher", placeholder="Numéro, client…", key="dev_search")

        filtres = [d for d in devis_list
                   if (fil == "Tous" or d["statut"] == fil)
                   and (not search or search.lower() in d["numero"].lower()
                        or search.lower() in d["client"].lower())]

        badge = {"brouillon":"#94A3B8","valide":GREEN,"facture":PRIMARY,"annule":RED}
        df = pd.DataFrame([{
            "Numéro": d["numero"], "Client": d["client"],
            "Début": d["date_debut"].strftime("%d/%m/%Y") if d["date_debut"] else "—",
            "Fin":   d["date_fin"].strftime("%d/%m/%Y") if d["date_fin"] else "—",
            "TTC (MAD)": f"{d['montant_ttc']:,.2f}",
            "Statut": d["statut"].upper(),
        } for d in filtres])
        st.dataframe(df, width="stretch", hide_index=True, height=280)

        _div()
        _sec("Actions sur un devis")

        d_map = {f"{d['numero']} — {d['client']} — {d['statut'].upper()}": d["id"]
                 for d in filtres}
        sel = st.selectbox("Sélectionner un devis", ["—"] + list(d_map.keys()), key="dev_sel")

        if sel != "—":
            dv_id  = d_map[sel]
            ddata  = ctrl.get_devis_by_id(dv_id)
            if not ddata:
                st.error("Devis introuvable."); return

            statut = ddata["statut"]
            col_a, col_c, col_d = st.columns(3)

            # ── Valider
            with col_a:
                if statut == "brouillon":
                    if st.button("Valider le Devis", type="primary", width="stretch",
                                  key="dv_val"):
                        ctrl.valider_devis(dv_id)
                        st.success("Devis validé !"); st.rerun()
                else:
                    st.button("Valider", disabled=True, width="stretch")

            # ── Annuler
            with col_c:
                if statut not in ["annule","facture"]:
                    if st.button("Annuler le Devis", type="secondary",
                                  width="stretch", key="dv_ann"):
                        ctrl.annuler_devis(dv_id); st.success("Devis annulé."); st.rerun()
                else:
                    st.button("Annuler", disabled=True, width="stretch")

            # ── PDF + Email
            with col_d:
                try:
                    from pdf_generator import generer_devis_pdf
                    pdf = generer_devis_pdf(ddata)
                    st.download_button("Télécharger PDF", data=pdf,
                        file_name=f"Devis_{ddata['numero']}.pdf",
                        mime="application/pdf", width="stretch", key="dv_pdf")
                except Exception as ex:
                    st.error(str(ex))

            # Bouton email sous les actions
            client_email = ddata.get("client_email","")
            if client_email:
                if st.button(f"Envoyer par Email ({client_email})",
                              key="dv_email", type="secondary"):
                    try:
                        from pdf_generator import generer_devis_pdf
                        from email_service import email_devis
                        pdf2 = generer_devis_pdf(ddata)
                        ok, msg = email_devis(
                            ddata["client_nom"], client_email, ddata["numero"],
                            ddata["date_debut"].strftime("%d/%m/%Y") if ddata.get("date_debut") else "",
                            ddata["date_fin"].strftime("%d/%m/%Y") if ddata.get("date_fin") else "",
                            ddata["montant_ttc"], pdf2)
                        if ok: st.success(f"✅ Devis envoyé à {client_email}")
                        else:  st.error(f"Erreur : {msg}")
                    except Exception as ex: st.error(str(ex))
            else:
                st.caption("⚠️ Email client manquant — ajoutez-le dans Clients")

            # Récapitulatif du devis sélectionné
            if ddata.get("lignes"):
                _div()
                _sec(f"Détail du devis {ddata['numero']}")
                st.markdown(f"**Client :** {ddata['client_nom']} &nbsp;|&nbsp; "
                            f"**Période :** {ddata.get('date_debut','—')} → {ddata.get('date_fin','—')} "
                            f"({ddata.get('duree_jours',0)} jours)")
                df_lig = pd.DataFrame([{
                    "Engin": l["engin_nom"], "Qté": l["quantite"],
                    "Prix/jr (MAD)": f"{l['prix_unitaire']:,.2f}",
                    "Total (MAD)": f"{l['montant']:,.2f}",
                } for l in ddata["lignes"]])
                st.dataframe(df_lig, width="stretch", hide_index=True)
                col_ht, col_tva, col_ttc = st.columns(3)
                col_ht.metric("HT (MAD)", f"{ddata['montant_ht']:,.2f}")
                col_tva.metric(f"TVA {ddata['tva_taux']}%", f"{ddata['montant_tva']:,.2f}")
                col_ttc.metric("TTC (MAD)", f"{ddata['montant_ttc']:,.2f}")

    # ── NOUVEAU DEVIS ──────────────────────────────────────────────────────────
    with tab_nouveau:
        clients  = ctrl.get_all_clients()
        engins_d = ctrl.get_all_engins()  # TOUS les engins sans exception

        if not clients:
            _err("Aucun client. Ajoutez un client d'abord."); return
        if not engins_d:
            _err("Aucun engin dans le parc. Ajoutez des engins d'abord."); return

        _sec("Informations générales")
        nd1, nd2, nd3 = st.columns(3)
        with nd1:
            cli_opts = {f"{c.nom_complet}": c.id for c in clients}
            sel_cli  = st.selectbox("Client *", list(cli_opts.keys()), key="nd_cli")
        with nd2:
            date_debut = st.date_input("Date de début *", value=date.today(), key="nd_deb")
        with nd3:
            date_fin   = st.date_input("Date de fin *",
                value=date.today() + timedelta(days=7), key="nd_fin")

        if date_fin <= date_debut:
            st.error("La date de fin doit être après la date de début.")
            return

        duree = (date_fin - date_debut).days
        if duree <= 0: duree = 1
        st.info(f"Durée : **{duree} jour(s)**")

        _div()
        _sec("Sélection des engins du parc")
        _info("Tous les engins sont affichés — loués, disponibles ou en maintenance.")

        # Afficher TOUS les engins
        eng_selec = {}
        for eng in engins_d:
            statut_eng = eng.statut or "disponible"
            badge = {"disponible": "🟢", "loue": "🔴", "maintenance": "🟡"}.get(statut_eng, "⚪")
            col_e, col_q = st.columns([4, 1])
            with col_e:
                selected = st.checkbox(
                    f"{badge} **{eng.nom}** ({eng.matricule or '—'}) — "
                    f"{eng.prix_journalier:,.0f} MAD/jr — *{statut_eng}*",
                    key=f"eng_chk_{eng.id}")
            with col_q:
                if selected:
                    qte = st.number_input("Qté", min_value=1,
                        max_value=int(eng.quantite_totale or 99),
                        value=1, key=f"eng_qty_{eng.id}")
                    eng_selec[eng.id] = {
                        "quantite": qte,
                        "prix_unitaire": eng.prix_journalier,
                        "montant": eng.prix_journalier * qte * duree
                    }
                    st.caption(f"{eng.prix_journalier:,.0f} × {qte} × {duree}j = {eng.prix_journalier*qte*duree:,.0f} MAD")

        if eng_selec:
            _div()
            ht  = sum(v["montant"] for v in eng_selec.values())
            nd_tva = st.number_input("TVA (%)", 0.0, 100.0, 20.0, 5.0, key="nd_tva")
            tva = ht * nd_tva / 100
            ttc = ht + tva
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("HT (MAD)", f"{ht:,.2f}")
            col_m2.metric(f"TVA {nd_tva:.0f}%", f"{tva:,.2f}")
            col_m3.metric("TTC (MAD)", f"{ttc:,.2f}")

            notes = st.text_area("Notes / Conditions", key="nd_notes")

            if st.button("Créer le Devis", type="primary", width="stretch", key="nd_create"):
                lignes = [{"engin_id": eid, **v} for eid, v in eng_selec.items()]
                with st.spinner("Création du devis en cours..."):
                    try:
                        dv_id, dv_num = ctrl.create_devis(
                            client_id=cli_opts[sel_cli],
                            date_debut=date_debut, date_fin=date_fin,
                            lignes=lignes, tva_taux=nd_tva,
                            notes=notes, echeance_jours=0)
                        st.success(f"✅ Devis **{dv_num}** créé avec succès ! Allez dans Liste → Valider → Transformer en Commande.")
                        st.balloons()
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Erreur : {ex}")
        else:
            _info("Sélectionnez au moins un engin pour calculer le montant.")