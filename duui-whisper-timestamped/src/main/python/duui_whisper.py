from typing import List, Optional
import logging
from platform import python_version
from sys import version as sys_version
from cassis import *
from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from functools import lru_cache
import whisper_timestamped as whisper
import base64
from time import time


DUUI_DEFAULT_LANGUAGE = "en"

SUPPORTED_LANGS = {
    "de",
    "en",
    "es",
    "fr",
    "it",
    "cn"

}

UIMA_TYPE_TRANSCRIPTION = "org.texttechnologylab.core.annotation.Transcription"

TEXTIMAGER_ANNOTATOR_OUTPUT_TYPES = {
    UIMA_TYPE_TRANSCRIPTION
}

TEXTIMAGER_ANNOTATOR_INPUT_TYPES = {
    "org.texttechnologylab.core.annotation.AudioWav"
}

class Settings(BaseSettings):
    variant: str
    annotator_name: str
    annotator_version: str
    log_level: str
    model_cache_size: int

    class Config:
        env_prefix = 'duui_transcription_whisper_timestamped_'

settings = Settings()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)
logger.info("TTLab TextImager DUUI Whisper-Timestamped")
logger.info("Name: %s", settings.annotator_name)
logger.info("Version: %s", settings.annotator_version)


class Transcription(BaseModel):
    startTime: float
    endTime: float
    speaker: str
    utterance: str
    model: str
    audio_wav_id: int

class AudioWav(BaseModel):
    begin: int
    end: int
    text: str
    base64: str
    channels: int
    frequence: int
    bitsPerSample: int
    id: int


class DUUIRequest(BaseModel):
    audios: List[AudioWav]
    lang: str
    model: Optional[str]

class DocumentModification(BaseModel):
    user: str
    timestamp: int
    comment: str

class DUUIResponse(BaseModel):
    transcripts: List[Transcription]
    modification_meta: Optional[List[DocumentModification]]

class DUUICapability(BaseModel):
    supported_languages: List[str]
    reproducible: bool


class DUUIDocumentation(BaseModel):
    annotator_name: str
    version: str
    implementation_lang: Optional[str]
    meta: Optional[dict]
    docker_container_id: Optional[str]
    parameters: Optional[dict]
    capability: DUUICapability
    implementation_specific: Optional[str]

class DUUIInputOutput(BaseModel):
    inputs: List[str]
    outputs: List[str]


# settings + cache
settings = Settings()
lru_cache_with_size = lru_cache(maxsize=3)


@lru_cache_with_size
def load_pipeline(**kwargs):
    # loads a trankit-Model
    return whisper.load_model(**kwargs)



# Start fastapi
# TODO openapi types are not shown?
# TODO self host swagger files: https://fastapi.tiangolo.com/advanced/extending-openapi/#self-hosting-javascript-and-css-for-docs
app = FastAPI(
    openapi_url="/openapi.json",
    docs_url="/api",
    redoc_url=None,
    title="Whisper-timestamped",
    description="Whisper-Timestamped Implementation for TTLab DUUI",
    version="0.1",
    terms_of_service="https://www.texttechnologylab.org/legal_notice/",
    contact={
        "name": "TTLab Team",
        "url": "https://texttechnologylab.org",
        "email": "schrottenbacher@em.uni-frankfurt.de",
    },
    license_info={
        "name": "AGPL",
        "url": "http://www.gnu.org/licenses/agpl-3.0.en.html",
    },
)

typesystem_filename = 'TypeSystem.xml'
logger.debug("Loading typesystem from \"%s\"", typesystem_filename)
with open(typesystem_filename, 'rb') as f:
    typesystem = load_typesystem(f)
    typesystem_xml_content = typesystem.to_xml().encode("utf-8")
    logger.debug("Base typesystem:")
    logger.debug(typesystem_xml_content)

lua_communication_script_filename = "communication.lua"
logger.debug("Loading Lua communication script from \"%s\"", lua_communication_script_filename)
with open(lua_communication_script_filename, 'rb') as f:
    lua_communication_script = f.read().decode("utf-8")
    logger.debug("Lua communication script:")
    logger.debug(lua_communication_script_filename)



@app.get("/v1/typesystem")
def get_typesystem() -> Response:
    return Response(
        content=typesystem_xml_content,
        media_type="application/xml"
    )


@app.get("/v1/details/input_output")
def get_input_output() -> DUUIInputOutput:
    return DUUIInputOutput(
        inputs=TEXTIMAGER_ANNOTATOR_INPUT_TYPES,
        outputs=TEXTIMAGER_ANNOTATOR_OUTPUT_TYPES
    )

@app.get("/v1/communication_layer", response_class=PlainTextResponse)
def get_communication_layer() -> str:
    return lua_communication_script


@app.get("/v1/documentation")
def get_documentation() -> DUUIDocumentation:
    capabilities = DUUICapability(
        supported_languages=sorted(list(SUPPORTED_LANGS)),
        reproducible=True
    )

    documentation = DUUIDocumentation(
        annotator_name=settings.annotator_name,
        version=settings.annotator_version,
        implementation_lang="Python",
        meta={
            "python_version": python_version(),
            "python_version_full": sys_version,
            "diaper_version": "diaper-08-02-2024",
        },
        docker_container_id="[TODO]",
        parameters={},
        capability=capabilities,
        implementation_specific=None,
    )

    return documentation



# Process request from DUUI
@app.post("/v1/process")
def post_process(request: DUUIRequest) -> DUUIResponse:
    
    config = {"name": request.model if request.model else "base"}
    # load pipeline
    pipeline = load_pipeline(**config)
    modification_timestamp_seconds = int(time())
    transcripts = []
    modification_meta = []

    lang = request.lang
    if lang not in SUPPORTED_LANGS:
        print("WARNING: Unsupported language detected:", lang, "using default language:", DUUI_DEFAULT_LANGUAGE)
        lang = DUUI_DEFAULT_LANGUAGE

    for audio in request.audios:
        try: 
            with open("audio.wav", "wb") as f:
                f.write(base64.b64decode(audio.base64))
            result = pipeline.transcribe(audio="audio.wav", language=lang, word_timestamps=True)

            for segment in result["segments"]:
                for word in segment["words"]:
                    audioStart = word['start']
                    audioEnd = word['end']
                    text = word['word']
                    transcripts.append(Transcription(
                        startTime=float(audioStart),
                        endTime=float(audioEnd),
                        speaker="Speaker",
                        utterance=text,
                        audio_wav_id=audio.id,
                        model=f"whisper-timestamped-{request.model}"
                    ))
            
            modification_meta.append(DocumentModification(
                user=settings.annotator_name,
                timestamp=modification_timestamp_seconds,
                comment=f"{settings.annotator_name} ({settings.annotator_version}), DiaPer (08-02-2024)"
            ))

        except Exception as ex:
            logger.exception(ex)


    
    logger.debug(transcripts)
    logger.debug(modification_meta)

    duration = int(time()) - modification_timestamp_seconds
    logger.info("Processed in %d seconds", duration)

    return DUUIResponse(
        transcripts = transcripts,
        modification_meta = modification_meta
    )


