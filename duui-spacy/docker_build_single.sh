export TEXTIMAGER_SPACY_SINGLE_MODEL_LANG=de
#export TEXTIMAGER_SPACY_SINGLE_MODEL_LANG=$1
#export TEXTIMAGER_SPACY_SINGLE_MODEL=de_core_news_sm
#export TEXTIMAGER_SPACY_SINGLE_MODEL=en_core_web_sm
#export TEXTIMAGER_SPACY_SINGLE_MODEL=de_core_news_lg
export TEXTIMAGER_SPACY_SINGLE_MODEL=$2
export TEXTIMAGER_SPACY_ANNOTATOR_NAME=duui-spacy-$TEXTIMAGER_SPACY_SINGLE_MODEL
export TEXTIMAGER_SPACY_ANNOTATOR_VERSION=$3
export TEXTIMAGER_SPACY_LOG_LEVEL=DEBUG
export TEXTIMAGER_SPACY_MODEL_CACHE_SIZE=3

export DOCKER_REGISTRY="docker.texttechnologylab.org/"

docker build \
  --build-arg TEXTIMAGER_SPACY_VARIANT \
  --build-arg TEXTIMAGER_SPACY_ANNOTATOR_NAME \
  --build-arg TEXTIMAGER_SPACY_ANNOTATOR_VERSION \
  --build-arg TEXTIMAGER_SPACY_LOG_LEVEL \
  --build-arg TEXTIMAGER_SPACY_SINGLE_MODEL_LANG \
  --build-arg TEXTIMAGER_SPACY_SINGLE_MODEL \
  -t ${DOCKER_REGISTRY}${TEXTIMAGER_SPACY_ANNOTATOR_NAME}:${TEXTIMAGER_SPACY_ANNOTATOR_VERSION} \
  -f src/main/docker/Dockerfile_single_model \
  .

