#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authentication routes for CAD-COIN Blockchain API
"""

import logging
import psycopg2
import bcrypt
import jwt
from datetime import datetime
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ..config import Config

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Missing token"}), 401

        try:
            if token.startswith("Bearer "):
                token = token[7:]
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            current_user = data["address"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)
    return decorated


def init_auth_routes(app, db_manager, limiter):
    """Initialize authentication routes"""
    
    @auth_bp.route("/register", methods=["POST"])
    @limiter.limit("5 per minute")
    def register():
        data = request.get_json() or {}
        if not data.get("address") or not data.get("password"):
            return jsonify({"error": "address and password required"}), 400

        try:
            password_hash = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users (address, password_hash, reputation_score) VALUES (%s, %s, %s)
                    """, (data["address"], password_hash, 100))
                    conn.commit()

            logger.info(f"User created: {data['address']}")
            return jsonify({"message": "User created", "initial_reputation": 100})
        except psycopg2.IntegrityError:
            return jsonify({"error": "Address already taken"}), 400
        except Exception as e:
            logger.error(f"Register error: {e}")
            return jsonify({"error": "Server error"}), 500

    @auth_bp.route("/login", methods=["POST"])
    @limiter.limit("10 per minute")
    def login():
        data = request.get_json() or {}
        if not data.get("address") or not data.get("password"):
            return jsonify({"error": "address and password required"}), 400

        try:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT password_hash, reputation_score FROM users WHERE address = %s", (data["address"],))
                    user = cur.fetchone()
                    if user and bcrypt.checkpw(data["password"].encode("utf-8"), user["password_hash"].encode("utf-8")):
                        # Update last activity
                        cur.execute("UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE address = %s", (data["address"],))
                        conn.commit()
                        
                        token = jwt.encode(
                            {"address": data["address"], "exp": datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES},
                            Config.JWT_SECRET_KEY,
                            algorithm="HS256"
                        )
                        logger.info(f"Login: {data['address']}")
                        return jsonify({
                            "token": token, 
                            "address": data["address"],
                            "reputation_score": user["reputation_score"]
                        })
                    else:
                        return jsonify({"error": "Invalid credentials"}), 401
        except Exception as e:
            logger.error(f"Login error: {e}")
            return jsonify({"error": "Server error"}), 500

    return auth_bp