from uuid import UUID

from src.domain.events.base import DomainEvent


class Entity:
    """Base class for any domain entity, identified by a stable UUID — independent
    of whatever persistence identity SQLAlchemy assigns it."""

    def __init__(self, entity_id: UUID) -> None:
        self.id = entity_id

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Entity) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class AggregateRoot(Entity):
    """Base class for aggregate roots. Collects domain events raised during a use
    case so the application layer can dispatch them after a successful commit.
    Dispatching is not wired up yet — this only prepares the contract."""

    def __init__(self, entity_id: UUID) -> None:
        super().__init__(entity_id)
        self._domain_events: list[DomainEvent] = []

    def record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_domain_events(self) -> list[DomainEvent]:
        events, self._domain_events = self._domain_events, []
        return events
