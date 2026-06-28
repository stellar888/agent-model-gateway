"""Tests for local model and profile configuration loading."""

from pathlib import Path

from app.gateway.registry import load_models, load_profiles

ROOT = Path(__file__).resolve().parents[2]


def test_model_and_profile_config_loads() -> None:
    """YAML configuration loads into typed registries."""
    profiles = load_profiles(ROOT / "config/model-profiles.yaml")
    models = load_models(ROOT / "config/models.yaml")

    assert profiles.get("coding_high").routes[0].provider == "fake"
    assert profiles.get("coding_power_openai").routes[0].model == "gpt-5.5"
    assert profiles.get("coding_fast_openai").routes[0].model == "gpt-5.4-mini"
    assert models.get("fake", "fake-coding-model").capabilities.structured_output is True
    assert models.get("openai", "gpt-5.4-mini").capabilities.max_context_window == 400_000
