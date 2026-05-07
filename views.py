"""
views.py — LocationBTP | Design SaaS Premium
Interface blanche, épurée, professionnelle — App Store Level
"""
import streamlit as st
from datetime import date, timedelta
import pandas as pd
import os, sys

# ── Constantes couleurs (alignées avec le CSS) ────────────────────────────────
PRIMARY = "#2563EB"
GRAY_900 = "#0F172A"
GRAY_700 = "#334155"
GRAY_500 = "#64748B"
GRAY_400 = "#94A3B8"
GRAY_200 = "#E2E8F0"
GREEN = "#10B981"
RED = "#EF4444"
ORANGE = "#F59E0B"
PURPLE = "#8B5CF6"
# Aliases for legacy code compatibility
BRUN = "#1E3A5F"
OR = "#2563EB"
VERT = "#10B981"
ROUGE = "#EF4444"


def apply_styles():
    from views_theme import LUXURY_CSS
    st.markdown(LUXURY_CSS, unsafe_allow_html=True)


# ── Helpers UI ─────────────────────────────────────────────────────────────────

def render_page_header(icon: str, title: str, subtitle: str = ""):
    sub_html = f'<div class="ph-sub">{subtitle}</div>' if subtitle else ''
    st.markdown(f"""
    <div class="ph-wrap">
        <div class="ph-left">
            <div class="ph-icon">{icon}</div>
            <div>
                <div class="ph-title">{title}</div>
                {sub_html}
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


def _lux_header(icon, title, subtitle=""):
    render_page_header(icon, title, subtitle)


def _sec(txt):
    st.markdown(f'<div class="sec-title">{txt}</div>', unsafe_allow_html=True)


def _div():
    st.markdown('<div class="lux-divider"></div>', unsafe_allow_html=True)


def _info(txt):
    st.markdown(f'<div class="box-info">ℹ️ {txt}</div>', unsafe_allow_html=True)


def _warn(txt):
    st.markdown(f'<div class="box-warn">⚠️ {txt}</div>', unsafe_allow_html=True)


def _ok(txt):
    st.markdown(f'<div class="box-success">✅ {txt}</div>', unsafe_allow_html=True)


def _err(txt):
    st.markdown(f'<div class="box-danger">❌ {txt}</div>', unsafe_allow_html=True)


def format_mad(v):
    return f"{v:,.2f} MAD"


def _badge_html(statut):
    MAP = {
        "disponible": ("b-green", "🟢"),
        "loue": ("b-blue", "🔵"),
        "maintenance": ("b-orange", "🔧"),
        "commande": ("b-purple", "📦"),
        "paye": ("b-green", "✅"),
        "en_attente": ("b-orange", "⏳"),
        "retard": ("b-red", "🔴"),
        "brouillon": ("b-gray", "📝"),
        "valide": ("b-green", "✅"),
        "annule": ("b-red", "❌"),
        "confirmee": ("b-green", "✅"),
        "partiel": ("b-blue", "🔵"),
        "facture": ("b-green", "🧾"),
        "emis": ("b-gray", "📋"),
        "signe": ("b-green", "✅"),
        "livree": ("b-blue", "📦"),
    }
    cls, ico = MAP.get(statut, ("b-gray", "•"))
    lbl = statut.replace("_", " ").upper()
    return f'<span class="badge {cls}">{ico} {lbl}</span>'


def _kpi(col, icon, label, value, sub="", color=PRIMARY, bg="#EFF6FF"):
    with col:
        st.markdown(f"""
        <div class="kpi">
            <div class="kpi-accent" style="background:{color}"></div>
            <div class="kpi-icon" style="background:{bg}">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {f'<div class="kpi-sub">{sub}</div>' if sub else ''}
        </div>""", unsafe_allow_html=True)


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

def render_dashboard():
    import controller as ctrl
    import matplotlib, matplotlib.pyplot as plt
    import matplotlib.ticker as mticker, numpy as np
    from io import BytesIO;
    import base64
    from collections import Counter
    matplotlib.use("Agg")
    plt.rcParams.update({"font.family": "DejaVu Sans"})

    render_page_header("", "Tableau de Bord", "Vue strategique — Wassime BTP")

    stats = ctrl.get_dashboard_stats()
    eng = stats.get("engins", {})
    ca_d = stats.get("ca_mensuel", [])
    ca_total = stats.get("ca_total", 0)
    ca_mois = stats.get("ca_mois", 0)
    creances = stats.get("creances", 0)
    dispo = eng.get("disponibles", 0)
    loues = eng.get("loues", 0)
    maint = eng.get("maintenance", 0)
    total_e = eng.get("total", 0)
    n_devis = stats.get("devis_en_cours", 0)
    n_retard = stats.get("factures_retard", 0)
    taux_enc = (ca_total / (ca_total + creances) * 100) if (ca_total + creances) > 0 else 100
    ca_vals = [d["ca"] for d in ca_d] if len(ca_d) >= 2 else [0] * 6

    # ── Sparkline helper ──────────────────────────────────────────────────────
    def spark(vals, color):
        fig, ax = plt.subplots(figsize=(3, 0.65))
        fig.patch.set_alpha(0);
        ax.set_facecolor("none")
        x = range(len(vals))
        ax.fill_between(x, vals, alpha=0.18, color=color)
        ax.plot(x, vals, color=color, lw=2, solid_capstyle="round")
        ax.set_xlim(0, max(len(vals) - 1, 1));
        ax.axis("off")
        plt.tight_layout(pad=0)
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=90, bbox_inches="tight", transparent=True)
        plt.close();
        buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode()

    # ════════════════════════════════════════════════════════════════════════
    # RANGÉE 1 — 5 KPI cards compactes, même hauteur
    # ════════════════════════════════════════════════════════════════════════
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_data = [
        (c1, "Chiffre d'Affaires", f"{ca_total:,.0f}", "MAD total",
         PRIMARY, spark(ca_vals, PRIMARY)),
        (c2, "CA ce Mois", f"{ca_mois:,.0f}", "MAD / mois",
         GREEN, spark([ca_mois * 0.5, ca_mois * 0.8, ca_mois], GREEN)),
        (c3, "Devis Actifs", str(n_devis), "en cours",
         PURPLE, spark([max(1, n_devis), max(1, n_devis), max(1, n_devis)], PURPLE)),
        (c4, "Retards", str(n_retard), "factures",
         RED, spark([0, n_retard, n_retard], RED)),
        (c5, "Engins Dispos", f"{dispo}/{total_e}", "disponibles",
         GREEN, spark([dispo, dispo, dispo], GREEN)),
    ]
    for col, label, val, sub, color, spk in kpi_data:
        with col:
            st.markdown(f"""
            <div style="background:white;border:1px solid #E2E8F0;border-radius:12px;
                        padding:16px 16px 12px;box-shadow:0 1px 4px rgba(0,0,0,.05)">
                <div style="font-size:10.5px;font-weight:600;text-transform:uppercase;
                            letter-spacing:.8px;color:{GRAY_500};margin-bottom:5px">
                    {label}</div>
                <div style="font-size:24px;font-weight:900;color:{GRAY_900};
                            letter-spacing:-0.5px;line-height:1.1">{val}</div>
                <div style="font-size:10.5px;color:{GRAY_400};margin-top:2px">{sub}</div>
                <img src="{spk}" style="width:100%;height:26px;margin-top:8px"/>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # RANGÉE 2 — CA barres (3col) | Parc donut (1col) | Top engins (2col)
    # ════════════════════════════════════════════════════════════════════════
    r2a, r2b, r2c = st.columns([3, 1.4, 1.6])

    # ── Graphique CA ─────────────────────────────────────────────────────────
    with r2a:
        _sec("Evolution du CA — 6 mois")
        with_data = any(v > 0 for v in ca_vals)
        fig_ca, ax_ca = plt.subplots(figsize=(7, 2.9))
        fig_ca.patch.set_facecolor("white");
        ax_ca.set_facecolor("white")
        if with_data:
            mois = [d["mois"] for d in ca_d];
            x = np.arange(len(mois))
            ax_ca.bar(x, ca_vals, width=0.52,
                      color=["#2563EB" if i == len(ca_vals) - 1 else "#BFDBFE" for i in range(len(ca_vals))],
                      edgecolor="none", zorder=3)
            ax_ca.fill_between(x, ca_vals, alpha=0.04, color="#2563EB", zorder=2)
            ax_ca.plot(x, ca_vals, color="#1D4ED8", lw=1.6, marker="o", markersize=3.5,
                       markerfacecolor="white", markeredgecolor="#1D4ED8",
                       markeredgewidth=1.5, zorder=5, alpha=0.7)
            for xi, v in zip(x, ca_vals):
                if v > 0:
                    ax_ca.text(xi, v + max(ca_vals) * 0.028, f"{v:,.0f}",
                               ha="center", va="bottom", fontsize=7, fontweight="700", color="#334155")
            ax_ca.set_xticks(x)
            ax_ca.set_xticklabels(mois, fontsize=8.5, color="#94A3B8")
        else:
            ax_ca.text(0.5, 0.5, "Aucune donnee CA", transform=ax_ca.transAxes,
                       ha="center", va="center", fontsize=11, color="#94A3B8")
        ax_ca.yaxis.set_major_formatter(mticker.FuncFormatter(
            lambda v, _: f"{v / 1000:.0f}k" if v >= 1000 else f"{v:.0f}"))
        ax_ca.tick_params(labelsize=8.5, colors="#94A3B8", length=0)
        ax_ca.grid(axis="y", ls="--", alpha=0.2, color="#E2E8F0");
        ax_ca.set_axisbelow(True)
        for sp in ax_ca.spines.values(): sp.set_visible(False)
        plt.tight_layout(pad=0.5)
        st.markdown(
            '<div style="background:white;border:1px solid #E2E8F0;border-radius:12px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.05)">',
            unsafe_allow_html=True)
        st.pyplot(fig_ca, width='stretch');
        plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Donut parc ───────────────────────────────────────────────────────────
    with r2b:
        _sec("Repartition Parc")
        st.markdown(
            '<div style="background:white;border:1px solid #E2E8F0;border-radius:12px;padding:14px;box-shadow:0 1px 4px rgba(0,0,0,.05);height:100%">',
            unsafe_allow_html=True)
        lp, vp, cp = [], [], []
        for lb, v, c in [("Dispos", dispo, GREEN), ("Loues", loues, PRIMARY), ("Maint.", maint, ORANGE)]:
            if v > 0: lp.append(lb); vp.append(v); cp.append(c)
        if vp:
            fig_d, ax_d = plt.subplots(figsize=(2.3, 2.0))
            fig_d.patch.set_facecolor("white");
            ax_d.set_facecolor("white")
            _, _, autos = ax_d.pie(vp, labels=None, colors=cp, autopct="%1.0f%%",
                                   startangle=90, pctdistance=0.73,
                                   wedgeprops=dict(edgecolor="white", linewidth=2, width=0.55))
            for t in autos: t.set_fontsize(8.5); t.set_fontweight("800"); t.set_color("white")
            ax_d.legend(lp, loc="lower center", ncol=3, fontsize=7.5,
                        frameon=False, bbox_to_anchor=(0.5, -0.14))
            plt.tight_layout(pad=0.2)
            st.pyplot(fig_d, width='stretch');
            plt.close()
        # Mini compteurs sous le donut
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-top:6px">
            <div style="background:#ECFDF5;border-radius:7px;padding:7px;text-align:center">
                <div style="font-size:16px;font-weight:800;color:{GREEN}">{dispo}</div>
                <div style="font-size:9.5px;color:#94A3B8">Dispos</div></div>
            <div style="background:#EFF6FF;border-radius:7px;padding:7px;text-align:center">
                <div style="font-size:16px;font-weight:800;color:{PRIMARY}">{loues}</div>
                <div style="font-size:9.5px;color:#94A3B8">Loues</div></div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Top engins ───────────────────────────────────────────────────────────
    with r2c:
        _sec("Top Engins")
        st.markdown(
            '<div style="background:white;border:1px solid #E2E8F0;border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.05);height:100%">',
            unsafe_allow_html=True)
        try:
            engs = sorted(ctrl.get_engins_disponibilite(), key=lambda e: e["prix_jr"], reverse=True)[:6]
            max_p = max((e["prix_jr"] for e in engs), default=1) or 1
            rc = ["#1D4ED8", "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"]
            for i, e in enumerate(engs):
                pct = int(e["prix_jr"] / max_p * 100)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;
                            padding:9px 14px;border-bottom:1px solid #F8FAFC">
                    <div style="width:20px;height:20px;background:{rc[i]};border-radius:50%;
                        flex-shrink:0;display:flex;align-items:center;justify-content:center;
                        font-size:10px;font-weight:800;color:white">{i + 1}</div>
                    <div style="flex:1;min-width:0">
                        <div style="font-size:11.5px;font-weight:600;color:#0F172A;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
                            {e["nom"]}</div>
                        <div style="background:#F1F5F9;border-radius:2px;height:3px;margin-top:3px">
                            <div style="background:{rc[i]};width:{pct}%;height:100%"></div>
                        </div>
                    </div>
                    <div style="font-size:11px;font-weight:700;color:#0F172A;
                                flex-shrink:0">{e["prix_jr"]:,.0f}</div>
                </div>""", unsafe_allow_html=True)
        except Exception:
            st.markdown('<div style="padding:16px;color:#94A3B8;font-size:12px">Aucune donnee</div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # RANGÉE 3 — Encaissement (2) | Paiements donut (1) | Alertes (1) | Devis (1)
    # ════════════════════════════════════════════════════════════════════════
    r3a, r3b, r3c, r3d = st.columns([2, 1.2, 1, 1])

    # ── Encaissement ─────────────────────────────────────────────────────────
    with r3a:
        _sec("Encaissement & Creances")
        col_b = "#10B981" if taux_enc > 80 else "#F59E0B" if taux_enc > 50 else "#EF4444"
        st.markdown(f"""
        <div style="background:white;border:1px solid #E2E8F0;border-radius:12px;
                    padding:18px;box-shadow:0 1px 4px rgba(0,0,0,.05)">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;
                        margin-bottom:14px">
                <div>
                    <div style="font-size:10.5px;font-weight:600;text-transform:uppercase;
                                letter-spacing:.8px;color:{GRAY_500};margin-bottom:4px">
                        Taux Encaissement</div>
                    <div style="font-size:30px;font-weight:900;color:{col_b};
                                letter-spacing:-1px">{taux_enc:.1f}%</div>
                </div>
                <div style="text-align:right">
                    <div style="font-size:10.5px;font-weight:600;text-transform:uppercase;
                                letter-spacing:.8px;color:{GRAY_500};margin-bottom:4px">
                        Creances</div>
                    <div style="font-size:20px;font-weight:700;
                                color:{"#EF4444" if creances > 0 else GREEN}">
                        {creances:,.0f} MAD</div>
                </div>
            </div>
            <div style="background:#F1F5F9;border-radius:6px;height:8px;overflow:hidden;
                        margin-bottom:6px">
                <div style="background:linear-gradient(90deg,{GREEN},{PRIMARY});
                            width:{min(taux_enc, 100):.0f}%;height:100%;border-radius:6px">
                </div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:11px;
                        color:{GRAY_400}">
                <span>Encaisse : {ca_total:,.0f} MAD</span>
                <span>Total : {ca_total + creances:,.0f} MAD</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Donut paiements ──────────────────────────────────────────────────────
    with r3b:
        _sec("Repartition Paiements")
        st.markdown(
            '<div style="background:white;border:1px solid #E2E8F0;border-radius:12px;padding:14px;box-shadow:0 1px 4px rgba(0,0,0,.05)">',
            unsafe_allow_html=True)
        try:
            all_fac = ctrl.get_all_factures()
            fc = Counter(f["statut"] for f in all_fac)
            pay_l = [];
            pay_v = [];
            pay_c = []
            cmap = {"paye": GREEN, "partiel": PRIMARY, "en_attente": ORANGE, "retard": RED}
            lmap = {"paye": "Paye", "partiel": "Partiel", "en_attente": "Attente", "retard": "Retard"}
            for s, v in fc.items():
                if v > 0: pay_l.append(lmap.get(s, s)); pay_v.append(v); pay_c.append(cmap.get(s, GRAY_400))
            if pay_v:
                fig_p, ax_p = plt.subplots(figsize=(2.2, 1.9))
                fig_p.patch.set_facecolor("white");
                ax_p.set_facecolor("white")
                _, _, autos = ax_p.pie(pay_v, labels=None, colors=pay_c, autopct="%1.0f%%",
                                       startangle=90, pctdistance=0.73,
                                       wedgeprops=dict(edgecolor="white", linewidth=2, width=0.55))
                for t in autos: t.set_fontsize(8); t.set_fontweight("800"); t.set_color("white")
                ax_p.legend(pay_l, loc="lower center", ncol=2, fontsize=7,
                            frameon=False, bbox_to_anchor=(0.5, -0.18))
                plt.tight_layout(pad=0.2)
                st.pyplot(fig_p, width='stretch');
                plt.close()
                payes = fc.get("paye", 0)
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;font-size:11px;margin-top:6px;padding-top:6px;border-top:1px solid #F1F5F9"><span style="color:{GREEN};font-weight:600">{payes} paye(s)</span><span style="color:{GRAY_400}">{len(all_fac)} total</span></div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div style="height:80px;display:flex;align-items:center;justify-content:center;color:#94A3B8;font-size:12px">Aucune facture</div>',
                    unsafe_allow_html=True)
        except Exception:
            st.markdown(
                '<div style="height:80px;display:flex;align-items:center;justify-content:center;color:#94A3B8;font-size:12px">Aucune donnee</div>',
                unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Alertes ──────────────────────────────────────────────────────────────
    with r3c:
        _sec("Alertes")
        alertes = []
        if n_retard > 0: alertes.append((RED, "#FEF2F2", "Retards", f"{n_retard} facture(s)"))
        if creances > 0: alertes.append((ORANGE, "#FFFBEB", "Creances", f"{creances:,.0f} MAD"))
        if loues > 0:    alertes.append((PRIMARY, "#EFF6FF", "En location", f"{loues} engin(s)"))
        if not alertes:
            st.markdown(
                '<div style="background:#ECFDF5;border:1px solid #A7F3D0;border-radius:12px;padding:16px;text-align:center"><div style="font-size:13px;font-weight:600;color:#065F46">Tout en ordre</div><div style="font-size:11px;color:#6EE7B7;margin-top:4px">Aucune alerte</div></div>',
                unsafe_allow_html=True)
        for c, cbg, t, m in alertes:
            st.markdown(
                f'<div style="background:{cbg};border-left:3px solid {c};border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:7px"><div style="font-size:12.5px;font-weight:700;color:#0F172A">{t}</div><div style="font-size:11px;color:{GRAY_500};margin-top:2px">{m}</div></div>',
                unsafe_allow_html=True)

    # ── Derniers devis ───────────────────────────────────────────────────────
    with r3d:
        _sec("Derniers Devis")
        try:
            dl = ctrl.get_all_devis()[:5]
            sc = {"brouillon": GRAY_400, "valide": GREEN, "facture": PRIMARY, "annule": RED}
            st.markdown(
                '<div style="background:white;border:1px solid #E2E8F0;border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.05)">',
                unsafe_allow_html=True)
            if dl:
                for d in dl:
                    c = sc.get(d["statut"], GRAY_400)
                    st.markdown(f'''<div style="padding:9px 14px;border-bottom:1px solid #F8FAFC">
                        <div style="font-size:11.5px;font-weight:700;color:#0F172A">{d["numero"]}</div>
                        <div style="font-size:10.5px;color:{GRAY_400}">{d["client"][:18]}</div>
                        <div style="font-size:11.5px;font-weight:700;color:{c}">{d["montant_ttc"]:,.0f} MAD</div>
                    </div>''', unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div style="padding:16px;color:#94A3B8;font-size:12px;text-align:center">Aucun devis</div>',
                    unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception:
            pass


# ─── HELPERS PHOTO & ENGINS ─────────────────────────────────────────────────

def _get_uploads_dir() -> str:
    """Retourne le dossier uploads/ à côté de views.py, le crée si besoin."""
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    return uploads_dir


def _sauvegarder_photo(fichier_upload, matricule: str) -> str:
    """Sauvegarde le fichier uploadé et retourne son chemin absolu."""
    ext = os.path.splitext(fichier_upload.name)[1].lower()  # .jpg / .png …
    # Nom sûr : pas d'espaces ni de caractères spéciaux
    nom_safe = matricule.replace(" ", "_").replace("/", "-")
    nom_fichier = f"{nom_safe}{ext}"
    chemin = os.path.join(_get_uploads_dir(), nom_fichier)
    with open(chemin, "wb") as f:
        f.write(fichier_upload.getbuffer())
    return chemin


# ─── PAGE ENGINS ────────────────────────────────────────────────────────────────

def render_engins():
    import controller as ctrl

    render_page_header("", "Parc d'Engins", "Gestion et suivi du parc matériel")

    tab_liste, tab_ajouter, tab_modifier = st.tabs([
        "Liste des Engins",
        "Ajouter un Engin",
        "Modifier un Engin",
    ])

    # ── ONGLET LISTE ──────────────────────────────────────────────────────────
    with tab_liste:
        engins_all = ctrl.get_all_engins()
        if not engins_all:
            st.markdown('<div class="lux-info"> Aucun engin dans le parc. Ajoutez-en via l\'onglet Ajouter.</div>',
                        unsafe_allow_html=True)
        else:
            # Filtres
            cf1, cf2 = st.columns([1, 3])
            with cf1:
                filtre_statut = st.selectbox(
                    "Filtrer", ["Tous", "disponible", "loue", "maintenance", "commande"],
                    key="filtre_liste"
                )
            engins_filtres = [e for e in engins_all if filtre_statut == "Tous" or e.statut == filtre_statut]

            st.markdown(f"""
            <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap">
                {" ".join([
                f'<span class="lux-badge badge-{s}">{ico} {n} : {sum(1 for e in engins_all if e.statut == s)}</span>'
                for s, ico, n in [
                    ("disponible", "", "Disponibles"),
                    ("loue", "", "Loués"),
                    ("commande", "", "Commandés"),
                    ("maintenance", "", "Maintenance"),
                ]
            ])}
            </div>
            """, unsafe_allow_html=True)

            # Grille de cartes — 3 colonnes, taille uniforme
            cols = st.columns(3)
            for i, engin in enumerate(engins_filtres):
                with cols[i % 3]:
                    # Badge statut
                    badge_map = {
                        "disponible": ("D1FAE5", "065F46", "🟢"),
                        "loue": ("DBEAFE", "1E3A5F", "🔵"),
                        "maintenance": ("FEF3C7", "78350F", "🔧"),
                        "commande": ("F5EDD8", "4A2C17", "📦"),
                    }
                    bg, fg, ico = badge_map.get(engin.statut, ("F3F4F6", "374151", "⚪"))

                    # Photo
                    photo_ok = engin.photo_path and os.path.exists(engin.photo_path)

                    # Encode photo as base64 for uniform size
                    import base64 as _b64c
                    photo_html = ""
                    if photo_ok:
                        try:
                            with open(engin.photo_path, "rb") as _pf:
                                _pb64 = _b64c.b64encode(_pf.read()).decode()
                            _pext = engin.photo_path.split(".")[-1].lower()
                            _pmime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(_pext, "jpeg")
                            photo_html = f'''<div style="width:100%;height:160px;overflow:hidden;flex-shrink:0">
                                <img src="data:image/{_pmime};base64,{_pb64}"
                                     style="width:100%;height:160px;object-fit:cover;display:block"/>
                            </div>'''
                        except Exception:
                            photo_html = ""
                    if not photo_html:
                        photo_html = '<div style="width:100%;height:160px;flex-shrink:0;background:#F1F5F9;display:flex;align-items:center;justify-content:center;font-size:36px">&#128666;</div>'

                    badge_cls = "b-green" if engin.statut == "disponible" else "b-blue" if engin.statut == "loue" else "b-purple" if engin.statut == "commande" else "b-orange"

                    st.markdown(f"""
                    <div style="background:white;border:1px solid #E2E8F0;border-radius:12px;
                                overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.07);
                                margin-bottom:16px;display:flex;flex-direction:column">
                        {photo_html}
                        <div style="padding:14px 16px;flex:1">
                            <div style="display:flex;justify-content:space-between;
                                        align-items:flex-start;gap:8px;margin-bottom:8px">
                                <div>
                                    <div style="font-size:13.5px;font-weight:700;
                                                color:#0F172A">{engin.nom}</div>
                                    <div style="font-size:11.5px;color:#94A3B8">{engin.matricule}</div>
                                </div>
                                <span class="badge {badge_cls}">{engin.statut.upper()}</span>
                            </div>
                            <div style="font-size:19px;font-weight:800;color:#2563EB;
                                        margin-bottom:4px">
                                {engin.prix_journalier:,.0f}
                                <span style="font-size:12px;font-weight:400;color:#94A3B8">
                                    MAD / jr</span>
                            </div>
                            <div style="font-size:11px;color:#94A3B8">
                                {engin.type_engin or ""}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Contrôles sous la carte
                    ce1, ce2 = st.columns(2)
                    with ce1:
                        statuts = ["disponible", "loue", "maintenance", "commande"]
                        idx = statuts.index(engin.statut) if engin.statut in statuts else 0
                        new_s = st.selectbox("Statut", statuts, index=idx,
                                             key=f"statut_{engin.id}",
                                             label_visibility="collapsed")
                        if new_s != engin.statut:
                            ctrl.update_engin(engin.id, statut=new_s)
                            st.rerun()
                    with ce2:
                        if st.button("Suppr.", key=f"del_{engin.id}",
                                     width='stretch', help="Supprimer cet engin"):
                            ctrl.delete_engin(engin.id)
                            st.rerun()

    # ── ONGLET AJOUTER ────────────────────────────────────────────────────────
    with tab_ajouter:
        _sec("Ajouter un nouvel engin au parc")
        with st.form("form_engin_new"):
            a1, a2 = st.columns(2)
            with a1:
                nom_e = st.text_input("Nom de l'engin *", placeholder="ex: CAMION 8X4")
                type_e = st.text_input("Type", placeholder="ex: Camion, Pelle, Niveleuse…")
                matricule = st.text_input("Matricule *", placeholder="ex: CAM-8X4-001")
            with a2:
                prix_jr = st.number_input("Prix journalier (MAD) *", min_value=0.0,
                                          value=1500.0, step=50.0)
                statut_e = st.selectbox("Statut initial",
                                        ["disponible", "loue", "maintenance", "commande"])
                quantite = st.number_input("Quantité dans le parc", min_value=1,
                                           max_value=99, value=1, step=1)
            desc_e = st.text_area("Description", placeholder="Caractéristiques, état…")
            if st.form_submit_button("Enregistrer l'engin", type="primary", width='stretch'):
                if not nom_e.strip() or not matricule.strip():
                    st.error("Le nom et le matricule sont obligatoires.")
                else:
                    try:
                        ctrl.create_engin(
                            nom=nom_e, type_engin=type_e, matricule=matricule,
                            prix_journalier=prix_jr, statut=statut_e,
                            description=desc_e, quantite_totale=int(quantite)
                        )
                        st.success(f"Engin **{nom_e}** ajouté avec succès !")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Erreur : {ex}")

        # Photo upload APRES création (hors du form pour éviter conflicts)
        st.markdown("---")
        _sec("Ajouter une photo a cet engin")
        _info("Après avoir enregistré l\'engin, sélectionnez-le et uploadez sa photo.")
        engins_fresh = ctrl.get_all_engins()
        if engins_fresh:
            ph_eng_map = {f"{e.nom} ({e.matricule})": e for e in engins_fresh}
            ph_eng_sel_lbl = st.selectbox("Selectionner l\'engin", list(ph_eng_map.keys()),
                                          key="ph_add_eng_sel")
            ph_eng_sel = ph_eng_map[ph_eng_sel_lbl]
            ph_file = st.file_uploader("Photo de l\'engin",
                                       type=["jpg", "jpeg", "png", "webp"],
                                       key="ph_add_upload",
                                       label_visibility="collapsed")
            if ph_file:
                st.image(ph_file, width=200)
                if st.button("Enregistrer la photo", key="ph_add_save", type="primary"):
                    try:
                        chemin = _sauvegarder_photo(ph_file, ph_eng_sel.matricule)
                        ctrl.update_engin(ph_eng_sel.id, photo_path=chemin)
                        st.success(f"Photo ajoutee pour {ph_eng_sel.nom} !")
                        st.rerun()
                    except Exception as ex:
                        st.error(str(ex))

    # ── ONGLET MODIFIER ───────────────────────────────────────────────────────
    with tab_modifier:
        engins_mod = ctrl.get_all_engins()
        if not engins_mod:
            _info("Aucun engin à modifier.")
        else:
            eng_map = {f"{e.nom} ({e.matricule})": e for e in engins_mod}
            sel_mod = st.selectbox("Sélectionner l'engin à modifier",
                                   list(eng_map.keys()), key="mod_eng_sel")
            engin_sel = eng_map[sel_mod]

            # Photo actuelle
            photo_ok_mod = engin_sel.photo_path and os.path.exists(engin_sel.photo_path)
            if photo_ok_mod:
                try:
                    import base64 as _b64m
                    with open(engin_sel.photo_path, "rb") as _mf:
                        _mb64 = _b64m.b64encode(_mf.read()).decode()
                    _mext = engin_sel.photo_path.split(".")[-1].lower()
                    _mmime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(_mext, "jpeg")
                    st.markdown(
                        f'<img src="data:image/{_mmime};base64,{_mb64}" '                        f'style="width:100%;max-height:180px;object-fit:cover;border-radius:10px;margin-bottom:10px"/>',
                        unsafe_allow_html=True)
                    st.caption(os.path.basename(engin_sel.photo_path))
                except Exception:
                    photo_ok_mod = False

            # Upload nouvelle photo
            new_photo = st.file_uploader("Remplacer la photo",
                                         type=["jpg", "jpeg", "png", "webp"],
                                         key=f"mod_ph_{engin_sel.id}_{engin_sel.matricule}",
                                         label_visibility="collapsed")
            if new_photo:
                if st.button("Enregistrer la photo", key="save_ph_mod",
                             type="primary"):
                    try:
                        chemin = _sauvegarder_photo(new_photo, engin_sel.matricule)
                        ctrl.update_engin(engin_sel.id, photo_path=chemin)
                        st.success("Photo enregistrée !")
                        st.rerun()
                    except Exception as ex:
                        st.error(str(ex))

            if photo_ok_mod:
                if st.button("Supprimer la photo actuelle", key="del_ph_mod"):
                    try:
                        if os.path.exists(engin_sel.photo_path):
                            os.remove(engin_sel.photo_path)
                        ctrl.update_engin(engin_sel.id, photo_path=None)
                        st.success("Photo supprimée.")
                        st.rerun()
                    except Exception as ex:
                        st.error(str(ex))

            _div()
            with st.form(f"form_mod_eng_{engin_sel.id}"):
                b1, b2 = st.columns(2)
                with b1:
                    new_nom = st.text_input("Nom *", value=engin_sel.nom)
                    new_type = st.text_input("Type", value=engin_sel.type_engin or "")
                    new_mat = st.text_input("Matricule *", value=engin_sel.matricule)
                with b2:
                    new_prix = st.number_input("Prix journalier (MAD)",
                                               min_value=0.0,
                                               value=float(engin_sel.prix_journalier or 0),
                                               step=50.0)
                    new_stat = st.selectbox("Statut",
                                            ["disponible", "loue", "maintenance", "commande"],
                                            index=["disponible", "loue", "maintenance", "commande"].index(
                                                engin_sel.statut) if engin_sel.statut in
                                                                     ["disponible", "loue", "maintenance",
                                                                      "commande"] else 0)
                    new_qty = st.number_input("Quantite dans le parc",
                                              min_value=1, max_value=99,
                                              value=int(engin_sel.quantite_totale or 1), step=1)
                new_desc = st.text_area("Description", value=engin_sel.description or "")
                if st.form_submit_button("Enregistrer les modifications",
                                         type="primary", width='stretch'):
                    if not new_nom.strip() or not new_mat.strip():
                        st.error("Nom et matricule obligatoires.")
                    else:
                        try:
                            ctrl.update_engin(engin_sel.id,
                                              nom=new_nom, type_engin=new_type, matricule=new_mat,
                                              prix_journalier=new_prix, statut=new_stat,
                                              description=new_desc, quantite_totale=int(new_qty))
                            st.success(f"Engin **{new_nom}** mis à jour !")
                            st.rerun()
                        except Exception as ex:
                            st.error(str(ex))


def render_clients():
    import controller as ctrl
    render_page_header("", "Gestion des Clients", "Base de données clients & historique")

    tab_liste, tab_ajouter, tab_modifier = st.tabs([
        "Tous les Clients", "Nouveau Client", "Modifier un Client"
    ])

    with tab_liste:
        clients = ctrl.get_all_clients()
        if not clients:
            _info(" Aucun client enregistré. Ajoutez votre premier client.")
        else:
            # Recherche
            search = st.text_input(" Rechercher un client…", placeholder="Nom, société, ICE…",
                                   key="client_search")
            filtres = [c for c in clients
                       if not search or search.lower() in c.nom_complet.lower()
                       or (c.ice and search.lower() in c.ice.lower())]

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
                <div class="stat-card" style="border-top-color:{OR};padding:10px 18px;flex:1">
                    <div class="stat-label">Total Clients</div>
                    <div class="stat-value" style="font-size:22px;color:{BRUN}">{len(clients)}</div>
                </div>
                <div class="stat-card" style="border-top-color:{VERT};padding:10px 18px;flex:1">
                    <div class="stat-label">Résultats</div>
                    <div class="stat-value" style="font-size:22px;color:{VERT}">{len(filtres)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Alerte clients sans email
            sans_email = [c for c in clients if not c.email]
            if sans_email:
                noms_sans = " · ".join([c.nom_complet for c in sans_email[:5]])
                plus = "..." if len(sans_email) > 5 else ""
                nb = len(sans_email)
                st.markdown(
                    f'<div style="background:#FFFBEB;border:1px solid #FDE68A;'
                    f'border-left:4px solid #F59E0B;border-radius:0 10px 10px 0;'
                    f'padding:12px 16px;margin-bottom:12px">'
                    f'<div style="font-size:13px;font-weight:700;color:#92400E">'
                    f'⚠️ {nb} client(s) sans email — emails automatiques désactivés</div>'
                    f'<div style="font-size:12px;color:#B45309;margin-top:4px">{noms_sans}{plus}</div>'
                    f'<div style="font-size:11px;color:#92400E;margin-top:4px">'
                    f'→ Allez dans Modifier un Client pour ajouter les emails manquants</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            df = pd.DataFrame([{
                "Nom / Société": c.nom_complet,
                "Téléphone": c.telephone or "—",
                "Email": ("✅ " + c.email) if c.email else "❌ Manquant",
                "ICE": c.ice or "—",
                "Adresse": (c.adresse or "—")[:40],
            } for c in filtres])
            st.dataframe(df, width='stretch', hide_index=True, height=360)

            # Suppression
            _div()
            _sec("Supprimer un client")
            c_ids = {c.nom_complet: c.id for c in clients}
            col_sel, col_btn = st.columns([3, 1])
            with col_sel:
                sel = st.selectbox("Sélectionner", ["—"] + list(c_ids.keys()), key="del_client_sel")
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if sel != "—" and st.button("Supprimer", type="secondary", width='stretch'):
                    ctrl.delete_client(c_ids[sel])
                    st.success(f"✅ Client **{sel}** supprimé.")
                    st.rerun()

    with tab_ajouter:
        _sec(" Informations du nouveau client")
        with st.form("form_client_new"):
            c1, c2 = st.columns(2)
            with c1:
                nom = st.text_input("Nom *", placeholder="Nom de famille")
                prenom = st.text_input("Prénom", placeholder="Prénom")
                societe = st.text_input("Société", placeholder="Raison sociale")
            with c2:
                ice = st.text_input("ICE", placeholder="ex: 001234567000001")
                tel = st.text_input("Téléphone", placeholder="+212 6XX XXX XXX")
                email = st.text_input("Email", placeholder="contact@exemple.ma")
            adresse = st.text_area("Adresse complète", placeholder="Ville, rue, code postal…")
            if st.form_submit_button("Enregistrer", type="primary",
                                     width='stretch'):
                if not nom.strip():
                    st.error("⚠️ Le nom est obligatoire.")
                else:
                    ctrl.create_client(nom=nom, prenom=prenom, societe=societe,
                                       ice=ice, telephone=tel, email=email, adresse=adresse)
                    st.success(f"✅ Client **{societe or nom}** ajouté avec succès !")
                    st.rerun()

    with tab_modifier:
        clients_mod = ctrl.get_all_clients()
        if not clients_mod:
            _info("Aucun client à modifier.")
        else:
            _sec("Modifier les informations d'un client")

            # Highlight clients without email
            sans_email_mod = [c for c in clients_mod if not c.email]
            if sans_email_mod:
                st.markdown(f"""
                <div style="background:#FFFBEB;border:1px solid #FDE68A;
                            border-radius:10px;padding:12px 16px;margin-bottom:12px">
                    <b style="color:#92400E">⚠️ Clients sans email ({len(sans_email_mod)}) :</b>
                    <span style="color:#B45309;font-size:12px">
                        {" · ".join([c.nom_complet for c in sans_email_mod])}
                    </span>
                </div>""", unsafe_allow_html=True)

            cli_map = {f"{c.nom_complet} {'✅' if c.email else '❌ sans email'}": c
                       for c in clients_mod}
            sel_cli = st.selectbox("Sélectionner le client à modifier",
                                   list(cli_map.keys()), key="mod_cli_sel")
            cli_sel = cli_map[sel_cli]

            # Show current email status
            if cli_sel.email:
                st.markdown(f"""<div class="box-success">
                    ✅ Email actuel : <b>{cli_sel.email}</b> — Les emails seront envoyés automatiquement
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""<div class="box-warn">
                    ⚠️ <b>Aucun email renseigné</b> — Les emails automatiques ne seront PAS envoyés à ce client.<br>
                    Ajoutez l'email ci-dessous pour activer l'envoi automatique.
                </div>""", unsafe_allow_html=True)

            with st.form(f"form_mod_cli_{cli_sel.id}"):
                mc1, mc2 = st.columns(2)
                with mc1:
                    new_nom = st.text_input("Nom *", value=cli_sel.nom)
                    new_prenom = st.text_input("Prénom", value=cli_sel.prenom or "")
                    new_societe = st.text_input("Société", value=cli_sel.societe or "")
                with mc2:
                    new_ice = st.text_input("ICE", value=cli_sel.ice or "")
                    new_tel = st.text_input("Téléphone", value=cli_sel.telephone or "")
                    new_email = st.text_input(
                        "Email *" if not cli_sel.email else "Email",
                        value=cli_sel.email or "",
                        placeholder="contact@societe.ma",
                        help="L'email est obligatoire pour l'envoi automatique des documents"
                    )
                new_adresse = st.text_area("Adresse", value=cli_sel.adresse or "")

                if st.form_submit_button("Enregistrer les modifications",
                                         type="primary", width="stretch"):
                    if not new_nom.strip():
                        st.error("Le nom est obligatoire.")
                    else:
                        try:
                            ctrl.update_client(cli_sel.id,
                                               nom=new_nom, prenom=new_prenom,
                                               societe=new_societe, ice=new_ice,
                                               telephone=new_tel, email=new_email,
                                               adresse=new_adresse)
                            if new_email:
                                st.success(f"✅ Client mis à jour ! Email : {new_email}")
                            else:
                                st.warning("Client mis à jour — mais aucun email renseigné.")
                            st.rerun()
                        except Exception as ex:
                            st.error(str(ex))

            # Test send email to this client
            if cli_sel.email:
                _div()
                _sec("Tester l'envoi d'email")
                if st.button(f"Envoyer un email de test à {cli_sel.email}",
                             key="test_email_cli"):
                    try:
                        from email_service import envoyer_email
                        ok, msg = envoyer_email(
                            destinataire=cli_sel.email,
                            sujet="Test LocationBTP — Wassime BTP",
                            corps_html=f"""
                            <div style="font-family:sans-serif;padding:20px">
                                <h2>Test de connexion email</h2>
                                <p>Bonjour <b>{cli_sel.nom_complet}</b>,</p>
                                <p>Ceci est un email de test envoyé depuis
                                <b>LocationBTP — Wassime BTP</b>.</p>
                                <p>La configuration email fonctionne correctement !</p>
                            </div>"""
                        )
                        if ok:
                            st.success(f"✅ Email de test envoyé à {cli_sel.email} !")
                        else:
                            st.error(f"Échec : {msg}")
                    except Exception as ex:
                        st.error(str(ex))


# ─── COMMANDES ────────────────────────────────────────────────────────────────

def render_commandes():
    import controller as ctrl
    render_page_header("", "Gestion des Commandes", "Bons de commande reçus des clients")

    tab_liste, tab_nouveau = st.tabs(["Commandes", "Nouvelle Commande"])

    with tab_liste:
        commandes = ctrl.get_all_commandes()
        if not commandes:
            _info(" Aucune commande reçue. Enregistrez votre première commande.")
            return

        # KPI bar
        total = len(commandes)
        attente = sum(1 for c in commandes if c["statut"] == "en_attente")
        conf = sum(1 for c in commandes if c["statut"] == "confirmee")
        ann = sum(1 for c in commandes if c["statut"] == "annulee")
        k1, k2, k3, k4 = st.columns(4)
        for col, (lbl, val, c) in zip([k1, k2, k3, k4], [
            ("Total Commandes", total, BRUN),
            ("En Attente", attente, "#92400E"),
            ("Confirmées", conf, VERT),
            ("Annulées", ann, ROUGE),
        ]):
            with col:
                st.markdown(f"""<div class="stat-card" style="border-top-color:{c};padding:14px 16px">
                    <div class="stat-label">{lbl}</div>
                    <div class="stat-value" style="font-size:24px;color:{c}">{val}</div>
                </div>""", unsafe_allow_html=True)

        _div()

        # Liste des commandes
        for cmd in commandes:
            s = cmd["statut"]
            s_colors = {"en_attente": ("#FEF3C7", "#78350F", "⏳"),
                        "confirmee": ("#D8F3DC", "#1B4332", "✅"),
                        "annulee": ("#FEE2E2", "#7F1D1D", "❌"),
                        "livree": ("#DBEAFE", "#1E3A5F", "📦")}
            bg, fg, ico = s_colors.get(s, ("#F2E8DC", "#4A2C17", "•"))

            with st.container():
                c_info, c_engins, c_dates, c_actions = st.columns([3, 2, 2, 2])
                with c_info:
                    st.markdown(f"""
                    <div style="padding:12px;background:white;border-radius:12px;
                                border-left:4px solid {OR};
                                box-shadow:0 2px 8px rgba(74,44,23,.07)">
                        <div style="font-size:14px;font-weight:800;color:{BRUN}">
                            {cmd["numero"]}
                        </div>
                        <div style="font-size:12px;color:#6B4C3B;margin-top:3px">{cmd["client"]}
                        </div>
                        <span style="background:{bg};color:{fg};padding:2px 10px;
                                     border-radius:20px;font-size:10px;font-weight:700">
                            {ico} {s.replace("_", " ").upper()}
                        </span>
                    </div>""", unsafe_allow_html=True)

                with c_engins:
                    engins_txt = "<br>".join([f"• {e}" for e in cmd["engins"]]) if cmd["engins"] else "—"
                    st.markdown(f"""<div style="padding:12px;background:#FAF6F1;border-radius:10px;
                        font-size:12px;color:{BRUN}">
                        <b style="font-size:11px;text-transform:uppercase;letter-spacing:.8px;
                                   color:#9B7B62">Engins</b><br>{engins_txt}
                    </div>""", unsafe_allow_html=True)

                with c_dates:
                    dd = cmd["date_debut"].strftime("%d/%m/%Y") if cmd.get("date_debut") else "—"
                    df = cmd["date_fin"].strftime("%d/%m/%Y") if cmd.get("date_fin") else "—"
                    st.markdown(f"""<div style="padding:12px;background:#FAF6F1;border-radius:10px;
                        font-size:12px;color:{BRUN}">
                        <b style="font-size:11px;text-transform:uppercase;letter-spacing:.8px;
                                   color:#9B7B62">Période</b><br>
                         {dd}<br> {df}<br>
                        <b style="color:#2563EB">{cmd["duree_jours"]} jr</b>
                    </div>""", unsafe_allow_html=True)

                with c_actions:
                    if s == "en_attente":
                        if st.button("Confirmer", key=f"conf_{cmd['id']}",
                                     type="primary", width='stretch'):
                            ctrl.confirmer_commande(cmd["id"])
                            ctrl.update_statut_engin_apres_commande(cmd["id"])
                            st.success("Commande confirmée — Engins marqués COMMANDÉS")
                            st.rerun()
                    if s in ["en_attente", "confirmee"]:
                        if st.button("Annuler", key=f"ann_{cmd['id']}",
                                     width='stretch'):
                            ctrl.annuler_commande(cmd["id"])
                            st.rerun()
                    if s == "confirmee" and not cmd.get("devis_id"):
                        if st.button("Creer Devis", key=f"dev_{cmd['id']}",
                                     width='stretch'):
                            try:
                                did, dnum = ctrl.creer_devis_depuis_commande(cmd["id"])
                                st.success(f"✅ Devis {dnum} créé !")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
                    if cmd.get("devis_id"):
                        st.markdown(f"""<div style="background:#D8F3DC;border-radius:8px;
                            padding:8px;text-align:center;font-size:11px;
                            font-weight:700;color:#1B4332"> Devis créé</div>""",
                                    unsafe_allow_html=True)

                st.markdown("<hr style='border:none;border-top:1px solid #F2E8DC;margin:8px 0'>",
                            unsafe_allow_html=True)

    with tab_nouveau:
        clients = ctrl.get_all_clients()
        engins = ctrl.get_all_engins()
        if not clients:
            _err("⚠️ Aucun client. Ajoutez d'abord un client dans l'onglet Clients.")
            return

        client_opts = {c.nom_complet: c.id for c in clients}
        _sec(" Informations de la commande")
        with st.form("form_cmd_new"):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                client_sel = st.selectbox(" Client *", list(client_opts.keys()))
            with c2:
                dd = st.date_input("📅 Début *", value=date.today())
            with c3:
                df = st.date_input("📅 Fin *", value=date.today() + timedelta(days=7))

            _sec("Sélection des engins")
            lignes = []
            for eng in engins:
                ce1, ce2 = st.columns([4, 1])
                with ce1:
                    s_ico = {"disponible": "🟢", "loue": "🔵", "maintenance": "🔧", "commande": "📦"}.get(eng.statut, "⚪")
                    chk = st.checkbox(f"{s_ico} {eng.nom} — {eng.prix_journalier:,.0f} MAD/jr",
                                      key=f"cmd_sel_{eng.id}")
                with ce2:
                    qty = st.number_input("Qté", 1, 99, 1, key=f"cmd_qty_{eng.id}",
                                          label_visibility="collapsed")
                if chk: lignes.append({"engin_id": eng.id, "quantite": qty})

            notes = st.text_area("📝 Notes", placeholder="Observations particulières…")
            if st.form_submit_button("💾 Enregistrer la Commande", type="primary",
                                     width='stretch'):
                if not lignes:
                    st.error("⚠️ Sélectionnez au moins un engin.")
                elif df <= dd:
                    st.error("⚠️ La date de fin doit être après la date de début.")
                else:
                    try:
                        cid, cnum = ctrl.create_commande(client_opts[client_sel], dd, df, lignes, notes)
                        st.success(f"✅ Commande **{cnum}** enregistrée avec succès !")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))


# ─── DEVIS ────────────────────────────────────────────────────────────────────

def render_devis():
    import controller as ctrl
    from pdf_generator import generer_devis_pdf
    render_page_header("", "Gestion des Devis", "Création, suivi et export des devis de location")

    tab_liste, tab_nouveau, tab_modifier = st.tabs([
        "Liste & Actions", "Nouveau Devis", "Modifier un Devis"
    ])

    # ── LISTE ──────────────────────────────────────────────────────────────────
    with tab_liste:
        devis_list = ctrl.get_all_devis()
        if not devis_list:
            _info(" Aucun devis. Créez votre premier devis via l'onglet .")
        else:
            # KPIs
            k1, k2, k3, k4 = st.columns(4)
            for col, (lbl, f, c) in zip([k1, k2, k3, k4], [
                ("Total", lambda d: True, BRUN),
                ("Brouillons", lambda d: d["statut"] == "brouillon", "#92400E"),
                ("Validés", lambda d: d["statut"] == "valide", VERT),
                ("CA Devis", None, OR),
            ]):
                with col:
                    val = f"{sum(d['montant_ttc'] for d in devis_list):,.0f}" if f is None else str(
                        sum(1 for d in devis_list if f(d)))
                    lbl2 = "MAD" if f is None else ""
                    st.markdown(f"""<div class="stat-card" style="border-top-color:{c};padding:12px 16px">
                        <div class="stat-label">{lbl}</div>
                        <div class="stat-value" style="font-size:22px;color:{c}">{val}</div>
                        <div class="stat-sub">{lbl2}</div>
                    </div>""", unsafe_allow_html=True)
            _div()

            # Tableau
            s_ico = {"brouillon": "📝", "valide": "✅", "facture": "🧾", "annule": "❌"}
            df_d = pd.DataFrame([{
                "N° Devis": d["numero"],
                "Client": d["client"],
                "Début": d["date_debut"].strftime("%d/%m/%Y") if d["date_debut"] else "—",
                "Fin": d["date_fin"].strftime("%d/%m/%Y") if d["date_fin"] else "—",
                "TTC (MAD)": f"{d['montant_ttc']:,.2f}",
                "Statut": s_ico.get(d["statut"], "•") + " " + d["statut"].upper(),
            } for d in devis_list])
            st.dataframe(df_d, width='stretch', hide_index=True, height=300)

            _div()
            _sec("Actions rapides")
            d_ids = {d["numero"]: d["id"] for d in devis_list}
            sel = st.selectbox("Sélectionner un devis", ["—"] + list(d_ids.keys()), key="devis_sel")
            if sel != "—":
                ddata = ctrl.get_devis_by_id(d_ids[sel])
                if ddata:
                    # Infos devis
                    st.markdown(f"""
                    <div class="lux-card" style="margin-bottom:16px;padding:16px 20px">
                        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">
                            <div>
                                <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#9B7B62">Client</div>
                                <div style="font-size:14px;font-weight:700;color:{BRUN}">{ddata["client_nom"]}</div>
                            </div>
                            <div>
                                <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#9B7B62">Période</div>
                                <div style="font-size:13px;font-weight:600;color:{BRUN}">
                                    {ddata["date_debut"].strftime("%d/%m/%Y") if ddata["date_debut"] else "—"}
                                    → {ddata["date_fin"].strftime("%d/%m/%Y") if ddata["date_fin"] else "—"}
                                    ({ddata["duree_jours"]} jr)
                                </div>
                            </div>
                            <div style="text-align:right">
                                <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#9B7B62">Total TTC</div>
                                <div style="font-size:22px;font-weight:900;color:{OR}">{ddata["montant_ttc"]:,.2f} MAD</div>
                            </div>
                        </div>
                        <div style="margin-top:12px;padding-top:12px;border-top:1px solid #F2E8DC;
                                    display:grid;grid-template-columns:repeat(3,1fr);gap:8px;
                                    font-size:12px;color:#6B4C3B">
                            <span>HT : <b>{ddata["montant_ht"]:,.2f} MAD</b></span>
                            <span>TVA {ddata["tva_taux"]:.0f}% : <b>{ddata["montant_tva"]:,.2f} MAD</b></span>
                            <span style="text-align:right">{_badge_html(ddata["statut"])}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)

                    if ddata.get("lignes"):
                        ldf = pd.DataFrame([{
                            "Désignation": l["description"], "Jours": l["quantite"],
                            "P.U (MAD)": f"{l['prix_unitaire']:,.2f}",
                            "Montant (MAD)": f"{l['montant']:,.2f}"
                        } for l in ddata["lignes"]])
                        st.dataframe(ldf, width='stretch', hide_index=True)

                    ca, cb, cc, cd = st.columns(4)
                    with ca:
                        if ddata["statut"] == "brouillon" and st.button("Valider", type="primary",
                                                                        width='stretch', key="dv_val"):
                            ctrl.valider_devis(d_ids[sel]);
                            st.success("Devis validé !");
                            st.rerun()
                    with cb:
                        if ddata["statut"] == "valide" and st.button("Creer Facture",
                                                                     width='stretch', key="dv_fac"):
                            _, fn = ctrl.create_facture(d_ids[sel]);
                            st.success(f"Facture {fn} créée !");
                            st.rerun()
                    with cc:
                        if ddata["statut"] not in ["annule", "facture"] and st.button("Annuler",
                                                                                      width='stretch', key="dv_ann"):
                            ctrl.annuler_devis(d_ids[sel]);
                            st.rerun()
                    with cd:
                        try:
                            pdf = generer_devis_pdf(ddata)
                            st.download_button("PDF", data=pdf,
                                               file_name=f"Devis_{ddata['numero']}.pdf",
                                               mime="application/pdf", width='stretch', key="dv_pdf")
                            # Bouton envoi email
                            client_email = ddata.get("client_email", "")
                            if client_email:
                                if st.button("Envoyer par Email", key="dv_email", width='stretch'):
                                    try:
                                        from email_service import email_devis
                                        ok, msg = email_devis(
                                            ddata["client_nom"], client_email,
                                            ddata["numero"],
                                            ddata["date_debut"].strftime("%d/%m/%Y") if ddata["date_debut"] else "",
                                            ddata["date_fin"].strftime("%d/%m/%Y") if ddata["date_fin"] else "",
                                            ddata["montant_ttc"], pdf)
                                        if ok:
                                            st.success(f"Email envoye : {msg}")
                                        else:
                                            st.error(f"Erreur : {msg}")
                                    except Exception as ex:
                                        st.error(str(ex))
                            else:
                                st.caption("Ajoutez un email client pour envoyer")
                        except Exception as e:
                            st.error(str(e))

    # ── NOUVEAU DEVIS ──────────────────────────────────────────────────────────
    with tab_nouveau:
        clients = ctrl.get_all_clients()
        engins = ctrl.get_all_engins()
        if not clients:
            _err("⚠️ Aucun client. Ajoutez un client d'abord.")
            return
        client_opts = {c.nom_complet: c.id for c in clients}

        with st.form("form_devis_new"):
            _sec("Informations générales")
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                client_s = st.selectbox(" Client *", list(client_opts.keys()))
            with c2:
                dd = st.date_input("📅 Date début *", value=date.today())
            with c3:
                df = st.date_input("📅 Date fin *", value=date.today() + timedelta(days=1))

            _sec(" TVA")
            ct1, ct2 = st.columns([1, 2])
            with ct1:
                tva_p = st.selectbox("Taux prédéfini",
                                     ["20% (standard)", "14%", "10%", "7%", "0% (exonéré)", "Personnalisé"])
                pmap = {"20% (standard)": 20, "14%": 14, "10%": 10, "7%": 7, "0% (exonéré)": 0, "Personnalisé": 20}
                tva = st.number_input("Taux exact (%)", 0.0, 100.0, float(pmap[tva_p]), 1.0)
            with ct2:
                st.markdown(f"""<div class="lux-info" style="margin-top:28px">
                     TVA : <b>{tva:.1f}%</b> —
                    Sur 10 000 MAD HT → TVA <b>{10000 * tva / 100:,.0f} MAD</b> →
                    TTC <b>{10000 * (1 + tva / 100):,.0f} MAD</b>
                </div>""", unsafe_allow_html=True)

            _sec("Engins à louer")
            lignes_s = []
            for eng in engins:
                s_ico = {"disponible": "🟢", "loue": "🔴", "maintenance": "🟡", "commande": "📦"}.get(eng.statut, "⚪")
                ce1, ce2, ce3 = st.columns([3, 1, 1])
                with ce1:
                    chk = st.checkbox(f"{s_ico} {eng.nom} — {eng.prix_journalier:,.0f} MAD/jr",
                                      key=f"nd_s_{eng.id}")
                with ce2:
                    qty = st.number_input("Jours", 1.0, 999.0, 1.0, 1.0, key=f"nd_q_{eng.id}",
                                          label_visibility="collapsed")
                with ce3:
                    if chk:
                        st.markdown(f"**{eng.prix_journalier * qty:,.0f}**")
                if chk:
                    lignes_s.append({"engin_id": eng.id, "quantite": qty,
                                     "prix_unitaire": eng.prix_journalier, "description": eng.nom})

            notes = st.text_area("📝 Notes", placeholder="Conditions particulières…")
            if lignes_s:
                ht, tva_m, ttc = ctrl.calculer_montants(lignes_s, tva)
                _div()
                r1, r2, r3 = st.columns(3)
                r1.metric("Total H.T", format_mad(ht))
                r2.metric(f"TVA {tva:.1f}%", format_mad(tva_m))
                r3.metric("Total TTC", format_mad(ttc))

            sub_new = st.form_submit_button("Creer le Devis", type="primary", width='stretch')

        if sub_new:
            if not lignes_s:
                st.error("⚠️ Sélectionnez au moins un engin.")
            elif df <= dd:
                st.error("⚠️ La date de fin doit être après la date de début.")
            else:
                try:
                    did, dnum = ctrl.create_devis(client_opts[client_s], dd, df, lignes_s, tva, notes)
                    st.success(f"✅ Devis **{dnum}** créé !")
                    ddata = ctrl.get_devis_by_id(did)
                    pdf = generer_devis_pdf(ddata)
                    st.download_button("Telecharger PDF", data=pdf,
                                       file_name=f"Devis_{dnum}.pdf", mime="application/pdf",
                                       width='stretch', type="primary", key="nd_dl")
                except Exception as e:
                    st.error(str(e))

    # ── MODIFIER ───────────────────────────────────────────────────────────────
    with tab_modifier:
        dl = ctrl.get_all_devis()
        brouillons = [d for d in dl if d["statut"] == "brouillon"]
        if not brouillons:
            _info(" Aucun devis en brouillon à modifier. Seuls les brouillons sont modifiables.")
            return
        clients = ctrl.get_all_clients()
        engins = ctrl.get_all_engins()
        c_opts = {c.nom_complet: c.id for c in clients}
        b_map = {d["numero"]: d["id"] for d in brouillons}
        sel_mod = st.selectbox("Sélectionner le devis à modifier", list(b_map.keys()), key="mod_sel")
        dd_data = ctrl.get_devis_by_id(b_map[sel_mod])
        if dd_data:
            cidx = list(c_opts.keys()).index(dd_data["client_nom"]) if dd_data["client_nom"] in c_opts else 0
            with st.form(f"form_mod_{b_map[sel_mod]}"):
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    cm = st.selectbox(" Client", list(c_opts.keys()), index=cidx)
                with c2:
                    dm = st.date_input("📅 Début", value=dd_data["date_debut"])
                with c3:
                    fm = st.date_input("📅 Fin", value=dd_data["date_fin"])
                ct, _ = st.columns([1, 2])
                with ct:
                    tva_m2 = st.number_input("TVA (%)", 0.0, 100.0, float(dd_data["tva_taux"]), 1.0)
                _sec("Engins (pré-sélectionnés selon le devis actuel)")
                actuels = {l["description"]: l["quantite"] for l in dd_data.get("lignes", [])}
                lgn_m = []
                for eng in engins:
                    in_d = eng.nom in actuels;
                    qd = actuels.get(eng.nom, 1.0)
                    mm1, mm2 = st.columns([3, 1])
                    with mm1:
                        chk = st.checkbox(f"{eng.nom} — {eng.prix_journalier:,.0f} MAD/jr",
                                          value=in_d, key=f"md_s_{eng.id}")
                    with mm2:
                        qty = st.number_input("Jours", 1.0, 999.0, float(qd), 1.0,
                                              key=f"md_q_{eng.id}", label_visibility="collapsed")
                    if chk: lgn_m.append({"engin_id": eng.id, "quantite": qty,
                                          "prix_unitaire": eng.prix_journalier, "description": eng.nom})
                notes_m = st.text_area("📝 Notes", value=dd_data.get("notes") or "")
                if lgn_m:
                    ht2, tv2, tt2 = ctrl.calculer_montants(lgn_m, tva_m2)
                    r1, r2, r3 = st.columns(3)
                    r1.metric("HT", format_mad(ht2));
                    r2.metric("TVA", format_mad(tv2))
                    r3.metric("TTC", format_mad(tt2))
                save_m = st.form_submit_button("Enregistrer les modifications", type="primary",
                                               width='stretch')
            if save_m:
                if not lgn_m:
                    st.error("⚠️ Au moins un engin requis.")
                elif fm <= dm:
                    st.error("⚠️ Date fin doit être après date début.")
                else:
                    try:
                        ctrl.update_devis_complet(b_map[sel_mod], c_opts[cm], dm, fm, lgn_m, tva_m2, notes_m)
                        st.success("✅ Devis mis à jour !")
                        du = ctrl.get_devis_by_id(b_map[sel_mod])
                        pdf = generer_devis_pdf(du)
                        st.download_button("📄 PDF mis à jour", data=pdf,
                                           file_name=f"Devis_{sel_mod}_MaJ.pdf", mime="application/pdf", key="mod_dl")
                    except Exception as e:
                        st.error(str(e))


# ─── BONS DE LIVRAISON ────────────────────────────────────────────────────────

def render_livraison():
    import controller as ctrl
    from pdf_generator import generer_bl_pdf
    render_page_header("", "Bons de Livraison", "Émission et suivi des bons de livraison")

    tab_liste, tab_creer = st.tabs(["Liste des BL", "Creer un BL"])

    with tab_liste:
        bls = ctrl.get_all_bons_livraison()
        if not bls:
            _info(" Aucun bon de livraison. Créez-en un depuis un devis validé.")
        else:
            s_ico = {"emis": "📋", "recu": "📥", "signe": "✅"}
            df_bl = pd.DataFrame([{
                "N° BL": b["numero"],
                "N° Devis": b["devis_numero"],
                "Client": b["client"],
                "Date": b["date_livraison"].strftime("%d/%m/%Y") if b["date_livraison"] else "—",
                "Lieu": b["lieu_livraison"] or "—",
                "Statut": s_ico.get(b["statut"], "•") + " " + b["statut"].upper(),
            } for b in bls])
            st.dataframe(df_bl, width='stretch', hide_index=True)
            _div()
            bl_map = {b["numero"]: b["id"] for b in bls}
            sel_bl = st.selectbox("Sélectionner un BL", ["—"] + list(bl_map.keys()),
                                  key="sel_bl_main")
            if sel_bl != "—":
                bl_d = ctrl.get_bon_livraison_by_id(bl_map[sel_bl])
                if bl_d:
                    try:
                        pdf_bl = generer_bl_pdf(bl_d)
                        col_bl1, col_bl2 = st.columns(2)
                        with col_bl1:
                            st.download_button("Télécharger PDF BL", data=pdf_bl,
                                               file_name=f"BL_{sel_bl}.pdf",
                                               mime="application/pdf", key="dl_bl",
                                               width="stretch")
                        with col_bl2:
                            try:
                                from database import SessionLocal
                                from models import BonLivraison as _BLM_l
                                _s_bl = SessionLocal()
                                _bl_obj = _s_bl.query(_BLM_l).filter(
                                    _BLM_l.id == bl_map[sel_bl]).first()
                                _e_bl = _bl_obj.devis.client.email if _bl_obj and _bl_obj.devis and _bl_obj.devis.client else ""
                                _n_bl = _bl_obj.devis.client.nom_complet if _bl_obj and _bl_obj.devis and _bl_obj.devis.client else ""
                                _s_bl.close()
                                if _e_bl:
                                    if st.button("Envoyer par Email",
                                                 key="btn_email_bl_list",
                                                 type="secondary",
                                                 width="stretch"):
                                        from email_service import email_bon_livraison
                                        _ok_bl, _msg_bl = email_bon_livraison(
                                            _n_bl, _e_bl, sel_bl,
                                            bl_d.get("lieu_livraison", ""), "", pdf_bl)
                                        if _ok_bl:
                                            st.success(f"✅ BL envoyé à {_e_bl}")
                                        else:
                                            st.error(f"Erreur : {_msg_bl}")
                                    st.caption(f"→ {_e_bl}")
                                else:
                                    st.warning("⚠️ Email client manquant")
                                    st.caption("Ajoutez-le dans Clients → Modifier")
                            except Exception:
                                pass
                    except Exception as e:
                        st.error(str(e))

    with tab_creer:
        dvs = [d for d in ctrl.get_all_devis() if d["statut"] in ["valide", "facture"]]
        if not dvs:
            _info(" Aucun devis validé. Validez d'abord un devis.")
            return
        d_opts = {f"{d['numero']} — {d['client']}": d["id"] for d in dvs}
        with st.form("form_bl_new"):
            _sec("Informations du bon de livraison")
            sel_d = st.selectbox(" Devis associé *", list(d_opts.keys()))
            lieu = st.text_input("📍 Lieu de livraison", placeholder="Chantier, adresse…")
            obs = st.text_area("📝 Observations", placeholder="Conditions de livraison…")
            if st.form_submit_button("Creer le Bon de Livraison", type="primary",
                                     width='stretch'):
                try:
                    bl_id, bl_num = ctrl.create_bon_livraison(d_opts[sel_d], lieu, obs)
                    ctrl.update_statut_engin_apres_livraison(bl_id)
                    st.success(f"✅ BL **{bl_num}** créé — Engins marqués LOUÉS !")
                    bl_d = ctrl.get_bon_livraison_by_id(bl_id)
                    pdf = generer_bl_pdf(bl_d)
                    st.download_button("Telecharger BL", data=pdf,
                                       file_name=f"BL_{bl_num}.pdf", mime="application/pdf", key="new_bl_dl")
                    # Bouton email BL
                    try:
                        from database import SessionLocal
                        from models import BonLivraison as _BLM
                        _s = SessionLocal()
                        _bl = _s.query(_BLM).filter(_BLM.id == bl_id).first()
                        _e_bl = _bl.devis.client.email if _bl and _bl.devis and _bl.devis.client else ""
                        _n_bl = _bl.devis.client.nom_complet if _bl and _bl.devis and _bl.devis.client else ""
                        _s.close()
                        if _e_bl:
                            if st.button(f"Envoyer BL par Email ({_e_bl})",
                                         key="btn_email_bl", type="secondary"):
                                try:
                                    from email_service import email_bon_livraison
                                    _ok_bl, _msg_bl = email_bon_livraison(
                                        _n_bl, _e_bl, bl_num, lieu, "", pdf)
                                    if _ok_bl:
                                        st.success(f"✅ BL envoyé à {_e_bl}")
                                    else:
                                        st.error(f"Erreur : {_msg_bl}")
                                except Exception as _ex:
                                    st.error(str(_ex))
                        else:
                            st.caption("⚠️ Email client manquant — ajoutez-le dans Clients")
                    except Exception:
                        pass
                except Exception as e:
                    st.error(str(e))


# ─── ATTACHEMENTS ─────────────────────────────────────────────────────────────

def render_attachements():
    import controller as ctrl, calendar
    from pdf_generator import generer_attachement_pdf
    render_page_header("", "Attachements", "Relevés journaliers du travail réel des engins")

    tab_liste, tab_creer = st.tabs(["Liste", "Creer"])

    with tab_liste:
        atts = ctrl.get_all_attachements()
        if not atts:
            _info(" Aucun attachement. Créez-en un pour saisir les jours réels de travail.")
        else:
            df_att = pd.DataFrame([{
                "N°": a["numero"], "N° Devis": a["devis_numero"], "Client": a["client"],
                "Engin": a["engin"], "Matricule": a["matricule"],
                "Mois": f"{a['mois']:02d}/{a['annee']}", "Projet": a["projet"] or "—",
                "Jours Réels": a["nb_jours"], "Heures": a["nb_heures"],
            } for a in atts])
            st.dataframe(df_att, width='stretch', hide_index=True)
            _div()
            att_map = {a["numero"]: a["id"] for a in atts}
            c1, c2 = st.columns([3, 1])
            with c1:
                sel_att = st.selectbox("Télécharger PDF", ["—"] + list(att_map.keys()))
            with c2:
                if sel_att != "—":
                    att_d = ctrl.get_attachement_by_id(att_map[sel_att])
                    if att_d:
                        try:
                            st.markdown("<br>", unsafe_allow_html=True)
                            pdf = generer_attachement_pdf(att_d)
                            st.download_button("Telecharger PDF", data=pdf,
                                               file_name=f"Att_{sel_att}.pdf", mime="application/pdf", key="dl_att")
                        except Exception as e:
                            st.error(str(e))

    with tab_creer:
        dvs = [d for d in ctrl.get_all_devis() if d["statut"] in ["valide", "facture"]]
        engs = ctrl.get_all_engins()
        if not dvs:
            _info(" Aucun devis validé.")
            return
        d_opts = {f"{d['numero']} — {d['client']}": d["id"] for d in dvs}
        e_opts = {f"{e.nom} ({e.matricule})": e for e in engs}

        _sec(" Informations de l'attachement")
        ca1, ca2, ca3 = st.columns([2, 1, 1])
        with ca1:
            sel_d2 = st.selectbox(" Devis *", list(d_opts.keys()))
        with ca2:
            mois_a = st.number_input("Mois", 1, 12, date.today().month)
        with ca3:
            annee_a = st.number_input("Année", 2020, 2035, date.today().year)
        cb1, cb2 = st.columns(2)
        with cb1:
            sel_eng = st.selectbox(" Engin *", list(e_opts.keys()))
        with cb2:
            projet_a = st.text_input("🏗️ Projet *", placeholder="ex: Place Jamaa El Fna")
        obs_a = st.text_area("📝 Observations")

        _div()
        _sec(f" Pointage journalier — Mois {mois_a:02d}/{annee_a}")
        nb_j = calendar.monthrange(annee_a, mois_a)[1]

        with st.form("form_att_new"):
            jours = []
            # En-têtes
            hdr = st.columns([1, 2, 2])
            hdr[0].markdown("**Jour**");
            hdr[1].markdown("**Heures**");
            hdr[2].markdown("**Jour (0/1)**")

            for j in range(1, nb_j + 1):
                wd = calendar.weekday(annee_a, mois_a, j)
                is_wk = (wd == 6)
                col_j, col_h, col_jt = st.columns([1, 2, 2])
                with col_j:
                    st.markdown(f"<b style='color:{'#DC2626' if is_wk else BRUN}'>{j}</b>",
                                unsafe_allow_html=True)
                with col_h:
                    h = st.number_input("Heures", 0.0, 24.0, 0.0 if is_wk else 9.0, 0.5,
                                        key=f"h_{j}", label_visibility="collapsed")
                with col_jt:
                    jt = st.number_input("Jour", 0.0, 1.0, 0.0 if is_wk else 1.0, 1.0,
                                         key=f"jt_{j}", label_visibility="collapsed")
                jours.append((j, h, jt))

            total_j = sum(int(jt) for _, _, jt in jours)
            st.markdown(f"""<div class="lux-success">
                 Total jours travaillés : <b>{total_j}</b> jours
            </div>""", unsafe_allow_html=True)

            if st.form_submit_button("💾 Enregistrer l'Attachement", type="primary",
                                     width='stretch'):
                if not projet_a:
                    st.error("⚠️ Le projet est obligatoire.")
                else:
                    try:
                        eng_obj = e_opts.get(sel_eng)
                        aid, anum = ctrl.create_attachement(
                            devis_id=d_opts[sel_d2], engin_id=eng_obj.id if eng_obj else None,
                            mois=mois_a, annee=annee_a, projet=projet_a,
                            matricule_engin=eng_obj.matricule if eng_obj else "",
                            jours_detail=jours, observations=obs_a)
                        st.success(f"✅ Attachement **{anum}** créé — {total_j} jours réels !")
                        att_d = ctrl.get_attachement_by_id(aid)
                        pdf = generer_attachement_pdf(att_d)
                        st.download_button("Telecharger PDF", data=pdf,
                                           file_name=f"Att_{anum}.pdf", mime="application/pdf", key="new_att_dl")
                    except Exception as e:
                        st.error(str(e))


# ─── FACTURATION ──────────────────────────────────────────────────────────────

def render_facturation():
    import controller as ctrl
    from pdf_generator import generer_facture_pdf
    render_page_header("", "Facturation", "Création, modification et export des factures")

    tab_liste, tab_devis, tab_att, tab_mod, tab_red = st.tabs([
        "Liste", "Depuis un Devis", "Depuis Attachement", "Modifier", "Reduction"
    ])
    factures = ctrl.get_all_factures()

    # ── LISTE ──────────────────────────────────────────────────────────────────
    with tab_liste:
        if factures:
            k1, k2, k3, k4 = st.columns(4)
            for col, (lbl, val, c) in zip([k1, k2, k3, k4], [
                ("Facturé Total", f"{sum(f['montant_ttc'] for f in factures):,.0f}", OR),
                ("Encaissé", f"{sum(f['montant_paye'] for f in factures):,.0f}", VERT),
                ("Restant", f"{sum(f['solde_restant'] for f in factures):,.0f}", ROUGE),
                ("En Retard", str(sum(1 for f in factures if f["statut"] == "retard")), ROUGE),
            ]):
                with col:
                    st.markdown(f"""<div class="stat-card" style="border-top-color:{c};padding:12px 16px">
                        <div class="stat-label">{lbl}</div>
                        <div class="stat-value" style="font-size:22px;color:{c}">{val}</div>
                        <div class="stat-sub">MAD</div>
                    </div>""", unsafe_allow_html=True)
            _div()
        if not factures:
            _info(" Aucune facture. Créez-en depuis un devis validé ou un attachement.")
        else:
            ico = {"en_attente": "⏳", "partiel": "🔵", "paye": "✅", "retard": "🔴"}
            df_f = pd.DataFrame([{
                "N° Facture": f["numero"],
                "Statut": ico.get(f["statut"], "•") + " " + f["statut"].upper(),
                "Client": f["client"],
                "Échéance": f["echeance"].strftime("%d/%m/%Y") if f["echeance"] else "—",
                "TTC (MAD)": f"{f['montant_ttc']:,.2f}",
                "Payé (MAD)": f"{f['montant_paye']:,.2f}",
                "Solde (MAD)": f"{f['solde_restant']:,.2f}",
            } for f in factures])
            st.dataframe(df_f, width='stretch', hide_index=True, height=320)
            _div()
            all_map = {f["numero"]: f["id"] for f in factures}
            sel_pdf = st.selectbox("Télécharger PDF", ["—"] + list(all_map.keys()),
                                   key="sel_fac_pdf")
            if sel_pdf != "—":
                fd = ctrl.get_facture_details_complets(all_map[sel_pdf])
                if fd:
                    try:
                        pdf = generer_facture_pdf(fd)
                    except Exception as _e_pdf:
                        pdf = None
                        st.error(f"Erreur PDF : {_e_pdf}")
                    if pdf:
                        col_dl, col_em = st.columns(2)
                        with col_dl:
                            st.download_button("Télécharger PDF", data=pdf,
                                               file_name=f"Fac_{sel_pdf}.pdf",
                                               mime="application/pdf", key="fac_dl",
                                               width="stretch")
                        with col_em:
                            _fac_email = fd.get("client_email", "")
                            _fac_nom = fd.get("client_nom", "")
                            if _fac_email:
                                if st.button(f"Envoyer par Email",
                                             key="btn_email_fac",
                                             type="secondary",
                                             width="stretch",
                                             help=f"Envoyer à {_fac_email}"):
                                    try:
                                        from email_service import email_facture
                                        _ech = fd["echeance"].strftime("%d/%m/%Y") if fd.get("echeance") else ""
                                        ok, msg = email_facture(
                                            _fac_nom, _fac_email,
                                            fd["numero"],
                                            (fd.get("devis") or {}).get("numero", ""),
                                            fd["montant_ttc"], _ech, pdf)
                                        if ok:
                                            st.success(f"✅ Facture envoyée à {_fac_email}")
                                        else:
                                            st.error(f"Erreur : {msg}")
                                    except Exception as ex:
                                        st.error(str(ex))
                                st.caption(f"→ {_fac_email}")
                            else:
                                st.warning("⚠️ Email client manquant")
                                st.caption("Ajoutez-le dans Clients → Modifier")

    # ── DEPUIS DEVIS ───────────────────────────────────────────────────────────
    with tab_devis:
        dvs = [d for d in ctrl.get_all_devis() if d["statut"] == "valide"]
        if not dvs:
            _info(" Aucun devis validé disponible.")
        else:
            d_opts2 = {f"{d['numero']} — {d['client']}": d["id"] for d in dvs}
            with st.form("form_fac_d"):
                _sec("Créer une facture depuis un devis")
                sel_d3 = st.selectbox("Devis *", list(d_opts2.keys()))
                c1, c2 = st.columns(2)
                with c1:
                    ech_d = st.date_input("📅 Échéance *", value=date.today() + timedelta(days=30))
                with c2:
                    tva_d = st.number_input("TVA (%)", 0.0, 100.0, 20.0, 1.0)
                if st.form_submit_button("Creer la Facture", type="primary", width='stretch'):
                    try:
                        fi, fn = ctrl.create_facture(d_opts2[sel_d3], echeance_jours=0)
                        from database import SessionLocal
                        from models import Facture as FM
                        s = SessionLocal();
                        fo = s.query(FM).filter(FM.id == fi).first()
                        fo.echeance = ech_d;
                        fo.tva_taux = tva_d;
                        s.commit();
                        s.close()
                        st.success(f"✅ Facture **{fn}** créée !")
                    except Exception as e:
                        st.error(str(e))

    # ── DEPUIS ATTACHEMENT ─────────────────────────────────────────────────────
    with tab_att:
        _sec(" Facture basée sur les jours réels de l'attachement")
        _info("Le montant est calculé sur les <b>jours réellement travaillés</b> × prix journalier.")
        atts2 = ctrl.get_all_attachements()
        if not atts2:
            st.info("Aucun attachement disponible.")
        else:
            ao = {f"{a['numero']} — {a['client']} — {a['engin']} ({a['nb_jours']} jr)": a["id"] for a in atts2}
            with st.form("form_fac_att2"):
                sel_a2 = st.selectbox(" Attachement *", list(ao.keys()))
                ai_info = next(a for a in atts2 if a["id"] == ao[sel_a2])
                c1, c2, c3 = st.columns(3)
                with c1:
                    ech_a = st.date_input("📅 Échéance *", value=date.today() + timedelta(days=30))
                with c2:
                    tva_a = st.number_input("TVA (%)", 0.0, 100.0, 20.0, 1.0)
                with c3:
                    red_a = st.number_input("Réduction (%)", 0.0, 100.0, 0.0, 1.0)
                notes_a = st.text_area("📝 Notes")
                st.markdown(f'<div class="lux-info"> Jours réels : <b>{ai_info["nb_jours"]}</b></div>',
                            unsafe_allow_html=True)
                if st.form_submit_button("Creer la Facture", type="primary", width='stretch'):
                    try:
                        fi2, fn2, ht2, tv2, tt2 = ctrl.create_facture_from_attachement(
                            ao[sel_a2], tva_a, ech_a, red_a, 0.0, notes_a)
                        st.success(f"✅ Facture **{fn2}** — TTC : {tt2:,.2f} MAD")
                        fd2 = ctrl.get_facture_details_complets(fi2)
                        pdf = generer_facture_pdf(fd2)
                        st.download_button("Telecharger PDF", data=pdf,
                                           file_name=f"Fac_{fn2}.pdf", mime="application/pdf", key="att_fac_dl2")
                    except Exception as e:
                        st.error(str(e))

    # ── MODIFIER ENGINS ────────────────────────────────────────────────────────
    with tab_mod:
        fmod = [f for f in factures if f["statut"] != "paye"]
        if not fmod:
            _ok("✅ Toutes les factures sont payées — aucune modification possible.")
        else:
            engs2 = ctrl.get_all_engins()
            fm_map = {f["numero"]: f["id"] for f in fmod}
            sel_m = st.selectbox("Facture à modifier", list(fm_map.keys()), key="fac_mod3")
            ff = ctrl.get_facture_details_complets(fm_map[sel_m])
            dv_mod = ff.get("devis") or {}
            la = {l["description"]: l["quantite"] for l in dv_mod.get("lignes", [])}
            pu = {l["description"]: l["prix_unitaire"] for l in dv_mod.get("lignes", [])}
            with st.form(f"form_fm_{fm_map[sel_m]}"):
                tva_fm = st.number_input("TVA (%)", 0.0, 100.0, float(ff.get("tva_taux", 20)), 1.0)
                lgn_fm = []
                for eng in engs2:
                    in_f = eng.nom in la;
                    qd = la.get(eng.nom, 1.0);
                    pd_ = pu.get(eng.nom, eng.prix_journalier)
                    m1, m2, m3 = st.columns([3, 1, 1.5])
                    with m1:
                        chk = st.checkbox(eng.nom, value=in_f, key=f"fm3_c_{eng.id}")
                    with m2:
                        qty = st.number_input("Jours", 1.0, 999.0, float(qd), 1.0,
                                              key=f"fm3_q_{eng.id}", label_visibility="collapsed")
                    with m3:
                        pu2 = st.number_input("Prix", 0.0, 99999.0, float(pd_), 50.0,
                                              key=f"fm3_p_{eng.id}", label_visibility="collapsed")
                    if chk: lgn_fm.append({"engin_id": eng.id, "quantite": qty,
                                           "prix_unitaire": pu2, "description": eng.nom})
                if st.form_submit_button("Enregistrer", type="primary", width='stretch'):
                    if not lgn_fm:
                        st.error("⚠️ Au moins un engin requis.")
                    else:
                        ctrl.update_facture_lignes(fm_map[sel_m], lgn_fm, tva_fm)
                        st.success("✅ Facture mise à jour !");
                        st.rerun()

    # ── RÉDUCTION ──────────────────────────────────────────────────────────────
    with tab_red:
        fr = [f for f in factures if f["statut"] != "paye"]
        if not fr:
            _ok("✅ Aucune facture à modifier.")
        else:
            fr_map = {f["numero"]: f["id"] for f in fr}
            sel_r = st.selectbox("Facture", list(fr_map.keys()), key="fac_red3")
            fi_r = next(f for f in fr if f["numero"] == sel_r)
            fd_r = ctrl.get_facture_details_complets(fr_map[sel_r])
            base = (fd_r.get("devis") or {}).get("montant_ttc", fi_r["montant_ttc"])
            st.markdown(f"**TTC base :** {base:,.2f} MAD")
            c1, c2 = st.columns(2)
            with c1:
                mode_r = st.radio("Type", ["En %", "En MAD"], key="red3_mode", horizontal=True)
            with c2:
                if mode_r == "En %":
                    rp = st.number_input("Réduction %", 0.0, 100.0, 0.0, key="r3_p")
                    rm = round(base * rp / 100, 2)
                else:
                    rm = st.number_input("Réduction MAD", 0.0, float(base), 0.0, key="r3_m")
                    rp = 0.0
                new_ttc = round(base - rm, 2)
                st.markdown(f"**Nouveau TTC : {new_ttc:,.2f} MAD**")
            if st.button("Appliquer la reduction", type="primary", key="btn_red3"):
                ctrl.update_facture_reduction(fr_map[sel_r], rp, rm)
                st.success("✅ Réduction appliquée !");
                st.rerun()


# ─── SUIVI PAIEMENTS ──────────────────────────────────────────────────────────

def render_paiements():
    import controller as ctrl
    render_page_header("", "Suivi des Paiements", "Vue consolidée des encaissements & créances")

    paiements = ctrl.get_suivi_paiements()
    if not paiements:
        _info(" Aucune facture enregistrée.")
        return

    total_fac = sum(p["montant_ttc"] for p in paiements)
    total_pay = sum(p["montant_paye"] for p in paiements)
    total_res = sum(p["solde_restant"] for p in paiements)
    retards = [p for p in paiements if p["nb_jours_retard"] > 0]

    # KPI
    k1, k2, k3, k4 = st.columns(4)
    for col, (lbl, val, c) in zip([k1, k2, k3, k4], [
        ("Facturé Total", f"{total_fac:,.2f}", OR),
        ("Encaissé", f"{total_pay:,.2f}", VERT),
        ("Restant", f"{total_res:,.2f}", ROUGE),
        ("En Retard", str(len(retards)), ROUGE),
    ]):
        with col:
            st.markdown(f"""<div class="stat-card" style="border-top-color:{c};padding:14px 16px">
                <div class="stat-label">{lbl}</div>
                <div class="stat-value" style="font-size:22px;color:{c}">{val}</div>
                <div class="stat-sub">MAD</div>
            </div>""", unsafe_allow_html=True)

    _div()

    if retards:
        _sec("Factures en Retard — Envoyer une Relance")
        # Sélecteur + bouton relance
        _col_r1, _col_r2 = st.columns([3, 1])
        with _col_r1:
            _retard_opts = {
                f"{p['numero']} — {p['client']} — {p['nb_jours_retard']} jours": p
                for p in retards
            }
            _sel_r = st.selectbox("Facture à relancer", list(_retard_opts.keys()),
                                  key="sel_relance_pay")
        with _col_r2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Envoyer Relance", type="primary",
                         width="stretch", key="btn_relance_pay"):
                _p_sel = _retard_opts[_sel_r]
                try:
                    from database import SessionLocal
                    from models import Facture as _FM_r
                    from email_service import email_relance_paiement
                    _sr = SessionLocal()
                    _fr = _sr.query(_FM_r).filter(_FM_r.id == _p_sel["id"]).first()
                    _er = _fr.devis.client.email if _fr and _fr.devis and _fr.devis.client else ""
                    _nr = _fr.devis.client.nom_complet if _fr and _fr.devis and _fr.devis.client else ""
                    _sr.close()
                    if _er:
                        _ok_r, _msg_r = email_relance_paiement(
                            _nr, _er, _p_sel["numero"],
                            _p_sel["montant_ttc"], _p_sel["montant_paye"],
                            _p_sel["solde_restant"],
                            _p_sel["echeance"].strftime("%d/%m/%Y") if _p_sel.get("echeance") else "",
                            _p_sel["nb_jours_retard"])
                        if _ok_r:
                            st.success(f"✅ Relance envoyée à {_er}")
                        else:
                            st.error(f"Erreur : {_msg_r}")
                    else:
                        st.error("⚠️ Email client manquant — ajoutez-le dans Clients")
                except Exception as _ex_r:
                    st.error(f"Erreur : {_ex_r}")
        _div()
        for p in retards:
            st.markdown(f"""
            <div style="background:#FEF2F2;border-left:5px solid #DC2626;
                        border-radius:0 12px 12px 0;padding:14px 18px;margin-bottom:8px;
                        box-shadow:0 2px 8px rgba(220,38,38,.10)">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <span style="font-size:14px;font-weight:800;color:#7F1D1D">{p["numero"]}
                        </span>
                        <span style="font-size:13px;color:#991B1B;margin-left:12px">
                            {p["client"]}
                        </span>
                    </div>
                    <div style="text-align:right">
                        <div style="font-size:16px;font-weight:800;color:#DC2626">
                            {p["solde_restant"]:,.2f} MAD
                        </div>
                        <div style="font-size:11px;color:#991B1B">
                            {p["nb_jours_retard"]} jours de retard
                        </div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
        _div()

    _sec("Détail de tous les paiements")
    ico = {"en_attente": "⏳", "partiel": "🔵", "paye": "✅", "retard": "🔴"}
    df_p = pd.DataFrame([{
        "N° Facture": p["numero"], "N° Devis": p["devis_numero"], "Client": p["client"],
        "Statut": ico.get(p["statut"], "•") + " " + p["statut"].upper(),
        "Échéance": p["echeance"].strftime("%d/%m/%Y") if p["echeance"] else "—",
        "Retard (j)": p["nb_jours_retard"] if p["nb_jours_retard"] > 0 else "—",
        "TTC": f"{p['montant_ttc']:,.2f}", "Payé": f"{p['montant_paye']:,.2f}",
        "Restant": f"{p['solde_restant']:,.2f}",
    } for p in paiements])
    st.dataframe(df_p, width='stretch', hide_index=True, height=320)

    _div()
    _sec("Enregistrer un paiement")
    non_p = [p for p in paiements if p["statut"] != "paye"]
    if not non_p:
        _ok("🎉 Toutes les factures sont soldées !")
    else:
        fo = {f"{p['numero']} — {p['client']} ({p['solde_restant']:,.2f} MAD)": p["id"] for p in non_p}
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            sel_p = st.selectbox("Facture", list(fo.keys()), key="pay_sel2")
        fi_p = next(p for p in non_p if p["id"] == fo[sel_p])
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
        fi_r = next(p for p in retards if p["id"] == fo[sel_r])

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