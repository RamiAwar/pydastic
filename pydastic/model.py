from typing import Any, Dict, Optional, Tuple, TypeVar, overload, Callable, Union
from elasticsearch import Elasticsearch
from pydantic import BaseModel
from pydantic.main import ModelMetaclass
from pydantic.main import Field, FieldInfo
from datetime import datetime

_T = TypeVar('_T')
def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: Tuple[Union[type, Callable[..., Any]], ...] = (()),
) -> Callable[[_T], _T]:
    """Decorator to allow python language servers to autocomplete ESModel instances"""
    return lambda a: a

@__dataclass_transform__(kw_only_default=True, field_descriptors=(Field, FieldInfo))
class ESModelMeta(ModelMetaclass):
    """Abstract ESModel Metaclass
    This Metaclass ensures that any concrete implementations of ESModel
    include all necessary definitions, ex. Meta internal class
    """

    def __new__(cls, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any], **kwds: Any):
        base_model = super().__new__(cls, name, bases, namespace, **kwds)
        meta = base_model.__dict__.get("Meta", False)
        if not meta:
            raise NotImplementedError("Internal 'Meta' not implemented")

        # Check existence of index name
        if not meta.__dict__.get("index", False):
            raise NotImplementedError("'index' property is missing from internal Meta class definition")

        return base_model


class ESModel(BaseModel, metaclass=ESModelMeta):

    id: Optional[Union[str, None]] = Field(default=None)

    class Meta:
        @property
        def index(self) -> str:
            """Elasticsearch index name associated with this model class"""
            raise NotImplementedError

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    def to_es(self, **kwargs) -> Dict:
        exclude_unset = kwargs.pop(
            "exclude_unset",
            False,  # Set as false so that default values are also stored
        )

        by_alias = kwargs.pop(
            "by_alias", True
        )  # whether field aliases should be used as keys in the returned dictionary

        # Converting the model to a dictionnary
        parsed = self.dict(by_alias=by_alias, exclude_unset=exclude_unset, **kwargs)

        return parsed

    @classmethod
    def from_es(cls, data: Dict[str, Any]):
        if not data:
            return None
        
        # TODO: Handle extract source + id automatically
        return cls(**data)

    def save(self, es: Elasticsearch, wait_for: bool = False):
        """Indexes document into elasticsearch.
        If document already exists, existing document will be updated as per native elasticsearch index operation.
        If model instance includes an 'id' property, this will be used as the elasticsearch _id.
        If no 'id' is provided, then document will be indexed and elasticsearch will generate a suitable id that will be populated on the returned model.
        
        Args:
            es (Elasticsearch): Elasticsearch client
            wait_for (bool, optional): Waits for all shards to sync before returning response - useful when writing tests. Defaults to False.
        """
        doc = self.dict(exclude={"id"})

        # Allow waiting for shards - useful when testing
        refresh = 'false'
        if wait_for:
            refresh = 'wait_for'

        res = es.index(index=123, body=doc, id=self.id, refresh=refresh)
        self.id = res.get("_id")
