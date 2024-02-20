from typing import List

from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, ResultReason, CancellationReason
from azure.cognitiveservices.speech.audio import AudioOutputConfig

from configs.logger import catch_error, print_info_log
from constants.log_tags import LogTag
from models.text_segment import TextSegment
from configs.env import SPEECH_REGION, SPEECH_KEY

# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = SpeechConfig(
    subscription=SPEECH_KEY,
    region=SPEECH_REGION
)


# languages can be found at https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts
def create_ssml_with_pauses(
    text_segments: List[TextSegment],
    voice_id: str,
    language: str,
    pause_duration_ms: int,
):
    """
    Create an SSML string with pauses and voice specification for Azure's Speech Service.

    :param text_segments: A list of dictionaries with 'text' keys.
    :param voice_id: The name of the voice to be used for speech synthesis.
    :param language: Language value in format expected from Microsoft.
    :param pause_duration_ms: The duration of pauses in milliseconds (default is 1.5 seconds).

    :return: A string formatted in SSML with pauses, voice tag, and necessary namespaces.
    """
    ssml_parts = [
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts"',
        f' xml:lang="{language}">',
        f'<voice name="{voice_id}">',
        f'<break time="{pause_duration_ms}ms"/>'
    ]
    for segment in text_segments:
        ssml_parts.append(segment.text)
        ssml_parts.append(f'<break time="{pause_duration_ms}ms"/>')
    ssml_parts.append('</voice></speak>')
    return ''.join(ssml_parts)


def generate_audio_with_microsoft_provider(
    output_audio_file_path: str,
    text_segments: List[TextSegment],
    voice_id: str,
    language: str,
    pause_duration_ms: int,
    project_id: str,
    show_logs: bool
):
    audio_config = AudioOutputConfig(filename=output_audio_file_path)

    if show_logs:
        print_info_log(
            tag=LogTag.MICROSOFT_PROVIDER,
            message=f"Initializing speech synthesizer..."
        )

    speech_synthesizer = SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    if show_logs:
        print_info_log(
            tag=LogTag.MICROSOFT_PROVIDER,
            message=f"Creating SSML model for synthesizing..."
        )

    # Joins segments into text with pause marks.
    text_for_synthesizing = create_ssml_with_pauses(
        text_segments=text_segments,
        voice_id=voice_id,
        language=language,
        pause_duration_ms=pause_duration_ms,
    )

    if show_logs:
        print_info_log(
            tag=LogTag.MICROSOFT_PROVIDER,
            message=f"Synthesizing text - {text_for_synthesizing}"
        )

    speech_synthesis_result = speech_synthesizer.speak_ssml_async(text_for_synthesizing).get()

    # If synthesizing completed
    if speech_synthesis_result.reason == ResultReason.SynthesizingAudioCompleted:
        if show_logs:
            print_info_log(
                tag=LogTag.MICROSOFT_PROVIDER,
                message=f"Speech synthesized completed."
            )

    # If synthesizing canceled
    elif speech_synthesis_result.reason == ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        catch_error(
            tag=LogTag.MICROSOFT_PROVIDER,
            error=Exception(f"Speech synthesis canceled: {cancellation_details.reason}"),
            project_id=project_id
        )

        if cancellation_details.reason == CancellationReason.Error:
            if cancellation_details.error_details:
                catch_error(
                    tag=LogTag.MICROSOFT_PROVIDER,
                    error=Exception(f"Error details: {cancellation_details.error_details}"),
                    project_id=project_id
                )


# For local test
if __name__ == "__main__":
    test_text_segments = [
        TextSegment(timestamp=(0.0, 3.36), text='Я просыпаюсь утром и хочу потянуться к своему телефону,'),
        TextSegment(timestamp=(3.36, 5.74), text='но я знаю, что даже если бы я прибавил яркость'),
        TextSegment(timestamp=(5.74, 7.0), text='на экране этого телефона,'),
        TextSegment(timestamp=(7.0, 10.28),
                    text='она все равно не достаточно ярка, чтобы вызвать резкий прилив кортизола.'),
        TextSegment(timestamp=(10.28, 14.36), text='И чтобы мне быть наиболее бодрым и сосредоточенным в течение'),
        TextSegment(timestamp=(14.36, 16.16), text='дня и оптимизировать свой сон ночью.'),
        TextSegment(timestamp=(16.16, 20.2), text='Поэтому я встаю с кровати и выхожу на улицу.'),
        TextSegment(timestamp=(20.2, 23.34), text='И если это яркий, чистый день,'),
        TextSegment(timestamp=(23.34, 25.18), text='и солнце низко в небе,'),
        TextSegment(timestamp=(25.18, 27.18), text='или уже начинает подниматься над головой,'),
        TextSegment(timestamp=(27.18, 28.7), text='то, что мы называем низким солнечным углом,'),
        TextSegment(timestamp=(28.7, 31.74), text='тогда я знаю, что вышел на улицу в правильное время.'),
        TextSegment(timestamp=(31.74, 34.78), text='Если небо затянуто облаками и я не вижу солнца,'),
        TextSegment(timestamp=(34.78, 36.38), text='то я также знаю, что делаю хорошее дело,'),
        TextSegment(timestamp=(36.38, 38.56), text='потому что оказывается, особенно в облачные дни,'),
        TextSegment(timestamp=(38.56, 40.66),
                    text='вы хотите выйти на улицу и получить как можно больше световой энергии'),
        TextSegment(timestamp=(40.66, 42.42), text='или фотонов в своих глазах.'),
        TextSegment(timestamp=(42.42, 44.3), text='Но допустим, это очень ясный день'),
        TextSegment(timestamp=(44.3, 46.44), text='и я вижу, где солнце.'),
        TextSegment(timestamp=(46.44, 49.24), text='Мне не нужно смотреть прямо на солнце.'),
        TextSegment(timestamp=(49.24, 52.2), text='Если оно очень низко в небе, я могу это сделать'),
        TextSegment(timestamp=(52.2, 54.52), text='потому что моим глазам это не причинит большой боли.'),
        TextSegment(timestamp=(54.52, 56.84), text='Однако, если солнце немного ярче.')
    ]
    test_output_audio_file_path = "translated-test.mp3"
    test_voice_id = "ru-RU-DmitryNeural"
    test_language = "russian"
    test_project_id = "07fsfECkwma6fVTDyqQf"
    generate_audio_with_microsoft_provider(
        output_audio_file_path=test_output_audio_file_path,
        text_segments=test_text_segments,
        voice_id=test_voice_id,
        language=test_language,
        pause_duration_ms=3000,
        project_id=test_project_id,
        show_logs=True
    )
