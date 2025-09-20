# Stress Test Scripts

This directory contains two stress test scripts to test your Rinha de Backend API:

## 1. Simple Stress Test (`simple_stress_test.py`)

A synchronous stress test using the `requests` library. Easier to set up and understand.

### Usage:

```bash
# Install dependencies first
pip install requests

# Basic test (5 clients, 20 requests each)
python simple_stress_test.py

# Custom configuration
python simple_stress_test.py --clients 10 --requests 50 --workers 20

# Test different URL
python simple_stress_test.py --url http://localhost:8081
```

### Parameters:
- `--url`: Base URL of your API (default: http://localhost:8000)
- `--clients`: Number of different client IDs to test (default: 5)
- `--requests`: Number of requests per client (default: 20)
- `--workers`: Number of concurrent workers (default: 10)

## 2. Advanced Stress Test (`stress_test.py`)

An asynchronous stress test using `aiohttp` for better performance and higher concurrency.

### Usage:

```bash
# Install dependencies first
pip install aiohttp

# Basic test (5 clients, 50 requests each)
python stress_test.py

# High load test
python stress_test.py --clients 20 --requests 100 --concurrent 50

# Test different URL
python stress_test.py --url http://localhost:8081
```

### Parameters:
- `--url`: Base URL of your API (default: http://localhost:8000)
- `--clients`: Number of different client IDs to test (default: 5)
- `--requests`: Number of requests per client (default: 50)
- `--concurrent`: Number of concurrent clients (default: 10)

## What the tests do:

Both scripts test your API by:

1. **Creating random transactions** via `POST /clientes/{id}/transacoes`
   - Random amounts (1-10000)
   - Random types (credit 'c' or debit 'd')
   - Random descriptions

2. **Retrieving client statements** via `GET /clientes/{id}/extrato`

3. **Measuring performance**:
   - Response times
   - Success/failure rates
   - Requests per second
   - Status code distribution
   - Error reporting

## Before running the tests:

1. **Start your database:**
   ```bash
   docker-compose up -d db
   ```

2. **Start your API:**
   ```bash
   fastapi dev src/main.py
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Make sure you have some test clients in your database** (the scripts test client IDs 1-5 by default)

## Example output:

```
🚀 Starting simple stress test...
📊 Configuration:
   - Clients: 5
   - Requests per client: 20
   - Max concurrent workers: 10
   - Total requests: 100
   - Base URL: http://localhost:8000

============================================================
📈 STRESS TEST RESULTS
============================================================
⏱️  Total execution time: 2.45 seconds
📊 Total requests: 100
✅ Successful requests: 95 (95.0%)
❌ Failed requests: 5 (5.0%)
🚀 Requests per second: 40.82

⏱️  Response Times:
   - Average: 245.67 ms
   - Minimum: 12.34 ms
   - Maximum: 1234.56 ms

📊 Status Codes:
   - 200: 95 requests
   - 404: 3 requests
   - 422: 2 requests

🎯 Endpoint Statistics:
   - POST /transacoes: 48/50 (96.0% success)
   - GET /extrato: 47/50 (94.0% success)
```

## Tips:

- Start with the simple test to verify your API works
- Use the advanced test for higher load testing
- Monitor your database and API logs while testing
- Adjust the parameters based on your system capabilities
