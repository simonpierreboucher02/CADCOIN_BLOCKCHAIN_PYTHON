#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Cache Manager for CAD-COIN Blockchain
"""

import json
import logging
import redis

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.cache_ttl = 3600  # 1 hour default

    def get(self, key):
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key, value, ttl=None):
        try:
            self.redis_client.setex(
                key,
                ttl or self.cache_ttl,
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    def delete(self, key):
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")

    def invalidate_pattern(self, pattern):
        """Invalidate all cache keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache pattern invalidation error: {e}")