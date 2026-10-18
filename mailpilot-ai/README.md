# MailPilot AI — Local Email Intelligence

**An experimental, privacy-first Gmail metadata classifier using Python, Ollama (Qwen 2.5), and Streamlit.**

> **Status:** v0.3 experimental release. This project explores email classification; it does not automatically organize, delete, or reply to messages.

## Why this project?

A simple rules-based inbox classifier struggled with messages from the same sender that had different purposes: a game-store receipt versus a promotional offer, or a train ticket versus a travel newsletter. MailPilot tests whether a locally hosted LLM can interpret message intent from the sender and subject more effectively.

## Features

- Read-only Gmail OAuth integration for two accounts.
- Local metadata extraction (sender, subject, year, Gmail labels).
- Rules-based baseline and Ollama-powered semantic classification.
- Streamlit dashboard with categories and human corrections.
- Local review storage and agreement metrics.
- No Gmail modifications and no cloud LLM API.

## Architecture

```text
Gmail (readonly) → Python metadata audit → Ollama (localhost)
                                            ↓
                                   Local classification JSON
                                            ↓
                                  Streamlit review dashboard
```

See [architecture](docs/architecture.md) and [privacy notes](docs/privacy.md).

## Experiment results

| Metric | Rules v0.2 | Ollama v0.3 |
|---|---:|---:|
| Messages analyzed | 1,000 | 1,000 |
| `other` messages | 594 | 94 |
| `other` rate | 59.4% | 9.4% |
| Reported model errors | Not measured | 11 |

**Important:** This measures *classification coverage*, not correctness. No representative, human-labeled accuracy study was completed. Technical failures may be included in `other`. The private dataset is not distributed.

See [experiment notes](docs/experiments.md).

## Setup (Windows / PowerShell)

Requirements: Python 3.12, [Ollama](https://ollama.com/download), Google Cloud Gmail API enabled, and OAuth desktop credentials.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -v
ollama pull qwen2.5:3b
```

Create `secrets/credentials.json` using your own Google Cloud OAuth desktop client. Add your own Google account(s) as OAuth test users if the consent screen is in Testing mode. Never commit the `secrets/` directory.

Read metadata (requires your own Gmail OAuth authorization):

```powershell
.\.venv\Scripts\python.exe -m mailpilot.cli --account account1 --limit 50
.\.venv\Scripts\python.exe -m mailpilot.semantic_cli --account account1 --limit 50
.\.venv\Scripts\python.exe -m streamlit run src/mailpilot/dashboard.py
```

To connect a second account, repeat the audit with `--account account2`, then classify with `--account both`.

**Note:** This is a local developer project, not a hosted public service. A sample of completely [fictional emails](examples/synthetic_emails.json) is provided for reference; the Gmail collector requires your own account to run.

## Limitations

- Only sender and subject are used for semantic inference; full conversational context is unavailable.
- Small local models can hallucinate or return incorrect categories.
- Review agreement on hand-picked messages is not an unbiased accuracy estimate.
- The original fixed-category taxonomy is not suitable for every message type.
- Ollama inference may be slow on CPU and occasionally fail.

## Future direction

The findings motivated a future **action-oriented inbox copilot**: identifying invitations, follow-ups, requests for documents, and suggested replies. These features are **not implemented** in this release.

## Security

The app requests only Gmail `gmail.readonly`; tokens, OAuth credentials, mailbox metadata, classifications, and reviews are stored locally under `secrets/`, which is Git-ignored. Do not deploy a dashboard containing real mailbox data publicly.

## License

[MIT](LICENSE)
