#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Transaction model for CAD-COIN Blockchain
"""

import time
import uuid
import json
import hashlib
from typing import Tuple


class Transaction:
    def __init__(self, sender: str, receiver: str, amount: float, coin_type: str = "CAD-COIN",
                 transaction_type: str = "transfer", metadata: dict = None, fee: float = 0.0):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.amount = float(amount)
        self.fee = float(fee)
        self.coin_type = coin_type
        self.transaction_type = transaction_type
        self.metadata = metadata or {}
        self.timestamp = time.time()

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "fee": self.fee,
            "coin_type": self.coin_type,
            "transaction_type": self.transaction_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

    def get_hash(self):
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()

    def is_valid(self) -> Tuple[bool, str]:
        """Enhanced transaction validation"""
        if self.amount <= 0:
            return False, "Amount must be positive"
        
        if self.fee < 0:
            return False, "Fee cannot be negative"
        
        if len(self.sender) < 3 or len(self.receiver) < 3:
            return False, "Invalid address format"
        
        if self.sender == self.receiver and self.transaction_type == "transfer":
            return False, "Cannot transfer to self"
        
        return True, "Valid"