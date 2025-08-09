from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import auth, credentials
from firebase_admin.auth import UserRecord

class FirebaseAuthError(Exception):
    pass

class FirebaseAuth:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseAuth, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            try:
                # Initialize Firebase Admin SDK
                # Note: You'll need to provide the path to your Firebase credentials JSON file
                cred = credentials.Certificate("path/to/your/firebase-credentials.json")
                firebase_admin.initialize_app(cred)
                self._initialized = True
            except Exception as e:
                raise FirebaseAuthError(f"Failed to initialize Firebase: {str(e)}")

    async def verify_token(self, token: str) -> Dict[str, Any]:
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            raise FirebaseAuthError(f"Failed to verify token: {str(e)}")

    async def get_user(self, uid: str) -> Optional[UserRecord]:
        try:
            user = auth.get_user(uid)
            return user
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            raise FirebaseAuthError(f"Failed to get user: {str(e)}")
