"""modules/livraison.py — Bons de Livraison depuis Commande | LocationBTP"""
import streamlit as st, pandas as pd
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import controller as ctrl
from modules.ui_helpers import (render_page_header, _sec, _info, _warn,
                                _div, PRIMARY, GREEN, RED, ORANGE, GRAY_400)

def render():
    render_page_header("📋", "Bons de Livraison",
        "Créez un BL depuis une commande confirmée")


    _div()

    tab_liste, tab_creer = st.tabs(["Liste des BL", "Créer un BL"])

    with tab_liste:
        try:
            bls = ctrl.get_all_bons_livraison()
        except Exception:
            bls = []

        if not bls:
            _info("Aucun bon de livraison. Créez-en un depuis une commande confirmée.")

        df_bl = pd.DataFrame([{
            "N° BL":      b.get("numero",""),
            "Client":     b.get("client",""),
            "Commande":   b.get("commande_numero","—"),
            "Livraison":  b.get("date_livraison","—"),
            "Lieu":       b.get("lieu_livraison","") or "—",
            "Statut":     {
                "emis":       "⏳ En attente",
                "signe":      "⏳ En attente",
                "en_cours":   "⏳ En attente",
                "en_attente": "⏳ En attente",
                "livre":      "✅ Livré",
                "livree":     "✅ Livré",
                "facture":    "✅ Livré",
            }.get(b.get("statut",""), "⏳ En attente"),
        } for b in bls])
        st.dataframe(df_bl, width="stretch", hide_index=True, height=300)

        _div()
        _sec("Télécharger / Envoyer un BL")
        bl_map = {b["numero"]: b["id"] for b in bls}
        sel_bl = st.selectbox("Sélectionner un BL", ["—"]+list(bl_map.keys()), key="sel_bl_main")

        if sel_bl != "—":
            bl_d = ctrl.get_bon_livraison_by_id(bl_map[sel_bl])
            if bl_d:
                try:
                    from pdf_generator import generer_bl_pdf
                    pdf_bl = generer_bl_pdf(bl_d)
                    col_dl, col_em = st.columns(2)
                    with col_dl:
                        st.download_button("Télécharger PDF BL", data=pdf_bl,
                            file_name=f"BL_{sel_bl}.pdf", mime="application/pdf",
                            width="stretch", key="dl_bl")
                    with col_em:
                        try:
                            from database import SessionLocal
                            from models import BonLivraison as BLM
                            _s = SessionLocal()
                            _bl_obj = _s.query(BLM).filter(BLM.id==bl_map[sel_bl]).first()
                            _e = _bl_obj.devis.client.email if _bl_obj and _bl_obj.devis and _bl_obj.devis.client else ""
                            _n = _bl_obj.devis.client.nom_complet if _bl_obj and _bl_obj.devis and _bl_obj.devis.client else ""
                            _s.close()
                            if _e:
                                if st.button("Envoyer par Email", key="btn_email_bl_list",
                                             type="secondary", width="stretch"):
                                    from email_service import email_bon_livraison
                                    ok, msg = email_bon_livraison(_n, _e, sel_bl,
                                        bl_d.get("lieu_livraison",""), "", pdf_bl)
                                    if ok: st.success(f"✅ BL envoyé à {_e}")
                                    else:  st.error(f"Erreur : {msg}")
                                st.caption(f"→ {_e}")
                            else:
                                st.warning("⚠️ Email client manquant")
                        except Exception: pass
                except Exception as e:
                    st.error(str(e))

    with tab_creer:
        # ── Pré-remplir depuis commande si venu de la page Commandes ─────
        cmd_prefill = st.session_state.get("bl_from_cmd", None)

        commandes = ctrl.get_all_commandes()
        cmds_ok   = [c for c in commandes if c.get("statut") in ["en_attente","confirmee"]]

        if not cmds_ok:
            _warn("Aucune commande confirmée disponible. Confirmez d'abord une commande.")

        _sec("Sélectionner la commande")
        cmd_opts = {f"{c['numero']} — {c['client']} ({c.get('date_debut','').strftime('%d/%m/%Y') if c.get('date_debut') else ''} → {c.get('date_fin','').strftime('%d/%m/%Y') if c.get('date_fin') else ''})": c
                    for c in cmds_ok}

        # Auto-select if coming from commandes page
        default_idx = 0
        if cmd_prefill:
            for i, key in enumerate(cmd_opts.keys()):
                if cmd_prefill.get("numero","") in key:
                    default_idx = i
                    break

        sel_cmd_bl = st.selectbox("Commande *", list(cmd_opts.keys()),
                                   index=default_idx, key="bl_cmd_sel")
        cmd_sel = cmd_opts.get(sel_cmd_bl) if cmd_opts else None
        if not cmd_sel: cmd_sel = next(iter(cmd_opts.values())) if cmd_opts else {}

        # Afficher détails de la commande sélectionnée
        engins_str = ""
        if cmd_sel.get("engins"):
            engins_str = ", ".join([
                f"{e['nom']} (x{e['quantite']})" if isinstance(e,dict) else str(e)
                for e in cmd_sel["engins"]])

        st.markdown(f"""
        <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;
                    padding:14px;margin-bottom:16px">
            <div style="font-size:13px;font-weight:600;color:#1D4ED8">
                Informations récupérées de la commande {cmd_sel.get('numero','')}
            </div>
            <div style="font-size:12px;color:#1E40AF;margin-top:6px">
                Client : <b>{cmd_sel.get('client','')}</b><br>
                Période : {cmd_sel.get('date_debut','').strftime('%d/%m/%Y') if cmd_sel.get('date_debut') else '—'}
                → {cmd_sel.get('date_fin','').strftime('%d/%m/%Y') if cmd_sel.get('date_fin') else '—'}
                ({cmd_sel.get('duree_jours',0)} jours)<br>
                Engins : {engins_str or '—'}
            </div>
        </div>""", unsafe_allow_html=True)

        _sec("Informations du bon de livraison")
        lieu = st.text_input("Lieu de livraison", placeholder="Chantier, adresse…", key="bl_lieu")
        obs  = st.text_area("Observations", placeholder="Conditions de livraison…", key="bl_obs")

        if st.button("Créer le Bon de Livraison", type="primary",
                      width="stretch", key="bl_create"):
            try:
                # Create BL linked to the commande's devis
                devis_id = cmd_sel.get("devis_id")
                if not devis_id:
                    st.error("Cette commande n'est pas liée à un devis. Vérifiez le processus.")
                    return

                bl_id, bl_num = ctrl.create_bon_livraison(devis_id, lieu, obs)
                ctrl.update_statut_engin_apres_livraison(bl_id)

                # Forcer statut BL → "en_cours" dès la création
                try:
                    from database import SessionLocal as SL_bl
                    from models import BonLivraison as BLM_cr
                    _s_cr = SL_bl()
                    _bl_cr = _s_cr.query(BLM_cr).filter(BLM_cr.id == bl_id).first()
                    if _bl_cr:
                        _bl_cr.statut = "en_cours"
                        _s_cr.commit()
                    _s_cr.close()
                except Exception:
                    pass

                # Update quantite_louee for each engin (sans changer statut commande)
                from database import SessionLocal
                from models import Commande as CmdModel, Engin as EnginM
                _s2 = SessionLocal()
                _c2 = _s2.query(CmdModel).filter(CmdModel.id==cmd_sel["id"]).first()
                if _c2:
                    for ligne in _c2.lignes:
                        eng = _s2.query(EnginM).filter(EnginM.id==ligne.engin_id).first()
                        if eng:
                            eng.quantite_louee = min(
                                (eng.quantite_louee or 0) + int(ligne.quantite or 1),
                                eng.quantite_totale or 1)
                            dispo = max(0, (eng.quantite_totale or 1)
                                       - (eng.quantite_louee or 0)
                                       - (eng.quantite_maintenance or 0))
                            eng.statut = "disponible" if dispo > 0 else "loue"
                _s2.commit(); _s2.close()

                st.success(f"✅ BL **{bl_num}** créé avec succès !")
                st.balloons()

                # PDF
                bl_d = ctrl.get_bon_livraison_by_id(bl_id)
                from pdf_generator import generer_bl_pdf
                pdf = generer_bl_pdf(bl_d)
                st.download_button("Télécharger BL PDF", data=pdf,
                    file_name=f"BL_{bl_num}.pdf", mime="application/pdf",
                    key="new_bl_dl")

                # Email
                try:
                    from database import SessionLocal as SL2
                    from models import BonLivraison as BLM2
                    _s3 = SL2()
                    _bl3 = _s3.query(BLM2).filter(BLM2.id==bl_id).first()
                    _e3 = _bl3.devis.client.email if _bl3 and _bl3.devis and _bl3.devis.client else ""
                    _n3 = _bl3.devis.client.nom_complet if _bl3 and _bl3.devis and _bl3.devis.client else ""
                    _s3.close()
                    if _e3:
                        if st.button(f"Envoyer BL par Email ({_e3})",
                                     key="btn_email_bl_new", type="secondary"):
                            from email_service import email_bon_livraison
                            ok2, msg2 = email_bon_livraison(_n3, _e3, bl_num, lieu, "", pdf)
                            if ok2: st.success(f"✅ BL envoyé à {_e3}")
                            else:   st.error(f"Erreur : {msg2}")
                except Exception: pass

                # Clear prefill
                if "bl_from_cmd" in st.session_state:
                    del st.session_state["bl_from_cmd"]
                st.rerun()

            except Exception as ex:
                st.error(f"Erreur : {ex}")