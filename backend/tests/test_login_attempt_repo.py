"""Tests for login attempt repository"""

from app.data.login_attempts_data import LOGIN_ATTEMPTS
from app.repositories.login_attempt_repo import(
    create_login_attempt,
    get_login_attempts_by_user,
    reset_login_attempts,
)

INCORRECT_PASSWORD = "Incorrect password"
ACCOUNT_LOCKED = "Account locked"

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

def test_create_login_attempt_with_reason():
    """Creating a failed login attempt should store the reason"""
    create_login_attempt(
        user_id="2",
        email="ansella@email.com",
        success=False,
        reason=INCORRECT_PASSWORD,
    )

    assert len(LOGIN_ATTEMPTS) == 1
    assert LOGIN_ATTEMPTS[0]["user_id"] == "2"
    assert LOGIN_ATTEMPTS[0]["email"] == "ansella@email.com"
    assert LOGIN_ATTEMPTS[0]["success"] is False
    assert LOGIN_ATTEMPTS[0]["reason"] == INCORRECT_PASSWORD
    assert "timestamp" in LOGIN_ATTEMPTS[0]

def test_get_login_attempts_by_user_returns_matching_attempts():
    """Getting login attempts should return only records for that user"""
    create_login_attempt("1", "ryan@email.com", True)
    create_login_attempt("2", "ansella@email.com", False, INCORRECT_PASSWORD)
    create_login_attempt("1", "ryan@email.com", False, ACCOUNT_LOCKED)

    attempts = get_login_attempts_by_user("1")

    assert len(attempts) == 2

    assert LOGIN_ATTEMPTS[0]["user_id"] == "1"
    assert LOGIN_ATTEMPTS[0]["email"] == "ryan@email.com"
    assert LOGIN_ATTEMPTS[0]["success"] is True
    assert LOGIN_ATTEMPTS[0]["reason"] is None
    assert "timestamp" in LOGIN_ATTEMPTS[0]

    assert attempts[1]["user_id"] == "1"
    assert attempts[1]["email"] == "ryan@email.com"
    assert attempts[1]["success"] is False
    assert attempts[1]["reason"] == ACCOUNT_LOCKED

def test_get_login_attempts_by_user_returns_empty_list():
    """Getting login attempts for unknown user should return empty list"""
    create_login_attempt("1", "ryan@email.com", True)

    attempts = get_login_attempts_by_user("999")

    assert not attempts

def test_reset_login_attempts_clears_records():
    """Resetting login attempts should clear stored records"""
    create_login_attempt("1", "ryan@email.com", True)
    create_login_attempt("2", "ansella@email.com", False, INCORRECT_PASSWORD)

    assert len(LOGIN_ATTEMPTS) == 2

    reset_login_attempts()

    assert not LOGIN_ATTEMPTS
