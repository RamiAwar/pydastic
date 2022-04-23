import typing as t

from elasticsearch import Elasticsearch


class PydasticClient:
    client: Elasticsearch = None

    def __getattribute__(self, __name: str) -> t.Any:
        if __name == "client" and object.__getattribute__(self, __name) is None:
            raise AttributeError("client not initialized - make sure to call Pydastic.connect()")
        return object.__getattribute__(self, __name)


_client = PydasticClient()

F = t.TypeVar("F", bound=t.Callable[..., t.Any])


class copy_signature(t.Generic[F]):
    def __init__(self, target: F) -> None:
        ...

    def __call__(self, wrapped: t.Callable[..., t.Any]) -> F:
        ...


@copy_signature(Elasticsearch)
def connect(*args, **kwargs):
    return Elasticsearch(*args, **kwargs)
