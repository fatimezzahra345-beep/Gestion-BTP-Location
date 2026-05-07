"""
views_theme.py — Design System Premium | LocationBTP
Inspiré des meilleures apps SaaS : Jibble, Linear, Notion, Stripe
Palette : Blanc pur · Gris neutres · Accent indigo/bleu · Rouge alerte
"""

LUXURY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ══════════════════════════════════════════════
   VARIABLES DESIGN SYSTEM
══════════════════════════════════════════════ */
:root {
  /* Couleurs principales */
  --primary:       #2563EB;
  --primary-light: #EFF6FF;
  --primary-dark:  #1D4ED8;

  /* Neutres */
  --white:    #FFFFFF;
  --gray-50:  #F8FAFC;
  --gray-100: #F1F5F9;
  --gray-200: #E2E8F0;
  --gray-300: #CBD5E1;
  --gray-400: #94A3B8;
  --gray-500: #64748B;
  --gray-600: #475569;
  --gray-700: #334155;
  --gray-800: #1E293B;
  --gray-900: #0F172A;

  /* Statuts */
  --green:      #10B981;
  --green-bg:   #ECFDF5;
  --green-text: #065F46;
  --red:        #EF4444;
  --red-bg:     #FEF2F2;
  --red-text:   #991B1B;
  --orange:     #F59E0B;
  --orange-bg:  #FFFBEB;
  --orange-text:#92400E;
  --blue:       #3B82F6;
  --blue-bg:    #EFF6FF;
  --blue-text:  #1D4ED8;
  --purple:     #8B5CF6;
  --purple-bg:  #F5F3FF;

  /* Ombres */
  --shadow-xs: 0 1px 2px rgba(0,0,0,.05);
  --shadow-sm: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md: 0 4px 6px rgba(0,0,0,.05), 0 2px 4px rgba(0,0,0,.04);
  --shadow-lg: 0 10px 15px rgba(0,0,0,.06), 0 4px 6px rgba(0,0,0,.04);
  --shadow-xl: 0 20px 25px rgba(0,0,0,.08), 0 10px 10px rgba(0,0,0,.04);

  /* Typographie */
  --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

  /* Rayons */
  --r-sm:  6px;
  --r-md:  10px;
  --r-lg:  14px;
  --r-xl:  20px;
  --r-2xl: 28px;
}

/* ══════════════════════════════════════════════
   RESET & BASE
══════════════════════════════════════════════ */
* { font-family: var(--font) !important; box-sizing: border-box; }

/* Fond général blanc */
.stApp, .main, [data-testid="stAppViewContainer"] {
  background: var(--gray-50) !important;
}
.main .block-container {
  padding: 28px 32px 48px !important;
  max-width: 1440px !important;
}

/* ══════════════════════════════════════════════
   SIDEBAR — Navigation SaaS moderne
══════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: var(--white) !important;
  border-right: 1px solid var(--gray-200) !important;
  box-shadow: var(--shadow-sm) !important;
  min-width: 240px !important;
  max-width: 240px !important;
}
[data-testid="stSidebar"] > div {
  padding: 0 !important;
  background: var(--white) !important;
}

/* Textes sidebar */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
  color: var(--gray-700) !important;
}

/* Boutons navigation radio — TOUS IDENTIQUES */
[data-testid="stSidebar"] .stRadio > div {
  display: flex !important;
  flex-direction: column !important;
  gap: 1px !important;
  padding: 8px 12px !important;
}
[data-testid="stSidebar"] .stRadio > div > label {
  display: flex !important;
  align-items: center !important;
  width: 100% !important;
  padding: 9px 12px !important;
  border-radius: var(--r-md) !important;
  border: none !important;
  cursor: pointer !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  color: var(--gray-600) !important;
  background: transparent !important;
  transition: all 0.15s ease !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  letter-spacing: 0 !important;
  line-height: 1.4 !important;
  min-height: 40px !important;
  margin: 0 !important;
}
[data-testid="stSidebar"] .stRadio > div > label:hover {
  background: var(--gray-100) !important;
  color: var(--gray-900) !important;
}
[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
[data-testid="stSidebar"] .stRadio > div > label[aria-checked="true"] {
  background: var(--primary-light) !important;
  color: var(--primary-dark) !important;
  font-weight: 600 !important;
}
[data-testid="stSidebar"] .stRadio input[type="radio"] { display: none !important; }

/* ══════════════════════════════════════════════
   MÉTRIQUES / KPI CARDS
══════════════════════════════════════════════ */
[data-testid="metric-container"] {
  background: var(--white) !important;
  border: 1px solid var(--gray-200) !important;
  border-radius: var(--r-lg) !important;
  padding: 20px !important;
  box-shadow: var(--shadow-sm) !important;
  transition: box-shadow .2s, transform .2s !important;
}
[data-testid="metric-container"]:hover {
  box-shadow: var(--shadow-md) !important;
  transform: translateY(-1px) !important;
}
[data-testid="metric-container"] label {
  font-size: 11.5px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.8px !important;
  color: var(--gray-500) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-size: 26px !important;
  font-weight: 800 !important;
  color: var(--gray-900) !important;
  letter-spacing: -0.5px !important;
}

/* ══════════════════════════════════════════════
   BOUTONS — Design System uniforme
══════════════════════════════════════════════ */
.stButton > button {
  font-family: var(--font) !important;
  font-size: 13.5px !important;
  font-weight: 600 !important;
  border-radius: var(--r-md) !important;
  padding: 9px 16px !important;
  border: 1px solid var(--gray-300) !important;
  background: var(--white) !important;
  color: var(--gray-700) !important;
  box-shadow: var(--shadow-xs) !important;
  cursor: pointer !important;
  transition: all .15s ease !important;
  line-height: 1.4 !important;
}
.stButton > button:hover {
  background: var(--gray-50) !important;
  border-color: var(--gray-400) !important;
  color: var(--gray-900) !important;
  box-shadow: var(--shadow-sm) !important;
}
.stButton > button[kind="primary"] {
  background: var(--primary) !important;
  color: var(--white) !important;
  border: none !important;
  box-shadow: 0 1px 3px rgba(37,99,235,.30) !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--primary-dark) !important;
  box-shadow: 0 4px 12px rgba(37,99,235,.35) !important;
  transform: translateY(-1px) !important;
}
.stDownloadButton > button {
  background: var(--green) !important;
  color: var(--white) !important;
  border: none !important;
  font-weight: 600 !important;
  border-radius: var(--r-md) !important;
  box-shadow: 0 1px 3px rgba(16,185,129,.25) !important;
}
.stDownloadButton > button:hover {
  background: #059669 !important;
  box-shadow: 0 4px 12px rgba(16,185,129,.30) !important;
}

/* ══════════════════════════════════════════════
   TABS
══════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 2px solid var(--gray-200) !important;
  border-radius: 0 !important;
  padding: 0 !important;
  gap: 0 !important;
  margin-bottom: 24px !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 0 !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  color: var(--gray-500) !important;
  padding: 10px 18px !important;
  border-bottom: 2px solid transparent !important;
  margin-bottom: -2px !important;
  transition: all .15s !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover {
  color: var(--gray-800) !important;
  background: var(--gray-50) !important;
}
.stTabs [aria-selected="true"] {
  color: var(--primary) !important;
  font-weight: 700 !important;
  border-bottom: 2px solid var(--primary) !important;
  background: transparent !important;
}

/* ══════════════════════════════════════════════
   INPUTS & FORMULAIRES
══════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input {
  font-family: var(--font) !important;
  font-size: 14px !important;
  border: 1.5px solid var(--gray-300) !important;
  border-radius: var(--r-md) !important;
  background: var(--white) !important;
  color: var(--gray-900) !important;
  padding: 9px 13px !important;
  transition: border-color .15s, box-shadow .15s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(37,99,235,.12) !important;
}
.stSelectbox > div > div,
.stSelectbox [data-baseweb="select"] > div {
  border: 1.5px solid var(--gray-300) !important;
  border-radius: var(--r-md) !important;
  background: var(--white) !important;
  font-size: 14px !important;
}
.stForm {
  background: var(--white) !important;
  border: 1px solid var(--gray-200) !important;
  border-radius: var(--r-xl) !important;
  padding: 28px !important;
  box-shadow: var(--shadow-sm) !important;
}
label[data-testid="stWidgetLabel"] p {
  font-size: 13px !important;
  font-weight: 600 !important;
  color: var(--gray-700) !important;
  margin-bottom: 4px !important;
}
.stCheckbox label p {
  font-size: 13.5px !important;
  color: var(--gray-700) !important;
}

/* ══════════════════════════════════════════════
   DATAFRAMES
══════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
  border: 1px solid var(--gray-200) !important;
  border-radius: var(--r-lg) !important;
  overflow: hidden !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ══════════════════════════════════════════════
   EXPANDER
══════════════════════════════════════════════ */
[data-testid="stExpander"] {
  border: 1px solid var(--gray-200) !important;
  border-radius: var(--r-lg) !important;
  background: var(--white) !important;
  box-shadow: var(--shadow-xs) !important;
}

/* ══════════════════════════════════════════════
   ALERTS
══════════════════════════════════════════════ */
[data-testid="stAlert"] {
  border-radius: var(--r-md) !important;
  border: none !important;
  font-size: 13.5px !important;
}

/* ══════════════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════════════ */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--gray-300); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--gray-400); }

/* ══════════════════════════════════════════════
   COMPOSANTS CUSTOM
══════════════════════════════════════════════ */

/* Page header */
.ph-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0 20px 0;
  border-bottom: 1px solid var(--gray-200);
  margin-bottom: 24px;
}
.ph-left { display: flex; align-items: center; gap: 14px; }
.ph-icon {
  width: 44px; height: 44px;
  background: var(--primary-light);
  border-radius: var(--r-lg);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px;
}
.ph-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--gray-900);
  letter-spacing: -0.3px;
  line-height: 1.2;
}
.ph-sub {
  font-size: 12.5px;
  color: var(--gray-500);
  font-weight: 400;
  margin-top: 2px;
}

/* Card blanche */
.card {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--r-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  transition: box-shadow .2s;
}
.card:hover { box-shadow: var(--shadow-md); }

/* KPI card custom */
.kpi {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--r-lg);
  padding: 18px 20px;
  box-shadow: var(--shadow-sm);
  transition: box-shadow .2s, transform .2s;
  position: relative;
  overflow: hidden;
}
.kpi:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.kpi-accent {
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  border-radius: var(--r-lg) var(--r-lg) 0 0;
}
.kpi-label {
  font-size: 11.5px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.8px; color: var(--gray-500); margin-bottom: 8px;
}
.kpi-value {
  font-size: 28px; font-weight: 800; color: var(--gray-900);
  letter-spacing: -0.8px; line-height: 1;
}
.kpi-sub { font-size: 12px; color: var(--gray-400); margin-top: 6px; font-weight: 400; }
.kpi-icon {
  position: absolute; top: 16px; right: 16px;
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}

/* Section title */
.sec-title {
  font-size: 11.5px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; color: var(--gray-500);
  padding-bottom: 10px; border-bottom: 1px solid var(--gray-200);
  margin-bottom: 16px;
}

/* Divider */
.lux-divider {
  height: 1px; background: var(--gray-200);
  margin: 20px 0; border: none;
}

/* Badge statut */
.badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: 20px;
  font-size: 11px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.b-green  { background: var(--green-bg);  color: var(--green-text); }
.b-red    { background: var(--red-bg);    color: var(--red-text); }
.b-orange { background: var(--orange-bg); color: var(--orange-text); }
.b-blue   { background: var(--blue-bg);   color: var(--blue-text); }
.b-gray   { background: var(--gray-100);  color: var(--gray-600); }
.b-purple { background: var(--purple-bg); color: var(--purple); }

/* Info / alert boxes */
.box-info {
  background: var(--blue-bg); border: 1px solid #BFDBFE;
  border-radius: var(--r-md); padding: 12px 16px;
  font-size: 13.5px; color: var(--blue-text); margin: 10px 0;
}
.box-warn {
  background: var(--orange-bg); border: 1px solid #FDE68A;
  border-radius: var(--r-md); padding: 12px 16px;
  font-size: 13.5px; color: var(--orange-text); margin: 10px 0;
}
.box-success {
  background: var(--green-bg); border: 1px solid #A7F3D0;
  border-radius: var(--r-md); padding: 12px 16px;
  font-size: 13.5px; color: var(--green-text); margin: 10px 0;
}
.box-danger {
  background: var(--red-bg); border: 1px solid #FCA5A5;
  border-radius: var(--r-md); padding: 12px 16px;
  font-size: 13.5px; color: var(--red-text); margin: 10px 0;
}

/* Table row hover */
.trow {
  display: grid; align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--gray-100);
  transition: background .12s;
  border-radius: var(--r-sm);
}
.trow:hover { background: var(--gray-50); }

/* Engin card — taille fixe uniforme */
.eng-card {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--r-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: box-shadow .2s, transform .2s;
  height: 320px;
  display: flex; flex-direction: column;
}
.eng-card:hover { box-shadow: var(--shadow-lg); transform: translateY(-3px); }
.eng-photo {
  width: 100%; height: 160px;
  object-fit: cover; display: block; flex-shrink: 0;
}
.eng-placeholder {
  width: 100%; height: 160px; flex-shrink: 0;
  background: var(--gray-100);
  display: flex; align-items: center; justify-content: center;
  font-size: 44px;
}
.eng-body {
  padding: 14px 16px; flex: 1;
  display: flex; flex-direction: column; gap: 6px;
}
.eng-name { font-size: 13.5px; font-weight: 700; color: var(--gray-900); }
.eng-mat  { font-size: 11.5px; color: var(--gray-400); font-weight: 500; }
.eng-price {
  margin-top: auto; font-size: 18px; font-weight: 800;
  color: var(--primary); letter-spacing: -0.3px;
}
.eng-price span { font-size: 12px; font-weight: 400; color: var(--gray-400); }

/* Stat mini card */
.stat-mini {
  background: var(--white); border: 1px solid var(--gray-200);
  border-radius: var(--r-md); padding: 14px 16px;
  box-shadow: var(--shadow-xs);
}
.stat-mini .lbl {
  font-size: 11px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.8px; color: var(--gray-400); margin-bottom: 4px;
}
.stat-mini .val {
  font-size: 22px; font-weight: 800; color: var(--gray-900);
}

/* Progress bar */
.prog-wrap {
  background: var(--gray-200); border-radius: 4px;
  height: 8px; overflow: hidden; margin: 8px 0;
}
.prog-fill { height: 100%; border-radius: 4px; transition: width .5s ease; }

/* Alert row */
.alert-row {
  background: var(--white); border: 1px solid var(--gray-200);
  border-left: 4px solid;
  border-radius: 0 var(--r-md) var(--r-md) 0;
  padding: 12px 16px; margin-bottom: 8px;
  box-shadow: var(--shadow-xs);
  display: flex; align-items: center; gap: 12px;
}

/* ══ FILE UPLOADER — Fix "uploadUpload" bug + clean design ══ */

/* Hide the duplicate label that causes "uploadUpload" */
[data-testid="stFileUploader"] > label {
    display: none !important;
}
[data-testid="stFileUploader"] > div > label {
    display: none !important;
}

/* Upload zone — clean dashed border */
[data-testid="stFileUploader"] section {
    border: 2px dashed #CBD5E1 !important;
    border-radius: 12px !important;
    background: #F8FAFC !important;
    padding: 24px 20px !important;
    transition: all .2s ease !important;
    text-align: center !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: #2563EB !important;
    background: #EFF6FF !important;
}

/* The "Browse files" button — single clean text */
[data-testid="stFileUploader"] section button {
    background: #2563EB !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 9px 20px !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    font-family: var(--font) !important;
    cursor: pointer !important;
    box-shadow: 0 1px 3px rgba(37,99,235,.25) !important;
    transition: all .15s ease !important;
}
[data-testid="stFileUploader"] section button:hover {
    background: #1D4ED8 !important;
    box-shadow: 0 4px 12px rgba(37,99,235,.30) !important;
}

/* Fix: hide duplicate text inside button */
[data-testid="stFileUploader"] section button span {
    display: none !important;
}
[data-testid="stFileUploader"] section button::after {
    content: "Choisir un fichier";
    display: inline !important;
    font-size: 13.5px;
    font-weight: 600;
}

/* Helper text below button */
[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section p {
    font-size: 12px !important;
    color: #94A3B8 !important;
    margin-top: 8px !important;
}


/* ══ SIDEBAR — Hide keyboard_double_arrow text ══ */
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}
/* Collapse button — only arrow, no text */
[data-testid="stSidebarCollapseButton"] button {
    width: 32px !important;
    height: 32px !important;
    border-radius: 8px !important;
    background: white !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.06) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stSidebarCollapseButton"] button span {
    font-size: 0 !important;
    width: 0 !important;
}
[data-testid="stSidebarCollapseButton"] button svg {
    width: 16px !important;
    height: 16px !important;
    color: #64748B !important;
}
/* Hide the expand icon text on collapsed state */
[data-testid="stSidebarCollapsedControl"] span {
    display: none !important;
}
button[data-testid="stBaseButton-headerNoPadding"] {
    display: none !important;
}
/* Hide any Material Icons text rendering */
.material-symbols-rounded {
    font-size: 18px !important;
    overflow: hidden !important;
}


/* ══ SIDEBAR COLLAPSE — Fleche propre ══ */
[data-testid="stSidebarCollapseButton"] {
    position: fixed !important;
    top: 14px !important;
    left: 248px !important;
    z-index: 999 !important;
}
[data-testid="stSidebarCollapseButton"] button {
    width: 28px !important;
    height: 28px !important;
    border-radius: 50% !important;
    background: white !important;
    border: 1.5px solid #E2E8F0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,.10) !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: all .15s !important;
}
[data-testid="stSidebarCollapseButton"] button:hover {
    background: #EFF6FF !important;
    border-color: #2563EB !important;
    box-shadow: 0 2px 12px rgba(37,99,235,.20) !important;
}
/* Hide text, keep only SVG icon */
[data-testid="stSidebarCollapseButton"] button span:not(:has(svg)) {
    display: none !important;
}
[data-testid="stSidebarCollapseButton"] button svg {
    width: 14px !important;
    height: 14px !important;
    color: #334155 !important;
}
/* Collapsed state — button on left */
[data-testid="stSidebarCollapsedControl"] {
    position: fixed !important;
    top: 14px !important;
    left: 8px !important;
    z-index: 999 !important;
}
[data-testid="stSidebarCollapsedControl"] button {
    width: 28px !important;
    height: 28px !important;
    border-radius: 50% !important;
    background: white !important;
    border: 1.5px solid #E2E8F0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,.10) !important;
}
/* Hide "keyboard_double_arrow" text completely */
[data-testid="stSidebarCollapsedControl"] button span:not(:has(svg)) {
    display: none !important;
}

</style>
"""