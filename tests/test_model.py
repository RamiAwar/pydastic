from datetime import datetime
from uuid import uuid4

import pytest
from elasticsearch import Elasticsearch
from user import User

from pydastic import ESModel, NotFoundError
from pydastic.error import InvalidElasticsearchResponse


def test_model_definition_yields_error_without_meta_class():
    with pytest.raises(NotImplementedError):

        class User(ESModel):
            pass


def test_model_definition_yields_error_without_index():
    with pytest.raises(NotImplementedError):

        class User(ESModel):
            class Meta:
                pass


def test_model_save(es: Elasticsearch):
    user = User(name="John")
    user.save(es, wait_for=True)
    assert user.id != None

    res = es.get(user.Meta.index, id=user.id)
    assert res["found"]

    # Check that fields match exactly
    model = user.to_es()
    assert res["_source"] == model


def test_model_save_with_index(es: Elasticsearch):
    preset_id = "sam@mail.com"
    user = User(id=preset_id, name="Sam")
    user.save(es, wait_for=True)

    res = es.get(user.Meta.index, id=preset_id)
    assert res["found"]

    model = user.to_es()
    assert res["_source"] == model


def test_model_save_datetime_saved_as_isoformat(es: Elasticsearch):
    date = datetime.now()
    iso = date.isoformat()

    user = User(name="Brandon", last_login=date)
    user.save(es, wait_for=True)

    res = es.get(user.Meta.index, id=user.id)
    assert res["found"]
    assert res["_source"]["last_login"] == iso


# TODO: Test save for updating documents

# TODO: Test save for adding field to a document

# TODO: Test save for modifying existing field in a document


def test_model_from_es(es: Elasticsearch):
    user = User(name="Alex")
    user.save(es, wait_for=True)

    res = es.get(user.Meta.index, id=user.id)
    user_from_es = User.from_es(res)

    assert user == user_from_es


def test_model_from_es_invalid_format():
    res = {"does not": "include _source", "or": "_id"}

    with pytest.raises(InvalidElasticsearchResponse):
        User.from_es(res)


def test_model_to_es(es: Elasticsearch):
    user = User(name="Claude")
    user.save(es, wait_for=True)
    es_from_user = user.to_es()

    res = es.get(user.Meta.index, id=user.id)
    assert res["_source"] == es_from_user


def test_model_get(es: Elasticsearch):
    user = User(name="Jean")
    user.save(es, wait_for=True)

    get = User.get(es, id=user.id)
    assert get == user


def test_model_get_nonexistent_raises_error(es: Elasticsearch):
    with pytest.raises(NotFoundError):
        User.get(es, id=uuid4())
