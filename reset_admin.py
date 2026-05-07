"""
reset_admin.py — Réinitialisation du mot de passe Admin
Exécutez ce script UNE SEULE FOIS depuis votre terminal :
    python reset_admin.py
"""
import sys, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from sqlalchemy import text, inspect

print("=" * 50)
print("  Réinitialisation du compte Admin — LocationBTP")
print("=" * 50)

# 1. Créer la table si elle n'existe pas
inspector = inspect(engine)
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS admin_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) DEFAULT 'Admin',
            password_hash VARCHAR(256) NOT NULL,
            updated_at DATETIME
        )
    """))
    conn.commit()

# 2. Nouveau mot de passe
NEW_PASSWORD = "Wassime2026"
USERNAME     = "Admin"
pwd_hash     = hashlib.sha256(NEW_PASSWORD.encode()).hexdigest()

# 3. Insérer ou mettre à jour
session = SessionLocal()
existing = session.execute(text("SELECT id FROM admin_config LIMIT 1")).fetchone()
if existing:
    session.execute(text(
        "UPDATE admin_config SET password_hash = :h, username = :u WHERE id = :id"
    ), {"h": pwd_hash, "u": USERNAME, "id": existing[0]})
else:
    session.execute(text(
        "INSERT INTO admin_config (username, password_hash) VALUES (:u, :h)"
    ), {"u": USERNAME, "h": pwd_hash})
session.commit()
session.close()

# 4. Vérification
from controller import verifier_mot_de_passe
ok = verifier_mot_de_passe(USERNAME, NEW_PASSWORD)

print()
print(f"  ✅ Compte Admin réinitialisé avec succès !" if ok else "  ❌ Erreur — relancez le script")
print()
print(f"  👤 Username  : {USERNAME}")
print(f"  🔑 Password  : {NEW_PASSWORD}")
print()
print("  Connectez-vous maintenant sur l'application.")
print("  Puis changez votre mot de passe dans ⚙️ Paramètres Admin.")
print("=" * 50)