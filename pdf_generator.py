"""
pdf_generator.py — Wassime BTP
Style exact des documents de l'entreprise :
- Logo + filigrane
- En-tête avec infos société
- Tableau professionnel bleu marine
- Pied de page avec infos légales
- UNE SEULE PAGE A4
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas as pdf_canvas
from io import BytesIO
from datetime import date
import os, calendar as cal_mod

# ── Couleurs ───────────────────────────────────────────────────────────────────
BLEU   = colors.HexColor("#1B2A4A")
OR     = colors.HexColor("#C89A4B")
GRIS   = colors.HexColor("#F2F2F2")
BLANC  = colors.white
NOIR   = colors.black
GRIS2  = colors.HexColor("#999999")
ROUGE  = colors.HexColor("#DC2626")

W, H = A4   # 595 x 842 pt
ML = MR = 1.4*cm
# Use logo_doc.jpeg first, fallback to logo_wassime_main.jpeg
_base = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(_base, "logo_wassime_main.jpeg")
if os.path.exists(os.path.join(_base, "logo_doc.jpeg")):
    LOGO = os.path.join(_base, "logo_doc.jpeg")

SIGNATURE = os.path.join(_base, "Signature.jpeg")
# Fallbacks
if not os.path.exists(SIGNATURE):
    SIGNATURE = os.path.join(_base, "Signature_.jpeg")
if not os.path.exists(SIGNATURE):
    SIGNATURE = os.path.join(_base, "signature_BTP.jpeg")


# ── Style helper ────────────────────────────────────────────────────────────────
def S(size=8.5, bold=False, align=TA_LEFT, color=NOIR, leading=None):
    return ParagraphStyle("s", fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=size, leading=leading or size+3.5, textColor=color, alignment=align)

def P(txt, **kw):
    return Paragraph(str(txt or ""), S(**kw))


# ── Montant en lettres ──────────────────────────────────────────────────────────
def _lettres(n):
    u = ["","UN","DEUX","TROIS","QUATRE","CINQ","SIX","SEPT","HUIT","NEUF",
         "DIX","ONZE","DOUZE","TREIZE","QUATORZE","QUINZE","SEIZE",
         "DIX-SEPT","DIX-HUIT","DIX-NEUF"]
    d = ["","","VINGT","TRENTE","QUARANTE","CINQUANTE","SOIXANTE",
         "SOIXANTE-DIX","QUATRE-VINGT","QUATRE-VINGT-DIX"]
    def cent(x):
        if not x: return ""
        c,r = divmod(x,100)
        s = ("CENT" if c==1 else u[c]+" CENT" if c>1 else "") if c else ""
        if not r: return s
        if r<20: return (s+" " if s else "")+u[r]
        dz,un = divmod(r,10)
        suf = u[10+un] if dz in (7,9) else d[dz]+("-"+u[un] if un else "")
        return (s+" " if s else "")+suf
    n = round(float(n or 0),2)
    ent = int(n); cts = round((n-ent)*100)
    mil,rest = divmod(ent,1000)
    parts = []
    if mil==1: parts.append("MILLE")
    elif mil>1: parts.append(cent(mil)+" MILLE")
    if rest: parts.append(cent(rest))
    txt = " ".join(p for p in parts if p) or "ZÉRO"
    return txt + f" DIRHAMS, {cts:02d} CENTIMES TOUTES TAXES COMPRISES"


# ── Canvas de base — dessin en-tête/pied/filigrane ─────────────────────────────
def _draw_page(c, doc_title, doc_num, doc_date):
    """Appelé pour chaque page — dessine logo, filigrane, en-tête, pied."""

    # FILIGRANE logo (opacité 6%)
    if os.path.exists(LOGO):
        c.saveState()
        c.setFillAlpha(0.06)
        try:
            c.drawImage(LOGO, W/2-140, H/2-120, width=280, height=240,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
        c.restoreState()

    # EN-TÊTE ─────────────────────────────────────────────────────────────────
    y_top = H - 0.8*cm

    # Logo — grande taille comme document original
    logo_h = 3.8*cm
    logo_w = 4.8*cm
    if os.path.exists(LOGO):
        try:
            c.drawImage(LOGO, ML, y_top - logo_h,
                        width=logo_w, height=logo_h,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # Texte activité à droite du logo
    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(BLEU)
    txt_x = ML + logo_w + 0.4*cm
    c.drawString(txt_x, y_top - 1.1*cm,
                 "Travaux Divers Ou Construction Transport De Marchandises")
    c.drawString(txt_x, y_top - 1.7*cm,
                 "Vente & Location Des Engins Btp")

    # Pas de lignes de séparation

    # PIED DE PAGE ─────────────────────────────────────────────────────────────
    y_foot = 0.4*cm
    foot_h = 2.2*cm

    # Fond doré
    c.setFillColor(OR)
    c.rect(0, y_foot, W, foot_h, fill=1, stroke=0)

    # ── Colonne gauche : infos légales ────────────────────────────────────────
    c.setFillColor(BLEU)
    c.setFont("Helvetica-Bold", 6.8)
    c.drawString(ML, y_foot + 1.72*cm, "TP  :  60271115          CNSS :  5408680")
    c.setFont("Helvetica", 6.8)
    c.drawString(ML, y_foot + 1.28*cm, "ICE :  003440371000093")
    c.drawString(ML, y_foot + 0.84*cm, "IF   :  60271115           RC  :  4113")
    c.drawString(ML, y_foot + 0.40*cm, "RIB :  145 450 2121167962380017 92 BP")

    # ── Tiret séparateur vertical au centre ───────────────────────────────────
    c.setStrokeColor(BLEU); c.setLineWidth(0.8)
    c.line(W/2, y_foot + 0.25*cm, W/2, y_foot + foot_h - 0.25*cm)

    # ── Colonne droite : contact ──────────────────────────────────────────────
    xr = W/2 + 0.5*cm
    c.setFillColor(BLEU)
    c.setFont("Helvetica-Bold", 6.8)
    c.drawString(xr, y_foot + 1.72*cm, "+212 688 540 102   -   +212 667 848 524")
    c.setFont("Helvetica", 6.8)
    c.drawString(xr, y_foot + 1.28*cm, "DR NOUAJI SIDI BOUOTHMANE , Ben Guérir")
    c.drawString(xr, y_foot + 0.84*cm, "STEWASSIMEBTP@GMAIL.COM")



# ── Build PDF ──────────────────────────────────────────────────────────────────
def _build(draw_fn, doc_title="", doc_num="", doc_date=""):
    """Construit un PDF en une page en utilisant canvas directement."""
    buf = BytesIO()
    c = pdf_canvas.Canvas(buf, pagesize=A4)
    _draw_page(c, doc_title, doc_num, doc_date)
    draw_fn(c)
    c.showPage()
    c.save()
    return buf.getvalue()


# ── Tableau commun ─────────────────────────────────────────────────────────────
def _table_header():
    return [
        P("Désignation", bold=True, align=TA_CENTER, color=BLANC, size=8.5),
        P("U",           bold=True, align=TA_CENTER, color=BLANC, size=8.5),
        P("QTE",         bold=True, align=TA_CENTER, color=BLANC, size=8.5),
        P("P.U H.T",     bold=True, align=TA_CENTER, color=BLANC, size=8.5),
        P("Montant",     bold=True, align=TA_CENTER, color=BLANC, size=8.5),
    ]

def _table_style(n_rows):
    return TableStyle([
        ('BACKGROUND',   (0,0),(-1,0), BLEU),
        ('TEXTCOLOR',    (0,0),(-1,0), BLANC),
        ('ROWBACKGROUND',(0,1),(-1,n_rows-1), [BLANC, GRIS]),
        ('GRID',         (0,0),(-1,n_rows-1), 0.4, colors.HexColor("#CCCCCC")),
        ('VALIGN',       (0,0),(-1,-1), 'MIDDLE'),
        ('LEFTPADDING',  (0,0),(-1,-1), 5),
        ('RIGHTPADDING', (0,0),(-1,-1), 5),
        ('TOPPADDING',   (0,0),(-1,-1), 4),
        ('BOTTOMPADDING',(0,0),(-1,-1), 4),
        ('ROWHEIGHT',    (0,1),(-1,-1), 0.65*cm),
    ])

def _totaux_block(ht, tva_taux, tva, ttc, red=0):
    rows = []
    if red > 0:
        rows.append(["", P("RÉDUCTION",  bold=True, align=TA_RIGHT, color=ROUGE, size=9),
                         P(f"-{red:,.2f}",align=TA_RIGHT, color=ROUGE, size=9)])
    rows += [
        ["", P("TOTAL H.T",  bold=True, align=TA_RIGHT, color=BLEU, size=9),
             P(f"{ht:,.2f}", align=TA_RIGHT, size=9)],
        ["", P(f"T.V.A {tva_taux:.0f}%", bold=True, align=TA_RIGHT, color=BLEU, size=9),
             P(f"{tva:,.2f}", align=TA_RIGHT, size=9)],
        ["", P("TOTAL T.T.C", bold=True, align=TA_RIGHT, color=BLEU, size=10),
             P(f"{ttc:,.2f}", bold=True, align=TA_RIGHT, color=BLEU, size=10)],
    ]
    AW = W - ML - MR
    t = Table(rows, colWidths=[AW*0.55, AW*0.25, AW*0.20])
    t.setStyle(TableStyle([
        ('BACKGROUND', (1,-1),(-1,-1), GRIS),
        ('LINEBELOW',  (1,-1),(-1,-1), 1.2, BLEU),
        ('LEFTPADDING',(0,0),(-1,-1), 4),('RIGHTPADDING',(0,0),(-1,-1),4),
        ('TOPPADDING', (0,0),(-1,-1), 4),('BOTTOMPADDING',(0,0),(-1,-1),4),
    ]))
    return t


def _draw_signatures(c, y):
    """Dessine uniquement la signature société à droite, centrée entre le contenu et le pied de page."""
    if not os.path.exists(SIGNATURE):
        return
    # Pied de page : y_foot=0.4cm, foot_h=2.2cm → top à 2.6cm
    y_footer_top = 0.4*cm + 2.2*cm  # = 2.6cm
    sig_w = 7.0*cm
    sig_h = 4.0*cm
    espace = y - y_footer_top
    sig_y = y_footer_top + (espace - sig_h) / 2
    sig_x = W - MR - sig_w
    try:
        c.drawImage(SIGNATURE,
                    sig_x, sig_y,
                    width=sig_w, height=sig_h,
                    preserveAspectRatio=True, mask='auto')
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════════
#  DEVIS
# ═══════════════════════════════════════════════════════════════════════════════
def generer_devis_pdf(data: dict) -> bytes:
    num   = data.get("numero","")
    today = date.today().strftime("%d/%m/%Y")
    cli   = data.get("client_nom","")
    ice   = data.get("client_ice","")
    adr   = data.get("client_adresse","")
    d_deb = data.get("date_debut")
    d_fin = data.get("date_fin")
    deb_s = d_deb.strftime("%d/%m/%Y") if d_deb else "—"
    fin_s = d_fin.strftime("%d/%m/%Y") if d_fin else "—"
    duree = (d_fin - d_deb).days if d_deb and d_fin else 0
    lignes= data.get("lignes",[])
    ht    = data.get("montant_ht",0)
    tva   = data.get("montant_tva",0)
    taux  = data.get("tva_taux",20)
    ttc   = data.get("montant_ttc",0)
    AW    = W - ML - MR
    TOP   = H - 5.5*cm  # début zone contenu (sous séparateur)

    def draw(c):
        y = TOP

        # Titre
        c.setFont("Helvetica-Bold", 14); c.setFillColor(BLEU)
        c.drawCentredString(W/2, y, f"DEVIS N° {num}")
        y -= 0.7*cm

        # Infos client
        c.setFont("Helvetica-Bold", 8.5); c.setFillColor(BLEU)
        c.drawString(ML, y, f"CLIENT : {cli}")
        c.setFont("Helvetica-Oblique", 8.5)
        c.drawRightString(W-MR, y, f"Marrakech le : {today}")
        y -= 0.45*cm
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(ML, y, f"ICE N° : {ice}")
        y -= 0.45*cm
        c.drawString(ML, y, f"Période : du {deb_s} au {fin_s} ({duree} jours)")
        y -= 0.45*cm
        c.drawString(ML, y, "Objet : LOCATION ENGINS DE CHANTIER .")
        y -= 0.5*cm

        # Tableau — uniquement les lignes avec contenu
        rows = [_table_header()]
        for l in lignes:
            nom   = l.get("engin_nom","")
            prix  = l.get("prix_unitaire",0)
            qte   = l.get("quantite",1)
            qte_total = qte * duree  # quantité × durée en jours
            tot   = prix * qte_total  # FORMULE CORRECTE : prix × qte × durée
            rows.append([
                P(f"LOCATION {nom.upper()}", size=8.5),
                P("Jr.", align=TA_CENTER, size=8.5),
                P(f"{qte_total:.2f}", align=TA_CENTER, size=8.5),
                P(f"{prix:,.2f}", align=TA_RIGHT, size=8.5),
                P(f"{tot:,.2f}", align=TA_RIGHT, size=8.5),
            ])
        # Pas de lignes vides — tableau uniquement avec le contenu réel

        cw = [AW*0.44, AW*0.08, AW*0.12, AW*0.18, AW*0.18]
        t = Table(rows, colWidths=cw)
        t.setStyle(_table_style(len(rows)))
        t.wrapOn(c, AW, H); t.drawOn(c, ML, y - t._height); y -= t._height + 0.35*cm

        # Totaux
        tt = _totaux_block(ht, taux, tva, ttc)
        tt.wrapOn(c, AW, H); tt.drawOn(c, ML, y - tt._height); y -= tt._height + 0.4*cm

        # Arrêté
        c.setFont("Helvetica", 8.5); c.setFillColor(BLEU)
        c.drawString(ML, y, "Arrêtée le présent Devis à la somme de :")
        y -= 0.4*cm
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(W/2, y, _lettres(ttc))
        y -= 1.2*cm

        # Signatures
        _draw_signatures(c, y)

    return _build(draw, "DEVIS", num, today)


# ═══════════════════════════════════════════════════════════════════════════════
#  FACTURE
# ═══════════════════════════════════════════════════════════════════════════════
def generer_facture_pdf(data: dict) -> bytes:
    num    = data.get("numero","")
    d_emis = data.get("date_emission")
    today  = d_emis.strftime("%d/%m/%Y") if d_emis else date.today().strftime("%d/%m/%Y")
    devis  = data.get("devis") or {}
    cli    = data.get("client_nom","") or devis.get("client_nom","")
    ice    = data.get("client_ice","") or devis.get("client_ice","")
    att    = data.get("attachement_numero","")
    ht     = data.get("montant_ht",0)
    tva    = data.get("montant_tva",0)
    taux   = data.get("tva_taux",20)
    red    = data.get("reduction",0)
    ttc    = data.get("montant_ttc",0)
    AW     = W - ML - MR
    TOP    = H - 5.5*cm

    # Construire un index prix depuis le devis pour fallback
    _prix_index = {}  # engin_nom_partiel → prix_unitaire
    _duree_devis = 0
    if devis.get("lignes"):
        d_deb_f = devis.get("date_debut")
        d_fin_f = devis.get("date_fin")
        _duree_devis = (d_fin_f - d_deb_f).days if d_deb_f and d_fin_f else 1
        for _l in devis["lignes"]:
            _nom = _l.get("engin_nom","").upper()
            _mat = _l.get("matricule","").upper()
            _prix_index[_nom] = _l.get("prix_unitaire", 0)
            if _mat:
                _prix_index[_mat] = _l.get("prix_unitaire", 0)

    def _get_prix_from_index(designation):
        """Retrouve le prix unitaire depuis le devis via la désignation."""
        desig = designation.upper().replace("LOCATION ", "")
        # Recherche exacte
        for k, v in _prix_index.items():
            if k in desig or desig in k:
                return v
        return 0

    # Lignes depuis attachements
    lignes_att = data.get("lignes_attachement") or []
    if not lignes_att and devis.get("lignes"):
        for _l in devis["lignes"]:
            qte_f  = _l.get("quantite", 1)
            prix_f = _l.get("prix_unitaire", 0)
            qte_tot = qte_f * _duree_devis
            lignes_att.append({
                "designation": f"LOCATION {_l.get('engin_nom','').upper()}",
                "qte":     qte_tot,
                "prix":    prix_f,
                "montant": prix_f * qte_tot,
            })

    # Corriger les lignes : prix et montant si manquants — NE PAS toucher qte
    lignes_att_fixed = []
    for l in lignes_att:
        prix  = l.get("prix", 0) or 0
        qte   = l.get("qte", 0) or 0
        desig = l.get("designation", "")

        # Si prix est 0 → chercher dans le devis
        if prix == 0:
            prix = _get_prix_from_index(desig)

        # Montant = prix × qte (qte vient du controller, déjà correct par engin)
        mont = round(prix * qte, 2)

        lignes_att_fixed.append({
            "designation": desig,
            "qte":     qte,
            "prix":    prix,
            "montant": mont,
        })
    lignes_att = lignes_att_fixed

    def draw(c):
        y = TOP
        c.setFont("Helvetica-Bold", 14); c.setFillColor(BLEU)
        c.drawCentredString(W/2, y, f"FACTURE N° {num}")
        y -= 0.7*cm

        c.setFont("Helvetica-Bold", 8.5); c.setFillColor(BLEU)
        c.drawString(ML, y, f"CLIENT : {cli} .")
        c.setFont("Helvetica-Oblique", 8.5)
        c.drawRightString(W-MR, y, f"Marrakech le : {today}")
        y -= 0.45*cm
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(ML, y, f"ICE N° : {ice}")
        y -= 0.45*cm
        c.drawString(ML, y, "Objet : LOCATION ENGINS DE CHANTIER .")
        y -= 0.45*cm
        if att:
            c.drawString(ML, y, f"Attach : {att} .")
            y -= 0.5*cm
        else:
            y -= 0.1*cm

        rows = [_table_header()]
        for l in lignes_att:
            rows.append([
                P(l.get("designation",""), size=8.5),
                P("Jr.", align=TA_CENTER, size=8.5),
                P(f"{l.get('qte',0):.2f}", align=TA_CENTER, size=8.5),
                P(f"{l.get('prix',0):,.2f}", align=TA_RIGHT, size=8.5),
                P(f"{l.get('montant',0):,.2f}", align=TA_RIGHT, size=8.5),
            ])
        # Pas de lignes vides — tableau uniquement avec le contenu réel

        cw = [AW*0.44, AW*0.08, AW*0.12, AW*0.18, AW*0.18]
        t = Table(rows, colWidths=cw)
        t.setStyle(_table_style(len(rows)))
        t.wrapOn(c, AW, H); t.drawOn(c, ML, y-t._height); y -= t._height+0.35*cm

        tt = _totaux_block(ht, taux, tva, ttc, red)
        tt.wrapOn(c, AW, H); tt.drawOn(c, ML, y-tt._height); y -= tt._height+0.4*cm

        c.setFont("Helvetica", 8.5); c.setFillColor(BLEU)
        c.drawString(ML, y, "Arrêtée la présente Facture à la somme de :")
        y -= 0.4*cm
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(W/2, y, _lettres(ttc))
        y -= 1.2*cm

        # Signatures
        _draw_signatures(c, y)

    return _build(draw, "FACTURE", num, today)


# ═══════════════════════════════════════════════════════════════════════════════
#  BON DE LIVRAISON
# ═══════════════════════════════════════════════════════════════════════════════
def generer_bl_pdf(data: dict) -> bytes:
    num   = data.get("numero","")
    d_liv = data.get("date_livraison")
    today = d_liv.strftime("%d/%m/%Y") if d_liv else date.today().strftime("%d/%m/%Y")
    devis = data.get("devis") or {}
    cli   = devis.get("client_nom","")
    ice   = devis.get("client_ice","")
    adr   = devis.get("client_adresse","")
    lieu  = data.get("lieu_livraison","") or adr
    cmd   = data.get("commande_numero","")
    d_deb = devis.get("date_debut")
    d_fin = devis.get("date_fin")
    duree = (d_fin - d_deb).days if d_deb and d_fin else 0
    lignes= devis.get("lignes",[])
    taux  = devis.get("tva_taux",20)
    AW    = W - ML - MR
    TOP   = H - 5.5*cm

    def draw(c):
        y = TOP
        c.setFont("Helvetica-Bold", 13); c.setFillColor(BLEU)
        c.drawCentredString(W/2, y, f"BON DE LIVRAISON N° {num}")
        y -= 0.7*cm

        c.setFont("Helvetica-Bold", 8.5); c.setFillColor(BLEU)
        c.drawString(ML, y, f"CLIENT : {cli}")
        c.setFont("Helvetica-Oblique", 8.5)
        c.drawRightString(W-MR, y, f"Marrakech le : {today}")
        y -= 0.45*cm
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(ML, y, f"ICE N° : {ice}")
        y -= 0.45*cm
        c.drawString(ML, y, f"BC N° : {cmd}")
        y -= 0.45*cm
        c.drawString(ML, y, f"Chantier : {lieu}")
        y -= 0.45*cm
        c.drawString(ML, y, "Objet : LOCATION DES ENGINS .")
        y -= 0.55*cm

        # Tableau — uniquement les lignes avec contenu
        hdr = [P("Désignation",bold=True,align=TA_CENTER,color=BLANC,size=8.5),
               P("U",bold=True,align=TA_CENTER,color=BLANC,size=8.5),
               P("QTE",bold=True,align=TA_CENTER,color=BLANC,size=8.5),
               P("P.U H.T",bold=True,align=TA_CENTER,color=BLANC,size=8.5),
               P("Montant",bold=True,align=TA_CENTER,color=BLANC,size=8.5)]
        rows = [hdr]
        ht_calc = 0
        for l in lignes:
            nom  = l.get("engin_nom","")
            prix = l.get("prix_unitaire",0)
            qte  = l.get("quantite",1)
            qte_total = qte * duree if duree else qte
            tot  = prix * qte_total  # FORMULE CORRECTE : prix × qte × durée
            ht_calc += tot
            rows.append([
                P(f"LOCATION {nom.upper()}", size=8.5),
                P("Jr.", align=TA_CENTER, size=8.5),
                P(f"{qte_total:.2f}", align=TA_CENTER, size=8.5),
                P(f"{prix:,.2f}", align=TA_RIGHT, size=8.5),
                P(f"{tot:,.2f}", align=TA_RIGHT, size=8.5),
            ])
        # Pas de lignes vides — tableau uniquement avec le contenu réel

        # Recalcul des totaux depuis les lignes réelles
        tva_calc = round(ht_calc * taux / 100, 2)
        ttc_calc = round(ht_calc + tva_calc, 2)

        cw = [AW*0.44, AW*0.08, AW*0.12, AW*0.18, AW*0.18]
        t = Table(rows, colWidths=cw)
        t.setStyle(_table_style(len(rows)))
        t.wrapOn(c, AW, H); t.drawOn(c, ML, y-t._height); y -= t._height+0.35*cm

        tt = _totaux_block(ht_calc, taux, tva_calc, ttc_calc)
        tt.wrapOn(c, AW, H); tt.drawOn(c, ML, y-tt._height); y -= tt._height+0.4*cm

        c.setFont("Helvetica", 8.5); c.setFillColor(BLEU)
        c.drawString(ML, y, "Arrêtée la présente Facture à la somme de :")
        y -= 0.4*cm
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(W/2, y, _lettres(ttc_calc))

        # Signatures
        y -= 1.2*cm
        _draw_signatures(c, y)

    return _build(draw, "BON DE LIVRAISON", num, today)


# ═══════════════════════════════════════════════════════════════════════════════
#  ATTACHEMENT — Multi-engins, style tableau exact
# ═══════════════════════════════════════════════════════════════════════════════
def generer_attachement_pdf(data: dict) -> bytes:
    num    = data.get("numero","")
    mois   = int(data.get("mois", date.today().month))
    annee  = int(data.get("annee", date.today().year))
    devis  = data.get("devis") or {}
    cli    = devis.get("client_nom","")
    projet = data.get("projet","")
    nb_j_m = cal_mod.monthrange(annee, mois)[1]
    last_day = f"{nb_j_m}/{mois}/{annee}"
    AW     = W - ML - MR
    TOP    = H - 5.5*cm

    # Engins dans cet attachement
    engins_att = data.get("engins_lignes", [])
    if not engins_att:
        engins_att = [{
            "nom": (data.get("engin_nom","") + " / " + data.get("matricule","")).strip(" /"),
            "jours": data.get("jours",[]),
            "total": data.get("nb_jours",0) or data.get("nb_jours_travailles",0),
        }]

    def draw(c):
        y = TOP

        # Titre
        c.setFont("Helvetica-Bold", 13); c.setFillColor(BLEU)
        c.drawCentredString(W/2, y, f"ATTACHEMENT du Mois : {mois:02d}/{annee}")
        y -= 0.6*cm

        # Infos
        c.setFont("Helvetica-Bold", 8.5); c.setFillColor(BLEU)
        c.drawString(ML, y, f"CLIENT : {cli}")
        c.setFont("Helvetica-Oblique", 8.5)
        c.drawRightString(W-MR, y, f"Marrakech le : {last_day}")
        y -= 0.42*cm
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(ML, y, f"Chantier : {projet}")
        y -= 0.42*cm
        c.drawString(ML, y, "Objet : LOCATION DES ENGINS .")
        y -= 0.5*cm

        # Tableau attachement multi-engins
        n_eng  = len(engins_att)
        c_date = 1.9*cm
        c_obs  = 2.2*cm
        c_eng  = (AW - c_date - c_obs) / max(n_eng, 1)

        # Calcul hauteur dispo
        h_available = y - 3.5*cm  # espace pour le tableau
        row_h = min(0.40*cm, h_available / (nb_j_m + 3))  # adapte si nécessaire

        # Construire le tableau
        # Ligne 1 header: DATE/ENGINS | Nom Engin 1 | Nom Engin 2 | OBS
        # Ligne 2 header:             | Nbr Jours   | Nbr Jours   |
        h1 = [P("DATE/ENGINS", bold=True, align=TA_CENTER, color=BLANC, size=7)]
        h2 = [P("", size=6)]
        for e in engins_att:
            h1.append(P(e["nom"].upper(), bold=True, align=TA_CENTER, color=BLANC, size=6.5))
            h2.append(P("Nbr des Jours", bold=True, align=TA_CENTER, color=BLANC, size=6.5))
        h1.append(P("OBSERVATION", bold=True, align=TA_CENTER, color=BLANC, size=7))
        h2.append(P("", size=6))

        rows = [h1, h2]
        totaux = [0.0]*n_eng

        for j in range(1, nb_j_m+1):
            row = [P(f"{j}/{mois}/{annee}", align=TA_CENTER, size=6.5)]
            for ei, e in enumerate(engins_att):
                val = 0.0
                for jt in e.get("jours",[]):
                    if isinstance(jt,(list,tuple)) and len(jt)>=2 and int(jt[0])==j:
                        val = float(jt[1]); break
                totaux[ei] += val
                row.append(P(f"{val:.2f}" if val>0 else "", align=TA_CENTER, size=6.5))
            row.append(P("", size=6))
            rows.append(row)

        # Ligne total
        tot_row = [P("Total en jours", bold=True, align=TA_CENTER, color=BLANC, size=7)]
        for tv in totaux:
            tot_row.append(P(f"{tv:.2f}", bold=True, align=TA_CENTER, color=BLANC, size=7))
        tot_row.append(P("", size=6))
        rows.append(tot_row)

        cw = [c_date] + [c_eng]*n_eng + [c_obs]
        nr = len(rows)

        ts = TableStyle([
            ('BACKGROUND',   (0,0), (-1,1),    BLEU),
            ('BACKGROUND',   (0,nr-1),(-1,nr-1), BLEU),
            ('TEXTCOLOR',    (0,0), (-1,1),    BLANC),
            ('TEXTCOLOR',    (0,nr-1),(-1,nr-1), BLANC),
            ('ROWBACKGROUND',(0,2), (-1,nr-2), [BLANC, GRIS]),
            ('GRID',         (0,0), (-1,-1),   0.3, colors.HexColor("#AAAAAA")),
            ('ALIGN',        (0,0), (-1,-1),   'CENTER'),
            ('VALIGN',       (0,0), (-1,-1),   'MIDDLE'),
            ('LEFTPADDING',  (0,0), (-1,-1),   2),
            ('RIGHTPADDING', (0,0), (-1,-1),   2),
            ('TOPPADDING',   (0,0), (-1,-1),   1.5),
            ('BOTTOMPADDING',(0,0), (-1,-1),   1.5),
            ('SPAN',         (0,0), (0,1)),
            ('SPAN',         (-1,0),(-1,1)),
            ('FONTNAME',     (0,0), (-1,1),    'Helvetica-Bold'),
            ('FONTNAME',     (0,nr-1),(-1,nr-1),'Helvetica-Bold'),
        ])

        t = Table(rows, colWidths=cw)
        t.setStyle(ts)
        t.wrapOn(c, AW, H)
        t.drawOn(c, ML, y - t._height)

    return _build(draw, "ATTACHEMENT", num, last_day)


# ═══════════════════════════════════════════════════════════════════════════════
#  ATTESTATION DE RETARD
# ═══════════════════════════════════════════════════════════════════════════════
def generer_attestation_retard_pdf(data: dict) -> bytes:
    num       = data.get("numero","")
    today     = date.today().strftime("%d/%m/%Y")
    cli_nom   = data.get("client_nom","")
    fac_num   = data.get("facture_numero","")
    nb_jours  = data.get("nb_jours_retard",0)
    capital   = data.get("montant_capital",0)
    interets  = data.get("montant_interets",0)
    total_att = data.get("montant_total", capital+interets)
    taux      = data.get("taux_interet",1.5)
    AW        = W - ML - MR
    TOP       = H - 5.5*cm

    # Extraire période depuis notes si présent
    notes_raw = data.get("notes","") or ""
    taux_label = ""
    notes_propres = notes_raw
    if notes_raw.startswith("[Taux :"):
        end_bracket = notes_raw.find("]")
        if end_bracket != -1:
            taux_label = notes_raw[8:end_bracket]
            notes_propres = notes_raw[end_bracket+2:].strip()

    def draw(c):
        y = TOP

        # Titre
        c.setFont("Helvetica-Bold", 13); c.setFillColor(BLEU)
        c.drawCentredString(W/2, y, "ATTESTATION DE RETARD DE PAIEMENT")
        y -= 0.4*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(W/2, y, f"N° {num}")
        y -= 0.8*cm

        # Date à droite
        c.setFont("Helvetica-Oblique", 9); c.setFillColor(BLEU)
        c.drawRightString(W-MR, y, f"Marrakech le : {today}")
        y -= 0.8*cm

        # Infos client + facture
        c.setFont("Helvetica-Bold", 9.5); c.setFillColor(BLEU)
        c.drawString(ML, y, f"CLIENT : {cli_nom}")
        y -= 0.5*cm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(ML, y, f"Facture N° : {fac_num}")
        y -= 0.5*cm
        c.drawString(ML, y, f"Jours de retard : {nb_jours} jour(s)")
        if taux_label:
            y -= 0.45*cm
            c.drawString(ML, y, f"Taux appliqué : {taux_label}")
        y -= 0.7*cm

        # Corps du texte
        c.setFont("Helvetica", 9); c.setFillColor(BLEU)
        corps = [
            "La société WASSIME BTP atteste par la présente que :",
            "",
            f"Le client {cli_nom} présente un retard de paiement",
            f"concernant la facture N° {fac_num}.",
            "",
            "Malgré nos relances, le règlement de cette facture n'a pas été effectué",
            "dans les délais convenus.",
        ]
        if taux > 0:
            corps += [
                "",
                f"En application de notre politique de retard, des intérêts",
                f"sont calculés au taux de : {taux_label or str(taux)+'%'}.",
            ]
        for line in corps:
            c.drawString(ML, y, line)
            y -= 0.42*cm
        y -= 0.3*cm

        # Texte libre si présent
        if notes_propres:
            y -= 0.1*cm
            c.setFont("Helvetica-Oblique", 8.5)
            # Wrap long text
            words = notes_propres.split()
            line_cur = ""
            for word in words:
                test = line_cur + " " + word if line_cur else word
                if c.stringWidth(test, "Helvetica-Oblique", 8.5) < AW - 1*cm:
                    line_cur = test
                else:
                    c.drawString(ML, y, line_cur)
                    y -= 0.4*cm
                    line_cur = word
            if line_cur:
                c.drawString(ML, y, line_cur)
                y -= 0.5*cm

        y -= 0.2*cm

        # Tableau récapitulatif — seulement le montant impayé
        rows = [
            [P("<b>Désignation</b>", bold=True, align=TA_CENTER, color=BLANC, size=9),
             P("<b>Montant (MAD)</b>", bold=True, align=TA_CENTER, color=BLANC, size=9)],
            [P(f"Montant impayé — Facture {fac_num}", size=9, color=BLEU),
             P(f"{capital:,.2f}", align=TA_RIGHT, size=9)],
        ]
        if interets > 0:
            rows.append([
                P(f"Intérêts de retard ({taux_label or str(taux)+'%'})",
                  size=9, color=ROUGE),
                P(f"+{interets:,.2f}", align=TA_RIGHT, size=9, color=ROUGE),
            ])
        rows.append([
            P("<b>TOTAL DÛ</b>", bold=True, size=10, color=BLEU),
            P(f"<b>{total_att:,.2f}</b>", bold=True, align=TA_RIGHT, size=10, color=BLEU),
        ])

        nr = len(rows)
        t = Table(rows, colWidths=[AW*0.65, AW*0.35])
        t.setStyle(TableStyle([
            ('BACKGROUND',   (0,0),  (-1,0),   BLEU),
            ('BACKGROUND',   (0,nr-1),(-1,nr-1), GRIS),
            ('LINEBELOW',    (0,nr-1),(-1,nr-1), 1.5, BLEU),
            ('ROWBACKGROUND',(0,1),  (-1,nr-2), [BLANC, GRIS]),
            ('GRID',         (0,0),  (-1,-1),   0.4, colors.HexColor("#CCCCCC")),
            ('LEFTPADDING',  (0,0),  (-1,-1),   8),
            ('RIGHTPADDING', (0,0),  (-1,-1),   8),
            ('TOPPADDING',   (0,0),  (-1,-1),   6),
            ('BOTTOMPADDING',(0,0),  (-1,-1),   6),
            ('ROWHEIGHT',    (0,1),  (-1,-1),   0.7*cm),
        ]))
        t.wrapOn(c, AW, H); t.drawOn(c, ML, y - t._height); y -= t._height + 0.5*cm

        # Arrêté en lettres
        c.setFont("Helvetica", 8.5); c.setFillColor(BLEU)
        c.drawString(ML, y, "Arrêtée la présente attestation à la somme de :")
        y -= 0.4*cm
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(W/2, y, _lettres(total_att))
        y -= 1.2*cm

        # Signatures
        _draw_signatures(c, y)

    return _build(draw, "ATTESTATION RETARD", num, today)