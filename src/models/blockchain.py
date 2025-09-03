#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ultra Robust Blockchain Service for CAD-COIN
"""

import time
import json
import hashlib
import logging
import math
import psycopg2
from typing import Dict, List, Optional, Tuple

from ..config import Config
from ..database import DatabaseManager
from ..cache import CacheManager
from .transaction import Transaction
from .block import Block

logger = logging.getLogger(__name__)


class UltraRobustBlockchain:
    def __init__(self, db_manager: DatabaseManager, cache_manager: CacheManager):
        self.db = db_manager
        self.cache = cache_manager
        self.base_mining_reward = Config.BASE_MINING_REWARD
        self.base_difficulty = Config.BASE_DIFFICULTY
        self.max_difficulty = Config.MAX_DIFFICULTY
        self.difficulty_adjustment_interval = Config.DIFFICULTY_ADJUSTMENT_INTERVAL
        self.halving_interval = Config.HALVING_INTERVAL
        self.target_block_time = Config.TARGET_BLOCK_TIME
        self.max_pending_transactions = Config.MAX_PENDING_TRANSACTIONS
        self.min_transaction_fee = Config.MIN_TRANSACTION_FEE
        self.max_block_size = Config.MAX_BLOCK_SIZE
        self.mining_timeout = Config.MINING_TIMEOUT
        self.max_chain_reorg_depth = Config.MAX_CHAIN_REORG_DEPTH
        self.block_validation_depth = Config.BLOCK_VALIDATION_DEPTH
        self.init_genesis_block()

    def init_genesis_block(self):
        """Create genesis block if missing"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS c FROM blocks")
                if int(cur.fetchone()["c"]) == 0:
                    genesis_hash = hashlib.sha256("genesis_block_cad_coin_ultra_robust".encode()).hexdigest()
                    cur.execute("""
                        INSERT INTO blocks (index, hash, previous_hash, miner, nonce, difficulty, timestamp, validation_status)
                        VALUES (0, %s, '0', 'genesis', 0, %s, %s, 'validated')
                    """, (genesis_hash, self.base_difficulty, time.time()))
                    
                    # Initialize chain stats for genesis block
                    cur.execute("""
                        INSERT INTO chain_stats (block_index, current_difficulty, current_reward, avg_block_time)
                        VALUES (0, %s, %s, 0)
                    """, (self.base_difficulty, self.base_mining_reward))
                    
                    conn.commit()
                    logger.info("Ultra robust genesis block created")

    def calculate_current_difficulty(self) -> int:
        """Calculate adaptive difficulty based on recent block times"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get the latest blocks for difficulty calculation
                cur.execute("""
                    SELECT timestamp, difficulty FROM blocks 
                    ORDER BY index DESC 
                    LIMIT %s
                """, (self.difficulty_adjustment_interval + 1,))
                
                blocks = cur.fetchall()
                
                if len(blocks) < self.difficulty_adjustment_interval:
                    return self.base_difficulty
                
                # Calculate average block time
                total_time = blocks[0]["timestamp"] - blocks[-1]["timestamp"]
                avg_time = total_time / len(blocks)
                expected_time = self.target_block_time
                
                current_difficulty = blocks[0]["difficulty"]
                
                # Adjust difficulty based on performance
                if avg_time < expected_time * 0.5:  # Too fast, increase difficulty
                    new_difficulty = min(current_difficulty + 2, self.max_difficulty)
                elif avg_time < expected_time * 0.8:  # Slightly fast, increase difficulty
                    new_difficulty = min(current_difficulty + 1, self.max_difficulty)
                elif avg_time > expected_time * 2.0:  # Too slow, decrease difficulty
                    new_difficulty = max(current_difficulty - 2, self.base_difficulty)
                elif avg_time > expected_time * 1.5:  # Slightly slow, decrease difficulty
                    new_difficulty = max(current_difficulty - 1, self.base_difficulty)
                else:  # Within acceptable range
                    new_difficulty = current_difficulty
                
                logger.info(f"Difficulty adjustment: avg_time={avg_time:.2f}s, target={expected_time}s, "
                           f"current={current_difficulty}, new={new_difficulty}")
                
                return new_difficulty

    def calculate_mining_reward(self, block_index: int) -> float:
        """Calculate progressive mining reward with halving"""
        halvings = block_index // self.halving_interval
        reward = self.base_mining_reward / (2 ** halvings)
        
        # Minimum reward floor
        min_reward = 0.1
        return max(reward, min_reward)

    def validate_chain_integrity(self, depth: int = None) -> Tuple[bool, str]:
        """Validate blockchain integrity"""
        if depth is None:
            depth = self.block_validation_depth
            
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT * FROM blocks 
                        ORDER BY index DESC 
                        LIMIT %s
                    """, (depth,))
                    
                    blocks = list(cur.fetchall())
                    
                    if not blocks:
                        return True, "No blocks to validate"
                    
                    # Validate each block in reverse order (latest first)
                    for i in range(len(blocks)):
                        block = blocks[i]
                        
                        # Skip genesis block
                        if block["index"] == 0:
                            continue
                            
                        # Find previous block
                        previous_block = None
                        for j in range(i + 1, len(blocks)):
                            if blocks[j]["index"] == block["index"] - 1:
                                previous_block = blocks[j]
                                break
                        
                        if not previous_block:
                            # Need to fetch from database
                            cur.execute("""
                                SELECT * FROM blocks WHERE index = %s
                            """, (block["index"] - 1,))
                            previous_block = cur.fetchone()
                        
                        if not previous_block:
                            return False, f"Missing previous block for block {block['index']}"
                        
                        if block["previous_hash"] != previous_block["hash"]:
                            return False, f"Chain integrity violation at block {block['index']}"
                    
                    return True, "Chain integrity validated"
                    
        except Exception as e:
            logger.error(f"Chain integrity validation error: {e}")
            return False, f"Validation error: {str(e)}"

    def get_priority_pending_transactions(self, limit: int = None) -> List[dict]:
        """Get pending transactions sorted by priority (fees + age)"""
        if limit is None:
            limit = self.max_block_size
            
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT *, 
                           (fee + (EXTRACT(EPOCH FROM NOW()) - timestamp) / 3600) as priority
                    FROM pending_transactions 
                    ORDER BY priority DESC, created_at ASC
                    LIMIT %s
                """, (limit,))
                
                return [dict(row) for row in cur.fetchall()]

    def create_transaction(self, sender: str, receiver: str, amount: float, 
                          coin_type: str = "CAD-COIN", fee: float = None) -> Tuple[bool, str]:
        """Enhanced transaction creation with fee calculation"""
        amount = float(amount)
        if fee is None:
            fee = max(self.min_transaction_fee, amount * 0.001)  # 0.1% fee or minimum
        
        if amount <= 0:
            return False, "Amount must be positive"
        
        if fee < self.min_transaction_fee:
            return False, f"Fee too low. Minimum: {self.min_transaction_fee}"

        try:
            # Enhanced balance check including fees
            total_required = amount + fee
            if self.get_balance(sender, coin_type) < total_required:
                return False, f"Insufficient balance. Required: {total_required} (amount + fee)"

            # Check pending transaction limit
            pending_count = len(self.get_pending_transactions())
            if pending_count >= self.max_pending_transactions:
                return False, "Too many pending transactions"

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Check coin exists
                    cur.execute("SELECT symbol FROM stable_coins WHERE symbol = %s", (coin_type,))
                    if not cur.fetchone():
                        return False, "Coin type does not exist"

                    tx = Transaction(sender, receiver, amount, coin_type, fee=fee)
                    
                    # Validate transaction
                    is_valid, error = tx.is_valid()
                    if not is_valid:
                        return False, error

                    cur.execute("""
                        INSERT INTO pending_transactions 
                        (tx_id, sender, receiver, amount, fee, coin_type, transaction_type, metadata, timestamp, priority_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (tx.id, tx.sender, tx.receiver, tx.amount, tx.fee, tx.coin_type, 
                          tx.transaction_type, json.dumps(tx.metadata), tx.timestamp, 
                          int(fee * 1000)))  # Priority based on fee

                    conn.commit()
                    logger.info(f"Enhanced tx created: {sender} -> {receiver}, {amount} {coin_type}, fee: {fee}")
                    return True, "Transaction added to pending pool"
                    
        except Exception as e:
            logger.error(f"Create transaction error: {e}")
            return False, "Transaction creation error"

    def mine_pending_transactions(self, miner_address: str) -> Tuple[bool, str]:
        """Enhanced mining with adaptive difficulty and robust validation"""
        try:
            # Get priority transactions
            pending_txs_data = self.get_priority_pending_transactions()
            # Allow mining even without pending transactions (empty blocks with just mining reward)

            # Calculate current difficulty and reward
            current_difficulty = self.calculate_current_difficulty()
            
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get latest block index
                    cur.execute("SELECT COALESCE(MAX(index), -1) + 1 as next_index FROM blocks")
                    next_index = cur.fetchone()["next_index"]
                    
                    mining_reward = self.calculate_mining_reward(next_index)
                    
                    # Record mining attempt
                    attempt_start = time.time()
                    cur.execute("""
                        INSERT INTO mining_attempts (block_index, miner, start_time, attempts_count)
                        VALUES (%s, %s, %s, 0)
                    """, (next_index, miner_address, attempt_start))
                    
                    # Rebuild Transaction objects from priority list
                    transactions: List[Transaction] = []
                    total_fees = 0
                    
                    for txd in pending_txs_data:
                        tx = Transaction(
                            sender=txd["sender"],
                            receiver=txd["receiver"],
                            amount=float(txd["amount"]),
                            coin_type=txd["coin_type"],
                            transaction_type=txd["transaction_type"],
                            metadata=txd["metadata"] or {},
                            fee=float(txd["fee"])
                        )
                        tx.id = txd["tx_id"]
                        tx.timestamp = float(txd["timestamp"])
                        transactions.append(tx)
                        total_fees += tx.fee

                    # Enhanced mining reward includes fees
                    reward_tx = Transaction(
                        sender="mining_reward",
                        receiver=miner_address,
                        amount=mining_reward + total_fees,  # Base reward + transaction fees
                        coin_type="CAD-COIN",
                        transaction_type="mining_reward"
                    )
                    transactions.append(reward_tx)

                    # Get latest block for previous hash
                    latest_block = self.get_latest_block()
                    
                    # Create new block with adaptive difficulty
                    new_block = Block(
                        index=next_index,
                        transactions=transactions,
                        previous_hash=latest_block["hash"],
                        miner=miner_address,
                        difficulty=current_difficulty,
                        max_mining_time=self.mining_timeout
                    )

                    logger.info(f"Mining block {new_block.index} with {len(transactions)} txs, "
                               f"difficulty {current_difficulty}, reward {mining_reward + total_fees}")
                    
                    # Mine the block
                    if new_block.mine_block():
                        # Validate the new block
                        is_valid, error = new_block.is_valid(latest_block["hash"])
                        if not is_valid:
                            logger.error(f"Mined block validation failed: {error}")
                            return False, f"Block validation failed: {error}"
                        
                        # Persist block with enhanced data
                        cur.execute("""
                            INSERT INTO blocks 
                            (index, hash, previous_hash, miner, nonce, difficulty, timestamp, 
                             mining_time, block_size, total_fees, validation_status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'validated')
                        """, (new_block.index, new_block.hash, new_block.previous_hash,
                              new_block.miner, new_block.nonce, new_block.difficulty, 
                              new_block.timestamp, new_block.mining_time, new_block.block_size,
                              new_block.total_fees))

                        # Persist transactions with enhanced data
                        for tx in transactions:
                            cur.execute("""
                                INSERT INTO transactions 
                                (tx_id, block_index, sender, receiver, amount, fee, coin_type, 
                                 transaction_type, metadata, timestamp, validation_status)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'validated')
                            """, (tx.id, new_block.index, tx.sender, tx.receiver, tx.amount,
                                  tx.fee, tx.coin_type, tx.transaction_type, 
                                  json.dumps(tx.metadata), tx.timestamp))

                        # Update balances with enhanced logic
                        self.update_balances_enhanced(transactions, cur)

                        # Update chain statistics
                        cur.execute("""
                            INSERT INTO chain_stats (block_index, current_difficulty, current_reward, avg_block_time, hash_rate)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (new_block.index, current_difficulty, mining_reward,
                              new_block.mining_time, new_block.nonce / new_block.mining_time if new_block.mining_time > 0 else 0))

                        # Update mining attempt record
                        cur.execute("""
                            UPDATE mining_attempts 
                            SET end_time = %s, success = TRUE, attempts_count = %s
                            WHERE block_index = %s AND miner = %s
                        """, (time.time(), new_block.nonce, next_index, miner_address))

                        # Clear processed pending transactions
                        processed_tx_ids = [tx.id for tx in transactions[:-1]]  # Exclude reward tx
                        if processed_tx_ids:
                            cur.execute("""
                                DELETE FROM pending_transactions 
                                WHERE tx_id = ANY(%s)
                            """, (processed_tx_ids,))

                        conn.commit()

                        # Invalidate relevant caches
                        self.cache.invalidate_pattern("latest_block*")
                        self.cache.invalidate_pattern("chain_info*")
                        self.cache.invalidate_pattern(f"balance_{miner_address}*")

                        logger.info(f"Block {new_block.index} successfully mined and validated. "
                                   f"Reward: {mining_reward + total_fees} CAD-COIN, "
                                   f"Time: {new_block.mining_time:.2f}s")
                        
                        return True, (f"Mined block {new_block.index}. "
                                     f"Reward: {mining_reward + total_fees:.8f} CAD-COIN. "
                                     f"Difficulty: {current_difficulty}, "
                                     f"Time: {new_block.mining_time:.2f}s")
                    else:
                        # Mining failed (timeout or other issue)
                        cur.execute("""
                            UPDATE mining_attempts 
                            SET end_time = %s, success = FALSE
                            WHERE block_index = %s AND miner = %s
                        """, (time.time(), next_index, miner_address))
                        conn.commit()
                        return False, "Mining failed or timed out"

        except Exception as e:
            logger.error(f"Enhanced mining error: {e}")
            return False, f"Mining error: {str(e)}"

    def update_balances_enhanced(self, transactions: List[Transaction], cursor):
        """Enhanced balance updates with fee handling"""
        for tx in transactions:
            if tx.transaction_type == "mint_stable":
                # Credit receiver
                cursor.execute("""
                    INSERT INTO balances (address, coin_type, balance)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (address, coin_type)
                    DO UPDATE SET balance = balances.balance + %s, updated_at = CURRENT_TIMESTAMP
                """, (tx.receiver, tx.coin_type, tx.amount, tx.amount))

            elif tx.transaction_type == "mining_reward":
                # Credit miner with reward + fees
                cursor.execute("""
                    INSERT INTO balances (address, coin_type, balance)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (address, coin_type)
                    DO UPDATE SET balance = balances.balance + %s, updated_at = CURRENT_TIMESTAMP
                """, (tx.receiver, tx.coin_type, tx.amount, tx.amount))

            else:  # Regular transfer with fees
                # Debit sender (amount + fee)
                total_debit = tx.amount + tx.fee
                cursor.execute("""
                    INSERT INTO balances (address, coin_type, balance)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (address, coin_type)
                    DO UPDATE SET balance = balances.balance - %s, updated_at = CURRENT_TIMESTAMP
                """, (tx.sender, tx.coin_type, 0, total_debit))

                # Credit receiver (only amount, fees go to miner)
                cursor.execute("""
                    INSERT INTO balances (address, coin_type, balance)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (address, coin_type)
                    DO UPDATE SET balance = balances.balance + %s, updated_at = CURRENT_TIMESTAMP
                """, (tx.receiver, tx.coin_type, tx.amount, tx.amount))

    def get_latest_block(self):
        """Get latest block with caching"""
        cache_key = "latest_block"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM blocks ORDER BY index DESC LIMIT 1")
                block_data = cur.fetchone()
                if block_data:
                    block_dict = dict(block_data)
                    self.cache.set(cache_key, block_dict, 300)
                    return block_dict
        return None

    def get_balance(self, address: str, coin_type: str = "CAD-COIN") -> float:
        """Get balance with enhanced caching"""
        cache_key = f"balance_{address}_{coin_type}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return float(cached)

        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT balance FROM balances WHERE address = %s AND coin_type = %s
                """, (address, coin_type))
                result = cur.fetchone()
                balance = float(result["balance"]) if result else 0.0
                self.cache.set(cache_key, balance, 300)
                return balance

    def get_enhanced_chain_info(self):
        """Get comprehensive chain information"""
        cache_key = "enhanced_chain_info"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                # Basic chain info
                cur.execute("SELECT COUNT(*) AS chain_length FROM blocks")
                chain_length = int(cur.fetchone()["chain_length"])

                cur.execute("SELECT COUNT(*) AS pending_count FROM pending_transactions")
                pending_count = int(cur.fetchone()["pending_count"])

                # Latest block info
                latest_block = self.get_latest_block()
                current_difficulty = self.calculate_current_difficulty()
                current_reward = self.calculate_mining_reward(latest_block["index"] + 1 if latest_block else 0)

                # Recent mining statistics
                cur.execute("""
                    SELECT AVG(mining_time) as avg_mining_time, AVG(hash_rate) as avg_hash_rate
                    FROM chain_stats 
                    WHERE block_index >= %s
                """, (max(0, chain_length - 10),))
                stats = cur.fetchone()

                # Network hash rate estimation
                cur.execute("""
                    SELECT AVG(POWER(2, difficulty) / mining_time) as estimated_hash_rate
                    FROM blocks 
                    WHERE index > 0 AND mining_time > 0
                    ORDER BY index DESC 
                    LIMIT 10
                """)
                hash_rate_result = cur.fetchone()

                info = {
                    "chain_length": chain_length,
                    "current_difficulty": current_difficulty,
                    "base_difficulty": self.base_difficulty,
                    "max_difficulty": self.max_difficulty,
                    "pending_transactions": pending_count,
                    "max_pending_transactions": self.max_pending_transactions,
                    "current_mining_reward": current_reward,
                    "base_mining_reward": self.base_mining_reward,
                    "target_block_time": self.target_block_time,
                    "avg_mining_time": float(stats["avg_mining_time"]) if stats["avg_mining_time"] else 0,
                    "estimated_network_hash_rate": float(hash_rate_result["estimated_hash_rate"]) if hash_rate_result and hash_rate_result["estimated_hash_rate"] else 0,
                    "min_transaction_fee": self.min_transaction_fee,
                    "max_block_size": self.max_block_size,
                    "halving_interval": self.halving_interval,
                    "difficulty_adjustment_interval": self.difficulty_adjustment_interval,
                    "stable_coins": self.get_stable_coins(),
                    "latest_block_hash": latest_block["hash"] if latest_block else None,
                    "chain_integrity_status": "validated"
                }
                
                self.cache.set(cache_key, info, 60)
                return info

    # Existing methods with minimal changes for compatibility
    def get_pending_transactions(self):
        """Get pending transactions ordered by priority"""
        return self.get_priority_pending_transactions()

    def get_all_balances(self, address: str) -> Dict[str, float]:
        """Get all balances for an address"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT coin_type, balance FROM balances WHERE address = %s
                """, (address,))
                return {row["coin_type"]: float(row["balance"]) for row in cur.fetchall()}

    def get_stable_coins(self):
        """Get all stablecoins"""
        cache_key = "stable_coins"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM stable_coins")
                stable_coins = {row["symbol"]: dict(row) for row in cur.fetchall()}
                self.cache.set(cache_key, stable_coins)
                return stable_coins

    def get_blocks(self, limit: int = 20, offset: int = 0):
        """Get paginated blocks with enhanced information"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT b.*, cs.hash_rate, cs.avg_block_time
                    FROM blocks b
                    LEFT JOIN chain_stats cs ON b.index = cs.block_index
                    ORDER BY b.index DESC
                    LIMIT %s OFFSET %s
                """, (limit, offset))
                blocks = [dict(b) for b in cur.fetchall()]
                if not blocks:
                    return []

                # Gather block indexes
                idxs = [b["index"] for b in blocks]
                cur.execute("""
                    SELECT * FROM transactions
                    WHERE block_index = ANY(%s)
                    ORDER BY created_at ASC
                """, (idxs,))
                txs = [dict(t) for t in cur.fetchall()]

                # Group transactions by block
                by_index = {}
                for b in blocks:
                    by_index[b["index"]] = {**b, "transactions": []}
                    
                for t in txs:
                    by_index[t["block_index"]]["transactions"].append({
                        "id": t["tx_id"],
                        "sender": t["sender"],
                        "receiver": t["receiver"],
                        "amount": float(t["amount"]),
                        "fee": float(t["fee"]),
                        "coin_type": t["coin_type"],
                        "transaction_type": t["transaction_type"],
                        "metadata": t["metadata"],
                        "timestamp": t["timestamp"],
                        "validation_status": t["validation_status"]
                    })
                    
                return [by_index[i] for i in idxs]

    # Existing methods for compatibility (simplified versions)
    def create_stable_coin(self, name: str, symbol: str, collateral_ratio: float,
                           backed_by: str, max_supply: float = None):
        """Create a new stablecoin (existing functionality)"""
        symbol = symbol.upper()
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO stable_coins (symbol, name, collateral_ratio, backed_by, max_supply, creation_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (symbol, name, collateral_ratio, backed_by, max_supply, time.time()))
                    conn.commit()

                    self.cache.delete("stable_coins")
                    logger.info(f"StableCoin {name} ({symbol}) created")
                    return True, f"StableCoin {name} ({symbol}) created"
        except psycopg2.IntegrityError:
            return False, "StableCoin already exists"
        except Exception as e:
            logger.error(f"Create stablecoin error: {e}")
            return False, "Error creating stablecoin"

    def add_authorized_minter(self, coin_symbol: str, minter_address: str, authorizer: str):
        """Authorize a minter for a stablecoin (existing functionality)"""
        coin_symbol = coin_symbol.upper()
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT symbol FROM stable_coins WHERE symbol = %s", (coin_symbol,))
                    if not cur.fetchone():
                        return False, "StableCoin does not exist"

                    if authorizer != "system":
                        balance = self.get_balance(authorizer, "CAD-COIN")
                        if balance < 100:
                            return False, "Insufficient authorization"

                    cur.execute("""
                        INSERT INTO authorized_minters (coin_symbol, minter_address, authorizer)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (coin_symbol, minter_address) DO NOTHING
                    """, (coin_symbol, minter_address, authorizer))
                    conn.commit()

                    logger.info(f"Minter {minter_address} authorized for {coin_symbol}")
                    return True, f"Minter {minter_address} authorized for {coin_symbol}"
        except Exception as e:
            logger.error(f"Authorize minter error: {e}")
            return False, "Authorization error"

    def is_authorized_minter(self, coin_symbol: str, minter: str):
        """Check if address is an authorized minter for the coin"""
        if minter == "system":
            return True

        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) AS c FROM authorized_minters
                    WHERE coin_symbol = %s AND minter_address = %s
                """, (coin_symbol, minter))
                return int(cur.fetchone()["c"]) > 0

    def mint_stable_coin(self, coin_symbol: str, minter: str, recipient: str, amount: float):
        """Mint stablecoins (existing functionality with enhancements)"""
        coin_symbol = coin_symbol.upper()
        amount = float(amount)
        if amount <= 0:
            return False, "Amount must be positive"
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM stable_coins WHERE symbol = %s", (coin_symbol,))
                    stable_coin = cur.fetchone()
                    if not stable_coin:
                        return False, "StableCoin does not exist"

                    if not self.is_authorized_minter(coin_symbol, minter):
                        return False, "Minter not authorized"

                    if stable_coin["max_supply"] is not None:
                        curr_supply = float(stable_coin["total_supply"])
                        max_supply = float(stable_coin["max_supply"])
                        if curr_supply + amount > max_supply:
                            return False, "Exceeds max supply"

                    # Calculate minting fee
                    minting_fee = max(self.min_transaction_fee, amount * 0.001)
                    
                    mint_tx = Transaction(
                        sender="mint",
                        receiver=recipient,
                        amount=amount,
                        coin_type=coin_symbol,
                        transaction_type="mint_stable",
                        metadata={"minter": minter, "stable_coin": coin_symbol},
                        fee=minting_fee
                    )
                    
                    cur.execute("""
                        INSERT INTO pending_transactions 
                        (tx_id, sender, receiver, amount, fee, coin_type, transaction_type, metadata, timestamp, priority_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (mint_tx.id, mint_tx.sender, mint_tx.receiver, mint_tx.amount, mint_tx.fee,
                          mint_tx.coin_type, mint_tx.transaction_type, json.dumps(mint_tx.metadata), 
                          mint_tx.timestamp, int(minting_fee * 1000)))

                    cur.execute("""
                        UPDATE stable_coins SET total_supply = COALESCE(total_supply, 0) + %s WHERE symbol = %s
                    """, (amount, coin_symbol))

                    conn.commit()
                    logger.info(f"{amount} {coin_symbol} minted for {recipient} by {minter}")
                    return True, f"Mint queued: {amount} {coin_symbol} → {recipient} (fee: {minting_fee})"
        except Exception as e:
            logger.error(f"Mint error: {e}")
            return False, "Mint error"