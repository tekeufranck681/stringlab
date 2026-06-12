from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    """Base for every API schema.

    API JSON is camelCase (idiomatic for the React/TS frontend) while Python
    code stays snake_case. The alias generator bridges the two: fields are
    declared snake_case here, serialised camelCase on the wire, and accepted in
    either form on input (``populate_by_name``). ``from_attributes`` lets a
    schema be built directly from a SQLAlchemy model instance.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
