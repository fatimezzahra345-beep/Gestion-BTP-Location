"""modules/commandes.py — Commandes avec changement statut + bouton BL | LocationBTP"""
import streamlit as st, pandas as pd
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import controller as ctrl
from modules.ui_helpers import (render_page_header, _sec, _info, _warn,
                                _div, PRIMARY, GREEN, RED, ORANGE, GRAY_400, GRAY_900)

def render():
    render_page_header("📦", "Commandes",
        "Créées automatiquement depuis les devis validés — Gérez les statuts")


    # ── Réinitialisation rapide ───────────────────────────────────────────────
    with st.expander("🗑️ Vider les données de cette page"):
        st.warning("⚠️ Supprime toutes les données de ce tableau. Les tables restent intactes.")
        if st.button("Confirmer la suppression", type="secondary",
                     key="del_commandes_btn"):
            try:
                from database import engine as _e_commandes
                from sqlalchemy import text as _t_commandes
                with _e_commandes.connect() as _c_commandes:
                    _c_commandes.execute(_t_commandes("DELETE FROM commandes"))
                    _c_commandes.commit()
                st.success("✅ Données supprimées. Les tables restent vides.")
                st.rerun()
            except Exception as _ex_commandes:
                st.error(str(_ex_commandes))
    _div()

    commandes = ctrl.get_all_commandes() if hasattr(ctrl,'get_all_commandes') else []

    if not commandes:
        _info("Aucune commande. Transformez un devis validé en commande (Devis → Transformer en Commande).")

    # Filtres
    sf, ss = st.columns([2, 3])
    with sf:
        fil = st.selectbox("Statut", ["Tous","en_attente","confirmee","livree","annulee"], key="cmd_fil")
    with ss:
        search = st.text_input("Rechercher", placeholder="Numéro, client…", key="cmd_search")

    filtres = [c for c in commandes
               if (fil=="Tous" or c.get("statut","")==fil)
               and (not search
                    or search.lower() in c.get("numero","").lower()
                    or search.lower() in c.get("client","").lower())]

    # Compteurs
    t1,t2,t3,t4 = st.columns(4)
    t1.metric("Total", len(commandes))
    t2.metric("En attente", sum(1 for c in commandes if c.get("statut")=="en_attente"))
    t3.metric("Confirmées", sum(1 for c in commandes if c.get("statut")=="confirmee"))
    t4.metric("Livrées",    sum(1 for c in commandes if c.get("statut")=="livree"))

    _div()

    # Tableau
    badge = {"en_attente":"⏳","confirmee":"✅","livree":"🚛","annulee":"❌"}
    df = pd.DataFrame([{
        "N° Commande":   c.get("numero",""),
        "Client":        c.get("client",""),
        "Dévis origine": c.get("devis_numero","—"),
        "Début":         c.get("date_debut").strftime("%d/%m/%Y") if c.get("date_debut") else "—",
        "Fin":           c.get("date_fin").strftime("%d/%m/%Y") if c.get("date_fin") else "—",
        "Durée (j)":     c.get("duree_jours",0),
        "Statut":        badge.get(c.get("statut",""),"") + " " + c.get("statut","").upper(),
    } for c in filtres])
    st.dataframe(df, width="stretch", hide_index=True, height=280)

    _div()
    _sec("Gérer une commande")

    c_map = {f"{c['numero']} — {c['client']} [{c.get('statut','').upper()}]": c
             for c in filtres}
    sel = st.selectbox("Sélectionner une commande", ["—"]+list(c_map.keys()), key="cmd_sel")

    if sel != "—":
        cmd = c_map[sel]
        statut_actuel = cmd.get("statut","en_attente")

        # Détail de la commande
        st.markdown(f"""
        <div style="background:white;border:1px solid #E2E8F0;border-radius:12px;
                    padding:18px;box-shadow:0 1px 4px rgba(0,0,0,.05);margin-bottom:16px">
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
                <div><div style="font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase">N° Commande</div>
                     <div style="font-size:16px;font-weight:700">{cmd.get('numero','')}</div></div>
                <div><div style="font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase">Client</div>
                     <div style="font-size:15px;font-weight:600">{cmd.get('client','')}</div></div>
                <div><div style="font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase">Devis origine</div>
                     <div style="font-size:15px">{cmd.get('devis_numero','—')}</div></div>
                <div><div style="font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase">Début</div>
                     <div style="font-size:15px">{cmd.get('date_debut').strftime('%d/%m/%Y') if cmd.get('date_debut') else '—'}</div></div>
                <div><div style="font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase">Fin</div>
                     <div style="font-size:15px">{cmd.get('date_fin').strftime('%d/%m/%Y') if cmd.get('date_fin') else '—'}</div></div>
                <div><div style="font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase">Durée</div>
                     <div style="font-size:15px">{cmd.get('duree_jours',0)} jour(s)</div></div>
            </div>
        </div>""", unsafe_allow_html=True)

        if cmd.get("engins"):
            engins_str = ", ".join([
                f"{e['nom']} (x{e['quantite']})" if isinstance(e,dict)
                else str(e) for e in cmd["engins"]])
            st.markdown(f"**Engins :** {engins_str}")

        _div()

        # ── Changer le statut ─────────────────────────────────────────────
        _sec("Changer le statut de la commande")
        statuts = ["en_attente","confirmee","livree","annulee"]
        labels  = {"en_attente":"⏳ En attente","confirmee":"✅ Confirmée",
                   "livree":"🚛 Livrée","annulee":"❌ Annulée"}
        idx = statuts.index(statut_actuel) if statut_actuel in statuts else 0

        col_st, col_btn = st.columns([3,1])
        with col_st:
            new_statut = st.selectbox("Nouveau statut",
                [labels[s] for s in statuts], index=idx, key="cmd_new_stat")
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Enregistrer", type="primary", width="stretch", key="cmd_stat_btn"):
                # Map label back to key
                stat_key = statuts[[labels[s] for s in statuts].index(new_statut)]
                try:
                    from database import SessionLocal
                    from models import Commande as CmdModel
                    s = SessionLocal()
                    c_obj = s.query(CmdModel).filter(CmdModel.id==cmd["id"]).first()
                    if c_obj:
                        c_obj.statut = stat_key
                        s.commit()
                    s.close()
                    st.success(f"Statut mis à jour : {new_statut}")
                    st.rerun()
                except Exception as ex:
                    st.error(str(ex))

        _div()

        # ── Bouton Transformer en Bon de Livraison ────────────────────────
        _sec("Créer un Bon de Livraison depuis cette commande")
        if statut_actuel in ["confirmee","en_attente"]:
            if st.button("🚚 Transformer en Bon de Livraison",
                          type="primary", width="stretch", key="cmd_to_bl"):
                # Store command info in session state for BL page
                st.session_state["bl_from_cmd"] = cmd
                st.session_state["bl_cmd_id"]   = cmd["id"]
                st.success(f"Commande {cmd['numero']} prête pour le BL. "
                           f"Allez dans **Bons de Livraison** pour finaliser.")
                st.info("➡️ Naviguez vers **Bons de Livraison** — la commande est pré-remplie.")
        else:
            st.info(f"Cette commande est **{statut_actuel}** — BL déjà créé ou annulé.")