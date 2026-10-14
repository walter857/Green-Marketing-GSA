"""Automatic review retrieval for landing pages.

The rule this encodes: an empty review placeholder is the last resort, not the first
response to a blocked Google interface. Google Business Profile is attempted first because
it is the strongest source; when it cannot be read, the client's own official website is a
legitimate fallback, and a strong general company review beats a placeholder.

What is never acceptable, at any stage: invented, paraphrased, combined, anonymous, or
competitor reviews, and reviewer names that were not displayed by the source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

SOURCE_GBP = "google_business_profile"
SOURCE_WEBSITE = "official_client_website"

#: Neutral fallback for the review card's third line. Callers should pass a client-specific
#: label; this module must not hard-code one client's wording.
DEFAULT_CUSTOMER_LABEL = "Verified Customer"

PLACEHOLDER = (
    "[REVIEW PENDING: supply an exact review and reviewer name from the verified Google "
    "Business Profile or the official client website. Do not substitute a third-party "
    "review.]"
)


class ReviewRetrievalError(RuntimeError):
    """Raised when a candidate review fails an integrity rule."""


@dataclass(frozen=True)
class Review:
    reviewer_name: str
    text: str
    source: str
    source_url: str
    retrieved_on: str
    star_rating: str | None = None
    service_relevant: bool = False

    def validate(self) -> None:
        if not self.reviewer_name.strip():
            raise ReviewRetrievalError("a review must carry the displayed reviewer name")
        if self.reviewer_name.strip().lower() in {"anonymous", "a google user", "customer"}:
            raise ReviewRetrievalError(f"anonymous reviewer {self.reviewer_name!r} is not usable")
        if not self.text.strip():
            raise ReviewRetrievalError("a review must carry its exact text")
        if not self.source_url.strip():
            raise ReviewRetrievalError("a review must record its source URL")


@dataclass
class RetrievalResult:
    reviews: list[Review] = field(default_factory=list)
    source_used: str | None = None
    attempts: list[dict[str, Any]] = field(default_factory=list)

    @property
    def resolved(self) -> bool:
        return len(self.reviews) == 3

    def card_values(self, customer_label: str = DEFAULT_CUSTOMER_LABEL) -> list[dict[str, str]]:
        """Per-card values. Each card gets its own review; nothing is duplicated across.

        ``customer_label`` fills the template's third line. It must stay a neutral,
        client-appropriate label and must never carry a source URL, platform name, or any
        other provenance detail, which belong in the internal manifest instead.
        """
        if not self.resolved:
            return [{"text": PLACEHOLDER, "reviewer": PLACEHOLDER, "attribution": PLACEHOLDER}
                    for _ in range(3)]
        return [{"text": r.text, "reviewer": r.reviewer_name, "attribution": customer_label}
                for r in self.reviews]

    def provenance(self) -> list[dict[str, Any]]:
        """Internal record only. Never rendered into customer-facing copy."""
        return [
            {"reviewer_name": r.reviewer_name, "exact_text": r.text, "source": r.source,
             "source_url": r.source_url, "retrieved_on": r.retrieved_on,
             "star_rating": r.star_rating, "service_relevant": r.service_relevant}
            for r in self.reviews
        ]


def select_three(candidates: list[Review]) -> list[Review]:
    """Prefer service-relevant reviews, then fall back to strong general company reviews."""
    for candidate in candidates:
        candidate.validate()
    relevant = [c for c in candidates if c.service_relevant]
    general = [c for c in candidates if not c.service_relevant]
    chosen = (relevant + general)[:3]
    return chosen if len(chosen) == 3 else []


def retrieve_reviews(
    *,
    gbp_fetcher: Callable[[], list[Review]] | None = None,
    website_fetcher: Callable[[], list[Review]] | None = None,
    identity_confirmed: bool = True,
) -> RetrievalResult:
    """Try GBP first, then the official client website, then a placeholder.

    ``identity_confirmed`` gates the GBP source: a listing that has not been matched to the
    client must never contribute a review.
    """
    result = RetrievalResult()

    if gbp_fetcher is not None:
        if not identity_confirmed:
            result.attempts.append({"source": SOURCE_GBP, "outcome": "identity_not_confirmed"})
        else:
            try:
                chosen = select_three(gbp_fetcher())
                if chosen:
                    result.reviews = chosen
                    result.source_used = SOURCE_GBP
                    result.attempts.append({"source": SOURCE_GBP, "outcome": "resolved"})
                    return result
                result.attempts.append({"source": SOURCE_GBP, "outcome": "insufficient_reviews"})
            except Exception as exc:  # noqa: BLE001
                result.attempts.append({"source": SOURCE_GBP, "outcome": "unreachable",
                                        "detail": type(exc).__name__})
    else:
        result.attempts.append({"source": SOURCE_GBP, "outcome": "no_fetcher_configured"})

    if website_fetcher is not None:
        try:
            chosen = select_three(website_fetcher())
            if chosen:
                result.reviews = chosen
                result.source_used = SOURCE_WEBSITE
                result.attempts.append({"source": SOURCE_WEBSITE, "outcome": "resolved"})
                return result
            result.attempts.append({"source": SOURCE_WEBSITE, "outcome": "insufficient_reviews"})
        except Exception as exc:  # noqa: BLE001
            result.attempts.append({"source": SOURCE_WEBSITE, "outcome": "unreachable",
                                    "detail": type(exc).__name__})
    else:
        result.attempts.append({"source": SOURCE_WEBSITE, "outcome": "no_fetcher_configured"})

    return result
