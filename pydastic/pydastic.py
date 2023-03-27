import typing as t

from elasticsearch import AsyncElasticsearch, Elasticsearch

ElasticClasses = t.Union[Elasticsearch, AsyncElasticsearch]


class PydasticClient:
    client: t.Optional[ElasticClasses] = None

    def __getattribute__(self, __name: str) -> t.Any:
        if __name == "client" and object.__getattribute__(self, __name) is None:
            raise AttributeError("client not initialized - make sure to call Pydastic.connect() or Pydastic.connect_async()")
        return object.__getattribute__(self, __name)

    def _set_client(self, client: ElasticClasses):
        object.__setattr__(self, "client", client)
        return client


_client = PydasticClient()

F = t.TypeVar("F", bound=t.Callable[..., t.Any])


class copy_signature(t.Generic[F]):
    def __init__(self, target: F) -> F:
        self._target = target

    def __call__(self, wrapped: t.Callable[..., t.Any]) -> F:
        def wrapped(*args, **kwargs):
            return _client._set_client(self._target(*args, **kwargs))

        return wrapped


@copy_signature(Elasticsearch)
def connect(*args, **kwargs):
    ...


@copy_signature(AsyncElasticsearch)
def connect_async(*args, **kwargs):
    ...
