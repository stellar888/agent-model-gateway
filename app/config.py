"""Application configuration helpers and service factories."""

import os
from pathlib import Path

from app.gateway.registry import ProviderRegistry, load_models, load_profiles
from app.gateway.router import CapabilityRouter
from app.gateway.service import ModelGateway
from app.providers.fake_provider import FakeProvider
from app.providers.openai_provider import OpenAIProvider
from app.runtime.runner import AgentRunner

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_env_file(path: Path | None = None) -> None:
    """Load a small .env file without overriding existing environment variables."""
    env_path = path or PROJECT_ROOT / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def openai_enabled() -> bool:
    """Return whether the real OpenAI provider should be registered."""
    load_env_file()
    explicit_setting = os.getenv("AMG_ENABLE_OPENAI")
    if explicit_setting is not None:
        return explicit_setting.lower() in {"1", "true", "yes", "on"}
    return bool(os.getenv("OPENAI_API_KEY"))


def build_provider_registry(include_openai: bool | None = None) -> ProviderRegistry:
    """Build the provider registry used by demos and API endpoints."""
    load_env_file()
    should_include_openai = openai_enabled() if include_openai is None else include_openai
    providers = ProviderRegistry({"fake": FakeProvider()})
    if should_include_openai:
        providers.register("openai", OpenAIProvider())
    return providers


def build_gateway(
    models_path: Path | None = None,
    profiles_path: Path | None = None,
    include_openai: bool | None = None,
) -> ModelGateway:
    """Build a gateway from local YAML configuration."""
    providers = build_provider_registry(include_openai=include_openai)
    models = load_models(models_path or PROJECT_ROOT / "config/models.yaml")
    profiles = load_profiles(profiles_path or PROJECT_ROOT / "config/model-profiles.yaml")
    router = CapabilityRouter(profiles, models, providers)
    return ModelGateway(router, providers)


def build_runner(include_openai: bool | None = None) -> AgentRunner:
    """Build an agent runner backed by the configured model gateway."""
    return AgentRunner(build_gateway(include_openai=include_openai))
