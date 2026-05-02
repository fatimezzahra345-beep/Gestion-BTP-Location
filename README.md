# 🏗️ LocationBTP — Wassime BTP

Application de Gestion de Location d'Engins de Chantier  
**Architecture MVC | Streamlit | SQLAlchemy | ReportLab**

---

## 📁 Structure du Projet

```
locationbtp/
├── app.py              # Point d'entrée — navigation Streamlit
├── models.py           # Couche Modèle — SQLAlchemy (ORM)
├── controller.py       # Couche Contrôleur — logique métier
├── views.py            # Couche Vue — interface Streamlit
├── pdf_generator.py    # Génération PDF (devis + factures)
├── requirements.txt    # Dépendances Python
├── uploads/            # Photos des engins (créé automatiquement)
└── locationbtp.db      # Base SQLite (créée automatiquement)
```

---

## 🚀 Installation et Lancement

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Lancer l'application
```bash
streamlit run app.py
```

### 3. Ouvrir dans le navigateur
```
http://localhost:8501
```

---

## 🎯 Fonctionnalités

### 🏠 Tableau de Bord
- Chiffre d'affaires total et mensuel
- Graphique CA par mois (6 derniers mois)
- Répartition du parc d'engins (camembert)
- Alertes créances et factures en retard

### 🚛 Parc d'Engins
- Catalogue complet avec tarifs pré-configurés (depuis le Devis N°05/2026)
- Upload photo par engin
- Changement de statut (disponible / loué / maintenance)
- Ajout / suppression d'engins

### 👥 Clients
- Base de données clients avec ICE, téléphone, email
- Historique des locations par client

### 📝 Devis
- Formulaire de création avec sélection multi-engins
- Calcul automatique HT / TVA 20% / TTC
- Génération PDF professionnel (format Wassime BTP)
- Validation → convertit en location active
- Annulation → libère les engins

### 💰 Facturation
- Création automatique depuis un devis validé
- Suivi des paiements (partiels ou complets)
- Détection automatique des retards
- Téléchargement PDF facture

### 📅 Calendrier
- Vue Gantt des locations actives
- Visualisation des conflits de disponibilité

### 📊 Rapports
- Répartition des devis par statut
- Répartition des paiements
- Top clients par CA

---

## 💰 Tarifs Pré-configurés (Devis N°05/2026)

| Engin | Prix / Jour (MAD) |
|-------|-------------------|
| Camion 8X4 | 1 700 |
| Niveleuse 12G | 2 000 |
| Compacteur 15T | 1 500 |
| Pelle Hydraulique (Chenille) | 2 000 |
| Pelle Hydraulique (Pneus) | 2 000 |
| Chargeuse Caterpillar | 1 500 |
| Chariot Élévateur Télescopique | 1 500 |
| Tractopelle | 900 |
| Camion Citerne | 900 |

---

## 🔧 Déploiement Web (Streamlit Cloud)

1. Pousser le code sur GitHub
2. Connecter sur [share.streamlit.io](https://share.streamlit.io)
3. Sélectionner `app.py` comme fichier principal
4. ⚠️ Pour la persistance en production, migrer vers PostgreSQL :
   ```python
   # Dans models.py, remplacer :
   engine = create_engine("sqlite:///locationbtp.db")
   # Par :
   engine = create_engine("postgresql://user:password@host/dbname")
   ```

---

## 📞 Contact Wassime BTP
- **ICE :** 003440371000093
- **Tél :** +212 688 540 102
- **Email :** STEWASSIMEBTP@GMAIL.COM
- **Adresse :** Marrakech, Maroc