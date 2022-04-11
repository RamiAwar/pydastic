import pytest
from pydastic.model import ESModel
from elasticsearch import Elasticsearch
from user import User

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
    user = User(name="John", age=20)
    user.save(es, wait_for=True)
    assert user.id != None
