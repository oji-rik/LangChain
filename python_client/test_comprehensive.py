"""
LangChain関数呼び出し評価のための包括的テストスイート

7つのテスト観点すべてを実行するメインテストランナー:
1. 複雑度レベル (基本、中級、上級、専門家)
2. 曖昧性解決 (明確 vs 曖昧なプロンプト)
3. 文脈理解 (逐次、条件付き、依存操作)
4. エラーハンドリング (無効な入力、エッジケース)
5. スケーラビリティ (大きな数値、複数操作)
6. 多言語サポート (日本語、英語、混合)
7. 数学的精度 (複雑な計算の検証)

使用方法:
    python test_comprehensive.py --all                    # 全テスト実行
    python test_comprehensive.py --basic                  # 基本テストのみ
    python test_comprehensive.py --complexity             # 複雑度テスト
    python test_comprehensive.py --quick                  # 簡易テスト
    python test_comprehensive.py --category basic         # 特定カテゴリ
    python test_comprehensive.py --max-tests 20          # テスト数制限
    python test_comprehensive.py --report-html           # HTMLレポート生成
"""

import argparse
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from test_data import ALL_TESTS, get_test_statistics
from test_utils import TestExecutor, TestSession, save_test_results, print_test_summary

class ComprehensiveTestRunner:
    """包括的評価のためのメインテストランナー"""
    
    def __init__(self):
        self.executor = TestExecutor()
        self.results: Dict[str, TestSession] = {}
        
    def run_perspective_tests(self, perspective_name: str, tests: List[Dict[str, Any]], 
                             max_tests: Optional[int] = None) -> TestSession:
        """Run tests for a specific perspective"""
        print(f"\n{'='*60}")
        print(f"🔍 TESTING PERSPECTIVE: {perspective_name.upper()}")
        print(f"{'='*60}")
        print(f"Number of tests: {len(tests)}")
        
        if max_tests:
            tests = tests[:max_tests]
            print(f"Limited to: {len(tests)} tests")
            
        session = self.executor.run_test_suite(tests, max_tests)
        self.results[perspective_name] = session
        
        print(f"\n📊 {perspective_name} Results:")
        print(f"   Success Rate: {session.get_success_rate():.1f}%")
        print(f"   Duration: {session.get_duration():.2f}s")
        
        return session
        
    def run_complexity_tests(self, max_tests_per_level: Optional[int] = None) -> Dict[str, TestSession]:
        """Run all complexity level tests"""
        complexity_results = {}
        
        complexity_levels = {
            "basic": ALL_TESTS["basic"],
            "intermediate": ALL_TESTS["intermediate"],
            "advanced": ALL_TESTS["advanced"],
            "expert": ALL_TESTS["expert"]
        }
        
        for level, tests in complexity_levels.items():
            session = self.run_perspective_tests(f"complexity_{level}", tests, max_tests_per_level)
            complexity_results[level] = session
            
        return complexity_results
        
    def run_ambiguity_tests(self, max_tests: Optional[int] = None) -> Dict[str, TestSession]:
        """Run ambiguity resolution tests"""
        ambiguity_results = {}
        
        # Clear prompts
        clear_session = self.run_perspective_tests("clear_prompts", ALL_TESTS["clear_prompts"], max_tests)
        ambiguity_results["clear"] = clear_session
        
        # Ambiguous prompts  
        ambiguous_session = self.run_perspective_tests("ambiguous_prompts", ALL_TESTS["ambiguous_prompts"], max_tests)
        ambiguity_results["ambiguous"] = ambiguous_session
        
        return ambiguity_results
        
    def run_context_tests(self, max_tests: Optional[int] = None) -> Dict[str, TestSession]:
        """Run context understanding tests"""
        context_results = {}
        
        # Sequential operations
        sequential_session = self.run_perspective_tests("sequential_operations", ALL_TESTS["sequential_operations"], max_tests)
        context_results["sequential"] = sequential_session
        
        # Conditional operations
        conditional_session = self.run_perspective_tests("conditional_operations", ALL_TESTS["conditional_operations"], max_tests)
        context_results["conditional"] = conditional_session
        
        return context_results
        
    def run_error_handling_tests(self, max_tests: Optional[int] = None) -> Dict[str, TestSession]:
        """Run error handling tests"""
        error_results = {}
        
        # Invalid input tests
        invalid_session = self.run_perspective_tests("invalid_input_tests", ALL_TESTS["invalid_input_tests"], max_tests)
        error_results["invalid_input"] = invalid_session
        
        # Edge case tests
        edge_session = self.run_perspective_tests("edge_case_tests", ALL_TESTS["edge_case_tests"], max_tests)
        error_results["edge_cases"] = edge_session
        
        return error_results
        
    def run_scalability_tests(self, max_tests: Optional[int] = None) -> Dict[str, TestSession]:
        """Run scalability tests"""
        scalability_results = {}
        
        # Large number tests
        large_session = self.run_perspective_tests("large_number_tests", ALL_TESTS["large_number_tests"], max_tests)
        scalability_results["large_numbers"] = large_session
        
        # Multiple operations tests
        multi_session = self.run_perspective_tests("multiple_operations_tests", ALL_TESTS["multiple_operations_tests"], max_tests)
        scalability_results["multiple_operations"] = multi_session
        
        return scalability_results
        
    def run_multilingual_tests(self, max_tests: Optional[int] = None) -> Dict[str, TestSession]:
        """Run multilingual support tests"""
        multilingual_results = {}
        
        # Japanese tests
        japanese_session = self.run_perspective_tests("japanese_tests", ALL_TESTS["japanese_tests"], max_tests)
        multilingual_results["japanese"] = japanese_session
        
        # English tests
        english_session = self.run_perspective_tests("english_tests", ALL_TESTS["english_tests"], max_tests)
        multilingual_results["english"] = english_session
        
        # Mixed language tests
        mixed_session = self.run_perspective_tests("mixed_language_tests", ALL_TESTS["mixed_language_tests"], max_tests)
        multilingual_results["mixed"] = mixed_session
        
        return multilingual_results
        
    def run_accuracy_tests(self, max_tests: Optional[int] = None) -> Dict[str, TestSession]:
        """Run mathematical accuracy tests"""
        accuracy_results = {}
        
        # Precision tests
        precision_session = self.run_perspective_tests("precision_tests", ALL_TESTS["precision_tests"], max_tests)
        accuracy_results["precision"] = precision_session
        
        # Verification tests
        verification_session = self.run_perspective_tests("verification_tests", ALL_TESTS["verification_tests"], max_tests)
        accuracy_results["verification"] = verification_session
        
        return accuracy_results
        
    def run_all_tests(self, max_tests_per_perspective: Optional[int] = None) -> Dict[str, Any]:
        """Run all test perspectives"""
        print("\n🚀 STARTING COMPREHENSIVE TEST SUITE")
        print("="*80)
        
        stats = get_test_statistics()
        print(f"📊 Test Suite Statistics:")
        print(f"   Total Tests: {stats['total_tests']}")
        print(f"   Test Perspectives: {len(stats['test_perspectives'])}")
        for perspective in stats['test_perspectives']:
            print(f"     - {perspective}")
            
        all_results = {}
        
        # 1. Complexity Levels
        print(f"\n🎯 PERSPECTIVE 1/7: COMPLEXITY LEVELS")
        all_results["complexity"] = self.run_complexity_tests(max_tests_per_perspective)
        
        # 2. Ambiguity Resolution
        print(f"\n🤔 PERSPECTIVE 2/7: AMBIGUITY RESOLUTION")
        all_results["ambiguity"] = self.run_ambiguity_tests(max_tests_per_perspective)
        
        # 3. Context Understanding
        print(f"\n🧠 PERSPECTIVE 3/7: CONTEXT UNDERSTANDING")
        all_results["context"] = self.run_context_tests(max_tests_per_perspective)
        
        # 4. Error Handling
        print(f"\n⚠️  PERSPECTIVE 4/7: ERROR HANDLING")
        all_results["error_handling"] = self.run_error_handling_tests(max_tests_per_perspective)
        
        # 5. Scalability
        print(f"\n📈 PERSPECTIVE 5/7: SCALABILITY")
        all_results["scalability"] = self.run_scalability_tests(max_tests_per_perspective)
        
        # 6. Multilingual Support
        print(f"\n🌍 PERSPECTIVE 6/7: MULTILINGUAL SUPPORT")
        all_results["multilingual"] = self.run_multilingual_tests(max_tests_per_perspective)
        
        # 7. Mathematical Accuracy
        print(f"\n🔢 PERSPECTIVE 7/7: MATHEMATICAL ACCURACY")
        all_results["accuracy"] = self.run_accuracy_tests(max_tests_per_perspective)
        
        return all_results
        
    def run_quick_test(self) -> Dict[str, TestSession]:
        """Run a quick subset of tests for fast feedback"""
        print("\n⚡ RUNNING QUICK TEST SUITE")
        print("="*50)
        
        quick_results = {}
        
        # Select a few tests from each category
        quick_tests = {
            "basic_sample": ALL_TESTS["basic"][:2],
            "intermediate_sample": ALL_TESTS["intermediate"][:2],
            "error_sample": ALL_TESTS["invalid_input_tests"][:1],
            "multilingual_sample": ALL_TESTS["japanese_tests"][:1]
        }
        
        for category, tests in quick_tests.items():
            session = self.run_perspective_tests(category, tests)
            quick_results[category] = session
            
        return quick_results
        
    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive summary report"""
        report_lines = []
        report_lines.append("COMPREHENSIVE TEST SUITE SUMMARY REPORT")
        report_lines.append("="*80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        total_tests = 0
        total_passed = 0
        total_duration = 0.0
        
        # Collect overall statistics
        for perspective_name, perspective_results in results.items():
            if isinstance(perspective_results, dict):
                for sub_name, session in perspective_results.items():
                    total_tests += session.total_tests
                    total_passed += session.passed_tests
                    total_duration += session.get_duration()
            else:
                session = perspective_results
                total_tests += session.total_tests
                total_passed += session.passed_tests
                total_duration += session.get_duration()
                
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report_lines.append("📊 OVERALL RESULTS")
        report_lines.append("-" * 30)
        report_lines.append(f"Total Tests: {total_tests}")
        report_lines.append(f"Total Passed: {total_passed}")
        report_lines.append(f"Total Failed: {total_tests - total_passed}")
        report_lines.append(f"Success Rate: {overall_success_rate:.1f}%")
        report_lines.append(f"Total Duration: {total_duration:.2f}s")
        report_lines.append("")
        
        # Detailed breakdown by perspective
        report_lines.append("🔍 RESULTS BY PERSPECTIVE")
        report_lines.append("-" * 40)
        
        for perspective_name, perspective_results in results.items():
            report_lines.append(f"\n{perspective_name.upper()}:")
            
            if isinstance(perspective_results, dict):
                for sub_name, session in perspective_results.items():
                    success_rate = session.get_success_rate()
                    status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
                    report_lines.append(f"  {status} {sub_name}: {session.passed_tests}/{session.total_tests} ({success_rate:.1f}%)")
            else:
                session = perspective_results
                success_rate = session.get_success_rate()
                status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
                report_lines.append(f"  {status} {perspective_name}: {session.passed_tests}/{session.total_tests} ({success_rate:.1f}%)")
                
        report_lines.append("")
        
        # Recommendations
        report_lines.append("💡 RECOMMENDATIONS")
        report_lines.append("-" * 30)
        if overall_success_rate >= 90:
            report_lines.append("🎉 Excellent performance! The LangChain integration is working very well.")
        elif overall_success_rate >= 80:
            report_lines.append("👍 Good performance with some areas for improvement.")
        elif overall_success_rate >= 60:
            report_lines.append("⚠️  Moderate performance. Consider investigating failed test patterns.")
        else:
            report_lines.append("🚨 Poor performance. Significant issues need to be addressed.")
            
        return "\n".join(report_lines)

def main():
    parser = argparse.ArgumentParser(description="Comprehensive LangChain Function Calling Test Suite")
    
    # Test selection arguments
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--quick", action="store_true", help="Run quick test subset")
    parser.add_argument("--complexity", action="store_true", help="Run complexity tests only")
    parser.add_argument("--ambiguity", action="store_true", help="Run ambiguity tests only")
    parser.add_argument("--context", action="store_true", help="Run context tests only")
    parser.add_argument("--error", action="store_true", help="Run error handling tests only")
    parser.add_argument("--scalability", action="store_true", help="Run scalability tests only")
    parser.add_argument("--multilingual", action="store_true", help="Run multilingual tests only")
    parser.add_argument("--accuracy", action="store_true", help="Run accuracy tests only")
    
    parser.add_argument("--category", type=str, help="Run specific test category")
    parser.add_argument("--max-tests", type=int, help="Maximum number of tests per perspective")
    
    # Output arguments
    parser.add_argument("--output", type=str, default="test_results.json", help="Output file for results")
    parser.add_argument("--report", type=str, help="Generate text report file")
    parser.add_argument("--report-html", action="store_true", help="Generate HTML report")
    
    # Debugging arguments
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--stats", action="store_true", help="Show test statistics and exit")
    
    args = parser.parse_args()
    
    if args.stats:
        stats = get_test_statistics()
        print("Test Suite Statistics:")
        print(f"Total Tests: {stats['total_tests']}")
        print(f"Complexity Distribution: {stats['complexity_distribution']}")
        print(f"Language Distribution: {stats['language_distribution']}")
        print(f"Categories: {list(stats['by_category'].keys())}")
        return
        
    runner = ComprehensiveTestRunner()
    results = {}
    
    try:
        if args.all:
            results = runner.run_all_tests(args.max_tests)
        elif args.quick:
            results = runner.run_quick_test()
        elif args.complexity:
            results["complexity"] = runner.run_complexity_tests(args.max_tests)
        elif args.ambiguity:
            results["ambiguity"] = runner.run_ambiguity_tests(args.max_tests)
        elif args.context:
            results["context"] = runner.run_context_tests(args.max_tests)
        elif args.error:
            results["error"] = runner.run_error_handling_tests(args.max_tests)
        elif args.scalability:
            results["scalability"] = runner.run_scalability_tests(args.max_tests)
        elif args.multilingual:
            results["multilingual"] = runner.run_multilingual_tests(args.max_tests)
        elif args.accuracy:
            results["accuracy"] = runner.run_accuracy_tests(args.max_tests)
        elif args.category:
            if args.category in ALL_TESTS:
                session = runner.run_perspective_tests(args.category, ALL_TESTS[args.category], args.max_tests)
                results[args.category] = session
            else:
                print(f"Error: Unknown category '{args.category}'")
                print(f"Available categories: {list(ALL_TESTS.keys())}")
                return 1
        else:
            # Default to quick test
            results = runner.run_quick_test()
            
        # Generate summary report
        summary = runner.generate_summary_report(results)
        print(f"\n{summary}")
        
        # Save results
        if args.output:
            # Convert results to serializable format
            serializable_results = {}
            for key, value in results.items():
                if isinstance(value, dict):
                    serializable_results[key] = {k: v.to_dict() for k, v in value.items()}
                else:
                    serializable_results[key] = value.to_dict()
                    
            import json
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump({
                    "summary": summary,
                    "results": serializable_results,
                    "timestamp": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            print(f"📁 Results saved to {args.output}")
            
        # Generate text report
        if args.report:
            with open(args.report, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"📄 Report saved to {args.report}")
            
        # Generate HTML report
        if args.report_html:
            try:
                from test_reporter import generate_html_report
                html_file = "test_report.html"
                generate_html_report(results, html_file)
                print(f"🌐 HTML report saved to {html_file}")
            except ImportError:
                print("⚠️  HTML report generation requires test_reporter.py")
                
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())