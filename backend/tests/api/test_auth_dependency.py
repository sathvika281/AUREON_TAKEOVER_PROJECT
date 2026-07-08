import pytest
from fastapi import HTTPException

from aureon.api import deps


class _FakeUser:
    def __init__(self, id: str) -> None:
        self.id = id


class _FakeUserResponse:
    def __init__(self, user: _FakeUser | None) -> None:
        self.user = user


class _FakeAuth:
    def __init__(self, token_map: dict[str, str]) -> None:
        self._map = token_map

    def get_user(self, token: str) -> _FakeUserResponse:
        user_id = self._map.get(token)
        if user_id is None:
            raise Exception("invalid or expired token")  # noqa: TRY002 — mirrors a real supabase-py failure
        return _FakeUserResponse(_FakeUser(user_id))


class _FakeClient:
    def __init__(self, auth: _FakeAuth) -> None:
        self.auth = auth


def _install(monkeypatch, token_map: dict[str, str]) -> None:
    monkeypatch.setattr(deps, "get_supabase_client", lambda: _FakeClient(_FakeAuth(token_map)))


async def test_missing_header_raises_401():
    with pytest.raises(HTTPException) as exc:
        await deps.get_current_user_id(authorization=None)
    assert exc.value.status_code == 401


async def test_malformed_header_raises_401():
    with pytest.raises(HTTPException) as exc:
        await deps.get_current_user_id(authorization="Token abc")
    assert exc.value.status_code == 401


async def test_invalid_token_raises_401(monkeypatch):
    _install(monkeypatch, {})
    with pytest.raises(HTTPException) as exc:
        await deps.get_current_user_id(authorization="Bearer bad-token")
    assert exc.value.status_code == 401


async def test_valid_token_returns_the_real_verified_user_id(monkeypatch):
    _install(monkeypatch, {"good-token": "user-abc"})
    user_id = await deps.get_current_user_id(authorization="Bearer good-token")
    assert user_id == "user-abc"


async def test_require_own_profile_passes_through_on_match():
    result = await deps.require_own_profile(student_id="user-abc", user_id="user-abc")
    assert result == "user-abc"


async def test_require_own_profile_raises_403_on_mismatch():
    """Never expose another student's profile — a verified user id that
    doesn't match the path's student_id is always rejected."""
    with pytest.raises(HTTPException) as exc:
        await deps.require_own_profile(student_id="someone-elses-id", user_id="user-abc")
    assert exc.value.status_code == 403
