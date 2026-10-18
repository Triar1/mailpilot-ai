# Privacy and security

- Gmail OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.
- `secrets/` contains OAuth client credentials, access/refresh tokens, and mailbox-derived data. It is **excluded from Git**.
- Ollama inference is requested at `http://127.0.0.1:11434` and does not use a cloud LLM API.
- Only email metadata (sender and subject) is used for semantic classification.
- The application cannot send, archive, delete, or relabel Gmail messages.
- The sample emails in `examples/` are fictional and contain no user data.
- Do not deploy the dashboard publicly with private mailbox files.
- Inspect `git status` and `git diff --cached --name-only` before pushing.
- If a token or credential was ever committed, remove it from history and revoke/rotate it. `.gitignore` alone is insufficient.
