from datetime import datetime

import requests

from configs.env import STRIPE_SECRET_KEY
from configs.logger import catch_error

stripe_api_exception = Exception("Error while sending usage record to Stripe API")

SEND_USAGE_RECORD_URL = "https://api.stripe.com/v1/subscription_items/{subscription_item_id}/usage_records"


def send_usage_record(subscription_item_id: str, used_minutes_count: int, project_id: str):
    try:
        print(f"(send_usage_record) Used seconds count for this project - {used_minutes_count}")

        request_url = SEND_USAGE_RECORD_URL.format(
            subscription_item_id=subscription_item_id
        )

        now_timestamp = int(datetime.now().timestamp())
        usage_record_data = {
            "quantity": used_minutes_count,
            "timestamp": now_timestamp,
        }
        auth_with_token = (STRIPE_SECRET_KEY, "")

        response = requests.post(
            url=request_url,
            data=usage_record_data,
            auth=auth_with_token
        )

        if not response.ok:
            catch_error(
                tag="send_usage_record",
                error=stripe_api_exception,
                project_id=project_id
            )
            raise stripe_api_exception

        return response.content
    except Exception as e:
        catch_error(
            tag="send_usage_record",
            error=e,
            project_id=project_id
        )
        raise stripe_api_exception
