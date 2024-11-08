FROM mambaorg/micromamba:cuda11.4.3-ubuntu20.04


WORKDIR /usr/src/app

EXPOSE 9714

COPY env.yaml /tmp/env.yaml
RUN micromamba install -y -n base -f /tmp/env.yaml 

ARG DUUI_AUDIO_ALIGNMENT_LOG_LEVEL="DEBUG"
ENV DUUI_AUDIO_ALIGNMENT_LOG_LEVEL=$DUUI_AUDIO_ALIGNMENT_LOG_LEVEL

ARG DUUI_AUDIO_ALIGNMENT_ANNOTATOR_NAME="duui-AUDIO_ALIGNMENT"
ENV DUUI_AUDIO_ALIGNMENT_ANNOTATOR_NAME=$DUUI_AUDIO_ALIGNMENT_ANNOTATOR_NAME
ARG DUUI_AUDIO_ALIGNMENT_ANNOTATOR_VERSION="unset"
ENV DUUI_AUDIO_ALIGNMENT_ANNOTATOR_VERSION=$DUUI_AUDIO_ALIGNMENT_ANNOTATOR_VERSION

ARG DUUI_AUDIO_ALIGNMENT_MODEL_CACHE_SIZE=3
ENV DUUI_AUDIO_ALIGNMENT_MODEL_CACHE_SIZE=$DUUI_AUDIO_ALIGNMENT_MODEL_CACHE_SIZE

ARG DUUI_AUDIO_ALIGNMENT_VARIANT=3
ENV DUUI_AUDIO_ALIGNMENT_VARIANT=$DUUI_AUDIO_ALIGNMENT_VARIANT

# Prefetch the punctation model
RUN "/usr/local/bin/_entrypoint.sh" python -c "from deepmultilingualpunctuation import PunctuationModel; PunctuationModel('kredor/punctuate-all')"

COPY ./src/main/resources/TypeSystem.xml ./TypeSystem.xml
COPY ./src/main/python/duui.py ./duui.py
COPY ./src/main/python/util.py ./util.py
COPY ./src/main/lua/communication.lua ./communication.lua

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh","uvicorn", "duui:app", "--host", "0.0.0.0", "--port" ,"9714"]
CMD ["--workers", "1"]
