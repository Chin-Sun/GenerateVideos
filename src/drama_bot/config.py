"""Fail-closed configuration. Enabling calls is not budget authorization."""
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DRAMA_", extra="ignore")

    database_url: str = "sqlite:///./var/drama.db"
    asset_root: Path = Path("var/assets")
    paid_calls_enabled: bool = False
    paid_authorization_id: str | None = None
    max_paid_submissions: int = 0
    allowed_user_ids: tuple[str, ...] = ()
    allowed_tenant_ids: tuple[str, ...] = ()
    default_aspect_ratio: Literal["9:16", "16:9", "1:1"] = "9:16"
    ppapi_base_url: str = ""
    ppapi_api_key: SecretStr | None = None
    feishu_app_id: str | None = None
    feishu_app_secret: SecretStr | None = None
    feishu_verification_token: SecretStr | None = None
    feishu_encrypt_key: SecretStr | None = None
    local_api_token: SecretStr | None = None
    local_tenant_id: str | None = None
    local_user_id: str | None = None
    local_chat_id: str | None = None
    download_allowed_hosts: tuple[str, ...] = ()
    allow_unverified_preview: bool = False
