from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.database import get_engine, get_sessionmaker, Base
from app.database import get_db as original_get_db
from app.auth.dependencies import get_current_active_user as original_get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse

# main.py = 18-58, 63-95, 97-104, 106-113, 115-127, 129-144, 146-161, 163-186, 196-206, 226-244, 254-287, 290-291, 294-307, 310-321, 335-347, 368-379

def create_in_memory_session():
    engine = get_engine("sqlite:///:memory:")
    TestingSessionLocal = get_sessionmaker(engine)
    # Create tables in the in-memory database
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def test_main_routes_calculation_crud_and_health():
    # Prepare in-memory DB sessionmaker and override dependencies
    TestingSessionLocal = create_in_memory_session()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[original_get_db] = override_get_db

    # Create a user directly in the test DB
    session = TestingSessionLocal()
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"test.user.{uuid.uuid4()}@example.com",
        "username": f"testuser_{uuid.uuid4().hex[:8]}",
        "password": "TestPass123!",
    }
    # Use the model register classmethod to add the user to the session
    user = User.register(session, {**user_data, "confirm_password": user_data["password"]})
    session.commit()
    session.refresh(user)

    # Build a UserResponse for dependency override
    user_resp = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

    # Override current user dependency
    app.dependency_overrides[original_get_current_active_user] = lambda: user_resp

    client = TestClient(app)

    # Health endpoint
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

    # Create a calculation (addition)
    payload = {"type": "addition", "inputs": [1, 2, 3]}
    r = client.post("/calculations", json=payload)
    assert r.status_code == 201, r.text
    calc = r.json()
    assert calc["result"] == 6
    calc_id = calc["id"]

    # List calculations
    r = client.get("/calculations")
    assert r.status_code == 200
    items = r.json()
    assert any(c["id"] == calc_id for c in items)

    # Get calculation by id
    r = client.get(f"/calculations/{calc_id}")
    assert r.status_code == 200
    assert r.json()["id"] == calc_id

    # Update calculation inputs
    r = client.put(f"/calculations/{calc_id}", json={"inputs": [5, 6]})
    assert r.status_code == 200
    updated = r.json()
    assert updated["result"] == 30

    # Delete calculation
    r = client.delete(f"/calculations/{calc_id}")
    assert r.status_code == 204

    # Confirm deletion
    r = client.get(f"/calculations/{calc_id}")
    assert r.status_code == 404

    # Simple web routes return HTML
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]

    # Cleanup dependency overrides
    app.dependency_overrides.pop(original_get_db, None)
    app.dependency_overrides.pop(original_get_current_active_user, None)
#