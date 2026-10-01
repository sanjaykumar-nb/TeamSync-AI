"""The settings a deployment depends on: CORS that cannot stop the app, and a
limit on guessing passwords."""

import pytest
from httpx import AsyncClient

from app.config import Settings
from app.core import rate_limit

pytestmark = pytest.mark.mvp


class TestCorsSetting:
    """It used to be a list, so any value that was not JSON stopped the app at startup."""

    def test_a_plain_list_a_json_list_and_an_empty_value_all_work(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "https://app.example.com, https://www.app.example.com/")
        assert Settings().cors_origins == ["https://app.example.com", "https://www.app.example.com"]

        monkeypatch.setenv("CORS_ORIGINS", '["https://app.example.com"]')
        assert Settings().cors_origins == ["https://app.example.com"]

        monkeypatch.setenv("CORS_ORIGINS", "")
        assert Settings().cors_origins == []

    def test_the_docs_are_closed_unless_debug_is_asked_for(self, monkeypatch):
        monkeypatch.delenv("DEBUG", raising=False)
        assert Settings().DEBUG is False


class TestSignInLimit:
    @pytest.fixture(autouse=True)
    def small_limit(self, monkeypatch):
        monkeypatch.setattr(rate_limit.settings, "AUTH_RATE_LIMIT_ATTEMPTS", 3)
        monkeypatch.setattr(rate_limit.settings, "AUTH_RATE_LIMIT_WINDOW_SECONDS", 60)
        rate_limit.forget_everything()
        yield
        rate_limit.forget_everything()

    async def test_a_burst_of_wrong_passwords_is_cut_off(self, client: AsyncClient, test_user):
        attempt = {"username": test_user.email, "password": "not-the-password"}
        for _ in range(3):
            assert (await client.post("/api/v1/auth/login", data=attempt)).status_code == 401

        stopped = await client.post("/api/v1/auth/login", data=attempt)
        assert stopped.status_code == 429
        assert int(stopped.headers["Retry-After"]) > 0
        assert "Too many attempts" in stopped.json()["detail"]

    async def test_the_right_password_is_refused_too_once_the_limit_is_reached(
        self, client: AsyncClient, test_user
    ):
        for _ in range(3):
            await client.post("/api/v1/auth/login", data={"username": test_user.email, "password": "wrong"})
        # A limit that let the correct password through would not stop guessing.
        blocked = await client.post("/api/v1/auth/login",
                                    data={"username": test_user.email, "password": "password123"})
        assert blocked.status_code == 429

    async def test_signing_up_has_its_own_tally(self, client: AsyncClient):
        # Registration is limited separately, so sign-in attempts do not use it up.
        rate_limit.forget_everything()
        for i in range(3):
            body = {"email": f"someone{i}@example.com", "password": "password123", "full_name": "Someone"}
            assert (await client.post("/api/v1/auth/register", json=body)).status_code in (200, 201)
        last = await client.post("/api/v1/auth/register",
                                 json={"email": "late@example.com", "password": "password123", "full_name": "Late"})
        assert last.status_code == 429

    async def test_turning_it_off_lets_everything_through(self, client: AsyncClient, monkeypatch, test_user):
        monkeypatch.setattr(rate_limit.settings, "AUTH_RATE_LIMIT_ATTEMPTS", 0)
        rate_limit.forget_everything()
        for _ in range(6):
            response = await client.post("/api/v1/auth/login",
                                         data={"username": test_user.email, "password": "password123"})
            assert response.status_code == 200
