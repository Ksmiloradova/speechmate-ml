import firebase_admin
from firebase_admin import credentials

from configs.env import CERTIFICATE_CONTENT


def init_firebase():
    cred = credentials.Certificate(CERTIFICATE_CONTENT)
    firebase_admin.initialize_app(cred)
