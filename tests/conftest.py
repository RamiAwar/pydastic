import os
import sys

import pytest
from elasticsearch import Elasticsearch
from user import User

from pydastic.pydastic import _client, connect


@pytest.fixture()
def es() -> Elasticsearch:
    connect(hosts="http://localhost:9200", ssl_show_warn=False)
    return _client.client


@pytest.fixture()
def user(es) -> User:
    user = User(name="John", phone="123456")
    user.save(wait_for=True)
    return user
