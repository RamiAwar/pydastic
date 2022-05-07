import pytest
from elasticsearch import Elasticsearch
from user import User

from pydastic import ESModel, Session
from pydastic.error import BulkError


def test_session_save_without_id(es: Elasticsearch):
    user = User(name="John")

    session = Session()

    session.save(user)
    session.commit(wait_for=True)

    res = es.search(index=user.Meta.index, body={"query": {"match_all": {}}})
    assert len(res["hits"]["hits"]) == 1

    model = user.to_es()
    assert res["hits"]["hits"][0]["_source"] == model


def test_session_save_with_id(es: Elasticsearch):
    user = User(id="john@mail.com", name="John")

    session = Session()
    session.save(user)
    session.commit(wait_for=True)

    res = es.get(index=user.Meta.index, id=user.id)
    assert res["found"]

    model = user.to_es()
    assert res["_source"] == model


def test_session_with_bulk_error(es: Elasticsearch):
    user = User(id="test", name="Jane")  # Not saved
    user2 = User(id="test2", name="test")

    session = Session()
    session.update(user)
    session.update(user2)

    with pytest.raises(BulkError):
        session.commit()


def test_session_with_bulk_error_without_raise_on_error(es: Elasticsearch):
    ...


def test_session_update(es: Elasticsearch):
    ...


def test_session_update_without_id_raises_error(es: Elasticsearch):
    ...


def test_session_delete(es: Elasticsearch):
    ...


def test_session_delete_without_id_raises_error(es: Elasticsearch):
    ...
