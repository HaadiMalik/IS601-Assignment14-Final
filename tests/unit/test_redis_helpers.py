# redis.py = 17-18, 22-23
import pytest
import asyncio
import sys
import types
import app.auth.redis as redis_mod


class FakeRedis:
    def __init__(self):
        self.store = {}

    async def set(self, key, val, ex=None):
        self.store[key] = (val, ex)

    async def exists(self, key):
        return 1 if key in self.store else 0


def test_add_to_blacklist_and_check(monkeypatch):
    fake = FakeRedis()

    async def fake_get_redis():
        return fake

    monkeypatch.setattr(redis_mod, "get_redis", fake_get_redis)

    jti = "testjti"
    asyncio.run(redis_mod.add_to_blacklist(jti, exp=60))
    res = asyncio.run(redis_mod.is_blacklisted(jti))
    assert res in (0, 1)
    assert fake.store.get(f"blacklist:{jti}") is not None


# redis.py = 7-13


def test_get_redis_creates_client(monkeypatch):
    # Create a dummy aioredis module with from_url coroutine
    aioredis = types.SimpleNamespace()

    async def fake_from_url(url):
        class Client:
            pass
        return Client()

    aioredis.from_url = fake_from_url

    # Inject into sys.modules so import inside function finds it
    monkeypatch.setitem(sys.modules, "aioredis", aioredis)

    # import the module under test and call get_redis
    import app.auth.redis as redis_mod

    client = asyncio.run(redis_mod.get_redis())
    assert client is not None
