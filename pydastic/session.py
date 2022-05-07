from typing import Optional

from elasticsearch.helpers import bulk

from pydastic.error import InvalidModelError
from pydastic.model import ESModel
from pydastic.pydastic import _client


class Session:
    def __init__(self):
        # Initialize state
        self._operations = []

    def save(self, model: ESModel, index: Optional[str] = None):
        # Create save bulk operation
        if not index:
            index = model.Meta.index

        doc = model.dict(exclude={"id"})
        op = {"_index": index, "_op_type": "index", **doc}

        self._operations.append(op)

    def update(self, model: ESModel, index: Optional[str] = None):
        if not index:
            index = model.Meta.index

        if not model.id:
            raise InvalidModelError("model id property is required for update operations")

        doc = model.dict(exclude={"id"})
        op = {"_id": model.id, "_index": index, "_op_type": "update", "_source": {"doc": doc}}

        self._operations.append(op)

    def commit(self, wait_for: Optional[bool] = False):
        refresh = "false"
        if wait_for:
            refresh = "wait_for"

        results = bulk(client=_client.client, actions=self._operations, refresh=refresh)

        # TODO: Process errors from operations
        pass

    def delete(self, model: ESModel, index: Optional[str] = None):
        raise NotImplementedError
