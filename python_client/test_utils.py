"""
LangChain関数呼び出し評価のための共通テストユーティリティ。
テスト実行、結果検証、レポート作成のためのヘルパー関数を提供。
"""

import time
import json
import re
import traceback
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import requests
from langchain_client import create_agent

class TestResult:
    """個別テスト結果のコンテナ"""
    def __init__(self, test_id: str, test_name: str, category: str):
        self.test_id = test_id
        self.test_name = test_name
        self.category = category
        self.success = False
        self.execution_time = 0.0
        self.prompt = ""
        self.expected_functions = []
        self.actual_functions = []
        self.expected_result = None
        self.actual_result = None
        self.error_message = ""
        self.agent_response = ""
        self.function_calls_log = []
        self.complexity = ""
        self.language = ""
        
    def to_dict(self) -> Dict[str, Any]:
        """テスト結果をJSON シリアライゼーション用の辞書に変換"""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "category": self.category,
            "success": self.success,
            "execution_time": self.execution_time,
            "prompt": self.prompt,
            "expected_functions": self.expected_functions,
            "actual_functions": self.actual_functions,
            "expected_result": self.expected_result,
            "actual_result": self.actual_result,
            "error_message": self.error_message,
            "agent_response": self.agent_response,
            "function_calls_log": self.function_calls_log,
            "complexity": self.complexity,
            "language": self.language
        }

class TestSession:
    """完全なテストセッションのコンテナ"""
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.results: List[TestResult] = []
        self.server_available = False
        self.agent_initialized = False
        
    def add_result(self, result: TestResult):
        """Add a test result to the session"""
        self.results.append(result)
        self.total_tests += 1
        if result.success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            
    def finish(self):
        """Mark session as finished"""
        self.end_time = datetime.now()
        
    def get_duration(self) -> float:
        """Get total session duration in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()
        
    def get_success_rate(self) -> float:
        """Get success rate as percentage"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for JSON serialization"""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.get_duration(),
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": self.get_success_rate(),
            "server_available": self.server_available,
            "agent_initialized": self.agent_initialized,
            "results": [result.to_dict() for result in self.results]
        }

class TestExecutor:
    """Main test execution engine"""
    
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url
        self.agent = None
        self.session = TestSession()
        
    def check_server_availability(self) -> bool:
        """Check if C# server is running and available"""
        try:
            response = requests.get(f"{self.server_url}/tools", timeout=5)
            self.session.server_available = response.status_code == 200
            return self.session.server_available
        except Exception as e:
            print(f"Server check failed: {e}")
            self.session.server_available = False
            return False
            
    def initialize_agent(self) -> bool:
        """Initialize LangChain agent"""
        try:
            self.agent = create_agent()
            self.session.agent_initialized = True
            return True
        except Exception as e:
            print(f"Agent initialization failed: {e}")
            self.session.agent_initialized = False
            return False
            
    def extract_function_calls(self, agent_response: str) -> List[str]:
        """エージェントレスポンスから呼び出された関数名を抽出"""
        import re
        called_functions = []
        
        print(f"[DEBUG] 関数抽出対象レスポンス: {agent_response[:200]}...")
        
        # 既知の関数名リスト
        known_functions = [
            'prime_factorization', 'sum', 'multiply', 'divide', 'power',
            'factorial', 'gcd', 'lcm', 'is_prime', 'square_root', 'abs',
            'modulo', 'max', 'min', 'average'
        ]
        
        # パターン1: LangChainの新形式 "Invoking: `function_name` with"
        invoke_pattern = r'Invoking:\s*`([^`]+)`'
        invoke_matches = re.findall(invoke_pattern, agent_response, re.IGNORECASE)
        print(f"[DEBUG] Invoking パターンマッチ: {invoke_matches}")
        called_functions.extend(invoke_matches)
        
        # パターン2: 内容ベースの関数推定
        response_lower = agent_response.lower()
        
        # 素因数分解の検出
        if any(word in response_lower for word in ["素因数分解", "prime", "factorization", "因数"]):
            called_functions.append("prime_factorization")
            print(f"[DEBUG] 内容推定: prime_factorization (素因数分解関連)")
        
        # 合計の検出
        if any(word in response_lower for word in ["合計", "総和", "sum", "足し", "加算"]):
            called_functions.append("sum")
            print(f"[DEBUG] 内容推定: sum (合計関連)")
        
        # 最大公約数の検出
        if any(word in response_lower for word in ["最大公約数", "gcd", "公約数"]):
            called_functions.append("gcd")
            print(f"[DEBUG] 内容推定: gcd (最大公約数関連)")
            
        # 最小公倍数の検出
        if any(word in response_lower for word in ["最小公倍数", "lcm", "公倍数"]):
            called_functions.append("lcm")
            print(f"[DEBUG] 内容推定: lcm (最小公倍数関連)")
        
        # 階乗の検出
        if any(word in response_lower for word in ["階乗", "factorial"]):
            called_functions.append("factorial")
            print(f"[DEBUG] 内容推定: factorial (階乗関連)")
        
        # 直接的な関数名検出（既存のロジック）
        for func_name in known_functions:
            if func_name.lower() in response_lower:
                called_functions.append(func_name)
                print(f"[DEBUG] 直接検出: {func_name}")
        
        # パターン3: その他の形式
        other_patterns = [
            r'calling\s+(\w+)',
            r'execute\s+(\w+)', 
            r'using\s+(\w+)',
            r'(\w+)\s*\(',
        ]
        
        for pattern in other_patterns:
            matches = re.findall(pattern, response_lower)
            for match in matches:
                if match in [f.lower() for f in known_functions]:
                    called_functions.append(match)
                    print(f"[DEBUG] パターンマッチ {pattern}: {match}")
        
        # 重複除去と正規化
        valid_functions = []
        for func in called_functions:
            func_lower = func.lower()
            if func_lower in [f.lower() for f in known_functions]:
                if func_lower not in valid_functions:
                    valid_functions.append(func_lower)
        
        print(f"[DEBUG] 最終抽出結果: {valid_functions}")
        return valid_functions
        
    def parse_numeric_result(self, response: str) -> Any:
        """エージェントレスポンスから数値結果を抽出"""
        import re
        import ast
        
        print(f"[DEBUG] 数値抽出対象レスポンス: {response[:300]}...")
        
        # パターン1: LangChainの関数実行直後の結果（最も信頼性が高い）
        # "Invoking: `function_name` with {...}\n\n[result]" 形式
        invoke_result_patterns = [
            r'Invoking:\s*`[^`]+`\s*with\s*[^\n]*\n\n([^\n]+)',
            r'`[^`]+`\s*with\s*[^\n]*\n\n([^\n]+)',
        ]
        
        for pattern in invoke_result_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            print(f"[DEBUG] 関数実行結果パターン検索: {matches}")
            
            for match in matches:
                match = match.strip()
                
                # リスト形式: [3, 3, 11] 
                if match.startswith('[') and match.endswith(']'):
                    try:
                        result = ast.literal_eval(match)
                        print(f"[DEBUG] リスト結果抽出成功: {result}")
                        return result
                    except Exception as e:
                        print(f"[DEBUG] リスト解析失敗: {e}")
                        continue
                
                # 単純な数値: 21, 15, 6
                if match.replace('.', '').replace('-', '').isdigit():
                    try:
                        if '.' in match:
                            result = float(match)
                        else:
                            result = int(match)
                        print(f"[DEBUG] 数値結果抽出成功: {result}")
                        return result
                    except ValueError as e:
                        print(f"[DEBUG] 数値変換失敗: {e}")
                        continue
        
        # パターン2: 特定用途の日本語数値抽出（配列形式を優先処理後）
        specific_japanese_patterns = [
            (r'総和は\s*([0-9]+)', "総和"),
            (r'合計は\s*([0-9]+)', "合計"), 
            (r'最大公約数は\s*([0-9]+)', "最大公約数"),
            (r'最小公倍数は\s*([0-9]+)', "最小公倍数"),
            (r'結果は\s*([0-9]+)', "結果"),
            (r'答えは\s*([0-9]+)', "答え"),
        ]
        
        # 素因数分解以外の単一数値結果をチェック
        for pattern, name in specific_japanese_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                try:
                    result = int(match.group(1))
                    print(f"[DEBUG] 特定用途日本語パターン({name})抽出成功: {result}")
                    return result
                except ValueError:
                    continue
        
        # パターン3: 数学的表現からの配列抽出（強化版）
        
        # 3 × 3 × 11 形式の抽出
        multiplication_patterns = [
            r'([0-9]+)\s*×\s*([0-9]+)\s*×\s*([0-9]+)',  # 3つの数値
            r'([0-9]+)\s*×\s*([0-9]+)',                   # 2つの数値
            r'([0-9]+)\s*\*\s*([0-9]+)\s*\*\s*([0-9]+)', # * 記号版
        ]
        
        for pattern in multiplication_patterns:
            match = re.search(pattern, response)
            if match:
                try:
                    numbers = [int(x) for x in match.groups() if x]
                    print(f"[DEBUG] 乗算形式抽出成功: {numbers}")
                    return numbers
                except Exception as e:
                    print(f"[DEBUG] 乗算形式解析失敗: {e}")
                    continue
        
        # カンマ区切り形式の抽出
        comma_patterns = [
            r'([0-9]+),\s*([0-9]+),\s*([0-9]+)',  # 3つの数値
            r'([0-9]+),\s*([0-9]+)',              # 2つの数値
            r'因数.*?([0-9,\s]+)',                # 因数という文字の後の数値列
            r'素因数.*?([0-9,\s×]+)',             # 素因数という文字の後の数値列
        ]
        
        for pattern in comma_patterns:
            match = re.search(pattern, response)
            if match:
                try:
                    if len(match.groups()) > 1:
                        # 複数グループの場合
                        numbers = [int(x) for x in match.groups() if x]
                        print(f"[DEBUG] 複数グループ抽出成功: {numbers}")
                        return numbers
                    else:
                        # 単一グループの場合（カンマ区切り文字列）
                        number_str = match.group(1).replace('×', ',')
                        numbers = [int(x.strip()) for x in number_str.split(',') if x.strip().isdigit()]
                        if len(numbers) > 1:
                            print(f"[DEBUG] カンマ区切り抽出成功: {numbers}")
                            return numbers
                except Exception as e:
                    print(f"[DEBUG] カンマ区切り解析失敗: {e}")
                    continue
        
        # ブラケット形式の検索
        bracket_patterns = [
            r'\[([0-9.,\s]+)\]',
            r'\(([0-9.,\s]+)\)',
        ]
        
        for pattern in bracket_patterns:
            match = re.search(pattern, response)
            if match:
                try:
                    if '[' in pattern or '(' in pattern:
                        # [3, 3, 11] や (3, 3, 11) 形式
                        result = ast.literal_eval(match.group(0))
                        print(f"[DEBUG] ブラケット形式抽出成功: {result}")
                        return result
                except Exception as e:
                    print(f"[DEBUG] ブラケット形式解析失敗: {e}")
                    continue
        
        # パターン4: 一般的な日本語パターン（最後の手段の前）
        general_japanese_patterns = [
            (r'([0-9]+)\s*です', "です形式"),
        ]
        
        for pattern, name in general_japanese_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                try:
                    result = int(match.group(1))
                    print(f"[DEBUG] 一般日本語パターン({name})抽出: {result}")
                    return result
                except ValueError:
                    continue
        
        # パターン5: 最後の手段 - 単純な数値検索
        simple_number = re.search(r'\b([0-9]+)\b', response)
        if simple_number:
            try:
                result = int(simple_number.group(1))
                print(f"[DEBUG] 単純数値抽出: {result}")
                return result
            except ValueError:
                pass
        
        print("[DEBUG] 数値抽出失敗: None を返す")
        return None
        
    def execute_test(self, test_data: Dict[str, Any]) -> TestResult:
        """Execute a single test case"""
        result = TestResult(
            test_id=test_data.get("id", "unknown"),
            test_name=test_data.get("prompt", "")[:50] + "...",
            category=test_data.get("category", "unknown")
        )
        
        result.prompt = test_data.get("prompt", "")
        result.expected_functions = test_data.get("expected_functions", [])
        result.expected_result = test_data.get("expected_result")
        result.complexity = test_data.get("complexity", "")
        
        # Detect language
        if any(ord(char) > 127 for char in result.prompt):
            result.language = "japanese" if any(ord(char) > 12287 for char in result.prompt) else "mixed"
        else:
            result.language = "english"
            
        start_time = time.time()
        
        try:
            if not self.agent:
                raise Exception("Agent not initialized")
                
            # Execute the test prompt
            import io
            import sys
            
            # 標準出力をキャプチャしてverboseログを取得
            captured_output = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured_output
            
            try:
                response = self.agent.invoke({"input": result.prompt})
                
                # 標準出力を復元
                sys.stdout = old_stdout
                verbose_log = captured_output.getvalue()
                
                # レスポンスと詳細ログを結合
                if isinstance(response, dict):
                    final_output = response.get("output", str(response))
                else:
                    final_output = str(response)
                
                # verbose ログと最終出力を結合
                result.agent_response = verbose_log + "\n" + final_output
                print(f"[DEBUG] 結合されたレスポンス長: {len(result.agent_response)}")
                print(f"[DEBUG] Verboseログ長: {len(verbose_log)}")
                print(f"[DEBUG] 最終出力長: {len(final_output)}")
                
            finally:
                # 必ず標準出力を復元
                sys.stdout = old_stdout
            
            # Extract function calls
            result.actual_functions = self.extract_function_calls(result.agent_response)
            
            # Extract result
            result.actual_result = self.parse_numeric_result(result.agent_response)
            
            # Evaluate success
            result.success = self.evaluate_test_success(test_data, result)
            
        except Exception as e:
            result.error_message = str(e)
            result.success = False
            
        result.execution_time = time.time() - start_time
        return result
        
    def evaluate_test_success(self, test_data: Dict[str, Any], result: TestResult) -> bool:
        """テストが成功したかどうかを評価（詳細デバッグ付き）"""
        
        print(f"\n[EVAL] テスト評価開始: {result.test_id}")
        print(f"[EVAL] プロンプト: {result.prompt}")
        
        # エラーハンドリングテストの場合
        if "expected_error" in test_data:
            expected_error = test_data["expected_error"]
            print(f"[EVAL] エラーテスト - 期待エラー: {expected_error}")
            print(f"[EVAL] 実際のエラー: {result.error_message}")
            success = expected_error.lower() in result.error_message.lower()
            print(f"[EVAL] エラーテスト結果: {success}")
            return success
            
        # 関数呼び出しチェック
        expected_functions = test_data.get("expected_functions", [])
        print(f"[EVAL] 期待関数: {expected_functions}")
        print(f"[EVAL] 実際の関数: {result.actual_functions}")
        
        function_check_passed = True
        if expected_functions:
            for expected_func in expected_functions:
                if expected_func.lower() not in [f.lower() for f in result.actual_functions]:
                    print(f"[EVAL] ❌ 関数 '{expected_func}' が見つかりません")
                    function_check_passed = False
                else:
                    print(f"[EVAL] ✅ 関数 '{expected_func}' が見つかりました")
        else:
            print("[EVAL] 関数チェックをスキップ（期待関数なし）")
            
        # 結果値チェック
        expected_result = test_data.get("expected_result")
        print(f"[EVAL] 期待結果: {expected_result} (型: {type(expected_result)})")
        print(f"[EVAL] 実際の結果: {result.actual_result} (型: {type(result.actual_result)})")
        
        result_check_passed = True
        if expected_result is not None:
            if result.actual_result is None:
                print("[EVAL] ❌ 実際の結果がNone")
                result_check_passed = False
            elif isinstance(expected_result, (int, float)) and isinstance(result.actual_result, (int, float)):
                # 数値比較（許容誤差あり）
                tolerance = 1e-6
                diff = abs(expected_result - result.actual_result)
                if diff > tolerance:
                    print(f"[EVAL] ❌ 数値不一致: 差分 {diff} > 許容誤差 {tolerance}")
                    result_check_passed = False
                else:
                    print(f"[EVAL] ✅ 数値一致: 差分 {diff} <= 許容誤差 {tolerance}")
            elif isinstance(expected_result, list) and isinstance(result.actual_result, list):
                # リスト比較
                if result.actual_result != expected_result:
                    print(f"[EVAL] ❌ リスト不一致")
                    print(f"[EVAL]   期待: {expected_result}")
                    print(f"[EVAL]   実際: {result.actual_result}")
                    result_check_passed = False
                else:
                    print("[EVAL] ✅ リスト一致")
            else:
                # 直接比較
                if result.actual_result != expected_result:
                    print(f"[EVAL] ❌ 直接比較不一致")
                    print(f"[EVAL]   期待: {expected_result}")
                    print(f"[EVAL]   実際: {result.actual_result}")
                    result_check_passed = False
                else:
                    print("[EVAL] ✅ 直接比較一致")
        else:
            print("[EVAL] 結果値チェックをスキップ（期待結果なし）")
            
        final_success = function_check_passed and result_check_passed
        print(f"[EVAL] 最終判定: 関数チェック={function_check_passed}, 結果チェック={result_check_passed}")
        print(f"[EVAL] 総合結果: {'✅ SUCCESS' if final_success else '❌ FAILED'}")
        
        return final_success
        
    def run_test_suite(self, test_suite: List[Dict[str, Any]], 
                      max_tests: Optional[int] = None) -> TestSession:
        """Run a complete test suite"""
        
        print("Starting test suite execution...")
        print(f"Total tests to run: {len(test_suite) if not max_tests else min(max_tests, len(test_suite))}")
        
        # Pre-flight checks
        if not self.check_server_availability():
            print("❌ C# server is not available")
            return self.session
            
        if not self.initialize_agent():
            print("❌ Failed to initialize LangChain agent")
            return self.session
            
        print("✅ Server and agent are ready")
        
        # Execute tests
        test_count = 0
        for test_data in test_suite:
            if max_tests and test_count >= max_tests:
                break
                
            print(f"\nRunning test {test_count + 1}: {test_data.get('id', 'unknown')}")
            print(f"Prompt: {test_data.get('prompt', '')[:100]}...")
            
            try:
                result = self.execute_test(test_data)
                self.session.add_result(result)
                
                if result.success:
                    print(f"✅ PASSED ({result.execution_time:.2f}s)")
                else:
                    print(f"❌ FAILED ({result.execution_time:.2f}s)")
                    if result.error_message:
                        print(f"   Error: {result.error_message}")
                        
            except Exception as e:
                print(f"❌ CRASHED: {e}")
                # Create a failure result
                crash_result = TestResult(
                    test_id=test_data.get("id", "unknown"),
                    test_name=test_data.get("prompt", "")[:50] + "...",
                    category=test_data.get("category", "unknown")
                )
                crash_result.error_message = f"Test crashed: {e}"
                crash_result.success = False
                self.session.add_result(crash_result)
                
            test_count += 1
            
            # Brief pause between tests
            time.sleep(0.5)
            
        self.session.finish()
        
        print(f"\n📊 Test Suite Complete!")
        print(f"Total: {self.session.total_tests}")
        print(f"Passed: {self.session.passed_tests}")
        print(f"Failed: {self.session.failed_tests}")
        print(f"Success Rate: {self.session.get_success_rate():.1f}%")
        print(f"Duration: {self.session.get_duration():.2f}s")
        
        return self.session

def save_test_results(session: TestSession, filename: str):
    """Save test results to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"Results saved to {filename}")

def load_test_results(filename: str) -> Dict[str, Any]:
    """Load test results from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def print_test_summary(session: TestSession):
    """Print a detailed test summary"""
    print("\n" + "="*60)
    print("TEST EXECUTION SUMMARY")
    print("="*60)
    
    print(f"📅 Start Time: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if session.end_time:
        print(f"⏰ End Time: {session.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Duration: {session.get_duration():.2f} seconds")
    print(f"🏃 Total Tests: {session.total_tests}")
    print(f"✅ Passed: {session.passed_tests}")
    print(f"❌ Failed: {session.failed_tests}")
    print(f"📈 Success Rate: {session.get_success_rate():.1f}%")
    
    # Breakdown by category
    categories = {}
    for result in session.results:
        cat = result.category
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0}
        categories[cat]["total"] += 1
        if result.success:
            categories[cat]["passed"] += 1
            
    print("\n📊 Results by Category:")
    for category, stats in categories.items():
        success_rate = (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f"  {category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
    # Show failed tests
    failed_tests = [r for r in session.results if not r.success]
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for result in failed_tests[:10]:  # Show first 10 failures
            print(f"  - {result.test_id}: {result.error_message or 'Assertion failed'}")
        if len(failed_tests) > 10:
            print(f"  ... and {len(failed_tests) - 10} more")

if __name__ == "__main__":
    # Example usage
    executor = TestExecutor()
    
    # Simple test case for demonstration
    sample_test = {
        "id": "sample_001",
        "prompt": "234を素因数分解してください",
        "expected_functions": ["prime_factorization"],
        "expected_result": [2, 3, 3, 13],
        "category": "basic"
    }
    
    session = executor.run_test_suite([sample_test])
    print_test_summary(session)