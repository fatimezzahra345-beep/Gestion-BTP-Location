"""
database.py — Gestion de la connexion DB
SQLite en local, PostgreSQL en production (Railway/cloud)
La base de données n'est JAMAIS perdue grâce à PostgreSQL persistant.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_engine():
    # En production (Railway), DATABASE_URL est définie automatiquement
    db_url = os.environ.get("DATABASE_URL", "")

    if db_url:
        # PostgreSQL en production — adapter le format pour SQLAlchemy
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        engine = create_engine(db_url, pool_pre_ping=True)
        print("✅ Connexion PostgreSQL (production)")
    else:
        # SQLite en local — pour développement
        db_path = os.path.join(os.path.dirname(__file__), "locationbtp.db")
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False}
        )
        print("✅ Connexion SQLite (local)")

    return engine


engine = get_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)