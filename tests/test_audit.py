from mailpilot.audit import normalize_message, summary, list_ids


def test_normalize():
    m = {"id": "x", "internalDate": "1735689600000", "payload": {"headers": [
        {"name": "From", "value": "Alice <ALICE@example.com>"},
        {"name": "Subject", "value": "Hello"}]}, "labelIds": ["INBOX", "UNREAD"]}
    r = normalize_message(m)
    assert r["sender"] == "alice@example.com"
    assert r["subject"] == "Hello"
    assert r["year"] == 2025
    assert summary([r])["unread"] == 1


def test_empty_summary():
    assert summary([])["analyzed"] == 0
    assert summary([])["top_senders"] == []


def test_invalid_limit():
    import pytest
    with pytest.raises(ValueError):
        list_ids(None, 0)
