#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CAD-COIN Blockchain — Ultra Robust Production Flask Server
Author: Simon‑Pierre Boucher (requested), implementation upgraded by Claude

This ultra robust version includes:
- Adaptive difficulty adjustment
- Progressive reward halving based on block count
- Enhanced validation system
- Chain integrity verification
- Advanced security features
- Transaction fee system
- Block size limits
- Mining timeout protection
"""

import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.config import Config
from src.database import DatabaseManager
from src.cache import CacheManager
from src.models import UltraRobustBlockchain
from src.api.auth import init_auth_routes
from src.api.blockchain_routes import init_blockchain_routes
from src.api.stablecoin_routes import init_stablecoin_routes

# Enhanced Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler("blockchain.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory"""
    app = Flask(__name__)
    CORS(app)
    
    # Initialize components
    db_manager = DatabaseManager(Config.DATABASE_URL)
    cache_manager = CacheManager(Config.REDIS_URL)
    blockchain = UltraRobustBlockchain(db_manager, cache_manager)
    
    # Rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=Config.RATELIMIT_STORAGE_URL,
        default_limits=["1000 per hour"]
    )
    
    # Register blueprints
    auth_bp = init_auth_routes(app, db_manager, limiter)
    app.register_blueprint(auth_bp)
    
    blockchain_bp = init_blockchain_routes(app, blockchain, cache_manager, db_manager, limiter)
    app.register_blueprint(blockchain_bp)
    
    stablecoin_bp = init_stablecoin_routes(app, blockchain, limiter)
    app.register_blueprint(stablecoin_bp)
    
    # Enhanced Error handlers
    @app.errorhandler(429)
    def rate_limit_handler(e):
        return jsonify({
            "error": "Rate limit exceeded", 
            "description": str(e.description),
            "retry_after": getattr(e, 'retry_after', None)
        }), 429

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404
    
    return app


def main():
    """Main entry point"""
    app = create_app()
    
    print("🚀 Starting CAD-COIN Ultra Robust Blockchain Server…")
    print("📊 Database: PostgreSQL (Enhanced)")
    print("💾 Cache: Redis (Enhanced)")
    print("🔒 Auth: JWT")
    print("⚡ Rate limiting: Enabled")
    print(f"💰 Base mining reward: {Config.BASE_MINING_REWARD} CAD-COIN")
    print(f"🔗 Base difficulty: {Config.BASE_DIFFICULTY}")
    print(f"📈 Max difficulty: {Config.MAX_DIFFICULTY}")
    print(f"⏱️ Target block time: {Config.TARGET_BLOCK_TIME}s")
    print(f"🔄 Difficulty adjustment: Every {Config.DIFFICULTY_ADJUSTMENT_INTERVAL} blocks")
    print(f"📉 Halving interval: Every {Config.HALVING_INTERVAL} blocks")
    print(f"💳 Min transaction fee: {Config.MIN_TRANSACTION_FEE} CAD-COIN")
    print(f"📦 Max block size: {Config.MAX_BLOCK_SIZE} transactions")
    print(f"⏰ Mining timeout: {Config.MINING_TIMEOUT} seconds")
    print(f"🌐 Server: http://{Config.HOST}:{Config.PORT}")
    print("🛡️ Ultra Robust Features: ACTIVE")
    
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=True)


if __name__ == "__main__":
    main()