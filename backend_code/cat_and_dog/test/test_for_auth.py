# -*- coding: utf-8 -*-
import pytest
from sanic.websocket import WebSocketProtocol

from cat_and_dog import create_app


@pytest.yield_fixture
def app():
    a = create_app("dev")
    yield a


@pytest.fixture
def test_cli(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app, protocol=WebSocketProtocol))


# def test_index_returns_200():
#     request, response = app.test_client.get('/')
#     assert response.status == 500
#
#
# def test_index_put_not_allowed():
#     request, response = app.test_client.put('/')
#     assert response.status == 405


async def test_fixture_test_client_get(test_cli):
    """
    GET request
    """
    resp = await test_cli.get('/')
    assert resp.status == 200
