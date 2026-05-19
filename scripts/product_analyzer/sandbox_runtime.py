"""Cua sandbox runtime context for batch workers.

Does not create sandboxes itself. Describes the contract passed to each Claude
worker so it can create and drive its own sandbox via the Cua Sandbox SDK.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

SandboxMode = Literal["local", "cloud"]

SANDBOX_IMAGES = {"auto", "linux", "macos", "windows"}
_NO_PROXY_HOSTS = "127.0.0.1,localhost"


@dataclass(frozen=True)
class SandboxContext:
    image: str
    mode: SandboxMode
    local: bool
    android_enabled: bool = True
    api_key: str | None = None

    @property
    def runtime(self) -> str:
        return "sandbox-local" if self.local else "sandbox-cloud"

    def env(self) -> dict[str, str]:
        out: dict[str, str] = {
            "ANALYZER_RUNTIME": self.runtime,
            "ANALYZER_SANDBOX_IMAGE": self.image,
            "ANALYZER_SANDBOX_LOCAL": "1" if self.local else "0",
            "ANALYZER_SANDBOX_MODE": self.mode,
            "ANALYZER_ANDROID_ENABLED": "1" if self.android_enabled else "0",
        }
        if self.local:
            out.update(_local_no_proxy_env())
        elif self.api_key:
            out["CUA_API_KEY"] = self.api_key
        return out


def _local_no_proxy_env() -> dict[str, str]:
    """Bypass system HTTP proxies for localhost Docker port probes (httpx)."""
    merged = _NO_PROXY_HOSTS
    for key in ("NO_PROXY", "no_proxy"):
        existing = os.environ.get(key, "").strip()
        if existing:
            merged = f"{merged},{existing}"
    return {"NO_PROXY": merged, "no_proxy": merged}


def normalize_sandbox_image(image: str | None) -> str:
    value = (image or "auto").strip().lower()
    if value not in SANDBOX_IMAGES:
        choices = ", ".join(sorted(SANDBOX_IMAGES))
        raise ValueError(f"unsupported sandbox image: {image!r}; choose one of {choices}")
    return value


def resolve_api_key(cli_key: str | None) -> str | None:
    if cli_key and cli_key.strip():
        return cli_key.strip()
    env_key = os.environ.get("CUA_API_KEY", "").strip()
    return env_key or None


def resolve_sandbox_mode(
    *,
    cli_sandbox: str | None,
    api_key: str | None,
    interactive: bool,
) -> SandboxMode:
    """Pick local vs cloud sandbox for batch mode.

    Priority:
    1. ``--sandbox cloud`` → cloud (caller must ensure API key)
    2. ``--sandbox local`` → local (even if CUA_API_KEY is set)
    3. API key present → cloud
    4. Interactive prompt, else default local
    """
    if cli_sandbox == "cloud":
        return "cloud"
    if cli_sandbox == "local":
        return "local"
    if interactive:
        return _prompt_sandbox_mode(api_key)
    if api_key:
        return "cloud"
    return "local"


def _prompt_sandbox_mode(api_key: str | None) -> SandboxMode:
    from .ui import prompt_str

    if api_key:
        use_cloud = prompt_str(
            "检测到 CUA_API_KEY,默认使用云端 sandbox。使用云端? [Y/n]: ",
            validate=lambda s: s.lower() in ("", "y", "yes", "n", "no"),
            allow_empty=True,
        )
        if use_cloud.lower() in ("n", "no"):
            return "local"
        return "cloud"

    choice = prompt_str(
        "Sandbox 运行环境 [1=本地 Docker/Lume, 2=云端 Cua Cloud, 默认 1]: ",
        validate=lambda s: s in ("", "1", "2"),
        allow_empty=True,
    )
    return "cloud" if choice == "2" else "local"


def build_sandbox_context(
    image: str | None,
    *,
    mode: SandboxMode,
    android_enabled: bool = True,
    api_key: str | None = None,
) -> SandboxContext:
    local = mode == "local"
    return SandboxContext(
        image=normalize_sandbox_image(image),
        mode=mode,
        local=local,
        android_enabled=android_enabled,
        api_key=api_key if not local else None,
    )
