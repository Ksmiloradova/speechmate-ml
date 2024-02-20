import os
from datetime import datetime

from fastapi import APIRouter

from configs.logger import print_info_log, catch_error
from constants.files import PROCESSING_FILES_DIR_PATH
from constants.log_tags import LogTag
from models.file_type import FileType
from models.project import ProjectStatus
from services.firebase.firestore.project import update_project_status_and_translated_link_by_id
from services.firebase.firestore.user_tokens import update_user_tokens
from services.firebase.storage.download_blob import download_blob
from services.firebase.storage.upload_blob import upload_blob
from services.overlay.overlay_audio_to_video import overlay_audio_to_video
from services.speech_to_text.speech_to_text import speech_to_text
from services.text_to_speech.text_to_speech import text_to_speech
from services.translation.translate_text import translate_text
from utils.files import get_file_extension, get_file_type, get_file_dir, get_file_name

dub_router = APIRouter(tags=["DUB"])


@dub_router.get("/")
def generate(
    project_id: str,
    target_language: str,
    voice_id: int,
    original_file_location: str,
    organization_id: str,
    user_email: str,
):
    """
    Generates a dubbed version of the original video or audio file in the target language
    and update user's used tokens in seconds.

    :param project_id: The id of the processing project.
    :param target_language: The language in which the video will be dubbed.
    :param voice_id: The identifier of the voice to be used for dubbing.
    :param original_file_location: The location of the original video file in the cloud storage.
    :param organization_id: The unique identifier of the organization.
    :param user_email: The unique identifier of the organization.

    :return: Upload the dubbed video to Firebase Cloud Storage

    :Example:
    >>> generate(
    ...     project_id=f"07fsfECkwma6fVTDyqQf",
    ...     target_language="Russian",
    ...     voice_id=165,
    ...     original_file_location="z8Z5j71WbmhaioUHDHh5KrBqEO13/07fsfECkwma6fVTDyqQf/test-video-1min.mp4",
    ...     organization_id="ZXIFYVhPAMql66Vg5f5Q"
    ...     user_email="your@email.com"
    ... )
    Check if project_id, organization_id and original_file_location exist in Firebase
    """

    try:
        start_time = datetime.now()
        print_info_log(
            tag=LogTag.MAIN,
            message=f"Job Started! Processing project with id {project_id}..."
        )

        """Download project file from Cloud Storage"""

        print_info_log(
            tag=LogTag.MAIN,
            message="Downloading file from Cloud Storage..."
        )

        source_blob_path = original_file_location
        # Extract extension from the original file location
        original_file_extension = get_file_extension(original_file_location)
        # Combine project_id with the extracted extension
        local_original_file_path = f"{PROCESSING_FILES_DIR_PATH}/{project_id}.{original_file_extension}"
        # Download file
        download_blob(
            source_blob_path=source_blob_path,
            destination_file_path=local_original_file_path,
            project_id=project_id,
            show_logs=True
        )

        print_info_log(
            tag=LogTag.MAIN,
            message="Downloading completed."
        )

        """Change project status to "translating"""

        print_info_log(
            tag=LogTag.MAIN,
            message="Updating project status to 'translating'..."
        )

        update_project_status_and_translated_link_by_id(
            project_id=project_id,
            status=ProjectStatus.TRANSLATING.value,
            translated_file_link="",
            show_logs=True
        )

        print_info_log(
            tag=LogTag.MAIN,
            message="Project status updated."
        )

        """Convert file speech to text"""

        print_info_log(
            tag=LogTag.MAIN,
            message="Starting speech to text..."
        )

        original_text_segments, used_tokens_in_seconds = speech_to_text(
            file_path=local_original_file_path,
            project_id=project_id,
            show_logs=True
        )

        print_info_log(
            tag=LogTag.MAIN,
            message="Speech to text completed."
        )

        """Translate text"""

        print_info_log(
            tag=LogTag.MAIN,
            message="Translating text..."
        )

        translated_text_segments = translate_text(
            text_segments=original_text_segments,
            language=target_language,
            project_id=project_id,
            show_logs=True
        )

        print_info_log(
            tag=LogTag.MAIN,
            message="Translation completed."
        )

        # """Detect gender of the voice"""
        #
        # gender = voice_gender_detection(video_path)

        """Generate audio from translated text"""

        print_info_log(
            tag=LogTag.MAIN,
            message="Text to speech..."
        )

        local_translated_audio_path, translated_text_segments_with_audio_timestamp = text_to_speech(
            text_segments=translated_text_segments,
            voice_id=voice_id,
            project_id=project_id,
            show_logs=True
        )

        print_info_log(
            tag=LogTag.MAIN,
            message="Text to speech completed."
        )

        """Overlay audio to video"""

        processed_project_is_video = get_file_type(local_original_file_path) == FileType.VIDEO
        # Overlay audio if project is video
        if processed_project_is_video:
            print_info_log(
                tag=LogTag.MAIN,
                message="Overlay audio to video..."
            )

            local_translated_file_path = overlay_audio_to_video(
                video_path=local_original_file_path,
                audio_path=local_translated_audio_path,
                text_segments_with_audio_timestamp=translated_text_segments_with_audio_timestamp,
                project_id=project_id,
                silent_original_audio=False,
                show_logs=True
            )

            print_info_log(
                tag=LogTag.MAIN,
                message="Overlay audio completed."
            )

        # Unless return translated audio
        else:
            local_translated_file_path = local_translated_audio_path

        """Upload audio to cloud storage"""

        # Extract the path and filename from the original_file_location
        original_file_dir = get_file_dir(original_file_location)
        original_file_name = get_file_name(original_file_location)
        original_file_suffix = get_file_extension(original_file_location)

        # Create the destination blob name with '-translated' appended to the filename
        destination_blob_name = f"{original_file_dir}/{original_file_name}-translated.{original_file_suffix}"

        print_info_log(
            tag=LogTag.MAIN,
            message="Uploading translated file to cloud storage..."
        )

        file_public_link = upload_blob(
            source_file_name=local_translated_file_path,
            destination_blob_name=destination_blob_name,
            project_id=project_id,
            show_logs=True
        )

        print_info_log(
            tag=LogTag.MAIN,
            message=f"File uploaded to cloud storage, destination_blob_name - {destination_blob_name}"
        )

        """Remove all processed files"""

        print_info_log(
            tag=LogTag.MAIN,
            message="Removing all project processed files..."
        )

        # Remove original file
        os.remove(local_original_file_path)
        # Remove translated file
        if processed_project_is_video:
            os.remove(local_translated_file_path)
            os.remove(local_translated_audio_path)
        else:
            os.remove(local_translated_file_path)

        print_info_log(
            tag=LogTag.MAIN,
            message="Removing completed."
        )

        """Change project status to "translated"""

        print_info_log(
            tag=LogTag.MAIN,
            message="Updating project status to 'translated'..."
        )

        update_project_status_and_translated_link_by_id(
            project_id=project_id,
            status=ProjectStatus.TRANSLATED.value,
            translated_file_link=file_public_link,
            show_logs=True
        )

        print_info_log(
            tag=LogTag.MAIN,
            message="Project status updated."
        )

        """Update user used tokens in seconds"""

        print_info_log(
            tag=LogTag.MAIN,
            message="Updating user used tokens..."
        )

        update_user_tokens(
            organization_id=organization_id,
            tokens_in_seconds=used_tokens_in_seconds,
            project_id=project_id
        )

        print_info_log(
            tag=LogTag.MAIN,
            message="User used tokens updated."
        )

        """Send email to user about successful project completion"""

        # print_info_log(
        #     tag=LogTag.MAIN,
        #     message="Sending email to user about successful project completion..."
        # )
        #
        # send_email_with_api(
        #     user_email=user_email,
        #     email_template=EmailTemplate.SuccessfulProjectCompletion,
        # )
        #
        # print_info_log(
        #     tag=LogTag.MAIN,
        #     message="Email was sent to user successfully."
        # )

        end_time = datetime.now()
        time_difference = end_time - start_time

        print_info_log(
            tag=LogTag.MAIN,
            message=f"Job Done! Project translation time: {time_difference}"
        )

        return {"status": "it is working!!!"}

    except Exception as e:
        catch_error(
            tag=LogTag.MAIN,
            error=e,
            project_id=project_id
        )


if __name__ == "__main__":
    test_user_id = "z8Z5j71WbmhaioUHDHh5KrBqEO13"
    test_project_id = "07fsfECkwma6fVTDyqQf"
    test_file_name = "test-video-1min.mp4"
    test_target_language = "Russian"
    test_voice_id = 165
    test_original_file_location = f"{test_user_id}/{test_project_id}/{test_file_name}"
    test_organization_id = "ZXIFYVhPAMql66Vg5f5Q"
    test_user_email = "your@email.com"
    generate(
        project_id=test_project_id,
        target_language=test_target_language,
        voice_id=test_voice_id,
        original_file_location=test_original_file_location,
        organization_id=test_organization_id,
        user_email=test_user_email
    )
