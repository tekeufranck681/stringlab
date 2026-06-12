from __future__ import annotations

from typing import Literal, Optional, Union

from app.core.schemas import BaseSchema

# Shared enums (contract §1.2, §2).
FieldType = Literal["string", "integer", "select", "boolean"]
VisualizationLevel = Literal["result", "step_log", "full"]


# ---------------------------------------------------------------------------
# inputSpec (contract §2) — drives the single generic input panel.
# ---------------------------------------------------------------------------
class SelectOption(BaseSchema):
    value: str
    label: str


class FieldConstraints(BaseSchema):
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    allowed_alphabet: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None
    options: Optional[list[SelectOption]] = None


class InputField(BaseSchema):
    name: str
    label: str
    type: FieldType
    required: bool
    placeholder: Optional[str] = None
    default: Optional[Union[str, int, bool]] = None
    constraints: Optional[FieldConstraints] = None


class InputSpec(BaseSchema):
    fields: list[InputField]


# ---------------------------------------------------------------------------
# Operation & Category (contract §1.1, §1.2).
# ---------------------------------------------------------------------------
class Complexity(BaseSchema):
    time: str
    space: str


class OperationSchema(BaseSchema):
    slug: str
    name: str
    category_slug: str
    description: str
    explanation: str
    input_spec: InputSpec
    complexity: Complexity
    visualization_level: VisualizationLevel


class CategorySchema(BaseSchema):
    slug: str
    name: str
    description: str
    display_order: int
    operations: list[OperationSchema] = []


# ---------------------------------------------------------------------------
# Endpoint responses (contract §4.1, §4.2).
# ---------------------------------------------------------------------------
class CatalogResponse(BaseSchema):
    categories: list[CategorySchema]


class OperationDetailResponse(BaseSchema):
    operation: OperationSchema
    examples: list["ExampleSchema"]


# Imported at the bottom to avoid a circular import while still resolving the
# forward reference in OperationDetailResponse.
from app.modules.examples.schemas import ExampleSchema  # noqa: E402

OperationDetailResponse.model_rebuild()
