import streamlit as st
import sys, os, base64
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="LocationBTP — Wassime BTP",
    page_icon="🏗️", layout="wide",
    initial_sidebar_state="expanded",
)

from models import init_db; init_db()
from views_theme import LUXURY_CSS
st.markdown(LUXURY_CSS, unsafe_allow_html=True)
import controller as ctrl

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.authenticated:
    st.markdown('<style>.stApp{background:#FFFFFF!important}.main .block-container{padding:0!important;max-width:100%!important}</style>', unsafe_allow_html=True)
    _, col_c, _ = st.columns([1, 1.1, 1])
    with col_c:
        st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
        logo_path2 = os.path.join(os.path.dirname(__file__), "logo_wassime_main.jpeg")
        if os.path.exists(logo_path2):
            with open(logo_path2,"rb") as lf2: lb64=base64.b64encode(lf2.read()).decode()
            st.markdown(f'<div style="text-align:center;margin-bottom:28px"><img src="data:image/jpeg;base64,{lb64}" style="height:180px;object-fit:contain"/></div>', unsafe_allow_html=True)
        st.markdown('<div style="background:white;border:1px solid #DDE3EA;border-radius:10px;padding:28px 32px;box-shadow:0 2px 12px rgba(0,0,0,.06)"><div style="font-size:22px;font-weight:800;color:#0A2540;margin-bottom:4px">Se connecter</div><div style="font-size:14px;color:#64748B;margin-bottom:20px">Accédez à votre espace Wassime BTP</div>', unsafe_allow_html=True)
        username = st.text_input("Nom d'utilisateur", placeholder="Admin", key="login_user")
        password = st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe", key="login_pass")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button("Se connecter", width="stretch", type="primary"):
            if ctrl.verifier_mot_de_passe(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Bouton "Mot de passe oublié ?" — toggle
        if "show_rec" not in st.session_state:
            st.session_state.show_rec = False

        col_r = st.columns([1,2,1])
        with col_r[1]:
            lbl = "✖ Annuler" if st.session_state.show_rec else "Mot de passe oublié ?"
            if st.button(lbl, key="btn_toggle_rec", use_container_width=True):
                st.session_state.show_rec = not st.session_state.show_rec
                st.rerun()

        if st.session_state.show_rec:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            recovery_email = st.text_input("Votre email",
                                            placeholder="votre@email.com",
                                            key="recovery_email")
            if st.button("Envoyer le mot de passe", key="btn_recovery",
                         type="primary", width="stretch"):
                if not recovery_email.strip():
                    st.error("Entrez votre adresse email.")
                else:
                    try:
                        from email_service import get_email_config, envoyer_email
                        _ecfg = get_email_config()
                        if not _ecfg or not _ecfg.get("active"):
                            st.error("Email non configuré. Allez dans Paramètres → Configuration Email.")
                        elif recovery_email.strip() != _ecfg.get("email_from",""):
                            st.error("Email non reconnu. Entrez l'email configuré dans Paramètres.")
                        else:
                            ok, msg = envoyer_email(
                                destinataire=recovery_email.strip(),
                                sujet="🔑 Récupération mot de passe — LocationBTP Wassime BTP",
                                corps_html=f"""
                                <div style="font-family:sans-serif;padding:24px;max-width:500px">
                                    <h2 style="color:#1B2A4A">Wassime BTP — LocationBTP</h2>
                                    <p>Vos identifiants de connexion :</p>
                                    <div style="background:#F8FAFC;border-radius:10px;
                                                padding:20px;margin:16px 0;
                                                border-left:4px solid #2563EB">
                                        <p><b>Nom d'utilisateur :</b> Admin</p>
                                        <p><b>Mot de passe :</b> Wassime2026</p>
                                        <p style="font-size:12px;color:#94A3B8">
                                        Si vous avez changé le mot de passe dans Paramètres,
                                        utilisez le nouveau mot de passe.</p>
                                    </div>
                                    <p style="color:#94A3B8;font-size:12px">
                                        LocationBTP — Wassime BTP, Marrakech © 2026</p>
                                </div>""")
                            if ok:
                                st.success(f"✅ Email envoyé à {recovery_email.strip()} !")
                            else:
                                st.error(f"Erreur : {msg}")
                    except Exception as ex:
                        st.error(f"Erreur : {ex}")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;margin-top:20px;font-size:12px;color:#94A3B8">Wassime BTP · Marrakech © 2026</div>', unsafe_allow_html=True)
    st.stop()

# SIDEBAR
logo_path = os.path.join(os.path.dirname(__file__), "logo_wassime_main.jpeg")
logo_src  = ""
if os.path.exists(logo_path):
    with open(logo_path,"rb") as lf: logo_src="data:image/jpeg;base64,"+base64.b64encode(lf.read()).decode()

with st.sidebar:
    st.markdown(f'<div style="padding:16px 16px 14px;border-bottom:1px solid #F1F5F9"><div style="display:flex;align-items:center;gap:10px"><img src="{logo_src}" style="height:38px;width:38px;object-fit:contain;border-radius:8px"/><div><div style="font-size:14px;font-weight:800;color:#0F172A">LocationBTP</div><div style="font-size:11px;color:#94A3B8">Wassime BTP</div></div></div></div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:12px 16px;margin:8px 12px;background:#F8FAFC;border-radius:10px;border:1px solid #E2E8F0"><div style="display:flex;align-items:center;gap:8px"><div style="width:34px;height:34px;background:#EFF6FF;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:#2563EB">MS</div><div><div style="font-size:13px;font-weight:700;color:#1E293B">Mr. Slimane</div><div style="font-size:11px;color:#94A3B8">Directeur Général</div></div></div></div>', unsafe_allow_html=True)

    NAV_ITEMS = [
        ("Clients",             "clients"),
        ("Parc d'Engins",       "engins"),
        ("Devis",               "devis"),
        ("Commandes",           "commandes"),
        ("Bons de Livraison",   "livraison"),
        ("Attachements",        "attachements"),
        ("Facturation",         "facturation"),
        ("Suivi des Paiements", "paiements"),
        ("Attestations Retard", "attestations"),
        ("Calendrier",          "calendrier"),
        ("Tableau de Bord",     "dashboard"),
        ("Paramètres",          "admin"),
    ]

    labels = [x[0] for x in NAV_ITEMS]
    keys   = [x[1] for x in NAV_ITEMS]
    page   = st.radio("nav", labels, label_visibility="collapsed")
    page_key = keys[labels.index(page)]

    st.markdown("<hr style='border:none;border-top:1px solid #F1F5F9;margin:8px 12px'>", unsafe_allow_html=True)
    if st.button("Se déconnecter", width="stretch", key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
    st.markdown('<div style="padding:12px 16px 8px;text-align:center"><div style="font-size:11px;color:#CBD5E1">LocationBTP v3.0</div></div>', unsafe_allow_html=True)

# ROUTING
if page_key == "clients":
    from modules.clients import render; render()
elif page_key == "engins":
    from modules.engins import render; render()
elif page_key == "devis":
    from modules.devis import render; render()
elif page_key == "commandes":
    from modules.commandes import render; render()
elif page_key == "livraison":
    from modules.livraison import render; render()
elif page_key == "attachements":
    from modules.attachements import render; render()
elif page_key == "facturation":
    from modules.facturation import render; render()
elif page_key == "paiements":
    from modules.paiements import render; render()
elif page_key == "attestations":
    from modules.attestations import render; render()
elif page_key == "dashboard":
    from modules.dashboard import render; render()
elif page_key == "calendrier":
    from modules.calendrier import render; render()

elif page_key == "admin":
    from modules.parametres import render; render()