"""
groq_rotation.py — shared multi-model rotation helper for Groq calls.

Groq's free tier enforces a per-model Tokens-Per-Day (TPD) budget on a
rolling 24h window, not a calendar-day reset — a 429 response names exactly
how long until enough tokens roll off to try again. Each model has an
independent TPD budget, so once one model's budget is tight, cycling to
another model keeps throughput up instead of blocking on a single cooldown.

This module tracks a per-model "available_at" timestamp (parsed from the
429 error text) and always calls whichever configured model is free right
now, falling back to sleeping only when every model is on cooldown.
"""

import re
import time

MODELS = [
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.1-8b-instant",
]

_available_at = {model: 0.0 for model in MODELS}

_WAIT_RE = re.compile(r"try again in (?:(\d+)m)?([\d.]+)s")


def _parse_wait_seconds(error_str):
    match = _WAIT_RE.search(error_str)
    if not match:
        return 60.0  # unknown format — short conservative cooldown
    minutes = float(match.group(1) or 0)
    seconds = float(match.group(2))
    return minutes * 60 + seconds + 2  # +2s buffer


def _is_daily_wall(error_str):
    return "tokens per day" in error_str or "TPD" in error_str


def next_available_model():
    """Returns (model, wait_seconds). wait_seconds is 0 if a model is free now."""
    now = time.time()
    free = [m for m in MODELS if _available_at[m] <= now]
    if free:
        return free[0], 0.0
    soonest_model = min(MODELS, key=lambda m: _available_at[m])
    return soonest_model, max(0.0, _available_at[soonest_model] - now)


def mark_exhausted(model, error_str):
    _available_at[model] = time.time() + _parse_wait_seconds(error_str)


def call_with_rotation(client, call_fn, max_wait_seconds=600):
    """call_fn(client, model) -> result. Tries whichever model is free,
    rotating on a daily-wall 429, sleeping (capped) only if all are on
    cooldown. Raises the last exception if a non-daily-wall error occurs."""
    tried_this_round = set()
    while True:
        model, wait = next_available_model()
        if wait > 0:
            if model in tried_this_round and wait > max_wait_seconds:
                time.sleep(max_wait_seconds)
            else:
                time.sleep(min(wait, max_wait_seconds))
            tried_this_round = set()
            continue
        try:
            return call_fn(client, model), model
        except Exception as e:
            error_str = str(e)
            if _is_daily_wall(error_str):
                mark_exhausted(model, error_str)
                tried_this_round.add(model)
                continue
            raise
