#!/bin/bash

# テスト実行スクリプト
echo "🧪 LangChain関数呼び出しテストスイート"
echo "=================================="

# 必要な依存関係をインストール
echo "📦 依存関係のインストール..."
pip install -r requirements.txt

# C#サーバーの接続確認
echo "🔍 C#サーバー接続確認..."
if curl -s http://localhost:8080/tools > /dev/null; then
    echo "✅ C#サーバー接続OK"
else
    echo "❌ C#サーバーに接続できません"
    echo "   以下の手順でC#サーバーを起動してください："
    echo "   1. Azure OpenAI APIキーを設定"
    echo "      export AZURE_OPENAI_API_KEY=\"your_api_key\""
    echo "   2. C#サーバーを起動"
    echo "      cd ../AzureOpenAI_Net481_FunctionCalling/AzureOpenAI_Net481_FunctionCalling/bin/Debug"
    echo "      ./AzureOpenAI_Net481_FunctionCalling.exe"
    echo "   3. プロンプトで '1' を選択（HTTPサーバーモード）"
    exit 1
fi

# Azure OpenAI APIキー確認
if [ -z "$AZURE_OPENAI_API_KEY" ]; then
    echo "❌ AZURE_OPENAI_API_KEY環境変数が設定されていません"
    echo "   export AZURE_OPENAI_API_KEY=\"your_api_key\" を実行してください"
    exit 1
fi

echo "✅ 環境確認完了"
echo ""

# テストオプション
echo "利用可能なテストオプション："
echo "1. 基本統合テスト (test_integration.py)"
echo "2. 簡易テスト (--quick)"
echo "3. 全てのテスト (--all)"
echo "4. 複雑度テスト (--complexity)"
echo "5. パフォーマンステスト (--benchmark-basic)"
echo ""

# デフォルトで基本統合テストを実行
if [ $# -eq 0 ]; then
    echo "🚀 基本統合テストを実行中..."
    python test_integration.py
else
    case $1 in
        "integration")
            echo "🚀 統合テストを実行中..."
            python test_integration.py
            ;;
        "quick")
            echo "⚡ 簡易テストを実行中..."
            python test_comprehensive.py --quick
            ;;
        "all")
            echo "🎯 全テストを実行中..."
            python test_comprehensive.py --all
            ;;
        "complexity")
            echo "📊 複雑度テストを実行中..."
            python test_comprehensive.py --complexity
            ;;
        "performance")
            echo "⚡ パフォーマンステストを実行中..."
            python test_performance.py --benchmark-basic
            ;;
        *)
            echo "❌ 不明なオプション: $1"
            echo "利用可能: integration, quick, all, complexity, performance"
            exit 1
            ;;
    esac
fi