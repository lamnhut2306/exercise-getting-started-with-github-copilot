from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def isolation():
    # Make a deep copy of the in-memory activities store and restore after test
    backup = deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(backup)


@pytest.fixture()
def client():
    return TestClient(app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # sample check: Chess Club should exist
    assert "Chess Club" in data


def test_signup_and_unregister_flow(client):
    activity = "Chess Club"
    email = "test.student@mergington.edu"

    # Ensure not already registered
    assert email not in activities[activity]["participants"]

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    data = resp.json()
    assert "Signed up" in data["message"]
    assert email in activities[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    data = resp.json()
    assert "Unregistered" in data["message"]
    assert email not in activities[activity]["participants"]


def test_signup_already_registered(client):
    activity = "Programming Class"
    # pick an existing participant
    existing = activities[activity]["participants"][0]

    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_unregister_not_registered(client):
    activity = "Math Club"
    email = "not.registered@mergington.edu"

    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"] == "Student is not registered for this activity"
