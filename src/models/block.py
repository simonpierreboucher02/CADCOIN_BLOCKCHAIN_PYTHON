#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Block model for CAD-COIN Blockchain
"""

import time
import json
import hashlib
import logging
from typing import List, Tuple
from .transaction import Transaction

logger = logging.getLogger(__name__)


class Block:
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str,
                 miner: str, difficulty: int = 4, max_mining_time: int = 300):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.miner = miner
        self.timestamp = time.time()
        self.difficulty = difficulty
        self.nonce = 0
        self.hash = None
        self.mining_time = 0
        self.max_mining_time = max_mining_time
        self.block_size = len(transactions)
        self.total_fees = sum(tx.fee for tx in transactions)

    def calculate_hash(self):
        block_data = {
            "index": self.index,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "miner": self.miner,
            "timestamp": self.timestamp,
            "nonce": self.nonce
        }
        return hashlib.sha256(json.dumps(block_data, sort_keys=True).encode()).hexdigest()

    def mine_block(self) -> bool:
        """Enhanced mining with timeout protection"""
        target = "0" * self.difficulty
        start_time = time.time()
        attempt_count = 0

        logger.info(f"Starting mining block {self.index} with difficulty {self.difficulty}")
        
        while True:
            self.hash = self.calculate_hash()
            if self.hash.startswith(target):
                end_time = time.time()
                self.mining_time = end_time - start_time
                logger.info(f"Block {self.index} mined! Hash: {self.hash}, Nonce: {self.nonce}, Time: {self.mining_time:.2f}s, Attempts: {attempt_count}")
                return True
            
            self.nonce += 1
            attempt_count += 1

            # Progress logging
            if attempt_count % 100000 == 0:
                elapsed_time = time.time() - start_time
                hash_rate = attempt_count / elapsed_time
                logger.info(f"Mining progress - Block {self.index}: {attempt_count} attempts, {hash_rate:.2f} H/s, {elapsed_time:.1f}s elapsed")
                
                # Timeout protection
                if elapsed_time > self.max_mining_time:
                    logger.warning(f"Mining timeout for block {self.index} after {elapsed_time:.1f}s")
                    return False

        return False

    def is_valid(self, expected_previous_hash: str) -> Tuple[bool, str]:
        """Enhanced block validation"""
        if self.previous_hash != expected_previous_hash:
            return False, f"Invalid previous hash. Expected: {expected_previous_hash}, Got: {self.previous_hash}"
        
        if not self.hash or not self.hash.startswith("0" * self.difficulty):
            return False, "Invalid block hash or difficulty"
        
        if self.calculate_hash() != self.hash:
            return False, "Block hash verification failed"
        
        if len(self.transactions) == 0:
            return False, "Block cannot be empty"
        
        # Allow blocks with only mining reward transaction
        if len(self.transactions) == 1 and self.transactions[0].transaction_type == "mining_reward":
            pass  # Valid empty block with just mining reward
        
        # Validate all transactions
        for tx in self.transactions:
            is_valid, error = tx.is_valid()
            if not is_valid:
                return False, f"Invalid transaction {tx.id}: {error}"
        
        return True, "Valid"

    def to_dict(self):
        return {
            "index": self.index,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "miner": self.miner,
            "timestamp": self.timestamp,
            "difficulty": self.difficulty,
            "nonce": self.nonce,
            "hash": self.hash,
            "mining_time": self.mining_time,
            "block_size": self.block_size,
            "total_fees": self.total_fees
        }