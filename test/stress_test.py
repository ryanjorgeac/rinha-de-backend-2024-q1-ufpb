import asyncio
import aiohttp
import time
import random
import json
import logging
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class TestResult:
    endpoint: str
    status_code: int
    response_time: float
    success: bool
    client_id: int
    timestamp: str
    request_data: dict = None
    response_data: str = None
    error: str = None


class APIStressTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.setup_logging()
        
    def setup_logging(self):
        os.makedirs("logs", exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"logs/stress_test_{timestamp}.log"
        self.logger = logging.getLogger('stress_test')
        self.logger.setLevel(logging.INFO)
        
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.log_filename = log_filename
        print(f"📝 Logging detailed results to: {log_filename}")
        self.logger.info(f"Stress test started - Logging to {log_filename}")
        
    async def create_transaction(self, session: aiohttp.ClientSession, client_id: int) -> TestResult:
        url = f"{self.base_url}/clientes/{client_id}/transacoes"

        transaction_data = {
            "valor": random.randint(1, 10000),
            "tipo": random.choice(["c", "d"]),  # credit or debit
            "descricao": f"test_{random.randint(1000, 9999)}"
        }
        
        timestamp = datetime.now().isoformat()
        start_time = time.time()
        
        try:
            async with session.post(url, json=transaction_data) as response:
                response_time = time.time() - start_time
                response_text = await response.text()
                
                result = TestResult(
                    endpoint="POST /transacoes",
                    status_code=response.status,
                    response_time=response_time,
                    success=response.status in [200, 201],
                    client_id=client_id,
                    timestamp=timestamp,
                    request_data=transaction_data,
                    response_data=response_text[:500]  # Limit response size
                )

                self.logger.info(
                    f"POST /clientes/{client_id}/transacoes | "
                    f"Status: {response.status} | "
                    f"Time: {response_time*1000:.2f}ms | "
                    f"Request: {json.dumps(transaction_data)} | "
                    f"Response: {response_text[:200]}..."
                )
                
                return result
                
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = str(e)
            
            result = TestResult(
                endpoint="POST /transacoes",
                status_code=0,
                response_time=response_time,
                success=False,
                client_id=client_id,
                timestamp=timestamp,
                request_data=transaction_data,
                error=error_msg
            )

            self.logger.error(
                f"POST /clientes/{client_id}/transacoes | "
                f"ERROR: {error_msg} | "
                f"Time: {response_time*1000:.2f}ms | "
                f"Request: {json.dumps(transaction_data)}"
            )
            
            return result
    
    async def get_statement(self, session: aiohttp.ClientSession, client_id: int) -> TestResult:
        url = f"{self.base_url}/clientes/{client_id}/extrato"
        
        timestamp = datetime.now().isoformat()
        start_time = time.time()
        
        try:
            async with session.get(url) as response:
                response_time = time.time() - start_time
                response_text = await response.text()
                
                result = TestResult(
                    endpoint="GET /extrato",
                    status_code=response.status,
                    response_time=response_time,
                    success=response.status == 200,
                    client_id=client_id,
                    timestamp=timestamp,
                    response_data=response_text[:500]  # Limit response size
                )

                self.logger.info(
                    f"GET /clientes/{client_id}/extrato | "
                    f"Status: {response.status} | "
                    f"Time: {response_time*1000:.2f}ms | "
                    f"Response: {response_text[:200]}..."
                )
                
                return result
                
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = str(e)
            
            result = TestResult(
                endpoint="GET /extrato",
                status_code=0,
                response_time=response_time,
                success=False,
                client_id=client_id,
                timestamp=timestamp,
                error=error_msg
            )

            self.logger.error(
                f"GET /clientes/{client_id}/extrato | "
                f"ERROR: {error_msg} | "
                f"Time: {response_time*1000:.2f}ms"
            )
            
            return result
    
    async def run_single_client_test(self, session: aiohttp.ClientSession, client_id: int, num_requests: int):
        self.logger.info(f"Starting tests for client {client_id} - {num_requests} requests")
        tasks = []
        
        for _ in range(num_requests):
            if random.choice([True, False]):
                tasks.append(self.create_transaction(session, client_id))
            else:
                tasks.append(self.get_statement(session, client_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, TestResult):
                self.results.append(result)
            else:
                error_result = TestResult(
                    endpoint="UNKNOWN",
                    status_code=0,
                    response_time=0,
                    success=False,
                    client_id=client_id,
                    timestamp=datetime.now().isoformat(),
                    error=str(result)
                )
                self.results.append(error_result)
                self.logger.error(f"Unexpected error for client {client_id}: {result}")
        
        self.logger.info(f"Completed tests for client {client_id}")
    
    async def run_stress_test(self, num_clients: int = 5, requests_per_client: int = 50, concurrent_clients: int = 10):
        config_info = {
            "clients": num_clients,
            "requests_per_client": requests_per_client,
            "concurrent_clients": concurrent_clients,
            "total_requests": num_clients * requests_per_client,
            "base_url": self.base_url
        }
        
        self.logger.info(f"Stress test configuration: {json.dumps(config_info, indent=2)}")
        
        print(f"🚀 Starting stress test...")
        print(f"📊 Configuration:")
        print(f"   - Clients: {num_clients}")
        print(f"   - Requests per client: {requests_per_client}")
        print(f"   - Concurrent clients: {concurrent_clients}")
        print(f"   - Total requests: {num_clients * requests_per_client}")
        print(f"   - Base URL: {self.base_url}")
        print()
        
        start_time = time.time()

        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            semaphore = asyncio.Semaphore(concurrent_clients)
            
            async def run_client_with_semaphore(client_id):
                async with semaphore:
                    await self.run_single_client_test(session, client_id, requests_per_client)

            client_tasks = [
                run_client_with_semaphore(client_id) 
                for client_id in range(1, num_clients + 1)
            ]
            
            await asyncio.gather(*client_tasks)
        
        total_time = time.time() - start_time
        self.save_detailed_results()
        self.print_results(total_time)
    
    def save_detailed_results(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"logs/stress_test_results_{timestamp}.json"
        
        results_data = {
            "test_summary": {
                "total_requests": len(self.results),
                "successful_requests": sum(1 for r in self.results if r.success),
                "failed_requests": sum(1 for r in self.results if not r.success),
                "test_timestamp": datetime.now().isoformat()
            },
            "detailed_results": [asdict(result) for result in self.results]
        }
        
        with open(json_filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"📊 Detailed results saved to: {json_filename}")
        self.logger.info(f"Detailed results saved to: {json_filename}")
    
    def print_results(self, total_time: float):
        self.logger.info("=" * 60)
        self.logger.info("STRESS TEST RESULTS SUMMARY")
        self.logger.info("=" * 60)
        
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

        self.logger.info(f"Total execution time: {total_time:.2f} seconds")
        self.logger.info(f"Total requests: {total_requests}")
        self.logger.info(f"Successful requests: {successful_requests} ({successful_requests/total_requests*100:.1f}%)")
        self.logger.info(f"Failed requests: {failed_requests} ({failed_requests/total_requests*100:.1f}%)")
        self.logger.info(f"Requests per second: {total_requests/total_time:.2f}")
        self.logger.info(f"Average response time: {avg_response_time*1000:.2f} ms")
        
        for status_code, count in sorted(status_codes.items()):
            self.logger.info(f"Status {status_code}: {count} requests")

        errors = [r for r in self.results if not r.success and r.error]
        if errors:
            print()
            print("❌ Errors (first 10):")
            for error in errors[:10]:
                print(f"   - {error.endpoint}: {error.error}")
            
            self.logger.warning(f"Total errors: {len(errors)}")
            for error in errors:
                self.logger.error(f"{error.endpoint} - Client {error.client_id}: {error.error}")
        
        print(f"\n📝 Check {self.log_filename} for detailed logs")
        self.logger.info("Stress test completed")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="API Stress Test for Rinha de Backend")
    parser.add_argument("--url", default="http://localhost:9999", help="Base URL of the API")
    parser.add_argument("--clients", type=int, default=5, help="Number of different client IDs to test")
    parser.add_argument("--requests", type=int, default=50, help="Number of requests per client")
    parser.add_argument("--concurrent", type=int, default=10, help="Number of concurrent clients")
    
    args = parser.parse_args()
    
    tester = APIStressTester(args.url)
    await tester.run_stress_test(
        num_clients=args.clients,
        requests_per_client=args.requests,
        concurrent_clients=args.concurrent
    )


if __name__ == "__main__":
    asyncio.run(main())
