"""Per-account OAuth credentials, stored only on the user's machine."""
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_service(account: str, client_file: Path, secrets_dir: Path):
    if account not in {"account1", "account2"}:
        raise ValueError("account must be account1 or account2")
    if not client_file.is_file():
        raise FileNotFoundError(f"OAuth client JSON not found: {client_file}")
    secrets_dir.mkdir(parents=True, exist_ok=True)
    token_file = secrets_dir / f"token_{account}.json"
    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        token_file.write_text(creds.to_json(), encoding="utf-8")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)
