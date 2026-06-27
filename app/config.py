"""Application configuration helpers and service factories."""

from pathlib import Path

from app.gateway.registry import ProviderRegistry, load_models, load_profiles
from app.gateway.router import CapabilityRouter
from app.gateway.service import ModelGateway
from app.providers.fake_provider import FakeProvider
from app.providers.openai_provider import OpenAIProvider
from app.runtime.runner import AgentRunner

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_provider_registry(include_openai: bool = False) -> ProviderRegistry:
    """Build the provider registry used by demos and API endpoints."""
    providers = ProviderRegistry({"fake": FakeProvider()})
    if include_openai:
        providers.register("openai", OpenAIProvider())
    return providers


def build_gateway(
    models_path: Path | None = None,
    profiles_path: Path | None = None,
    include_openai: bool = False,
) -> ModelGateway:
    """Build a gateway from local YAML configuration."""
    providers = build_provider_registry(include_openai=include_openai)
    models = load_models(models_path or PROJECT_ROOT / "config/models.yaml")
    profiles = load_profiles(profiles_path or PROJECT_ROOT / "config/model-profiles.yaml")
    router = CapabilityRouter(profiles, models, providers)
    return ModelGateway(router, providers)


def build_runner(include_openai: bool = False) -> AgentRunner:
    """Build an agent runner backed by the configured model gateway."""
    return AgentRunner(build_gateway(include_openai=include_openai))
