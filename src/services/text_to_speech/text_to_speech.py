from typing import List, Tuple

from pydub import AudioSegment
from pydub.silence import detect_nonsilent

from constants.files import PROCESSING_FILES_DIR_PATH
from constants.log_tags import LogTag
from services.text_to_speech.providers.elevenlabs import generate_audio_with_elevenlabs_provider
from services.text_to_speech.providers.microsoft import generate_audio_with_microsoft_provider
from models.text_segment import TextSegment, TextSegmentWithAudioTimestamp
from models.voice_provider import VoiceProvider
from configs.logger import catch_error, print_info_log
from configs.tts_config import tts_config

DELAY_TO_WAIT_IN_SECONDS = 5 * 60

AUDIO_SEGMENT_PAUSE = 3000  # 3 sec


def add_audio_timestamps_to_segments(
    audio_file_path: str,
    text_segments: List[TextSegment],
    min_silence_len=2000,
    silence_thresh=-30,
    padding=500
):
    """
    Detects pauses in an audio file and adds audio_timestamps to segments.

    :param audio_file_path: Path to the audio file.
    :param text_segments: A list of text segments with 'timestamp' and 'text' keys.
    :param min_silence_len: Minimum length of silence to consider as a pause in milliseconds.
    :param silence_thresh: Silence threshold in dB.
    :param padding: Additional time in milliseconds to add to the end of each segment.
    :return: A list of tuples where each tuple is (start, end) time of pauses.
    """

    audio = AudioSegment.from_file(audio_file_path)
    speak_times = detect_nonsilent(
        audio_segment=audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )
    adjusted_speak_times: List[Tuple[float, float]] = []
    for start, end in speak_times:
        timestamps = max(start - padding, 0), min(end + padding, len(audio))
        adjusted_speak_times.append(timestamps)

    # Combine text segments and audio timestamps to one list
    combined_list: List[Tuple[TextSegment, Tuple[float, float]]] = list(
        zip(text_segments, adjusted_speak_times)
    )

    text_segments_with_audio_timestamps = []
    for segment, audio_timestamp in combined_list:
        text_segments_with_audio_timestamps.append(
            TextSegmentWithAudioTimestamp(
                **segment.dict(),  # Convert TextSegment to dict
                audio_timestamp=audio_timestamp
            )
        )
    return text_segments_with_audio_timestamps

    # Check the time difference between the end of one segment and the start of the next
    # for i in range(len(adjusted_speak_times) - 1):
    #     end_of_current = adjusted_speak_times[i][1]
    #     start_of_next = adjusted_speak_times[i + 1][0]
    #     time_diff = start_of_next - end_of_current
    #     if abs(time_diff - 3000) > 100:  # Allowing a 100ms deviation
    #         print(f'Time gap discrepancy between segments {i} and {i + 1}: {time_diff}ms')


def get_voice_by_id(voice_id: int):
    """
    Return voice from tts-configs by specified voice_id

    :param voice_id: Target voice id

    :returns: Voice object from tts-configs
    """

    for voice_from_config in tts_config:
        if voice_from_config.voice_id == voice_id:
            return voice_from_config

    # If voice not returned after loop
    catch_error(
        tag=LogTag.GET_VOICE_BY_ID,
        error=Exception(f"Voice with id {voice_id} is not found in tts-config.")
    )


def text_to_speech(
    text_segments: List[TextSegment],
    voice_id: int,
    project_id: str,
    show_logs: bool = False
):
    translated_audio_file_path = f"{PROCESSING_FILES_DIR_PATH}/{project_id}-translated.mp3"
    try:
        voice_from_config = get_voice_by_id(voice_id)
        original_voice_id = voice_from_config.original_id
        voice_provider = voice_from_config.provider
        voice_language = voice_from_config.languages[0]

        if voice_provider == VoiceProvider.ELEVEN_LABS:
            if show_logs:
                print_info_log(
                    tag=LogTag.TEXT_TO_SPEECH,
                    message=f"Processing text to speech for voice with id {voice_id} with {voice_provider}"
                )
            generate_audio_with_elevenlabs_provider(
                output_audio_file_path=translated_audio_file_path,
                text_segments=text_segments,
                voice_id=original_voice_id,
                pause_duration_ms=AUDIO_SEGMENT_PAUSE,
                project_id=project_id,
                show_logs=show_logs
            )
        elif voice_provider == VoiceProvider.MICROSOFT:
            if show_logs:
                print_info_log(
                    tag=LogTag.TEXT_TO_SPEECH,
                    message=f"Processing text to speech for voice with id {voice_id} with {voice_provider}"
                )
            generate_audio_with_microsoft_provider(
                output_audio_file_path=translated_audio_file_path,
                text_segments=text_segments,
                voice_id=original_voice_id,
                language=voice_language,
                pause_duration_ms=AUDIO_SEGMENT_PAUSE,
                project_id=project_id,
                show_logs=show_logs
            )
        else:
            catch_error(
                tag=LogTag.TEXT_TO_SPEECH,
                error=Exception(f"Voice provider to found for voice with id {voice_id} and {voice_provider}"),
                project_id=project_id
            )

        if show_logs:
            print_info_log(
                tag=LogTag.TEXT_TO_SPEECH,
                message=f"Translated audio save to {translated_audio_file_path}"
            )

        translated_text_segments_with_audio_timestamp = add_audio_timestamps_to_segments(
            audio_file_path=translated_audio_file_path,
            text_segments=text_segments
        )
        return translated_audio_file_path, translated_text_segments_with_audio_timestamp

    except Exception as e:
        catch_error(
            tag=LogTag.TEXT_TO_SPEECH,
            error=e,
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
    # test_voice_id = 559  # 11labs voice
    test_voice_id = 165  # microsoft voice
    test_project_id = "07fsfECkwma6fVTDyqQf"
    test_translated_audio_file_path, test_translated_text_segments_with_audio_timestamp = text_to_speech(
        text_segments=test_text_segments,
        voice_id=test_voice_id,
        project_id=test_project_id,
        show_logs=True
    )
    print(test_translated_audio_file_path)
    print(test_translated_text_segments_with_audio_timestamp)
