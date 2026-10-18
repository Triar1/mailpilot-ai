# Architecture

```text
Gmail API (read-only OAuth)
          |
          v
Python metadata collector
          |
          v
Local JSON audit files (ignored: secrets/)
          |
          +--> Deterministic rule-based baseline (v0.2)
          |
          +--> Ollama localhost:11434 / qwen2.5:3b
                       |
                       v
                 Local semantic JSON
                       |
                       v
                 Streamlit dashboard
                       |
                       v
                 Human review JSON
```

The classifier only sends sender name, sender email and subject to the locally running Ollama service. No Gmail mutation scopes are requested. The Streamlit dashboard writes human annotations to local JSON files; it does not call Gmail write endpoints.

This release is an experiment in metadata classification, not an automated inbox-cleaning tool.
