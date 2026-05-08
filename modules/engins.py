"""pages/engins.py — Parc d'Engins avec gestion des quantités | LocationBTP"""
import streamlit as st, pandas as pd, os, base64
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import controller as ctrl
from modules.ui_helpers import (render_page_header, _sec, _info, _warn,
                                _div, PRIMARY, GREEN, RED, ORANGE, PURPLE,
                                GRAY_400, GRAY_900)


def _get_uploads_dir():
    d = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    os.makedirs(d, exist_ok=True);
    return d


def _sauvegarder_photo(fichier, matricule):
    import time
    ext = fichier.name.rsplit(".", 1)[-1].lower()
    nom = f"{matricule}_{int(time.time())}.{ext}"
    path = os.path.join(_get_uploads_dir(), nom)
    with open(path, "wb") as f: f.write(fichier.getbuffer())
    return path


def _photo_b64(path, height=160):
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = path.rsplit(".", 1)[-1].lower()
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "jpeg")
        return (f'<div style="height:{height}px;overflow:hidden">'
                f'<img src="data:image/{mime};base64,{b64}" '
                f'style="width:100%;height:{height}px;object-fit:cover;display:block"/></div>')
    except Exception:
        return (f'<div style="height:{height}px;background:#F1F5F9;display:flex;'
                f'align-items:center;justify-content:center;font-size:32px">🚧</div>')


def render():
    render_page_header("🚛", "Parc d'Engins",
                       "Gestion du parc matériel — quantités et disponibilités")

    # Synchronisation automatique : libère les engins dont la commande est terminée
    try:
        ctrl.sync_engins_depuis_commandes()
    except Exception:
        pass

    tab_liste, tab_ajouter, tab_modifier = st.tabs([
        "Liste des Engins", "Ajouter un Engin", "Modifier un Engin"
    ])

    # ── LISTE ─────────────────────────────────────────────────────────────────
    with tab_liste:
        engins = ctrl.get_all_engins()
        if not engins:
            _info("Aucun engin. Ajoutez-en via l'onglet Ajouter.")
            return

        filtre = st.selectbox("Filtrer par statut",
                              ["Tous", "disponible", "loue"],
                              key="eng_filtre")
        engins_filtres = [e for e in engins
                          if filtre == "Tous" or e.statut == filtre]

        # Compteurs — auto-calculés depuis les quantités réelles
        dispos = sum(
            max(0, (e.quantite_totale or 1) - (e.quantite_louee or 0) - (e.quantite_maintenance or 0)) for e in engins)
        loues = sum(e.quantite_louee or 0 for e in engins)
        total_u = sum(e.quantite_totale or 1 for e in engins)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total unités", total_u)
        c2.metric("Disponibles", dispos)
        c3.metric("Loués", loues)

        _div()

        # Grille de cartes
        cols = st.columns(3)
        for i, engin in enumerate(engins_filtres):
            dispo = max(0, (engin.quantite_totale or 1)
                        - (engin.quantite_louee or 0)
                        - (engin.quantite_maintenance or 0))
            # Badge couleur selon disponibilité
            if dispo > 0:
                badge_bg, badge_fg = "#ECFDF5", "#065F46"
                badge_lbl = f"{dispo} DISPO"
            elif (engin.quantite_louee or 0) > 0:
                badge_bg, badge_fg = "#EFF6FF", "#1D4ED8"
                badge_lbl = f"{engin.quantite_louee} LOUÉ(S)"
            else:
                badge_bg, badge_fg = "#FEF2F2", "#991B1B"
                badge_lbl = "MAINTENANCE"

            # Generate photo HTML safely
            _ph = engin.photo_path or ""
            if _ph and os.path.exists(_ph):
                try:
                    with open(_ph, "rb") as _pf:
                        _pb = base64.b64encode(_pf.read()).decode()
                    _pxt = _ph.rsplit(".", 1)[-1].lower()
                    _pmi = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(_pxt, "jpeg")
                    photo_html = (f'<div style="height:160px;overflow:hidden;flex-shrink:0">'
                                  f'<img src="data:image/{_pmi};base64,{_pb}" '
                                  f'style="width:100%;height:160px;object-fit:cover;display:block"/>'
                                  f'</div>')
                except Exception:
                    photo_html = ('<div style="height:160px;background:#F1F5F9;'
                                  'display:flex;align-items:center;justify-content:center;'
                                  'font-size:32px">🚧</div>')
            else:
                photo_html = ('<div style="height:160px;background:#F8FAFC;'
                              'display:flex;align-items:center;justify-content:center;'
                              'font-size:40px">🚛</div>')

            with cols[i % 3]:
                # Build card HTML as plain string concatenation (no f-string conflict)
                _type_str = str(engin.type_engin or "")
                _qty_str = f"  |  Qté: {engin.quantite_totale or 1}"
                _loue_str = f"  |  {engin.quantite_louee or 0} loué(s)" if (engin.quantite_louee or 0) > 0 else ""
                _maint_str = f"  |  {engin.quantite_maintenance or 0} maint." if (
                                                                                             engin.quantite_maintenance or 0) > 0 else ""
                _prix_str = f"{engin.prix_journalier:,.0f}"

                _card_top = (
                    '<div style="background:white;border:1px solid #E2E8F0;border-radius:12px;'
                    'overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.06);margin-bottom:12px">'
                )
                _card_info = (
                    f'<div style="padding:14px 16px">'
                    f'<div style="display:flex;justify-content:space-between;'
                    f'align-items:flex-start;gap:8px;margin-bottom:8px">'
                    f'<div>'
                    f'<div style="font-size:13.5px;font-weight:700;color:{GRAY_900}">{engin.nom}</div>'
                    f'<div style="font-size:11.5px;color:{GRAY_400}">{engin.matricule}</div>'
                    f'</div>'
                    f'<span style="background:{badge_bg};color:{badge_fg};padding:3px 10px;'
                    f'border-radius:20px;font-size:10px;font-weight:700;white-space:nowrap">{badge_lbl}</span>'
                    f'</div>'
                    f'<div style="font-size:19px;font-weight:800;color:{PRIMARY};margin-bottom:4px">'
                    f'{_prix_str}'
                    f'<span style="font-size:12px;font-weight:400;color:{GRAY_400}"> MAD / jr</span>'
                    f'</div>'
                    f'<div style="font-size:11.5px;color:{GRAY_400}">'
                    f'{_type_str}{_qty_str}{_loue_str}{_maint_str}'
                    f'</div></div></div>'
                )
                st.markdown(_card_top + photo_html + _card_info, unsafe_allow_html=True)

                # Bouton supprimer seulement (statut géré automatiquement)
                if st.button("Suppr.", key=f"del_{engin.id}", type="secondary"):
                    ctrl.delete_engin(engin.id);
                    st.rerun()

    # ── AJOUTER ───────────────────────────────────────────────────────────────
    with tab_ajouter:
        _sec("Ajouter un nouvel engin au parc")
        with st.form("form_eng_new"):
            a1, a2 = st.columns(2)
            with a1:
                nom_e = st.text_input("Nom de l'engin *", placeholder="ex: CAMION 8X4")
                type_e = st.text_input("Type", placeholder="ex: Camion, Pelle…")
                matricule = st.text_input("Matricule *", placeholder="ex: CAM-8X4-001")
            with a2:
                prix_jr = st.number_input("Prix journalier (MAD) *",
                                          min_value=0.0, value=1500.0, step=50.0)
                quantite = st.number_input("Quantité dans le parc",
                                           min_value=1, max_value=99, value=1, step=1)
            desc_e = st.text_area("Description", placeholder="Caractéristiques, état…")
            if st.form_submit_button("Enregistrer l'engin", type="primary", width="stretch"):
                if not nom_e.strip() or not matricule.strip():
                    st.error("Le nom et le matricule sont obligatoires.")
                else:
                    try:
                        ctrl.create_engin(nom=nom_e, type_engin=type_e,
                                          matricule=matricule, prix_journalier=prix_jr,
                                          statut="disponible", description=desc_e,
                                          quantite_totale=int(quantite))
                        st.success(f"Engin {nom_e} ajouté !");
                        st.rerun()
                    except Exception as ex:
                        st.error(str(ex))

        # Upload photo
        _div();
        _sec("Ajouter une photo à un engin")
        engins_f = ctrl.get_all_engins()
        if engins_f:
            ph_map = {f"{e.nom} ({e.matricule})": e for e in engins_f}
            ph_sel = st.selectbox("Sélectionner l'engin", list(ph_map.keys()), key="ph_add_sel")
            ph_file = st.file_uploader("Photo", type=["jpg", "jpeg", "png", "webp"],
                                       key="ph_add_up", label_visibility="collapsed")
            if ph_file:
                st.image(ph_file, width=200)
                if st.button("Enregistrer la photo", key="ph_add_save", type="primary"):
                    try:
                        chemin = _sauvegarder_photo(ph_file, ph_map[ph_sel].matricule)
                        ctrl.update_engin(ph_map[ph_sel].id, photo_path=chemin)
                        st.success("Photo enregistrée !");
                        st.rerun()
                    except Exception as ex:
                        st.error(str(ex))

    # ── MODIFIER ──────────────────────────────────────────────────────────────
    with tab_modifier:
        engins_m = ctrl.get_all_engins()
        if not engins_m:
            _info("Aucun engin à modifier.");
            return
        eng_map = {f"{e.nom} ({e.matricule})": e for e in engins_m}
        sel_m = st.selectbox("Sélectionner l'engin", list(eng_map.keys()), key="mod_eng_sel")
        engin_m = eng_map[sel_m]

        # ── Photo ─────────────────────────────────────────────────────────
        _sec("Photo de l'engin")
        col_ph_cur, col_ph_new = st.columns(2)
        with col_ph_cur:
            st.markdown("**Photo actuelle**")
            if engin_m.photo_path and os.path.exists(engin_m.photo_path or ""):
                _ph_html = _photo_b64(engin_m.photo_path, 150)
                st.markdown(_ph_html, unsafe_allow_html=True)
                st.caption(os.path.basename(engin_m.photo_path))
                if st.button("Supprimer la photo", key="mod_ph_del_btn", type="secondary"):
                    try:
                        if os.path.exists(engin_m.photo_path): os.remove(engin_m.photo_path)
                        ctrl.update_engin(engin_m.id, photo_path=None)
                        st.success("Photo supprimée.");
                        st.rerun()
                    except Exception as ex:
                        st.error(str(ex))
            else:
                st.markdown('<div style="height:120px;background:#F8FAFC;border:2px dashed #E2E8F0;'
                            'border-radius:10px;display:flex;align-items:center;'
                            'justify-content:center;color:#94A3B8;font-size:13px">'
                            'Aucune photo</div>', unsafe_allow_html=True)
        with col_ph_new:
            st.markdown("**Ajouter / Remplacer**")
            new_ph = st.file_uploader("Nouvelle photo",
                                      type=["jpg", "jpeg", "png", "webp"],
                                      key=f"mod_ph_up_{engin_m.id}",
                                      label_visibility="collapsed")
            if new_ph:
                st.image(new_ph, width=200)
                if st.button("Enregistrer la photo", key="mod_ph_save_btn", type="primary"):
                    try:
                        ch = _sauvegarder_photo(new_ph, engin_m.matricule)
                        ctrl.update_engin(engin_m.id, photo_path=ch)
                        st.success("✅ Photo mise à jour !");
                        st.rerun()
                    except Exception as ex:
                        st.error(str(ex))
        _div()

        # Photo actuelle (legacy check — kept for form below)
        if engin_m.photo_path and os.path.exists(engin_m.photo_path):
            st.markdown(_photo_b64(engin_m.photo_path, 150), unsafe_allow_html=True)
            col_ph1, col_ph2 = st.columns(2)
            with col_ph1:
                new_ph = st.file_uploader("Remplacer la photo",
                                          type=["jpg", "jpeg", "png", "webp"],
                                          key=f"mod_ph_{engin_m.id}", label_visibility="collapsed")
                if new_ph and st.button("Enregistrer la photo", key="mod_ph_save"):
                    ch = _sauvegarder_photo(new_ph, engin_m.matricule)
                    ctrl.update_engin(engin_m.id, photo_path=ch)
                    st.success("Photo mise à jour !");
                    st.rerun()
            with col_ph2:
                if st.button("Supprimer la photo", key="mod_ph_del"):
                    if os.path.exists(engin_m.photo_path): os.remove(engin_m.photo_path)
                    ctrl.update_engin(engin_m.id, photo_path=None)
                    st.success("Photo supprimée.");
                    st.rerun()

        _div()
        with st.form(f"form_mod_eng_{engin_m.id}"):
            b1, b2 = st.columns(2)
            with b1:
                new_nom = st.text_input("Nom *", value=engin_m.nom)
                new_type = st.text_input("Type", value=engin_m.type_engin or "")
                new_mat = st.text_input("Matricule *", value=engin_m.matricule)
            with b2:
                new_prix = st.number_input("Prix journalier (MAD)",
                                           min_value=0.0, value=float(engin_m.prix_journalier or 0), step=50.0)
                new_qty = st.number_input("Quantité totale",
                                          min_value=1, max_value=99, value=int(engin_m.quantite_totale or 1))
            new_desc = st.text_area("Description", value=engin_m.description or "")

            # Infos calculées automatiquement (lecture seule)
            new_loue = engin_m.quantite_louee or 0
            new_maint = engin_m.quantite_maintenance or 0
            dispo_calc = max(0, int(new_qty) - int(new_loue) - int(new_maint))
            st.info(f"Quantité disponible : **{dispo_calc}** / {int(new_qty)} total | Loués : **{new_loue}** (mis à jour automatiquement)")

            if st.form_submit_button("Enregistrer les modifications",
                                     type="primary", width="stretch"):
                if not new_nom.strip() or not new_mat.strip():
                    st.error("Nom et matricule obligatoires.")
                elif int(new_loue) + int(new_maint) > int(new_qty):
                    st.error("Loués + Maintenance ne peut pas dépasser la quantité totale.")
                else:
                    # Déterminer statut automatique
                    dispo = int(new_qty) - int(new_loue) - int(new_maint)
                    new_stat = "disponible" if dispo > 0 else ("loue" if int(new_loue) > 0 else "maintenance")
                    ctrl.update_engin(engin_m.id, nom=new_nom, type_engin=new_type,
                                      matricule=new_mat, prix_journalier=new_prix,
                                      description=new_desc, quantite_totale=int(new_qty),
                                      quantite_louee=int(new_loue),
                                      quantite_maintenance=int(new_maint), statut=new_stat)
                    st.success(f"Engin mis à jour ! Statut auto : {new_stat}");
                    st.rerun()