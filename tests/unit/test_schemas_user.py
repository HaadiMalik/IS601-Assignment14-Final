# user.py = 53-55, 60-68 (-62, 66)
import pytest
from app.schemas.user import UserCreate


def test_usercreate_password_mismatch():
    data = {
        "first_name": "A",
        "last_name": "B",
        "email": "a.b@example.com",
        "username": "abuser",
        "password": "SecurePass1!",
        "confirm_password": "Different1!",
    }
    with pytest.raises(Exception):
        UserCreate(**data)


def test_usercreate_weak_passwords():
    base = {
        "first_name": "A",
        "last_name": "B",
        "email": "a.b2@example.com",
        "username": "abuser2",
        "confirm_password": "",
    }

    # too short
    data = {**base, "password": "Short1!", "confirm_password": "Short1!"}
    with pytest.raises(Exception):
        UserCreate(**data)

    # missing uppercase
    data = {**base, "password": "lowercase1!", "confirm_password": "lowercase1!"}
    with pytest.raises(Exception):
        UserCreate(**data)

    # missing digit
    data = {**base, "password": "NoDigits!!A", "confirm_password": "NoDigits!!A"}
    with pytest.raises(Exception):
        UserCreate(**data)

# user.py = 66, 69-70
def test_usercreate_missing_lowercase():
    data = {
        "first_name": "A",
        "last_name": "B",
        "email": "a.b3@example.com",
        "username": "abuser3",
        "password": "UPPERCASE1!",
        "confirm_password": "UPPERCASE1!",
    }
    with pytest.raises(Exception):
        UserCreate(**data)


def test_usercreate_missing_special_char():
    data = {
        "first_name": "A",
        "last_name": "B",
        "email": "a.b4@example.com",
        "username": "abuser4",
        "password": "NoSpecial1A",
        "confirm_password": "NoSpecial1A",
    }
    with pytest.raises(Exception):
        UserCreate(**data)
