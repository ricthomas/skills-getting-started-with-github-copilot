import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def client_and_reset():
    """Provide a TestClient and reset in-memory activities after each test."""
    # Make a deep copy of the initial activities to restore after test
    original = copy.deepcopy(app_module.activities)
    client = TestClient(app_module.app)
    yield client
    # restore
    app_module.activities = original


def test_get_activities(client_and_reset):
    client = client_and_reset
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate(client_and_reset):
    client = client_and_reset
    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    # Ensure not already present
    assert email not in app_module.activities[activity]["participants"]

    # Signup should succeed
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")
    assert email in app_module.activities[activity]["participants"]

    # Duplicate signup should fail
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister_and_not_found(client_and_reset):
    client = client_and_reset
    activity = "Programming Class"
    email = "toremove@mergington.edu"

    # Add participant then unregister
    resp_add = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp_add.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    resp_del = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp_del.status_code == 200
    assert email not in app_module.activities[activity]["participants"]

    # Unregistering a non-existent email returns 404
    resp_not_found = client.delete(f"/activities/{activity}/participants?email=doesnotexist@mergington.edu")
    assert resp_not_found.status_code == 404
