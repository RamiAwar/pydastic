import os
import sys

import pytest
from elasticsearch import Elasticsearch
from user import User

# Enable backwards compatibility of es client 8.x.x with ES db 7.x.x
os.environ["ELASTIC_CLIENT_APIVERSIONING"] = "1"


@pytest.fixture()
def es() -> Elasticsearch:
    return Elasticsearch(hosts="http://localhost:9200", ssl_show_warn=False)


@pytest.fixture()
def user(es) -> User:
    user = User(name="John", phone="123456")
    user.save(es, wait_for=True)
    return user
