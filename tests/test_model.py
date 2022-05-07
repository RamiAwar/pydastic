from copy import deepcopy
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


def test_model_save_without_connection_raises_attribute_error():
    with pytest.raises(AttributeError):
        user = User(name="Liam")
        user.save(wait_for=True)


def test_model_save(es: Elasticsearch):
    user = User(name="John")
    user.save(wait_for=True)
    assert user.id != None

    res = es.get(index=user.Meta.index, id=user.id)
    assert res["found"]

    # Check that fields match exactly
    model = user.to_es()
    assert res["_source"] == model


def test_model_save_with_index(es: Elasticsearch):
    preset_id = "sam@mail.com"
    user = User(id=preset_id, name="Sam")
    user.save(wait_for=True)

    res = es.get(index=user.Meta.index, id=preset_id)
    assert res["found"]

    model = user.to_es()
    assert res["_source"] == model


def test_model_save_with_dynamic_index(es: Elasticsearch):
    preset_id = "abc@mail.com"
    user = User(id=preset_id, name="Sam")
    user.save(index="custom-user", wait_for=True)

    res = es.get(index="custom-user", id=preset_id)
    assert res["found"]

    model = user.to_es()
    assert res["_source"] == model


def test_model_save_datetime_saved_as_isoformat(es: Elasticsearch):
    date = datetime.now()
    iso = date.isoformat()

    user = User(name="Brandon", last_login=date)
    user.save(wait_for=True)

    res = es.get(index=user.Meta.index, id=user.id)
    assert res["found"]
    assert res["_source"]["last_login"] == iso


def test_model_save_to_update(es: Elasticsearch, user: User):
    # Update user details
    user_copy = deepcopy(user)

    dummy_name = "xxxxx"
    user.name = dummy_name

    user.save(wait_for=True)
    saved_user = User.get(id=user.id)

    assert saved_user.name == user.name

    # Change name back to compare with old object
    saved_user.name = user_copy.name
    assert saved_user == user_copy


def test_model_save_additional_fields(es: Elasticsearch):
    extra_fields = {"name": "John", "location": "Seattle", "manager_ids": ["Pam", "Sam"]}
    res = es.index(index=User.Meta.index, body=extra_fields)

    user = User.get(res["_id"], extra_fields=True)

    # Confirm that user has these extra fields
    assert user.location == extra_fields["location"]
    assert user.manager_ids == extra_fields["manager_ids"]

    # Check that extra fields dict is exact subset
    user_dict = user.dict()
    assert dict(user_dict, **extra_fields) == user_dict


# TODO: Test partial updates (to dict, exclude = True) -> maybe provide a partial api?


def test_model_ignores_additional_fields(es: Elasticsearch):
    extra_fields = {"name": "John", "location": "Seattle", "manager_ids": ["Pam", "Sam"]}
    res = es.index(index=User.Meta.index, body=extra_fields)

    user = User.get(res["_id"])
    with pytest.raises(AttributeError):
        user.location

    with pytest.raises(AttributeError):
        user.manager_ids


def test_model_get_fields_unaffected(es: Elasticsearch, user: User):
    """Bug where fields get overwritten when model is fetched and ID is popped out"""
    User.get(id=user.id)
    assert "id" in User.__fields__


def test_model_from_es(es: Elasticsearch):
    user = User(name="Alex")
    user.save(wait_for=True)

    res = es.get(index=user.Meta.index, id=user.id)
    assert res["found"]

    user_from_es = User.from_es(res)
    assert user == user_from_es


def test_model_from_es_empty_data():
    user = User.from_es({})
    assert user is None


def test_model_from_es_invalid_format():
    res = {"does not": "include _source", "or": "_id"}

    with pytest.raises(InvalidElasticsearchResponse):
        User.from_es(res)


def test_model_to_es(es: Elasticsearch):
    user = User(name="Claude")
    user.save(wait_for=True)
    es_from_user = user.to_es()

    res = es.get(index=user.Meta.index, id=user.id)
    assert res["_source"] == es_from_user


def test_model_to_es_with_exclude(es: Elasticsearch):
    user = User(name="Carla")
    user.save(wait_for=True)
    es_from_user = user.to_es(exclude={"last_login", "phone"})

    # Check that id excluded and fields excluded
    assert es_from_user == {"name": "Carla"}


def test_model_get(es: Elasticsearch):
    user = User(name="Jean", phone="128")
    user.save(wait_for=True)

    get = User.get(id=user.id)
    assert get == user


def test_model_get_with_dynamic_index(es: Elasticsearch):
    user = User(name="Philip", phone="128")
    user.save(index="custom", wait_for=True)

    get = User.get(index="custom", id=user.id)
    assert get == user


def test_model_get_nonexistent_raises_error(es: Elasticsearch):
    with pytest.raises(NotFoundError):
        User.get(id=uuid4())


def test_model_delete_raises_error(es: Elasticsearch):
    user = User(name="James")

    with pytest.raises(ValueError):
        user.delete(wait_for=True)

    with pytest.raises(NotFoundError):
        user.id = "123456"
        user.delete(wait_for=True)


def test_model_delete(es: Elasticsearch):
    user = User(name="Marie")
    user.save(wait_for=True)
    user.delete(wait_for=True)

    with pytest.raises(NotFoundError):
        User.get(id=user.id)


def test_model_delete_with_dynamic_index(es: Elasticsearch):
    user = User(name="Marie")
    user.save(index="abc", wait_for=True)
    user.delete(index="abc", wait_for=True)

    with pytest.raises(NotFoundError):
        User.get(id=user.id, index="abc")


def test_internal_meta_class_changes_limited_to_instance():
    # Cannot modify Meta index to have a dynamic index name
    user = User(name="a")
    user.Meta.index = "dev-user"

    assert User.Meta.index == "dev-user"
    assert user.Meta.index == "dev-user"
