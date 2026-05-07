"""pages/dashboard.py — LocationBTP"""
import streamlit as st, pandas as pd, os
from datetime import date, timedelta
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import controller as ctrl
from modules.ui_helpers import (render_page_header, _sec, _info, _warn,
                               _err, _div, PRIMARY, GREEN, RED, ORANGE,
                               PURPLE, GRAY_400, GRAY_500, GRAY_900,
                               GRAY_200, BRUN, OR, VERT, ROUGE)


def render():
    import controller as ctrl
    import matplotlib, matplotlib.pyplot as plt

    # ── Forcer données fraîches — pas de cache ────────────────────────────────
    try:
        st.cache_data.clear()
        st.cache_resource.clear()
    except Exception:
        pass

    import matplotlib.ticker as mticker, numpy as np
    from io import BytesIO; import base64
    from collections import Counter
    matplotlib.use("Agg")
    plt.rcParams.update({"font.family":"DejaVu Sans"})

    render_page_header("", "Tableau de Bord", "Vue strategique — Wassime BTP")

    # Bouton d'actualisation
    col_ref = st.columns([5,1])[1]
    with col_ref:
        if st.button("🔄 Actualiser", key="db_refresh", type="secondary"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()

    stats   = ctrl.get_dashboard_stats()
    eng     = stats.get("engins", {})
    ca_d    = stats.get("ca_mensuel", [])
    ca_total= stats.get("ca_total", 0)
    ca_mois = stats.get("ca_mois", 0)
    creances= stats.get("creances", 0)
    dispo   = eng.get("disponibles", 0)
    loues   = eng.get("loues", 0)
    maint   = eng.get("maintenance", 0)
    total_e = eng.get("total", 0)
    n_devis = stats.get("devis_en_cours", 0)
    n_retard= stats.get("factures_retard", 0)
    taux_enc= (ca_total/(ca_total+creances)*100) if (ca_total+creances)>0 else 100
    ca_vals = [d["ca"] for d in ca_d] if len(ca_d)>=2 else [0]*6

    # ── Sparkline helper ──────────────────────────────────────────────────────
    def spark(vals, color):
        fig, ax = plt.subplots(figsize=(3, 0.65))
        fig.patch.set_alpha(0); ax.set_facecolor("none")
        x = range(len(vals))
        ax.fill_between(x, vals, alpha=0.18, color=color)
        ax.plot(x, vals, color=color, lw=2, solid_capstyle="round")
        ax.set_xlim(0, max(len(vals)-1, 1)); ax.axis("off")
        plt.tight_layout(pad=0)
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=90, bbox_inches="tight", transparent=True)
        plt.close(); buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode()

    # ════════════════════════════════════════════════════════════════════════
    # RANGÉE 1 — 5 KPI cards compactes, même hauteur
    # ════════════════════════════════════════════════════════════════════════
    c1,c2,c3,c4,c5 = st.columns(5)
    kpi_data = [
        (c1, "Chiffre d'Affaires", f"{ca_total:,.0f}", "MAD total",
         PRIMARY, spark(ca_vals, PRIMARY)),
        (c2, "CA ce Mois", f"{ca_mois:,.0f}", "MAD / mois",
         GREEN, spark([ca_mois*0.5, ca_mois*0.8, ca_mois], GREEN)),
        (c3, "Devis Actifs", str(n_devis), "en cours",
         PURPLE, spark([max(1,n_devis), max(1,n_devis), max(1,n_devis)], PURPLE)),
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
        fig_ca.patch.set_facecolor("white"); ax_ca.set_facecolor("white")
        if with_data:
            mois = [d["mois"] for d in ca_d]; x = np.arange(len(mois))
            ax_ca.bar(x, ca_vals, width=0.52,
                color=["#2563EB" if i==len(ca_vals)-1 else "#BFDBFE" for i in range(len(ca_vals))],
                edgecolor="none", zorder=3)
            ax_ca.fill_between(x, ca_vals, alpha=0.04, color="#2563EB", zorder=2)
            ax_ca.plot(x, ca_vals, color="#1D4ED8", lw=1.6, marker="o", markersize=3.5,
                    markerfacecolor="white", markeredgecolor="#1D4ED8",
                    markeredgewidth=1.5, zorder=5, alpha=0.7)
            for xi, v in zip(x, ca_vals):
                if v > 0:
                    ax_ca.text(xi, v + max(ca_vals)*0.028, f"{v:,.0f}",
                            ha="center", va="bottom", fontsize=7, fontweight="700", color="#334155")
            ax_ca.set_xticks(x)
            ax_ca.set_xticklabels(mois, fontsize=8.5, color="#94A3B8")
        else:
            ax_ca.text(0.5, 0.5, "Aucune donnee CA", transform=ax_ca.transAxes,
                      ha="center", va="center", fontsize=11, color="#94A3B8")
        ax_ca.yaxis.set_major_formatter(mticker.FuncFormatter(
            lambda v,_: f"{v/1000:.0f}k" if v>=1000 else f"{v:.0f}"))
        ax_ca.tick_params(labelsize=8.5, colors="#94A3B8", length=0)
        ax_ca.grid(axis="y", ls="--", alpha=0.2, color="#E2E8F0"); ax_ca.set_axisbelow(True)
        for sp in ax_ca.spines.values(): sp.set_visible(False)
        plt.tight_layout(pad=0.5)
        st.markdown('<div style="background:white;border:1px solid #E2E8F0;border-radius:12px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.05)">', unsafe_allow_html=True)
        st.pyplot(fig_ca, width='stretch'); plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Donut parc ───────────────────────────────────────────────────────────
    with r2b:
        _sec("Repartition Parc")
        st.markdown('<div style="background:white;border:1px solid #E2E8F0;border-radius:12px;padding:14px;box-shadow:0 1px 4px rgba(0,0,0,.05);height:100%">', unsafe_allow_html=True)
        lp,vp,cp=[],[],[]
        for lb,v,c in [("Dispos",dispo,GREEN),("Loues",loues,PRIMARY),("Maint.",maint,ORANGE)]:
            if v > 0: lp.append(lb); vp.append(v); cp.append(c)
        if vp:
            fig_d,ax_d = plt.subplots(figsize=(2.3, 2.0))
            fig_d.patch.set_facecolor("white"); ax_d.set_facecolor("white")
            _,_,autos = ax_d.pie(vp, labels=None, colors=cp, autopct="%1.0f%%",
                startangle=90, pctdistance=0.73,
                wedgeprops=dict(edgecolor="white", linewidth=2, width=0.55))
            for t in autos: t.set_fontsize(8.5); t.set_fontweight("800"); t.set_color("white")
            ax_d.legend(lp, loc="lower center", ncol=3, fontsize=7.5,
                       frameon=False, bbox_to_anchor=(0.5, -0.14))
            plt.tight_layout(pad=0.2)
            st.pyplot(fig_d, width='stretch'); plt.close()
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
        st.markdown('<div style="background:white;border:1px solid #E2E8F0;border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.05);height:100%">', unsafe_allow_html=True)
        try:
            engs = sorted(ctrl.get_engins_disponibilite(), key=lambda e: e["prix_jr"], reverse=True)[:6]
            max_p = max((e["prix_jr"] for e in engs), default=1) or 1
            rc = ["#1D4ED8","#2563EB","#3B82F6","#60A5FA","#93C5FD","#BFDBFE"]
            for i, e in enumerate(engs):
                pct = int(e["prix_jr"] / max_p * 100)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;
                            padding:9px 14px;border-bottom:1px solid #F8FAFC">
                    <div style="width:20px;height:20px;background:{rc[i]};border-radius:50%;
                        flex-shrink:0;display:flex;align-items:center;justify-content:center;
                        font-size:10px;font-weight:800;color:white">{i+1}</div>
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
            st.markdown('<div style="padding:16px;color:#94A3B8;font-size:12px">Aucune donnee</div>', unsafe_allow_html=True)
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
                                color:{"#EF4444" if creances>0 else GREEN}">
                        {creances:,.0f} MAD</div>
                </div>
            </div>
            <div style="background:#F1F5F9;border-radius:6px;height:8px;overflow:hidden;
                        margin-bottom:6px">
                <div style="background:linear-gradient(90deg,{GREEN},{PRIMARY});
                            width:{min(taux_enc,100):.0f}%;height:100%;border-radius:6px">
                </div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:11px;
                        color:{GRAY_400}">
                <span>Encaisse : {ca_total:,.0f} MAD</span>
                <span>Total : {ca_total+creances:,.0f} MAD</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Donut paiements ──────────────────────────────────────────────────────
    with r3b:
        _sec("Repartition Paiements")
        st.markdown('<div style="background:white;border:1px solid #E2E8F0;border-radius:12px;padding:14px;box-shadow:0 1px 4px rgba(0,0,0,.05)">', unsafe_allow_html=True)
        try:
            all_fac = ctrl.get_all_factures()
            fc = Counter(f["statut"] for f in all_fac)
            pay_l=[]; pay_v=[]; pay_c=[]
            cmap={"paye":GREEN,"partiel":PRIMARY,"en_attente":ORANGE,"retard":RED}
            lmap={"paye":"Paye","partiel":"Partiel","en_attente":"Attente","retard":"Retard"}
            for s,v in fc.items():
                if v>0: pay_l.append(lmap.get(s,s)); pay_v.append(v); pay_c.append(cmap.get(s,GRAY_400))
            if pay_v:
                fig_p,ax_p = plt.subplots(figsize=(2.2, 1.9))
                fig_p.patch.set_facecolor("white"); ax_p.set_facecolor("white")
                _,_,autos = ax_p.pie(pay_v, labels=None, colors=pay_c, autopct="%1.0f%%",
                    startangle=90, pctdistance=0.73,
                    wedgeprops=dict(edgecolor="white", linewidth=2, width=0.55))
                for t in autos: t.set_fontsize(8); t.set_fontweight("800"); t.set_color("white")
                ax_p.legend(pay_l, loc="lower center", ncol=2, fontsize=7,
                           frameon=False, bbox_to_anchor=(0.5,-0.18))
                plt.tight_layout(pad=0.2)
                st.pyplot(fig_p, width='stretch'); plt.close()
                payes = fc.get("paye", 0)
                st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:11px;margin-top:6px;padding-top:6px;border-top:1px solid #F1F5F9"><span style="color:{GREEN};font-weight:600">{payes} paye(s)</span><span style="color:{GRAY_400}">{len(all_fac)} total</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="height:80px;display:flex;align-items:center;justify-content:center;color:#94A3B8;font-size:12px">Aucune facture</div>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<div style="height:80px;display:flex;align-items:center;justify-content:center;color:#94A3B8;font-size:12px">Aucune donnee</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Alertes ──────────────────────────────────────────────────────────────
    with r3c:
        _sec("Alertes")
        alertes = []
        if n_retard > 0: alertes.append((RED, "#FEF2F2", "Retards", f"{n_retard} facture(s)"))
        if creances > 0: alertes.append((ORANGE, "#FFFBEB", "Creances", f"{creances:,.0f} MAD"))
        if loues > 0:    alertes.append((PRIMARY, "#EFF6FF", "En location", f"{loues} engin(s)"))
        if not alertes:
            st.markdown('<div style="background:#ECFDF5;border:1px solid #A7F3D0;border-radius:12px;padding:16px;text-align:center"><div style="font-size:13px;font-weight:600;color:#065F46">Tout en ordre</div><div style="font-size:11px;color:#6EE7B7;margin-top:4px">Aucune alerte</div></div>', unsafe_allow_html=True)
        for c, cbg, t, m in alertes:
            st.markdown(f'<div style="background:{cbg};border-left:3px solid {c};border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:7px"><div style="font-size:12.5px;font-weight:700;color:#0F172A">{t}</div><div style="font-size:11px;color:{GRAY_500};margin-top:2px">{m}</div></div>', unsafe_allow_html=True)

    # ── Derniers devis ───────────────────────────────────────────────────────
    with r3d:
        _sec("Derniers Devis")
        try:
            dl = ctrl.get_all_devis()[:5]
            sc = {"brouillon":GRAY_400,"valide":GREEN,"facture":PRIMARY,"annule":RED}
            st.markdown('<div style="background:white;border:1px solid #E2E8F0;border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.05)">', unsafe_allow_html=True)
            if dl:
                for d in dl:
                    c = sc.get(d["statut"], GRAY_400)
                    st.markdown(f'''<div style="padding:9px 14px;border-bottom:1px solid #F8FAFC">
                        <div style="font-size:11.5px;font-weight:700;color:#0F172A">{d["numero"]}</div>
                        <div style="font-size:10.5px;color:{GRAY_400}">{d["client"][:18]}</div>
                        <div style="font-size:11.5px;font-weight:700;color:{c}">{d["montant_ttc"]:,.0f} MAD</div>
                    </div>''', unsafe_allow_html=True)
            else:
                st.markdown('<div style="padding:16px;color:#94A3B8;font-size:12px;text-align:center">Aucun devis</div>', unsafe_allow_html=True)
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