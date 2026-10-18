"""Read private local audit JSON; write private local triage suggestions only."""
import argparse
import json
from pathlib import Path
from collections import Counter
from .classifier import classify_records


def triage_account(root: Path, account: str) -> tuple[Path, int]:
    if account not in {'account1', 'account2'}:
        raise ValueError('Unknown account')
    path = root / 'secrets' / f'audit_{account}.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    records = classify_records(data['records'])
    report = {'account': data.get('account', account), 'sample_size': len(records),
              'categories': dict(Counter(r['category'] for r in records)), 'records': records,
              'mode': 'read-only; suggestions only; no email deletion, archive or labels applied'}
    dest = root / 'secrets' / f'triage_{account}.json'
    dest.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    return dest, len(records)


def main():
    parser = argparse.ArgumentParser(description='Classify local Gmail audit files without modifying Gmail')
    parser.add_argument('--account', choices=['account1','account2','both'], default='both')
    args = parser.parse_args()
    for account in (['account1','account2'] if args.account == 'both' else [args.account]):
        try:
            dest, count = triage_account(Path.cwd(), account)
            print(f'{account}: classified {count} sampled messages -> {dest}')
        except FileNotFoundError:
            print(f'{account}: no local audit found. Run mailpilot.cli first.')

if __name__ == '__main__':
    main()
