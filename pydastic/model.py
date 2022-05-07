from copy import copy
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar, Union

from elasticsearch import NotFoundError as ElasticNotFoundError
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from pydantic.main import ModelMetaclass

from pydastic.error import InvalidElasticsearchResponse, NotFoundError
from pydastic.pydastic import _client

_T = TypeVar("_T")


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


M = TypeVar("M", bound="ESModel")


class ESModel(BaseModel, metaclass=ESModelMeta):
    id: Optional[str] = Field(default=None)

    class Meta:
        @property
        def index(self) -> str:
            """Elasticsearch index name associated with this model class"""
            raise NotImplementedError

    class Config:
        allow_population_by_field_name = True
        extra = "allow"
        json_encoders = {datetime: lambda dt: dt.isoformat()}

    def to_es(self: Type[M], **kwargs) -> Dict:
        """Generates an dictionary equivalent to what elasticsearch returns in the '_source' property of a response. This excludes the id property.

        Args:
            **kwargs: Pydantic .dict() options

        Returns:
            Dict
        """
        exclude_unset = kwargs.pop(
            "exclude_unset",
            False,  # Set as false so that default values are also stored
        )

        exclude: set = kwargs.pop("exclude", {"id"})
        if "id" not in exclude:
            exclude.add("id")

        d = self.dict(exclude=exclude, exclude_unset=exclude_unset, **kwargs)

        # Encode datetime fields
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()

        return d

    @classmethod
    def from_es(cls: Type[M], data: Dict[str, Any]) -> M:
        """Returns an ESModel from an elasticsearch document that has _id, _source

        Args:
            data (Dict[str, Any]): elasticsearch document that has _id, _source

        Raises:
            InvalidElasticsearchResponse: raised if an invalid elasticsearch document format is provided

        Returns:
            ESModel
        """
        if not data:
            return None

        source = data.get("_source")
        id = data.get("_id")

        if not source or not id:
            raise InvalidElasticsearchResponse

        model = cls(**source)
        model.id = id

        return model

    def save(self: Type[M], index: Optional[str] = None, wait_for: Optional[bool] = False):
        """Indexes document into elasticsearch.
        If document already exists, existing document will be updated as per native elasticsearch index operation.
        If model instance includes an 'id' property, this will be used as the elasticsearch _id.
        If no 'id' is provided, then document will be indexed and elasticsearch will generate a suitable id that will be populated on the returned model.

        Args:
            index (str, optional): Index name
            wait_for (bool, optional): Waits for all shards to sync before returning response - useful when writing tests. Defaults to False.
        """
        doc = self.dict(exclude={"id"})

        # Allow waiting for shards - useful when testing
        refresh = "false"
        if wait_for:
            refresh = "wait_for"

        # Use user-provided index if provided (dynamic index support)
        if not index:
            index = self.Meta.index

        res = _client.client.index(index=index, body=doc, id=self.id, refresh=refresh)
        self.id = res.get("_id")

    @classmethod
    def get(cls: Type[M], id: str, extra_fields: Optional[bool] = False, index: Optional[str] = None) -> M:
        """Fetches document and returns ESModel instance populated with properties.

        Args:
            id (str): Document id
            extra_fields (bool, Optional): Include fields found in elasticsearch but not part of the model definition
            index (str, optional): Index name

        Returns:
            ESModel

        Raises:
            NotFoundError: Returned if document not found
        """
        source_includes = None
        if not extra_fields:
            fields: dict = copy(vars(cls).get("__fields__"))
            fields.pop("id", None)
            source_includes = list(fields.keys())

        # Use user-provided index if provided (dynamic index support)
        if not index:
            index = cls.Meta.index

        try:
            res = _client.client.get(index=index, id=id, _source_includes=source_includes)
        except ElasticNotFoundError:
            raise NotFoundError(f"document with id {id} not found")

        model = cls.from_es(res)
        model.id = id

        return model

    def delete(self: Type[M], index: Optional[str] = None, wait_for: Optional[bool] = False):
        """Deletes document from elasticsearch.

        Args:
            index (str, optional): Index name
            wait_for (bool, optional): Waits for all shards to sync before returning response - useful when writing tests. Defaults to False.

        Raises:
            NotFoundError: Returned if document not found
            ValueError: Returned when id attribute missing from instance
        """
        if not self.id:
            raise ValueError("id missing from object")

        # Allow waiting for shards - useful when testing
        refresh = "false"
        if wait_for:
            refresh = "wait_for"

        # Use user-provided index if provided (dynamic index support)
        if not index:
            index = self.Meta.index

        try:
            _client.client.delete(index=index, id=self.id, refresh=refresh)
        except ElasticNotFoundError:
            raise NotFoundError(f"document with id {id} not found")
