import time
from datetime import datetime

import requests
from requests.exceptions import SSLError

from configs.env import WHISPER_BEARER_TOKEN, ENDPOINT_WHISPER_API_URL
from configs.logger import print_info_log, catch_error
from constants.log_tags import LogTag

headers = {
    "Authorization": f"Bearer {WHISPER_BEARER_TOKEN}",
    "Content-Type": "audio/m4a"
}

DELAY_TO_REPEAT_REQUEST_IN_SECONDS = 3 * 60
DELAY_FOR_UNKNOWN_ERRORS_IN_SECONDS = 5


def send_request_to_whisper_endpoint(temp_file_name: str, show_logs: bool):
    try:
        with open(temp_file_name, "rb") as f:
            data = f.read()

        if show_logs:
            print_info_log(
                tag=LogTag.WHISPER_ENDPOINT_REQUEST,
                message=f"Sending request to Whisper endpoint..."
            )

        request_time = datetime.now()
        response = requests.post(ENDPOINT_WHISPER_API_URL, headers=headers, data=data)
        response_time = datetime.now()
        time_difference = response_time - request_time

        if show_logs:
            print_info_log(
                tag=LogTag.WHISPER_ENDPOINT_RESPONSE,
                message=f"Response time is {time_difference}"
            )

        if not response.ok:
            # If Whisper endpoint is scaled to zero (is sleeping)
            if response.status_code == 502:
                # Wait while endpoint started
                if show_logs:
                    print_info_log(
                        tag=LogTag.WHISPER_ENDPOINT_RESPONSE,
                        message=f"Whisper endpoint is scaled to zero (is sleeping)."
                    )
                    print_info_log(
                        tag=LogTag.WHISPER_ENDPOINT_RESPONSE,
                        message=f"Wait {DELAY_TO_REPEAT_REQUEST_IN_SECONDS} seconds to repeat..."
                    )
                time.sleep(DELAY_TO_REPEAT_REQUEST_IN_SECONDS)
                if show_logs:
                    print_info_log(
                        tag=LogTag.WHISPER_ENDPOINT_RESPONSE,
                        message=f"Trying to send request to Whisper endpoint again..."
                    )
                return send_request_to_whisper_endpoint(
                    temp_file_name=temp_file_name,
                    show_logs=show_logs
                )

            # Some other error with Whisper endpoint
            else:
                catch_error(
                    tag=LogTag.WHISPER_ENDPOINT_RESPONSE,
                    error=Exception(f"Whisper API Error ({response.status_code}): {response.text}")
                )

        if show_logs:
            print_info_log(
                tag=LogTag.WHISPER_ENDPOINT_RESPONSE,
                message="Sending request completed."
            )
        return response.json()

    except SSLError as se:
        print_info_log(
            tag=LogTag.WHISPER_ENDPOINT_RESPONSE,
            message=f"Connection SSLError: {str(se)}"
        )
        print_info_log(
            tag=LogTag.WHISPER_ENDPOINT_REQUEST,
            message=f"Wait {DELAY_TO_REPEAT_REQUEST_IN_SECONDS} seconds to repeat..."
        )
        time.sleep(DELAY_TO_REPEAT_REQUEST_IN_SECONDS)
        print_info_log(
            tag=LogTag.WHISPER_ENDPOINT_REQUEST,
            message=f"Trying to send request to Whisper endpoint again..."
        )
        return send_request_to_whisper_endpoint(
            temp_file_name=temp_file_name,
            show_logs=show_logs
        )

    except ConnectionResetError as cre:
        # Try again because something went wrong
        print_info_log(
            tag=LogTag.WHISPER_ENDPOINT_RESPONSE,
            message=f"ConnectionResetError: {str(cre)}"
        )
        print_info_log(
            tag=LogTag.WHISPER_ENDPOINT_RESPONSE,
            message="Wait {DELAY_FOR_UNKNOWN_ERRORS_IN_SECONDS} seconds to repeat..."
        )
        time.sleep(DELAY_FOR_UNKNOWN_ERRORS_IN_SECONDS)
        print_info_log(
            tag=LogTag.WHISPER_ENDPOINT_RESPONSE,
            message="Trying to send request to Whisper endpoint again..."
        )
        return send_request_to_whisper_endpoint(
            temp_file_name=temp_file_name,
            show_logs=show_logs
        )
