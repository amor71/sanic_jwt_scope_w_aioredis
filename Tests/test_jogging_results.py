import pytest
from sanic import Sanic
import random
import json
from jogging.main import config_app
from jogging import config
from jogging.Models.user import User

username = None
access_token = None
refresh_token = None


@pytest.yield_fixture
def app():
    config.app = Sanic("test_sanic_app")
    config_app()
    yield config.app


@pytest.fixture
def test_cli(loop, app, sanic_client):

    global username
    while username is None:
        i = random.randint(1, 10000)
        username = f"amichay.oren+{i}@gmail.com"
        if User.username_exists(username):
            username = None

    return loop.run_until_complete(sanic_client(app))


async def test_positive_register_(test_cli):
    data = {"username": username, "password": "testing123G"}
    resp = await test_cli.post("/users", data=json.dumps(data))
    assert resp.status == 201


async def test_positive_login(test_cli):
    data = {"username": username, "password": "testing123G"}
    resp = await test_cli.post("/auth", data=json.dumps(data))
    resp_json = await resp.json()
    print(resp_json)
    global access_token
    access_token = resp_json["access_token"]
    global refresh_token
    refresh_token = resp_json["refresh_token"]
    assert access_token is not None
    assert refresh_token is not None
    assert resp.status == 200


async def test_negative_jogging_result(test_cli):
    global access_token
    global refresh_token
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "date": "1971-06-20",
        "distance": 2000,
        "time": 405,
        "location": "32.0853 34.7818",
    }
    resp = await test_cli.post(
        "/results", headers=headers, data=json.dumps(data)
    )
    assert resp.status == 400


async def test_positive_jogging_result(test_cli):
    global access_token
    global refresh_token
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "date": "2015-06-20",
        "distance": 2000,
        "time": 405,
        "location": "32.0853 34.7818",
    }
    resp = await test_cli.post(
        "/results", headers=headers, data=json.dumps(data)
    )
    resp_json = await resp.json()
    print(resp_json)

    assert resp.status == 200