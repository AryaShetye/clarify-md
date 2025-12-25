"""Firebase Authentication integration for CLARIFY.MD.

This module provides an OPTIONAL integration with Firebase Auth to
identify the doctor using the system. It uses the **REST API** so
there is no hard dependency on additional SDKs.

Design constraints:
- If FIREBASE_API_KEY is not set, the app runs in demo mode with a
  local doctor identity (no login required).
- Doctors are identified by their Firebase `localId` (UID) and email,
  which can be used to separate dashboard storage per doctor.

NOTE: This module does NOT store or log passwords. It only forwards
credentials to the Firebase Auth endpoint over HTTPS.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import os
import requests

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")


@dataclass
class FirebaseUser:
    uid: str
    email: str
    id_token: str


class FirebaseAuthClient:
    """Thin REST client for Firebase Authentication (email/password).

    This is intentionally minimal: only sign-in is implemented. In a
    real deployment you may wish to add sign-up or password reset
    flows, but those are out of scope for the CLARIFY.MD demo.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "https://identitytoolkit.googleapis.com/v1"

    def sign_in_with_email_and_password(self, email: str, password: str) -> FirebaseUser:
        url = f"{self.base_url}/accounts:signInWithPassword?key={self.api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }
        resp = requests.post(url, json=payload, timeout=10)
        if not resp.ok:
            try:
                data = resp.json()
                message = data.get("error", {}).get("message", resp.text)
            except Exception:
                message = resp.text
            raise RuntimeError(f"Firebase sign-in failed: {message}")

        data = resp.json()
        return FirebaseUser(uid=data["localId"], email=data["email"], id_token=data["idToken"]) 


def get_firebase_client() -> Optional[FirebaseAuthClient]:
    """Return a FirebaseAuthClient if FIREBASE_API_KEY is configured.

    If the API key is missing, returns None so the app can run in
    demo mode without authentication.
    """
    

    if not FIREBASE_API_KEY:
        return None
    return FirebaseAuthClient(FIREBASE_API_KEY)
