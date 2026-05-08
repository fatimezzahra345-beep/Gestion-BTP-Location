"""pages/calendrier.py — LocationBTP"""
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
    import controller as ctrl, matplotlib, matplotlib.pyplot as plt
    matplotlib.use("Agg")
    render_page_header("", "Calendrier des Locations","Visualisation Gantt des réservations actives")

    events=ctrl.get_locations_calendrier()
    if not events:
        _info("Aucune location active. Le calendrier s'affichera dès que des commandes seront créées.")

    df_ev=pd.DataFrame([{
        "N° Facture":e["devis"],"Client":e["client"],
        "Début":e["debut"].strftime("%d/%m/%Y"),"Fin":e["fin"].strftime("%d/%m/%Y"),
        "Durée (j)":(e["fin"]-e["debut"]).days+1,
        "Statut":e["statut"].upper(),
        "Montant (MAD)":f"{e['montant']:,.2f}",
    } for e in events])
    st.dataframe(df_ev,width='stretch',hide_index=True)