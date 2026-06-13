# StringLab

> **An interactive web toolkit for the analysis of character sequences and string problems.**
> A Python-powered application that makes string algorithms *visible* — and traces their roots in computation theory.

StringLab is a full-stack web application built for the **Theory of Computation & Automata** course (Project 4). It implements **twelve classic string operations** across four categories and — crucially — does not just return an answer. It *replays the computation step by step*: animating a dynamic-programming matrix as it fills, sliding a search pattern beneath the text, and narrating every decision the algorithm makes.

The goal is to make the abstract machinery of computation theory concrete and observable, demonstrating genuine understanding of the underlying algorithms rather than reliance on library calls.

---

## Table of Contents

- [What StringLab Does](#what-stringlab-does)
- [Tech Stack](#tech-stack)
- [Architecture at a Glance](#architecture-at-a-glance)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Backend Setup (Docker)](#backend-setup-docker)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Configure environment variables](#2-configure-environment-variables)
  - [3. Start the backend stack](#3-start-the-backend-stack)
  - [4. Database migrations (Alembic)](#4-database-migrations-alembic)
  - [5. Inspect the database with Adminer](#5-inspect-the-database-with-adminer)
  - [6. Verify the API is running](#6-verify-the-api-is-running)
  - [Everyday Docker commands](#everyday-docker-commands)
- [Frontend Setup](#frontend-setup)
- [Running the Full App](#running-the-full-app)
- [Collaboration & Git Workflow](#collaboration--git-workflow)
- [Troubleshooting](#troubleshooting)

---

## What StringLab Does

Twelve operations, grouped into four categories, each with one of three **visualisation levels**:

| # | Operation | Category | Technique | Visualisation |
|---|---|---|---|---|
| 1 | Palindrome detection | Analysis & Properties | Two-pointer scan | Result |
| 2 | Character frequency | Analysis & Properties | Hash counting | Result |
| 3 | Longest palindromic substring | Analysis & Properties | Expand around centre | Step log |
| 4 | Find all occurrences | Search & Matching | Index scan | Result |
| 5 | Occurrence counter | Search & Matching | Linear pass | Result |
| 6 | **Knuth–Morris–Pratt search** | Search & Matching | Failure-function DFA | **Full animation** |
| 7 | Anagram detection | Comparison & Similarity | Frequency compare | Result |
| 8 | **Levenshtein edit distance** | Comparison & Similarity | Dynamic programming | **Full animation** |
| 9 | Longest common subsequence | Comparison & Similarity | Dynamic programming | Step log |
| 10 | Reversal & case transform | Transformation & Encoding | Linear rewrite | Result |
| 11 | Caesar cipher | Transformation & Encoding | Modular shift | Result |
| 12 | Run-length encode/decode | Transformation & Encoding | Symbol run grouping | Result |

The two **flagship** operations (KMP search and edit distance) ship with a full, frame-by-frame animation. The full data contract between backend and frontend lives in [`docs/StringLab_Technical_Contract.md`](docs/StringLab_Technical_Contract.md).

---

## Tech Stack

| Tier | Technology | Responsibility |
|---|---|---|
| **Presentation** | React 19 + TypeScript (Vite), Tailwind CSS | Interface, animation playback, client-side validation |
| **Application** | Python 3.12 + FastAPI | Algorithm execution, trace generation, REST API |
| **Data** | PostgreSQL 16 via SQLAlchemy (async) | Operations catalogue, examples, run history |
| **Migrations** | Alembic | Versioned database schema |
| **Tooling** | Docker & Docker Compose, Adminer | Reproducible dev environment, DB inspection |

---

## Architecture at a Glance

Three tiers, talking to each other over HTTP and a database connection:

```
┌─────────────────┐        HTTP/JSON        ┌──────────────────┐        SQL        ┌──────────────────┐
│   React (Vite)  │  ───────────────────▶   │  FastAPI backend │  ──────────────▶  │   PostgreSQL 16  │
│   localhost:5173│  ◀───────────────────   │  localhost:8000  │  ◀──────────────  │  (in Docker)     │
└─────────────────┘                         └──────────────────┘                   └──────────────────┘
                                                                                            ▲
                                                                                            │ inspect
                                                                                    ┌──────────────────┐
                                                                                    │     Adminer      │
                                                                                    │  localhost:8080  │
                                                                                    └──────────────────┘
```

The backend, database, and Adminer all run as **Docker containers** defined in [`docker-compose.dev.yml`](docker-compose.dev.yml). The frontend runs directly on your machine with Node.js during development.

---

## Project Structure

```
stringlab/
├── docker-compose.dev.yml      # Defines the backend, Postgres, and Adminer containers
├── docs/                       # Project report + the backend/frontend data contract
├── backend/
│   ├── Dockerfile              # Builds the FastAPI image
│   ├── entrypoint.sh           # Waits for DB → runs migrations → starts the server
│   ├── requirements.txt        # Python dependencies
│   ├── alembic.ini             # Alembic configuration
│   ├── alembic/                # Migration scripts live in alembic/versions/
│   └── app/
│       ├── main.py             # FastAPI app entry point
│       ├── core/config.py      # Settings (reads env vars)
│       ├── database/           # Async engine, session, declarative Base
│       └── modules/            # One folder per feature (catalogue, computation, runs, …)
└── frontend/                   # React + TypeScript + Vite single-page app
```

---

## Prerequisites

You only need **two** tools installed on your machine. Everything else (Python, PostgreSQL, all the libraries) runs *inside Docker*, so you do **not** need to install them yourself.

### 1. Docker Desktop (required)

Docker lets us run the backend, database, and DB viewer as isolated "containers" with one command — no manual Python or Postgres installation needed.

- **Download & install:** <https://www.docker.com/products/docker-desktop/>
- **Official docs / install guide:** <https://docs.docker.com/get-docker/>

After installing, **open Docker Desktop and wait until it says "Engine running"**, then confirm it works from a terminal:

```bash
docker --version
docker compose version
```

Both commands should print a version number. If `docker compose version` errors, you have an old Docker — update it (Compose v2 is required).

### 2. Node.js (required only for the frontend)

Node.js runs the React development server.

- **Download & install (LTS version):** <https://nodejs.org/>
- **Official docs:** <https://nodejs.org/en/learn/getting-started/how-to-install-nodejs>

Verify:

```bash
node --version    # should be v18 or newer
npm --version
```

### 3. Git (to clone the project)

- **Download & install:** <https://git-scm.com/downloads>

```bash
git --version
```

> 💡 **New to the terminal?** A "terminal" (or "command line") is the text window where you type the commands below. On Windows use **PowerShell** or the **Git Bash** that ships with Git; on macOS/Linux use **Terminal**. You type a command, press Enter, and wait for it to finish before typing the next one.

---

## Backend Setup (Docker)

This section gets the API and database running from scratch. Follow it top to bottom.

### 1. Clone the repository

```bash
git clone <repository-url> stringlab
cd stringlab
```

All commands below assume your terminal is **inside the `stringlab/` folder** (the one containing `docker-compose.dev.yml`).

### 2. Configure environment variables

The backend container reads its settings from `backend/.env.development`. A template is provided at [`backend/.env.example`](backend/.env.example). Copy it:

```bash
cp backend/.env.example backend/.env.development
```

Open `backend/.env.development` and confirm it contains the following. These values **must match** the database credentials in `docker-compose.dev.yml`, so leave them as-is unless you change both files together:

```ini
DATABASE_URL=postgresql+asyncpg://stringlab_user:stringlabpass6789.@stringlab-db:5432/stringlab_db
ENV=development
DB_HOST=stringlab-db
DB_PORT=5432
POSTGRES_USER=stringlab_user
POSTGRES_PASSWORD=stringlabpass6789.
WORKERS=1
```

> 🔎 **Why `stringlab-db` and not `localhost`?** Inside the Docker network, containers find each other by their **service name**, not `localhost`. `stringlab-db` is the name of the Postgres container, so the backend connects to it by that name.

### 3. Start the backend stack

This single command builds the backend image and starts **all three** containers — FastAPI, PostgreSQL, and Adminer:

```bash
docker compose -f docker-compose.dev.yml up --build
```

What happens, in order (you'll see it scroll past in the logs):

1. Docker builds the Python image and starts PostgreSQL.
2. The backend's [`entrypoint.sh`](backend/entrypoint.sh) **waits for Postgres** to be ready (`⏳ Waiting for Postgres...`).
3. It then **runs `alembic upgrade head`** automatically to apply all database migrations (`🧬 Running Alembic migrations...`).
4. Finally it starts the FastAPI server with auto-reload (`🛠 Running in development mode`).

When you see Uvicorn report `Application startup complete`, the API is live.

- To run it in the background instead, add `-d`: `docker compose -f docker-compose.dev.yml up --build -d`
- To stop it: press `Ctrl+C` (or `docker compose -f docker-compose.dev.yml down` if running detached).

### 4. Database migrations (Alembic)

**Alembic** is the tool that creates and updates database tables in versioned, repeatable steps (think "Git for your database schema"). Migration files live in [`backend/alembic/versions/`](backend/alembic/) and are **committed to Git**.

**How migrations flow through the project:**

- You **generate** migration files **locally**, on your own machine, against a local Postgres.
- You **commit** those files. The `Dockerfile` copies them into the image.
- On container startup, [`entrypoint.sh`](backend/entrypoint.sh) runs `alembic upgrade head` automatically, applying those same committed files to the container's database.

So the container **never generates** migrations — it only **applies** the ones you committed. That keeps your local database and the Docker database in perfect sync, because they replay the exact same migration files. **You only run the steps below when you add or change a SQLAlchemy model.**

#### Step-by-step: generating a migration locally

**1. Create your local environment file.** Copy the example and confirm it points at `localhost` (not the container hostname), since you'll run Alembic from your own machine:

```bash
cp backend/.env.example backend/.env.local
```

`backend/.env.local` should contain (note `localhost`):

```ini
DATABASE_URL=postgresql+asyncpg://stringlab_user:stringlabpass6789.@localhost:5432/stringlab_db
ENV=development
DB_HOST=localhost
DB_PORT=5432
POSTGRES_USER=stringlab_user
POSTGRES_PASSWORD=stringlabpass6789.
```

> The local app reads `backend/.env.local`; the Docker container reads `backend/.env.development`. Same credentials, different host (`localhost` vs `stringlab-db`).

**2. Start a local Postgres with the *same* credentials.** Using identical credentials to the container means zero connection-string juggling. The simplest way is a throwaway Postgres container published on `localhost:5432`:

```bash
docker run --name stringlab-local-db \
  -e POSTGRES_USER=stringlab_user \
  -e POSTGRES_PASSWORD=stringlabpass6789. \
  -e POSTGRES_DB=stringlab_db \
  -p 5432:5432 \
  -d postgres:16
```

(Already have a Postgres on `localhost:5432` with those credentials? Skip this.) Stop/remove it later with `docker stop stringlab-local-db && docker rm stringlab-local-db`.

**3. Set up the Python virtual environment** (first time only), then start the backend locally to confirm the models import and the database connects:

```bash
cd backend

python3 -m venv env                 # create the virtual environment
source env/bin/activate             # activate it (Windows: env\Scripts\activate)
pip install -r requirements.txt     # install dependencies

# Start the server — it will connect to your local Postgres and confirm startup
uvicorn app.main:app --reload
```

If you see `Database connection OK` and `Application startup complete`, you're wired up correctly. Leave this running (or stop it with `Ctrl+C` — the next step doesn't need it).

**4. Generate and apply the migration.** In the `backend/` folder, with the virtual environment activated:

```bash
# Generate a new migration — autogenerate diffs your models against the local DB
alembic revision --autogenerate -m "describe your change here"

# Apply it to your local database
alembic upgrade head
```

> ⚠️ Any new model must be **imported in [`backend/app/database/base.py`](backend/app/database/base.py)** so Alembic can "see" it. If autogenerate produces an empty migration, this import is usually what's missing.

**5. Review and commit** the generated file in `backend/alembic/versions/`. Autogenerate is a helpful draft, not gospel — read it before committing. Once pushed, every teammate's container picks it up and applies it automatically on the next `up`.

#### Useful inspection commands

Run these locally (virtual environment activated, from `backend/`):

```bash
alembic current      # show the current applied revision
alembic history      # show the full migration history
alembic downgrade -1 # roll back the most recent migration
```

#### Why this local-first approach?

Generating migrations **inside** the container would write the new file into the container's filesystem, where it's awkward to get back out and easy to lose. By generating locally and committing the file, the migration becomes the **single source of truth**: your local database and every container apply the identical committed files, so the schema can never drift between local development and the Dockerised backend.

#### Resetting after a migration history rewrite

Alembic tracks which revision a database is on in an `alembic_version` table. Normally you only ever *add* migrations, so this never matters. But occasionally — early in the project — a migration is **rewritten or replaced** (for example, squashing several migrations into a fresh initial one, or a sweeping schema change like switching all IDs to UUIDs). When that happens, a database still pointing at a now-deleted revision can no longer upgrade cleanly: Alembic looks for a revision file that isn't there.

Because the database lives in a Docker **volume** (`stringlab_pg_data`) that survives a normal `down`, you must wipe that volume to start from a clean slate:

```bash
docker compose -f docker-compose.dev.yml down -v      # ⚠️ deletes all DB data
docker compose -f docker-compose.dev.yml up --build    # re-migrates + re-seeds from scratch
```

The same applies to your **local** Postgres (the one you generate migrations against): drop and recreate the database, or `alembic downgrade base` before re-applying, so it isn't stranded on a missing revision.

> ⚠️ `down -v` is destructive — it erases every run in the history table. That is fine in development (the catalogue re-seeds automatically and runs are disposable), but **never** do this against data you want to keep.

### 5. Inspect the database with Adminer

**Adminer** is a lightweight web UI for browsing the database — viewing tables, running SQL, and checking that your data seeded correctly. It's already running as part of the stack.

1. Open your browser to **<http://localhost:8080>**
2. Fill in the login form with these credentials:

| Field | Value |
|---|---|
| **System** | `PostgreSQL` |
| **Server** | `stringlab-db` |
| **Username** | `stringlab_user` |
| **Password** | `stringlabpass6789.` |
| **Database** | `stringlab_db` |

3. Click **Login**. You can now browse the `categories`, `operations`, `examples`, and `runs` tables.

> 🔎 Use `stringlab-db` (the container name) as the **Server**, *not* `localhost` — Adminer runs inside the same Docker network as Postgres and reaches it by service name.

> 🗄️ **Two databases, don't mix them up.** This Adminer (the one in the Docker stack) talks to the **container database** via Server `stringlab-db`. The **local Postgres** you started for generating migrations (step 4) is a *separate* database, reachable from your machine at **`localhost:5432`** with the same credentials — connect to it with a local client (`psql`, a DB GUI, or your own Adminer pointed at `localhost`). They share credentials but hold independent data.

### 6. Verify the API is running

With the stack up, check these URLs:

| URL | What it is |
|---|---|
| <http://localhost:8000/> | Welcome message |
| <http://localhost:8000/health> | Health check (`{"status": "healthy"}`) |
| <http://localhost:8000/docs> | **Interactive API documentation** (Swagger UI) — explore and test every endpoint |
| <http://localhost:8000/redoc> | Alternative API documentation |

### Everyday Docker commands

```bash
# Start everything (rebuild if you changed dependencies or the Dockerfile)
docker compose -f docker-compose.dev.yml up --build

# Start in the background
docker compose -f docker-compose.dev.yml up -d

# Watch the backend logs
docker compose -f docker-compose.dev.yml logs -f backend

# Open a shell inside the backend container
docker compose -f docker-compose.dev.yml exec backend sh

# Stop the containers (keeps the database data)
docker compose -f docker-compose.dev.yml down

# Stop AND wipe the database (fresh start — you'll lose all data)
docker compose -f docker-compose.dev.yml down -v
```

> 💾 The database data is stored in a Docker **volume** (`stringlab_pg_data`), so it survives `down` and restarts. Only `down -v` deletes it.

---

## Frontend Setup

The frontend is a React + TypeScript app powered by Vite. It runs directly on your machine (not in Docker) for fast hot-reloading during development.

```bash
# From the project root, move into the frontend folder
cd frontend

# Install the JavaScript dependencies (only needed the first time, or when they change)
npm install

# Start the development server
npm run dev
```

Vite will print a local URL — by default **<http://localhost:5173>**. Open it in your browser. The page hot-reloads automatically as you edit files.

Other frontend scripts:

```bash
npm run build     # Type-check and build a production bundle into dist/
npm run preview   # Preview the production build locally
npm run lint      # Run ESLint
```

---

## Running the Full App

To work on the complete application, you need **both** halves running at once, in **two separate terminals**:

**Terminal 1 — backend (API + database + Adminer):**

```bash
cd stringlab
docker compose -f docker-compose.dev.yml up --build
```

**Terminal 2 — frontend (React dev server):**

```bash
cd stringlab/frontend
npm run dev
```

Then open the frontend at **<http://localhost:5173>**. It talks to the backend API at `http://localhost:8000`.

| Service | URL |
|---|---|
| Frontend (React) | <http://localhost:5173> |
| Backend API | <http://localhost:8000> |
| API docs (Swagger) | <http://localhost:8000/docs> |
| Adminer (DB UI) | <http://localhost:8080> |

---

## Collaboration & Git Workflow

We work as a team on a shared repository, so a few simple rules keep everyone's work safe and avoid painful merge conflicts. Please read this before pushing anything.

### Branches

| Branch | Purpose | Push directly? |
|---|---|---|
| `main` | **Stable, demo-ready code only.** This is what we present. | ❌ **Never** — protected |
| `dev`  | **Integration branch.** Everyone's day-to-day work lands here. | ✅ Yes (after pulling) |

> ⚠️ **Never push directly to `main`.** Code reaches `main` only by merging `dev` into it once a milestone is stable. If `main` breaks, the demo breaks.

### The golden rule: always pull before you write or push

Before starting new work **and** before pushing, sync with the remote so you build on everyone else's latest changes:

```bash
git checkout dev
git pull origin dev      # get the latest before you start coding
```

When you're ready to share your work:

```bash
git pull origin dev      # pull AGAIN in case teammates pushed while you worked
git add .
git commit -m "clear message describing what you changed"
git push origin dev
```

> 💡 Pulling before pushing means Git merges others' changes into yours *locally* (where you can fix conflicts calmly), instead of rejecting your push.

### Feature branches (optional)

The app is small, so working directly on `dev` is fine for quick changes. For anything larger — or if two people touch the same area — branch off `dev` so your work stays isolated until it's ready:

```bash
git checkout dev
git pull origin dev
git checkout -b feat/kmp-animation     # create your feature branch
# ... write code, commit as you go ...
git push origin feat/kmp-animation
```

Then open a **Pull Request** on GitHub targeting `dev` (not `main`) so a teammate can glance at it before it merges.

**Branch naming convention:**

| Prefix | Use for | Example |
|---|---|---|
| `feat/` | A new feature | `feat/edit-distance-trace` |
| `fix/`  | A bug fix | `fix/cors-credentials` |
| `chore/`| Tooling, config, docs | `chore/update-readme` |

### Commit messages

Write short, present-tense messages that say *what changed and why*:

- ✅ `add KMP failure-table computation` / `fix Adminer server hostname in README`
- ❌ `stuff` / `update` / `asdf`

### Quick checklist before every push

1. `git pull origin dev` — am I up to date?
2. Does the backend still start? (`docker compose -f docker-compose.dev.yml up`)
3. Are my commit messages clear?
4. Am I pushing to `dev` (or a `feat/` branch), **never** `main`?

---

## Troubleshooting

| Symptom | Likely cause & fix |
|---|---|
| `docker: command not found` | Docker isn't installed or Docker Desktop isn't running. Open Docker Desktop and wait for "Engine running". |
| Backend logs stuck on `⏳ Waiting for Postgres...` | The database is still starting — give it a few seconds. If it never connects, run `down -v` and `up --build` for a clean start. |
| `port is already allocated` (8000, 8080, 5173, or 5432) | Another program is using that port. Stop it, or change the port mapping in `docker-compose.dev.yml`. |
| Adminer says "connection refused" | Make sure **Server** is `stringlab-db`, not `localhost`, and that the Postgres container is running. |
| Alembic autogenerate creates an empty migration | Your new model isn't imported in [`backend/app/database/base.py`](backend/app/database/base.py). Import it, then regenerate. |
| Code changes to the backend aren't picked up | Dev mode uses `--reload`; if a change is ignored, restart the backend container. Changes to `requirements.txt` or the `Dockerfile` require `up --build`. |
| `npm run dev` fails with module errors | Run `npm install` again inside `frontend/`. Delete `node_modules` and reinstall if it persists. |

---

*Built for the Theory of Computation & Automata course — Project 4. See [`docs/`](docs/) for the full project report and technical contract.*
