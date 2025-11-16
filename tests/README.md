Local test & docker instructions

Run tests locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest
pytest -q
```

Build Docker image locally (tests run during build):

```bash
# set IMAGE and optionally TAG
IMAGE=yourrepo/flask_blog TAG=latest ./scripts/build_and_push.sh
```

CI / GitHub Actions

Set the following repository secrets for the provided workflow:
- DOCKER_REGISTRY (e.g., docker.io)
- DOCKER_USERNAME
- DOCKER_PASSWORD
- DOCKER_REPOSITORY (e.g., myuser/flask_blog)
