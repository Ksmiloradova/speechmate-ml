from datetime import datetime

import requests

from configs.logger import print_info_log
from constants.log_tags import LogTag
from configs.env import UPDATE_PROJECT_URL


def update_project_status_and_translated_link_by_id(
    project_id: str,
    status: str,
    translated_file_link: str,
    show_logs: bool = False
):
    project_fields_to_update = {
        "id": project_id,
        "status": status,
        "translatedFileLink": translated_file_link
    }

    if show_logs:
        print_info_log(
            tag=LogTag.UPDATE_PROJECT,
            message=f"Project fields to update: {project_fields_to_update}"
        )

    request_time = datetime.now()
    response = requests.post(
        UPDATE_PROJECT_URL,
        project_fields_to_update,
    )
    response_time = datetime.now()
    time_difference = response_time - request_time

    if show_logs:
        print_info_log(
            tag=LogTag.UPDATE_PROJECT,
            message=f"Response time is {time_difference}"
        )

    if not response.ok:
        raise Exception(f"Firebase Cloud Function Error ({response.status_code}): {response.text}")
