#!/usr/bin/env bash
set -euo pipefail

export LANGUAGE_ANNOTATOR_CUDA=
#export LANGUAGE_ANNOTATOR_CUDA="-cuda"

export LANGUAGE_ANNOTATOR_NAME=duui-language-annotation
export LANGUAGE_ANNOTATOR_VERSION=0.2.0
export LANGUAGE_LOG_LEVEL=DEBUG
export LANGUAGE_MODEL_CACHE_SIZE=3
export DOCKER_REGISTRY="docker.texttechnologylab.org/"


docker build \
  --build-arg LANGUAGE_ANNOTATOR_NAME \
  --build-arg LANGUAGE_ANNOTATOR_VERSION \
  --build-arg LANGUAGE_LOG_LEVEL \
  -t ${DOCKER_REGISTRY}${LANGUAGE_ANNOTATOR_NAME}:${LANGUAGE_ANNOTATOR_VERSION}${LANGUAGE_ANNOTATOR_CUDA} \
  -f src/main/docker/Dockerfile${LANGUAGE_ANNOTATOR_CUDA} \
  .

docker tag \
  ${DOCKER_REGISTRY}${LANGUAGE_ANNOTATOR_NAME}:${LANGUAGE_ANNOTATOR_VERSION}${LANGUAGE_ANNOTATOR_CUDA} \
  ${DOCKER_REGISTRY}${LANGUAGE_ANNOTATOR_NAME}:latest${LANGUAGE_ANNOTATOR_CUDA}
