#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stablecoin routes for CAD-COIN Blockchain API
"""

import logging
from flask import Blueprint, request, jsonify
from .auth import token_required

logger = logging.getLogger(__name__)

stablecoin_bp = Blueprint('stablecoin', __name__)


def init_stablecoin_routes(app, blockchain, limiter):
    """Initialize stablecoin routes"""
    
    @stablecoin_bp.route("/stable_coin", methods=["POST"])
    @token_required
    @limiter.limit("5 per hour")
    def create_stable_coin(current_user):
        data = request.get_json() or {}
        required = ["name", "symbol", "backed_by"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing: name, symbol, backed_by"}), 400

        success, message = blockchain.create_stable_coin(
            data["name"],
            data["symbol"],
            float(data.get("collateral_ratio", 1.0)),
            data["backed_by"],
            float(data["max_supply"]) if data.get("max_supply") is not None else None
        )
        if success:
            return jsonify({"message": message})
        else:
            return jsonify({"error": message}), 400

    @stablecoin_bp.route("/mint", methods=["POST"])
    @token_required
    @limiter.limit("20 per hour")
    def mint_stable(current_user):
        data = request.get_json() or {}
        required = ["coin_symbol", "recipient", "amount"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing: coin_symbol, recipient, amount"}), 400

        success, message = blockchain.mint_stable_coin(
            data["coin_symbol"],
            current_user,
            data["recipient"],
            float(data["amount"])
        )
        if success:
            return jsonify({"message": message})
        else:
            return jsonify({"error": message}), 400

    @stablecoin_bp.route("/authorize_minter", methods=["POST"])
    @token_required
    @limiter.limit("10 per hour")
    def authorize_minter(current_user):
        data = request.get_json() or {}
        required = ["coin_symbol", "minter_address"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing: coin_symbol, minter_address"}), 400

        success, message = blockchain.add_authorized_minter(
            data["coin_symbol"],
            data["minter_address"],
            current_user  # Use current user as authorizer
        )
        if success:
            return jsonify({"message": message})
        else:
            return jsonify({"error": message}), 400

    @stablecoin_bp.route("/stable_coins", methods=["GET"])
    def list_stable_coins():
        sc = blockchain.get_stable_coins()
        return jsonify({"stable_coins": sc, "count": len(sc)})

    return stablecoin_bp