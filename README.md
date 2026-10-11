# Campus Creatives

Campus Creatives is a server-rendered Django application by Decreaviator Campus Creative Agency. It helps campus creatives find collaborators, organize project work, and publish completed projects with team credit.

## What works

- Email/password registration, login, logout, and a custom email-based user model
- Creative profiles with an admin-managed campus, up to three skills, portfolio links, availability, optional photo and private-by-default WhatsApp details
- Creative directory and idea discovery filters
- Idea posting with Paid, Free collaboration, or Revenue share budgets
- Explainable matching based on requested-skill overlap, campus, and availability (up to ten results)
- Owner invitations and creative applications, with duplicate prevention and accept/decline flows
- Workspace activation after one accepted collaborator
- Private team workspace with a four-column Kanban board and page-refresh discussion
- Project completion, deliberate showcase publishing, team role credits, and optional media links/images
- One 1–5 rating per teammate per completed project, plus a clearly labelled average of submitted ratings
- Django Admin management for users, campuses, skills, profiles, ideas, invitations, projects, tasks, discussion, showcase entries, ratings, and reports

## Local setup

Python 3.12+ is recommended. The repository currently targets Django 6.0.

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py seed_catalog
py manage.py createsuperuser
py manage.py runserver
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_catalog
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Admin is at `http://127.0.0.1:8000/admin/`.

`seed_catalog` is optional and safe to run more than once. It adds an editable starter set of campuses and skills without replacing existing records. The owner can add, rename, deactivate, or remove choices in Django Admin.

## Development checks

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

SQLite is used by default at `db.sqlite3`. To prepare for PostgreSQL later, settings accept `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`; install a PostgreSQL driver before changing the engine.

Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, and `DJANGO_ALLOWED_HOSTS` before a non-local deployment. No credentials belong in the repository.

## Styling and uploaded files

Templates use Tailwind CSS through its browser CDN for this first release, plus a small static stylesheet for the shared visual system. An internet connection is needed for Tailwind utilities while developing. A later production deployment should compile and self-host Tailwind.

Profile and showcase images are optional, limited to 5 MB, validated as images, and stored under `media/` locally. Uploaded media and the SQLite database are intentionally ignored by Git.

## Intentionally deferred

- Google sign-in (no credentials are configured)
- Payments, wallets, escrow, and client hiring
- Real-time chat, WebSockets, and notifications
- Likes and public comments on showcase entries
- File sharing inside workspaces
- Growth Hub content, analytics dashboards, disputes, and AI-based matching

These are not represented by inactive buttons. The current project discussion uses ordinary Django forms and page refreshes.
