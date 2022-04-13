import pytest
from elasticsearch import Elasticsearch


@pytest.fixture()
def es() -> Elasticsearch:
    return Elasticsearch(ssl_show_warn=False)
