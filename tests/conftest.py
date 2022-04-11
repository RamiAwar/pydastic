from elasticsearch import Elasticsearch
import pytest

@pytest.fixture()
def es() -> Elasticsearch:
    return Elasticsearch()
