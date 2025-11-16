#!/usr/bin/env bash
set -euo pipefail

# Usage:
# REGISTRY=myregistry.example.com IMAGE_NAME=myuser/flask_blog TAG=ci-123 ./ci/test_and_push.sh
# If DOCKER_USERNAME and DOCKER_PASSWORD are set, the script will attempt to login first.

REGISTRY=${REGISTRY:-}
IMAGE_NAME=${IMAGE_NAME:-flask_blog}
TAG=${TAG:-latest}

if [ -n "$REGISTRY" ]; then
  IMAGE="$REGISTRY/$IMAGE_NAME:$TAG"
else
  IMAGE="$IMAGE_NAME:$TAG"
fi

echo "Building image $IMAGE"
docker build -t "$IMAGE" .

echo "Running tests in container (this will run 'pytest -q')"
# Run the container; since Dockerfile ENTRYPOINT runs pytest, the container will exit with pytest status
docker run --rm "$IMAGE"

echo "Tests passed. Preparing to push $IMAGE"

if [ -n "${DOCKER_USERNAME:-}" ] && [ -n "${DOCKER_PASSWORD:-}" ]; then
  echo "Logging into registry ${REGISTRY:-docker.io}"
  if [ -n "$REGISTRY" ]; then
    docker login "$REGISTRY" -u "$DOCKER_USERNAME" -p "$DOCKER_PASSWORD"
  else
    docker login -u "$DOCKER_USERNAME" -p "$DOCKER_PASSWORD"
  fi
fi

echo "Pushing $IMAGE"
docker push "$IMAGE"

echo "Push completed"
