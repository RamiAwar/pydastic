import pytest
from car import Car
from elasticsearch import AsyncElasticsearch, Elasticsearch
from user import User

from pydastic.pydastic import _client, connect, connect_async


@pytest.fixture()
async def async_es() -> AsyncElasticsearch:
    connect_async(hosts="http://localhost:9200")
    await _client.client.delete_by_query(index="_all", body={"query": {"match_all": {}}}, wait_for_completion=True, refresh=True)
    return _client.client


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


@pytest.fixture()
def car(aes: AsyncElasticsearch) -> Car:
    car = Car(name="Seat", year="2023")
    car.save(wait_for=True)
    return car
