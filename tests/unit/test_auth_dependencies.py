# dependencies.py = 37, 52-64
import pytest
from datetime import datetime
from uuid import UUID, uuid4
from app.auth import dependencies
from app.schemas.user import UserResponse
from app.models import user as user_model


def test_get_current_user_with_full_payload(monkeypatch):
    payload = {
        "id": str(uuid4()),
        "username": "tester",
        "email": "t@example.com",
        "first_name": "T",
        "last_name": "User",
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    monkeypatch.setattr(user_model.User, "verify_token", staticmethod(lambda t: payload))

    result = dependencies.get_current_user(token="fake-token")
    assert isinstance(result, UserResponse)
    assert result.username == "tester"


def test_get_current_user_with_minimal_payload(monkeypatch):
    minimal = {"sub": str(uuid4())}
    monkeypatch.setattr(user_model.User, "verify_token", staticmethod(lambda t: minimal))

    result = dependencies.get_current_user(token="fake-token")
    assert isinstance(result, UserResponse)
    assert result.username == "unknown"


def test_get_current_user_with_none(monkeypatch):
    monkeypatch.setattr(user_model.User, "verify_token", staticmethod(lambda t: None))
    with pytest.raises(Exception):
        dependencies.get_current_user(token="fake-token")


def test_get_current_user_with_uuid(monkeypatch):
    uid = uuid4()
    monkeypatch.setattr(user_model.User, "verify_token", staticmethod(lambda t: uid))
    result = dependencies.get_current_user(token="fake-token")
    assert isinstance(result, UserResponse)
    assert result.id == uid


def test_get_current_active_user_inactive_raises():
    # create a UserResponse that is inactive
    inactive = UserResponse(
        id=uuid4(),
        username="inactive",
        email="i@example.com",
        first_name="I",
        last_name="N",
        is_active=False,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    with pytest.raises(Exception):
        dependencies.get_current_active_user(current_user=inactive)
