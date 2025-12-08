# user.py = 126-129, 290-291
import pytest
from app.models.user import User
from app.core.config import get_settings
from jose import jwt


def test_user_update_changes_updated_at():
    u = User(first_name="A", last_name="B", email="e@example.com", username="u", password="p")
    before = u.updated_at
    u.update(first_name="New")
    assert u.first_name == "New"
    assert u.updated_at >= before


def test_verify_token_non_uuid():
    # create a token with sub that is not a UUID
    settings = get_settings()
    payload = {"sub": "not-a-uuid"}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)

    # verify_token should return None for non-uuid sub
    assert User.verify_token(token) is None
