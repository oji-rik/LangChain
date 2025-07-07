# C# ↔ Python LangChain Function Integration

このプロジェクトは、C#（.NET Framework 4.8.1）で定義された関数を、Python LangChainエージェントがHTTP経由で呼び出すシステムです。

## 概要

- **C#側**: 関数実行エンジン + HTTPサーバー
- **Python側**: LangChain エージェント + HTTPクライアント
- **通信**: HTTP/JSON ベースの相互通信（localhost:8080）

## 機能

### 利用可能な関数
1. **prime_factorization(number)** - 整数の素因数分解
2. **sum(list)** - 整数リストの合計計算

### テストケース
- 入力: "234を素因数分解し、その因数の総和を返してください"
- 期待結果: 21 （234 = 2×3×3×13, 2+3+3+13 = 21）

## セットアップ

### 前提条件
- .NET Framework 4.8.1
- Python 3.8+
- Azure OpenAI API キー

### 1. C#サーバーの起動

```bash
cd AzureOpenAI_Net481_FunctionCalling
# Visual Studio でビルドするか、MSBuildを使用
dotnet build  # または Visual Studio でビルド
cd bin/Debug
./AzureOpenAI_Net481_FunctionCalling.exe
```

プロンプトで「1」を選択してHTTPサーバーモードで起動：
```
Choose mode:
1. HTTP Server mode (for Python LangChain integration)
2. Original chat mode
Enter choice (1 or 2): 1
```

サーバーが起動すると以下のメッセージが表示されます：
```
Function Server started at http://localhost:8080/
Available endpoints:
  GET /tools - Get available tool definitions
  POST /execute - Execute a function
Press 'q' to quit server...
```

### 2. Python環境のセットアップ

```bash
cd python_client
pip install -r requirements.txt
```

### 3. Azure OpenAI API キーの設定

```bash
export AZURE_OPENAI_API_KEY="your_api_key_here"
```

## 使用方法

### インテグレーションテストの実行

```bash
cd python_client
python test_integration.py
```

このテストは以下を検証します：
1. C#サーバーとの直接通信
2. LangChainエージェントとの統合
3. テストケースの実行

### インタラクティブチャットの開始

```bash
cd python_client
python langchain_client.py
```

### 使用例

```
質問: 234を素因数分解し、その因数の総和を返してください

回答:
まず234を素因数分解します。

prime_factorization(234) を実行した結果: [2, 3, 3, 13]

次に、これらの因数の総和を計算します。

sum([2, 3, 3, 13]) を実行した結果: 21

したがって、234の素因数分解の結果は 2 × 3 × 3 × 13 で、
その因数の総和は 21 です。
```

## アーキテクチャ

### 通信フロー
```
Python LangChain → HTTP Request → C# Server
                ←  JSON Response ←
```

### エンドポイント
- `GET /tools` - 利用可能なツール定義を取得
- `POST /execute` - 関数を実行

### リクエスト例
```json
POST /execute
{
  "function_name": "prime_factorization",
  "arguments": {"number": 234},
  "request_id": "uuid-string"
}
```

### レスポンス例
```json
{
  "request_id": "uuid-string",
  "result": [2, 3, 3, 13],
  "success": true,
  "error": null
}
```

## ファイル構成

```
├── ClaudeCodePlan.md                    # 実装計画書
├── README.md                            # このファイル
├── AzureOpenAI_Net481_FunctionCalling/  # C#プロジェクト
│   ├── AzureOpenAI_Net481_FunctionCalling/
│   │   ├── Program.cs                   # メインプログラム
│   │   ├── FunctionServer.cs           # HTTPサーバー実装
│   │   └── Models/                     # データモデル
│   │       ├── FunctionRequest.cs
│   │       ├── FunctionResponse.cs
│   │       └── ToolDefinition.cs
│   └── AzureOpenAI_Net481_FunctionCalling.csproj
└── python_client/                      # Pythonクライアント
    ├── requirements.txt                # Python依存関係
    ├── langchain_client.py            # LangChainクライアント
    ├── csharp_tools.py               # C#関数ツール定義
    └── test_integration.py           # 統合テスト
```

## トラブルシューティング

### C#サーバーが起動しない
- .NET Framework 4.8.1がインストールされていることを確認
- ポート8080が使用されていないことを確認
- 管理者権限が必要な場合があります

### Python接続エラー
- C#サーバーが起動していることを確認
- ファイアウォール設定を確認
- `http://localhost:8080/tools` にブラウザでアクセスして動作確認

### Azure OpenAI接続エラー
- API キーが正しく設定されていることを確認
- エンドポイントURLが正しいことを確認
- API使用量制限に達していないことを確認

## 開発者向け情報

### 新しい関数の追加

1. **C#側**: `FunctionServer.cs`の`ExecuteFunctionAsync`メソッドに新しいケースを追加
2. **C#側**: `GetToolDefinitions`メソッドに新しいツール定義を追加
3. **Python側**: 自動的に新しいツールが認識されます

### デバッグ

- C#サーバーは詳細なログを出力します
- Python側は`verbose=True`でエージェント実行の詳細を表示
- HTTPリクエスト/レスポンスを確認するには、ブラウザの開発者ツールやPostmanを使用

## ライセンス

このプロジェクトはサンプル実装であり、教育目的で提供されています。