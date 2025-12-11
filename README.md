# Flask Blog (Monolith)

Simple Flask blog that stores posts in SQLite, ships as a single container image, and can be run locally, via Docker, or on Kubernetes.

## Architecture

```
Browser
  |
  | HTTP
  v
NodePort service (port 30080) -> Kubernetes Service :80 -> targetPort 5000
  |
  v
Deployment (1 replica) -> Pod running image varadpoddar/flask_blog
  |
  v
Flask app (app.py + templates + static)
  |
  v
SQLite database file (/app/database.db)

CI/CD path:
GitHub repo -> GitHub Actions -> docker/build-push-action -> image varadpoddar/flask_blog:latest -> used by Deployment
```

## Services in this repo

- Monolith: `app.py` (kept for reference and legacy UI).
- `blog-api-service`: REST-only Flask app for posts CRUD (services/blog-api).
- `auth-service`: REST Flask app for signup/login/JWT auth (services/auth).

## Microservice architecture (after, Assignment 2)

The monolith bundled blog logic, templates, and (in a fuller version) auth into one Flask app. Splitting helps with independent scaling, clearer ownership, and faster/safer deploys.

```
User
  |
  v
[frontend/consumer] -- REST -->
  |
  | /posts, /comments
  v
[blog-api-service] ----> blog DB (SQLite in dev; Postgres/MySQL in prod)
  |
  | /login, /signup, /me
  v
[auth-service] ---------> auth DB (SQLite in dev; Postgres/MySQL in prod)
```

## Quickstart (monolith, local)

- Create a venv and install deps: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Initialize the DB (creates `database.db` and seeds two posts): `python init_db.py`
- Run the app: `export FLASK_APP=app.py && flask run` then open http://127.0.0.1:5000

## Microservices: develop locally

Blog API:
- `cd services/blog-api`
- `python3 -m venv .venv && source .venv/bin/activate`
- `pip install -r requirements.txt`
- Run tests: `pytest -q`
- Run service: `BLOG_DB_PATH=./database.db flask --app app run --port 5001`

Auth service:
- `cd services/auth`
- `python3 -m venv .venv && source .venv/bin/activate`
- `pip install -r requirements.txt`
- Run tests: `pytest -q`
- Run service: `AUTH_DB_PATH=./auth.db JWT_SECRET=dev-secret flask --app app run --port 5002`

## Tests

- Monolith: `pytest -q` — uses a temp SQLite DB and seeds data via the fixture in `tests/conftest.py`.
- Services: `pytest services/blog-api/tests -q` and `pytest services/auth/tests -q`.

## Container & Kubernetes

- Monolith image: `docker build -t varadpoddar/flask_blog:latest .`
- Blog API image: `docker build -t varadpoddar/blog-api:latest services/blog-api`
- Auth image: `docker build -t varadpoddar/auth-service:latest services/auth`
- K8s (monolith): apply `k8s/monolith-deployment.yaml` + `k8s/monolith-service.yaml` (NodePort 30080 -> 5000).
- K8s (microservices): apply `k8s/blog-api-deployment.yaml` + `k8s/blog-api-service.yaml` (NodePort 30081 -> 5001) and `k8s/auth-deployment.yaml` + `k8s/auth-service.yaml` (NodePort 30082 -> 5002). Set `JWT_SECRET` for auth in production.

## CI/CD

- `.github/workflows/ci-cd.yml` builds and pushes three images on pushes/PRs to `main`:
  - monolith: `varadpoddar/flask_blog`
  - blog API: `varadpoddar/blog-api`
  - auth service: `varadpoddar/auth-service`
  Uses `docker/build-push-action`, tags `latest` and commit SHA; requires Docker Hub credentials.

## Repo Highlights

- `app.py` — monolith routes for listing, viewing, creating, editing, and deleting posts.
- `init_db.py` / `schema.sql` — initialize and seed SQLite.
- `scripts/docker-entrypoint.sh` — monolith boot-time DB creation inside the container.
- `Dockerfile` — monolith multi-stage: deps -> tests -> slim runtime.
- `templates/` & `static/` — UI (Bootstrap 4 + custom CSS).
- `services/blog-api` — REST blog API, tests, Dockerfile, entrypoint, schema.
- `services/auth` — REST auth API (JWT), tests, Dockerfile, entrypoint, schema.
