"""Structured output validation helpers."""

from app.runtime.errors import OutputValidationError


def validate_output_schema(value: object, schema: dict[str, object]) -> dict[str, object]:
    """Validate structured output against the supported JSON Schema subset."""
    _validate(value, schema, path="$")
    if not isinstance(value, dict):
        raise OutputValidationError("structured output must be a JSON object")
    return value


def _validate(value: object, schema: dict[str, object], path: str) -> None:
    expected_type = schema.get("type")
    if isinstance(expected_type, str):
        _validate_type(value, expected_type, path)

    enum_values = schema.get("enum")
    if isinstance(enum_values, list) and value not in enum_values:
        raise OutputValidationError(f"{path} must be one of {enum_values}")

    if expected_type == "object":
        _validate_object(value, schema, path)
    if expected_type == "array":
        _validate_array(value, schema, path)


def _validate_type(value: object, expected_type: str, path: str) -> None:
    checks = {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "number": isinstance(value, int | float) and not isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
    }
    if expected_type in checks and not checks[expected_type]:
        raise OutputValidationError(f"{path} must be {expected_type}")


def _validate_object(value: object, schema: dict[str, object], path: str) -> None:
    if not isinstance(value, dict):
        return

    required = schema.get("required")
    if isinstance(required, list):
        for key in required:
            if isinstance(key, str) and key not in value:
                raise OutputValidationError(f"{path}.{key} is required")

    properties = schema.get("properties")
    if isinstance(properties, dict):
        for key, property_schema in properties.items():
            if key in value and isinstance(property_schema, dict):
                _validate(value[key], property_schema, f"{path}.{key}")

    if schema.get("additionalProperties") is False and isinstance(properties, dict):
        allowed = {str(key) for key in properties}
        extra = set(value) - allowed
        if extra:
            raise OutputValidationError(f"{path} contains unsupported keys: {sorted(extra)}")


def _validate_array(value: object, schema: dict[str, object], path: str) -> None:
    if not isinstance(value, list):
        return
    item_schema = schema.get("items")
    if not isinstance(item_schema, dict):
        return
    for index, item in enumerate(value):
        _validate(item, item_schema, f"{path}[{index}]")
