import json
import os
from typing import List

from configs.logger import catch_error
from constants.log_tags import LogTag
from models.target_voice import TargetVoice

# Get the absolute path to the current file
current_file = __file__

# Get the absolute path to the folder containing the current file
current_folder_path = os.path.dirname(os.path.abspath(current_file))

# Absolute path to tts-voices config
tts_config_path = f"{current_folder_path}/tts-voices.json"

try:
    tts_config_file = open(tts_config_path, "r")
    # Convert dict to list of TargetVoices
    tts_config: List[TargetVoice] = [TargetVoice(**voice) for voice in json.load(tts_config_file)]
    tts_config_file.close()
except Exception as e:
    catch_error(
        tag=LogTag.TTS_CONFIG,
        error=e,
    )
