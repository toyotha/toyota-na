import os
import tempfile
from typing import TypedDict

from aiolimiter import AsyncLimiter

tmp_dir = tempfile.gettempdir()


class LimiterConfig(TypedDict):
    max_limit: float
    path: str
    starting_limit: int
    window: int


REQUEST_RATE_LIMITER: LimiterConfig = {
    "max_limit": 400.0,
    "path": f"{tmp_dir}/toyota_na_status_rate_limit",
    "starting_limit": 50,
    "window": 86400,  # 1 day
}

REFRESH_RATE_LIMITER: LimiterConfig = {
    "max_limit": 20.0,
    "path": f"{tmp_dir}/toyota_na_refresh_rate_limit",
    "starting_limit": 5,
    "window": 86400,  # 1 day
}


async def get_rate_limiter(limiter: LimiterConfig) -> AsyncLimiter:
    """Initializes and prepares a rate limiter with a given config"""

    if limiter == None:
        raise ValueError("No limiter config provided")

    # Init the bucket with the max allowable limit. We'll drain it later to match where the system left off
    initial_limiter = AsyncLimiter(limiter["max_limit"], limiter["window"])

    # Read the current bucket level from the cache. Sets a default of 20 if none exists
    cached_bucket_fill_level = _read_cache(limiter)

    # This bucket fills as you use requests. So we will fill it to match where the current rate usage should be.
    # The amount of "air" below the rim is what the user has left in terms of requests
    await initial_limiter.acquire(cached_bucket_fill_level)

    print(
        f"Initializing limiter with {limiter['max_limit'] - cached_bucket_fill_level} requests"
    )

    return initial_limiter


def cache_limit_to_disk(limiter: LimiterConfig, limit: float):
    with open(os.open(limiter["path"], os.O_CREAT | os.O_WRONLY, 0o600), "w") as fh:

        bytes = bytearray(f"{limit}", encoding="utf-8").hex()
        fh.seek(0)
        fh.write(bytes)
        fh.truncate()


def _read_cache(limiter: LimiterConfig) -> float:
    try:
        with open(os.open(limiter["path"], os.O_RDONLY), "r") as fh:
            val = fh.read()
            if val:
                parsed = bytes.fromhex(f"{val}".strip().replace("'", ""))
            return float(parsed)  # type: ignore
    except (FileNotFoundError, ValueError):
        return float(limiter["max_limit"] - limiter["starting_limit"])
