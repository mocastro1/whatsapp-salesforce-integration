"""
Phone matcher: normalize phone numbers and lookup candidates in Salesforce (or simulate).
"""
from typing import List, Dict, Optional
import os

try:
    import phonenumbers
except ImportError:
    phonenumbers = None


def normalize_phone(raw_phone: str, default_region: str = "BR") -> Optional[str]:
    """Normalize phone to E.164 using phonenumbers. Returns None if cannot parse."""
    if not raw_phone:
        return None

    # Quick cleanup
    p = raw_phone.strip()
    # Remove common delimiters
    p = p.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")

    if phonenumbers is None:
        # phonenumbers not installed; return raw cleaned
        return p

    try:
        parsed = phonenumbers.parse(p, default_region)
        if not phonenumbers.is_valid_number(parsed):
            return None
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return None


def lookup_salesforce_by_phone(sf_conn, e164_phone: str) -> List[Dict]:
    """Lookup contacts/leads in Salesforce by exact phone (E.164).

    If sf_conn is None or not connected, return empty list.
    Returns list of candidate dicts with keys: Id, Name, Email, Phone, MobilePhone, RecordType (Contact/Lead)
    """
    candidates = []
    if not e164_phone:
        return candidates

    # If simple-salesforce is available and sf_conn is provided, query Salesforce
    try:
        if sf_conn and getattr(sf_conn, 'sf', None):
            sf = sf_conn.sf
            # Query Contacts
            q_contacts = (
                "SELECT Id, Name, Email, Phone, MobilePhone FROM Contact "
                f"WHERE Phone = '{e164_phone}' OR MobilePhone = '{e164_phone}' LIMIT 50"
            )
            res_c = sf.query(q_contacts)
            for r in res_c.get('records', []):
                candidates.append({
                    'Id': r.get('Id'),
                    'Name': r.get('Name'),
                    'Email': r.get('Email'),
                    'Phone': r.get('Phone'),
                    'MobilePhone': r.get('MobilePhone'),
                    'RecordType': 'Contact'
                })

            # Query Leads
            q_leads = (
                "SELECT Id, Name, Company, Phone, Email FROM Lead "
                f"WHERE Phone = '{e164_phone}' LIMIT 50"
            )
            res_l = sf.query(q_leads)
            for r in res_l.get('records', []):
                candidates.append({
                    'Id': r.get('Id'),
                    'Name': r.get('Name'),
                    'Company': r.get('Company'),
                    'Email': r.get('Email'),
                    'Phone': r.get('Phone'),
                    'RecordType': 'Lead'
                })

            return candidates
    except Exception:
        # On any SF error, fall through to empty list
        return []

    # If no Salesforce connection, try to simulate by scanning outputs/ for names (optional)
    outputs_dir = os.path.join(os.getcwd(), 'outputs')
    if os.path.exists(outputs_dir):
        # No reliable mapping available; return empty to force fallback
        return []

    return candidates


def rank_candidates_by_name(candidates: List[Dict], name_hint: Optional[str]) -> List[Dict]:
    """Rank candidate list by fuzzy match against name_hint. Adds a 'score' key to each candidate.

    Uses rapidfuzz if available; otherwise returns original order with score 0.
    """
    try:
        from rapidfuzz import fuzz
    except Exception:
        # rapidfuzz not available
        for c in candidates:
            c['score'] = 0.0
        return candidates

    if not name_hint:
        for c in candidates:
            c['score'] = 0.0
        return candidates

    ranked = []
    for c in candidates:
        candidate_name = c.get('Name') or c.get('Company') or ''
        score = fuzz.token_set_ratio(name_hint, candidate_name) / 100.0
        c['score'] = round(score, 3)
        ranked.append(c)

    ranked.sort(key=lambda x: x.get('score', 0), reverse=True)
    return ranked
