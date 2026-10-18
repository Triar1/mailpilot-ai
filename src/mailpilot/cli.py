"""Explicit CLI entry point: local read-only audit."""
import argparse
import json
from pathlib import Path
from .auth import get_service
from .audit import list_ids, fetch_metadata, summary


def main():
    parser = argparse.ArgumentParser(description="MailPilot AI: read-only Gmail audit")
    parser.add_argument("--account", choices=["account1", "account2"], required=True)
    parser.add_argument("--limit", type=int, default=500, help="Max messages to analyze (default: 500)")
    parser.add_argument("--query", default=None, help="Optional Gmail search query")
    args = parser.parse_args()
    root = Path.cwd()
    client = root / "secrets" / "credentials.json"
    service = get_service(args.account, client, root / "secrets")
    email = service.users().getProfile(userId="me").execute().get("emailAddress")
    print(f"Authenticated as: {email} ({args.account})")
    print("Read-only mode: no emails will be changed.")
    ids = list_ids(service, max_messages=args.limit, query=args.query)
    records = fetch_metadata(service, ids)
    output = root / "secrets" / f"audit_{args.account}.json"
    output.write_text(json.dumps({"account": email, "summary": summary(records), "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Analyzed {len(records)} messages. Private local report: {output}")
    print("Note: this is a sample, not a complete mailbox census unless all messages were fetched.")


if __name__ == "__main__":
    main()
