import os
import tempfile
from pathlib import Path
from typing import List, Tuple

from pydub import AudioSegment

from constants.files import PROCESSING_FILES_DIR_PATH
from constants.log_tags import LogTag
from models.text_segment import TextSegment
from services.speech_to_text.whisper_endpoint import send_request_to_whisper_endpoint
from configs.logger import catch_error, print_info_log

MINIMUM_AUDIO_LENGTH_MS = 100  # 0.1 seconds in milliseconds


def speech_to_text(file_path: str, project_id: str, show_logs: bool = False) -> Tuple[List[TextSegment], int]:
    """Convert the audio content of file into text."""

    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")

        file = Path(file_path)
        file_format = file.suffix.replace('.', '')  # Strip the dot from the suffix

        # Extract Audio from Video
        audio_segment = AudioSegment.from_file(file_path, format=file_format)
        audio_len_in_seconds = len(audio_segment) // 1000

        # Determine the 1-minute Mark
        one_minute_in_ms = 1 * 60 * 1000

        # Initialize an Empty Transcript parts
        transcript_parts: List[TextSegment] = []

        # Loop Through 10-minute Segments
        elapsed_time = 0  # in milliseconds

        if show_logs:
            print_info_log(
                tag=LogTag.SPEECH_TO_TEXT,
                message=f"Converting speech to text of {file_path}"
            )

        for start_time in range(0, len(audio_segment), one_minute_in_ms):
            end_time = min(len(audio_segment), start_time + one_minute_in_ms)
            current_segment = audio_segment[start_time:end_time]

            # Check if segment length is at least 0.1 seconds - Whisper won't accept small files
            if len(current_segment) < MINIMUM_AUDIO_LENGTH_MS:
                continue

            # Use a temporary file to avoid overwriting conflicts
            with tempfile.NamedTemporaryFile(
                dir=PROCESSING_FILES_DIR_PATH,
                suffix=".wav",
                delete=True
            ) as temp_file:
                current_segment.export(temp_file.name, format="wav")

                # Use OpenAI's Whisper ASR to transcribe
                json_response = send_request_to_whisper_endpoint(
                    temp_file_name=temp_file.name,
                    show_logs=show_logs
                )

                # Adjust the timestamps by adding the elapsed_time
                for chunk in json_response['chunks']:
                    # Convert milliseconds to seconds
                    chunk['timestamp'][0] += elapsed_time / 1000
                    chunk['timestamp'][1] += elapsed_time / 1000
                    segment = {
                        "original_timestamp": tuple(chunk['timestamp']),
                        "text": chunk['text']
                    }

                    # Add chunk to transcript parts as TextSegment
                    transcript_parts.append(
                        TextSegment(**segment)
                    )

            # Update the elapsed_time
            elapsed_time += one_minute_in_ms

        return transcript_parts, audio_len_in_seconds

    except ValueError as ve:
        catch_error(
            tag=LogTag.SPEECH_TO_TEXT,
            error=ve,
            project_id=project_id
        )


if __name__ == "__main__":
    test_project_id = "07fsfECkwma6fVTDyqQf"
    test_file_path = f"{PROCESSING_FILES_DIR_PATH}/{test_project_id}.mp4"
    test_transcript_parts, test_used_tokens_in_seconds = speech_to_text(
        file_path=test_file_path,
        project_id=test_project_id,
        show_logs=True
    )
    print(test_transcript_parts)
    print(test_used_tokens_in_seconds)
