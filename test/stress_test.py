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
    def __init__(self, base_url: str = "http://localhost:9999"):
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
        console_handler.setLevel(logging.INFO)  # Changed to INFO to see more output

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
        start_time = time.perf_counter()
        
        try:
            async with session.post(url, json=transaction_data) as response:
                response_text = await response.text()
                response_time = time.perf_counter() - start_time
                
                result = TestResult(
                    endpoint="POST /transacoes",
                    status_code=response.status,
                    response_time=response_time,
                    success=response.status in [200, 201],
                    client_id=client_id,
                    timestamp=timestamp,
                    request_data=transaction_data,
                    response_data=response_text[:500]
                )

                # Only log errors and warnings to console
                if result.success:
                    self.logger.debug(  # Changed to debug level
                        f"POST /clientes/{client_id}/transacoes | "
                        f"Status: {response.status} | "
                        f"Time: {response_time*1000:.2f}ms"
                    )
                else:
                    self.logger.warning(
                        f"POST /clientes/{client_id}/transacoes | "
                        f"Status: {response.status} | "
                        f"Time: {response_time*1000:.2f}ms | "
                        f"Response: {response_text[:200]}"
                    )
                
                return result
                
        except asyncio.TimeoutError:
            response_time = time.perf_counter() - start_time
            error_msg = f"TIMEOUT after {response_time:.2f}s"
            
            result = TestResult(
                endpoint="POST /transacoes",
                status_code=408,  # Request Timeout
                response_time=response_time,
                success=False,
                client_id=client_id,
                timestamp=timestamp,
                request_data=transaction_data,
                error=error_msg
            )

            self.logger.error(
                f"POST /clientes/{client_id}/transacoes | "
                f"TIMEOUT: {error_msg} | "
                f"Time: {response_time*1000:.2f}ms"
            )
            
            return result
            
        except aiohttp.ClientError as e:
            response_time = time.perf_counter() - start_time
            error_msg = f"CLIENT ERROR: {str(e)}"
            
            result = TestResult(
                endpoint="POST /transacoes",
                status_code=0,  # Connection error
                response_time=response_time,
                success=False,
                client_id=client_id,
                timestamp=timestamp,
                request_data=transaction_data,
                error=error_msg
            )

            self.logger.error(
                f"POST /clientes/{client_id}/transacoes | "
                f"CLIENT ERROR: {error_msg} | "
                f"Time: {response_time*1000:.2f}ms"
            )
            
            return result
            
        except Exception as e:
            response_time = time.perf_counter() - start_time
            error_msg = f"UNEXPECTED ERROR: {str(e)}"
            
            result = TestResult(
                endpoint="POST /transacoes",
                status_code=-1,  # Unexpected error
                response_time=response_time,
                success=False,
                client_id=client_id,
                timestamp=timestamp,
                request_data=transaction_data,
                error=error_msg
            )

            self.logger.error(
                f"POST /clientes/{client_id}/transacoes | "
                f"UNEXPECTED ERROR: {error_msg} | "
                f"Time: {response_time*1000:.2f}ms"
            )
            
            return result
    
    async def get_statement(self, session: aiohttp.ClientSession, client_id: int) -> TestResult:
        url = f"{self.base_url}/clientes/{client_id}/extrato"
        
        timestamp = datetime.now().isoformat()
        start_time = time.perf_counter()
        
        try:
            async with session.get(url) as response:
                response_text = await response.text()
                response_time = time.perf_counter() - start_time
                
                result = TestResult(
                    endpoint="GET /extrato",
                    status_code=response.status,
                    response_time=response_time,
                    success=response.status == 200,
                    client_id=client_id,
                    timestamp=timestamp,
                    response_data=response_text[:500]
                )

                if result.success:
                    self.logger.debug(
                        f"GET /clientes/{client_id}/extrato | "
                        f"Status: {response.status} | "
                        f"Time: {response_time*1000:.2f}ms"
                    )
                else:
                    self.logger.warning(
                        f"GET /clientes/{client_id}/extrato | "
                        f"Status: {response.status} | "
                        f"Time: {response_time*1000:.2f}ms | "
                        f"Response: {response_text[:200]}"
                    )
                
                return result
                
        except asyncio.TimeoutError:
            response_time = time.perf_counter() - start_time
            error_msg = f"TIMEOUT after {response_time:.2f}s"
            
            result = TestResult(
                endpoint="GET /extrato",
                status_code=408,
                response_time=response_time,
                success=False,
                client_id=client_id,
                timestamp=timestamp,
                error=error_msg
            )

            self.logger.error(
                f"GET /clientes/{client_id}/extrato | "
                f"TIMEOUT: {error_msg} | "
                f"Time: {response_time*1000:.2f}ms"
            )
            
            return result
            
        except aiohttp.ClientError as e:
            response_time = time.perf_counter() - start_time
            error_msg = f"CLIENT ERROR: {str(e)}"
            
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
                f"CLIENT ERROR: {error_msg} | "
                f"Time: {response_time*1000:.2f}ms"
            )
            
            return result
            
        except Exception as e:
            response_time = time.perf_counter() - start_time
            error_msg = f"UNEXPECTED ERROR: {str(e)}"
            
            result = TestResult(
                endpoint="GET /extrato",
                status_code=-1,
                response_time=response_time,
                success=False,
                client_id=client_id,
                timestamp=timestamp,
                error=error_msg
            )

            self.logger.error(
                f"GET /clientes/{client_id}/extrato | "
                f"UNEXPECTED ERROR: {error_msg} | "
                f"Time: {response_time*1000:.2f}ms"
            )
            
            return result
    
    async def run_single_client_test(self, session: aiohttp.ClientSession, client_id: int, num_requests: int):
        self.logger.info(f"Starting tests for client {client_id} - {num_requests} requests")
        
        for i in range(num_requests):
            if i > 0:
                await asyncio.sleep(random.uniform(0.01, 0.05))  # 10-50ms between requests

            if random.choice([True, False]):
                result = await self.create_transaction(session, client_id)
            else:
                result = await self.get_statement(session, client_id)
            
            self.results.append(result)

            if (i + 1) % 10 == 0:
                success_count = sum(1 for r in self.results[-10:] if r.success)
                self.logger.info(f"Client {client_id}: {i+1}/{num_requests} requests ({success_count}/10 recent success)")
        
        self.logger.info(f"Completed tests for client {client_id}")
    
    async def run_stress_test(self, num_clients: int = 5, requests_per_client: int = 50, concurrent_clients: int = 5):
        """Run stress test with better connection management and gradual ramp-up"""
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
        
        # Warm up the API first
        print("🔥 Warming up API...")
        await self.warmup_api()
        
        start_time = time.time()

        # Better connection configuration
        connector = aiohttp.TCPConnector(
            limit=200,                # Total connection pool size
            limit_per_host=50,        # Per host limit
            keepalive_timeout=60,     # Keep connections alive longer
            enable_cleanup_closed=True,
            use_dns_cache=True
        )
        
        # More reasonable timeouts
        timeout = aiohttp.ClientTimeout(
            total=60,      # Total timeout
            connect=10,    # Connection timeout
            sock_read=30   # Read timeout
        )
        
        async with aiohttp.ClientSession(
            connector=connector, 
            timeout=timeout,
            headers={"Connection": "keep-alive"}
        ) as session:
            semaphore = asyncio.Semaphore(concurrent_clients)
            
            async def run_client_with_semaphore(client_id):
                async with semaphore:
                    await self.run_single_client_test(session, client_id, requests_per_client)

            # Gradual ramp-up of clients
            client_tasks = []
            for client_id in range(1, num_clients + 1):
                client_tasks.append(run_client_with_semaphore(client_id))
                # Small delay between starting each client
                if client_id < num_clients:
                    await asyncio.sleep(0.1)
            
            await asyncio.gather(*client_tasks)
        
        total_time = time.time() - start_time
        self.save_detailed_results()
        self.print_results(total_time)
    
    async def warmup_api(self):
        """Warm up the API like Gatling does"""
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i in range(3):
                try:
                    async with session.get(f"{self.base_url}/clientes/1/extrato") as response:
                        if response.status == 200:
                            print(f"✅ API warmup request {i+1}/3 successful")
                        else:
                            print(f"⚠️ API warmup request {i+1}/3 returned {response.status}")
                except Exception as e:
                    print(f"❌ API warmup request {i+1}/3 failed: {e}")
                
                if i < 2:
                    await asyncio.sleep(1)
    
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

        all_response_times = [r.response_time for r in self.results]
        successful_response_times = [r.response_time for r in self.results if r.success]

        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        max_response_time = max(all_response_times) if all_response_times else 0
        min_response_time = min(all_response_times) if all_response_times else 0

        avg_success_response_time = sum(successful_response_times) / len(successful_response_times) if successful_response_times else 0

        # Calculate percentiles for successful requests
        if successful_response_times:
            sorted_times = sorted(successful_response_times)
            p50 = sorted_times[int(len(sorted_times) * 0.5)]
            p75 = sorted_times[int(len(sorted_times) * 0.75)]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]

        status_codes = {}
        for result in self.results:
            status_codes[result.status_code] = status_codes.get(result.status_code, 0) + 1

        endpoint_stats = {}
        for result in self.results:
            if result.endpoint not in endpoint_stats:
                endpoint_stats[result.endpoint] = {"total": 0, "success": 0, "response_times": []}
            endpoint_stats[result.endpoint]["total"] += 1
            if result.success:
                endpoint_stats[result.endpoint]["success"] += 1
                endpoint_stats[result.endpoint]["response_times"].append(result.response_time)

        print(f"⏱️  Total execution time: {total_time:.2f} seconds")
        print(f"📊 Total requests: {total_requests}")
        print(f"✅ Successful requests: {successful_requests} ({successful_requests/total_requests*100:.1f}%)")
        print(f"❌ Failed requests: {failed_requests} ({failed_requests/total_requests*100:.1f}%)")
        print(f"🚀 Requests per second: {total_requests/total_time:.2f}")
        print()
        
        print("⏱️  Response Times (All Requests):")
        print(f"   - Average: {avg_response_time*1000:.2f} ms")
        print(f"   - Minimum: {min_response_time*1000:.2f} ms")
        print(f"   - Maximum: {max_response_time*1000:.2f} ms")
        
        if successful_response_times:
            print(f"\n⏱️  Response Times (Successful Requests Only):")
            print(f"   - Average: {avg_success_response_time*1000:.2f} ms")
            print(f"   - P50 (median): {p50*1000:.2f} ms")
            print(f"   - P75: {p75*1000:.2f} ms")
            print(f"   - P95: {p95*1000:.2f} ms")
            print(f"   - P99: {p99*1000:.2f} ms")
        print()
        
        print("📊 Status Codes:")
        for status_code, count in sorted(status_codes.items()):
            percentage = count / total_requests * 100
            print(f"   - {status_code}: {count} requests ({percentage:.1f}%)")
        print()
        
        print("🎯 Endpoint Statistics:")
        for endpoint, stats in endpoint_stats.items():
            success_rate = stats["success"] / stats["total"] * 100
            avg_time = sum(stats["response_times"]) / len(stats["response_times"]) * 1000 if stats["response_times"] else 0
            print(f"   - {endpoint}: {stats['success']}/{stats['total']} ({success_rate:.1f}% success, avg: {avg_time:.1f}ms)")

        self.logger.info(f"Total execution time: {total_time:.2f} seconds")
        self.logger.info(f"Total requests: {total_requests}")
        self.logger.info(f"Successful requests: {successful_requests} ({successful_requests/total_requests*100:.1f}%)")
        self.logger.info(f"Failed requests: {failed_requests} ({failed_requests/total_requests*100:.1f}%)")
        self.logger.info(f"Requests per second: {total_requests/total_time:.2f}")
        self.logger.info(f"Average response time (all): {avg_response_time*1000:.2f} ms")
        if successful_response_times:
            self.logger.info(f"Average response time (success only): {avg_success_response_time*1000:.2f} ms")
            self.logger.info(f"P95 response time: {p95*1000:.2f} ms")
        
        for status_code, count in sorted(status_codes.items()):
            self.logger.info(f"Status {status_code}: {count} requests")

        errors = [r for r in self.results if not r.success and r.error]
        if errors:
            print()
            print("❌ Error Analysis:")
            error_types = {}
            for error in errors:
                error_type = error.error.split(':')[0] if error.error else 'Unknown'
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {error_type}: {count} occurrences")
            
            print("\n❌ First 5 Error Details:")
            for error in errors[:5]:
                print(f"   - {error.endpoint} (Client {error.client_id}): {error.error}")
            
            self.logger.warning(f"Total errors: {len(errors)}")
            for error_type, count in error_types.items():
                self.logger.error(f"{error_type}: {count} occurrences")
        
        print(f"\n📝 Check {self.log_filename} for detailed logs")
        self.logger.info("Stress test completed")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="API Stress Test for Rinha de Backend")
    parser.add_argument("--url", default="http://localhost:9999", help="Base URL of the API")
    parser.add_argument("--clients", type=int, default=5, help="Number of different client IDs to test")
    parser.add_argument("--requests", type=int, default=50, help="Number of requests per client")
    parser.add_argument("--concurrent", type=int, default=5, help="Number of concurrent clients")
    
    args = parser.parse_args()
    
    tester = APIStressTester(args.url)
    await tester.run_stress_test(
        num_clients=args.clients,
        requests_per_client=args.requests,
        concurrent_clients=args.concurrent
    )


if __name__ == "__main__":
    asyncio.run(main())
