import os
import sys

import pytest
from elasticsearch import Elasticsearch
from user import User

from pydastic.pydastic import PydasticClient, connect


@pytest.fixture(scode="module")
def elasticsearch() -> Elasticsearch:
    connect(hosts="http://localhost:9200", ssl_show_warn=False)
    return PydasticClient.client


@pytest.fixture()
def user(elasticsearch) -> User:
    user = User(name="John", phone="123456")
    user.save(wait_for=True)
    return user
