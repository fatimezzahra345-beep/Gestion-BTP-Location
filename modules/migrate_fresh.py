"""
migrate_fresh.py — Crée une base de données propre avec TOUTES les colonnes
Exécutez après avoir supprimé locationbtp.db :
    del locationbtp.db
    python migrate_fresh.py
    streamlit run app.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 55)
print("  Création base de données — LocationBTP Wassime BTP")
print("=" * 55)

from database import engine
from sqlalchemy import text, inspect

# ── Créer toutes les tables depuis models.py ──────────────────────────────────
from models import Base, init_db
Base.metadata.create_all(bind=engine)
print("✅ Tables principales créées")

# ── Ajouter toutes les colonnes manquantes ────────────────────────────────────
def add_col(table, col, defn):
    inspector = inspect(engine)
    try:
        cols = [c["name"] for c in inspector.get_columns(table)]
        if col not in cols:
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {defn}"))
                conn.commit()
            print(f"✅ {table}.{col}")
        else:
            print(f"ℹ️  {table}.{col} — déjà présent")
    except Exception as e:
        print(f"⚠️  {table}.{col}: {e}")

# Engins
add_col("engins", "quantite_totale",      "INTEGER DEFAULT 1")
add_col("engins", "quantite_louee",       "INTEGER DEFAULT 0")
add_col("engins", "quantite_maintenance", "INTEGER DEFAULT 0")

# Commandes
add_col("commandes", "devis_id", "INTEGER")

# Factures
add_col("factures", "attachement_id",      "INTEGER")
add_col("factures", "montant_ht",          "REAL DEFAULT 0")
add_col("factures", "tva_taux",            "REAL DEFAULT 20")
add_col("factures", "montant_tva",         "REAL DEFAULT 0")
add_col("factures", "reduction",           "REAL DEFAULT 0")
add_col("factures", "reduction_pct",       "REAL DEFAULT 0")
add_col("factures", "solde_restant",       "REAL DEFAULT 0")
add_col("factures", "montant_paye",        "REAL DEFAULT 0")
add_col("factures", "taux_interet_retard", "REAL DEFAULT 0")

# Jours attachement
add_col("jours_attachement", "engin_id",       "INTEGER")
add_col("jours_attachement", "matricule_engin", "TEXT")

# ── Table email_config ────────────────────────────────────────────────────────
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS email_config (
            id             INTEGER PRIMARY KEY,
            smtp_host      TEXT    DEFAULT 'smtp.gmail.com',
            smtp_port      INTEGER DEFAULT 587,
            email_from     TEXT,
            password       TEXT,
            nom_expediteur TEXT    DEFAULT 'Wassime BTP',
            active         INTEGER DEFAULT 1,
            updated_at     TEXT
        )
    """))
    conn.commit()
    print("✅ Table email_config")

# ── Initialiser admin ─────────────────────────────────────────────────────────
init_db()
print("✅ Compte Admin créé (Admin / Wassime2026)")

print()
print("✅ Base prête ! Lancez : streamlit run app.py")
print("=" * 55)