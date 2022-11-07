#!/usr/bin/env python3.8

from endgame_validator import redis as app_redis
from redis import Redis

redis: Redis = app_redis

def test_endgame_validator():
    assert 1 + 1 == 2