#jwt.py = 46, 58, 90-127 (-122)
import pytest
import asyncio
from jose import JWTError
from datetime import timedelta
from uuid import uuid4
from app.auth import jwt as jwt_mod
from app.schemas.token import TokenType


def test_password_hash_and_verify():
    pw = "MyS3cret!"
    hashed = jwt_mod.get_password_hash(pw)
    assert isinstance(hashed, str) and hashed != pw
    assert jwt_mod.verify_password(pw, hashed) is True
    assert jwt_mod.verify_password("wrong", hashed) is False


def test_create_and_decode_access_token(monkeypatch):
    user_id = uuid4()
    token = jwt_mod.create_token(user_id, TokenType.ACCESS, expires_delta=timedelta(minutes=5))

    # ensure blacklist check returns False
    async def fake_is_blacklisted(jti):
        return False

    monkeypatch.setattr("app.auth.jwt.is_blacklisted", fake_is_blacklisted)

    payload = asyncio.run(jwt_mod.decode_token(token, TokenType.ACCESS))
    assert payload["sub"] == str(user_id)
    assert payload["type"] == TokenType.ACCESS.value


def test_decode_token_invalid_type(monkeypatch):
    user_id = uuid4()
    # create access token but try to decode as refresh
    token = jwt_mod.create_token(user_id, TokenType.ACCESS, expires_delta=timedelta(minutes=5))

    async def fake_is_blacklisted(jti):
        return False

    monkeypatch.setattr("app.auth.jwt.is_blacklisted", fake_is_blacklisted)

    with pytest.raises(Exception) as exc:
        asyncio.run(jwt_mod.decode_token(token, TokenType.REFRESH))
    assert "Invalid token type" in str(exc.value)


def test_decode_expired_token(monkeypatch):
    user_id = uuid4()
    # create token that expires immediately (negative delta)
    token = jwt_mod.create_token(user_id, TokenType.ACCESS, expires_delta=timedelta(seconds=-1))

    async def fake_is_blacklisted(jti):
        return False

    monkeypatch.setattr("app.auth.jwt.is_blacklisted", fake_is_blacklisted)

    with pytest.raises(Exception) as exc:
        asyncio.run(jwt_mod.decode_token(token, TokenType.ACCESS, verify_exp=True))
    assert "expired" in str(exc.value).lower()


#jwt.py = 76-77, 112, 141-161 (-158)

def test_create_token_raises_http_exception(monkeypatch):
    # force jwt.encode to raise
    def bad_encode(payload, secret, algorithm):
        raise RuntimeError("boom")

    monkeypatch.setattr(jwt_mod.jwt, "encode", bad_encode)
    with pytest.raises(Exception) as exc:
        jwt_mod.create_token(uuid4(), TokenType.ACCESS)
    assert "Could not create token" in str(exc.value)


def test_decode_token_jwt_error(monkeypatch):
    # simulate jwt.decode raising JWTError
    def bad_decode(token, secret, algorithms, options):
        raise JWTError("bad")

    monkeypatch.setattr(jwt_mod.jwt, "decode", bad_decode)

    with pytest.raises(Exception) as exc:
        asyncio.run(jwt_mod.decode_token("fake", TokenType.ACCESS))
    assert "Could not validate" in str(exc.value) or "Could not validate credentials" in str(exc.value)


def test_decode_token_revoked(monkeypatch):
    # create a valid token then make is_blacklisted return True
    user_id = uuid4()
    token = jwt_mod.create_token(user_id, TokenType.ACCESS, expires_delta=timedelta(minutes=5))

    async def true_blacklist(jti):
        return True

    monkeypatch.setattr("app.auth.jwt.is_blacklisted", true_blacklist)

    with pytest.raises(Exception) as exc:
        asyncio.run(jwt_mod.decode_token(token, TokenType.ACCESS))
    assert "revoked" in str(exc.value).lower()


def test_get_current_user_not_found_and_inactive(monkeypatch):
    # monkeypatch decode_token to return payload with sub
    payload = {"sub": str(uuid4()), "type": TokenType.ACCESS.value}
    async def fake_decode(token, token_type, verify_exp=True):
        return payload

    monkeypatch.setattr(jwt_mod, "decode_token", fake_decode)

    # fake db where query(...).filter(...).first() returns None
    class FakeQuery:
        def filter(self, *a, **k):
            return self
        def first(self):
            return None

    class FakeDB:
        def query(self, model):
            return FakeQuery()

    # user not found -> should raise HTTPException wrapped
    with pytest.raises(Exception):
        asyncio.run(jwt_mod.get_current_user(token="t", db=FakeDB()))

    # now return inactive user
    class InactiveUser:
        is_active = False

    class FakeQuery2(FakeQuery):
        def first(self):
            return InactiveUser()

    class FakeDB2(FakeDB):
        def query(self, model):
            return FakeQuery2()

    with pytest.raises(Exception):
        asyncio.run(jwt_mod.get_current_user(token="t", db=FakeDB2()))
