"""
pdf_generator.py — Wassime BTP
PDF professionnel sur UNE SEULE PAGE A4 avec vrai logo extrait du devis original.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage
)
from io import BytesIO
from datetime import date
import os

# ── Couleurs ──────────────────────────────────────────────────────────────────
BLEU   = colors.HexColor("#1B2A4A")
ORANGE = colors.HexColor("#E8671B")
GRIS   = colors.HexColor("#F5F7FA")
GRIS2  = colors.HexColor("#CCCCCC")
BLANC  = colors.white
NOIR   = colors.black
VERT   = colors.HexColor("#059669")
ROUGE  = colors.HexColor("#DC2626")

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_wassime.jpeg")

W_PAGE, H_PAGE = A4          # 595.3 x 841.9 pt
ML = MR = 1.4 * cm
MT = 1.0 * cm
MB = 1.2 * cm
AW = W_PAGE - ML - MR        # largeur utile ≈ 538 pt ≈ 18.98 cm


# ── Style factory ─────────────────────────────────────────────────────────────
def _s(name, size=8.5, bold=False, align=TA_LEFT, color=NOIR, leading=None):
    return ParagraphStyle(
        name,
        fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=size,
        leading=leading or (size + 3),
        textColor=color,
        alignment=align,
    )


def _p(txt, style):
    return Paragraph(txt or "", style)


# ── Montant en lettres ────────────────────────────────────────────────────────
def _lettres(n):
    u = ["","UN","DEUX","TROIS","QUATRE","CINQ","SIX","SEPT","HUIT","NEUF",
         "DIX","ONZE","DOUZE","TREIZE","QUATORZE","QUINZE","SEIZE",
         "DIX-SEPT","DIX-HUIT","DIX-NEUF"]

    def inf100(x):
        if x == 0: return ""
        if x < 20: return u[x]
        q, r = divmod(x, 10)
        if q == 7: return "SOIXANTE-" + u[r + 10]
        if q == 8: return "QUATRE-VINGTS" if r == 0 else "QUATRE-VINGT-" + u[r]
        if q == 9: return "QUATRE-VINGT-" + u[r + 10]
        d = ["","DIX","VINGT","TRENTE","QUARANTE","CINQUANTE","SOIXANTE"]
        return d[q] + ("-" + u[r] if r else "")

    def inf1000(x):
        if x == 0: return ""
        c, r = divmod(x, 100)
        if c == 0: return inf100(r)
        cs = ("CENT" if c == 1 else u[c] + " CENT") + ("S" if r == 0 and c > 1 else "")
        return cs + (" " + inf100(r) if r else "")

    entier = int(n)
    cts = round((n - entier) * 100)
    if entier == 0:
        mots = "ZÉRO"
    elif entier < 1000:
        mots = inf1000(entier)
    elif entier < 1_000_000:
        m, r = divmod(entier, 1000)
        mots = ("MILLE" if m == 1 else inf1000(m) + " MILLE") + (" " + inf1000(r) if r else "")
    else:
        mil, r = divmod(entier, 1_000_000)
        mots = inf1000(mil) + " MILLIONS"
        if r:
            m2, r2 = divmod(r, 1000)
            if m2: mots += " " + ("MILLE" if m2 == 1 else inf1000(m2) + " MILLE")
            if r2: mots += " " + inf1000(r2)
    res = mots.strip() + " DIRHAMS"
    if cts:
        res += " ET " + inf100(cts) + " CENTIMES"
    return res


# ── Constructeur de document ──────────────────────────────────────────────────
def _build_pdf(data: dict, doc_type: str) -> bytes:
    buf = BytesIO()

    # ── Préparer les données ───────────────────────────────────────────────────
    numero     = data.get("numero", "")
    if doc_type == "DEVIS":
        date_doc   = data.get("date_creation") or date.today()
        client_nom = data.get("client_nom", "")
        client_ice = data.get("client_ice", "")
        client_tel = data.get("client_tel", "")
        client_adr = data.get("client_adresse", "")
        date_debut = data.get("date_debut")
        date_fin   = data.get("date_fin")
        duree      = data.get("duree_jours", 0)
        lignes_src = data.get("lignes", [])
        ht         = data.get("montant_ht", 0)
        tva_taux   = data.get("tva_taux", 20)
        tva        = data.get("montant_tva", 0)
        ttc        = data.get("montant_ttc", 0)
        red        = 0.0
        red_pct    = 0.0
        notes      = data.get("notes", "")
    else:  # FACTURE
        date_doc   = data.get("date_emission") or date.today()
        devis      = data.get("devis") or {}
        client_nom = devis.get("client_nom", "")
        client_ice = devis.get("client_ice", "")
        client_tel = devis.get("client_tel", "")
        client_adr = devis.get("client_adresse", "")
        date_debut = devis.get("date_debut")
        date_fin   = devis.get("date_fin")
        duree      = devis.get("duree_jours", 0)
        lignes_src = data.get("lignes") or devis.get("lignes", [])
        ht         = data.get("montant_ht")  or devis.get("montant_ht", 0)
        tva_taux   = data.get("tva_taux")    or devis.get("tva_taux", 20)
        tva        = data.get("montant_tva") or devis.get("montant_tva", 0)
        ttc        = data.get("montant_ttc", 0)
        red        = data.get("reduction", 0) or 0
        red_pct    = data.get("reduction_pct", 0) or 0
        notes      = data.get("notes", "")

    date_str   = date_doc.strftime("%d/%m/%Y") if hasattr(date_doc, "strftime") else str(date_doc)
    debut_str  = date_debut.strftime("%d/%m/%Y") if date_debut else "—"
    fin_str    = date_fin.strftime("%d/%m/%Y")   if date_fin   else "—"

    # ── Styles ────────────────────────────────────────────────────────────────
    sN    = _s("N")
    sNB   = _s("NB",  bold=True)
    sNR   = _s("NR",  align=TA_RIGHT)
    sNBR  = _s("NBR", bold=True, align=TA_RIGHT)
    sNC   = _s("NC",  align=TA_CENTER)
    sNBC  = _s("NBC", bold=True, align=TA_CENTER)
    sTH   = _s("TH",  bold=True, align=TA_CENTER, color=BLANC)
    sFT   = _s("FT",  size=6.8, align=TA_CENTER,  color=colors.HexColor("#555555"))
    sTITRE= _s("TITRE", size=12, bold=True, align=TA_RIGHT, color=BLEU)
    sDATE = _s("DATE",  size=8,  align=TA_RIGHT,  color=NOIR)
    sLTTR = _s("LTTR",  size=8,  align=TA_CENTER, color=BLEU, bold=True)
    sSIG  = _s("SIG",   size=7.5, align=TA_CENTER, color=colors.HexColor("#444444"))

    story = []

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. EN-TÊTE : Logo réel + Titre document
    # ═══════════════════════════════════════════════════════════════════════════
    logo_w = AW * 0.60
    logo_h = logo_w * (141 / 723)   # ratio réel du logo

    if os.path.exists(LOGO_PATH):
        logo_img = RLImage(LOGO_PATH, width=logo_w, height=logo_h)
    else:
        logo_img = _p("<b>Ste Wassime BTP</b>", _s("LG", size=12, bold=True, color=BLEU))

    titre_block = Table([[
        _p(f"<b>{doc_type} N°{numero}</b>", sTITRE),
    ],[
        _p(f"Marrakech le : <i>{date_str}</i>", sDATE),
    ]], colWidths=[AW * 0.38])
    titre_block.setStyle(TableStyle([
        ("ALIGN",        (0, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING",   (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
    ]))

    header = Table([[logo_img, titre_block]],
                   colWidths=[AW * 0.62, AW * 0.38])
    header.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))
    story.append(header)
    story.append(HRFlowable(width="100%", thickness=2, color=ORANGE, spaceAfter=5, spaceBefore=4))

    # ═══════════════════════════════════════════════════════════════════════════
    # 2. BLOC CLIENT + OBJET
    # ═══════════════════════════════════════════════════════════════════════════
    ref_label = "Réf. Devis" if doc_type == "FACTURE" else ""
    ref_val   = (data.get("devis") or {}).get("numero", "") if doc_type == "FACTURE" else ""

    echeance_str = ""
    if doc_type == "FACTURE" and data.get("echeance"):
        echeance_str = data["echeance"].strftime("%d/%m/%Y")

    col_left  = [
        [_p(f"<b>CLIENT :</b> {client_nom}", sNB)],
        [_p(f"<b>ICE N° :</b> {client_ice or '—'}", sN)],
        [_p(f"<b>Tél :</b> {client_tel or '—'}", sN)],
    ]
    col_right = [
        [_p(f"<b>Période :</b> Du {debut_str} au {fin_str}  ({duree} jr)", sN)],
        [_p("<b>Objet :</b> LOCATION ENGINS DE CHANTIER", sNB)],
        [_p(f"<b>{ref_label} :</b> {ref_val}" if ref_label else
            f"<b>Statut :</b> {data.get('statut','').upper()}", sN)],
    ]
    if echeance_str:
        col_right.append([_p(f"<b>Échéance :</b> {echeance_str}", sN)])
        col_left.append( [_p("", sN)])

    t_client = Table(
        [[Table(col_left,  colWidths=[AW * 0.48]),
          Table(col_right, colWidths=[AW * 0.48])]],
        colWidths=[AW * 0.50, AW * 0.50]
    )
    t_client.setStyle(TableStyle([
        ("BOX",          (0, 0), (-1, -1), 0.5,  GRIS2),
        ("BACKGROUND",   (0, 0), (-1, -1), GRIS),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_client)
    story.append(Spacer(1, 5))

    # ═══════════════════════════════════════════════════════════════════════════
    # 3. TABLEAU DES LIGNES
    # ═══════════════════════════════════════════════════════════════════════════
    cw = [AW - 4*cm - 2.8*cm - 3*cm, 1.5*cm, 2.5*cm, 2.5*cm, 3*cm]
    # [Désignation, U, QTE, P.U H.T, Montant]

    rows = [[
        _p("<b>Désignation</b>", sTH),
        _p("<b>U</b>",           sTH),
        _p("<b>QTE</b>",         sTH),
        _p("<b>P.U H.T</b>",     sTH),
        _p("<b>Montant</b>",      sTH),
    ]]

    for l in lignes_src:
        rows.append([
            _p(l.get("description") or l.get("engin_nom", ""), sN),
            _p("Jr",                                             sNC),
            _p(f"{l['quantite']:.2f}",                          sNC),
            _p(f"{l['prix_unitaire']:,.2f}",                    sNR),
            _p(f"<b>{l['montant']:,.2f}</b>",                   sNBR),
        ])

    n_data = len(lignes_src)

    # Ligne séparatrice vide
    rows.append(["", "", "", "", ""])

    # Totaux
    rows.append(["", "", "", _p("<b>TOTAL H.T</b>", sNBR), _p(f"<b>{ht:,.2f}</b>", sNBR)])
    rows.append(["", "", "", _p(f"T.V.A {tva_taux:.0f}%", sNR), _p(f"{tva:,.2f}", sNR)])

    if red and red > 0:
        lbl_red = f"Réduction {red_pct:.0f}%" if red_pct else "Réduction"
        rows.append(["", "", "",
                      _p(f"<font color='#E8671B'><b>{lbl_red}</b></font>", sNR),
                      _p(f"<font color='#E8671B'><b>- {red:,.2f}</b></font>", sNR)])

    rows.append(["", "", "",
                 _p("<b>TOTAL T.T.C</b>",
                    _s("TTCL", size=9.5, bold=True, align=TA_RIGHT, color=BLEU)),
                 _p(f"<b>{ttc:,.2f}</b>",
                    _s("TTCV", size=9.5, bold=True, align=TA_RIGHT, color=ORANGE))])

    n_rows = len(rows)

    ts = TableStyle([
        # Header
        ("BACKGROUND",   (0, 0), (-1, 0),        BLEU),
        ("TEXTCOLOR",    (0, 0), (-1, 0),        BLANC),
        ("LINEBELOW",    (0, 0), (-1, 0),        1.5, ORANGE),
        # Grille data
        ("GRID",         (0, 0), (-1, n_data),   0.4, GRIS2),
        # Alternance lignes data
        *[("BACKGROUND", (0, i), (-1, i), colors.HexColor("#EEF4FF"))
          for i in range(2, n_data + 1, 2)],
        # Séparation totaux
        ("LINEABOVE",    (3, n_data + 2), (-1, n_data + 2), 1,  BLEU),
        # Ligne TTC
        ("BACKGROUND",   (3, n_rows - 1), (-1, n_rows - 1), colors.HexColor("#E8F4FD")),
        ("LINEABOVE",    (3, n_rows - 1), (-1, n_rows - 1), 1.5, ORANGE),
        ("LINEBELOW",    (3, n_rows - 1), (-1, n_rows - 1), 1.5, ORANGE),
        # Padding
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        # Span colonnes vides dans totaux
        ("SPAN",         (0, n_data + 1), (2, n_rows - 1)),
    ])

    t_lignes = Table(rows, colWidths=cw, repeatRows=1)
    t_lignes.setStyle(ts)
    story.append(t_lignes)
    story.append(Spacer(1, 5))

    # ═══════════════════════════════════════════════════════════════════════════
    # 4. MONTANT EN LETTRES
    # ═══════════════════════════════════════════════════════════════════════════
    t_lettres = Table([[
        _p(f"Arrêtée le présent {doc_type.capitalize()} à la somme de :<br/>"
           f"<b>{_lettres(ttc)}</b> — Toutes Taxes Comprises",
           sLTTR)
    ]], colWidths=[AW])
    t_lettres.setStyle(TableStyle([
        ("BOX",          (0, 0), (-1, -1), 1,   ORANGE),
        ("BACKGROUND",   (0, 0), (-1, -1), colors.HexColor("#FFF8F3")),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
    ]))
    story.append(t_lettres)
    story.append(Spacer(1, 6))

    # ═══════════════════════════════════════════════════════════════════════════
    # 5. NOTES (si présentes)
    # ═══════════════════════════════════════════════════════════════════════════
    if notes and notes.strip():
        t_notes = Table([[
            _p(f"<b>Notes :</b> {notes}", _s("NT", size=8))
        ]], colWidths=[AW])
        t_notes.setStyle(TableStyle([
            ("BOX",         (0,0),(-1,-1), 0.5, GRIS2),
            ("BACKGROUND",  (0,0),(-1,-1), GRIS),
            ("TOPPADDING",  (0,0),(-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ("LEFTPADDING", (0,0),(-1,-1), 8),
        ]))
        story.append(t_notes)
        story.append(Spacer(1, 5))

    # ═══════════════════════════════════════════════════════════════════════════
    # 6. SIGNATURE (Wassime BTP uniquement)
    # ═══════════════════════════════════════════════════════════════════════════
    t_sig = Table([[
        _p("", sN),
        Table([[
            _p("<b>Cachet et Signature</b>", sSIG),
            _p("<b>Ste Wassime BTP</b>",
               _s("SB", size=8, bold=True, align=TA_CENTER, color=BLEU)),
        ]], colWidths=[6*cm])
    ]], colWidths=[AW - 6*cm, 6*cm])
    t_sig.setStyle(TableStyle([
        ("BOX",         (1, 0), (1, 0), 0.5, GRIS2),
        ("BACKGROUND",  (1, 0), (1, 0), GRIS),
        ("TOPPADDING",  (0, 0), (-1,-1), 30),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("ALIGN",       (1, 0), (1, 0), "CENTER"),
        ("VALIGN",      (0, 0), (-1,-1), "BOTTOM"),
    ]))
    story.append(t_sig)
    story.append(Spacer(1, 6))

    # ═══════════════════════════════════════════════════════════════════════════
    # 7. PIED DE PAGE (coordonnées SARL)
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=1.5, color=ORANGE,
                             spaceBefore=0, spaceAfter=3))
    t_footer = Table([[
        _p("TP : 60271115   |   CNSS : 5408680   |   ICE : 003440371000093   |   "
           "IF : 60271115   |   RC : 4113", sFT),
    ],[
        _p("RIB : 145 450 2121167962380017 92 BP   |   "
           "+212 688 540 102  /  +212 667 848 524   |   "
           "STEWASSIMEBTP@GMAIL.COM   |   DR NOUAJI SIDI BOUOTHMANE, Ben Guérir", sFT),
    ]], colWidths=[AW])
    t_footer.setStyle(TableStyle([
        ("TOPPADDING",   (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
    ]))
    story.append(t_footer)

    # ═══════════════════════════════════════════════════════════════════════════
    # Build — une seule Frame qui remplit toute la page
    # ═══════════════════════════════════════════════════════════════════════════
    doc = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=ML, rightMargin=MR,
        topMargin=MT, bottomMargin=MB,
        title=f"{doc_type} {numero} — Wassime BTP"
    )
    frame = Frame(ML, MB, W_PAGE - ML - MR, H_PAGE - MT - MB,
                  id="main", showBoundary=0)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame])])
    doc.build(story)
    return buf.getvalue()


# ── API publique ──────────────────────────────────────────────────────────────
def generer_devis_pdf(devis_data: dict) -> bytes:
    return _build_pdf(devis_data, "DEVIS")

def generer_facture_pdf(facture_data: dict) -> bytes:
    return _build_pdf(facture_data, "FACTURE")


# ─── BON DE LIVRAISON PDF ────────────────────────────────────────────────────────

def generer_bl_pdf(bl_data: dict) -> bytes:
    """bl_data: dict from controller.get_bon_livraison_by_id()"""
    devis = bl_data.get("devis") or {}
    # Adapter le format pour réutiliser _build_pdf
    fake_data = {
        "numero":       bl_data["numero"],
        "date_creation": bl_data.get("date_livraison") or date.today(),
        "client_nom":   devis.get("client_nom",""),
        "client_ice":   devis.get("client_ice",""),
        "client_tel":   devis.get("client_tel",""),
        "client_adresse": devis.get("client_adresse",""),
        "date_debut":   devis.get("date_debut"),
        "date_fin":     devis.get("date_fin"),
        "duree_jours":  devis.get("duree_jours",0),
        "lignes":       devis.get("lignes",[]),
        "montant_ht":   devis.get("montant_ht",0),
        "tva_taux":     devis.get("tva_taux",20),
        "montant_tva":  devis.get("montant_tva",0),
        "montant_ttc":  devis.get("montant_ttc",0),
        "statut":       bl_data.get("statut","emis"),
        "notes": f"Lieu de livraison : {bl_data.get('lieu_livraison','')}\n"
                 f"{bl_data.get('observations','') or ''}",
    }
    return _build_pdf(fake_data, "BON DE LIVRAISON")


# ─── ATTACHEMENT PDF ─────────────────────────────────────────────────────────────

def generer_attachement_pdf(att_data: dict) -> bytes:
    """att_data: dict from controller.get_attachement_by_id()"""
    buf = BytesIO()
    W_PAGE, H_PAGE = A4
    ML = MR = 1.4*cm
    MT = MB = 1.2*cm
    AW = W_PAGE - ML - MR

    BLEU_ATT = colors.HexColor("#1B2A4A")
    OR_ATT   = colors.HexColor("#C9A96E")
    VERT_ATT = colors.HexColor("#D4EDDA")
    GRIS_ATT = colors.HexColor("#F5F0EB")
    GRIS2_ATT= colors.HexColor("#CCCCCC")

    def sa(name, size=8.5, bold=False, align=TA_CENTER, color=NOIR):
        return ParagraphStyle(name, fontName="Helvetica-Bold" if bold else "Helvetica",
                              fontSize=size, leading=size+3, textColor=color, alignment=align)

    story = []

    # Header logo
    if os.path.exists(LOGO_PATH):
        lw = AW * 0.55; lh = lw * (141/723)
        story.append(RLImage(LOGO_PATH, width=lw, height=lh))
    story.append(HRFlowable(width="100%", thickness=2, color=OR_ATT, spaceAfter=5, spaceBefore=4))

    devis = att_data.get("devis") or {}
    mois_noms = ["","Janvier","Février","Mars","Avril","Mai","Juin",
                 "Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
    mois_str = mois_noms[att_data.get("mois",1)] if 1 <= att_data.get("mois",1) <= 12 else str(att_data.get("mois",""))

    # Titre
    t_titre = Table([[
        _p(f"<b>PROJET : {att_data.get('projet','—')}</b>",
           sa("TT", size=11, bold=True, color=BLEU_ATT)),
    ],[
        _p("Situation de location des matériels", sa("ST", size=9, color=NOIR)),
    ],[
        _p(f"Fournisseur : Wassime BTP", sa("FT", size=9, bold=True, color=BLEU_ATT)),
    ],[
        _p(f"Attachement en date du {att_data.get('annee','')} — {mois_str}",
           sa("DT", size=8.5)),
    ]], colWidths=[AW])
    t_titre.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
    ]))
    story.append(t_titre)
    story.append(Spacer(1,5))

    # Ligne engin
    engin_nom = att_data.get("engin_nom","—")
    matricule = att_data.get("matricule","—")
    t_engin = Table([[
        _p(f"<b>{engin_nom} / {matricule}</b>",
           sa("EN", size=10, bold=True, color=BLANC))
    ]], colWidths=[AW])
    t_engin.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), BLEU_ATT),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
    ]))
    story.append(t_engin)
    story.append(Spacer(1,4))

    # Tableau jours
    col_j = [AW*0.25, AW*0.40, AW*0.35]
    rows_j = [[
        _p(f"<b>MOIS {att_data.get('mois','')} — JOUR</b>",
           sa("TJH", bold=True, color=BLANC)),
        _p("<b>Pointage / Heures</b>", sa("TPH", bold=True, color=BLANC)),
        _p("<b>Pointage / Jour</b>",   sa("TPJ", bold=True, color=BLANC)),
    ]]

    jours = att_data.get("jours", [])
    total_j = 0; total_h = 0.0
    for jour, heures, jt in jours:
        is_off = (jt == 0)
        bg = GRIS_ATT if is_off else BLANC
        rows_j.append([
            _p(str(jour), sa(f"J{jour}", color=BLEU_ATT if is_off else NOIR)),
            _p(str(int(heures)) if heures else "0", sa(f"H{jour}")),
            _p(str(int(jt)),                        sa(f"JT{jour}")),
        ])
        total_j += int(jt); total_h += heures

    # Ligne total
    rows_j.append([
        _p("<b>Nombre Total des jours</b>",
           sa("TOT", bold=True, align=TA_LEFT, color=BLANC)),
        _p("", sa("TOT2")),
        _p(f"<b>{total_j}</b>", sa("TOTV", bold=True, color=BLANC)),
    ])

    n_j = len(rows_j)
    t_jours = Table(rows_j, colWidths=col_j, repeatRows=1)
    ts_j = TableStyle([
        ("BACKGROUND",   (0,0),(-1,0),  BLEU_ATT),
        ("BACKGROUND",   (0,n_j-1),(-1,n_j-1), BLEU_ATT),
        ("LINEBELOW",    (0,0),(-1,0),  1, OR_ATT),
        ("GRID",         (0,0),(-1,n_j-2), 0.4, GRIS2_ATT),
        ("TOPPADDING",   (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING",  (0,0),(-1,-1), 6),
    ])
    # Alternance et jours off
    for idx, (jour, _, jt) in enumerate(jours, start=1):
        if jt == 0:
            ts_j.add("BACKGROUND", (0,idx),(-1,idx), GRIS_ATT)
    t_jours.setStyle(ts_j)
    story.append(t_jours)
    story.append(Spacer(1,8))

    # Signatures 3 colonnes
    t_sig3 = Table([[
        _p("<b>Wassime BTP</b><br/>(Fournisseur)",
           sa("S1", bold=True, color=BLEU_ATT)),
        _p("<b>Comptable de Chantier</b>",
           sa("S2", bold=True, color=BLEU_ATT)),
        _p(f"<b>{devis.get('client_nom','Client')}</b>",
           sa("S3", bold=True, color=BLEU_ATT)),
    ]], colWidths=[AW/3]*3)
    t_sig3.setStyle(TableStyle([
        ("BOX",         (0,0),(0,-1), 0.5, GRIS2_ATT),
        ("BOX",         (1,0),(1,-1), 0.5, GRIS2_ATT),
        ("BOX",         (2,0),(2,-1), 0.5, GRIS2_ATT),
        ("BACKGROUND",  (0,0),(-1,-1), GRIS_ATT),
        ("TOPPADDING",  (0,0),(-1,-1), 35),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(t_sig3)
    story.append(Spacer(1,8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=OR_ATT, spaceAfter=3))

    sFT2 = sa("FT2", size=6.8, color=colors.HexColor("#555555"))
    story.append(Table([[
        _p("TP : 60271115 | CNSS : 5408680 | ICE : 003440371000093 | IF : 60271115 | RC : 4113", sFT2)
    ],[
        _p("RIB : 145 450 2121167962380017 92 BP | +212 688 540 102 | STEWASSIMEBTP@GMAIL.COM", sFT2)
    ]], colWidths=[AW]))

    doc = BaseDocTemplate(buf, pagesize=A4, leftMargin=ML, rightMargin=MR,
                          topMargin=MT, bottomMargin=MB)
    frame = Frame(ML, MB, W_PAGE-ML-MR, H_PAGE-MT-MB, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame])])
    doc.build(story)
    return buf.getvalue()


# ─── ATTESTATION DE RETARD PDF ───────────────────────────────────────────────────

def generer_attestation_retard_pdf(att_data: dict) -> bytes:
    """att_data: dict from controller.get_attestation_by_id()"""
    buf = BytesIO()
    W_PAGE, H_PAGE = A4
    ML = MR = 1.8*cm
    MT = MB = 1.5*cm
    AW = W_PAGE - ML - MR

    BRUN  = colors.HexColor("#5C3D2E")
    OR    = colors.HexColor("#C9A96E")
    GRIS  = colors.HexColor("#F5F0EB")
    ROUGE = colors.HexColor("#DC2626")

    def sa(name, size=9, bold=False, align=TA_LEFT, color=NOIR):
        return ParagraphStyle(name,
            fontName="Helvetica-Bold" if bold else "Helvetica",
            fontSize=size, leading=size+4, textColor=color, alignment=align)

    story = []

    # Logo
    if os.path.exists(LOGO_PATH):
        lw = AW * 0.55; lh = lw*(141/723)
        story.append(RLImage(LOGO_PATH, width=lw, height=lh))
    story.append(HRFlowable(width="100%", thickness=2, color=OR, spaceAfter=8, spaceBefore=4))

    # Titre
    t_titre = Table([[
        _p("<b>ATTESTATION DE RETARD DE PAIEMENT</b>",
           sa("T", size=14, bold=True, align=TA_CENTER, color=BRUN)),
    ],[
        _p(f"N° {att_data.get('numero','')}  —  Marrakech le : "
           f"{att_data['date_emission'].strftime('%d/%m/%Y') if att_data.get('date_emission') else ''}",
           sa("ST", size=9, align=TA_CENTER, color=colors.HexColor("#666666"))),
    ]], colWidths=[AW])
    t_titre.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4)
    ]))
    story.append(t_titre)
    story.append(Spacer(1, 10))

    # Bloc client / référence
    t_ref = Table([[
        _p(f"<b>Client :</b> {att_data.get('client_nom','')}",
           sa("R1", bold=False)),
        _p(f"<b>ICE :</b> {att_data.get('client_ice','—')}",
           sa("R2", bold=False, align=TA_RIGHT)),
    ],[
        _p(f"<b>Réf. Facture :</b> {att_data.get('facture_numero','')}",
           sa("R3")),
        _p(f"<b>Période :</b> {att_data.get('devis_periode','—')}",
           sa("R4", align=TA_RIGHT)),
    ]], colWidths=[AW*0.55, AW*0.45])
    t_ref.setStyle(TableStyle([
        ("BOX",         (0,0),(-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ("BACKGROUND",  (0,0),(-1,-1), GRIS),
        ("TOPPADDING",  (0,0),(-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
        ("LEFTPADDING", (0,0),(-1,-1), 10),
        ("RIGHTPADDING",(0,0),(-1,-1), 10),
    ]))
    story.append(t_ref)
    story.append(Spacer(1, 14))

    # Texte formel
    echeance_str = att_data["date_echeance_initiale"].strftime("%d/%m/%Y") \
        if att_data.get("date_echeance_initiale") else "—"
    texte = (
        f"La société <b>Ste Wassime BTP</b>, sise à Marrakech, Maroc, "
        f"atteste par la présente que <b>{att_data.get('client_nom','')}</b> "
        f"est en retard de paiement sur la facture <b>{att_data.get('facture_numero','')}</b> "
        f"dont l'échéance était fixée au <b>{echeance_str}</b>."
    )
    story.append(_p(texte, sa("TX", size=9.5, leading=16)))
    story.append(Spacer(1, 8))
    story.append(_p(
        f"À la date du {att_data['date_emission'].strftime('%d/%m/%Y') if att_data.get('date_emission') else '—'}, "
        f"le retard constaté est de <b>{att_data.get('nb_jours_retard',0)} jours</b>.",
        sa("TX2", size=9.5, leading=16)
    ))
    story.append(Spacer(1, 14))

    # Tableau calcul
    sH = sa("TH", bold=True, align=TA_CENTER, color=BLANC)
    sV = sa("TV", align=TA_RIGHT)
    sVB= sa("TVB", bold=True, align=TA_RIGHT, color=ROUGE)

    capital   = att_data.get("montant_capital", 0)
    taux      = att_data.get("taux_interet", 1.5)
    nb_j      = att_data.get("nb_jours_retard", 0)
    nb_mois   = round(nb_j / 30, 2)
    interets  = att_data.get("montant_interets", 0)
    total     = att_data.get("montant_total", 0)

    rows_calc = [[
        _p("<b>Désignation</b>", sH),
        _p("<b>Détail</b>",      sH),
        _p("<b>Montant (MAD)</b>",sH),
    ],[
        _p("Solde de la facture (capital dû)", sa("L1")),
        _p("Montant impayé à l'échéance",      sa("L1D")),
        _p(f"{capital:,.2f}", sV),
    ],[
        _p("Durée du retard",  sa("L2")),
        _p(f"{nb_j} jours ({nb_mois:.1f} mois)", sa("L2D")),
        _p("", sV),
    ],[
        _p(f"Taux d'intérêt de retard",  sa("L3")),
        _p(f"{taux:.2f}% / mois",         sa("L3D")),
        _p("", sV),
    ],[
        _p("Intérêts de retard calculés",  sa("L4")),
        _p(f"{capital:,.2f} × {taux}% × {nb_mois:.2f} mois", sa("L4D")),
        _p(f"{interets:,.2f}", sV),
    ],[
        _p("<b>TOTAL DÛ (Capital + Intérêts)</b>", sa("LT", bold=True)),
        _p("", sa("LTD")),
        _p(f"<b>{total:,.2f}</b>", sVB),
    ]]

    t_calc = Table(rows_calc, colWidths=[AW*0.38, AW*0.35, AW*0.27])
    t_calc.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,0), BRUN),
        ("LINEBELOW",    (0,0),(-1,0), 1.5, OR),
        ("GRID",         (0,0),(-1,-2), 0.4, colors.HexColor("#DDDDDD")),
        ("BACKGROUND",   (0,-1),(-1,-1), colors.HexColor("#FFF3F3")),
        ("LINEABOVE",    (0,-1),(-1,-1), 1.5, ROUGE),
        ("LINEBELOW",    (0,-1),(-1,-1), 1.5, ROUGE),
        ("TOPPADDING",   (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ("RIGHTPADDING", (0,0),(-1,-1), 8),
        *[("BACKGROUND",(0,i),(-1,i), GRIS) for i in range(2, len(rows_calc)-1, 2)],
    ]))
    story.append(t_calc)
    story.append(Spacer(1, 10))

    # Montant en lettres
    t_l = Table([[
        _p(f"Arrêtée la présente attestation à la somme totale de :<br/>"
           f"<b>{_lettres(total)}</b>",
           sa("LT2", size=8, align=TA_CENTER, bold=True, color=BRUN))
    ]], colWidths=[AW])
    t_l.setStyle(TableStyle([
        ("BOX",         (0,0),(-1,-1), 1, OR),
        ("BACKGROUND",  (0,0),(-1,-1), colors.HexColor("#FFF8F0")),
        ("TOPPADDING",  (0,0),(-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
    ]))
    story.append(t_l)
    story.append(Spacer(1, 10))

    # Notes
    if att_data.get("notes"):
        story.append(_p(f"<b>Notes :</b> {att_data['notes']}",
                        sa("N", size=8.5, color=colors.HexColor("#555555"))))
        story.append(Spacer(1, 8))

    # Signature
    t_sig = Table([[
        _p("", sa("SE")),
        Table([[
            _p("<b>Cachet et Signature</b><br/>Ste Wassime BTP",
               sa("SS", size=8, align=TA_CENTER, color=BRUN))
        ]], colWidths=[6*cm])
    ]], colWidths=[AW - 6*cm, 6*cm])
    t_sig.setStyle(TableStyle([
        ("BOX",         (1,0),(1,0), 0.5, colors.HexColor("#CCCCCC")),
        ("BACKGROUND",  (1,0),(1,0), GRIS),
        ("TOPPADDING",  (0,0),(-1,-1), 30),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(t_sig)
    story.append(Spacer(1, 8))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1.5, color=OR, spaceAfter=3))
    sF = sa("FT", size=6.8, align=TA_CENTER, color=colors.HexColor("#666666"))
    story.append(Table([[
        _p("TP : 60271115 | CNSS : 5408680 | ICE : 003440371000093 | IF : 60271115 | RC : 4113", sF)
    ],[
        _p("RIB : 145 450 2121167962380017 92 BP | +212 688 540 102 | STEWASSIMEBTP@GMAIL.COM", sF)
    ]], colWidths=[AW]))

    doc = BaseDocTemplate(buf, pagesize=A4,
                          leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB)
    frame = Frame(ML, MB, W_PAGE-ML-MR, H_PAGE-MT-MB, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame])])
    doc.build(story)
    return buf.getvalue()
