"""Provider-neutral message and content block domain models."""

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MessageRole(StrEnum):
    """Supported roles in a model conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ContentBlockType(StrEnum):
    """Supported provider-neutral content block types."""

    TEXT = "text"
    JSON = "json"


class ContentBlock(BaseModel):
    """A provider-neutral content item in a message or response."""

    model_config = ConfigDict(extra="forbid")

    type: ContentBlockType
    text: str | None = None
    data: dict[str, object] | list[object] | str | int | float | bool | None = None

    @classmethod
    def text_block(cls, text: str) -> Self:
        """Create a text content block."""
        return cls(type=ContentBlockType.TEXT, text=text)

    @classmethod
    def json_block(cls, data: dict[str, object]) -> Self:
        """Create a JSON content block."""
        return cls(type=ContentBlockType.JSON, data=data)

    @model_validator(mode="after")
    def validate_payload(self) -> Self:
        """Ensure each block carries the payload required by its type."""
        if self.type == ContentBlockType.TEXT and not self.text:
            raise ValueError("text content blocks require non-empty text")
        if self.type == ContentBlockType.JSON and self.data is None:
            raise ValueError("json content blocks require data")
        return self


class Message(BaseModel):
    """A provider-neutral chat message."""

    model_config = ConfigDict(extra="forbid")

    role: MessageRole
    content: list[ContentBlock] = Field(min_length=1)
    name: str | None = None

    @classmethod
    def from_text(cls, role: MessageRole, text: str, name: str | None = None) -> Self:
        """Create a message containing one text block."""
        return cls(role=role, content=[ContentBlock.text_block(text)], name=name)
