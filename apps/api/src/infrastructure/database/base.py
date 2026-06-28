from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base shared by every module's ORM models. Naming convention
    is enforced here so Alembic autogenerate produces stable constraint names."""

    pass
