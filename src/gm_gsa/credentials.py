from __future__ import annotations

import os
from typing import Any

from .config import ConfigurationError, load_dotenv_if_available, normalize_customer_id, required_env

GOOGLE_ADS_ENV_KEYS = [
    "GOOGLE_ADS_DEVELOPER_TOKEN",
    "GOOGLE_ADS_CLIENT_ID",
    "GOOGLE_ADS_CLIENT_SECRET",
    "GOOGLE_ADS_REFRESH_TOKEN",
    "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
]


def google_ads_config() -> dict[str, Any]:
    load_dotenv_if_available()
    values = required_env(GOOGLE_ADS_ENV_KEYS)
    return {
        "developer_token": values["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id": values["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": values["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": values["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": normalize_customer_id(
            values["GOOGLE_ADS_LOGIN_CUSTOMER_ID"]
        ),
        "use_proto_plus": True,
    }


def load_google_ads_client() -> Any:
    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError as exc:
        raise ConfigurationError(
            "The google-ads package is not installed. Run: "
            "python -m pip install -r requirements.txt"
        ) from exc
    return GoogleAdsClient.load_from_dict(google_ads_config())


def legacy_offline_upload_allowed() -> bool:
    return os.getenv("GOOGLE_ADS_LEGACY_OFFLINE_UPLOAD_ELIGIBLE", "").lower() == "true"

