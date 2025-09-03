#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Blockchain routes for CAD-COIN Blockchain API
"""

import time
import logging
from flask import Blueprint, request, jsonify
from .auth import token_required

logger = logging.getLogger(__name__)

blockchain_bp = Blueprint('blockchain', __name__)


def init_blockchain_routes(app, blockchain, cache_manager, db_manager, limiter):
    """Initialize blockchain routes"""
    
    @blockchain_bp.route("/", methods=["GET"])
    def home():
        return jsonify({
            "message": "CAD-COIN Ultra Robust Blockchain Server",
            "version": "3.0-UltraRobust",
            "status": "active",
            "features": [
                "Adaptive difficulty adjustment",
                "Progressive reward halving",
                "Enhanced validation system",
                "Chain integrity verification",
                "Transaction fee system",
                "Priority-based mining",
                "Timeout protection",
                "Advanced caching"
            ],
            "endpoints": {
                "auth": {
                    "/auth/register": "POST",
                    "/auth/login": "POST"
                },
                "blockchain": {
                    "/chain": "GET (paginated)",
                    "/info": "GET (enhanced)",
                    "/balance/<address>": "GET",
                    "/balance/<address>/<coin_type>": "GET",
                    "/mine": "POST (auth, ultra robust)",
                    "/transaction": "POST (auth, with fees)"
                },
                "stablecoins": {
                    "/stable_coin": "POST (auth)",
                    "/mint": "POST (auth, enhanced)",
                    "/authorize_minter": "POST (auth)",
                    "/stable_coins": "GET"
                },
                "ops": {
                    "/pending_transactions": "GET",
                    "/health": "GET",
                    "/validate_chain": "GET (new)",
                    "/mining_stats": "GET (new)"
                }
            }
        })

    @blockchain_bp.route("/info", methods=["GET"])
    def get_info():
        return jsonify(blockchain.get_enhanced_chain_info())

    @blockchain_bp.route("/chain", methods=["GET"])
    def get_chain():
        try:
            limit = int(request.args.get("limit", "20"))
            offset = int(request.args.get("offset", "0"))
        except ValueError:
            return jsonify({"error": "limit/offset must be integers"}), 400

        limit = max(1, min(limit, 200))
        offset = max(0, offset)
        blocks = blockchain.get_blocks(limit=limit, offset=offset)
        return jsonify({"blocks": blocks, "limit": limit, "offset": offset})

    @blockchain_bp.route("/balance/<address>", methods=["GET"])
    def get_balance_all(address):
        balances = blockchain.get_all_balances(address)
        return jsonify({
            "address": address, 
            "balances": balances, 
            "total_coins": len(balances),
            "total_value_cad": sum(balances.values())
        })

    @blockchain_bp.route("/balance/<address>/<coin_type>", methods=["GET"])
    def get_balance_coin(address, coin_type):
        balance = blockchain.get_balance(address, coin_type.upper())
        return jsonify({
            "address": address, 
            "coin_type": coin_type.upper(), 
            "balance": balance,
            "formatted_balance": f"{balance:.8f}"
        })

    @blockchain_bp.route("/transaction", methods=["POST"])
    @token_required
    @limiter.limit("100 per hour")
    def create_transaction(current_user):
        data = request.get_json() or {}
        if "receiver" not in data or "amount" not in data:
            return jsonify({"error": "Missing fields: receiver, amount"}), 400

        coin_type = (data.get("coin_type") or "CAD-COIN").upper()
        fee = data.get("fee")  # Optional custom fee
        
        success, message = blockchain.create_transaction(
            current_user,
            data["receiver"],
            data["amount"],
            coin_type,
            fee
        )
        if success:
            return jsonify({"message": message})
        else:
            return jsonify({"error": message}), 400

    @blockchain_bp.route("/mine", methods=["POST"])
    @token_required
    @limiter.limit("10 per hour")
    def mine_block(current_user):
        success, message = blockchain.mine_pending_transactions(current_user)
        if success:
            # Invalidate balance cache for miner
            cache_manager.delete(f"balance_{current_user}_*")
            return jsonify({"message": message, "miner": current_user})
        else:
            return jsonify({"error": message}), 400

    @blockchain_bp.route("/pending_transactions", methods=["GET"])
    def list_pending():
        limit = int(request.args.get("limit", "50"))
        pending = blockchain.get_priority_pending_transactions(limit)
        return jsonify({
            "pending": pending,
            "count": len(pending),
            "max_pending": blockchain.max_pending_transactions
        })

    @blockchain_bp.route("/validate_chain", methods=["GET"])
    def validate_chain():
        """Validate blockchain integrity"""
        depth = int(request.args.get("depth", blockchain.block_validation_depth))
        is_valid, message = blockchain.validate_chain_integrity(depth)
        
        return jsonify({
            "valid": is_valid,
            "message": message,
            "validation_depth": depth,
            "timestamp": time.time()
        })

    @blockchain_bp.route("/mining_stats", methods=["GET"])
    def mining_stats():
        """Get detailed mining statistics"""
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                # Recent mining attempts
                cur.execute("""
                    SELECT miner, COUNT(*) as attempts, 
                           SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
                           AVG(CASE WHEN success THEN (end_time - start_time) ELSE NULL END) as avg_time
                    FROM mining_attempts 
                    WHERE start_time > %s
                    GROUP BY miner
                    ORDER BY successful DESC
                    LIMIT 10
                """, (time.time() - 86400,))  # Last 24 hours
                
                miners = [dict(row) for row in cur.fetchall()]
                
                # Network statistics
                cur.execute("""
                    SELECT AVG(difficulty) as avg_difficulty,
                           AVG(current_reward) as avg_reward,
                           AVG(hash_rate) as avg_hash_rate
                    FROM chain_stats
                    WHERE block_index >= %s
                """, (max(0, blockchain.get_enhanced_chain_info()["chain_length"] - 100),))
                
                network_stats = cur.fetchone()
                
        return jsonify({
            "top_miners_24h": miners,
            "network_stats": dict(network_stats) if network_stats else {},
            "current_difficulty": blockchain.calculate_current_difficulty(),
            "next_reward": blockchain.calculate_mining_reward(blockchain.get_latest_block()["index"] + 1),
            "target_block_time": blockchain.target_block_time,
            "timestamp": time.time()
        })

    @blockchain_bp.route("/health", methods=["GET"])
    def health_check():
        try:
            # Database health
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    
            # Cache health
            cache_manager.set("health_test", "ok", 10)
            cache_test = cache_manager.get("health_test")
            
            # Chain integrity check
            is_valid, validation_message = blockchain.validate_chain_integrity(5)
            
            return jsonify({
                "status": "healthy",
                "database": "ok",
                "cache": "ok" if cache_test == "ok" else "error",
                "chain_integrity": "valid" if is_valid else "invalid",
                "validation_message": validation_message,
                "version": "3.0-UltraRobust",
                "timestamp": time.time()
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }), 500

    return blockchain_bp