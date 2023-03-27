from copy import deepcopy
from datetime import datetime
from uuid import uuid4

import pytest
from car import Car
from elasticsearch import AsyncElasticsearch

from pydastic import ESAsyncModel, NotFoundError
from pydastic.error import InvalidElasticsearchResponse

pytestmark = pytest.mark.asyncio


async def test_model_definition_yields_error_without_meta_class():
    with pytest.raises(NotImplementedError):

        class AsyncUser(ESAsyncModel):
            pass


async def test_model_definition_yields_error_without_index():
    with pytest.raises(NotImplementedError):

        class AsyncUser(ESAsyncModel):
            class Meta:
                pass


@pytest.mark.asyncio
async def test_model_async_save_without_connection_raises_attribute_error():
    with pytest.raises(AttributeError):
        car = Car(model="Fiat")
        await car.save(wait_for=True)


@pytest.mark.asyncio
async def test_model_async_save(async_es: AsyncElasticsearch):
    car = Car(model="Fiat")
    await car.save(wait_for=True)
    assert car.id is not None

    res = await async_es.get(index=car.Meta.index, id=car.id)
    assert res["found"]

    # Check that fields match exactly
    model = car.to_es()
    assert res["_source"] == model


@pytest.mark.asyncio
async def test_model_save_with_index(async_es: AsyncElasticsearch):
    preset_id = "sam@mail.com"
    car = Car(id=preset_id, model="Fiat")
    await car.save(wait_for=True)

    res = await async_es.get(index=car.Meta.index, id=preset_id)
    assert res["found"]

    model = car.to_es()
    assert res["_source"] == model


@pytest.mark.asyncio
async def test_model_save_with_dynamic_index(async_es: AsyncElasticsearch):
    preset_id = "123456"
    car = Car(id=preset_id, model="Fiat")
    await car.save(index="custom-car", wait_for=True)

    res = await async_es.get(index="custom-car", id=preset_id)
    assert res["found"]

    model = car.to_es()
    assert res["_source"] == model


@pytest.mark.asyncio
async def test_model_save_datetime_saved_as_isoformat(async_es: AsyncElasticsearch):
    date = datetime.now()
    iso = date.isoformat()

    car = Car(model="Fiat", year=1994)
    await car.save(wait_for=True)

    res = async_es.get(index=car.Meta.index, id=car.id)
    assert res["found"]
    assert res["_source"]["last_test"] == iso


@pytest.mark.asyncio
async def test_model_save_to_update(async_es: AsyncElasticsearch, car: Car):
    # Update user details
    user_copy = deepcopy(car)

    dummy_name = "xxxxx"
    car.name = dummy_name

    await car.save(wait_for=True)
    saved_car = await Car.get(id=car.id)

    assert saved_car.model == car.model

    # Change name back to compare with old object
    saved_car.name = user_copy.name
    assert saved_car == user_copy


@pytest.mark.asyncio
async def test_model_save_additional_fields(async_es: AsyncElasticsearch):
    extra_fields = {"horse_power": "250", "color": "red"}
    res = async_es.index(index=Car.Meta.index, body=extra_fields)

    car = await Car.get(res["_id"], extra_fields=True)

    # Confirm that user has these extra fields
    assert car.horse_power == extra_fields["horse_power"]
    assert car.color == extra_fields["color"]

    # Check that extra fields dict is exact subset
    user_dict = car.dict()
    assert dict(user_dict, **extra_fields) == user_dict


@pytest.mark.asyncio
async def test_model_ignores_additional_fields(async_es: AsyncElasticsearch):
    extra_fields = {"horse_power": "250", "color": "red"}
    res = async_es.index(index=Car.Meta.index, body=extra_fields)

    car = await Car.get(res["_id"])
    with pytest.raises(AttributeError):
        car.horse_power

    with pytest.raises(AttributeError):
        car.color


@pytest.mark.asyncio
async def test_model_get_fields_unaffected(async_es: AsyncElasticsearch, car: Car):
    """Bug where fields get overwritten when model is fetched and ID is popped out"""
    await Car.get(id=car.id)
    assert "id" in Car.__fields__


@pytest.mark.asyncio
async def test_model_from_es(async_es: AsyncElasticsearch):
    car = Car(model="Fiat")
    await car.save(wait_for=True)

    res = async_es.get(index=car.Meta.index, id=car.id)
    assert res["found"]

    car_from_es = Car.from_es(res)
    assert car == car_from_es


@pytest.mark.asyncio
async def test_model_from_es_empty_data():
    car = Car.from_es({})
    assert car is None


@pytest.mark.asyncio
async def test_model_from_es_invalid_format():
    res = {"does not": "include _source", "or": "_id"}

    with pytest.raises(InvalidElasticsearchResponse):
        Car.from_es(res)


@pytest.mark.asyncio
async def test_model_to_es(async_es: AsyncElasticsearch):
    car = Car(model="Fiat")
    await car.save(wait_for=True)
    es_from_car = car.to_es()

    res = async_es.get(index=car.Meta.index, id=car.id)
    assert res["_source"] == es_from_car


@pytest.mark.asyncio
async def test_model_to_es_with_exclude(async_es: AsyncElasticsearch):
    car = Car(model="Fiat")
    await car.save(wait_for=True)
    es_from_car = car.to_es(exclude={"last_test", "year"})

    # Check that id excluded and fields excluded
    assert es_from_car == {"model": "Fiat"}


@pytest.mark.asyncio
async def test_model_get(async_es: AsyncElasticsearch):
    car = Car(model="Fiat", year="1976")
    await car.save(wait_for=True)

    get = Car.get(id=car.id)
    assert get == car


@pytest.mark.asyncio
async def test_model_get_with_dynamic_index(async_es: AsyncElasticsearch):
    car = Car(model="Fiat", year="1964")
    await car.save(index="custom", wait_for=True)

    get = await Car.get(index="custom", id=car.id)
    assert get == car


@pytest.mark.asyncio
async def test_model_get_nonexistent_raises_error(async_es: AsyncElasticsearch):
    with pytest.raises(NotFoundError):
        await Car.get(id=str(uuid4()))


@pytest.mark.asyncio
async def test_model_delete_raises_error(async_es: AsyncElasticsearch):
    car = Car(model="Fiat")

    with pytest.raises(ValueError):
        await car.delete(wait_for=True)

    with pytest.raises(NotFoundError):
        car.id = "123456"
        await car.delete(wait_for=True)


@pytest.mark.asyncio
async def test_model_delete(async_es: AsyncElasticsearch):
    car = Car(model="Fiat")
    await car.save(wait_for=True)
    await car.delete(wait_for=True)

    with pytest.raises(NotFoundError):
        await Car.get(id=car.id)


@pytest.mark.asyncio
async def test_model_delete_with_dynamic_index(async_es: AsyncElasticsearch):
    car = Car(model="Fiat")
    await car.save(index="abc", wait_for=True)
    await car.delete(index="abc", wait_for=True)

    with pytest.raises(NotFoundError):
        await Car.get(id=car.id, index="abc")


@pytest.mark.asyncio
async def test_internal_meta_class_changes_limited_to_instance():
    # Cannot modify Meta index to have a dynamic index name
    car = Car(model="Fiat")
    car.Meta.index = "dev-car"

    assert Car.Meta.index == "dev-car"
    assert car.Meta.index == "dev-car"
