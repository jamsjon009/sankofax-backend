# SankofaX — Backend API

Django 5 + Django REST Framework backend for the SankofaX Global Black & African Business Directory platform.

## Tech Stack

- **Python** 3.12
- **Django** 5.0.6 + **Django REST Framework** 3.15
- **PostgreSQL** (database, via `DATABASE_URL`)
- **JWT Auth** via djangorestframework-simplejwt
- **django-unfold** — modern admin dashboard
- **Stripe** — subscription payments
- **Gunicorn** + **WhiteNoise** — production serving

## Project Structure

```
sankofax-backend/
├── apps/
│   ├── accounts/       # Custom User model (email login, UUID PK, role/region), JWT, email verify, password reset
│   ├── profiles/       # UserProfile, CompanyProfile, IdentityBadge (ownership badges)
│   ├── directory/      # Listings, Categories, Amenities, listing images
│   ├── reviews/        # Reviews & owner replies
│   ├── subscriptions/  # Plans (Global North/South) + Stripe checkout/webhook/portal
│   ├── events/         # Community events
│   ├── marketplace/    # Products
│   ├── crm/            # Leads, support tickets, listing approval workflow
│   ├── newsletter/     # Subscribers + CSV export
│   ├── blog/           # Blog posts & categories
│   └── core/           # Site settings, pages, FAQs, testimonials, analytics, seed commands
├── config/
│   ├── settings/       # base.py, dev.py, prod.py
│   ├── urls.py
│   └── wsgi.py
├── templates/admin/    # Custom unfold dashboard
├── requirements.txt
├── Dockerfile
└── nginx.conf
```

## Quick Start (Local)

### Prerequisites
- Python 3.12+
- PostgreSQL running locally

### 1. Clone
```bash
git clone https://github.com/jamsjon009/sankofax-backend.git
cd sankofax-backend
```

### 2. Virtual environment
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

### 4. Environment variables
Create a `.env` file in the project root:
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

### 7. Load demo data
```bash
python manage.py seed_demo
```
Creates demo users, categories, amenities, companies, listings, subscription plans,
reviews, identity badges, blog posts, testimonials, pages, FAQs, events and newsletter
subscribers. Safe to re-run — existing rows are skipped.

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
| `http://localhost:8000/admin/` | Admin dashboard (django-unfold) |
| `http://localhost:8000/api/docs/` | Swagger API docs (interactive, always current) |
| `http://localhost:8000/api/schema/` | OpenAPI schema |

---

## Understanding the API (REST conventions)

The API is REST-style, so **the same URL can serve different actions depending on the
HTTP method** — this is normal and intended, not a duplicate route. For example:

| URL | `GET` | `POST` |
|-----|-------|--------|
| `/api/listings/` | List published listings | Create a new listing (auth) |
| `/api/companies/` | List your companies (auth) | Create a company (auth) |

And a single-item URL varies by method too:

| URL | `GET` | `PATCH` | `DELETE` |
|-----|-------|---------|----------|
| `/api/listings/{slug}/` | Get one listing | Update it (owner) | Delete it (owner) |

So when you see one endpoint listed for both "get" and "create", it is **one URL with two
methods** — the method (`GET` vs `POST`) decides what happens. The Swagger page at
`/api/docs/` lists every URL broken down by method, and is the authoritative reference.

All endpoints are served under the `/api/` prefix (there is **no** `/api/v1/`).

---

## API Overview

Representative endpoints (see `/api/docs/` for the complete, live list):

### Auth — `/api/auth/`
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Login — returns JWT `access` + `refresh` |
| POST | `/api/auth/refresh/` | Refresh the access token |
| POST | `/api/auth/logout/` | Blacklist the refresh token |
| GET | `/api/auth/me/` | Current user |
| POST | `/api/auth/verify-email/` · `resend-verification/` · `forgot-password/` · `reset-password/` | Email & password flows |

### Directory & reviews — `/api/`
| Method | Endpoint | Description |
|---|---|---|
| GET / POST | `/api/listings/` | List published listings / create one |
| GET | `/api/listings/?my=true` | The current owner's listings |
| GET / PATCH / DELETE | `/api/listings/{slug}/` | Retrieve / update / delete a listing |
| POST | `/api/listings/{id}/images/` | Upload a gallery image |
| GET / POST | `/api/listings/{slug}/reviews/` | List / create reviews |
| PATCH | `/api/reviews/{id}/reply/` | Owner replies to a review |
| GET | `/api/categories/` · `/api/categories/{slug}/` | Categories |
| GET | `/api/amenities/` | Amenities |

### Profiles & badges — `/api/`
| Method | Endpoint | Description |
|---|---|---|
| GET / PATCH | `/api/profile/` | Current user's profile |
| GET | `/api/badges/` | Ownership / identity badges |
| GET / POST | `/api/companies/` | List your companies / create one |
| GET / PATCH | `/api/companies/{slug}/` | Retrieve / update a company |

### Subscriptions — `/api/`
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/plans/` | Subscription plans (region-aware) |
| POST | `/api/subscriptions/checkout/` | Create a Stripe checkout session |
| POST | `/api/subscriptions/portal/` | Open the Stripe billing portal |
| POST | `/api/webhooks/stripe/` | Stripe webhook receiver |

### Content — `/api/`
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/events/` | Published events |
| GET | `/api/blog/` · `/api/blog/{slug}/` · `/api/blog/categories/` | Blog |
| GET | `/api/faqs/` · `/api/site-settings/` · `/api/pages/{slug}/` · `/api/testimonials/` | Site content |
| POST | `/api/contact/` · `/api/newsletter/subscribe/` | Contact form / newsletter |
| GET | `/api/admin/stats/` | Admin dashboard statistics (staff only) |

Full, always-current docs: `http://localhost:8000/api/docs/`

---

## Docker

A `Dockerfile` is provided for building the backend image. PostgreSQL is expected to run
separately (managed DB or a local instance); point `DATABASE_URL` at it.

```bash
docker build -t sankofax-backend .
docker run --env-file .env -p 8000:8000 sankofax-backend
```

---

## Production Deployment

### Environment
Set `DJANGO_SETTINGS_MODULE=config.settings.prod` and provide all env vars listed in Quick Start.

### Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
```

### Static files
```bash
python manage.py collectstatic --no-input
```

See `nginx.conf` for the Nginx reverse-proxy configuration.

---

## Branches

| Branch | Purpose |
|---|---|
| `main` | Source of truth / pull-request target |
| `development` | Active development branch |

Day-to-day work happens on `development`; changes are merged into `main` via pull request.

---

## Related

- **Frontend:** `sankofax-frontend` (Next.js) — consumes this API.
- **Roadmap / progress:** see `PROGRESS.md` for what's built and what's remaining.
