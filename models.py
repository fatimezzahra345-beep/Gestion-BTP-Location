"""
models.py — Modèles SQLAlchemy pour LocationBTP
Supporte SQLite (local) et PostgreSQL (production/Railway)
"""
from sqlalchemy import (Column, Integer, String, Float, Date, DateTime,
                        Text, ForeignKey, Boolean)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

Base = declarative_base()

class Engin(Base):
    __tablename__ = "engins"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    nom             = Column(String(100), nullable=False)
    matricule       = Column(String(50),  unique=True, nullable=False)
    type_engin      = Column(String(100))
    quantite_totale      = Column(Integer, default=1)   # total dans le parc
    quantite_louee       = Column(Integer, default=0)   # en location active
    quantite_maintenance = Column(Integer, default=0)   # en maintenance
    prix_journalier = Column(Float,   nullable=False)
    statut          = Column(String(20), default="disponible")  # disponible/loue/maintenance/commande
    photo_path      = Column(String(255), nullable=True)
    description     = Column(Text, nullable=True)
    date_acquisition= Column(Date, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    @property
    def quantite_disponible(self):
        return max(0,(self.quantite_totale or 1)-(self.quantite_louee or 0)-(self.quantite_maintenance or 0))

    lignes_devis    = relationship("LigneDevis",   back_populates="engin")
    commandes       = relationship("LigneCommande",back_populates="engin")

class Client(Base):
    __tablename__ = "clients"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    nom        = Column(String(100), nullable=False)
    prenom     = Column(String(100), nullable=True)
    societe    = Column(String(150), nullable=True)
    ice        = Column(String(50),  nullable=True)
    telephone  = Column(String(20),  nullable=True)
    email      = Column(String(100), nullable=True)
    adresse    = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    devis      = relationship("Devis",    back_populates="client")
    commandes  = relationship("Commande", back_populates="client")

    @property
    def nom_complet(self):
        return self.societe or f"{self.prenom or ''} {self.nom}".strip()

class Commande(Base):
    """Bon de commande reçu d'un client."""
    __tablename__ = "commandes"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    numero      = Column(String(20), unique=True, nullable=False)
    client_id   = Column(Integer, ForeignKey("clients.id"), nullable=False)
    date_commande = Column(Date, default=date.today)
    date_debut  = Column(Date, nullable=False)
    date_fin    = Column(Date, nullable=False)
    statut      = Column(String(20), default="en_attente")  # en_attente/confirmee/annulee/livree
    notes       = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    client      = relationship("Client",       back_populates="commandes")
    lignes      = relationship("LigneCommande",back_populates="commande", cascade="all, delete-orphan")
    devis       = relationship("Devis",        back_populates="commande", uselist=False)

    @property
    def duree_jours(self):
        return (self.date_fin - self.date_debut).days + 1 if self.date_debut and self.date_fin else 0

class LigneCommande(Base):
    __tablename__ = "lignes_commande"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    commande_id = Column(Integer, ForeignKey("commandes.id"), nullable=False)
    engin_id    = Column(Integer, ForeignKey("engins.id"),    nullable=False)
    quantite    = Column(Integer, default=1)
    commande    = relationship("Commande", back_populates="lignes")
    engin       = relationship("Engin",    back_populates="commandes")

class Devis(Base):
    __tablename__ = "devis"
    id                  = Column(Integer, primary_key=True, autoincrement=True)
    numero              = Column(String(20), unique=True, nullable=False)
    client_id           = Column(Integer, ForeignKey("clients.id"),   nullable=False)
    commande_id         = Column(Integer, ForeignKey("commandes.id"), nullable=True)
    date_creation       = Column(Date, default=date.today)
    date_debut          = Column(Date, nullable=False)
    date_fin            = Column(Date, nullable=False)
    montant_ht          = Column(Float, default=0.0)
    tva_taux            = Column(Float, default=20.0)
    montant_tva         = Column(Float, default=0.0)
    montant_ttc         = Column(Float, default=0.0)
    statut              = Column(String(20), default="brouillon")
    notes               = Column(Text, nullable=True)
    echeance_paiement   = Column(Date, nullable=True)
    created_at          = Column(DateTime, default=datetime.utcnow)
    client              = relationship("Client",   back_populates="devis")
    commande            = relationship("Commande", back_populates="devis")
    lignes              = relationship("LigneDevis",back_populates="devis", cascade="all, delete-orphan")
    factures            = relationship("Facture",  back_populates="devis")
    bons_livraison      = relationship("BonLivraison", back_populates="devis")
    attachements        = relationship("Attachement",  back_populates="devis")

    @property
    def duree_jours(self):
        return (self.date_fin - self.date_debut).days + 1 if self.date_debut and self.date_fin else 0

class LigneDevis(Base):
    __tablename__ = "lignes_devis"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    devis_id      = Column(Integer, ForeignKey("devis.id"),   nullable=False)
    engin_id      = Column(Integer, ForeignKey("engins.id"),  nullable=False)
    quantite      = Column(Float, default=1.0)
    prix_unitaire = Column(Float, nullable=False)
    montant       = Column(Float, nullable=False)
    description   = Column(Text, nullable=True)
    devis         = relationship("Devis",  back_populates="lignes")
    engin         = relationship("Engin",  back_populates="lignes_devis")

class BonLivraison(Base):
    __tablename__ = "bons_livraison"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    numero        = Column(String(20), unique=True, nullable=False)
    devis_id      = Column(Integer, ForeignKey("devis.id"), nullable=False)
    date_livraison= Column(Date, default=date.today)
    lieu_livraison= Column(String(200), nullable=True)
    observations  = Column(Text, nullable=True)
    statut        = Column(String(20), default="emis")  # emis/recu/signe
    created_at    = Column(DateTime, default=datetime.utcnow)
    devis         = relationship("Devis", back_populates="bons_livraison")

class Attachement(Base):
    """Document d'attachement : relevé journalier de travail réel d'un engin."""
    __tablename__ = "attachements"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    numero        = Column(String(20), unique=True, nullable=False)
    devis_id      = Column(Integer, ForeignKey("devis.id"),   nullable=False)
    engin_id      = Column(Integer, ForeignKey("engins.id"),  nullable=True)
    mois          = Column(Integer, nullable=False)   # 1-12
    annee         = Column(Integer, nullable=False)
    projet        = Column(String(200), nullable=True)
    matricule_engin = Column(String(50), nullable=True)
    nb_jours_travailles = Column(Integer, default=0)
    nb_heures_travaillees = Column(Float, default=0.0)
    observations  = Column(Text, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    devis         = relationship("Devis",  back_populates="attachements")
    engin_obj     = relationship("Engin")
    jours         = relationship("JourAttachement", back_populates="attachement",
                                 cascade="all, delete-orphan")

class JourAttachement(Base):
    """Détail jour par jour de l'attachement — un enregistrement par engin par jour."""
    __tablename__ = "jours_attachement"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    attachement_id  = Column(Integer, ForeignKey("attachements.id"), nullable=False)
    engin_id        = Column(Integer, ForeignKey("engins.id"), nullable=True)
    matricule_engin = Column(String(50), nullable=True)
    jour            = Column(Integer, nullable=False)    # 1-31
    heures          = Column(Float, default=0.0)
    jours_travail   = Column(Float, default=0.0)         # 0 ou 1
    attachement     = relationship("Attachement", back_populates="jours")

class Facture(Base):
    __tablename__ = "factures"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    numero          = Column(String(20), unique=True, nullable=False)
    devis_id        = Column(Integer, ForeignKey("devis.id"), nullable=False)
    attachement_id  = Column(Integer, ForeignKey("attachements.id"), nullable=True)
    date_emission   = Column(Date, default=date.today)
    echeance        = Column(Date, nullable=True)
    montant_ht      = Column(Float, default=0.0)
    tva_taux        = Column(Float, default=20.0)
    montant_tva     = Column(Float, default=0.0)
    reduction       = Column(Float, default=0.0)
    reduction_pct   = Column(Float, default=0.0)
    montant_ttc     = Column(Float, nullable=False)
    montant_paye    = Column(Float, default=0.0)
    statut          = Column(String(20), default="en_attente")
    taux_interet_retard = Column(Float, default=0.0)   # % intérêts de retard
    notes           = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    devis           = relationship("Devis", back_populates="factures")

    @property
    def solde_restant(self):
        return max(0.0, self.montant_ttc - self.montant_paye)

    @property
    def interets_retard(self):
        if self.taux_interet_retard and self.solde_restant > 0:
            return round(self.solde_restant * self.taux_interet_retard / 100, 2)
        return 0.0

    @property
    def total_avec_interets(self):
        return round(self.solde_restant + self.interets_retard, 2)


# ── Initialisation DB ─────────────────────────────────────────────────────────
def init_db():
    from database import engine, SessionLocal
    from sqlalchemy import text, inspect

    # 1. Créer toutes les nouvelles tables (sans toucher aux existantes)
    Base.metadata.create_all(bind=engine)

    # 2. Migration complète : ajouter TOUTES les colonnes manquantes
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    def get_cols(table):
        if table not in existing_tables:
            return []
        return [c["name"] for c in inspector.get_columns(table)]

    migrations = {
        # table : [(colonne, définition SQL)]
        "engins": [
            ("quantite_totale", "INTEGER DEFAULT 1"),
        ],
        "devis": [
            ("commande_id", "INTEGER"),
            ("echeance_paiement", "DATE"),
        ],
        "factures": [
            ("montant_ht",          "REAL DEFAULT 0"),
            ("tva_taux",            "REAL DEFAULT 20"),
            ("montant_tva",         "REAL DEFAULT 0"),
            ("reduction",           "REAL DEFAULT 0"),
            ("reduction_pct",       "REAL DEFAULT 0"),
            ("taux_interet_retard", "REAL DEFAULT 0"),
        ],
        "lignes_devis": [
            ("description", "TEXT"),
        ],
    }

    with engine.connect() as conn:
        for table, cols in migrations.items():
            existing_cols = get_cols(table)
            for col_name, col_def in cols:
                if col_name not in existing_cols:
                    try:
                        conn.execute(text(
                            f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}"
                        ))
                        conn.commit()
                    except Exception:
                        pass  # colonne déjà existante ou autre erreur ignorée

    # 2b. Créer les nouvelles tables si pas encore existantes
    # (AttestationRetard et AdminConfig sont créées par create_all ci-dessus)

    # Ajouter colonnes manquantes dans tables existantes
    cols_fac = get_cols("factures")
    with engine.connect() as conn:
        for col, typ in [
            ("montant_ht","REAL DEFAULT 0"),("tva_taux","REAL DEFAULT 20"),
            ("montant_tva","REAL DEFAULT 0"),("reduction","REAL DEFAULT 0"),
            ("reduction_pct","REAL DEFAULT 0"),("taux_interet_retard","REAL DEFAULT 0"),
        ]:
            if col not in cols_fac:
                try:
                    conn.execute(text(f"ALTER TABLE factures ADD COLUMN {col} {typ}"))
                    conn.commit()
                except Exception: pass

    # 3. Données par défaut (engins de base si table vide)
    session = SessionLocal()
    try:
        if session.query(Engin).count() == 0:
            for nom, mat, typ, qty, prix in [
                ("CAMION 8X4",                    "CAM-8X4-001", "Camion",         1, 1700.0),
                ("NIVELEUSE 12G",                  "NIV-12G-001", "Niveleuse",      1, 2000.0),
                ("COMPACTEUR 15T",                 "COM-15T-001", "Compacteur",     1, 1500.0),
                ("PELLE HYDRAULIQUE CHENILLE",     "PEL-CH-001",  "Pelle",          1, 2000.0),
                ("PELLE HYDRAULIQUE PNEUS",        "PEL-PN-001",  "Pelle",          1, 2000.0),
                ("CHARGEUSE CATERPILLAR",          "CHA-CAT-001", "Chargeuse",      1, 1500.0),
                ("CHARIOT ÉLÉVATEUR TÉLESCOPIQUE", "CHT-TEL-001", "Chariot",        1, 1500.0),
                ("TRACTOPELLE",                    "TRA-001",     "Tractopelle",    2,  900.0),
                ("CAMION CITERNE",                 "CAM-CIT-001", "Camion Citerne", 3,  900.0),
            ]:
                session.add(Engin(
                    nom=nom, matricule=mat, type_engin=typ,
                    quantite_totale=qty, prix_journalier=prix
                ))
            session.commit()
        # Créer le compte admin par défaut si non existant
        from models import AdminConfig
        import hashlib
        if session.query(AdminConfig).count() == 0:
            # Mot de passe par défaut : Wassime2026
            pwd_hash = hashlib.sha256("Wassime2026".encode()).hexdigest()
            session.add(AdminConfig(username="Admin", password_hash=pwd_hash))
            session.commit()
    finally:
        session.close()


class AttestationRetard(Base):
    """Attestation de retard de paiement avec intérêts."""
    __tablename__ = "attestations_retard"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    numero          = Column(String(20), unique=True, nullable=False)
    facture_id      = Column(Integer, ForeignKey("factures.id"), nullable=False)
    date_emission   = Column(Date, default=date.today)
    date_echeance_initiale = Column(Date, nullable=True)
    nb_jours_retard = Column(Integer, default=0)
    taux_interet    = Column(Float, default=1.5)   # % par mois
    montant_capital = Column(Float, default=0.0)   # solde dû
    montant_interets= Column(Float, default=0.0)   # intérêts calculés
    montant_total   = Column(Float, default=0.0)   # capital + intérêts
    notes           = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    facture         = relationship("Facture")


class AdminConfig(Base):
    """Configuration admin : mot de passe hashé, username."""
    __tablename__ = "admin_config"
    id            = Column(Integer, primary_key=True)
    username      = Column(String(50), default="Admin")
    password_hash = Column(String(256), nullable=False)
    updated_at    = Column(DateTime, default=datetime.utcnow)