#!/usr/bin/env python3
"""
シンプルテスト実行のためのユーティリティ
評価機能を削除し、実行のみに特化

元のtest_utils.pyから評価ロジックを削除した簡素版
"""

import time
import os
from typing import List, Dict, Any
from datetime import datetime
import requests
from langchain_client import create_agent

class SimpleTestResult:
    """シンプルなテスト結果コンテナ（評価なし）"""
    def __init__(self, test_id: str, test_name: str, category: str):
        self.test_id = test_id
        self.test_name = test_name
        self.category = category
        self.execution_time = 0.0
        self.prompt = ""
        self.agent_response = ""
        self.error_message = ""
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式で結果を返す"""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "category": self.category,
            "execution_time": self.execution_time,
            "prompt": self.prompt,
            "agent_response": self.agent_response,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat()
        }

class SimpleTestExecutor:
    """評価なしのシンプルテスト実行エンジン"""
    
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url
        self.agent = None
        
    def check_server_availability(self) -> bool:
        """C#サーバーが利用可能かチェック"""
        try:
            response = requests.get(f"{self.server_url}/tools", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"サーバーチェック失敗: {e}")
            return False
            
    def initialize_agent(self) -> bool:
        """LangChainエージェントを初期化"""
        try:
            self.agent = create_agent()
            return True
        except Exception as e:
            print(f"エージェント初期化失敗: {e}")
            return False
            
    def execute_test(self, test_data: Dict[str, Any]) -> SimpleTestResult:
        """テストを実行（評価なし）"""
        result = SimpleTestResult(
            test_id=test_data.get("id", "unknown"),
            test_name=test_data.get("prompt", "")[:50] + "...",
            category=test_data.get("category", "unknown")
        )
        
        result.prompt = test_data.get("prompt", "")
        
        start_time = time.time()
        
        try:
            if not self.agent:
                raise Exception("エージェントが初期化されていません")
                
            # テストプロンプトを実行
            response = self.agent.invoke({"input": result.prompt})
            
            # レスポンスを処理
            if isinstance(response, dict):
                result.agent_response = response.get("output", str(response))
            else:
                result.agent_response = str(response)
                
        except Exception as e:
            result.error_message = str(e)
            result.agent_response = f"エラー: {e}"
            
        result.execution_time = time.time() - start_time
        return result

def check_prerequisites() -> bool:
    """前提条件をチェック"""
    print("🔍 前提条件をチェック中...")
    
    # API キーチェック
    api_key = os.getenv("AZURE_OPENAI_GPT4.1_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        print("❌ AZURE_OPENAI_API_KEY環境変数が設定されていません")
        return False
    
    # C#サーバーチェック
    executor = SimpleTestExecutor()
    if not executor.check_server_availability():
        print("❌ C#サーバーに接続できません (http://localhost:8080)")
        print("   C#サーバーが起動していることを確認してください")
        return False
    
    print("✅ 前提条件クリア")
    return True

def run_single_test_simple(test_data: Dict[str, Any]) -> SimpleTestResult:
    """単一テストをシンプルに実行"""
    executor = SimpleTestExecutor()
    
    if not executor.initialize_agent():
        result = SimpleTestResult(
            test_id=test_data.get("id", "unknown"),
            test_name="初期化失敗",
            category="error"
        )
        result.error_message = "エージェント初期化失敗"
        return result
    
    return executor.execute_test(test_data)

if __name__ == "__main__":
    # 簡単なテスト用サンプル
    sample_test = {
        "id": "sample_001",
        "prompt": "234を素因数分解してください",
        "category": "basic"
    }
    
    if check_prerequisites():
        print(f"\n🧪 サンプルテスト実行: {sample_test['id']}")
        print(f"📝 プロンプト: {sample_test['prompt']}")
        print("\n" + "="*50)
        
        result = run_single_test_simple(sample_test)
        
        print(f"⏱️  実行時間: {result.execution_time:.2f}秒")
        if result.error_message:
            print(f"❌ エラー: {result.error_message}")
        else:
            print("📄 結果:")
            print(result.agent_response)
        print("="*50)
    else:
        print("❌ 前提条件が満たされていません")