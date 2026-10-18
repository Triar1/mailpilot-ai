"""Conservative, deterministic, explainable email triage suggestions.

This is a baseline classifier, NOT an LLM. No Gmail write calls are made.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from email.utils import parseaddr
import re

CATEGORIES = ('finance', 'administrative', 'security', 'personal', 'work_studies', 'travel_events', 'shopping', 'newsletter', 'promotion', 'other')
PROTECTED = {'finance', 'administrative', 'security', 'personal'}
PATTERNS = [
    ('security', r'password|mot de passe|security alert|alerte de s.curit.|verification code|code de v.rification|connexion inhabituelle|2fa|authentification'),
    ('finance', r'facture|invoice|receipt|re.u|quittance|imp.t|tax|payment|paiement|remboursement|bank|banque|relev. bancaire'),
    ('administrative', r'contrat|attestation|assurance|administration|pr.fecture|visa|carte vitale|identit.|document officiel'),
    ('travel_events', r'billet|ticket|r.servation|booking|boarding|train|flight|vol |concert|event|.v.nement|invitation'),
    ('work_studies', r'universit.|university|school|.cole|stage|internship|recrutement|interview|entretien|cours|assignment|project|projet'),
    ('shopping', r'commande|order confirmation|colis|livraison|delivery|shipping|exp.di.'),
    ('newsletter', r'newsletter|digest|weekly update|lettre d.information|unsubscribe|d.sabonner'),
    ('promotion', r'promo|promotion|soldes|discount|offre sp.ciale|black friday|% off|coupon|deal'),
]


def classify(record: dict) -> dict:
    """Classify from sender, subject and Gmail labels only; no message body."""
    sender = str(record.get('sender') or '').lower()
    subject = str(record.get('subject') or '')
    labels = set(record.get('labels') or [])
    text = f'{sender} {subject}'.lower()
    matches = [(category, pattern) for category, pattern in PATTERNS if re.search(pattern, text, flags=re.IGNORECASE)]
    # Multiple distinct categories are ambiguous, especially around receipts/promotions.
    distinct = list(dict.fromkeys(cat for cat, _ in matches))
    if len(distinct) > 1:
        category, confidence, reason = 'other', 0.40, f'Ambiguous keywords: {", ".join(distinct)}'
    elif distinct:
        category, confidence, reason = distinct[0], 0.78, 'Keyword match in sender or subject'
    elif 'CATEGORY_PROMOTIONS' in labels:
        category, confidence, reason = 'promotion', 0.65, 'Gmail Promotions category'
    elif 'CATEGORY_SOCIAL' in labels:
        category, confidence, reason = 'newsletter', 0.55, 'Gmail Social category'
    elif 'CATEGORY_UPDATES' in labels:
        category, confidence, reason = 'other', 0.35, 'Gmail Updates category (insufficient evidence)'
    else:
        category, confidence, reason = 'other', 0.25, 'Insufficient metadata for reliable classification'
    if category in PROTECTED or category == 'other':
        action = 'review' if category == 'other' else 'keep'
    elif category in {'promotion', 'newsletter'}:
        action = 'review_for_cleanup'  # never automatically delete
    else:
        action = 'archive_candidate' if 'INBOX' in labels else 'keep'
    return {'category': category, 'confidence': confidence, 'suggested_action': action,
            'reason': reason, 'needs_review': confidence < 0.80}


def classify_records(records: list[dict]) -> list[dict]:
    return [{**record, **classify(record)} for record in records]
