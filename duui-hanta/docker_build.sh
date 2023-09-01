export TEXTIMAGER_HANTA_ANNOTATOR_NAME=textimager_duui_hanta
export TEXTIMAGER_HANTA_ANNOTATOR_VERSION=0.0.1
export TEXTIMAGER_HANTA_LOG_LEVEL=DEBUG
export TEXTIMAGER_HANTA_PARSER_MODEL_NAME=morphmodel_ger.pgz

docker build \
  --build-arg TEXTIMAGER_HANTA_ANNOTATOR_NAME \
  --build-arg TEXTIMAGER_HANTA_ANNOTATOR_VERSION \
  --build-arg TEXTIMAGER_HANTA_LOG_LEVEL \
  -t ${TEXTIMAGER_HANTA_ANNOTATOR_NAME}:${TEXTIMAGER_HANTA_ANNOTATOR_VERSION} \
  -f src/main/docker/Dockerfile \
  .