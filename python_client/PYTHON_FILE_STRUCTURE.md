# Python Client File Structure Documentation

このドキュメントでは、LangChain ↔ C# Function Calling統合システムのPython側ファイル構造と機能について詳細に説明します。

## ファイル一覧

### 1. コアファイル

#### `langchain_client.py` - メインLangChainクライアント
- **機能**: Azure OpenAI + LangChainエージェントの作成とインタラクティブチャット
- **主要関数**:
  - `create_langchain_agent()`: 設定可能なエージェント作成
  - `create_agent()`: デフォルト設定エージェント作成（テスト用）
  - `main()`: インタラクティブチャットループ
- **特徴**: 
  - Azure OpenAI GPT-4.1との統合
  - C#サーバー接続テスト機能
  - 会話履歴管理
  - verbose モード対応

#### `csharp_tools.py` - C#関数通信ツール
- **機能**: LangChain ToolsとしてC#関数をHTTP経由で呼び出し
- **主要クラス**:
  - `CSharpFunctionTool`: 個別C#関数のLangChainツールラッパー
- **主要関数**:
  - `create_tools_from_csharp_server()`: C#サーバーからツール定義を動的生成
  - `test_csharp_server_connection()`: サーバー接続テスト
- **特徴**:
  - 動的ツール生成
  - パラメータ名柔軟対応（LangChain parameter mapping issue対応）
  - エラーハンドリング

### 2. テストシステムファイル

#### `test_utils.py` - テスト実行エンジン（中核）
- **機能**: 包括的テスト実行・評価システム
- **主要クラス**:
  - `TestResult`: 個別テスト結果コンテナ
  - `TestSession`: テストセッション管理
  - `TestExecutor`: メインテスト実行エンジン
- **主要メソッド**:
  - `extract_function_calls()`: エージェントレスポンスから関数呼び出し検出
    - LangChain新形式 "Invoking: `function_name`" パターン
    - 内容ベース関数推定（素因数分解、合計、最大公約数等）
    - 直接的関数名検出
  - `parse_numeric_result()`: 数値結果抽出（多段階パターンマッチング）
    - 関数実行直後結果抽出 [3, 3, 11]
    - 乗算形式抽出 "3 × 3 × 11"
    - カンマ区切り抽出
    - 日本語パターン "総和は21です"
  - `execute_test()`: 単一テスト実行（stdout キャプチャ対応）
  - `evaluate_test_success()`: 詳細デバッグ付きテスト評価
- **特徴**:
  - stdout キャプチャでverbose ログ取得
  - 多段階パターンマッチング
  - 詳細デバッグログ
  - エラーハンドリング

#### `test_data.py` - テストケース定義
- **機能**: 79+個の包括的テストケース定義
- **テストカテゴリー**:
  - BASIC_TESTS: 基本的な単一関数呼び出し
  - COMPLEX_TESTS: 複数ステップ・複数関数呼び出し
  - JAPANESE_TESTS: 日本語プロンプト専用
  - EDGE_CASE_TESTS: エッジケース・エラーハンドリング
  - PERFORMANCE_TESTS: パフォーマンス測定用
  - MULTILINGUAL_TESTS: 多言語対応
  - CONTEXTUAL_TESTS: 文脈理解・推論
- **各テストケース構造**:
  ```python
  {
      "id": "unique_test_id",
      "prompt": "テストプロンプト",
      "expected_functions": ["function_name"],
      "expected_result": 期待値,
      "category": "カテゴリー",
      "complexity": "difficulty_level",
      "language": "言語"
  }
  ```

#### `test_comprehensive.py` - メインテストスイート実行
- **機能**: コマンドライン引数によるテスト実行制御
- **実行オプション**:
  - `--quick`: 基本テスト (5件)
  - `--basic`: 基本テストスイート
  - `--complex`: 複雑テストスイート
  - `--japanese`: 日本語テスト
  - `--all`: 全テスト実行
  - `--category`: カテゴリー別実行
  - `--complexity`: 複雑度別実行
- **特徴**:
  - JSON結果出力
  - 詳細サマリー表示
  - エラーハンドリング

#### `test_performance.py` - パフォーマンス測定
- **機能**: 実行時間・スループット測定
- **測定項目**:
  - 個別テスト実行時間
  - 関数呼び出し頻度
  - 成功率統計
  - カテゴリー別パフォーマンス
- **出力**: JSON形式の詳細パフォーマンス報告

#### `test_reporter.py` - HTML報告書生成
- **機能**: Chart.js使用のビジュアル報告書作成
- **生成内容**:
  - テスト成功率グラフ
  - カテゴリー別統計
  - 実行時間分析
  - 失敗テスト詳細
- **出力**: `test_report.html`

#### `debug_test.py` - 単一テストデバッグ
- **機能**: 1つのテストケースの詳細デバッグ実行
- **デバッグ情報**:
  - 前提条件チェック
  - 詳細レスポンス表示
  - 比較テスト実行
  - ステップバイステップ分析

### 3. 統合・実行ファイル

#### `test_integration.py` - 基本統合テスト
- **機能**: C#サーバー直接通信 + LangChain統合テスト
- **テスト内容**:
  - C#サーバー接続確認
  - 直接関数呼び出し (prime_factorization, sum)
  - LangChain経由での複合テスト
  - 結果検証

#### `run_tests.sh` - テスト実行スクリプト
- **機能**: 環境確認・依存関係・テスト実行の自動化
- **チェック項目**:
  - C#サーバー接続確認
  - Azure OpenAI APIキー確認
  - 依存関係インストール
- **実行オプション**: integration, quick, all, complexity, performance

### 4. 設定・その他ファイル

#### `requirements.txt` - Python依存関係
```
langchain==0.1.0
langchain-openai==0.0.2
requests==2.31.0
```

## システム動作フロー

### 1. テスト実行フロー
```
run_tests.sh → test_comprehensive.py → test_utils.TestExecutor → langchain_client.create_agent() → csharp_tools → C#サーバー
```

### 2. 関数呼び出しフロー
```
LangChain Agent → csharp_tools.CSharpFunctionTool → HTTP POST → C#サーバー → JSON結果 → LangChain Agent
```

### 3. テスト評価フロー
```
Agent Response → extract_function_calls() → parse_numeric_result() → evaluate_test_success() → TestResult
```

## 主要な技術的特徴

### 1. LangChain Parameter Mapping Issue対応
- C#側で複数パラメータ名受け入れ機能
- `GetArgumentValue()` ヘルパーメソッド実装

### 2. Verbose Mode対応
- stdout キャプチャでLangChain詳細ログ取得
- 関数呼び出し詳細の確実な検出

### 3. 多段階パターンマッチング
- 関数実行直後結果の優先抽出
- 数学的表現からの配列抽出
- 日本語表現対応

### 4. 包括的エラーハンドリング
- 接続エラー、APIエラー、パース エラーの分類
- 詳細デバッグログによる問題特定

### 5. スケーラブルテスト設計
- カテゴリー別テスト実行
- 複雑度レベル管理
- パフォーマンス測定

## 今後の拡張ポイント

1. **新しい関数の追加**: `test_data.py`にテストケース追加
2. **新しい言語サポート**: 多言語パターンマッチング拡張
3. **新しい評価指標**: `test_utils.py`の評価ロジック拡張
4. **レポート機能強化**: `test_reporter.py`のビジュアライゼーション追加

このシステムは、LangChainエージェントの関数呼び出し能力を包括的にテストし、C#との統合品質を継続的に監視する役割を果たしています。