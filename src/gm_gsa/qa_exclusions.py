"""QA test-lead exclusion, enforced wherever WhatConverts leads feed a report or upload.

Rules live in clients/<slug>/client.yaml under ``qa_exclusions``. A lead is QA when ANY of
these match:

* its WhatConverts lead id is listed in ``known_qa_leads``;
* an email field equals a QA identity email (case-insensitive);
* a phone field matches a QA identity phone, including the form of it that a US input mask
  produces from an international number (first ten national digits);
* any submitted field contains the label marker (dash style and case ignored).

The module never prints lead contents. Callers get the kept leads plus a count and the ids
that were dropped, so a report can state exactly what it excluded.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from gm_gsa.config import load_yaml

# Submitted / call-level fields only. contact_* fields are WhatConverts contact enrichment
# and can carry a QA value onto a lead that nobody documented as a test.
EMAIL_FIELDS = ("email_address",)
PHONE_FIELDS = ("phone_number", "caller_number")
_DASHES = re.compile(r"[‐-―−-]+")


def _digits(value: Any) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def _norm_text(value: Any) -> str:
    return _DASHES.sub("-", str(value or "")).lower()


@dataclass
class QARules:
    emails: set[str] = field(default_factory=set)
    phone_variants: set[str] = field(default_factory=set)
    marker: str = ""
    lead_ids: set[str] = field(default_factory=set)

    @classmethod
    def from_client_yaml(cls, path: str | Path) -> "QARules":
        block = (load_yaml(path) or {}).get("qa_exclusions") or {}
        rules = cls(marker=_norm_text(block.get("label_marker", "")).strip())
        for ident in block.get("identities") or []:
            if ident.get("email"):
                rules.emails.add(str(ident["email"]).strip().lower())
            d = _digits(ident.get("phone_e164"))
            if d:
                rules.phone_variants.add(d)
                national = d[1:] if d.startswith("1") and len(d) == 11 else d
                rules.phone_variants.add(national[-10:])
                rules.phone_variants.add(national[:10])
                # an international number typed into a US mask keeps its first ten digits
                if not d.startswith("1"):
                    rules.phone_variants.add(d[:10])
        for row in block.get("known_qa_leads") or []:
            if row.get("whatconverts_lead_id"):
                rules.lead_ids.add(str(row["whatconverts_lead_id"]))
        return rules

    def reason(self, lead: dict[str, Any]) -> str | None:
        if str(lead.get("lead_id")) in self.lead_ids:
            return "known_qa_lead_id"
        for f in EMAIL_FIELDS:
            if str(lead.get(f) or "").strip().lower() in self.emails and lead.get(f):
                return "qa_email"
        for f in PHONE_FIELDS:
            d = _digits(lead.get(f))
            if d and (d in self.phone_variants or d[-10:] in self.phone_variants):
                return "qa_phone"
        extra = lead.get("additional_fields") or {}
        values: Iterable[Any] = extra.values() if isinstance(extra, dict) else extra
        for v in values:
            text = _norm_text(v)
            if self.marker and self.marker in text:
                return "qa_marker"
            d = _digits(v)
            if len(d) >= 10 and (d in self.phone_variants or d[-10:] in self.phone_variants):
                return "qa_phone"
            if str(v or "").strip().lower() in self.emails:
                return "qa_email"
        return None


def split_qa(leads: Iterable[dict[str, Any]], rules: QARules):
    """Return (kept, excluded) where excluded is a list of (lead_id, reason)."""
    kept, excluded = [], []
    for lead in leads:
        why = rules.reason(lead)
        if why:
            excluded.append((str(lead.get("lead_id")), why))
        else:
            kept.append(lead)
    return kept, excluded
