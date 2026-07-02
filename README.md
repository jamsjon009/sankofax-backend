# SankofaX — Backend API

Django 5 + Django REST Framework backend for the SankofaX Global Black & African Business Directory platform.

## Tech Stack

- **Python** 3.12
- **Django** 5.0.6 + **Django REST Framework** 3.15
- **PostgreSQL** 16 (database)
- **JWT Auth** via djangorestframework-simplejwt
- **django-unfold** — modern CRM admin dashboard
- **Stripe** — subscription payments
- **Gunicorn** + **WhiteNoise** — production serving

## Project Structure

```
backend/
├── apps/
│   ├── accounts/       # Custom User model (email login, UUID PK, role/region)
│   ├── profiles/       # UserProfile + CompanyProfile
│   ├── directory/      # Listings, Categories, Amenities
│   ├── reviews/        # Reviews & owner replies
│   ├── subscriptions/  # Plans + Stripe checkout/webhook/portal
│   ├── events/         # Community events
│   ├── marketplace/    # Products
│   ├── crm/            # Leads + Support tickets
│   ├── newsletter/     # Subscribers + CSV export
│   └── core/           # Admin dashboard, seed data
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   └── urls.py
├── templates/
│   └── admin/index.html  # Custom unfold dashboard
├── .env.example
├── requirements.txt
├── Dockerfile
└── nginx.conf
```

## Quick Start (Local)

### Prerequisites
- Python 3.12+
- PostgreSQL 16 running locally

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_ORG/sankofax-backend.git
cd sankofax-backend
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and fill in your values (at minimum `DATABASE_URL`):
```env
DEBUG=True
SECRET_KEY=your-secret-key-change-this
DATABASE_URL=postgres://postgres:postgres@localhost:5432/sankofax
CORS_ALLOWED_ORIGINS=http://localhost:3000
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
```

### 5. Create the database
```sql
-- In psql:
CREATE DATABASE sankofax;
```

### 6. Run migrations
```bash
python manage.py migrate
```

### 7. Load seed data (demo content)
```bash
python manage.py seed_data
```
This creates 10 categories, ~30 listings, 6 subscription plans, and sample users.

### 8. Create a superuser
```bash
python manage.py createsuperuser
```

### 9. Start the server
```bash
python manage.py runserver
```

| URL | Description |
|-----|-------------|
| `http://localhost:8000/admin/` | CRM Admin (django-unfold) |
| `http://localhost:8000/api/docs/` | Swagger API docs |
| `http://localhost:8000/api/v1/` | REST API root |

---

## API Overview

| Endpoint | Description |
|---|---|
| `POST /api/v1/auth/register/` | Register new user |
| `POST /api/v1/auth/token/` | Login — returns JWT |
| `POST /api/v1/auth/token/refresh/` | Refresh access token |
| `GET /api/v1/listings/` | List published listings |
| `GET /api/v1/listings/?my=true` | Owner's own listings |
| `GET /api/v1/categories/` | All categories |
| `GET /api/v1/plans/` | Subscription plans |
| `POST /api/v1/subscriptions/checkout/` | Create Stripe checkout session |
| `POST /api/v1/subscriptions/portal/` | Open Stripe billing portal |
| `GET /api/v1/events/` | Published events |
| `GET /api/v1/marketplace/` | Active products |

Full docs: `http://localhost:8000/api/docs/`

---

## Running with Docker

```bash
docker compose up --build
```

This starts PostgreSQL + Django together. Backend available at `http://localhost:8000`.

---

## Production Deployment

### Environment
Set `DJANGO_SETTINGS_MODULE=config.settings.prod` and fill all env vars from `.env.example`.

### Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
```

### Static files
```bash
python manage.py collectstatic --no-input
```

See `nginx.conf` for the Nginx reverse proxy configuration.

---

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Source of truth |
| `production` | Live release |
| `staging` | Pre-release QA |
| `development` | Integration branch |
| `backend` | Active development work |

Workflow: `backend` → `development` → `staging` → `production` → `main`
