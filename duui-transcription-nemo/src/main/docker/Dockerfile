FROM nvcr.io/nvidia/nemo:24.05

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales libsndfile1 ffmpeg
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

WORKDIR /usr/src/app

EXPOSE 9714

RUN pip install setuptools wheel

ARG DUUI_TRANSCRIPTION_NEMO_LOG_LEVEL="DEBUG"
ENV DUUI_TRANSCRIPTION_NEMO_LOG_LEVEL=$DUUI_TRANSCRIPTION_NEMO_LOG_LEVEL

ARG DUUI_TRANSCRIPTION_NEMO_ANNOTATOR_NAME="duui-transcription-nemo"
ENV DUUI_TRANSCRIPTION_NEMO_ANNOTATOR_NAME=$DUUI_TRANSCRIPTION_NEMO_ANNOTATOR_NAME
ARG DUUI_TRANSCRIPTION_NEMO_ANNOTATOR_VERSION="unset"
ENV DUUI_TRANSCRIPTION_NEMO_ANNOTATOR_VERSION=$DUUI_TRANSCRIPTION_NEMO_ANNOTATOR_VERSION

ARG DUUI_TRANSCRIPTION_NEMO_MODEL_CACHE_SIZE=3
ENV DUUI_TRANSCRIPTION_NEMO_MODEL_CACHE_SIZE=$DUUI_TRANSCRIPTION_NEMO_MODEL_CACHE_SIZE

ARG DUUI_TRANSCRIPTION_NEMO_VARIANT=3
ENV DUUI_TRANSCRIPTION_NEMO_VARIANT=$DUUI_TRANSCRIPTION_NEMO_VARIANT


COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt


COPY ./src/main/resources/TypeSystem.xml ./TypeSystem.xml
COPY ./src/main/python/duui.py ./duui.py
COPY ./src/main/lua/communication.lua ./communication.lua
COPY ./src/main/python/configs ./data

ENTRYPOINT ["uvicorn", "duui:app", "--host", "0.0.0.0", "--port" ,"9714"]
CMD ["--workers", "1"]
