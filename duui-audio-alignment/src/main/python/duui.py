import base64
import logging
from platform import python_version
from sys import version as sys_version
from time import time
from typing import List, Optional

from cassis import load_typesystem
from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings

import os


from util import get_words_speaker_mapping, get_sentences_speaker_mapping, get_realigned_ws_mapping_with_punctuation
import re
from deepmultilingualpunctuation import PunctuationModel

DUUI_DEFAULT_LANGUAGE = "en"

class Settings(BaseSettings):
    variant: str
    annotator_name: str
    annotator_version: str
    log_level: str
    model_cache_size: int

    class Config:
        env_prefix = 'duui_transcription_diaper_'

settings = Settings()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)
logger.info("TTLab TextImager DUUI DiaPer")
logger.info("Name: %s", settings.annotator_name)
logger.info("Version: %s", settings.annotator_version)


UIMA_TYPE_RTTM = "org.texttechnologylab.core.annotation.RTTM"

DUUI_OUTPUT_TYPES = {
    UIMA_TYPE_RTTM
}

DUUI_INPUT_TYPES = {
    "org.texttechnologylab.core.annotation.AudioWav"
}

SUPPORTED_LANGS = {
    "any",
}


class AnnotationMeta(BaseModel):
    name: str
    version: str
    modelName: str
    modelVersion: str
    spacyVersion: str
    modelLang: str
    modelSpacyVersion: str
    modelSpacyGitVersion: str


class DocumentModification(BaseModel):
    user: str
    timestamp: int
    comment: str

class AudioWav(BaseModel):
    begin: int
    end: int
    text: str
    base64: str
    channels: int
    frequence: int
    bitsPerSample: int
    id: int


class RTTM(BaseModel):
    segmentType: str
    channel: int
    turnOnset: float
    turnDuration: float
    orthographyField: str
    speakerType: str
    speakerName: str
    confidenceScore: float
    signalLookaheadTime: float
    model: str
    audio_wav_id: int


class DUUIRequest(BaseModel):
    audios: List[AudioWav]
    len: int
    lang: str


class DUUIResponse(BaseModel):
    rttms: List[RTTM]
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


ROOT = os.getcwd()
data_dir = os.path.join(ROOT,'data')
os.makedirs(data_dir, exist_ok=True)

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


def read_file(path_to_file):
    with open(path_to_file) as f:
        contents = f.read().splitlines()
    return contents

def find_rttm_file(dir):
    for subdir, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".rttm"):
                return subdir, file

app = FastAPI(
    title=settings.annotator_name,
    description="DiaPer implementation for TTLab TextImager DUUI",
    version=settings.annotator_version,
    terms_of_service="https://www.texttechnologylab.org/legal_notice/",
    contact={
        "name": "TTLab Team - Patrick Schrottenbacher",
        "url": "https://texttechnologylab.org",
        "email": "schrottenbacher@em.uni-frankfurt.de",
    },
    license_info={
        "name": "AGPL",
        "url": "http://www.gnu.org/licenses/agpl-3.0.en.html",
    },
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


@app.get("/v1/typesystem")
def get_typesystem() -> Response:
    return Response(
        content=typesystem_xml_content,
        media_type="application/xml"
    )


@app.get("/v1/details/input_output")
def get_input_output() -> DUUIInputOutput:
    return DUUIInputOutput(
        inputs=DUUI_INPUT_TYPES,
        outputs=DUUI_OUTPUT_TYPES
    )

@app.post("/v1/process")
def post_process(request: DUUIRequest) -> DUUIResponse:
    modification_timestamp_seconds = int(time())
    rttms = []
    modification_meta = []

    try:

        AUDIO_NAME = "audio"
        AUDIO_FILENAME = AUDIO_NAME + ".wav"

        for audio in request.audios:
            
            with open(os.path.join(data_dir,'transcript.json'),'r') as fp:
                file = json.load(fp)

            word_timestamps = []
            # [{'text': 'Und', 'start': 4.14, 'end': 5.68, 'confidence': 0.036}, {'text': 'zwar', 'start': 15.73, 'end': 18.03, 'confidence': 0.623}, {'text': 'werde
            # We can also select text here
            for segment in file['segments']:
                word_timestamps.extend(segment['words'])

            speaker_ts = []
            with open(os.path.join(data_dir, "pred_rttms", "test.rttm"), "r") as f:
                lines = f.readlines()
                for line in lines:
                    line_list = line.split(" ")
                    s = int(float(line_list[5]) * 1000)
                    e = s + int(float(line_list[8]) * 1000)
                    speaker_ts.append([s, e, int(line_list[11].split("_")[-1])])

            wsm = get_words_speaker_mapping(word_timestamps, speaker_ts, "start")


            ######


            punct_model = PunctuationModel(model="kredor/punctuate-all")

            words_list = list(map(lambda x: x["word"], wsm))

            labled_words = punct_model.predict(words_list)

            ending_puncts = ".?!"
            model_puncts = ".,;:!?"

            # We don't want to punctuate U.S.A. with a period. Right?
            is_acronym = lambda x: re.fullmatch(r"\b(?:[a-zA-Z]\.){2,}", x)
            for word_dict, labeled_tuple in zip(wsm, labled_words):
                word = word_dict["word"]
                if (word and labeled_tuple[1] in ending_puncts and (word[-1] not in model_puncts or is_acronym(word))):
                    word += labeled_tuple[1]
                    if word.endswith(".."):
                        word = word.rstrip(".")
                    word_dict["word"] = word

            wsm = get_realigned_ws_mapping_with_punctuation(wsm)
            ssm = get_sentences_speaker_mapping(wsm, speaker_ts)



            for line in pred_rttm:
                elements = line.replace("   ", " ").split(" ")
                if len(elements) < 10:
                    print(f"Error parsing line: {line}")
                    continue
                rttms.append(RTTM(
                    segmentType=elements[0],
                    #file=elements[1],
                    channel=int(elements[2]),
                    turnOnset=float(elements[3]),
                    turnDuration=float(elements[4]),
                    orthographyField=elements[5],
                    speakerType=elements[6],
                    speakerName=elements[7],
                    confidenceScore=float(elements[8]) if "NA" not in elements[8] else -1,
                    signalLookaheadTime=float(elements[9]) if "NA" not in elements[9] else -1,
                    model=model_name,
                    audio_wav_id=audio.id
                ))

        
            modification_meta.append(DocumentModification(
                user=settings.annotator_name,
                timestamp=modification_timestamp_seconds,
                comment=f"{settings.annotator_name} ({settings.annotator_version}), DiaPer (08-02-2024)"
            ))

    except Exception as ex:
        logger.exception(ex)

    logger.debug(rttms)
    logger.debug(modification_meta)

    duration = int(time()) - modification_timestamp_seconds
    logger.info("Processed in %d seconds", duration)

    return DUUIResponse(
        rttms=rttms,
        modification_meta=modification_meta,
    )

if __name__ == "__main__":
    AUDIO_FILENAME = "audio.wav"
    model = "infer_16k_10attractors.yaml"
    models = "10attractors/SC_LibriSpeech_2spk_adapted1-10/models/"
    sample_rate = 16000
