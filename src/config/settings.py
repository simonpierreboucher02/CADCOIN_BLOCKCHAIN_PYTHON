#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration settings for CAD-COIN Blockchain
"""

import os
from datetime import timedelta


class Config:
    # PostgreSQL
    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/blockchain_db")

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Security
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-this-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get("JWT_EXPIRES_HOURS", "24")))

    # Ultra Robust Mining Configuration
    BASE_MINING_REWARD = float(os.environ.get("BASE_MINING_REWARD", "50.0"))
    BASE_DIFFICULTY = int(os.environ.get("BASE_DIFFICULTY", "4"))
    MAX_DIFFICULTY = int(os.environ.get("MAX_DIFFICULTY", "20"))
    DIFFICULTY_ADJUSTMENT_INTERVAL = int(os.environ.get("DIFFICULTY_ADJUSTMENT_INTERVAL", "10"))  # Every 10 blocks
    HALVING_INTERVAL = int(os.environ.get("HALVING_INTERVAL", "100"))  # Every 100 blocks
    TARGET_BLOCK_TIME = int(os.environ.get("TARGET_BLOCK_TIME", "10"))  # 10 seconds target
    
    # Blockchain Security
    MAX_PENDING_TRANSACTIONS = int(os.environ.get("MAX_PENDING_TRANSACTIONS", "1000"))
    MIN_TRANSACTION_FEE = float(os.environ.get("MIN_TRANSACTION_FEE", "0.001"))
    MAX_BLOCK_SIZE = int(os.environ.get("MAX_BLOCK_SIZE", "100"))  # Max transactions per block
    MINING_TIMEOUT = int(os.environ.get("MINING_TIMEOUT", "300"))  # 5 minutes max mining time
    
    # Chain Validation
    MAX_CHAIN_REORG_DEPTH = int(os.environ.get("MAX_CHAIN_REORG_DEPTH", "10"))
    BLOCK_VALIDATION_DEPTH = int(os.environ.get("BLOCK_VALIDATION_DEPTH", "5"))

    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", os.environ.get("REDIS_URL", "redis://localhost:6379/1"))

    # Server
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "80"))
    DEBUG = os.environ.get("DEBUG", "0") == "1"