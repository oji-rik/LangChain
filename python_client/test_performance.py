"""
LangChain関数呼び出しシステムのためのパフォーマンスベンチマークモジュール

包括的なパフォーマンステストとベンチマーク機能を提供:
- レスポンス時間分析
- スループットテスト
- メモリ使用量監視
- スケーラビリティテスト
- 遅延分布分析
- パフォーマンス回帰検出

使用方法:
    python test_performance.py --benchmark-basic        # 基本パフォーマンステスト
    python test_performance.py --benchmark-stress       # ストレステスト
    python test_performance.py --benchmark-memory       # メモリ使用量分析
    python test_performance.py --benchmark-all          # 全パフォーマンステスト
    python test_performance.py --load-test 100          # N回リクエストの負荷テスト
"""

import time
import psutil
import statistics
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime
import argparse
import sys

from test_utils import TestExecutor, TestResult
from test_data import BASIC_TESTS, INTERMEDIATE_TESTS

class PerformanceMetrics:
    """パフォーマンス測定データのコンテナ"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.success_count: int = 0
        self.failure_count: int = 0
        self.start_time: float = 0
        self.end_time: float = 0
        self.peak_memory: float = 0
        self.avg_cpu: float = 0
        
    def add_response_time(self, response_time: float):
        """Add a response time measurement"""
        self.response_times.append(response_time)
        
    def add_system_metrics(self, memory_mb: float, cpu_percent: float):
        """Add system resource usage metrics"""
        self.memory_usage.append(memory_mb)
        self.cpu_usage.append(cpu_percent)
        self.peak_memory = max(self.peak_memory, memory_mb)
        
    def record_result(self, success: bool):
        """Record test result"""
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
            
    def get_statistics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance statistics"""
        if not self.response_times:
            return {"error": "No data recorded"}
            
        duration = self.end_time - self.start_time if self.end_time > 0 else 0
        total_requests = len(self.response_times)
        
        stats = {
            "duration_seconds": duration,
            "total_requests": total_requests,
            "successful_requests": self.success_count,
            "failed_requests": self.failure_count,
            "success_rate": (self.success_count / total_requests * 100) if total_requests > 0 else 0,
            "throughput_rps": total_requests / duration if duration > 0 else 0,
            
            # Response time statistics
            "response_time": {
                "min": min(self.response_times),
                "max": max(self.response_times),
                "mean": statistics.mean(self.response_times),
                "median": statistics.median(self.response_times),
                "std_dev": statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0,
                "p95": self._percentile(self.response_times, 95),
                "p99": self._percentile(self.response_times, 99)
            },
            
            # Memory statistics
            "memory": {
                "peak_mb": self.peak_memory,
                "avg_mb": statistics.mean(self.memory_usage) if self.memory_usage else 0,
                "max_mb": max(self.memory_usage) if self.memory_usage else 0
            },
            
            # CPU statistics
            "cpu": {
                "avg_percent": statistics.mean(self.cpu_usage) if self.cpu_usage else 0,
                "max_percent": max(self.cpu_usage) if self.cpu_usage else 0
            }
        }
        
        return stats
        
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

class SystemMonitor:
    """Monitor system resources during test execution"""
    
    def __init__(self, metrics: PerformanceMetrics):
        self.metrics = metrics
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start system resource monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop system resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
            
    def _monitor_loop(self):
        """Monitor system resources in a loop"""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                # Memory usage in MB
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                # CPU usage percentage
                cpu_percent = process.cpu_percent()
                
                self.metrics.add_system_metrics(memory_mb, cpu_percent)
                
                time.sleep(0.1)  # Monitor every 100ms
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                break

class PerformanceBenchmark:
    """Main performance benchmarking class"""
    
    def __init__(self):
        self.executor = TestExecutor()
        
    def single_request_benchmark(self, test_cases: List[Dict[str, Any]], 
                                iterations: int = 100) -> PerformanceMetrics:
        """Benchmark single request performance"""
        print(f"🔬 Single Request Benchmark - {iterations} iterations")
        
        metrics = PerformanceMetrics()
        monitor = SystemMonitor(metrics)
        
        # Initialize system
        if not self.executor.check_server_availability():
            raise Exception("Server not available")
        if not self.executor.initialize_agent():
            raise Exception("Agent initialization failed")
            
        # Start monitoring
        monitor.start_monitoring()
        metrics.start_time = time.time()
        
        try:
            for i in range(iterations):
                if i % 10 == 0:
                    print(f"  Progress: {i}/{iterations}")
                    
                # Select random test case
                test_case = test_cases[i % len(test_cases)]
                
                start_time = time.time()
                try:
                    result = self.executor.execute_test(test_case)
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    metrics.add_response_time(response_time)
                    metrics.record_result(result.success)
                    
                except Exception as e:
                    end_time = time.time()
                    response_time = end_time - start_time
                    metrics.add_response_time(response_time)
                    metrics.record_result(False)
                    
                # Brief pause between requests
                time.sleep(0.01)
                
        finally:
            metrics.end_time = time.time()
            monitor.stop_monitoring()
            
        return metrics
        
    def concurrent_request_benchmark(self, test_cases: List[Dict[str, Any]],
                                   concurrent_users: int = 10,
                                   requests_per_user: int = 10) -> PerformanceMetrics:
        """Benchmark concurrent request performance"""
        print(f"🚀 Concurrent Request Benchmark - {concurrent_users} users, {requests_per_user} requests each")
        
        metrics = PerformanceMetrics()
        monitor = SystemMonitor(metrics)
        
        # Initialize system
        if not self.executor.check_server_availability():
            raise Exception("Server not available")
        if not self.executor.initialize_agent():
            raise Exception("Agent initialization failed")
            
        def worker_function(user_id: int, result_queue: queue.Queue):
            """Worker function for concurrent testing"""
            executor = TestExecutor()  # Each worker gets its own executor
            executor.initialize_agent()
            
            for request_id in range(requests_per_user):
                test_case = test_cases[(user_id * requests_per_user + request_id) % len(test_cases)]
                
                start_time = time.time()
                try:
                    result = executor.execute_test(test_case)
                    end_time = time.time()
                    
                    result_queue.put({
                        "response_time": end_time - start_time,
                        "success": result.success,
                        "user_id": user_id,
                        "request_id": request_id
                    })
                    
                except Exception as e:
                    end_time = time.time()
                    result_queue.put({
                        "response_time": end_time - start_time,
                        "success": False,
                        "user_id": user_id,
                        "request_id": request_id,
                        "error": str(e)
                    })
                    
        # Start monitoring
        monitor.start_monitoring()
        metrics.start_time = time.time()
        
        try:
            result_queue = queue.Queue()
            threads = []
            
            # Start worker threads
            for user_id in range(concurrent_users):
                thread = threading.Thread(target=worker_function, args=(user_id, result_queue))
                thread.start()
                threads.append(thread)
                
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
                
            # Collect results
            while not result_queue.empty():
                result = result_queue.get()
                metrics.add_response_time(result["response_time"])
                metrics.record_result(result["success"])
                
        finally:
            metrics.end_time = time.time()
            monitor.stop_monitoring()
            
        return metrics
        
    def load_test(self, test_cases: List[Dict[str, Any]], 
                 target_rps: float = 10, duration_seconds: int = 60) -> PerformanceMetrics:
        """Run a sustained load test"""
        print(f"📈 Load Test - {target_rps} RPS for {duration_seconds} seconds")
        
        metrics = PerformanceMetrics()
        monitor = SystemMonitor(metrics)
        
        # Initialize system
        if not self.executor.check_server_availability():
            raise Exception("Server not available")
        if not self.executor.initialize_agent():
            raise Exception("Agent initialization failed")
            
        interval = 1.0 / target_rps
        request_count = 0
        
        # Start monitoring
        monitor.start_monitoring()
        metrics.start_time = time.time()
        
        try:
            end_time = time.time() + duration_seconds
            
            while time.time() < end_time:
                test_case = test_cases[request_count % len(test_cases)]
                
                start_time = time.time()
                try:
                    result = self.executor.execute_test(test_case)
                    response_time = time.time() - start_time
                    metrics.add_response_time(response_time)
                    metrics.record_result(result.success)
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    metrics.add_response_time(response_time)
                    metrics.record_result(False)
                    
                request_count += 1
                
                # Rate limiting
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
                if request_count % 50 == 0:
                    elapsed_total = time.time() - metrics.start_time
                    current_rps = request_count / elapsed_total
                    print(f"  Progress: {request_count} requests, {current_rps:.1f} RPS")
                    
        finally:
            metrics.end_time = time.time()
            monitor.stop_monitoring()
            
        return metrics
        
    def memory_stress_test(self, test_cases: List[Dict[str, Any]], 
                          max_requests: int = 1000) -> PerformanceMetrics:
        """Test memory usage under stress"""
        print(f"🧠 Memory Stress Test - {max_requests} requests")
        
        metrics = PerformanceMetrics()
        monitor = SystemMonitor(metrics)
        
        # Initialize system
        if not self.executor.check_server_availability():
            raise Exception("Server not available")
        if not self.executor.initialize_agent():
            raise Exception("Agent initialization failed")
            
        # Start monitoring
        monitor.start_monitoring()
        metrics.start_time = time.time()
        
        try:
            for i in range(max_requests):
                if i % 100 == 0:
                    print(f"  Progress: {i}/{max_requests}")
                    
                test_case = test_cases[i % len(test_cases)]
                
                start_time = time.time()
                try:
                    result = self.executor.execute_test(test_case)
                    response_time = time.time() - start_time
                    metrics.add_response_time(response_time)
                    metrics.record_result(result.success)
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    metrics.add_response_time(response_time)
                    metrics.record_result(False)
                    
                # No delay - stress test
                
        finally:
            metrics.end_time = time.time()
            monitor.stop_monitoring()
            
        return metrics

def run_basic_benchmark():
    """Run basic performance benchmarks"""
    benchmark = PerformanceBenchmark()
    test_cases = BASIC_TESTS[:5]  # Use first 5 basic tests
    
    results = {}
    
    print("🏃 Starting Basic Performance Benchmarks")
    print("="*50)
    
    # Single request benchmark
    try:
        metrics = benchmark.single_request_benchmark(test_cases, iterations=50)
        results["single_request"] = metrics.get_statistics()
        print("✅ Single request benchmark completed")
    except Exception as e:
        print(f"❌ Single request benchmark failed: {e}")
        
    # Concurrent request benchmark
    try:
        metrics = benchmark.concurrent_request_benchmark(test_cases, concurrent_users=5, requests_per_user=5)
        results["concurrent_request"] = metrics.get_statistics()
        print("✅ Concurrent request benchmark completed")
    except Exception as e:
        print(f"❌ Concurrent request benchmark failed: {e}")
        
    return results

def run_stress_benchmark():
    """Run stress performance benchmarks"""
    benchmark = PerformanceBenchmark()
    test_cases = BASIC_TESTS + INTERMEDIATE_TESTS[:3]
    
    results = {}
    
    print("💪 Starting Stress Performance Benchmarks")
    print("="*50)
    
    # Load test
    try:
        metrics = benchmark.load_test(test_cases, target_rps=5, duration_seconds=30)
        results["load_test"] = metrics.get_statistics()
        print("✅ Load test completed")
    except Exception as e:
        print(f"❌ Load test failed: {e}")
        
    # Memory stress test
    try:
        metrics = benchmark.memory_stress_test(test_cases, max_requests=200)
        results["memory_stress"] = metrics.get_statistics()
        print("✅ Memory stress test completed")
    except Exception as e:
        print(f"❌ Memory stress test failed: {e}")
        
    return results

def print_performance_report(results: Dict[str, Any]):
    """Print a formatted performance report"""
    print("\n" + "="*80)
    print("PERFORMANCE BENCHMARK REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    for test_name, stats in results.items():
        if "error" in stats:
            print(f"\n❌ {test_name.upper()}: {stats['error']}")
            continue
            
        print(f"\n📊 {test_name.upper()}")
        print("-" * 40)
        print(f"Duration: {stats['duration_seconds']:.2f}s")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print(f"Throughput: {stats['throughput_rps']:.1f} RPS")
        
        rt = stats['response_time']
        print(f"Response Time - Min: {rt['min']:.3f}s, Max: {rt['max']:.3f}s, Mean: {rt['mean']:.3f}s")
        print(f"Response Time - P95: {rt['p95']:.3f}s, P99: {rt['p99']:.3f}s")
        
        mem = stats['memory']
        print(f"Memory - Peak: {mem['peak_mb']:.1f}MB, Average: {mem['avg_mb']:.1f}MB")
        
        cpu = stats['cpu']
        print(f"CPU - Average: {cpu['avg_percent']:.1f}%, Peak: {cpu['max_percent']:.1f}%")

def save_performance_results(results: Dict[str, Any], filename: str):
    """Save performance results to JSON file"""
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "system_info": {
            "cpu_count": psutil.cpu_count(),
            "memory_total_mb": psutil.virtual_memory().total / 1024 / 1024,
            "python_version": sys.version
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(report_data, f, indent=2)
    print(f"📁 Performance results saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Performance Benchmark Suite")
    
    parser.add_argument("--benchmark-basic", action="store_true", help="Run basic benchmarks")
    parser.add_argument("--benchmark-stress", action="store_true", help="Run stress benchmarks")
    parser.add_argument("--benchmark-memory", action="store_true", help="Run memory benchmarks")
    parser.add_argument("--benchmark-all", action="store_true", help="Run all benchmarks")
    parser.add_argument("--load-test", type=int, metavar="REQUESTS", help="Run load test with N requests")
    parser.add_argument("--output", type=str, default="performance_results.json", help="Output file")
    
    args = parser.parse_args()
    
    results = {}
    
    try:
        if args.benchmark_all or args.benchmark_basic:
            basic_results = run_basic_benchmark()
            results.update(basic_results)
            
        if args.benchmark_all or args.benchmark_stress:
            stress_results = run_stress_benchmark()
            results.update(stress_results)
            
        if args.load_test:
            benchmark = PerformanceBenchmark()
            test_cases = BASIC_TESTS[:3]
            metrics = benchmark.load_test(test_cases, target_rps=10, duration_seconds=args.load_test)
            results["custom_load_test"] = metrics.get_statistics()
            
        if not results:
            # Default to basic benchmark
            results = run_basic_benchmark()
            
        print_performance_report(results)
        save_performance_results(results, args.output)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Performance testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Performance testing failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())