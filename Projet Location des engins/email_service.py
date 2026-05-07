"""
email_service.py — Service d'envoi d'emails automatiques
LocationBTP | Wassime BTP

Utilise SMTP Gmail (ou autre fournisseur).
Configuration dans l'onglet Paramètres Admin de l'application.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import date
from database import SessionLocal
from sqlalchemy import text


# ─── CONFIG EMAIL (lue depuis la base de données) ────────────────────────────

def get_email_config() -> dict:
    """Récupère la configuration email depuis la base de données."""
    session = SessionLocal()
    try:
        result = session.execute(
            text("SELECT * FROM email_config LIMIT 1")
        ).fetchone()
        if result:
            return {
                "smtp_host":  result[1],
                "smtp_port":  result[2],
                "email_from": result[3],
                "password":   result[4],
                "nom_expediteur": result[5],
                "active":     bool(result[6]),
            }
        return {}
    except Exception:
        return {}
    finally:
        session.close()


def save_email_config(smtp_host, smtp_port, email_from, password,
                      nom_expediteur, active=True):
    """Enregistre ou met à jour la configuration email."""
    session = SessionLocal()
    try:
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS email_config (
                id INTEGER PRIMARY KEY,
                smtp_host TEXT,
                smtp_port INTEGER DEFAULT 587,
                email_from TEXT,
                password TEXT,
                nom_expediteur TEXT DEFAULT 'Wassime BTP',
                active INTEGER DEFAULT 1,
                updated_at TEXT
            )
        """))
        existing = session.execute(
            text("SELECT id FROM email_config LIMIT 1")
        ).fetchone()
        if existing:
            session.execute(text("""
                UPDATE email_config SET
                    smtp_host=:h, smtp_port=:p, email_from=:f,
                    password=:pw, nom_expediteur=:n, active=:a,
                    updated_at=datetime('now')
                WHERE id=:id
            """), {"h":smtp_host,"p":smtp_port,"f":email_from,
                   "pw":password,"n":nom_expediteur,"a":int(active),"id":existing[0]})
        else:
            session.execute(text("""
                INSERT INTO email_config
                (smtp_host,smtp_port,email_from,password,nom_expediteur,active,updated_at)
                VALUES (:h,:p,:f,:pw,:n,:a,datetime('now'))
            """), {"h":smtp_host,"p":smtp_port,"f":email_from,
                   "pw":password,"n":nom_expediteur,"a":int(active)})
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def tester_connexion_smtp(smtp_host, smtp_port, email_from, password) -> tuple:
    """
    Teste la connexion SMTP.
    Retourne (True, "OK") ou (False, "message d'erreur")
    """
    try:
        # Désactiver vérif SSL (fix Python 3.12+ Windows)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with smtplib.SMTP(smtp_host, int(smtp_port), timeout=10) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(email_from, password)
        return True, "Connexion SMTP réussie !"
    except smtplib.SMTPAuthenticationError:
        return False, "Erreur d'authentification — vérifiez email et mot de passe d'application."
    except smtplib.SMTPConnectError:
        return False, f"Impossible de se connecter à {smtp_host}:{smtp_port}"
    except Exception as e:
        return False, f"Erreur : {str(e)}"


# ─── ENVOI GÉNÉRIQUE ─────────────────────────────────────────────────────────

def envoyer_email(destinataire: str, sujet: str, corps_html: str,
                  pdf_bytes: bytes = None, nom_pdf: str = None) -> tuple:
    """
    Envoie un email HTML avec pièce jointe PDF optionnelle.
    Retourne (True, "OK") ou (False, "erreur")
    """
    config = get_email_config()
    if not config:
        return False, "Configuration email non définie. Configurez dans Paramètres."
    if not config.get("active"):
        return False, "Envoi email désactivé dans les paramètres."
    if not destinataire or "@" not in destinataire:
        return False, f"Email client invalide : '{destinataire}'"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = sujet
        msg["From"]    = f"{config['nom_expediteur']} <{config['email_from']}>"
        msg["To"]      = destinataire

        # Corps HTML
        msg.attach(MIMEText(corps_html, "html", "utf-8"))

        # Pièce jointe PDF
        if pdf_bytes and nom_pdf:
            attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
            attachment.add_header("Content-Disposition", "attachment",
                                  filename=nom_pdf)
            msg.attach(attachment)

        # Envoi SMTP
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with smtplib.SMTP(config["smtp_host"], int(config["smtp_port"]),
                          timeout=15) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(config["email_from"], config["password"])
            server.sendmail(config["email_from"], destinataire, msg.as_string())

        return True, f"Email envoyé à {destinataire}"
    except smtplib.SMTPRecipientsRefused:
        return False, f"Adresse email refusée : {destinataire}"
    except smtplib.SMTPAuthenticationError:
        return False, "Erreur d'authentification SMTP — vérifiez vos identifiants."
    except Exception as e:
        return False, f"Erreur envoi : {str(e)}"


# ─── TEMPLATES HTML ──────────────────────────────────────────────────────────

def _template_base(contenu: str, titre: str) -> str:
    """Template HTML professionnel Wassime BTP."""
    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background:#F8FAFC; margin:0; padding:0; color:#334155; }}
  .container {{ max-width:600px; margin:32px auto; background:white;
                border-radius:12px; overflow:hidden;
                box-shadow:0 4px 24px rgba(0,0,0,.08); }}
  .header {{ background:linear-gradient(135deg,#0F172A,#1E3A5F);
             padding:28px 32px; text-align:center; }}
  .header-title {{ color:#E2E8F0; font-size:22px; font-weight:800;
                   letter-spacing:-0.3px; margin:0; }}
  .header-sub {{ color:#94A3B8; font-size:12px; margin-top:6px;
                 text-transform:uppercase; letter-spacing:1px; }}
  .accent {{ height:4px; background:linear-gradient(90deg,#2563EB,#10B981); }}
  .body {{ padding:32px; }}
  .title {{ font-size:20px; font-weight:700; color:#0F172A;
            margin-bottom:8px; }}
  .subtitle {{ font-size:14px; color:#64748B; margin-bottom:24px; }}
  .card {{ background:#F8FAFC; border:1px solid #E2E8F0;
           border-radius:10px; padding:20px; margin:20px 0; }}
  .card-row {{ display:flex; justify-content:space-between;
               padding:8px 0; border-bottom:1px solid #F1F5F9; }}
  .card-row:last-child {{ border-bottom:none; }}
  .card-label {{ color:#64748B; font-size:13px; }}
  .card-value {{ color:#0F172A; font-size:13px; font-weight:600; }}
  .amount {{ font-size:28px; font-weight:900; color:#2563EB;
             letter-spacing:-0.5px; text-align:center;
             padding:16px; background:#EFF6FF; border-radius:10px;
             margin:16px 0; }}
  .btn {{ display:block; background:#2563EB; color:white !important;
          text-decoration:none; text-align:center; padding:14px 28px;
          border-radius:8px; font-weight:700; font-size:14px;
          margin:24px 0; }}
  .alert {{ background:#FEF2F2; border-left:4px solid #EF4444;
            border-radius:0 8px 8px 0; padding:14px 18px; margin:16px 0; }}
  .success {{ background:#ECFDF5; border-left:4px solid #10B981;
              border-radius:0 8px 8px 0; padding:14px 18px; margin:16px 0; }}
  .footer {{ background:#F8FAFC; border-top:1px solid #E2E8F0;
             padding:20px 32px; text-align:center;
             font-size:11px; color:#94A3B8; }}
  .footer strong {{ color:#64748B; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="header-title">🏗️ Wassime BTP</div>
    <div class="header-sub">Location d'Engins de Chantier — Marrakech</div>
  </div>
  <div class="accent"></div>
  <div class="body">
    {contenu}
  </div>
  <div class="footer">
    <strong>Ste Wassime BTP</strong> · ICE : 003440371000093<br>
    📞 +212 688 540 102 · ✉️ STEWASSIMEBTP@GMAIL.COM<br>
    Marrakech, Maroc
  </div>
</div>
</body>
</html>
"""


# ─── EMAILS MÉTIER ───────────────────────────────────────────────────────────

def email_devis(client_nom: str, client_email: str, devis_num: str,
                date_debut: str, date_fin: str, montant_ttc: float,
                pdf_bytes: bytes) -> tuple:
    """Email envoyé au client lors de la création d'un devis."""
    contenu = f"""
    <div class="title">Votre Devis {devis_num}</div>
    <div class="subtitle">Bonjour {client_nom}, veuillez trouver ci-joint votre devis de location.</div>
    <div class="card">
      <div class="card-row">
        <span class="card-label">Référence</span>
        <span class="card-value">{devis_num}</span>
      </div>
      <div class="card-row">
        <span class="card-label">Période de location</span>
        <span class="card-value">{date_debut} → {date_fin}</span>
      </div>
      <div class="card-row">
        <span class="card-label">Date d'émission</span>
        <span class="card-value">{date.today().strftime('%d/%m/%Y')}</span>
      </div>
    </div>
    <div class="amount">{montant_ttc:,.2f} MAD TTC</div>
    <div class="success">
      📎 Votre devis est joint en PDF à cet email.<br>
      Pour toute question, contactez-nous au <strong>+212 688 540 102</strong>.
    </div>
    <p style="font-size:13px;color:#64748B">
      Ce devis est valable 30 jours à compter de sa date d'émission.
      Merci de votre confiance.
    </p>
    """
    return envoyer_email(
        destinataire=client_email,
        sujet=f"Wassime BTP — Devis {devis_num}",
        corps_html=_template_base(contenu, f"Devis {devis_num}"),
        pdf_bytes=pdf_bytes,
        nom_pdf=f"Devis_{devis_num}_WassimeBTP.pdf"
    )


def email_facture(client_nom: str, client_email: str, facture_num: str,
                  devis_num: str, montant_ttc: float, echeance: str,
                  pdf_bytes: bytes) -> tuple:
    """Email envoyé au client avec la facture."""
    contenu = f"""
    <div class="title">Facture {facture_num}</div>
    <div class="subtitle">Bonjour {client_nom}, veuillez trouver ci-joint votre facture.</div>
    <div class="card">
      <div class="card-row">
        <span class="card-label">N° Facture</span>
        <span class="card-value">{facture_num}</span>
      </div>
      <div class="card-row">
        <span class="card-label">Référence Devis</span>
        <span class="card-value">{devis_num}</span>
      </div>
      <div class="card-row">
        <span class="card-label">Date d'émission</span>
        <span class="card-value">{date.today().strftime('%d/%m/%Y')}</span>
      </div>
      <div class="card-row">
        <span class="card-label">📅 Date d'échéance</span>
        <span class="card-value" style="color:#EF4444;font-weight:700">{echeance}</span>
      </div>
    </div>
    <div class="amount">{montant_ttc:,.2f} MAD TTC</div>
    <div class="success">
      📎 Votre facture est jointe en PDF.<br>
      Merci de procéder au règlement avant le <strong>{echeance}</strong>.
    </div>
    <p style="font-size:13px;color:#64748B">
      Coordonnées bancaires :<br>
      <strong>RIB :</strong> 145 450 2121167962380017 92 BP
    </p>
    """
    return envoyer_email(
        destinataire=client_email,
        sujet=f"Wassime BTP — Facture {facture_num}",
        corps_html=_template_base(contenu, f"Facture {facture_num}"),
        pdf_bytes=pdf_bytes,
        nom_pdf=f"Facture_{facture_num}_WassimeBTP.pdf"
    )


def email_bon_livraison(client_nom: str, client_email: str, bl_num: str,
                        lieu: str, date_livraison: str,
                        pdf_bytes: bytes) -> tuple:
    """Email envoyé au client avec le bon de livraison."""
    contenu = f"""
    <div class="title">Bon de Livraison {bl_num}</div>
    <div class="subtitle">Bonjour {client_nom}, voici votre bon de livraison.</div>
    <div class="card">
      <div class="card-row">
        <span class="card-label">N° BL</span>
        <span class="card-value">{bl_num}</span>
      </div>
      <div class="card-row">
        <span class="card-label">Date de livraison</span>
        <span class="card-value">{date_livraison}</span>
      </div>
      <div class="card-row">
        <span class="card-label">Lieu de livraison</span>
        <span class="card-value">{lieu or 'Non spécifié'}</span>
      </div>
    </div>
    <div class="success">
      ✅ Les engins ont été préparés et sont prêts pour la livraison.<br>
      📎 Le bon de livraison est joint en PDF.
    </div>
    <p style="font-size:13px;color:#64748B">
      Merci de signer le bon de livraison à la réception des engins.
    </p>
    """
    return envoyer_email(
        destinataire=client_email,
        sujet=f"Wassime BTP — Bon de Livraison {bl_num}",
        corps_html=_template_base(contenu, f"BL {bl_num}"),
        pdf_bytes=pdf_bytes,
        nom_pdf=f"BL_{bl_num}_WassimeBTP.pdf"
    )


def email_relance_paiement(client_nom: str, client_email: str,
                            facture_num: str, montant_ttc: float,
                            montant_paye: float, solde: float,
                            echeance: str, nb_jours_retard: int) -> tuple:
    """Email de relance pour facture en retard."""
    contenu = f"""
    <div class="title">Rappel de Paiement — {facture_num}</div>
    <div class="subtitle">Bonjour {client_nom},</div>
    <div class="alert">
      ⚠️ Votre facture <strong>{facture_num}</strong> est en retard de paiement
      de <strong>{nb_jours_retard} jour(s)</strong>.<br>
      Date d'échéance dépassée : <strong>{echeance}</strong>
    </div>
    <div class="card">
      <div class="card-row">
        <span class="card-label">Montant total TTC</span>
        <span class="card-value">{montant_ttc:,.2f} MAD</span>
      </div>
      <div class="card-row">
        <span class="card-label">Déjà réglé</span>
        <span class="card-value" style="color:#10B981">{montant_paye:,.2f} MAD</span>
      </div>
      <div class="card-row">
        <span class="card-label">Solde restant dû</span>
        <span class="card-value" style="color:#EF4444;font-weight:800">{solde:,.2f} MAD</span>
      </div>
    </div>
    <div class="amount" style="color:#EF4444;background:#FEF2F2">
      {solde:,.2f} MAD à régler
    </div>
    <p style="font-size:13px;color:#64748B">
      Merci de procéder au règlement dans les meilleurs délais.<br>
      En cas de difficulté, contactez-nous au <strong>+212 688 540 102</strong>.<br><br>
      <strong>RIB :</strong> 145 450 2121167962380017 92 BP
    </p>
    """
    return envoyer_email(
        destinataire=client_email,
        sujet=f"RAPPEL — Wassime BTP — Facture {facture_num} en attente",
        corps_html=_template_base(contenu, f"Relance {facture_num}"),
    )


def email_attestation_retard(client_nom: str, client_email: str,
                              att_num: str, facture_num: str,
                              capital: float, interets: float,
                              total: float, pdf_bytes: bytes) -> tuple:
    """Email avec attestation de retard."""
    contenu = f"""
    <div class="title">Attestation de Retard {att_num}</div>
    <div class="subtitle">Bonjour {client_nom},</div>
    <div class="alert">
      📋 Suite au retard de paiement constaté sur la facture
      <strong>{facture_num}</strong>, nous vous adressons ci-joint
      l'attestation de retard officielle.
    </div>
    <div class="card">
      <div class="card-row">
        <span class="card-label">Capital dû</span>
        <span class="card-value">{capital:,.2f} MAD</span>
      </div>
      <div class="card-row">
        <span class="card-label">Intérêts de retard</span>
        <span class="card-value" style="color:#EF4444">{interets:,.2f} MAD</span>
      </div>
      <div class="card-row">
        <span class="card-label">Total dû</span>
        <span class="card-value" style="color:#EF4444;font-weight:800">
          {total:,.2f} MAD
        </span>
      </div>
    </div>
    <div class="amount" style="color:#EF4444;background:#FEF2F2">
      Total : {total:,.2f} MAD
    </div>
    <p style="font-size:13px;color:#64748B">
      📎 L'attestation officielle est jointe en PDF.<br>
      Merci de régulariser votre situation rapidement.
    </p>
    """
    return envoyer_email(
        destinataire=client_email,
        sujet=f"Wassime BTP — Attestation de Retard {att_num}",
        corps_html=_template_base(contenu, f"Attestation {att_num}"),
        pdf_bytes=pdf_bytes,
        nom_pdf=f"Attestation_{att_num}_WassimeBTP.pdf"
    )


def email_confirmation_paiement(client_nom: str, client_email: str,
                                 facture_num: str, montant_recu: float,
                                 solde_restant: float) -> tuple:
    """Email de confirmation de réception de paiement."""
    solde_msg = (
        f"✅ Votre compte est soldé. Merci !"
        if solde_restant == 0
        else f"Solde restant : <strong>{solde_restant:,.2f} MAD</strong>"
    )
    contenu = f"""
    <div class="title">Confirmation de Paiement</div>
    <div class="subtitle">Bonjour {client_nom},</div>
    <div class="success">
      ✅ Nous avons bien reçu votre paiement de
      <strong>{montant_recu:,.2f} MAD</strong>
      concernant la facture <strong>{facture_num}</strong>.
    </div>
    <div class="card">
      <div class="card-row">
        <span class="card-label">N° Facture</span>
        <span class="card-value">{facture_num}</span>
      </div>
      <div class="card-row">
        <span class="card-label">Montant reçu</span>
        <span class="card-value" style="color:#10B981">
          {montant_recu:,.2f} MAD
        </span>
      </div>
      <div class="card-row">
        <span class="card-label">Date de réception</span>
        <span class="card-value">{date.today().strftime('%d/%m/%Y')}</span>
      </div>
    </div>
    <p style="font-size:13px;color:#64748B">{solde_msg}</p>
    <p style="font-size:13px;color:#64748B">
      Merci pour votre confiance. Nous restons à votre disposition.
    </p>
    """
    return envoyer_email(
        destinataire=client_email,
        sujet=f"Wassime BTP — Paiement reçu — Facture {facture_num}",
        corps_html=_template_base(contenu, "Confirmation Paiement"),
    )