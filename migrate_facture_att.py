"""
migrate_facture_att.py — Ajoute attachement_id à la table factures
Exécutez UNE SEULE FOIS : python migrate_facture_att.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text, inspect

print("=" * 50)
print("  Migration factures.attachement_id")
print("=" * 50)

inspector = inspect(engine)
cols = [c["name"] for c in inspector.get_columns("factures")]
print(f"Colonnes actuelles : {cols}")

with engine.connect() as conn:
    if "attachement_id" not in cols:
        conn.execute(text("ALTER TABLE factures ADD COLUMN attachement_id INTEGER"))
        conn.commit()
        print("✅ Colonne 'attachement_id' ajoutée à factures")
    else:
        print("ℹ️  'attachement_id' existe déjà")

print("\n✅ Migration terminée ! Lancez : streamlit run app.py")
print("=" * 50)