"""Tests for login attempt repository"""

from backend.app.data.login_attempts_data import LOGIN_ATTEMPTS
from backend.app.repositories.login_attempt_repo import(
    create_login_attempt,
    get_login_attempts_by_user,
    reset_login_attempts,
)

def setup_function():
    """Reset login attempts before each test"""
    reset_login_attempts()

def test_create_login_attempt_adds_record():
    """Creating a login attempt should add a record"""
    create_login_attempt(
        user_id="1",
        email="ryan@email.com",
        success=True,
    )

    assert len(LOGIN_ATTEMPTS) == 1
    assert LOGIN_ATTEMPTS[0]["user_id"] == "1"
    assert LOGIN_ATTEMPTS[0]["email"] == "ryan@email.com"
    assert LOGIN_ATTEMPTS[0]["success"] is True
    assert LOGIN_ATTEMPTS[0]["reason"] is None
    assert "timestamp" in LOGIN_ATTEMPTS[0]

def test_create_login_attemp_with_reason():
    """Creating a failed login attempt should store the reason"""
    create_login_attempt(
        user_id="2",
        email="ansella@email.com",
        success=False,
        reason="Incorrect password",
    )

    assert len(LOGIN_ATTEMPTS) == 1
    assert LOGIN_ATTEMPTS[0]["user_id"] == "2"
    assert LOGIN_ATTEMPTS[0]["email"] == "ansella@email.com"
    assert LOGIN_ATTEMPTS[0]["success"] is False
    assert LOGIN_ATTEMPTS[0]["reason"] == "Incorrect password"
    assert "timestamp" in LOGIN_ATTEMPTS[0]

def test_get_login_attempts_by_user_returns_matching_attempts():
    """Getting login attempts should return only records for that user"""
    create_login_attempt("1", "ryan@email.com", True)
    create_login_attempt("2", "ansella@email.com", False, "Incorrect password")
    create_login_attempt("1", "ryan@email.com", False, "Account locked")

    attempts = get_login_attempts_by_user("1")

    assert len(attempts) == 2
    assert all(attempt["user_id"] == "1" for attempt in attempts)

def test_get_login_attempts_by_user_returns_empty_list():
    """Getting login attempts for unknown user should return empty list"""
    create_login_attempt("1", "ryan@email.com", True)

    attempts = get_login_attempts_by_user("999")

    assert attempts == []

def test_reset_login_attempts_clear_records():
    """Resetting login attempts should clear stored records"""
    create_login_attempt("1", "ryan@email.com", True)
    create_login_attempt("2", "ansella@email.com", False, "Incorrect password")

    assert len(LOGIN_ATTEMPTS) == 2

    reset_login_attempts()

    assert not LOGIN_ATTEMPTS
