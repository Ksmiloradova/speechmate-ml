import time
from typing import List

from elevenlabs import APIError, generate as generate_audio, set_api_key, RateLimitError

from configs.logger import print_info_log, catch_error
from constants.log_tags import LogTag
from models.text_segment import TextSegment
from configs.env import ELEVEN_LABS_API_KEY

set_api_key(ELEVEN_LABS_API_KEY)

DELAY_TO_WAIT_IN_SECONDS = 5 * 60


def generate_audio_with_elevenlabs_provider(
    output_audio_file_path: str,
    text_segments: List[TextSegment],
    voice_id: str,
    pause_duration_ms: int,
    project_id: str,
    show_logs: bool = False
):
    pause_tag = f" <break time=\"{pause_duration_ms / 1000}s\"/> "
    combined_text = ""

    for segment in text_segments:
        combined_text += segment.text + pause_tag

    try:
        audio = generate_audio(
            text=combined_text,
            voice=voice_id,
            model="eleven_multilingual_v2"
        )
        with open(output_audio_file_path, 'wb') as f:
            f.write(audio)

    except APIError as api_error:
        print("(elevenlabs_provider) API Error:", str(api_error))

        # If too many requests to 11labs, wait and then try again
        if isinstance(api_error, RateLimitError):
            if show_logs:
                print_info_log(
                    tag=LogTag.ELEVENLABS_PROVIDER,
                    message=f"Wait {DELAY_TO_WAIT_IN_SECONDS} seconds and then repeat request to 11labs..."
                )
            time.sleep(DELAY_TO_WAIT_IN_SECONDS)
            return generate_audio_with_elevenlabs_provider(
                output_audio_file_path=output_audio_file_path,
                text_segments=text_segments,
                voice_id=voice_id,
                pause_duration_ms=pause_duration_ms,
                project_id=project_id,
                show_logs=show_logs
            )
        else:
            catch_error(
                tag=LogTag.ELEVENLABS_PROVIDER,
                error=api_error,
                project_id=project_id
            )


# Example usage
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
    test_voice_id = "N2lVS1w4EtoT3dr4eOWO"
    test_project_id = "07fsfECkwma6fVTDyqQf"
    generate_audio_with_elevenlabs_provider(
        output_audio_file_path=test_output_audio_file_path,
        text_segments=test_text_segments,
        voice_id=test_voice_id,
        project_id=test_project_id,
        pause_duration_ms=3000,
        show_logs=True
    )
