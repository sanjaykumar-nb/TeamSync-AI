"""A per-caller limit on the few endpoints worth hammering.

Sign-in is the expensive one: each attempt costs a bcrypt hash by design, so a
few hundred attempts a minute would both guess passwords and eat the server.
This allows a handful per minute per caller and answers 429 after that.

It counts in memory, per process: with several workers each keeps its own tally,
so the real limit is the setting times the number of workers. That is enough to
make guessing impractical at this scale. An exact, shared limit needs a shared
store (Redis), which is the next step if the product ever needs one.
"""

from collections import defaultdict, deque
from time import monotonic
from typing import Callable

from fastapi import HTTPException, Request, status

from app.config import get_settings

settings = get_settings()

_attempts: dict[tuple[str, str], deque] = defaultdict(deque)


def caller(request: Request) -> str:
    """Who is asking. Behind a proxy that is the first hop in X-Forwarded-For —
    trusted only when TRUST_PROXY_HEADERS says a proxy really is in front, since
    the header is otherwise whatever the caller typed."""
    if settings.TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def limit(name: str, count_every_attempt: bool = False) -> Callable:
    """A dependency allowing AUTH_RATE_LIMIT_ATTEMPTS per window, per caller.

    By default only failures count, recorded by the endpoint through `record_failure`:
    a team signing in one after another is normal, a run of wrong passwords is not.
    `count_every_attempt` counts them all, which suits creating accounts, where the
    successes are the thing to limit. `name` keeps one endpoint's tally separate from
    another's, and setting the attempts to 0 turns the limit off (the test suite does).
    """

    async def check(request: Request) -> None:
        allowed = settings.AUTH_RATE_LIMIT_ATTEMPTS
        window = settings.AUTH_RATE_LIMIT_WINDOW_SECONDS
        if allowed <= 0:
            return
        key = (name, caller(request))
        now = monotonic()
        recent = _attempts[key]
        while recent and now - recent[0] > window:
            recent.popleft()
        if len(recent) >= allowed:
            wait = int(window - (now - recent[0])) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many attempts. Try again in {wait} seconds.",
                headers={"Retry-After": str(wait)},
            )
        if count_every_attempt:
            recent.append(now)

    return check


def record_failure(request: Request, name: str) -> None:
    """One more failed attempt from this caller. Once they reach the limit, every
    attempt is refused for the rest of the window — including the right password,
    or guessing would simply continue until it worked."""
    if settings.AUTH_RATE_LIMIT_ATTEMPTS > 0:
        _attempts[(name, caller(request))].append(monotonic())


def forget_everything() -> None:
    """Drop every tally — for tests, and anything that needs a clean slate."""
    _attempts.clear()
