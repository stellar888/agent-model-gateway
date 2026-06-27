"""Provider, model, and profile registry helpers."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from app.domain.capabilities import ModelProfile
from app.domain.models import ModelDescriptor
from app.gateway.errors import ModelNotFoundError, ProfileNotFoundError, ProviderNotFoundError
from app.providers.base import ModelProvider


class ProviderRegistry:
    """In-memory registry of provider adapters by provider name."""

    def __init__(self, providers: dict[str, ModelProvider] | None = None) -> None:
        """Create a registry with optional initial providers."""
        self._providers = providers or {}

    def register(self, name: str, provider: ModelProvider) -> None:
        """Register a provider adapter."""
        self._providers[name] = provider

    def get(self, name: str) -> ModelProvider:
        """Return a provider adapter or raise a typed error."""
        try:
            return self._providers[name]
        except KeyError as exc:
            raise ProviderNotFoundError(f"provider {name!r} is not registered") from exc

    def list_names(self) -> list[str]:
        """Return registered provider names in deterministic order."""
        return sorted(self._providers)


class ModelRegistry:
    """In-memory registry of concrete provider model descriptors."""

    def __init__(self, models: list[ModelDescriptor] | None = None) -> None:
        """Create a model registry keyed by provider and model name."""
        self._models = {(model.provider, model.model): model for model in models or []}

    def get(self, provider: str, model: str) -> ModelDescriptor:
        """Return a concrete model descriptor or raise a typed error."""
        try:
            return self._models[(provider, model)]
        except KeyError as exc:
            raise ModelNotFoundError(f"model {provider}/{model} is not configured") from exc

    def list(self) -> list[ModelDescriptor]:
        """Return model descriptors in deterministic provider/model order."""
        return [self._models[key] for key in sorted(self._models)]


class ProfileRegistry:
    """In-memory registry of logical model profiles."""

    def __init__(self, profiles: list[ModelProfile] | None = None) -> None:
        """Create a profile registry keyed by profile name."""
        self._profiles = {profile.name: profile for profile in profiles or []}

    def get(self, name: str) -> ModelProfile:
        """Return a profile or raise a typed error."""
        try:
            return self._profiles[name]
        except KeyError as exc:
            raise ProfileNotFoundError(f"profile {name!r} is not configured") from exc

    def list(self) -> list[ModelProfile]:
        """Return profiles in deterministic name order."""
        return [self._profiles[key] for key in sorted(self._profiles)]


class ModelsConfig(BaseModel):
    """Validated models configuration file."""

    model_config = ConfigDict(extra="forbid")

    models: list[ModelDescriptor] = Field(default_factory=list)


class ProfilesConfig(BaseModel):
    """Validated profiles configuration file."""

    model_config = ConfigDict(extra="forbid")

    profiles: dict[str, ModelProfile]

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "ProfilesConfig":
        """Validate profiles while copying mapping keys into profile names."""
        profiles = {
            name: ModelProfile.model_validate({"name": name, **payload})
            for name, payload in raw.get("profiles", {}).items()
        }
        return cls(profiles=profiles)


def load_models(path: Path) -> ModelRegistry:
    """Load concrete model descriptors from a YAML file."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    config = ModelsConfig.model_validate(raw)
    return ModelRegistry(config.models)


def load_profiles(path: Path) -> ProfileRegistry:
    """Load logical model profiles from a YAML file."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    config = ProfilesConfig.from_raw(raw)
    return ProfileRegistry(list(config.profiles.values()))
