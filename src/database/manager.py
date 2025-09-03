#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Database Manager for CAD-COIN Blockchain
"""

import time
import logging
import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.init_database()

    def get_connection(self):
        return psycopg2.connect(self.database_url, cursor_factory=psycopg2.extras.RealDictCursor)

    def init_database(self):
        """Initialize enhanced database schema"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Users with enhanced features
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        address VARCHAR(255) UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        is_authorized_minter BOOLEAN DEFAULT FALSE,
                        reputation_score INTEGER DEFAULT 100,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Enhanced Blocks table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS blocks (
                        id SERIAL PRIMARY KEY,
                        index INTEGER UNIQUE NOT NULL,
                        hash VARCHAR(64) UNIQUE NOT NULL,
                        previous_hash VARCHAR(64) NOT NULL,
                        miner VARCHAR(255) NOT NULL,
                        nonce BIGINT NOT NULL,
                        difficulty INTEGER NOT NULL,
                        timestamp DOUBLE PRECISION NOT NULL,
                        mining_time DOUBLE PRECISION DEFAULT 0,
                        block_size INTEGER DEFAULT 0,
                        total_fees DECIMAL(20, 8) DEFAULT 0,
                        validation_status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Enhanced Transactions table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id SERIAL PRIMARY KEY,
                        tx_id VARCHAR(36) UNIQUE NOT NULL,
                        block_index INTEGER REFERENCES blocks(index),
                        sender VARCHAR(255) NOT NULL,
                        receiver VARCHAR(255) NOT NULL,
                        amount DECIMAL(20, 8) NOT NULL,
                        fee DECIMAL(20, 8) DEFAULT 0,
                        coin_type VARCHAR(50) NOT NULL,
                        transaction_type VARCHAR(50) NOT NULL,
                        metadata JSONB,
                        timestamp DOUBLE PRECISION NOT NULL,
                        validation_status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Stable coins (unchanged)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS stable_coins (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(20) UNIQUE NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        collateral_ratio DECIMAL(10, 4) NOT NULL,
                        backed_by VARCHAR(50) NOT NULL,
                        max_supply DECIMAL(20, 8),
                        total_supply DECIMAL(20, 8) DEFAULT 0,
                        creation_date DOUBLE PRECISION NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Enhanced Balances table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS balances (
                        id SERIAL PRIMARY KEY,
                        address VARCHAR(255) NOT NULL,
                        coin_type VARCHAR(50) NOT NULL,
                        balance DECIMAL(20, 8) DEFAULT 0,
                        frozen_balance DECIMAL(20, 8) DEFAULT 0,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(address, coin_type)
                    )
                """)

                # Authorized minters (unchanged)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS authorized_minters (
                        id SERIAL PRIMARY KEY,
                        coin_symbol VARCHAR(20) NOT NULL REFERENCES stable_coins(symbol),
                        minter_address VARCHAR(255) NOT NULL,
                        authorizer VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(coin_symbol, minter_address)
                    )
                """)

                # Enhanced Pending transactions table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pending_transactions (
                        id SERIAL PRIMARY KEY,
                        tx_id VARCHAR(36) UNIQUE NOT NULL,
                        sender VARCHAR(255) NOT NULL,
                        receiver VARCHAR(255) NOT NULL,
                        amount DECIMAL(20, 8) NOT NULL,
                        fee DECIMAL(20, 8) DEFAULT 0,
                        coin_type VARCHAR(50) NOT NULL,
                        transaction_type VARCHAR(50) NOT NULL,
                        metadata JSONB,
                        timestamp DOUBLE PRECISION NOT NULL,
                        priority_score INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    ALTER TABLE pending_transactions ADD COLUMN IF NOT EXISTS priority_score INTEGER DEFAULT 0;
                """)

                # Chain statistics table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chain_stats (
                        id SERIAL PRIMARY KEY,
                        block_index INTEGER UNIQUE NOT NULL,
                        current_difficulty INTEGER NOT NULL,
                        current_reward DECIMAL(20, 8) NOT NULL,
                        avg_block_time DOUBLE PRECISION DEFAULT 0,
                        hash_rate DOUBLE PRECISION DEFAULT 0,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Mining attempts table for difficulty calculation
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS mining_attempts (
                        id SERIAL PRIMARY KEY,
                        block_index INTEGER NOT NULL,
                        miner VARCHAR(255) NOT NULL,
                        start_time DOUBLE PRECISION NOT NULL,
                        end_time DOUBLE PRECISION,
                        success BOOLEAN DEFAULT FALSE,
                        attempts_count BIGINT DEFAULT 0
                    )
                """)

                # Ensure reputation_score and last_activity columns exist in users table
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS reputation_score INTEGER DEFAULT 100")
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                
                # Ensure fee column exists in pending_transactions table
                cur.execute("ALTER TABLE pending_transactions ADD COLUMN IF NOT EXISTS fee DECIMAL(20, 8) DEFAULT 0")

                # Enhanced Indexes
                cur.execute("CREATE INDEX IF NOT EXISTS idx_blocks_hash ON blocks(hash)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_blocks_miner ON blocks(miner)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_blocks_timestamp ON blocks(timestamp)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_transactions_block ON transactions(block_index)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_transactions_sender ON transactions(sender)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_transactions_receiver ON transactions(receiver)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_balances_address ON balances(address)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_priority ON pending_transactions(priority_score DESC)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_chain_stats_block ON chain_stats(block_index)")

                # Initialize CAD-COIN if not present
                cur.execute("""
                    INSERT INTO stable_coins (symbol, name, collateral_ratio, backed_by, creation_date)
                    VALUES ('CAD-COIN', 'CAD-COIN', 1.0000, 'CAD', %s)
                    ON CONFLICT (symbol) DO NOTHING
                """, (time.time(),))

                conn.commit()
                logger.info("Enhanced database initialized successfully")