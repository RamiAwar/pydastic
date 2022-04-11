from typing import Any
from elasticsearch import Elasticsearch, AsyncElasticsearch
from pydastic.model import ESModel

class Session:
    def __init__(self, es: Elasticsearch):
        self.es = es
        raise NotImplementedError

    def create(self, model: ESModel):
        """Indexes a new document from an ESModel in elasticsearch

        Args:
            model (ESModel): model instance to be serialized and indexed into elasticsearch
        """
        raise NotImplementedError

    
    def update(self, model: ESModel):
        """Updates an already existing document in elasticsearch
        Raises an error if document does not exist

        Args:
            model (ESModel): model instance to be serialized and sent as an update to elasticsearch
        """
        raise NotImplementedError

    
    def commit(self):
        """Executes the accumulated operations and sends them as a bulk request to elasticsearch
        """
        raise NotImplementedError
