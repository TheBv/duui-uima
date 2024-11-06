FROM mambaorg/micromamba:cuda11.4.3-ubuntu20.04


WORKDIR /usr/src/app

EXPOSE 9714

COPY env.yaml /tmp/env.yaml
RUN micromamba install -y -n base -f /tmp/env.yaml 

ARG DUUI_TRANSCRIPTION_DIAPER_LOG_LEVEL="DEBUG"
ENV DUUI_TRANSCRIPTION_DIAPER_LOG_LEVEL=$DUUI_TRANSCRIPTION_DIAPER_LOG_LEVEL

ARG DUUI_TRANSCRIPTION_DIAPER_ANNOTATOR_NAME="duui-transcription-diaper"
ENV DUUI_TRANSCRIPTION_DIAPER_ANNOTATOR_NAME=$DUUI_TRANSCRIPTION_DIAPER_ANNOTATOR_NAME
ARG DUUI_TRANSCRIPTION_DIAPER_ANNOTATOR_VERSION="unset"
ENV DUUI_TRANSCRIPTION_DIAPER_ANNOTATOR_VERSION=$DUUI_TRANSCRIPTION_DIAPER_ANNOTATOR_VERSION

ARG DUUI_TRANSCRIPTION_DIAPER_MODEL_CACHE_SIZE=3
ENV DUUI_TRANSCRIPTION_DIAPER_MODEL_CACHE_SIZE=$DUUI_TRANSCRIPTION_DIAPER_MODEL_CACHE_SIZE

ARG DUUI_TRANSCRIPTION_DIAPER_VARIANT=3
ENV DUUI_TRANSCRIPTION_DIAPER_VARIANT=$DUUI_TRANSCRIPTION_DIAPER_VARIANT


COPY ./src/main/python/diaper ./diaper
COPY ./src/main/python/examples ./examples
COPY ./src/main/python/models ./models
COPY ./src/main/resources/TypeSystem.xml ./TypeSystem.xml
COPY ./src/main/python/duui.py ./duui.py
COPY ./src/main/lua/communication.lua ./communication.lua

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh","uvicorn", "duui:app", "--host", "0.0.0.0", "--port" ,"9714"]
CMD ["--workers", "1"]
