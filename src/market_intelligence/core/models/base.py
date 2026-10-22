"""Base classes shared by all data contracts."""

from collections.abc import Mapping
from typing import Annotated, Any, Final, Literal, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict, model_validator

SCHEMA_VERSION: Final = 2
"""Data contract schema version; bump on any incompatible change (DEC-005, DEC-022)."""

_BINARY_TYPES = (bytes, bytearray, memoryview)


def _require_exact_int(value: object) -> object:
    if type(value) is not int:
        raise ValueError(
            "schema_version must be an integer; bool, float, Decimal and str are not accepted"
        )
    return value


SchemaVersion = Annotated[Literal[2], BeforeValidator(_require_exact_int)]


class ContractModel(BaseModel):
    """Immutable, always-validated value object (DEC-005, DEC-021).

    - Unknown fields are rejected and instances cannot be mutated.
    - Nested contract instances are re-validated whenever they are passed into another
      contract, so an unvalidated instance cannot be smuggled in.
    - ``model_copy(update=...)`` and ``copy.replace`` re-validate the result.
    - Binary input (``bytes``, ``bytearray``, ``memoryview``) is rejected for every field;
      callers must decode it explicitly.

    ``model_construct`` skips validation and must not be used outside tests.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_default=True,
        allow_inf_nan=False,
        revalidate_instances="always",
    )

    @model_validator(mode="before")
    @classmethod
    def _reject_binary_input(cls, data: Any) -> Any:
        if isinstance(data, Mapping):
            for key, value in data.items():
                if isinstance(value, _BINARY_TYPES):
                    raise ValueError(
                        f"field {key!r}: binary input is not accepted; decode it explicitly"
                    )
        return data

    def replace(self, **changes: Any) -> Self:
        """Return a new record with ``changes`` applied, validated like a new record."""
        return type(self).model_validate({**self.model_dump(), **changes})

    def model_copy(self, *, update: Mapping[str, Any] | None = None, deep: bool = False) -> Self:
        """Copy the record; with ``update`` the result is fully validated (see ``replace``)."""
        if update:
            return self.replace(**update)
        return super().model_copy(deep=deep)


class VersionedContractModel(ContractModel):
    """Top-level record carrying the data schema version.

    Deserializing a payload with a different ``schema_version`` fails validation.
    """

    schema_version: SchemaVersion = SCHEMA_VERSION
