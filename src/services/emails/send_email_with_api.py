import requests

from configs.env import SEND_EMAIL_URL
from models.emailTemplates import EmailTemplate


def send_email_with_api(user_email: str, email_template: EmailTemplate):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "userEmail": user_email,
        "emailTemplate": email_template.value,
    }

    response = requests.post(SEND_EMAIL_URL, headers=headers, json=payload)

    if not response.ok:
        raise Exception(
            f"Email {email_template} sending failed with status {response.status_code}. Details: {response.text}"
        )


if __name__ == "__main__":
    test_user_email = "sakh.alexandr@gmail.com"
    test_email_template = EmailTemplate.SuccessfulProjectCompletion.value
    send_email_with_api(
        user_email=test_user_email,
        email_template=test_email_template
    )
