import pytest
from elasticsearch import Elasticsearch
from user import User


@pytest.fixture()
def es() -> Elasticsearch:
    return Elasticsearch(hosts="http://localhost:9200", ssl_show_warn=False, headers={"Accept": "application/json", "Content-Type": "application/json"})


@pytest.fixture()
def user(es) -> User:
    user = User(name="John", phone="123456")
    user.save(es, wait_for=True)
    return user
