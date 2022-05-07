import pytest
from elasticsearch import Elasticsearch
from user import User

from pydastic.pydastic import _client, connect


@pytest.fixture()
def es() -> Elasticsearch:
    connect(hosts="http://localhost:9200")
    _client.client.delete_by_query(index="_all", body={"query": {"match_all": {}}}, wait_for_completion=True, refresh=True)
    return _client.client


@pytest.fixture()
def user(es: Elasticsearch) -> User:
    user = User(name="John", phone="123456")
    user.save(wait_for=True)
    return user
