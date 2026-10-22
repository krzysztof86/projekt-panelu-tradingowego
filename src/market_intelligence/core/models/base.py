"""Base classes shared by all data contracts."""

from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

SCHEMA_VERSION: Final = 1
"""Version of the data contract schema. Bump on any incompatible contract change (DEC-005)."""

SchemaVersion = Literal[1]


class ContractModel(BaseModel):
    """Immutable value object: unknown fields are rejected, instances cannot be mutated."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_default=True,
        allow_inf_nan=False,
    )


class VersionedContractModel(ContractModel):
    """Top-level record carrying the data schema version.

    Deserializing a payload with a different ``schema_version`` fails validation.
    """

    schema_version: SchemaVersion = SCHEMA_VERSION
