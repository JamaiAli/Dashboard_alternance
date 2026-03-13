# 🚀 Dashboard Alternance — STI_NEXUS

> **Dashboard de suivi de candidatures d'alternance** — Interface Kanban cyberpunk pour tracker, organiser et analyser vos candidatures.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![React](https://img.shields.io/badge/React-19-blue?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)

---

## 📖 Description

**STI_NEXUS** est un outil de suivi de candidatures d'alternance/stage conçu pour centraliser et visualiser l'avancement de vos démarches. Il se compose de :

- Un **tableau Kanban interactif** avec drag & drop pour déplacer vos candidatures entre les étapes (Wishlist → Applied → Interview → Technical Test → Offer / Rejected).
- Un **panneau d'analytics** affichant les statistiques en temps réel.
- Un **gestionnaire de documents** (CV, lettres de motivation) rattachés à chaque candidature.
- Un **système de notes** pour consigner les échanges et remarques.
- Un **import par URL** avec scraping automatique de la fiche de poste.
- Un **filtre de recherche** par nom d'entreprise ou technologie.

---

## 🛠️ Stack Technique

| Couche | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS 4, dnd-kit, Lucide Icons, Axios |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy (async), Alembic, Pydantic |
| **Base de données** | PostgreSQL 15 (via Docker) |
| **Scraping** | BeautifulSoup4, Requests |
| **Infrastructure** | Docker Compose |

---

## 📁 Organisation du Projet

```
Dashboard_alternance/
├── backend/                    # API REST FastAPI
│   ├── app/
│   │   ├── core/               # Configuration (settings, .env)
│   │   ├── models/             # Modèles SQLAlchemy
│   │   │   ├── application.py  # Modèle de candidature
│   │   │   ├── company.py      # Modèle d'entreprise
│   │   │   ├── document.py     # Modèle de document
│   │   │   └── note.py         # Modèle de note
│   │   ├── routers/            # Endpoints API
│   │   │   ├── applications.py # CRUD candidatures
│   │   │   ├── companies.py    # CRUD entreprises
│   │   │   ├── documents.py    # Upload / gestion documents
│   │   │   ├── notes.py        # CRUD notes
│   │   │   └── scraper.py      # Endpoint de scraping URL
│   │   ├── schemas/            # Schémas Pydantic (validation)
│   │   ├── services/           # Logique métier
│   │   │   └── scraping_service.py
│   │   ├── database.py         # Configuration async SQLAlchemy
│   │   └── main.py             # Point d'entrée FastAPI
│   ├── alembic/                # Migrations de base de données
│   ├── uploads/                # Stockage des fichiers uploadés
│   └── .env                    # Variables d'environnement
├── frontend/                   # Application React
│   ├── src/
│   │   ├── components/
│   │   │   ├── KanbanBoard/    # Tableau Kanban (colonnes + cartes)
│   │   │   ├── Analytics/      # Widget de statistiques
│   │   │   ├── Documents/      # Gestionnaire de documents
│   │   │   ├── Modals/         # Modales (ajout, import URL)
│   │   │   └── SearchFilter/   # Filtre par tech / entreprise
│   │   ├── App.tsx             # Composant principal
│   │   ├── types.ts            # Types TypeScript
│   │   └── main.tsx            # Point d'entrée React
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml          # Configuration Docker (PostgreSQL)
└── README.md
```

---

## 🏗️ Architecture

### Vue d'ensemble

```mermaid
graph TB
    subgraph Client["🖥️ Frontend — React / Vite"]
        A["App.tsx"] --> B["KanbanBoard"]
        A --> C["AnalyticsWidget"]
        A --> D["SearchFilter"]
        A --> E["AddApplicationModal"]
        A --> F["ImportUrlModal"]
        B --> G["KanbanColumn"]
        G --> H["ApplicationCard"]
        H --> I["DocumentManager"]
    end

    subgraph API["⚙️ Backend — FastAPI"]
        J["main.py"] --> K["/api/v1/applications"]
        J --> L["/api/v1/companies"]
        J --> M["/api/v1/documents"]
        J --> N["/api/v1/notes"]
        J --> O["/api/v1/scraper"]
        O --> P["ScrapingService"]
    end

    subgraph DB["🗄️ PostgreSQL"]
        Q["companies"]
        R["applications"]
        S["documents"]
        T["notes"]
    end

    Client -- "HTTP / REST (Axios)" --> API
    API -- "SQLAlchemy Async" --> DB
    R -- "FK company_id" --> Q
    S -- "FK application_id" --> R
    T -- "FK application_id" --> R
```

### Modèle de données

```mermaid
erDiagram
    COMPANY ||--o{ APPLICATION : "possède"
    APPLICATION ||--o{ DOCUMENT : "contient"
    APPLICATION ||--o{ NOTE : "contient"

    COMPANY {
        uuid id PK
        string name
        string sector
        string[] tech_stack
    }

    APPLICATION {
        uuid id PK
        uuid company_id FK
        datetime date_sent
        datetime last_contact_date
        enum status
        enum type
        float salary_proposed
        string job_url
        text raw_description
    }

    DOCUMENT {
        uuid id PK
        uuid application_id FK
        string filename
        string filepath
        datetime uploaded_at
    }

    NOTE {
        uuid id PK
        uuid application_id FK
        text content
        datetime created_at
    }
```

### Flux utilisateur

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant F as Frontend React
    participant B as Backend FastAPI
    participant D as PostgreSQL
    participant W as Web (URL)

    U->>F: Ouvre le dashboard
    F->>B: GET /api/v1/applications
    B->>D: SELECT applications + companies
    D-->>B: Données
    B-->>F: JSON applications
    F-->>U: Affiche le Kanban Board

    U->>F: Drag & Drop une carte
    F->>B: PUT /api/v1/applications/{id}
    B->>D: UPDATE status
    D-->>B: OK
    B-->>F: 200

    U->>F: Import via URL
    F->>B: POST /api/v1/scraper/extract
    B->>W: GET page web
    W-->>B: HTML
    B-->>F: Texte extrait
    F-->>U: Pré-remplit le formulaire
```

---

## 🚀 Installation et Lancement

### Prérequis

- **Docker Desktop** installé et démarré
- **Python 3.11+** avec `pip`
- **Node.js 18+** avec `npm`
- **Git**

### 1. Cloner le dépôt

```bash
git clone https://github.com/JamaiAli/Dashboard_alternance.git
cd Dashboard_alternance
```

### 2. Lancer la base de données

```bash
docker-compose up -d
```

Vérifier que PostgreSQL tourne :

```bash
docker ps
# Vous devez voir un conteneur postgres:15 actif sur le port 5432
```

### 3. Configurer et lancer le Backend

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (PowerShell Windows)
.\venv\Scripts\Activate.ps1

# Ou sur Linux/Mac
# source venv/bin/activate

# Installer les dépendances
pip install fastapi uvicorn sqlalchemy[asyncio] asyncpg alembic python-dotenv pydantic-settings requests beautifulsoup4 python-multipart aiofiles

# Lancer les migrations
cd backend
alembic upgrade head

# Démarrer le serveur
uvicorn app.main:app --reload --port 8000
```

Le backend est accessible sur **http://localhost:8000**.

### 4. Lancer le Frontend

Dans un **nouveau terminal** :

```bash
cd frontend
npm install
npm run dev
```

Le frontend est accessible sur **http://localhost:5173**.

---

## 🧪 Tester l'Application

### Interface Web

Ouvrez **http://localhost:5173** pour accéder au dashboard Kanban.

| Action | Comment |
|---|---|
| Ajouter une candidature | Cliquer sur `+ ADD_APPLICATION` |
| Importer via URL | Cliquer sur `> IMPORT_VIA_URL` |
| Déplacer une candidature | Drag & drop entre les colonnes |
| Ajouter une note | Cliquer sur une carte → section notes |
| Uploader un document | Cliquer sur une carte → section documents |
| Supprimer une candidature | Bouton supprimer sur la carte |
| Filtrer | Taper dans la barre de recherche |

### API Swagger

Accédez à **http://localhost:8000/docs** pour tester chaque endpoint REST directement via l'interface Swagger UI.

### Endpoints principaux

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/applications/` | Liste toutes les candidatures |
| `POST` | `/api/v1/applications/` | Crée une candidature |
| `PUT` | `/api/v1/applications/{id}` | Met à jour une candidature |
| `DELETE` | `/api/v1/applications/{id}` | Supprime une candidature |
| `GET` | `/api/v1/companies/` | Liste les entreprises |
| `POST` | `/api/v1/companies/` | Crée une entreprise |
| `POST` | `/api/v1/documents/upload` | Upload un document |
| `GET` | `/api/v1/notes/` | Liste les notes |
| `POST` | `/api/v1/scraper/extract` | Extrait le texte d'une URL |

---

## ⚙️ Variables d'Environnement

Le fichier `backend/.env` contient :

```env
DATABASE_URL=postgresql+asyncpg://crm_user:crm_password@localhost:5432/crm_db
```

Ces valeurs correspondent à la configuration du `docker-compose.yml`.

---

## 🐛 Résolution de Problèmes

| Problème | Solution |
|---|---|
| Docker Compose échoue | Vérifier que Docker Desktop est lancé |
| Erreur connexion BDD | Vérifier que le conteneur PostgreSQL tourne (`docker ps`) |
| Port 8000 occupé | Changer le port : `uvicorn app.main:app --reload --port 8001` |
| Port 5173 occupé | Vite choisira automatiquement un port libre |
| `npm run dev` échoue | Lancer `npm install` d'abord |
| Erreur d'import Python | Vérifier que le `venv` est activé |

---

## 📄 Licence

Projet développé dans le cadre d'une recherche d'alternance.

---

<p align="center">
  <b>STI_NEXUS</b> — Conçu avec ❤️ pour optimiser la recherche d'alternance
</p>
