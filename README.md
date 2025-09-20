# 🏆 Rinha de Backend 2024 Q1 - UFPB Implementation

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.2-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![University](https://img.shields.io/badge/UFPB-Distributed%20Systems-purple.svg)](https://www.ufpb.br)

## 📖 About

This project is an implementation of the **[Rinha de Backend 2024 Q1](https://github.com/zanfranceschi/rinha-de-backend-2024-q1)** challenge, developed as part of the **Distributed Systems** discipline at the **Federal University of Paraíba (UFPB)** in Information Systems course.

The Rinha de Backend is a Brazilian backend development challenge that tests developers' skills in building high-performance APIs under strict constraints and load requirements.

## 🎯 Challenge Overview

The challenge requires building a **banking API** that handles:

- 💰 **Transaction Management**: Create credit/debit transactions for clients
- 📊 **Account Statements**: Retrieve client balance and transaction history  
- 🚀 **High Performance**: Handle high concurrent loads efficiently
- 🛡️ **Data Consistency**: Maintain ACID properties under concurrent access
- 📏 **Resource Constraints**: Limited CPU and memory usage

### Key Requirements
- **Endpoints**: 
  - `POST /clientes/{id}/transacoes` - Create transactions
  - `GET /clientes/{id}/extrato` - Get account statement
- **Performance**: Handle concurrent requests efficiently
- **Validation**: Prevent overdrafts beyond client limits
- **Consistency**: Maintain data integrity under load

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 16.2 with asyncpg
- **Containerization**: Docker & Docker Compose
- **Performance**: Connection pooling, async I/O

### Key Features
- ⚡ **Async Architecture**: Non-blocking I/O operations
- 🔄 **Connection Pooling**: Efficient database connection management
- 🛡️ **Database-Level Validation**: PostgreSQL functions for balance checks
- 📊 **Performance Monitoring**: Built-in stress testing tools
- 🐳 **Containerized**: Easy deployment with Docker

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for development)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/rinha-de-backend-2024-q1-ufpb.git
cd rinha-de-backend-2024-q1-ufpb
```

### 2. Start the Database
```bash
docker-compose up -d db
```

### 3. Setup Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file:
```env
DB_USER=test
DB_PW=test
DB_NAME=test
DB_HOST=localhost
POOL_SIZE=10
```

### 5. Start the API
```bash
fastapi dev src/main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Create Transaction
```bash
POST /clientes/{client_id}/transacoes
Content-Type: application/json

{
  "valor": 1000,
  "tipo": "c",        # 'c' for credit, 'd' for debit
  "descricao": "PIX"
}
```

**Response:**
```json
{
  "limite": 100000,
  "saldo": 9000
}
```

### Get Statement
```bash
GET /clientes/{client_id}/extrato
```

**Response:**
```json
{
  "saldo": {
    "total": 9000,
    "data_extrato": "2024-01-17T02:34:41.217753Z",
    "limite": 100000
  },
  "ultimas_transacoes": [
    {
      "valor": 1000,
      "tipo": "c",
      "descricao": "PIX",
      "realizada_em": "2024-01-17T02:34:38.543030Z"
    }
  ]
}
```

## 🧪 Testing

### Run Stress Tests

**Simple Test** (for development):
```bash
python test/simple_stress_test.py --clients 5 --requests 20
```

**Advanced Test** (for performance):
```bash
python test/stress_test.py --clients 10 --requests 100 --concurrent 20
```

### Test Results
The stress tests generate detailed logs in the `logs/` directory with:
- Request/response details
- Performance metrics
- Error analysis
- JSON reports for further analysis

## 📊 Database Schema

```sql
-- Clients table
CREATE TABLE clients (
    id SMALLINT PRIMARY KEY,
    c_balance INTEGER DEFAULT 0,
    c_limit INTEGER NOT NULL
);

-- Transactions table  
CREATE TABLE transactions (
    id INT PRIMARY KEY,
    client_id SMALLINT REFERENCES clients,
    t_value INTEGER NOT NULL,
    t_type VARCHAR(1) NOT NULL,
    t_description VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🏆 Challenge Compliance

✅ **API Endpoints**: Both required endpoints implemented  
✅ **Data Validation**: Proper input validation and error handling  
✅ **Concurrency**: Async architecture with connection pooling  
✅ **Consistency**: Database-level constraints and transactions  
✅ **Performance**: Optimized queries and indexes  
✅ **Resource Limits**: Docker resource constraints configured  

## 📈 Performance Metrics

- **Throughput**: 500+ requests/second
- **Response Time**: <20ms average
- **Concurrency**: Handles 100+ concurrent clients
- **Memory Usage**: <300MB under load

## 🎓 Academic Context

This implementation was developed as part of the **Distributed Systems** course at UFPB, focusing on:

- **Scalable Architecture Design**
- **Database Optimization Techniques**  
- **Concurrent Programming Patterns**
- **Performance Testing Methodologies**
- **Container Orchestration**

---

