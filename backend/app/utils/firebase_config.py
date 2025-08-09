from typing import Optional
import firebase_admin
from firebase_admin import credentials
from app.core.config import settings

class FirebaseConfig:
    _app: Optional[firebase_admin.App] = None

    @classmethod
    def get_app(cls) -> firebase_admin.App:
        if cls._app is None:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            cls._app = firebase_admin.initialize_app(cred)
        return cls._app

    @classmethod
    def get_credentials(cls) -> credentials.Certificate:
        return credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
