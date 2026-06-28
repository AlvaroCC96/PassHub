from collections.abc import Callable
from functools import lru_cache
from typing import Any, TypeVar, cast

T = TypeVar("T")


class Container:
    """Minimal service locator used as the composition root.

    Bindings map a port (interface) to a factory that builds its concrete
    adapter. Swapping an adapter (e.g. MinIOStorageProvider -> GoogleCloudStorageProvider)
    only requires changing the binding here — domain and application layers never
    reference concrete infrastructure classes.
    """

    def __init__(self) -> None:
        self._bindings: dict[type[Any], Callable[[], Any]] = {}

    def bind(self, port: type[T], factory: Callable[[], T]) -> None:
        self._bindings[port] = factory

    def resolve(self, port: type[T]) -> T:
        try:
            factory = self._bindings[port]
        except KeyError as exc:
            raise LookupError(f"No binding registered for {port!r}") from exc
        return cast(T, factory())


@lru_cache
def get_container() -> Container:
    return Container()
