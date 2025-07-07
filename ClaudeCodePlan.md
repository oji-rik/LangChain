# ClaudeCodePlan - C# ↔ Python LangChain 連携システム

## 概要
C#（.NET Framework 4.8.1）で定義された関数を、Python LangChainエージェントが HTTP経由で呼び出すシステムを構築する。関数の実装はC#側のみに存在し、Python側は関数呼び出しのプロキシとして機能する。

## アーキテクチャ

```
┌─────────────────┐    HTTP Request     ┌─────────────────┐
│   Python        │ ─────────────────► │   C# Server     │
│   LangChain     │                    │  (.NET Fw 4.8.1)│
│   Agent         │ ◄───────────────── │                 │
└─────────────────┘    JSON Response   └─────────────────┘
```

## 技術スタック

### C#側 (.NET Framework 4.8.1)
- **HTTPサーバー**: `System.Net.HttpListener`
- **JSON処理**: `Newtonsoft.Json 13.0.3` (既存)
- **非同期処理**: `async/await` + `Task`

### Python側
- **LLM**: `langchain-openai.AzureChatOpenAI`
- **エージェント**: `langchain.agents.AgentExecutor`
- **HTTP通信**: `requests`
- **スキーマ定義**: `pydantic`

## 通信プロトコル

### エンドポイント設計
- `GET http://localhost:8080/tools` - 利用可能ツール一覧
- `POST http://localhost:8080/execute` - 関数実行

### リクエスト/レスポンス形式

**ツール定義取得**
```http
GET /tools
```
```json
{
  "tools": [
    {
      "name": "prime_factorization",
      "description": "整数を素因数分解する",
      "parameters": {
        "type": "object",
        "properties": {
          "number": {"type": "integer", "description": "対象の整数"}
        },
        "required": ["number"]
      }
    },
    {
      "name": "sum",
      "description": "整数リストの合計を計算する",
      "parameters": {
        "type": "object", 
        "properties": {
          "list": {"type": "array", "items": {"type": "integer"}}
        },
        "required": ["list"]
      }
    }
  ]
}
```

**関数実行**
```http
POST /execute
Content-Type: application/json

{
  "function_name": "prime_factorization",
  "arguments": {"number": 234},
  "request_id": "uuid-string"
}
```
```json
{
  "request_id": "uuid-string",
  "result": [2, 3, 3, 13],
  "success": true,
  "error": null
}
```

## 実装計画

### Phase 1: C#側HTTPサーバー実装

**1.1 HttpListenerサーバークラス作成**
```csharp
public class FunctionServer
{
    private HttpListener _listener;
    private readonly string _baseUrl = "http://localhost:8080/";
    
    public async Task StartAsync()
    {
        _listener = new HttpListener();
        _listener.Prefixes.Add(_baseUrl);
        _listener.Start();
        
        while (_listener.IsListening)
        {
            var context = await _listener.GetContextAsync();
            _ = Task.Run(() => ProcessRequestAsync(context));
        }
    }
}
```

**1.2 関数実行エンジン拡張**
- 既存の`PrimeFactorization`メソッド活用
- 新しい`Sum`メソッド追加
- 関数ディスパッチャー実装

**1.3 JSON シリアライゼーション**
- リクエスト/レスポンスのデータクラス定義
- Newtonsoft.Jsonでの変換処理

### Phase 2: Python側LangChainクライアント実装

**2.1 カスタムツールクラス**
```python
from langchain.tools import BaseTool
import requests
from typing import Any, Dict

class CSharpFunctionTool(BaseTool):
    name: str
    description: str
    base_url: str = "http://localhost:8080"
    
    def _run(self, **kwargs: Any) -> str:
        response = requests.post(
            f"{self.base_url}/execute",
            json={
                "function_name": self.name,
                "arguments": kwargs,
                "request_id": str(uuid.uuid4())
            }
        )
        return str(response.json()["result"])
```

**2.2 動的ツール生成**
```python
def create_tools_from_csharp():
    response = requests.get("http://localhost:8080/tools")
    tools_def = response.json()["tools"]
    
    tools = []
    for tool_def in tools_def:
        tool = CSharpFunctionTool(
            name=tool_def["name"],
            description=tool_def["description"]
        )
        tools.append(tool)
    return tools
```

**2.3 LangChainエージェント設定**
```python
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent

llm = AzureChatOpenAI(
    azure_endpoint="https://weida-mbw67lla-swedencentral.cognitiveservices.azure.com/",
    azure_deployment="gpt-4.1",
    api_version="2024-12-01-preview"
)

tools = create_tools_from_csharp()
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

### Phase 3: 統合テスト

**テストケース**
- 入力: "234を素因数分解し、その因数の総和を返してください"
- 期待される動作:
  1. `prime_factorization(234)` → `[2, 3, 3, 13]`
  2. `sum([2, 3, 3, 13])` → `21`
- 最終出力: "21"

**検証手順**
1. C#サーバー起動 (`http://localhost:8080`)
2. Python LangChainクライアント実行
3. テストプロンプト入力
4. 結果検証 (234 = 2×3×3×13, 2+3+3+13 = 21)

## ファイル構成

```
AzureOpenAI_Net481_FunctionCalling/
├── ClaudeCodePlan.md                    # このプラン文書
├── AzureOpenAI_Net481_FunctionCalling/
│   ├── Program.cs                       # 既存 (修正)
│   ├── FunctionServer.cs               # 新規 (HTTPサーバー)
│   ├── Models/                         # 新規
│   │   ├── FunctionRequest.cs
│   │   ├── FunctionResponse.cs
│   │   └── ToolDefinition.cs
│   └── AzureOpenAI_Net481_FunctionCalling.csproj  # 既存
├── python_client/                      # 新規ディレクトリ
│   ├── requirements.txt
│   ├── langchain_client.py
│   ├── csharp_tools.py
│   └── test_integration.py
└── README.md                           # 使用方法説明
```

## 開発順序
1. **C#サーバー実装** (FunctionServer.cs + Models)
2. **C#統合テスト** (サーバー単体動作確認)
3. **Pythonクライアント実装** (LangChainエージェント)
4. **統合テスト** (C# ↔ Python 連携確認)
5. **ドキュメント整備** (README.md作成)

## 実装メモ

### .NET Framework 4.8.1 制約
- `HttpListener`は利用可能
- `async/await`サポート済み
- `Newtonsoft.Json`を活用

### セキュリティ考慮事項
- localhostのみでの通信
- 入力検証の実装
- エラーハンドリングの充実

### パフォーマンス考慮事項
- 非同期処理による応答性向上
- 接続プールの利用
- JSON シリアライゼーションの最適化