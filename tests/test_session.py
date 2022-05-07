import pytest
from elasticsearch import Elasticsearch
from user import User

from pydastic import ESModel, Session


def test_session_save(es: Elasticsearch):
    user = User(name="John")

    session = Session()

    session.save(user)
    session.commit(wait_for=True)

    res = es.search(index=user.Meta.index, body={"query": {"match_all": {}}})
    assert len(res["hits"]["hits"]) == 1

    model = user.to_es()
    assert res["hits"]["hits"][0]["_source"] == model


def test_session_save_with(es: Elasticsearch):
    ...


def test_session_save_with_bulk_error(es: Elasticsearch):
    ...


def test_session_update(es: Elasticsearch):
    ...
