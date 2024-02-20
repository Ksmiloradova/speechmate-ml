from enum import Enum


class VoiceProvider(str, Enum):
    MICROSOFT = "azure"
    ELEVEN_LABS = "eleven_labs"
