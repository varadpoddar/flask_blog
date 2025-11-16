#!/usr/bin/env bash
set -euo pipefail

# Simple helper to build the Docker image (which runs tests during build) and push it.
# Usage:
#   IMAGE=myregistry.io/myuser/flask_blog TAG=latest ./scripts/build_and_push.sh

IMAGE=${IMAGE:-}
TAG=${TAG:-latest}

if [ -z "$IMAGE" ]; then
  echo "Please set IMAGE environment variable, e.g. IMAGE=yourrepo/flask_blog"
  exit 2
fi

FULL="${IMAGE}:${TAG}"

echo "Building image ${FULL} (tests run during build)..."
docker build -t "$FULL" .

echo "Pushing image ${FULL}..."
docker push "$FULL"

echo "Done."
