#!/usr/bin/env python3
"""
デバッグ用の単一テスト実行
修正されたtest_utilsの動作確認用
"""

import os
import sys
from test_utils import TestExecutor
from test_data import BASIC_TESTS

def main():
    print("🔧 修正版テストシステムのデバッグ実行")
    print("="*50)
    
    # Azure OpenAI APIキーチェック
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        print("❌ AZURE_OPENAI_API_KEY環境変数が設定されていません")
        return 1
    
    # テストエグゼキューターを作成
    executor = TestExecutor()
    
    # サーバー接続確認
    if not executor.check_server_availability():
        print("❌ C#サーバーに接続できません")
        return 1
    
    # エージェント初期化
    if not executor.initialize_agent():
        print("❌ LangChainエージェントの初期化に失敗")
        return 1
    
    print("✅ 前提条件クリア")
    print()
    
    # 単一テストケースを実行
    test_case = BASIC_TESTS[0]  # "234を素因数分解してください"
    print(f"📋 テストケース: {test_case['id']}")
    print(f"📝 プロンプト: {test_case['prompt']}")
    print(f"🎯 期待関数: {test_case['expected_functions']}")
    print(f"🎯 期待結果: {test_case['expected_result']}")
    print()
    
    print("🚀 テスト実行開始...")
    print("-" * 50)
    
    # テスト実行
    result = executor.execute_test(test_case)
    
    print("-" * 50)
    print("📊 テスト結果サマリー:")
    print(f"   成功: {result.success}")
    print(f"   実行時間: {result.execution_time:.2f}秒")
    print(f"   検出関数: {result.actual_functions}")
    print(f"   抽出結果: {result.actual_result}")
    
    if result.error_message:
        print(f"   エラー: {result.error_message}")
    
    print("\n📋 詳細レスポンス:")
    print("=" * 60)
    print(result.agent_response)
    print("=" * 60)
    
    # もう一度簡易テストを実行（比較用）
    print("\n🔄 比較テスト（簡易版）:")
    try:
        simple_response = executor.agent.invoke({"input": test_case['prompt']})
        simple_output = simple_response.get("output", str(simple_response)) if isinstance(simple_response, dict) else str(simple_response)
        print(f"簡易レスポンス: {simple_output}")
    except Exception as e:
        print(f"簡易テストエラー: {e}")
    
    return 0 if result.success else 1

if __name__ == "__main__":
    sys.exit(main())