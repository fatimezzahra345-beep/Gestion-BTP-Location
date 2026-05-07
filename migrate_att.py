"""migrate_att.py — Ajoute engin_id et matricule_engin à jours_attachement"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import engine
from sqlalchemy import text, inspect

inspector = inspect(engine)
cols = [c["name"] for c in inspector.get_columns("jours_attachement")]
print(f"Colonnes actuelles: {cols}")

with engine.connect() as conn:
    for col, defn in [("engin_id","INTEGER"),("matricule_engin","TEXT")]:
        if col not in cols:
            conn.execute(text(f"ALTER TABLE jours_attachement ADD COLUMN {col} {defn}"))
            conn.commit()
            print(f"✅ {col} ajouté")
        else:
            print(f"ℹ️  {col} déjà présent")

print("✅ Migration terminée — lancez : streamlit run app.py")