# 🪙 CAD-COIN Blockchain - Ultra Robust Version

[![Version](https://img.shields.io/badge/version-3.0--UltraRobust-blue.svg)](https://github.com/spboucher/cadcoin-blockchain)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Security](https://img.shields.io/badge/security-enhanced-red.svg)](#security-features)
[![Architecture](https://img.shields.io/badge/architecture-modular-purple.svg)](#project-structure)

> **Author**: Simon-Pierre Boucher, Université Laval  
> **Purpose**: A robust, production-ready blockchain implementation with advanced mining, stablecoins, and comprehensive API.

![CAD-COIN Logo](https://img.shields.io/badge/🍁-CAD--COIN-ff6b35?style=for-the-badge)

---

## 🌟 Features

### 🔥 Core Blockchain Features
- ✅ **Adaptive Difficulty Adjustment** - Dynamic mining difficulty based on network performance
- ✅ **Progressive Reward Halving** - Bitcoin-style reward reduction every 100 blocks  
- ✅ **Enhanced Validation System** - Multi-layer transaction and block validation
- ✅ **Chain Integrity Verification** - Continuous blockchain validation
- ✅ **Transaction Fee System** - Priority-based transaction processing
- ✅ **Mining Timeout Protection** - Prevents infinite mining loops
- ✅ **Advanced Caching** - Redis-powered performance optimization

### 💰 Financial Features  
- 🪙 **CAD-COIN Native Currency** - Canadian Dollar-backed digital currency
- 🏛️ **Stablecoin Support** - Create and manage multiple stablecoins
- 👥 **Authorized Minting** - Controlled token creation system
- 💳 **Multi-currency Balances** - Support for multiple token types
- 📊 **Mining Statistics** - Comprehensive network analytics

### 🛡️ Security & Performance
- 🔐 **JWT Authentication** - Secure API access with tokens
- ⚡ **Rate Limiting** - Protection against API abuse
- 🚀 **PostgreSQL Backend** - Robust, ACID-compliant database
- 💾 **Redis Caching** - High-performance data caching
- 📈 **Horizontal Scaling** - Modular architecture ready for scaling

---

## 🏗️ Project Structure

```
📦 cadcoin_blockchain/
├── 📁 src/
│   ├── 📁 config/          # 🔧 Configuration management
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── 📁 database/        # 🗄️ Database layer
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── 📁 cache/           # 💾 Redis caching
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── 📁 models/          # 🧱 Core blockchain models
│   │   ├── __init__.py
│   │   ├── transaction.py
│   │   ├── block.py
│   │   └── blockchain.py
│   ├── 📁 api/             # 🌐 REST API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── blockchain_routes.py
│   │   └── stablecoin_routes.py
│   └── 📁 utils/           # 🔧 Utility functions
│       └── __init__.py
├── 📄 main.py              # 🚀 Application entry point
├── 📄 requirements.txt     # 📦 Python dependencies
└── 📄 README.md           # 📖 This file
```

---

## 🚀 Quick Start

### Prerequisites
![Docker](https://img.shields.io/badge/docker-optional-blue?logo=docker)
![PostgreSQL](https://img.shields.io/badge/postgresql-14+-336791?logo=postgresql)
![Redis](https://img.shields.io/badge/redis-6+-dc382d?logo=redis)
![Python](https://img.shields.io/badge/python-3.8+-3776ab?logo=python)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/spboucher/cadcoin-blockchain.git
   cd cadcoin-blockchain
   ```

2. **Install Dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Database**
   ```bash
   # PostgreSQL
   createdb blockchain_db
   
   # Redis
   sudo systemctl start redis-server  # Linux
   brew services start redis          # macOS
   ```

4. **Configure Environment**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/blockchain_db"
   export REDIS_URL="redis://localhost:6379/0"
   export JWT_SECRET_KEY="your-ultra-secure-secret-key"
   export BASE_MINING_REWARD="50.0"
   export BASE_DIFFICULTY="4"
   export PORT="80"
   ```

5. **Start the Server**
   ```bash
   python3 main.py
   ```

   🌐 **Server runs at**: `http://localhost:80`

---

## 📡 API Endpoints

### 🔐 Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/auth/register` | Create new user account | ❌ |
| `POST` | `/auth/login` | Login and get JWT token | ❌ |

### ⛓️ Blockchain Operations  
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | Server info and features | ❌ |
| `GET` | `/info` | Detailed blockchain stats | ❌ |
| `GET` | `/chain` | Get blocks (paginated) | ❌ |
| `GET` | `/balance/<address>` | Get all balances | ❌ |
| `GET` | `/balance/<address>/<coin>` | Get specific balance | ❌ |
| `POST` | `/transaction` | Create transaction | ✅ |
| `POST` | `/mine` | Mine new block | ✅ |

### 🪙 Stablecoin Management
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/stable_coin` | Create new stablecoin | ✅ |
| `POST` | `/mint` | Mint tokens | ✅ |
| `POST` | `/authorize_minter` | Authorize minter | ✅ |
| `GET` | `/stable_coins` | List all stablecoins | ❌ |

### 📊 Operations & Monitoring
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/pending_transactions` | List pending transactions | ❌ |
| `GET` | `/health` | System health check | ❌ |
| `GET` | `/validate_chain` | Verify chain integrity | ❌ |
| `GET` | `/mining_stats` | Mining statistics | ❌ |

---

## 💡 Usage Examples

### 🔑 Basic User Operations

#### Create Users
```bash
# Create Alice
curl -X POST http://localhost:80/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "address": "alice123",
    "password": "secure_password"
  }'

# Create Bob  
curl -X POST http://localhost:80/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "address": "bob456", 
    "password": "another_password"
  }'
```

#### Get Authentication Tokens
```bash
# Alice login
ALICE_TOKEN=$(curl -s -X POST http://localhost:80/auth/login \
  -H "Content-Type: application/json" \
  -d '{"address":"alice123","password":"secure_password"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

# Bob login
BOB_TOKEN=$(curl -s -X POST http://localhost:80/auth/login \
  -H "Content-Type: application/json" \
  -d '{"address":"bob456","password":"another_password"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
```

### ⛏️ Mining Operations

#### Mine Your First Block
```bash
# Alice mines a block (gets 50 CAD-COIN reward)
curl -X POST http://localhost:80/mine \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "message": "Mined block 1. Reward: 50.00000000 CAD-COIN. Difficulty: 4, Time: 2.34s",
  "miner": "alice123"
}
```

#### Check Balance
```bash
curl http://localhost:80/balance/alice123
```

**Response:**
```json
{
  "address": "alice123",
  "balances": {
    "CAD-COIN": 50.0
  },
  "total_coins": 1,
  "total_value_cad": 50.0
}
```

### 💸 Transfer Tokens

#### Send CAD-COIN from Alice to Bob
```bash
curl -X POST http://localhost:80/transaction \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver": "bob456",
    "amount": 10.0,
    "coin_type": "CAD-COIN",
    "fee": 0.01
  }'
```

#### Mine the Transaction
```bash
# Anyone can mine pending transactions
curl -X POST http://localhost:80/mine \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json"
```

#### Verify Final Balances
```bash
# Alice's balance (50 - 10 - 0.01 + mining_reward)
curl http://localhost:80/balance/alice123

# Bob's balance (10)  
curl http://localhost:80/balance/bob456
```

### 🪙 Stablecoin Operations

#### Create a New Stablecoin
```bash
curl -X POST http://localhost:80/stable_coin \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "USD Coin",
    "symbol": "USDC", 
    "backed_by": "USD",
    "collateral_ratio": 1.0,
    "max_supply": 1000000
  }'
```

#### Authorize Minter
```bash
curl -X POST http://localhost:80/authorize_minter \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "coin_symbol": "USDC",
    "minter_address": "alice123"
  }'
```

#### Mint Tokens
```bash
curl -X POST http://localhost:80/mint \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "coin_symbol": "USDC",
    "recipient": "bob456", 
    "amount": 100
  }'
```

---

## ⛏️ Mining Guide

### 🎯 Mining Strategy

Mining in CAD-COIN is **always profitable** as rewards are guaranteed even with empty blocks:

- **Base Reward**: 50.0 CAD-COIN per block
- **Halving Schedule**: Every 100 blocks (50 → 25 → 12.5...)
- **Transaction Fees**: Added to base reward
- **Minimum Fee**: 0.001 CAD-COIN per transaction

### 🤖 Automated Mining Script

Create `auto_miner.py`:
```python
#!/usr/bin/env python3
import requests
import time
import sys

# Configuration
API_BASE = "http://localhost:80"
TOKEN = "YOUR_JWT_TOKEN_HERE"
MINER_ADDRESS = "your_address"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def get_chain_info():
    try:
        response = requests.get(f"{API_BASE}/info")
        return response.json()
    except Exception as e:
        print(f"❌ Error getting chain info: {e}")
        return None

def mine_block():
    try:
        response = requests.post(f"{API_BASE}/mine", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Block mined! {result['message']}")
            return True
        else:
            error = response.json().get('error', 'Unknown error')
            print(f"⚠️ Mining failed: {error}")
            return False
    except Exception as e:
        print(f"❌ Mining error: {e}")
        return False

def check_balance():
    try:
        response = requests.get(f"{API_BASE}/balance/{MINER_ADDRESS}")
        if response.status_code == 200:
            balance_info = response.json()
            total_cad = balance_info.get('total_value_cad', 0)
            print(f"💰 Current balance: {total_cad:.8f} CAD total")
        return True
    except Exception as e:
        print(f"❌ Balance check error: {e}")
        return False

def main():
    print("🚀 Starting CAD-COIN Auto Miner")
    print(f"👤 Miner: {MINER_ADDRESS}")
    
    while True:
        try:
            info = get_chain_info()
            if info:
                print(f"📊 Block: {info['chain_length']}")
                print(f"🎯 Difficulty: {info['current_difficulty']}")
                print(f"💎 Reward: {info['current_mining_reward']} CAD-COIN")
                print(f"⏳ Pending: {info['pending_transactions']} transactions")
                
                print("⛏️ Attempting to mine...")
                success = mine_block()
                
                if success:
                    check_balance()
                    time.sleep(5)
                else:
                    time.sleep(15)
            else:
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n⏹️ Miner stopped by user")
            break
        except Exception as e:
            print(f"❌ General error: {e}")
            time.sleep(15)

if __name__ == "__main__":
    main()
```

**Run the miner:**
```bash
python3 auto_miner.py
```

### 📊 Monitor Network Stats
```bash
# Get mining statistics  
curl http://localhost:80/mining_stats

# Check chain health
curl http://localhost:80/validate_chain

# View pending transactions
curl http://localhost:80/pending_transactions?limit=10
```

---

## 🔧 Configuration

### Environment Variables
```bash
# Database
export DATABASE_URL="postgresql://user:pass@localhost/blockchain_db"
export REDIS_URL="redis://localhost:6379/0"

# Security  
export JWT_SECRET_KEY="ultra-secure-secret-key"
export JWT_EXPIRES_HOURS="24"

# Mining Configuration
export BASE_MINING_REWARD="50.0"
export BASE_DIFFICULTY="4" 
export MAX_DIFFICULTY="20"
export DIFFICULTY_ADJUSTMENT_INTERVAL="10"
export HALVING_INTERVAL="100"
export TARGET_BLOCK_TIME="10"
export MINING_TIMEOUT="300"

# Transaction Limits
export MIN_TRANSACTION_FEE="0.001"
export MAX_PENDING_TRANSACTIONS="1000"
export MAX_BLOCK_SIZE="100"

# Server
export HOST="0.0.0.0"
export PORT="80"
export DEBUG="0"
```

### Performance Tuning

#### PostgreSQL Optimization
```sql
-- Optimize for frequent writes
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET random_page_cost = 1.1;
SELECT pg_reload_conf();
```

#### Redis Configuration
```redis
# In redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

---

## 🛡️ Security Features

### 🔐 Authentication & Authorization
- **JWT Tokens**: Secure API access with configurable expiration
- **Password Hashing**: bcrypt with salt for user passwords  
- **Rate Limiting**: Protection against API abuse and spam
- **Input Validation**: Comprehensive data validation on all endpoints

### 🛡️ Blockchain Security
- **Chain Integrity**: Continuous validation of block relationships
- **Transaction Validation**: Multi-layer verification before mining
- **Mining Protection**: Timeout prevention for infinite loops
- **Fee Requirements**: Minimum transaction fees prevent spam

### 🔒 Infrastructure Security
- **Database Prepared Statements**: SQL injection protection
- **CORS Configuration**: Cross-origin request management
- **Error Handling**: Secure error responses without data leakage
- **Environment Separation**: Configuration via environment variables

---

## 🧪 Testing

### Health Check
```bash
curl http://localhost:80/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "ok", 
  "cache": "ok",
  "chain_integrity": "valid",
  "validation_message": "Chain integrity validated",
  "version": "3.0-UltraRobust",
  "timestamp": 1693747200.123
}
```

### Chain Validation
```bash
curl http://localhost:80/validate_chain?depth=10
```

### Performance Testing
```bash
# Test transaction throughput
for i in {1..10}; do
  curl -X POST http://localhost:80/transaction \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"receiver\":\"test$i\",\"amount\":1,\"fee\":0.001}"
done
```

---

## 🐛 Troubleshooting

### Common Issues

#### ❌ "No pending transactions"
**Cause**: No transactions to mine  
**Solution**: Create transactions or mine empty blocks for rewards

#### ❌ "Mining failed or timed out"  
**Solutions**:
```bash
# Reduce difficulty
export BASE_DIFFICULTY="3"

# Increase timeout
export MINING_TIMEOUT="600"

# Increase target block time  
export TARGET_BLOCK_TIME="20"
```

#### ❌ "Token expired"
**Solution**: Re-login to get new token
```bash
curl -X POST http://localhost:80/auth/login \
  -H "Content-Type: application/json" \
  -d '{"address":"your_address","password":"your_password"}'
```

#### ❌ Database Connection Errors
```bash
# Test PostgreSQL connection
psql -h localhost -U your_user -d blockchain_db -c "SELECT 1;"

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### ❌ Redis Connection Errors  
```bash
# Test Redis connection
redis-cli ping

# Restart Redis
sudo systemctl restart redis
```

### Performance Optimization

#### Monitor Resource Usage
```bash
# CPU usage
htop

# Memory usage  
free -h

# Disk I/O
iostat -x 1
```

#### System Tuning
```bash
# Increase file limits
ulimit -n 4096

# Process priority
nice -n -10 python3 main.py
```

---

## 📈 Architecture & Scaling

### 🏗️ Modular Design
- **Separation of Concerns**: Each module handles specific functionality
- **Loose Coupling**: Modules communicate through well-defined interfaces
- **High Cohesion**: Related functionality grouped together
- **Extensible**: Easy to add new features and modules

### 📊 Scalability Considerations
- **Database Connection Pooling**: Ready for connection pool implementation
- **Horizontal Scaling**: Stateless API design supports load balancing
- **Caching Strategy**: Redis caching reduces database load
- **Asynchronous Processing**: Mining operations can be offloaded to workers

### 🔄 Future Enhancements
- 🌐 **Network P2P**: Distributed node communication
- 🔄 **Consensus Algorithms**: PBFT, PoS implementation options
- 📱 **Mobile APIs**: GraphQL endpoint support
- 🔍 **Analytics Dashboard**: Web-based monitoring interface
- 🐳 **Containerization**: Docker and Kubernetes deployment

---

## 📚 Additional Resources

### 📖 Extended Documentation
- Complete mining tutorial with automated scripts
- Detailed API examples with real token transfers  
- Performance optimization guides
- Security best practices

### 🔗 Useful Links
- **PostgreSQL**: https://postgresql.org/
- **Redis**: https://redis.io/
- **Flask**: https://flask.palletsprojects.com/
- **JWT**: https://jwt.io/

### 📞 Support
- **Issues**: [GitHub Issues](https://github.com/spboucher/cadcoin-blockchain/issues)
- **Documentation**: Complete API docs at `http://localhost:80/`
- **Logs**: System logs in `blockchain.log`

---

## 👨‍💻 Author

**Simon-Pierre Boucher**  
🏫 Université Laval  
📧 Contact via GitHub Issues  
🇨🇦 Québec, Canada

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Université Laval for academic support
- The Flask and PostgreSQL communities
- Blockchain research community
- Canadian fintech innovation ecosystem

---

<div align="center">

### 🍁 Made in Canada with ❤️

![Canada](https://img.shields.io/badge/Made%20in-Canada-red?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuNzUgOC4yNUwyMSA4TDE0LjI1IDEyTDE2IDIwTDEyIDEyTDggMjBMOS43NSAxMkwzIDhMMTAuMjUgOC4yNUwxMiAyWiIgZmlsbD0iI0ZGMDAwMCIvPgo8L3N2Zz4K)

**⭐ Star this repository if you found it helpful!**

</div>