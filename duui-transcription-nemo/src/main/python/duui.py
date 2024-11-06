import base64
import logging
from pathlib import Path
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
import json

import nemo

from omegaconf import OmegaConf

from nemo.collections.asr.parts.utils.diarization_utils import OfflineDiarWithASR
from nemo.collections.asr.parts.utils.decoder_timestamps_utils import ASRDecoderTimeStamps

DUUI_DEFAULT_LANGUAGE = "en"

class Settings(BaseSettings):
    variant: str
    annotator_name: str
    annotator_version: str
    log_level: str
    model_cache_size: int

    class Config:
        env_prefix = 'duui_transcription_nemo_'


settings = Settings()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)
logger.info("TTLab TextImager DUUI Nemo")
logger.info("Name: %s", settings.annotator_name)
logger.info("Version: %s", settings.annotator_version)


UIMA_TYPE_RTTM = "org.texttechnologylab.core.annotation.RTTM"
UIMA_TYPE_TRANSCRIPTION = "org.texttechnologylab.core.annotation.Transcription"

TEXTIMAGER_ANNOTATOR_OUTPUT_TYPES = {
    UIMA_TYPE_RTTM,
    UIMA_TYPE_TRANSCRIPTION
}

TEXTIMAGER_ANNOTATOR_INPUT_TYPES = {
    "org.texttechnologylab.core.annotation.AudioWav"
}

SUPPORTED_LANGS = {
    "en",
    "de",
    "es"
}

VALID_DOMAINS = {
    "general",
    "meeting",
    "telephonic"
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

class Transcription(BaseModel):
    startTime: float
    endTime: float
    speaker: str
    utterance: str
    model: str
    audio_wav_id: int

class DUUIRequest(BaseModel):
    audios: list[AudioWav]
    lang: str
    domain_type: str


class DUUIResponse(BaseModel):
    rttms: list[RTTM]
    transcripts: list[Transcription]
    modification_meta: Optional[list[DocumentModification]]


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

app = FastAPI(
    title=settings.annotator_name,
    description="nemo implementation for TTLab TextImager DUUI",
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
            "nemo_version": nemo.__version__,
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
        inputs=TEXTIMAGER_ANNOTATOR_INPUT_TYPES,
        outputs=TEXTIMAGER_ANNOTATOR_OUTPUT_TYPES
    )

@app.post("/v1/process")
def post_process(request: DUUIRequest) -> DUUIResponse:
    modification_timestamp_seconds = int(time())


    lang = request.lang
    if lang not in SUPPORTED_LANGS:
        print("WARNING: Unsupported language detected:", lang, "using default language:", DUUI_DEFAULT_LANGUAGE)
        lang = DUUI_DEFAULT_LANGUAGE

    rttms = []
    transcripts = []
    modification_meta = []
    
    try:

        DOMAIN_TYPE = request.domain_type

        if DOMAIN_TYPE not in VALID_DOMAINS:
            print("WARNING: Unsupported domain type detected:", request.domain_type, "using default domain type: meeting")
            DOMAIN_TYPE = "meeting"
        CONFIG_FILE_NAME = f"diar_infer_{DOMAIN_TYPE}.yaml"

        CONFIG = Path(data_dir) / CONFIG_FILE_NAME
        cfg = OmegaConf.load(CONFIG)

        for audio in request.audios:

            AUDIO_NAME = "audio"
            AUDIO_FILENAME = AUDIO_NAME + ".wav"

            with open(AUDIO_FILENAME, "wb") as f:
                f.write(base64.b64decode(audio.base64))


            meta = {
                'audio_filepath': str(AUDIO_FILENAME),
                'offset': 0,
                'duration': None,
                'label': 'infer',
                'text': '-',
                'num_speakers': None,
                'rttm_filepath': None,
                'uem_filepath': None
            }
            with open(Path(data_dir) / 'input_manifest.json', 'w') as fp:
                json.dump(meta, fp)
                fp.write('\n')

            cfg.diarizer.manifest_filepath = str(Path(data_dir) / 'input_manifest.json')
            
            pretrained_speaker_model = 'titanet_large'
            # cfg.diarizer.manifest_filepath = cfg.diarizer.manifest_filepath
            cfg.diarizer.out_dir = data_dir  # Directory to store intermediate files and prediction outputs
            cfg.diarizer.speaker_embeddings.model_path = pretrained_speaker_model
            cfg.diarizer.clustering.parameters.oracle_num_speakers = False

            # Using Neural VAD and Conformer ASR
            cfg.diarizer.vad.model_path = 'vad_multilingual_marblenet'
            # TODO: Make model parameters configurable
            cfg.diarizer.asr.model_path = f'stt_{lang}_conformer_ctc_large'
            cfg.diarizer.oracle_vad = False  # ----> Not using oracle VAD
            cfg.diarizer.asr.parameters.asr_based_vad = False
            
            asr_decoder_ts = ASRDecoderTimeStamps(cfg.diarizer)
            
            asr_model = asr_decoder_ts.set_asr_model()
            word_hyp, word_ts_hyp = asr_decoder_ts.run_ASR(asr_model)
            asr_diar_offline = OfflineDiarWithASR(cfg.diarizer)
            asr_diar_offline.word_ts_anchor_offset = asr_decoder_ts.word_ts_anchor_offset

            diar_hyp, diar_score = asr_diar_offline.run_diarization(cfg, word_ts_hyp)
            predicted_speaker_label_rttm_path = f"{data_dir}/pred_rttms/{AUDIO_NAME}.rttm"
            pred_rttm = read_file(predicted_speaker_label_rttm_path)

            model_slug = f"{DOMAIN_TYPE}_{cfg.diarizer.speaker_embeddings.model_path}_{cfg.diarizer.vad.model_path}_{cfg.diarizer.asr.model_path}"

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
                    model=model_slug,
                    audio_wav_id=audio.id
                ))


            trans_info_dict = asr_diar_offline.get_transcript_with_speaker_labels(diar_hyp, word_hyp, word_ts_hyp)

            for item in trans_info_dict["audio"]["words"]:
                transcripts.append(Transcription(
                    startTime=item["start_time"],
                    endTime=item["end_time"],
                    speaker=item["speaker"],
                    utterance=item["word"],
                    model=model_slug,
                    audio_wav_id=audio.id
                ))
            
            modification_meta.append(DocumentModification(
                user=settings.annotator_name,
                timestamp=modification_timestamp_seconds,
                comment=f"{settings.annotator_name} ({settings.annotator_version}), nemo ({nemo.__version__})"
            ))

    except Exception as ex:
        logger.exception(ex)

    logger.debug(rttms)
    logger.debug(transcripts)
    logger.debug(meta)
    logger.debug(modification_meta)

    duration = int(time()) - modification_timestamp_seconds
    logger.info("Processed in %d seconds", duration)

    return DUUIResponse(
        rttms=rttms,
        transcripts=transcripts,
        modification_meta=modification_meta,
    )
