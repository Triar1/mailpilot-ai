"""Fetch Gmail message metadata; never fetch message bodies or modify Gmail."""
from collections import Counter
from datetime import datetime, timezone
from email.utils import parseaddr


def headers_to_dict(headers):
    return {h.get("name", "").lower(): h.get("value", "") for h in headers}


def normalize_message(message):
    headers = headers_to_dict(message.get("payload", {}).get("headers", []))
    sender_name, sender_email = parseaddr(headers.get("from", ""))
    millis = int(message.get("internalDate", "0"))
    return {
        "id": message["id"],
        "thread_id": message.get("threadId", ""),
        "sender": sender_email.lower() or headers.get("from", "(unknown)"),
        "sender_name": sender_name,
        "subject": headers.get("subject", ""),
        "year": datetime.fromtimestamp(millis / 1000, tz=timezone.utc).year if millis else None,
        "labels": message.get("labelIds", []),
    }


def list_ids(service, max_messages=500, query=None):
    if max_messages < 1:
        raise ValueError("max_messages must be positive")
    result = []
    token = None
    while len(result) < max_messages:
        params = {"userId": "me", "maxResults": min(500, max_messages - len(result))}
        if token:
            params["pageToken"] = token
        if query:
            params["q"] = query
        page = service.users().messages().list(**params).execute()
        result.extend(page.get("messages", []))
        token = page.get("nextPageToken")
        if not token:
            break
    return result


def fetch_metadata(service, message_ids):
    records = []
    for item in message_ids:
        msg = service.users().messages().get(
            userId="me", id=item["id"], format="metadata",
            metadataHeaders=["From", "Subject"],
        ).execute()
        records.append(normalize_message(msg))
    return records


def summary(records):
    return {
        "analyzed": len(records),
        "top_senders": Counter(r["sender"] for r in records).most_common(20),
        "by_year": sorted(Counter(r["year"] for r in records if r["year"] is not None).items()),
        "in_inbox": sum("INBOX" in r["labels"] for r in records),
        "unread": sum("UNREAD" in r["labels"] for r in records),
    }
