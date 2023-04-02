from abc import ABC, abstractmethod
from copy import copy
from datetime import datetime
from functools import partial
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

        Returns:
            New document ID
        """
        return Save(index=index, wait_for=wait_for, model=self).sync()

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
        try:
            return Get(model=cls, id_=id, index=index, extra_fields=extra_fields).sync()
        except ElasticNotFoundError:
            raise NotFoundError(f"document with id {id} not found")

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
        try:
            Delete(index=index, model=self).sync()
        except ElasticNotFoundError:
            raise NotFoundError(f"document with id {id} not found")


class ESAsyncModel(ESModel):
    class Meta:
        @property
        def index(self) -> str:
            """Elasticsearch index name associated with this model class"""
            raise NotImplementedError

    async def save(self: Type[M], index: Optional[str] = None, wait_for: Optional[bool] = False):
        """Indexes document into elasticsearch.
        If document already exists, existing document will be updated as per native elasticsearch index operation.
        If model instance includes an 'id' property, this will be used as the elasticsearch _id.
        If no 'id' is provided, then document will be indexed and elasticsearch will generate a suitable id that will be populated on the returned model.

        Args:
            index (str, optional): Index name
            wait_for (bool, optional): Waits for all shards to sync before returning response - useful when writing tests. Defaults to False.

        Returns:
            New document ID
        """
        return await Save(index=index, wait_for=wait_for, model=self).asyncio()

    @classmethod
    async def get(cls: Type[M], id: str, extra_fields: Optional[bool] = False, index: Optional[str] = None) -> M:
        """Fetches document and returns ESModel instance populated with properties.

        Args:
            id (str): Document id
            extra_fields (bool, Optional): Include fields found in elasticsearch but not part of the model definition
            index (str, optional): Index name

        Returns:
            ESAsyncModel

        Raises:
            NotFoundError: Returned if document not found
        """
        get = Get(model=cls, id_=id, extra_fields=extra_fields, index=index)
        try:
            return await get.asyncio()
        except ElasticNotFoundError:
            raise NotFoundError(f"document with id {id} not found")

    async def delete(self: Type[M], index: Optional[str] = None, wait_for: Optional[bool] = False):
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
        try:
            await Delete(index=index, model=self, wait_for=wait_for).asyncio()
        except ElasticNotFoundError:
            raise NotFoundError(f"document with id {id} not found")


class BaseESOperation(ABC):
    """Abstract class of ES operation: save, get, delete

    Each subclass should set INDEX_METHOD_NAME which is the ES client function to run
    initiator (__init__) is used as pre-operation activity.
    """

    INDEX_METHOD_NAME: Optional[str] = None

    def __init__(self, model: Type[M], index: str, wait_for: Optional[bool] = None):
        if self.INDEX_METHOD_NAME is None:
            raise AttributeError(f"Must set INDEX_METHOD_NAME variable for class {self.__class__.__name__}")
        self._es_client_func = getattr(_client.client, self.INDEX_METHOD_NAME)

        self.model = model
        self.index = index
        if wait_for is not None:
            # Allow waiting for shards - useful when testing
            self.refresh = "wait_for" if wait_for else "false"

    @abstractmethod
    @property
    def kwargs(self):
        """ES operation kwargs"""
        raise NotImplementedError()

    @abstractmethod
    def post(self, *args, **kwargs):
        """Post activites after ES operation is done"""
        # do nothing by default
        raise NotImplementedError()

    def sync(self):
        """Run in blocking mode"""
        es_result = self._es_callable()
        return self.post(es_result=es_result)

    async def asyncio(self):
        """Run in async mode"""
        es_result = await self._es_callable()
        return self.post(es_result=es_result)

    @property
    def _es_callable(self) -> callable:
        return partial(self._es_client_func, **self.kwargs)


class Get(BaseESOperation):
    INDEX_METHOD_NAME = "get"

    def __init__(self, model: Type[M], id_: str, index: Optional[str] = None, extra_fields: Optional[bool] = False):
        super().__init__(index=index, model=model)
        self.id = id_

        self.source_includes = None
        if not extra_fields:
            fields: dict = copy(vars(model).get("__fields__"))
            fields.pop("id", None)
            self.source_includes = list(fields.keys())

    @property
    def kwargs(self):
        return dict(index=self.index, id=self.id, _source_includes=self.source_includes)

    def post(self, es_result: dict) -> M:
        model = self.model.from_es(es_result)
        model.id = self.id
        return model


class Save(BaseESOperation):
    INDEX_METHOD_NAME = "index"

    def __init__(self, model: Type[M], index: Optional[str] = None, wait_for: Optional[bool] = False):
        super().__init__(model=model, index=index, wait_for=wait_for)
        self.doc = self.model.dict(exclude={"id"})

    def post(self, es_result: dict) -> str:
        self.model.id = es_result.get("_id")
        return self.model.id

    @property
    def kwargs(self):
        return dict(index=self.index, doc=self.doc, id=self.model.id, refresh=self.refresh)


class Delete(BaseESOperation):

    INDEX_METHOD_NAME = "delete"

    def __init__(self, model: Type[M], index: Optional[str] = None, wait_for: Optional[bool] = False):
        super().__init__(model=model, index=index, wait_for=wait_for)

    @property
    def kwargs(self):
        return dict(index=self.index, id=self.model.id, refresh=self.refresh)

    def post(self, es_result: dict) -> None:
        return None
