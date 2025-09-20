import requests
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List


@dataclass
class TestResult:
    endpoint: str
    status_code: int
    response_time: float
    success: bool
    error: str = None


class SimpleStressTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.lock = threading.Lock()
    
    def create_transaction(self, client_id: int) -> TestResult:
        url = f"{self.base_url}/clientes/{client_id}/transacoes"

        transaction_data = {
            "valor": random.randint(1, 10000),
            "tipo": random.choice(["c", "d"]),
            "descricao": f"test_{random.randint(1000, 9999)}"
        }
        
        start_time = time.time()
        try:
            response = requests.post(url, json=transaction_data, timeout=10)
            response_time = time.time() - start_time
            
            return TestResult(
                endpoint="POST /transacoes",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code in [200, 201]
            )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint="POST /transacoes",
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    def get_statement(self, client_id: int) -> TestResult:
        url = f"{self.base_url}/clientes/{client_id}/extrato"
        
        start_time = time.time()
        try:
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            
            return TestResult(
                endpoint="GET /extrato",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200
            )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint="GET /extrato",
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    def run_client_requests(self, client_id: int, num_requests: int):
        for _ in range(num_requests):
            if random.choice([True, False]):
                result = self.create_transaction(client_id)
            else:
                result = self.get_statement(client_id)
            
            with self.lock:
                self.results.append(result)
    
    def run_stress_test(self, num_clients: int = 5, requests_per_client: int = 20, max_workers: int = 10):
        print(f"🚀 Starting simple stress test...")
        print(f"📊 Configuration:")
        print(f"   - Clients: {num_clients}")
        print(f"   - Requests per client: {requests_per_client}")
        print(f"   - Max concurrent workers: {max_workers}")
        print(f"   - Total requests: {num_clients * requests_per_client}")
        print(f"   - Base URL: {self.base_url}")
        print()
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for concurrent execution
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks for each client
            futures = [
                executor.submit(self.run_client_requests, client_id, requests_per_client)
                for client_id in range(1, num_clients + 1)
            ]
            
            # Wait for all tasks to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in worker thread: {e}")
        
        total_time = time.time() - start_time
        self.print_results(total_time)
    
    def print_results(self, total_time: float):
        print("=" * 60)
        print("📈 STRESS TEST RESULTS")
        print("=" * 60)
        
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests

        response_times = [r.response_time for r in self.results if r.success]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0

        status_codes = {}
        for result in self.results:
            status_codes[result.status_code] = status_codes.get(result.status_code, 0) + 1

        endpoint_stats = {}
        for result in self.results:
            if result.endpoint not in endpoint_stats:
                endpoint_stats[result.endpoint] = {"total": 0, "success": 0}
            endpoint_stats[result.endpoint]["total"] += 1
            if result.success:
                endpoint_stats[result.endpoint]["success"] += 1
        
        print(f"⏱️  Total execution time: {total_time:.2f} seconds")
        print(f"📊 Total requests: {total_requests}")
        print(f"✅ Successful requests: {successful_requests} ({successful_requests/total_requests*100:.1f}%)")
        print(f"❌ Failed requests: {failed_requests} ({failed_requests/total_requests*100:.1f}%)")
        print(f"🚀 Requests per second: {total_requests/total_time:.2f}")
        print()
        
        print("⏱️  Response Times:")
        print(f"   - Average: {avg_response_time*1000:.2f} ms")
        print(f"   - Minimum: {min_response_time*1000:.2f} ms")
        print(f"   - Maximum: {max_response_time*1000:.2f} ms")
        print()
        
        print("📊 Status Codes:")
        for status_code, count in sorted(status_codes.items()):
            print(f"   - {status_code}: {count} requests")
        print()
        
        print("🎯 Endpoint Statistics:")
        for endpoint, stats in endpoint_stats.items():
            success_rate = stats["success"] / stats["total"] * 100
            print(f"   - {endpoint}: {stats['success']}/{stats['total']} ({success_rate:.1f}% success)")

        errors = [r for r in self.results if not r.success and r.error]
        if errors:
            print()
            print("❌ Errors (first 10):")
            for error in errors[:10]:
                print(f"   - {error.endpoint}: {error.error}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple API Stress Test")
    parser.add_argument("--url", default="http://localhost:9999", help="Base URL of the API")
    parser.add_argument("--clients", type=int, default=5, help="Number of different client IDs to test")
    parser.add_argument("--requests", type=int, default=20, help="Number of requests per client")
    parser.add_argument("--workers", type=int, default=10, help="Number of concurrent workers")
    
    args = parser.parse_args()
    
    tester = SimpleStressTester(args.url)
    tester.run_stress_test(
        num_clients=args.clients,
        requests_per_client=args.requests,
        max_workers=args.workers
    )


if __name__ == "__main__":
    main()
