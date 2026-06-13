"""Mapping helpers: SQLAlchemy ORM rows -> catalogue API schemas.

The database stores snake_case columns (and a couple of values that the API
shape splits or renames); these helpers do that translation in one place so the
service stays focused on querying.
"""

from __future__ import annotations

from app.modules.catalogue.models import Category, Operation
from app.modules.catalogue.schemas import (
    CategorySchema,
    Complexity,
    InputSpec,
    OperationSchema,
)
from app.modules.examples.models import Example
from app.modules.examples.schemas import ExampleSchema


def operation_to_schema(operation: Operation, category_slug: str) -> OperationSchema:
    """Map an Operation row to its API schema.

    `category_slug` is passed in by the caller (it already has the parent
    category in hand) so we never trigger a lazy load — important under async
    SQLAlchemy, where implicit lazy loading is not allowed.

    Two columns are reshaped: ``time_complexity`` + ``space_complexity`` compose
    the nested ``complexity`` object, and the British-spelled ``visualisation_level``
    column becomes the API's ``visualizationLevel``.
    """
    return OperationSchema(
        slug=operation.slug,
        name=operation.name,
        category_slug=category_slug,
        description=operation.description,
        explanation=operation.explanation,
        # input_spec is JSONB stored in the API's camelCase shape; BaseSchema's
        # populate_by_name lets it validate straight from those aliases.
        input_spec=InputSpec.model_validate(operation.input_spec),
        complexity=Complexity(
            time=operation.time_complexity,
            space=operation.space_complexity,
        ),
        visualization_level=operation.visualisation_level,
    )


def category_to_schema(category: Category) -> CategorySchema:
    """Map a Category row (with its operations loaded) to its API schema."""
    return CategorySchema(
        slug=category.slug,
        name=category.name,
        description=category.description,
        display_order=category.display_order,
        operations=[
            operation_to_schema(op, category.slug) for op in category.operations
        ],
    )


def example_to_schema(example: Example) -> ExampleSchema:
    """Map an Example row to its API schema (``example_id`` becomes ``id``)."""
    return ExampleSchema(
        id=example.example_id,
        label=example.label,
        inputs=example.inputs,
        note=example.note,
    )
