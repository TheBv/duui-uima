TEXTIMAGER_DUUI_TRANSFORMERS_TOXIC_ANNOTATOR_NAME="textimager-duui-transformers-toxic" \
TEXTIMAGER_DUUI_TRANSFORMERS_TOXIC_ANNOTATOR_VERSION="unset" \
TEXTIMAGER_DUUI_TRANSFORMERS_TOXIC_LOG_LEVEL="DEBUG" \
TEXTIMAGER_DUUI_TRANSFORMERS_TOXIC_MODEL_CACHE_SIZE="1" \
uvicorn src.main.python.textimager_duui_transformers_toxic:app --host 0.0.0.0 --port 9714 --workers 1
