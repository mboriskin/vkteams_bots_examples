import pytest
import asynctest.mock as amock

import asyncio

from serious_bot.database.sqlite import DatabaseSqlite


def test_init():
    database = DatabaseSqlite(
        {
            "path": "database.db"
        }
    )
    assert database.client is None
    assert "database.db" == database.db_file
    assert "testtt" == database.table
    assert {
        "isolation_level": None
    } == database.conn_args


@pytest.mark.anyio
async def test_connect():
    database = DatabaseSqlite(
        {
            "path": "database.db"
        }
    )
    cor_mock = amock.CoroutineMock()
    cor_mock.eventloop = asyncio.new_event_loop()

    try:
        await database.connect()
        table = database.table
        client = type(database.client).__name__
        await database.disconnect()
    except NotImplementedError:
        raise Exception
    else:
        assert "testtt" == table
        assert "Connection" == client


@pytest.mark.anyio
async def test_disconnect():
    database = DatabaseSqlite(
        {
            "path": "database.db"
        }
    )
    cor_mock = amock.CoroutineMock()
    cor_mock.eventloop = asyncio.new_event_loop()

    try:
        await database.connect()
        await database.disconnect()
    except NotImplementedError:
        raise Exception
    else:
        pass


@pytest.mark.anyio
async def test_get_put_and_delete():
    database = DatabaseSqlite(
        {
            "path": "database.db"
        }
    )
    cor_mock = amock.CoroutineMock()
    cor_mock.eventloop = asyncio.new_event_loop()

    try:
        await database.connect()
        table = database.table
        client = type(database.client).__name__
        await database.put("hello", {})
        data = await database.get("hello")
        await database.delete("hello")
        await database.disconnect()
    except NotImplementedError:
        raise Exception
    else:
        assert "testtt" == table
        assert {} == data
        assert "Connection" == client
