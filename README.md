<div align="center">

# HomeMatch

**AI-powered real estate search platform**

</div>

HomeMatch is a real estate platform built with Django REST Framework and a static HTML/CSS/JavaScript frontend. The system supports property listing, authentication, favorites, reviews, image upload and AI-assisted visual analysis of property photos.

The project currently includes a working backend API, asynchronous image analysis with Celery, local or Cloudflare R2 image storage, and a frontend prepared to integrate with a backend natural-language search module.

---

## Features

- JWT authentication with register, login, logout and token refresh.
- User profile page.
- Property listing and detail pages.
- Property CRUD through the REST API.
- Objective property filters by city, neighborhood, price, area, rooms, condominium features, type and purpose.
- Property photo upload.
- Local media storage for development.
- Cloudflare R2 support for remote image storage.
- AI photo analysis using a vision model.
- Per-photo subjective visual attributes.
- Aggregated per-property subjective visual attributes.
- User favorites.
- Reviews with ratings and comments.
- Average rating per property.
- Static frontend integrated with the API.
- Frontend prepared for backend-owned natural-language search.

---

## Architecture

```txt
HomeMatch/
├── apps/
│   ├── users/          # Authentication, profile, favorites
│   ├── properties/     # Properties, photos, filters, reviews
│   ├── ai_analysis/    # Vision model integration and visual attributes
│   └── search/         # Natural-language search integration point
├── config/             # Django settings and root URLs
├── frontend/           # Static HTML/CSS/JS frontend
├── docs/
├── tools/
├── docker-compose.yaml
├── Dockerfile
└── requirements.txt
```

### Photo analysis flow

```txt
Property photo is uploaded
    -> image is saved locally or in Cloudflare R2
    -> Celery task analyzes the photo with a vision model
    -> PhotoSubjectiveAttribute records are saved
    -> PropertySubjectiveAttribute aggregates are updated
    -> frontend displays the visual analysis on the details page
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 + Django 5.2 |
| API | Django REST Framework |
| Authentication | JWT / Simple JWT |
| Database | PostgreSQL |
| Async tasks | Celery |
| Broker | Redis |
| Storage | Local media or Cloudflare R2 |
| AI | Gemini SDK for local files; OpenAI-compatible client for remote URLs |
| Frontend | Static HTML, CSS and JavaScript modules |
| Containers | Docker + Docker Compose |

---

## Frontend

The frontend is a static multi-page application. It does not require React, Vite or npm.

Expected structure:

```txt
frontend/
├── index.html
├── imoveis.html
├── detalhes.html
├── login.html
├── cadastro.html
├── perfil.html
├── styles.css
└── assets/
    ├── api.js
    └── homematch-logo.jpeg
```

Run it locally with:

```bash
python -m http.server 5500 -d frontend
```

Then open:

```txt
http://localhost:5500
```

The frontend expects the backend at:

```txt
http://localhost:8000
```

Image URLs returned as `/media/...` must be resolved against the backend base URL.

---

## Search

The frontend is prepared to call this backend-owned natural-language search endpoint:

```txt
GET /api/search/properties/?q=<query>&city=<city>&type=<type>&property_purpose=<purpose>
```

The frontend does not interpret natural language and does not rank semantic results. It only sends the query and objective filters, then renders the properties in the order returned by the backend.

---

## AI Analysis

The AI module stores subjective attributes at two levels:

```txt
PhotoSubjectiveAttribute
PropertySubjectiveAttribute
```

Examples of visual attributes:

```txt
aesthetics.color.brightness
aesthetics.color.visual_warmth
current_state.ventilation
current_state.cleanliness
current_state.structural_integrity
livability.coziness
livability.spaciousness
livability.verdancy
aesthetics.architecture.contemporary
aesthetics.architecture.minimalist
```

For local development, use:

```env
USE_LOCAL_STORAGE=True
AI_MODEL=gemini-2.5-flash
```

The configured model must support `generateContent` and image input.

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/users/register/` | Register user |
| `POST` | `/api/users/login/` | Login and return JWT tokens |
| `POST` | `/api/users/token/refresh/` | Refresh access token |
| `POST` | `/api/users/logout/` | Logout / blacklist refresh token |

### Users

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/users/me/` | Get current user |
| `PATCH` | `/api/users/me/` | Update current user |
| `GET` | `/api/users/favorites/` | List favorites |
| `POST` | `/api/users/favorites/` | Add favorite |
| `DELETE` | `/api/users/favorites/` | Remove favorite |

### Properties

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/properties/` | List properties with filters |
| `POST` | `/api/properties/` | Create property |
| `GET` | `/api/properties/{id}/` | Property details |
| `PATCH` | `/api/properties/{id}/` | Update property |
| `DELETE` | `/api/properties/{id}/` | Delete property |

### Photos

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/properties/{id}/photos/` | Upload property photo |
| `DELETE` | `/api/properties/photos/{id}/` | Delete property photo |

### Reviews

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/properties/{id}/reviews/` | List reviews |
| `POST` | `/api/properties/{id}/reviews/` | Create review |
| `PATCH` | `/api/properties/{id}/reviews/{review_id}/` | Edit review |
| `DELETE` | `/api/properties/{id}/reviews/{review_id}/` | Delete review |

### Search

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/search/properties/` | Natural-language property search |

---

## Filters

Supported objective filters for `/api/properties/` and expected for `/api/search/properties/`:

```txt
?min_price=1000&max_price=5000
?min_area=50&max_area=150
?city=Natal
?neighborhood=Ponta+Negra
?bedrooms=2
?bathrooms=1
?parking_spots=1
?type=A
?property_purpose=R
?condo_gym=true
?condo_pool=true
?living_room=true
?garden=true
```

---

## Getting Started

### 1. Clone

```bash
git clone https://github.com/lucasanselmocc/HomeMatch.git
cd HomeMatch
```

### 2. Configure environment

```bash
cp .env.example .env
```

Example local `.env`:

```env
SECRET_KEY=local-dev-secret
DEBUG=True

DB_NAME=homematch_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

USE_LOCAL_STORAGE=True

R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_ACCOUNT_ID=

AI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
AI_API_KEY=your-google-ai-studio-key
AI_MODEL=gemini-2.5-flash

GOOGLE_PLACES_API_KEY=dummy-key-for-local-dev
```

### 3. Start backend

```bash
docker compose up --build -d
```

### 4. Run migrations

```bash
docker compose exec web python manage.py migrate
```

### 5. Create admin user

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Start frontend

```bash
python -m http.server 5500 -d frontend
```

### 7. Access

```txt
Frontend:     http://localhost:5500
API:          http://localhost:8000
Django Admin: http://localhost:8000/admin
```

---

## Useful Commands

View logs:

```bash
docker compose logs -f web celery_worker
```

Check AI settings:

```bash
docker compose exec web python manage.py shell -c "
from django.conf import settings
print('USE_LOCAL_STORAGE =', settings.USE_LOCAL_STORAGE)
print('AI_MODEL =', settings.AI_MODEL)
print('AI_API_KEY set =', bool(settings.AI_API_KEY))
"
```

List available Gemini models:

```bash
docker compose exec web python manage.py shell -c "
import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.AI_API_KEY)

for model in genai.list_models():
    methods = getattr(model, 'supported_generation_methods', [])
    if 'generateContent' in methods:
        print(model.name)
"
```

Change admin password:

```bash
docker compose exec web python manage.py changepassword <admin-email-or-username>
```

Run reports:

```bash
pip install -r tools/requirements-dev.txt
./tools/run_reports.sh
```

---

## Team

| Name | GitHub |
|---|---|
| Kauã do Vale Ferreira | [@DevlTz](https://github.com/DevlTz) |
| Luisa Ferreira de Souza Santos | [@luisaferreirass](https://github.com/luisaferreirass) |
| Lucas Graziano dos Santos Anselmo | [@lucasanselmocc](https://github.com/lucasanselmocc) |

---

*Software Engineering course project @UFRN*
