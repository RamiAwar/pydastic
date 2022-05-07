import json
from typing import List, Optional

from elasticsearch.helpers import bulk

from pydastic.error import BulkError, InvalidModelError
from pydastic.model import ESModel
from pydastic.pydastic import _client


class Session:
    def __init__(self):
        # Initialize state
        self._operations = []

    def save(self, model: ESModel, index: Optional[str] = None):
        """Save bulk operation

        Args:
            model (ESModel): Model to be indexed. If id is included, that id will be used in the indexing operation.
            index (Optional[str], optional): Dynamic index name to perform operation on. Defaults to index set in model Meta class.
        """
        if not index:
            index = model.Meta.index

        doc = model.dict(exclude={"id"})
        op = {"_index": index, "_op_type": "index", **doc}

        # Allow specifying id when indexing
        if model.id:
            op["_id"] = model.id

        self._operations.append(op)

    def update(self, model: ESModel, index: Optional[str] = None):
        """Update bulk operation

        Args:
            model (ESModel): Model to be updated. Must have an id set.
            index (Optional[str], optional): Dynamic index name to perform operation on. Defaults to index set in model Meta class.

        Raises:
            InvalidModelError: Raised when model id is missing
        """
        if not index:
            index = model.Meta.index

        if not model.id:
            raise InvalidModelError("model id property is required for update operations")

        doc = model.dict(exclude={"id"})
        op = {"_id": model.id, "_index": index, "_op_type": "update", "_source": {"doc": doc}}

        self._operations.append(op)

    def commit(self, wait_for: Optional[bool] = False, raise_on_error: Optional[bool] = True) -> Optional[List[dict]]:
        """Commits all saved operations to database.

        Args:
            wait_for (Optional[bool], optional):  Waits for all shards to sync before returning response - useful when writing tests. Defaults to False.
            raise_on_error (Optional[bool], optional): If set to False, errors are returned as an array of dicts. Defaults to True.

        Returns:
            List[dict]: Optionally returns list of errors

        Raises:
            BulkError: If any errors are encountered during executing the bulk operations and raise_on_error is True, this error is thrown, forwarding the ES errors all at once in a meaningful way.
        """
        refresh = "false"
        if wait_for:
            refresh = "wait_for"

        results = bulk(client=_client.client, actions=self._operations, refresh=refresh, raise_on_error=False)
        errors = results[1]

        if len(errors) != 0:
            if raise_on_error:
                # Pretty print error list
                raise BulkError(json.dumps(errors, indent=4))
            else:
                return errors

    def delete(self, model: ESModel, index: Optional[str] = None):
        """Delete bulk operation

        Args:
            model (ESModel): Model to be deleted. Must have an id set.
            index (Optional[str], optional): Dynamic index name to perform operation on. Defaults to index set in model Meta.

        Raises:
            InvalidModelError: Raised when model id is missing
        """
        if not index:
            index = model.Meta.index

        if not model.id:
            raise InvalidModelError("model id property is required for delete operations")

        op = {"_id": model.id, "_index": index, "_op_type": "delete"}
        self._operations.append(op)
