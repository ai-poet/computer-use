"""Local Cua sandbox runtime context for batch workers.

This module does not create sandboxes itself. It describes the runtime
contract passed to each Claude worker so the worker can create and drive its
own isolated local sandbox with the Cua Sandbox SDK.
"""

from __future__ import annotations

from dataclasses import dataclass


SANDBOX_IMAGES = {"auto", "linux", "macos", "windows"}


@dataclass(frozen=True)
class SandboxContext:
    image: str
    local: bool = True
    android_enabled: bool = True

    def env(self) -> dict[str, str]:
        return {
            "ANALYZER_RUNTIME": "sandbox-local",
            "ANALYZER_SANDBOX_IMAGE": self.image,
            "ANALYZER_SANDBOX_LOCAL": "1" if self.local else "0",
            "ANALYZER_ANDROID_ENABLED": "1" if self.android_enabled else "0",
        }


def normalize_sandbox_image(image: str | None) -> str:
    value = (image or "auto").strip().lower()
    if value not in SANDBOX_IMAGES:
        choices = ", ".join(sorted(SANDBOX_IMAGES))
        raise ValueError(f"unsupported sandbox image: {image!r}; choose one of {choices}")
    return value


def build_sandbox_context(
    image: str | None,
    *,
    android_enabled: bool = True,
) -> SandboxContext:
    return SandboxContext(
        image=normalize_sandbox_image(image),
        local=True,
        android_enabled=android_enabled,
    )
