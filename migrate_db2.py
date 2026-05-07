"""
migrate_db2.py — Ajoute la colonne attachement_id à la table factures
Exécutez UNE SEULE FOIS : python migrate_db2.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text, inspect

print("=" * 50)
print("  Migration DB v2 — LocationBTP")
print("=" * 50)

inspector = inspect(engine)

with engine.connect() as conn:
    # Table factures — ajout attachement_id
    cols_fac = [c["name"] for c in inspector.get_columns("factures")]
    if "attachement_id" not in cols_fac:
        conn.execute(text("ALTER TABLE factures ADD COLUMN attachement_id INTEGER"))
        conn.commit()
        print("✅ Colonne 'attachement_id' ajoutée à factures")
    else:
        print("ℹ️  'attachement_id' existe déjà")

print("\n✅ Migration réussie ! Lancez : streamlit run app.py")
print("=" * 50)
