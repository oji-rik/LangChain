#!/usr/bin/env python3
"""
シンプルテスト実行ツール
自動評価なしで、人間による目視確認のためのLangChainテスト実行

使用例:
  python simple_test_runner.py --test basic_001
  python simple_test_runner.py --category basic
  python simple_test_runner.py --all
  python simple_test_runner.py --interactive
"""

import os
import sys
import argparse
import time
from typing import List, Dict, Any, Optional
from langchain_client import create_agent
from test_data import (
    BASIC_TESTS, INTERMEDIATE_TESTS, ADVANCED_TESTS, EXPERT_TESTS,
    EDGE_CASE_TESTS, JAPANESE_TESTS, ENGLISH_TESTS, MIXED_LANGUAGE_TESTS,
    LARGE_NUMBER_TESTS, MULTIPLE_OPERATIONS_TESTS, PRECISION_TESTS
)

class SimpleTestRunner:
    """評価なしのシンプルテスト実行"""
    
    def __init__(self):
        self.agent = None
        self.all_tests = self._load_all_tests()
        
    def _load_all_tests(self) -> List[Dict[str, Any]]:
        """全テストケースを読み込み"""
        all_tests = []
        test_collections = [
            ("basic", BASIC_TESTS),
            ("intermediate", INTERMEDIATE_TESTS),
            ("advanced", ADVANCED_TESTS),
            ("expert", EXPERT_TESTS),
            ("edge_case", EDGE_CASE_TESTS),
            ("japanese", JAPANESE_TESTS),
            ("english", ENGLISH_TESTS),
            ("mixed_language", MIXED_LANGUAGE_TESTS),
            ("large_number", LARGE_NUMBER_TESTS),
            ("multiple_operations", MULTIPLE_OPERATIONS_TESTS),
            ("precision", PRECISION_TESTS)
        ]
        
        for category_name, tests in test_collections:
            for test in tests:
                test_copy = test.copy()
                if 'category' not in test_copy:
                    test_copy['category'] = category_name
                all_tests.append(test_copy)
                
        return all_tests
    
    def initialize_agent(self) -> bool:
        """LangChainエージェントを初期化"""
        try:
            print("🔧 LangChainエージェントを初期化中...")
            self.agent = create_agent()
            print("✅ エージェント初期化完了")
            return True
        except Exception as e:
            print(f"❌ エージェント初期化失敗: {e}")
            return False
    
    def find_test_by_id(self, test_id: str) -> Optional[Dict[str, Any]]:
        """IDでテストケースを検索"""
        for test in self.all_tests:
            if test.get('id') == test_id:
                return test
        return None
    
    def find_tests_by_category(self, category: str) -> List[Dict[str, Any]]:
        """カテゴリでテストケースを検索"""
        return [test for test in self.all_tests if test.get('category') == category]
    
    def display_test_info(self, test: Dict[str, Any]):
        """テスト情報を表示"""
        print("\n" + "="*80)
        print(f"📋 テストID: {test.get('id', 'unknown')}")
        print(f"📂 カテゴリ: {test.get('category', 'unknown')}")
        print(f"🎯 複雑度: {test.get('complexity', 'unknown')}")
        print(f"🌐 言語: {test.get('language', 'unknown')}")
        print("="*80)
        print(f"📝 プロンプト:")
        print(f"   {test.get('prompt', '')}")
        print()
        
        # 期待される動作の説明（参考情報として）
        expected_functions = test.get('expected_functions', [])
        expected_result = test.get('expected_result')
        
        if expected_functions or expected_result is not None:
            print("💡 期待される動作（参考）:")
            if expected_functions:
                print(f"   関数呼び出し: {', '.join(expected_functions)}")
            if expected_result is not None:
                print(f"   期待結果: {expected_result}")
            print()
    
    def execute_test(self, test: Dict[str, Any]) -> str:
        """テストを実行して結果を返す"""
        if not self.agent:
            raise Exception("エージェントが初期化されていません")
            
        prompt = test.get('prompt', '')
        
        print("🚀 実行中...")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # LangChainエージェントでテスト実行
            response = self.agent.invoke({"input": prompt})
            
            # レスポンスから出力を抽出
            if isinstance(response, dict):
                output = response.get("output", str(response))
            else:
                output = str(response)
                
            execution_time = time.time() - start_time
            
            print("-" * 40)
            print(f"⏱️  実行時間: {execution_time:.2f}秒")
            print()
            
            return output
            
        except Exception as e:
            execution_time = time.time() - start_time
            print("-" * 40)
            print(f"❌ エラー発生 ({execution_time:.2f}秒): {e}")
            print()
            return f"エラー: {e}"
    
    def display_result(self, result: str):
        """結果をクリーンに表示"""
        print("📄 実行結果:")
        print("="*80)
        print(result)
        print("="*80)
        print()
    
    def run_single_test(self, test_id: str):
        """単一テストを実行"""
        test = self.find_test_by_id(test_id)
        if not test:
            print(f"❌ テストID '{test_id}' が見つかりません")
            return
            
        self.display_test_info(test)
        result = self.execute_test(test)
        self.display_result(result)
    
    def run_category_tests(self, category: str):
        """カテゴリのテストを実行"""
        tests = self.find_tests_by_category(category)
        if not tests:
            print(f"❌ カテゴリ '{category}' のテストが見つかりません")
            return
            
        print(f"📂 カテゴリ '{category}' のテスト実行 ({len(tests)}件)")
        
        for i, test in enumerate(tests, 1):
            print(f"\n📍 {i}/{len(tests)} 実行中...")
            self.display_test_info(test)
            result = self.execute_test(test)
            self.display_result(result)
            
            # 次のテストへの待機（キーボード割り込みで中断可能）
            if i < len(tests):
                try:
                    input("👆 結果を確認してください。次のテストに進むにはEnterキーを押してください (Ctrl+Cで中断)...")
                except KeyboardInterrupt:
                    print("\n\n⏹️  テスト実行を中断しました")
                    break
    
    def run_all_tests(self):
        """全テストを実行"""
        print(f"🎯 全テスト実行 ({len(self.all_tests)}件)")
        
        for i, test in enumerate(self.all_tests, 1):
            print(f"\n📍 {i}/{len(self.all_tests)} 実行中...")
            self.display_test_info(test)
            result = self.execute_test(test)
            self.display_result(result)
            
            # 次のテストへの待機
            if i < len(self.all_tests):
                try:
                    input("👆 結果を確認してください。次のテストに進むにはEnterキーを押してください (Ctrl+Cで中断)...")
                except KeyboardInterrupt:
                    print("\n\n⏹️  テスト実行を中断しました")
                    break
    
    def interactive_mode(self):
        """インタラクティブモード"""
        print("\n🎮 インタラクティブテストモード")
        print("="*50)
        
        while True:
            print("\n選択してください:")
            print("1. テストID で実行")
            print("2. カテゴリで実行")
            print("3. 全テスト実行")
            print("4. テスト一覧表示")
            print("5. 終了")
            
            choice = input("\n選択 (1-5): ").strip()
            
            if choice == "1":
                test_id = input("テストID を入力: ").strip()
                if test_id:
                    self.run_single_test(test_id)
                    
            elif choice == "2":
                print("\n利用可能なカテゴリ:")
                categories = set(test.get('category', 'unknown') for test in self.all_tests)
                for cat in sorted(categories):
                    count = len([t for t in self.all_tests if t.get('category') == cat])
                    print(f"  - {cat} ({count}件)")
                
                category = input("\nカテゴリ名を入力: ").strip()
                if category:
                    self.run_category_tests(category)
                    
            elif choice == "3":
                confirm = input("全テストを実行しますか？ (y/N): ").strip().lower()
                if confirm == 'y':
                    self.run_all_tests()
                    
            elif choice == "4":
                self.show_test_list()
                
            elif choice == "5":
                print("👋 終了します")
                break
                
            else:
                print("❌ 無効な選択です")
    
    def show_test_list(self):
        """テスト一覧を表示"""
        print("\n📋 利用可能なテスト一覧:")
        print("="*80)
        
        by_category = {}
        for test in self.all_tests:
            category = test.get('category', 'unknown')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(test)
        
        for category in sorted(by_category.keys()):
            print(f"\n📂 {category.upper()} ({len(by_category[category])}件):")
            for test in by_category[category][:5]:  # 最初の5件のみ表示
                print(f"   {test.get('id', 'unknown')}: {test.get('prompt', '')[:60]}...")
            if len(by_category[category]) > 5:
                print(f"   ... および {len(by_category[category]) - 5} 件")

def main():
    parser = argparse.ArgumentParser(description="シンプルテスト実行ツール")
    parser.add_argument("--test", help="実行するテストID")
    parser.add_argument("--category", help="実行するカテゴリ名")
    parser.add_argument("--all", action="store_true", help="全テストを実行")
    parser.add_argument("--interactive", action="store_true", help="インタラクティブモード")
    parser.add_argument("--list", action="store_true", help="テスト一覧を表示")
    
    args = parser.parse_args()
    
    # 引数なしの場合はインタラクティブモード
    if not any([args.test, args.category, args.all, args.interactive, args.list]):
        args.interactive = True
    
    print("🧪 シンプルテスト実行ツール")
    print("="*50)
    
    # Azure OpenAI API キー確認
    api_key = os.getenv("AZURE_OPENAI_GPT4.1_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        print("❌ AZURE_OPENAI_API_KEY環境変数が設定されていません")
        print("   export AZURE_OPENAI_API_KEY='your_api_key' を実行してください")
        sys.exit(1)
    
    runner = SimpleTestRunner()
    
    # テスト一覧表示のみの場合
    if args.list:
        runner.show_test_list()
        return
    
    # エージェント初期化
    if not runner.initialize_agent():
        print("❌ エージェントの初期化に失敗しました")
        sys.exit(1)
    
    try:
        if args.test:
            runner.run_single_test(args.test)
        elif args.category:
            runner.run_category_tests(args.category)
        elif args.all:
            runner.run_all_tests()
        elif args.interactive:
            runner.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  テスト実行を中断しました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()