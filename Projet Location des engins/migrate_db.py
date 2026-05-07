"""
migrate_db.py — Migration de la base de données
Ajoute les colonnes quantite_louee et quantite_maintenance à la table engins.

Exécutez ce script UNE SEULE FOIS :
    python migrate_db.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text, inspect

print("=" * 50)
print("  Migration DB — LocationBTP")
print("=" * 50)

inspector = inspect(engine)

# ── Table engins ──────────────────────────────────────────────────────────────
cols_engins = [c["name"] for c in inspector.get_columns("engins")]
print(f"\nColonnes actuelles (engins) : {cols_engins}")

with engine.connect() as conn:
    migrations = [
        ("quantite_louee",       "INTEGER DEFAULT 0"),
        ("quantite_maintenance", "INTEGER DEFAULT 0"),
    ]
    for col, definition in migrations:
        if col not in cols_engins:
            try:
                conn.execute(text(f"ALTER TABLE engins ADD COLUMN {col} {definition}"))
                conn.commit()
                print(f"✅ Colonne '{col}' ajoutée")
            except Exception as e:
                print(f"⚠️  {col} : {e}")
        else:
            print(f"ℹ️  '{col}' existe déjà")

# ── Table commandes ───────────────────────────────────────────────────────────
try:
    cols_cmd = [c["name"] for c in inspector.get_columns("commandes")]
    with engine.connect() as conn:
        if "devis_id" not in cols_cmd:
            conn.execute(text("ALTER TABLE commandes ADD COLUMN devis_id INTEGER"))
            conn.commit()
            print("✅ Colonne 'devis_id' ajoutée à commandes")
        else:
            print("ℹ️  'devis_id' existe déjà dans commandes")
except Exception as e:
    print(f"⚠️  commandes : {e}")

# ── Table email_config ────────────────────────────────────────────────────────
with engine.connect() as conn:
    try:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS email_config (
                id INTEGER PRIMARY KEY,
                smtp_host TEXT DEFAULT 'smtp.gmail.com',
                smtp_port INTEGER DEFAULT 587,
                email_from TEXT,
                password TEXT,
                nom_expediteur TEXT DEFAULT 'Wassime BTP',
                active INTEGER DEFAULT 1,
                updated_at TEXT
            )
        """))
        conn.commit()
        print("✅ Table 'email_config' vérifiée")
    except Exception as e:
        print(f"⚠️  email_config : {e}")

# ── Vérification finale ───────────────────────────────────────────────────────
inspector2 = inspect(engine)
cols_final = [c["name"] for c in inspector2.get_columns("engins")]
print(f"\nColonnes finales (engins) : {cols_final}")

ok = "quantite_louee" in cols_final and "quantite_maintenance" in cols_final
print()
print("✅ Migration réussie ! Lancez maintenant : streamlit run app.py"
      if ok else "❌ Erreur — relancez le script")
print("=" * 50)