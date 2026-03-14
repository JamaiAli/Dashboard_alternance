# Dashboard Alternance — NEXUS

> **Système de suivi de candidatures** — Interface de gestion centralisée pour l'organisation et l'analyse de vos candidatures en alternance ou stage.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![React](https://img.shields.io/badge/React-19-blue?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)

---

## Description

**NEXUS** est une solution logicielle conçue pour optimiser le processus de recherche d'alternance ou de stage. L'outil permet de centraliser l'ensemble des démarches et d'en visualiser l'avancement via une interface moderne et fonctionnelle.

Principales fonctionnalités :
- **Tableau Kanban** : Gestion visuelle des candidatures avec support du glisser-déposer (SOUHAITS → POSTULÉ → RELANCE → ENTRETIEN → TEST TECHNIQUE → OFFRE / REFUSÉ).
- **Analyse de Performance** : Indicateurs clés et statistiques de réussite en temps réel.
- **Gestion Documentaire** : Centralisation des CV et lettres de motivation associés à chaque dossier.
- **Suivi des Échanges** : Module de notes pour l'historique des interactions avec les recruteurs.
- **Automatisation** : Importation de fiches de poste via URL avec extraction automatique des données.
- **Recherche Avancée** : Filtrage multicritère par entreprise ou stack technologique.

---

## Architecture Technique

| Composant | Technologie |
|---|---|
| **Interface Utilisateur** | React 19, TypeScript, Vite, Tailwind CSS 4, dnd-kit |
| **API Backend** | Python 3.11+, FastAPI, SQLAlchemy (Asynchrone), Alembic, Pydantic |
| **Base de Données** | PostgreSQL 15 |
| **Services** | BeautifulSoup4, Requests (Collecte de données) |
| **Conteneurisation** | Docker Compose |

---

## Structure du Projet

```
Dashboard_alternance/
├── backend/                    # Serveur API FastAPI
│   ├── app/
│   │   ├── core/               # Configuration et variables d'environnement
│   │   ├── models/             # Modèles de données SQLAlchemy
│   │   ├── routers/            # Contrôleurs API
│   │   ├── schemas/            # Modèles de validation Pydantic
│   │   ├── services/           # Services métier et scraping
│   │   ├── database.py         # Gestion de la session de base de données
│   │   └── main.py             # Point d'entrée de l'application
│   ├── alembic/                # Scripts de migration
│   └── uploads/                # Stockage des documents
├── frontend/                   # Client React
│   ├── src/
│   │   ├── components/         # Composants d'interface (Kanban, Modales, etc.)
│   │   ├── App.tsx             # Composant racine
│   │   ├── types.ts            # Définitions de types globaux
│   │   └── main.tsx            # Initialisation React
├── docker-compose.yml          # Infrastructure Docker
└── README.md                   # Documentation projet
```

---

## Installation et Déploiement

### Prérequis
- Docker Desktop
- Python 3.11+
- Node.js 18+
- Client Git

### 1. Clonage du dépôt
```bash
git clone https://github.com/JamaiAli/Dashboard_alternance.git
cd Dashboard_alternance
```

### 2. Initialisation de la base de données
```bash
docker-compose up -d
```

### 3. Configuration du Backend
```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Unix/macOS
# source venv/bin/activate

pip install -r requirements.txt # Ou installation manuelle des dépendances listées dans le code
cd backend
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 4. Configuration du Frontend
Dans un terminal distinct :
```bash
cd frontend
npm install
npm run dev
```

L'application est accessible à l'adresse suivante : **http://localhost:5173**

---

## Utilisation

### Interface Utilisateur
- **Création** : Utilisation du bouton `+ AJOUTER_CANDIDATURE` pour une entrée manuelle.
- **Importation** : Utilisation de `> IMPORTER_VIA_URL` pour l'extraction automatique.
- **Gestion** : Suivi des étapes par déplacement des cartes dans le tableau Kanban.
- **Documents** : Gestion des pièces jointes directement sur le détail de la candidature.

### Documentation API
Le backend génère automatiquement une documentation interactive (Swagger UI) accessible sur : **http://localhost:8000/docs**

---

## Configuration

Le fichier `backend/.env` gère la connexion à la base de données :
```env
DATABASE_URL=postgresql+asyncpg://crm_user:crm_password@localhost:5432/crm_db
```

---

## Maintenance et Dépannage

- **Docker** : Assurez-vous que le service Docker est opérationnel en cas d'erreur de base de données.
- **Ports** : Si le port 8000 (Backend) ou 5173 (Frontend) est déjà utilisé, les services proposeront ou nécessiteront un changement de port.
- **Dépendances** : En cas d'erreur d'exécution, renouvelez l'installation des dépendances (`pip install` ou `npm install`).

---

## Licence

Ce projet est développé à des fins professionnelles dans le cadre de la recherche d'opportunités en alternance.

---

<p align="center">
  <b>NEXUS</b> — Solution optimisée pour le suivi de carrière
</p>
