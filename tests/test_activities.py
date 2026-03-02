import copy

from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

# snapshot of initial data so we can reset state between tests
_initial_snapshot = copy.deepcopy(app_module.activities)


def setup_function(function):
    """Reset activities dict before each test."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(_initial_snapshot))


def test_get_activities_returns_initial_dict():
    # Arrange: state restored by setup_function
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == set(_initial_snapshot.keys())


def test_signup_valid_activity_adds_participant():
    # Act
    resp = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new@mergington.edu"},
    )
    # Assert
    assert resp.status_code == 200
    assert resp.json() == {"message": "Signed up new@mergington.edu for Chess Club"}
    assert "new@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    resp = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity_returns_404():
    resp = client.post(
        "/activities/Nonexistent/signup",
        params={"email": "someone@mergington.edu"},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"


def test_delete_registered_participant_succeeds():
    resp = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"message": "Removed michael@mergington.edu from Chess Club"}
    assert "michael@mergington.edu" not in app_module.activities["Chess Club"]["participants"]


def test_delete_nonexistent_participant_returns_404():
    resp = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "not@here.edu"},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Participant not found in activity"
