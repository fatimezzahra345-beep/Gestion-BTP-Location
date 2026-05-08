"""
controller.py — Couche Contrôleur (MVC)
Logique métier, calculs et opérations CRUD pour LocationBTP
"""

from datetime import date, timedelta
from database import SessionLocal
from models import Engin, Client, Devis, LigneDevis, Facture
import os


# ─── HELPERS ────────────────────────────────────────────────────────────────────

def _next_numero(prefix: str, model_class, field: str = "numero") -> str:
    """Génère un numéro séquentiel ex: DEV-2026-001"""
    session = SessionLocal()
    try:
        year = date.today().year
        count = session.query(model_class).filter(
            getattr(model_class, field).like(f"{prefix}-{year}-%")
        ).count()
        return f"{prefix}-{year}-{str(count + 1).zfill(3)}"
    finally:
        session.close()


# ─── ENGINS ─────────────────────────────────────────────────────────────────────

def get_all_engins():
    session = SessionLocal()
    try:
        return session.query(Engin).order_by(Engin.nom).all()
    finally:
        session.close()


def get_engins_disponibles():
    session = SessionLocal()
    try:
        return session.query(Engin).filter(Engin.statut == "disponible").order_by(Engin.nom).all()
    finally:
        session.close()


def get_engin_by_id(engin_id: int):
    session = SessionLocal()
    try:
        return session.query(Engin).filter(Engin.id == engin_id).first()
    finally:
        session.close()


def create_engin(nom, matricule, type_engin, prix_journalier, description="", photo_path=None, date_acquisition=None, statut="disponible", quantite_totale=1):
    session = SessionLocal()
    try:
        engin = Engin(
            nom=nom, matricule=matricule, type_engin=type_engin,
            prix_journalier=prix_journalier, description=description,
            photo_path=photo_path, date_acquisition=date_acquisition,
            statut=statut, quantite_totale=quantite_totale,
            quantite_louee=0, quantite_maintenance=0,
        )
        session.add(engin)
        session.commit()
        return engin.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def update_engin(engin_id, **kwargs):
    session = SessionLocal()
    try:
        engin = session.query(Engin).filter(Engin.id == engin_id).first()
        if engin:
            for key, value in kwargs.items():
                if hasattr(engin, key):
                    setattr(engin, key, value)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_engin(engin_id):
    session = SessionLocal()
    try:
        engin = session.query(Engin).filter(Engin.id == engin_id).first()
        if engin:
            session.delete(engin)
            session.commit()
            return True
        return False
    finally:
        session.close()


def get_engins_stats():
    session = SessionLocal()
    try:
        from sqlalchemy import func
        engins = session.query(Engin).all()
        total       = sum(e.quantite_totale or 1 for e in engins)
        loues       = sum(e.quantite_louee or 0 for e in engins)
        maintenance = sum(e.quantite_maintenance or 0 for e in engins)
        disponibles = max(0, total - loues - maintenance)
        return {
            "total":        total,
            "disponibles":  disponibles,
            "loues":        loues,
            "maintenance":  maintenance,
        }
    finally:
        session.close()


# ─── CLIENTS ────────────────────────────────────────────────────────────────────

def get_all_clients():
    session = SessionLocal()
    try:
        return session.query(Client).order_by(Client.nom).all()
    finally:
        session.close()


def get_client_by_id(client_id: int):
    session = SessionLocal()
    try:
        return session.query(Client).filter(Client.id == client_id).first()
    finally:
        session.close()


def create_client(nom, prenom="", societe="", ice="", telephone="", email="", adresse=""):
    session = SessionLocal()
    try:
        client = Client(
            nom=nom, prenom=prenom, societe=societe, ice=ice,
            telephone=telephone, email=email, adresse=adresse
        )
        session.add(client)
        session.commit()
        return client.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def update_client(client_id, **kwargs):
    session = SessionLocal()
    try:
        client = session.query(Client).filter(Client.id == client_id).first()
        if client:
            for key, value in kwargs.items():
                if hasattr(client, key):
                    setattr(client, key, value)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_client(client_id):
    session = SessionLocal()
    try:
        client = session.query(Client).filter(Client.id == client_id).first()
        if client:
            session.delete(client)
            session.commit()
            return True
        return False
    finally:
        session.close()


# ─── DEVIS ──────────────────────────────────────────────────────────────────────

def calculer_montants(lignes: list, tva_taux: float = 20.0):
    """
    lignes = [{"engin_id": x, "quantite": y, "prix_unitaire": z, "montant": total}, ...]
    Uses "montant" field if present (includes duree), otherwise qty * prix
    Retourne (montant_ht, montant_tva, montant_ttc)
    """
    montant_ht = sum(
        l.get("montant", l["quantite"] * l["prix_unitaire"])
        for l in lignes
    )
    montant_tva = round(montant_ht * tva_taux / 100, 2)
    montant_ttc = round(montant_ht + montant_tva, 2)
    return montant_ht, montant_tva, montant_ttc


def create_devis(client_id, date_debut, date_fin, lignes: list, tva_taux=20.0, notes="", echeance_jours=30):
    """
    lignes = [{"engin_id": int, "quantite": float, "prix_unitaire": float, "description": str}]
    """
    session = SessionLocal()
    try:
        numero = _next_numero("DEV", Devis)
        montant_ht, montant_tva, montant_ttc = calculer_montants(lignes, tva_taux)
        echeance = date_fin + timedelta(days=echeance_jours) if date_fin else None

        devis = Devis(
            numero=numero, client_id=client_id,
            date_debut=date_debut, date_fin=date_fin,
            montant_ht=montant_ht, tva_taux=tva_taux,
            montant_tva=montant_tva, montant_ttc=montant_ttc,
            notes=notes, echeance_paiement=echeance,
            statut="brouillon"
        )
        session.add(devis)
        session.flush()

        for l in lignes:
            engin = session.query(Engin).filter(Engin.id == l["engin_id"]).first()
            ligne = LigneDevis(
                devis_id=devis.id,
                engin_id=l["engin_id"],
                quantite=l["quantite"],
                prix_unitaire=l["prix_unitaire"],
                montant=l["quantite"] * l["prix_unitaire"],
                description=l.get("description", engin.nom if engin else "")
            )
            session.add(ligne)

        session.commit()
        return devis.id, numero
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_devis():
    session = SessionLocal()
    try:
        devis_list = session.query(Devis).order_by(Devis.created_at.desc()).all()
        result = []
        for d in devis_list:
            client_nom = d.client.nom_complet if d.client else "N/A"
            result.append({
                "id": d.id, "numero": d.numero, "client": client_nom,
                "date_debut": d.date_debut, "date_fin": d.date_fin,
                "montant_ttc": d.montant_ttc, "statut": d.statut,
                "date_creation": d.date_creation
            })
        return result
    finally:
        session.close()


def get_devis_by_id(devis_id: int):
    session = SessionLocal()
    try:
        d = session.query(Devis).filter(Devis.id == devis_id).first()
        if not d:
            return None
        lignes_data = []
        for l in d.lignes:
            engin_nom = l.engin.nom if l.engin else "N/A"
            lignes_data.append({
                "engin_nom": engin_nom,
                "quantite": l.quantite,
                "prix_unitaire": l.prix_unitaire,
                "montant": l.montant,
                "description": l.description
            })
        return {
            "id": d.id, "numero": d.numero,
            "client_id": d.client_id,
            "client_nom": d.client.nom_complet if d.client else "N/A",
            "client_email": d.client.email if d.client else "",
            "client_ice": d.client.ice if d.client else "",
            "client_tel": d.client.telephone if d.client else "",
            "client_adresse": d.client.adresse if d.client else "",
            "date_creation": d.date_creation,
            "date_debut": d.date_debut, "date_fin": d.date_fin,
            "duree_jours": d.duree_jours,
            "montant_ht": d.montant_ht, "tva_taux": d.tva_taux,
            "montant_tva": d.montant_tva, "montant_ttc": d.montant_ttc,
            "statut": d.statut, "notes": d.notes,
            "echeance_paiement": d.echeance_paiement,
            "lignes": lignes_data
        }
    finally:
        session.close()


def valider_devis(devis_id: int):
    session = SessionLocal()
    try:
        d = session.query(Devis).filter(Devis.id == devis_id).first()
        if d:
            d.statut = "valide"
            # Mettre les engins à "loue"
            for ligne in d.lignes:
                if ligne.engin:
                    ligne.engin.statut = "loue"
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def annuler_devis(devis_id: int):
    session = SessionLocal()
    try:
        d = session.query(Devis).filter(Devis.id == devis_id).first()
        if d:
            d.statut = "annule"
            for ligne in d.lignes:
                if ligne.engin:
                    ligne.engin.statut = "disponible"
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ─── FACTURATION ────────────────────────────────────────────────────────────────

def create_facture(devis_id: int, echeance_jours: int = 30):
    session = SessionLocal()
    try:
        d = session.query(Devis).filter(Devis.id == devis_id).first()
        if not d:
            raise ValueError("Devis introuvable")
        numero = _next_numero("FAC", Facture)
        echeance = date.today() + timedelta(days=echeance_jours)
        facture = Facture(
            numero=numero, devis_id=devis_id,
            montant_ttc=d.montant_ttc, echeance=echeance,
            statut="en_attente"
        )
        d.statut = "facture"
        session.add(facture)
        session.commit()
        return facture.id, numero
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def enregistrer_paiement(facture_id: int, montant: float):
    session = SessionLocal()
    try:
        f = session.query(Facture).filter(Facture.id == facture_id).first()
        if not f:
            raise ValueError("Facture introuvable")
        f.montant_paye += montant
        if f.montant_paye >= f.montant_ttc:
            f.statut = "paye"
            # Libérer les engins
            if f.devis:
                for ligne in f.devis.lignes:
                    if ligne.engin:
                        ligne.engin.statut = "disponible"
        elif f.montant_paye > 0:
            f.statut = "partiel"
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_factures():
    session = SessionLocal()
    try:
        factures = session.query(Facture).order_by(Facture.created_at.desc()).all()
        today = date.today()
        updated = False
        result = []
        for f in factures:
            client_nom = f.devis.client.nom_complet if f.devis and f.devis.client else "N/A"
            # Mettre à jour statut retard ET sauvegarder en base
            if f.statut == "en_attente" and f.echeance and f.echeance < today:
                f.statut = "retard"
                updated = True
        if updated:
            session.commit()
        for f in factures:
            client_nom = f.devis.client.nom_complet if f.devis and f.devis.client else "N/A"
            result.append({
                "id": f.id, "numero": f.numero, "client": client_nom,
                "devis_numero": f.devis.numero if f.devis else "N/A",
                "date_emission": f.date_emission, "echeance": f.echeance,
                "montant_ttc": f.montant_ttc, "montant_paye": f.montant_paye,
                "solde_restant": f.solde_restant, "statut": f.statut
            })
        return result
    finally:
        session.close()


def get_facture_by_id(facture_id: int):
    session = SessionLocal()
    try:
        f = session.query(Facture).filter(Facture.id == facture_id).first()
        if not f:
            return None
        return {
            "id": f.id, "numero": f.numero,
            "devis": get_devis_by_id(f.devis_id) if f.devis_id else None,
            "date_emission": f.date_emission, "echeance": f.echeance,
            "montant_ttc": f.montant_ttc, "montant_paye": f.montant_paye,
            "solde_restant": f.solde_restant, "statut": f.statut,
            "notes": f.notes
        }
    finally:
        session.close()


# ─── DASHBOARD / STATISTIQUES ───────────────────────────────────────────────────

def get_dashboard_stats():
    session = SessionLocal()
    try:
        from sqlalchemy import func

        today = date.today()

        # Mettre à jour les statuts retard avant calcul
        retard_updated = False
        factures_all = session.query(Facture).all()
        for f in factures_all:
            if f.statut == "en_attente" and f.echeance and f.echeance < today:
                f.statut = "retard"
                retard_updated = True
        if retard_updated:
            session.commit()

        # CA total (factures payées ou partielles) — inchangé
        ca_total = session.query(func.sum(Facture.montant_paye)).scalar() or 0.0

        # CA du mois courant
        ca_mois = session.query(func.sum(Facture.montant_paye)).filter(
            func.strftime('%Y-%m', Facture.date_emission) == today.strftime('%Y-%m')
        ).scalar() or 0.0

        # Devis en cours
        devis_en_cours = session.query(Devis).filter(Devis.statut == "valide").count()

        # Factures en retard — après mise à jour statut
        factures_retard = session.query(Facture).filter(
            Facture.statut == "retard"
        ).count()

        # Engins stats — somme des quantités réelles
        engins_stats = get_engins_stats()

        # CA par mois (6 derniers mois)
        ca_mensuel = []
        for i in range(5, -1, -1):
            mois_date = date(today.year, today.month, 1) - timedelta(days=30 * i)
            mois_str  = mois_date.strftime('%Y-%m')
            ca = session.query(func.sum(Facture.montant_paye)).filter(
                func.strftime('%Y-%m', Facture.date_emission) == mois_str
            ).scalar() or 0.0
            ca_mensuel.append({"mois": mois_date.strftime('%b %Y'), "ca": ca})

        # Créances
        creances = session.query(
            func.sum(Facture.montant_ttc - Facture.montant_paye)
        ).filter(
            Facture.statut.in_(["en_attente", "partiel", "retard"])
        ).scalar() or 0.0

        return {
            "ca_total":        ca_total,
            "ca_mois":         ca_mois,
            "devis_en_cours":  devis_en_cours,
            "factures_retard": factures_retard,
            "engins":          engins_stats,
            "ca_mensuel":      ca_mensuel,
            "creances":        creances,
        }
    finally:
        session.close()


def get_locations_calendrier():
    """Retourne les locations pour l'affichage calendrier — uniquement les factures payées."""
    session = SessionLocal()
    try:
        factures = session.query(Facture).filter(Facture.statut == "paye").all()
        events = []
        for f in factures:
            if not f.devis:
                continue
            d = f.devis
            client_nom = d.client.nom_complet if d.client else "N/A"
            engins_noms = ", ".join(
                l.engin.nom for l in d.lignes if l.engin
            ) or "N/A"
            events.append({
                "devis": f.numero,
                "client": client_nom,
                "engin": engins_noms,
                "debut": d.date_debut,
                "fin": d.date_fin,
                "statut": f.statut,
                "montant": f.montant_ttc
            })
        return events
    finally:
        session.close()


# ─── MODIFICATION DEVIS (avant validation) ──────────────────────────────────────

def update_devis_complet(devis_id: int, client_id: int, date_debut, date_fin,
                         lignes: list, tva_taux: float = 20.0, notes: str = ""):
    """
    Met à jour un devis brouillon : remplace toutes les lignes et recalcule les montants.
    lignes = [{"engin_id": int, "quantite": float, "prix_unitaire": float, "description": str}]
    """
    session = SessionLocal()
    try:
        d = session.query(Devis).filter(Devis.id == devis_id).first()
        if not d:
            raise ValueError("Devis introuvable")
        if d.statut != "brouillon":
            raise ValueError("Seuls les devis en brouillon peuvent être modifiés")

        # Supprimer les anciennes lignes
        for ligne in d.lignes:
            session.delete(ligne)
        session.flush()

        # Recalculer
        from datetime import timedelta
        montant_ht = sum(l["quantite"] * l["prix_unitaire"] for l in lignes)
        montant_tva = round(montant_ht * tva_taux / 100, 2)
        montant_ttc = round(montant_ht + montant_tva, 2)

        d.client_id    = client_id
        d.date_debut   = date_debut
        d.date_fin     = date_fin
        d.montant_ht   = montant_ht
        d.tva_taux     = tva_taux
        d.montant_tva  = montant_tva
        d.montant_ttc  = montant_ttc
        d.notes        = notes
        d.echeance_paiement = date_fin + timedelta(days=30) if date_fin else None

        # Ajouter les nouvelles lignes
        for l in lignes:
            engin = session.query(Engin).filter(Engin.id == l["engin_id"]).first()
            session.add(LigneDevis(
                devis_id=devis_id,
                engin_id=l["engin_id"],
                quantite=l["quantite"],
                prix_unitaire=l["prix_unitaire"],
                montant=l["quantite"] * l["prix_unitaire"],
                description=l.get("description", engin.nom if engin else "")
            ))

        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ─── MODIFICATION FACTURE (réduction + recalcul) ────────────────────────────────

def update_facture_reduction(facture_id: int, reduction_pct: float = 0.0,
                              reduction_mad: float = 0.0, notes: str = ""):
    """
    Applique une réduction à une facture et recalcule le TTC.
    On peut passer soit un pourcentage, soit un montant fixe.
    Si les deux sont fournis, le pourcentage prime.
    """
    session = SessionLocal()
    try:
        f = session.query(Facture).filter(Facture.id == facture_id).first()
        if not f:
            raise ValueError("Facture introuvable")

        devis = f.devis
        if not devis:
            raise ValueError("Devis associé introuvable")

        ht       = devis.montant_ht
        tva_taux = devis.tva_taux
        tva      = devis.montant_tva
        base_ttc = devis.montant_ttc  # TTC avant réduction

        if reduction_pct > 0:
            red = round(base_ttc * reduction_pct / 100, 2)
        else:
            red = round(reduction_mad, 2)

        new_ttc = round(base_ttc - red, 2)
        if new_ttc < 0:
            new_ttc = 0.0

        f.reduction     = red
        f.reduction_pct = reduction_pct if reduction_pct > 0 else 0.0
        f.montant_ht    = ht
        f.tva_taux      = tva_taux
        f.montant_tva   = tva
        f.montant_ttc   = new_ttc
        if notes:
            f.notes = notes

        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_facture_details_complets(facture_id: int):
    """Retourne les détails complets d'une facture avec le devis et les lignes."""
    session = SessionLocal()
    try:
        f = session.query(Facture).filter(Facture.id == facture_id).first()
        if not f:
            return None
        # Load client email INSIDE session (before close)
        client_email_fac = ""
        client_nom_fac   = ""
        try:
            if f.devis_id:
                from models import Devis as DevisM
                dv = session.query(DevisM).filter(DevisM.id==f.devis_id).first()
                if dv and dv.client:
                    client_email_fac = dv.client.email or ""
                    client_nom_fac   = dv.client.nom_complet or ""
        except Exception:
            pass
        devis_data = get_devis_by_id(f.devis_id) if f.devis_id else None
        # Get attachement + lignes par engin
        att_num_fac = ""
        lignes_att_fac = []
        try:
            from models import Attachement as AttModel, Engin as EnginM3
            from sqlalchemy import text as _text
            _att_id = getattr(f, 'attachement_id', None)
            if _att_id:
                att_f = session.query(AttModel).filter(AttModel.id==_att_id).first()
                if att_f:
                    att_num_fac = att_f.numero or ""
                    # Lignes par engin
                    rows_f = session.execute(
                        _text("SELECT engin_id, SUM(heures) "
                              "FROM jours_attachement WHERE attachement_id=:aid "
                              "GROUP BY engin_id"),
                        {"aid": _att_id}
                    ).fetchall()
                    from collections import defaultdict
                    for eid_f, nb_j_f in rows_f:
                        if not nb_j_f or nb_j_f <= 0: continue
                        eng_f = session.query(EnginM3).filter(EnginM3.id==eid_f).first() if eid_f else None
                        nom_f = eng_f.nom.upper() if eng_f else (att_f.matricule_engin or "ENGIN")
                        prix_f= eng_f.prix_journalier if eng_f else 0
                        lignes_att_fac.append({
                            "designation": f"LOCATION {nom_f}",
                            "qte":    float(nb_j_f),
                            "prix":   prix_f,
                            "montant":round(prix_f * float(nb_j_f), 2),
                        })
        except Exception:
            pass

        return {
            "id": f.id, "numero": f.numero,
            "client_nom":   client_nom_fac,
            "client_email": client_email_fac,
            "attachement_numero": att_num_fac,
            "lignes_attachement": lignes_att_fac,
            "devis": devis_data,
            "date_emission": f.date_emission,
            "echeance": f.echeance,
            "montant_ht":   getattr(f, "montant_ht", 0) or (devis_data or {}).get("montant_ht", 0),
            "tva_taux":     getattr(f, "tva_taux", 20)  or (devis_data or {}).get("tva_taux", 20),
            "montant_tva":  getattr(f, "montant_tva", 0) or (devis_data or {}).get("montant_tva", 0),
            "reduction":     getattr(f, "reduction", 0) or 0,
            "reduction_pct": getattr(f, "reduction_pct", 0) or 0,
            "montant_ttc":  f.montant_ttc,
            "montant_paye": f.montant_paye,
            "solde_restant": f.solde_restant,
            "statut": f.statut,
            "notes": f.notes,
        }
    finally:
        session.close()


# ─── MODIFIER LES LIGNES D'UNE FACTURE ─────────────────────────────────────────

def update_facture_lignes(facture_id: int, lignes: list,
                           tva_taux: float = None,
                           reduction_pct: float = 0.0,
                           reduction_mad: float = 0.0):
    """
    Modifie les engins/lignes d'une facture avant paiement.
    lignes = [{"engin_id":int, "quantite":float, "prix_unitaire":float, "description":str}]
    Recalcule HT, TVA, réduction et TTC.
    """
    session = SessionLocal()
    try:
        f = session.query(Facture).filter(Facture.id == facture_id).first()
        if not f:
            raise ValueError("Facture introuvable")
        if f.statut == "paye":
            raise ValueError("Impossible de modifier une facture déjà payée")

        d = f.devis
        if not d:
            raise ValueError("Devis associé introuvable")

        # Recalculer sur les nouvelles lignes
        tva = tva_taux if tva_taux is not None else d.tva_taux
        montant_ht  = sum(l["quantite"] * l["prix_unitaire"] for l in lignes)
        montant_tva = round(montant_ht * tva / 100, 2)
        base_ttc    = round(montant_ht + montant_tva, 2)

        if reduction_pct > 0:
            red = round(base_ttc * reduction_pct / 100, 2)
        else:
            red = round(reduction_mad, 2)
        new_ttc = max(0.0, round(base_ttc - red, 2))

        # Mettre à jour le devis associé avec les nouvelles lignes
        for ligne in d.lignes:
            session.delete(ligne)
        session.flush()

        for l in lignes:
            engin = session.query(Engin).filter(Engin.id == l["engin_id"]).first()
            session.add(LigneDevis(
                devis_id=d.id,
                engin_id=l["engin_id"],
                quantite=l["quantite"],
                prix_unitaire=l["prix_unitaire"],
                montant=l["quantite"] * l["prix_unitaire"],
                description=l.get("description", engin.nom if engin else "")
            ))

        # Mettre à jour les montants du devis
        d.montant_ht  = montant_ht
        d.tva_taux    = tva
        d.montant_tva = montant_tva
        d.montant_ttc = base_ttc

        # Mettre à jour la facture
        f.montant_ht    = montant_ht
        f.tva_taux      = tva
        f.montant_tva   = montant_tva
        f.reduction     = red
        f.reduction_pct = reduction_pct if reduction_pct > 0 else 0.0
        f.montant_ttc   = new_ttc

        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ─── COMMANDES ───────────────────────────────────────────────────────────────────

def _next_num(prefix, model_class, field="numero"):
    from database import SessionLocal
    from datetime import date as d
    session = SessionLocal()
    try:
        year = d.today().year
        count = session.query(model_class).filter(
            getattr(model_class, field).like(f"{prefix}-{year}-%")
        ).count()
        return f"{prefix}-{year}-{str(count+1).zfill(3)}"
    finally:
        session.close()

def get_all_commandes():
    from database import SessionLocal
    from models import Commande
    session = SessionLocal()
    try:
        cmds = session.query(Commande).order_by(Commande.created_at.desc()).all()
        result = []
        for c in cmds:
            engins_list = [{"nom": l.engin.nom, "quantite": l.quantite}
                           for l in c.lignes if l.engin]
            devis_num = c.devis.numero if c.devis else "—"
            result.append({
                "id": c.id, "numero": c.numero,
                "client": c.client.nom_complet if c.client else "N/A",
                "client_email": c.client.email if c.client else "",
                "client_id": c.client_id,
                "date_commande": c.date_commande,
                "date_debut": c.date_debut, "date_fin": c.date_fin,
                "duree_jours": c.duree_jours,
                "statut": c.statut, "notes": c.notes,
                "engins": engins_list,
                "devis_id": c.devis.id if c.devis else None,
                "devis_numero": devis_num,
            })
        return result
    finally:
        session.close()

def create_commande(client_id, date_debut, date_fin, lignes_engins, notes=""):
    """lignes_engins = [{"engin_id": x, "quantite": y}]"""
    from database import SessionLocal
    from models import Commande, LigneCommande, Engin
    session = SessionLocal()
    try:
        numero = _next_num("CMD", Commande)
        cmd = Commande(numero=numero, client_id=client_id,
                       date_debut=date_debut, date_fin=date_fin,
                       statut="en_attente", notes=notes)
        session.add(cmd)
        session.flush()
        for l in lignes_engins:
            engin = session.query(Engin).filter(Engin.id == l["engin_id"]).first()
            if engin:
                session.add(LigneCommande(commande_id=cmd.id,
                                          engin_id=l["engin_id"], quantite=l["quantite"]))
                engin.statut = "commande"
        session.commit()
        return cmd.id, numero
    except Exception as e:
        session.rollback(); raise e
    finally:
        session.close()

def confirmer_commande(commande_id):
    from database import SessionLocal
    from models import Commande
    session = SessionLocal()
    try:
        c = session.query(Commande).filter(Commande.id == commande_id).first()
        if c: c.statut = "confirmee"; session.commit()
    finally:
        session.close()

def annuler_commande(commande_id):
    from database import SessionLocal
    from models import Commande, Engin
    session = SessionLocal()
    try:
        c = session.query(Commande).filter(Commande.id == commande_id).first()
        if c:
            c.statut = "annulee"
            for l in c.lignes:
                if l.engin and l.engin.statut == "commande":
                    l.engin.statut = "disponible"
            session.commit()
    finally:
        session.close()

def creer_devis_depuis_commande(commande_id, tva_taux=20.0):
    from database import SessionLocal
    from models import Commande, Devis, LigneDevis
    from datetime import timedelta
    session = SessionLocal()
    try:
        c = session.query(Commande).filter(Commande.id == commande_id).first()
        if not c: raise ValueError("Commande introuvable")
        numero = _next_num("DEV", Devis)
        lignes_data = [{"engin_id": l.engin_id, "quantite": float(l.quantite),
                         "prix_unitaire": l.engin.prix_journalier,
                         "description": l.engin.nom} for l in c.lignes if l.engin]
        ht  = sum(l["quantite"] * l["prix_unitaire"] for l in lignes_data)
        tva = round(ht * tva_taux / 100, 2)
        ttc = round(ht + tva, 2)
        d = Devis(numero=numero, client_id=c.client_id, commande_id=c.id,
                  date_debut=c.date_debut, date_fin=c.date_fin,
                  montant_ht=ht, tva_taux=tva_taux, montant_tva=tva, montant_ttc=ttc,
                  echeance_paiement=c.date_fin + timedelta(days=30))
        session.add(d); session.flush()
        for l in lignes_data:
            session.add(LigneDevis(devis_id=d.id, engin_id=l["engin_id"],
                                   quantite=l["quantite"], prix_unitaire=l["prix_unitaire"],
                                   montant=l["quantite"]*l["prix_unitaire"],
                                   description=l["description"]))
        c.statut = "livree"
        session.commit()
        return d.id, numero
    except Exception as e:
        session.rollback(); raise e
    finally:
        session.close()


# ─── BONS DE LIVRAISON ──────────────────────────────────────────────────────────

def get_all_bons_livraison():
    from database import SessionLocal
    from models import BonLivraison
    session = SessionLocal()
    try:
        bls = session.query(BonLivraison).order_by(BonLivraison.created_at.desc()).all()
        updated = False
        for b in bls:
            cmd = b.devis.commande if b.devis and b.devis.commande else None
            if cmd and cmd.statut == "livree":
                if b.statut != "livre":
                    b.statut = "livre"
                    updated = True
            else:
                if b.statut not in ("livre", "en_attente"):
                    b.statut = "en_attente"
                    updated = True
        if updated:
            session.commit()
        return [{
            "id": b.id, "numero": b.numero,
            "devis_numero": b.devis.numero if b.devis else "N/A",
            "commande_numero": b.devis.commande.numero if b.devis and b.devis.commande else "—",
            "client": b.devis.client.nom_complet if b.devis and b.devis.client else "N/A",
            "client_email": b.devis.client.email if b.devis and b.devis.client else "",
            "date_livraison": b.date_livraison,
            "lieu_livraison": b.lieu_livraison,
            "statut": b.statut, "observations": b.observations,
            "devis_id": b.devis_id,
        } for b in bls]
    finally:
        session.close()

def create_bon_livraison(devis_id, lieu_livraison="", observations=""):
    from database import SessionLocal
    from models import BonLivraison
    session = SessionLocal()
    try:
        numero = _next_num("BL", BonLivraison)
        bl = BonLivraison(numero=numero, devis_id=devis_id,
                          lieu_livraison=lieu_livraison, observations=observations)
        session.add(bl); session.commit()
        return bl.id, numero
    except Exception as e:
        session.rollback(); raise e
    finally:
        session.close()

def get_bon_livraison_by_id(bl_id):
    from database import SessionLocal
    from models import BonLivraison
    session = SessionLocal()
    try:
        b = session.query(BonLivraison).filter(BonLivraison.id == bl_id).first()
        if not b: return None
        devis_data = get_devis_by_id(b.devis_id)
        return {
            "id": b.id, "numero": b.numero,
            "devis": devis_data,
            "date_livraison": b.date_livraison,
            "lieu_livraison": b.lieu_livraison,
            "statut": b.statut, "observations": b.observations,
        }
    finally:
        session.close()


# ─── ATTACHEMENTS ────────────────────────────────────────────────────────────────

def get_all_attachements():
    from database import SessionLocal
    from models import Attachement
    session = SessionLocal()
    try:
        atts = session.query(Attachement).order_by(Attachement.created_at.desc()).all()
        return [{
            "id": a.id, "numero": a.numero,
            "devis_numero": a.devis.numero if a.devis else "N/A",
            "commande_numero": a.devis.commande.numero if a.devis and a.devis.commande else "—",
            "client": a.devis.client.nom_complet if a.devis and a.devis.client else "N/A",
            "engin_nom": a.engin_obj.nom if a.engin_obj else (a.matricule_engin or "N/A"),
            "engin": a.engin_obj.nom if a.engin_obj else (a.matricule_engin or "N/A"),
            "matricule": a.matricule_engin,
            "mois": a.mois, "annee": a.annee,
            "projet": a.projet,
            "nb_jours": a.nb_jours_travailles,
            "nb_jours_travailles": a.nb_jours_travailles,
            "nb_heures_travaillees": a.nb_heures_travaillees,
            "nb_heures": a.nb_heures_travaillees,
        } for a in atts]
    finally:
        session.close()

def create_attachement(devis_id, engin_id, mois, annee, projet,
                        matricule_engin, jours_detail, observations=""):
    """
    jours_detail = [(jour, heures, jours_travail), ...]
    """
    from database import SessionLocal
    from models import Attachement, JourAttachement
    session = SessionLocal()
    try:
        numero = _next_num("ATT", Attachement)
        nb_j = sum(1 for _,_,jt in jours_detail if jt > 0)
        nb_h = sum(h for _,h,_ in jours_detail)
        att = Attachement(numero=numero, devis_id=devis_id, engin_id=engin_id,
                           mois=mois, annee=annee, projet=projet,
                           matricule_engin=matricule_engin,
                           nb_jours_travailles=nb_j,
                           nb_heures_travaillees=nb_h,
                           observations=observations)
        session.add(att); session.flush()
        for jour, heures, jt in jours_detail:
            session.add(JourAttachement(attachement_id=att.id, jour=jour,
                                         heures=heures, jours_travail=jt))
        session.commit()
        return att.id, numero
    except Exception as e:
        session.rollback(); raise e
    finally:
        session.close()


def create_attachement_multi(devis_id, engins_jours: list, mois, annee, projet, observations=""):
    """
    Crée UN SEUL attachement pour plusieurs engins d'un même client.
    engins_jours = [
        {
            "engin_id": int,
            "matricule": str,
            "nom": str,
            "jours_detail": [(jour, heures, jours_travail), ...]
        },
        ...
    ]
    """
    from database import SessionLocal
    from models import Attachement, JourAttachement
    session = SessionLocal()
    try:
        numero = _next_num("ATT", Attachement)
        # Totaux globaux — somme des valeurs réelles (0.5 = demi-jour, 1 = journée)
        nb_j_total = 0.0
        nb_h_total = 0.0
        for eng in engins_jours:
            nb_j_total += sum(float(jt) for _,_,jt in eng["jours_detail"] if jt > 0)
            nb_h_total += sum(float(jt) for _,_,jt in eng["jours_detail"] if jt > 0)

        att = Attachement(
            numero=numero, devis_id=devis_id,
            engin_id=engins_jours[0]["engin_id"] if engins_jours else None,
            mois=mois, annee=annee, projet=projet,
            matricule_engin=", ".join(e["matricule"] for e in engins_jours),
            nb_jours_travailles=nb_j_total,
            nb_heures_travaillees=nb_h_total,
            observations=observations
        )
        session.add(att); session.flush()

        # Enregistrer les jours par engin
        for eng in engins_jours:
            for jour, heures, jt in eng["jours_detail"]:
                session.add(JourAttachement(
                    attachement_id=att.id,
                    engin_id=eng["engin_id"],
                    matricule_engin=eng["matricule"],
                    jour=jour, heures=heures, jours_travail=jt
                ))

        session.commit()
        return att.id, numero
    except Exception as e:
        session.rollback(); raise e
    finally:
        session.close()


def get_attachement_by_id(att_id):
    from database import SessionLocal
    from models import Attachement, JourAttachement, Engin as EnginM
    session = SessionLocal()
    try:
        a = session.query(Attachement).filter(Attachement.id == att_id).first()
        if not a: return None

        # Charger tous les jours avec SQL direct (évite lazy loading)
        from sqlalchemy import text
        rows = session.execute(
            text("SELECT jour, heures, jours_travail, engin_id, matricule_engin "
                 "FROM jours_attachement WHERE attachement_id = :aid ORDER BY engin_id, matricule_engin, jour"),
            {"aid": att_id}
        ).fetchall()

        # Grouper par engin — clé = engin_id si disponible, sinon matricule
        from collections import OrderedDict
        engins_dict = OrderedDict()
        engin_cache = {}  # cache engin_id → obj

        for row in rows:
            jour, heures, jt, eid, mat = row
            val = float(jt if jt is not None else heures or 0)

            # Clé unique : priorité engin_id, sinon matricule
            if eid and eid not in engin_cache:
                eng_obj = session.query(EnginM).filter(EnginM.id == eid).first()
                engin_cache[eid] = eng_obj
            eng_obj = engin_cache.get(eid) if eid else None
            if not eng_obj and mat:
                eng_obj = session.query(EnginM).filter(EnginM.matricule == mat).first()
                if eng_obj:
                    engin_cache[eng_obj.id] = eng_obj

            # Clé = engin_id si dispo, sinon matricule (garantit séparation)
            key = eid if eid else mat

            if key not in engins_dict:
                nom = ""
                prix = 0
                if eng_obj:
                    nom = eng_obj.nom + (" / " + eng_obj.matricule if eng_obj.matricule else "")
                    prix = eng_obj.prix_journalier or 0
                elif mat:
                    nom = mat
                engins_dict[key] = {
                    "nom":       nom or (a.engin_obj.nom if a.engin_obj else a.matricule_engin or ""),
                    "matricule": (eng_obj.matricule if eng_obj else None) or mat or a.matricule_engin or "",
                    "prix":      prix,
                    "jours":     [],
                    "total":     0.0,
                }
            if val > 0:
                engins_dict[key]["jours"].append((jour, val, val))
                engins_dict[key]["total"] += val

        # Si pas de lignes (ancien attachement), fallback single engin
        if not engins_dict:
            engins_dict[0] = {
                "nom":      a.engin_obj.nom if a.engin_obj else (a.matricule_engin or ""),
                "matricule": a.matricule_engin or "",
                "prix":     a.engin_obj.prix_journalier if a.engin_obj else 0,
                "jours":    [],
                "total":    float(a.nb_jours_travailles or 0),
            }

        engins_lignes = list(engins_dict.values())

        # Calcul prix/jr pour facturation (premier engin)
        prix_j = engins_lignes[0]["prix"] if engins_lignes else 0

        return {
            "id":       a.id,
            "numero":   a.numero,
            "devis":    get_devis_by_id(a.devis_id),
            "engin_nom": engins_lignes[0]["nom"] if engins_lignes else (a.matricule_engin or ""),
            "matricule": a.matricule_engin,
            "prix_journalier": prix_j,
            "mois":     a.mois,
            "annee":    a.annee,
            "projet":   a.projet,
            "nb_jours_travailles":  a.nb_jours_travailles,
            "nb_heures_travaillees": a.nb_heures_travaillees,
            "nb_jours": a.nb_jours_travailles,
            "nb_heures": a.nb_heures_travaillees,
            "observations": a.observations,
            "engins_lignes": engins_lignes,   # ← multi-engins pour PDF
            "jours": engins_lignes[0]["jours"] if engins_lignes else [],
        }
    finally:
        session.close()


# ─── INTÉRÊTS DE RETARD ─────────────────────────────────────────────────────────

def appliquer_interets_retard(facture_id, taux_pct):
    from database import SessionLocal
    from models import Facture
    session = SessionLocal()
    try:
        f = session.query(Facture).filter(Facture.id == facture_id).first()
        if f:
            f.taux_interet_retard = taux_pct
            session.commit()
    finally:
        session.close()

def get_engins_disponibilite():
    """Retourne pour chaque engin: quantite totale, louee, commandee, disponible."""
    from database import SessionLocal
    from models import Engin, LigneCommande, LigneDevis, Commande, Devis
    from datetime import date as today_date
    session = SessionLocal()
    try:
        result = []
        today = today_date.today()
        for engin in session.query(Engin).all():
            # Compter loués (devis validés actifs)
            loues = session.query(LigneDevis).join(Devis).filter(
                LigneDevis.engin_id == engin.id,
                Devis.statut == "valide",
                Devis.date_debut <= today,
                Devis.date_fin   >= today,
            ).count()
            # Compter commandés
            commandes = session.query(LigneCommande).join(Commande).filter(
                LigneCommande.engin_id == engin.id,
                Commande.statut.in_(["en_attente","confirmee"]),
            ).count()
            total = engin.quantite_totale or 1
            dispo = max(0, total - loues - commandes)
            result.append({
                "id": engin.id, "nom": engin.nom, "matricule": engin.matricule,
                "type": engin.type_engin, "prix_jr": engin.prix_journalier,
                "statut": engin.statut, "photo_path": engin.photo_path,
                "total": total, "loues": loues,
                "commandes_count": commandes, "disponibles": dispo,
            })
        return result
    finally:
        session.close()


# ─── ATTESTATION DE RETARD ───────────────────────────────────────────────────────

def get_all_attestations():
    from database import SessionLocal
    from models import AttestationRetard
    session = SessionLocal()
    try:
        atts = session.query(AttestationRetard).order_by(
            AttestationRetard.created_at.desc()).all()
        return [{
            "id": a.id, "numero": a.numero,
            "facture_numero": a.facture.numero if a.facture else "N/A",
            "client": (a.facture.devis.client.nom_complet
                       if a.facture and a.facture.devis and a.facture.devis.client
                       else "N/A"),
            "date_emission": a.date_emission,
            "date_echeance_initiale": a.date_echeance_initiale,
            "nb_jours_retard": a.nb_jours_retard,
            "taux_interet": a.taux_interet,
            "montant_capital": a.montant_capital,
            "montant_interets": a.montant_interets,
            "montant_total": a.montant_total,
            "notes": a.notes,
        } for a in atts]
    finally:
        session.close()


def create_attestation_retard(facture_id, taux_interet, notes="",
                               nb_periodes=None, periode_label="Mensuel"):
    """
    Crée une attestation de retard.
    - Sans période (taux fixe) → intérêts calculés immédiatement
    - Avec période (jour/semaine/mois) → intérêts = 0, taux mentionné seulement
    """
    from database import SessionLocal
    from models import AttestationRetard, Facture
    from datetime import date as today_date
    session = SessionLocal()
    try:
        f = session.query(Facture).filter(Facture.id == facture_id).first()
        if not f:
            raise ValueError("Facture introuvable")

        today         = today_date.today()
        date_echeance = f.echeance or today
        nb_jours      = max(0, (today - date_echeance).days)
        capital       = round(f.solde_restant, 2)

        # Calculer intérêts SEULEMENT si taux fixe (sans période)
        taux_fixe = "taux fixe" in (periode_label or "").lower() or nb_periodes == 1
        if taux_fixe and taux_interet > 0:
            interets = round(capital * taux_interet / 100, 2)
        else:
            interets = 0.0  # Pas calculé — dépend de la durée finale

        total    = round(capital + interets, 2)

        # Inclure la période dans les notes
        notes_complet = f"[Taux : {periode_label}]\n{notes}" if notes else f"[Taux : {periode_label}]"

        numero = _next_num("ATR", AttestationRetard)
        att = AttestationRetard(
            numero=numero, facture_id=facture_id,
            date_emission=today,
            date_echeance_initiale=date_echeance,
            nb_jours_retard=nb_jours,
            taux_interet=taux_interet,
            montant_capital=capital,
            montant_interets=interets,
            montant_total=total,
            notes=notes_complet,
        )
        session.add(att)
        session.commit()
        return att.id, numero, nb_jours, capital, interets, total
    except Exception as e:
        session.rollback(); raise e
    finally:
        session.close()


def get_attestation_by_id(att_id):
    from database import SessionLocal
    from models import AttestationRetard
    session = SessionLocal()
    try:
        a = session.query(AttestationRetard).filter(AttestationRetard.id == att_id).first()
        if not a: return None
        f = a.facture
        devis = f.devis if f else None
        return {
            "id": a.id, "numero": a.numero,
            "facture_numero": f.numero if f else "N/A",
            "client_nom": devis.client.nom_complet if devis and devis.client else "N/A",
            "client_ice": devis.client.ice if devis and devis.client else "",
            "date_emission": a.date_emission,
            "date_echeance_initiale": a.date_echeance_initiale,
            "nb_jours_retard": a.nb_jours_retard,
            "taux_interet": a.taux_interet,
            "montant_capital": a.montant_capital,
            "montant_interets": a.montant_interets,
            "montant_total": a.montant_total,
            "notes": a.notes,
            "devis_periode": (
                f"{devis.date_debut.strftime('%d/%m/%Y')} — {devis.date_fin.strftime('%d/%m/%Y')}"
                if devis and devis.date_debut else "—"
            ),
        }
    finally:
        session.close()


# ─── FACTURE DEPUIS ATTACHEMENT ──────────────────────────────────────────────────

def create_facture_depuis_attachement(attachement_id, tva_taux=20.0,
                                       reduction_pct=0.0, echeance_jours=30):
    """
    Génère une facture basée sur le nombre de jours RÉELS de l'attachement.
    Le prix est calculé sur jours_travailles × prix_journalier de chaque engin.
    """
    from database import SessionLocal
    from models import Attachement, Facture, Devis, LigneDevis
    from datetime import timedelta, date as today_date
    session = SessionLocal()
    try:
        att = session.query(Attachement).filter(Attachement.id == attachement_id).first()
        if not att: raise ValueError("Attachement introuvable")
        if not att.devis: raise ValueError("Attachement sans devis associé")

        devis = att.devis
        engin = att.engin_obj

        # Recalculer sur la base des jours réels
        prix_jr = engin.prix_journalier if engin else 0
        jours_reels = att.nb_jours_travailles
        ht_att  = round(prix_jr * jours_reels, 2)
        tva_att = round(ht_att * tva_taux / 100, 2)
        base_ttc = round(ht_att + tva_att, 2)
        reduction = round(base_ttc * reduction_pct / 100, 2) if reduction_pct else 0.0
        ttc       = round(base_ttc - reduction, 2)

        numero = _next_num("FAC", Facture)
        echeance = today_date.today() + timedelta(days=echeance_jours)

        fac = Facture(
            numero=numero, devis_id=devis.id,
            date_emission=today_date.today(), echeance=echeance,
            montant_ht=ht_att, tva_taux=tva_taux,
            montant_tva=tva_att, reduction=reduction,
            reduction_pct=reduction_pct, montant_ttc=ttc,
        )
        session.add(fac)
        devis.statut = "facture"
        session.commit()
        return fac.id, numero
    except Exception as e:
        session.rollback(); raise e
    finally:
        session.close()


# ─── STATUT ENGIN SELON COMMANDES + LIVRAISONS ───────────────────────────────────

def update_statut_engin_apres_commande(commande_id):
    """Marque les engins comme 'commande' après validation d'une commande."""
    from database import SessionLocal
    from models import Commande, Engin
    session = SessionLocal()
    try:
        cmd = session.query(Commande).filter(Commande.id == commande_id).first()
        if cmd:
            for ligne in cmd.lignes:
                if ligne.engin:
                    ligne.engin.statut = "commande"
            session.commit()
    finally:
        session.close()


def update_statut_engin_apres_livraison(bon_livraison_id):
    """Marque les engins comme 'loue' après validation du bon de livraison."""
    from database import SessionLocal
    from models import BonLivraison, Engin
    session = SessionLocal()
    try:
        bl = session.query(BonLivraison).filter(BonLivraison.id == bon_livraison_id).first()
        if bl and bl.devis:
            for ligne in bl.devis.lignes:
                if ligne.engin:
                    ligne.engin.statut = "loue"
            bl.statut = "signe"
            session.commit()
    finally:
        session.close()


def get_factures_en_retard():
    """Retourne toutes les factures dont l'échéance est dépassée et non payées."""
    from database import SessionLocal
    from models import Facture
    from datetime import date as today_date
    session = SessionLocal()
    try:
        today = today_date.today()
        factures = session.query(Facture).filter(
            Facture.statut.in_(["en_attente","partiel"]),
            Facture.echeance < today
        ).all()
        result = []
        for f in factures:
            client_nom = (f.devis.client.nom_complet
                          if f.devis and f.devis.client else "N/A")
            nb_jours = (today - f.echeance).days if f.echeance else 0
            result.append({
                "id": f.id, "numero": f.numero,
                "client": client_nom,
                "echeance": f.echeance,
                "solde_restant": f.solde_restant,
                "nb_jours_retard": nb_jours,
            })
        return result
    finally:
        session.close()


# ─── AUTHENTIFICATION ADMIN ──────────────────────────────────────────────────────
import hashlib

def verifier_mot_de_passe(username: str, password: str) -> bool:
    from database import SessionLocal
    from models import AdminConfig
    session = SessionLocal()
    try:
        admin = session.query(AdminConfig).filter(
            AdminConfig.username == username
        ).first()
        if not admin:
            return False
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        return pwd_hash == admin.password_hash
    finally:
        session.close()

def changer_mot_de_passe(username: str, nouveau_mdp: str) -> bool:
    from database import SessionLocal
    from models import AdminConfig
    from datetime import datetime
    session = SessionLocal()
    try:
        admin = session.query(AdminConfig).filter(
            AdminConfig.username == username
        ).first()
        if not admin:
            return False
        admin.password_hash = hashlib.sha256(nouveau_mdp.encode()).hexdigest()
        admin.updated_at = datetime.utcnow()
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_admin_username() -> str:
    from database import SessionLocal
    from models import AdminConfig
    session = SessionLocal()
    try:
        admin = session.query(AdminConfig).first()
        return admin.username if admin else "Admin"
    finally:
        session.close()


# ─── FACTURE DEPUIS ATTACHEMENT (AVEC DATE ECHEANCE LIBRE) ───────────────────────

def create_facture_from_attachement(attachement_id: int, tva_taux: float,
                                     date_echeance, reduction_pct: float = 0.0,
                                     reduction_mad: float = 0.0, notes: str = ""):
    """
    Génère une facture depuis un attachement multi-engins.
    Chaque engin = ses jours réels × son prix journalier propre.
    """
    from database import SessionLocal
    from models import Attachement, Facture, Engin as EnginM
    from datetime import date as today_date
    from sqlalchemy import text
    session = SessionLocal()
    try:
        att = session.query(Attachement).filter(Attachement.id == attachement_id).first()
        if not att:
            raise ValueError("Attachement introuvable")
        if not att.devis:
            raise ValueError("Attachement sans devis associé")

        # ── Récupérer les jours par engin depuis get_attachement_by_id ──────────
        att_data = get_attachement_by_id(attachement_id)
        engins_lignes = att_data.get("engins_lignes", []) if att_data else []

        lignes_att = []
        ht_total   = 0.0

        if engins_lignes:
            for eng_ligne in engins_lignes:
                nb_jours = float(eng_ligne.get("total", 0) or 0)
                if nb_jours <= 0:
                    continue
                prix_jr  = float(eng_ligne.get("prix", 0) or 0)
                nom_eng  = eng_ligne.get("nom", "Engin")
                mat_eng  = eng_ligne.get("matricule", "")
                montant  = round(prix_jr * nb_jours, 2)
                ht_total += montant
                lignes_att.append({
                    "designation": f"LOCATION {nom_eng.upper().split(' / ')[0]}",
                    "matricule":   mat_eng,
                    "qte":         nb_jours,
                    "prix":        prix_jr,
                    "montant":     montant,
                })
        else:
            # Fallback ancienne logique
            engin = att.engin_obj
            prix_jr = engin.prix_journalier if engin else 0
            nb_j   = float(att.nb_jours_travailles or 0)
            ht_total = round(prix_jr * nb_j, 2)
            lignes_att.append({
                "designation": f"LOCATION {engin.nom.upper() if engin else ''}",
                "matricule":   engin.matricule if engin else "",
                "qte":         nb_j,
                "prix":        prix_jr,
                "montant":     ht_total,
            })

        ht_total  = round(ht_total, 2)
        tva_mont  = round(ht_total * tva_taux / 100, 2)
        base_ttc  = round(ht_total + tva_mont, 2)

        # Réduction
        if reduction_pct > 0:
            red = round(base_ttc * reduction_pct / 100, 2)
        else:
            red = round(reduction_mad, 2)
        ttc = max(0.0, round(base_ttc - red, 2))

        numero = _next_num("FAC", Facture)
        fac = Facture(
            numero=numero, devis_id=att.devis.id,
            attachement_id=att.id,
            date_emission=today_date.today(),
            echeance=date_echeance,
            montant_ht=ht_total, tva_taux=tva_taux,
            montant_tva=tva_mont, reduction=red,
            reduction_pct=reduction_pct if reduction_pct > 0 else 0.0,
            montant_ttc=ttc, notes=notes,
        )
        session.add(fac)
        att.devis.statut = "facture"
        session.commit()

        return fac.id, numero, ht_total, tva_mont, ttc, lignes_att

    except Exception as e:
        session.rollback(); raise e
    finally:
        session.close()


# ─── GESTION PAIEMENTS AVANCÉE ───────────────────────────────────────────────────

def get_suivi_paiements():
    """Vue consolidée de tous les paiements : payés, en attente, retard."""
    from database import SessionLocal
    from models import Facture
    from datetime import date as today_date
    session = SessionLocal()
    try:
        today = today_date.today()
        factures = session.query(Facture).all()
        result = []
        for f in factures:
            client_nom = (f.devis.client.nom_complet
                          if f.devis and f.devis.client else "N/A")
            nb_jours_retard = 0
            if f.echeance and f.statut in ["en_attente", "partiel", "retard"]:
                nb_jours_retard = max(0, (today - f.echeance).days)
                if nb_jours_retard > 0 and f.statut in ["en_attente", "partiel"]:
                    f.statut = "retard"
            result.append({
                "id": f.id, "numero": f.numero,
                "client": client_nom,
                "date_emission": f.date_emission,
                "echeance": f.echeance,
                "montant_ttc": f.montant_ttc,
                "montant_paye": f.montant_paye,
                "solde_restant": f.solde_restant,
                "statut": f.statut,
                "nb_jours_retard": nb_jours_retard,
                "devis_numero": f.devis.numero if f.devis else "N/A",
            })
        session.commit()
        return result
    finally:
        session.close()


# ─── STATUT ENGIN — QUANTITÉ DISPONIBLE ─────────────────────────────────────────

def update_quantite_engin(engin_id: int, nouvelle_quantite: int):
    from database import SessionLocal
    from models import Engin
    session = SessionLocal()
    try:
        e = session.query(Engin).filter(Engin.id == engin_id).first()
        if e:
            e.quantite_totale = max(1, nouvelle_quantite)
            session.commit()
            return True
        return False
    except Exception as ex:
        session.rollback(); raise ex
    finally:
        session.close()


# ─── ENGINS DISPONIBLES POUR COMMANDE ────────────────────────────────────────

def get_engins_disponibles_commande():
    """
    Retourne les engins ayant au moins 1 unité disponible.
    quantite_disponible = quantite_totale - quantite_louee - quantite_maintenance
    """
    session = SessionLocal()
    try:
        engins = session.query(Engin).order_by(Engin.nom).all()
        result = []
        for e in engins:
            dispo = max(0, (e.quantite_totale or 1)
                        - (e.quantite_louee or 0)
                        - (e.quantite_maintenance or 0))
            if dispo > 0:
                result.append({
                    "id":            e.id,
                    "nom":           e.nom,
                    "matricule":     e.matricule,
                    "type_engin":    e.type_engin,
                    "prix_journalier": e.prix_journalier,
                    "quantite_totale": e.quantite_totale or 1,
                    "quantite_louee":  e.quantite_louee or 0,
                    "quantite_maintenance": e.quantite_maintenance or 0,
                    "quantite_disponible": dispo,
                    "statut_affichage": f"{dispo} dispo / {e.quantite_louee or 0} loué(s) / {e.quantite_maintenance or 0} maintenance",
                })
        return result
    finally:
        session.close()


def incrementer_quantite_louee(engin_id: int, quantite: int = 1):
    """Incrémente la quantité louée d'un engin."""
    session = SessionLocal()
    try:
        e = session.query(Engin).filter(Engin.id == engin_id).first()
        if e:
            e.quantite_louee = (e.quantite_louee or 0) + quantite
            # Si tout est loué, marquer statut "loue"
            dispo = max(0, (e.quantite_totale or 1) - (e.quantite_louee or 0)
                        - (e.quantite_maintenance or 0))
            if dispo == 0:
                e.statut = "loue"
            session.commit()
    finally:
        session.close()


def decrementer_quantite_louee(engin_id: int, quantite: int = 1):
    """Décrémente la quantité louée (retour d'engin)."""
    session = SessionLocal()
    try:
        e = session.query(Engin).filter(Engin.id == engin_id).first()
        if e:
            e.quantite_louee = max(0, (e.quantite_louee or 0) - quantite)
            dispo = max(0, (e.quantite_totale or 1) - (e.quantite_louee or 0)
                        - (e.quantite_maintenance or 0))
            if dispo > 0:
                e.statut = "disponible"
            session.commit()
    finally:
        session.close()


def devis_vers_commande(devis_id: int) -> tuple:
    """
    Transforme un devis validé en commande.
    Transfère client, engins, dates automatiquement.
    Retourne (commande_id, numero_commande)
    """
    from models import Commande, LigneCommande, Devis, LigneDevis
    session = SessionLocal()
    try:
        d = session.query(Devis).filter(Devis.id == devis_id).first()
        if not d:
            raise ValueError("Devis introuvable")
        if d.statut != "valide":
            raise ValueError("Le devis doit être validé avant transformation")

        # Générer numéro commande
        year = d.date_creation.year if d.date_creation else __import__('datetime').date.today().year
        from sqlalchemy import func
        count = session.query(func.count(Commande.id)).scalar() or 0
        num_cmd = f"CMD-{year}-{str(count+1).zfill(3)}"

        # Créer la commande
        cmd = Commande(
            numero=num_cmd,
            client_id=d.client_id,
            date_commande=__import__('datetime').date.today(),
            date_debut=d.date_debut,
            date_fin=d.date_fin,
            statut="confirmee",
            notes=f"Généré depuis devis {d.numero}",
        )
        session.add(cmd)
        session.flush()

        # Transférer les lignes (engins)
        for ligne in d.lignes:
            lc = LigneCommande(
                commande_id=cmd.id,
                engin_id=ligne.engin_id,
                quantite=int(ligne.quantite or 1),
            )
            session.add(lc)
            # Mettre à jour statut engin (quantite_louee gérée au BL)
            engin = session.query(Engin).filter(Engin.id == ligne.engin_id).first()
            if engin:
                dispo = max(0, (engin.quantite_totale or 1)
                            - (engin.quantite_louee or 0)
                            - (engin.quantite_maintenance or 0))
                engin.statut = "commande" if dispo > 0 else "loue"

        # Lier devis à commande
        d.commande_id = cmd.id

        session.commit()
        return cmd.id, num_cmd
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def reset_quantites_engins():
    """Remet quantite_louee = 0 et statut = 'disponible' sur tous les engins."""
    session = SessionLocal()
    try:
        engins = session.query(Engin).all()
        for e in engins:
            e.quantite_louee = 0
            e.quantite_maintenance = 0
            e.statut = "disponible"
        session.commit()
    except Exception as ex:
        session.rollback()
        raise ex
    finally:
        session.close()