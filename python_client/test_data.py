"""
LangChainが複雑なプロンプトを分解し、適切な関数シーケンスを実行する能力を評価するための包括的テストデータ。

テストカテゴリ:
1. 複雑度レベル (基本、中級、上級、専門家)
2. 曖昧性の解決 (明確 vs 曖昧なプロンプト)
3. 文脈理解 (逐次、条件付き、依存操作)
4. エラーハンドリング (無効な入力、エッジケース)
5. スケーラビリティ (大きな数値、複数操作)
6. 多言語サポート (日本語、英語、混合)
7. 数学的精度 (複雑な計算の検証)
"""

# 1. 複雑度レベルテスト
BASIC_TESTS = [
    {
        "id": "basic_001",
        "prompt": "234を素因数分解してください",
        "expected_functions": ["prime_factorization"],
        "expected_result": [2, 3, 3, 13],
        "complexity": "basic",
        "category": "single_function"
    },
    {
        "id": "basic_002", 
        "prompt": "[1, 2, 3, 4, 5]の合計を計算してください",
        "expected_functions": ["sum"],
        "expected_result": 15,
        "complexity": "basic",
        "category": "single_function"
    },
    {
        "id": "basic_003",
        "prompt": "100は素数ですか？",
        "expected_functions": ["is_prime"],
        "expected_result": False,
        "complexity": "basic",
        "category": "single_function"
    },
    {
        "id": "basic_004",
        "prompt": "5の階乗を計算してください",
        "expected_functions": ["factorial"],
        "expected_result": 120,
        "complexity": "basic",
        "category": "single_function"
    },
    {
        "id": "basic_005",
        "prompt": "36の平方根を求めてください",
        "expected_functions": ["square_root"],
        "expected_result": 6.0,
        "complexity": "basic",
        "category": "single_function"
    }
]

INTERMEDIATE_TESTS = [
    {
        "id": "intermediate_001",
        "prompt": "234を素因数分解し、その因数の総和を返してください",
        "expected_functions": ["prime_factorization", "sum"],
        "expected_result": 21,
        "complexity": "intermediate",
        "category": "two_step_sequential"
    },
    {
        "id": "intermediate_002",
        "prompt": "12と18の最大公約数と最小公倍数を求めてください",
        "expected_functions": ["gcd", "lcm"],
        "expected_result": {"gcd": 6, "lcm": 36},
        "complexity": "intermediate",
        "category": "parallel_operations"
    },
    {
        "id": "intermediate_003",
        "prompt": "2の10乗を計算し、その結果が素数かどうか判定してください",
        "expected_functions": ["power", "is_prime"],
        "expected_result": {"power": 1024, "is_prime": False},
        "complexity": "intermediate",
        "category": "sequential_dependent"
    },
    {
        "id": "intermediate_004",
        "prompt": "[10, 20, 30, 40, 50]の最大値、最小値、平均値を求めてください",
        "expected_functions": ["max", "min", "average"],
        "expected_result": {"max": 50, "min": 10, "average": 30.0},
        "complexity": "intermediate",
        "category": "multiple_operations"
    },
    {
        "id": "intermediate_005",
        "prompt": "60を素因数分解し、その結果を掛け合わせて元の数を確認してください",
        "expected_functions": ["prime_factorization", "multiply"],
        "expected_result": {"factors": [2, 2, 3, 5], "verification": 60},
        "complexity": "intermediate",
        "category": "verification"
    }
]

ADVANCED_TESTS = [
    {
        "id": "advanced_001",
        "prompt": "1から100までの素数をすべて見つけ、それらの合計、平均、最大値を求めてください",
        "expected_functions": ["is_prime", "sum", "average", "max"],
        "expected_description": "Multiple prime checks, then statistical operations",
        "complexity": "advanced",
        "category": "batch_processing"
    },
    {
        "id": "advanced_002",
        "prompt": "フィボナッチ数列の最初の10項を生成し（1, 1, 2, 3, 5, 8, 13, 21, 34, 55）、各項が素数かどうか判定し、素数のみの合計を求めてください",
        "expected_functions": ["is_prime", "sum"],
        "expected_fibonacci": [1, 1, 2, 3, 5, 8, 13, 21, 34, 55],
        "expected_primes": [2, 3, 5, 13],
        "expected_result": 23,
        "complexity": "advanced",
        "category": "conditional_filtering"
    },
    {
        "id": "advanced_003",
        "prompt": "100の階乗を計算し、その桁数を求め、さらにその桁数の階乗を計算してください",
        "expected_functions": ["factorial", "factorial"],
        "expected_description": "Nested factorial operations with string length calculation",
        "complexity": "advanced",
        "category": "nested_operations"
    },
    {
        "id": "advanced_004",
        "prompt": "24を素因数分解し、各因数のべき乗（2^2, 3^1）を計算し、それらの合計と積を求めてください",
        "expected_functions": ["prime_factorization", "power", "power", "sum", "multiply"],
        "expected_description": "Factor analysis with power calculations",
        "complexity": "advanced",
        "category": "mathematical_analysis"
    },
    {
        "id": "advanced_005",
        "prompt": "1から20の数字について、各数の約数の個数を求め、約数の個数が最大の数とその約数の個数を特定してください",
        "expected_functions": ["prime_factorization", "max"],
        "expected_description": "Divisor counting analysis",
        "complexity": "advanced",
        "category": "number_theory"
    }
]

EXPERT_TESTS = [
    {
        "id": "expert_001",
        "prompt": "100以下の完全数（自分自身を除く約数の和が自分自身と等しい数）をすべて見つけ、それらの素因数分解を行い、各完全数の素因数の種類数を求めてください",
        "expected_functions": ["sum", "prime_factorization"],
        "expected_perfect_numbers": [6, 28],
        "expected_description": "Perfect number identification and prime factor analysis",
        "complexity": "expert",
        "category": "advanced_number_theory"
    },
    {
        "id": "expert_002", 
        "prompt": "ユークリッドの互除法を使って120と90の最大公約数を求める過程をシミュレートし、各ステップでの余りを記録し、最終的にGCDを求めてください",
        "expected_functions": ["modulo", "gcd"],
        "expected_steps": [(120, 90), (90, 30), (30, 0)],
        "expected_result": 30,
        "complexity": "expert",
        "category": "algorithm_simulation"
    },
    {
        "id": "expert_003",
        "prompt": "カタラン数の最初の6項（1, 1, 2, 5, 14, 42）について、各項を階乗で表現できるかチェックし、素数である項の平方根を求めてください",
        "expected_functions": ["factorial", "is_prime", "square_root"],
        "expected_catalan": [1, 1, 2, 5, 14, 42],
        "expected_description": "Catalan number analysis with multiple conditions",
        "complexity": "expert",
        "category": "sequence_analysis"
    }
]

# 2. 曖昧性解決テスト
CLEAR_PROMPTS = [
    {
        "id": "clear_001",
        "prompt": "prime_factorization(456)を実行してください",
        "expected_functions": ["prime_factorization"],
        "expected_result": [2, 2, 2, 3, 19],
        "category": "explicit_function_call"
    },
    {
        "id": "clear_002",
        "prompt": "リスト[7, 14, 21, 28]のsum()を計算してください",
        "expected_functions": ["sum"],
        "expected_result": 70,
        "category": "explicit_function_call"
    }
]

AMBIGUOUS_PROMPTS = [
    {
        "id": "ambiguous_001",
        "prompt": "456を分析してください",
        "expected_functions": ["prime_factorization"],
        "expected_description": "Should interpret as prime factorization",
        "category": "implicit_intent"
    },
    {
        "id": "ambiguous_002",
        "prompt": "これらの数字を処理してください: [7, 14, 21, 28]",
        "expected_functions": ["sum", "max", "min", "average"],
        "expected_description": "Should apply multiple statistical operations",
        "category": "multiple_interpretations"
    },
    {
        "id": "ambiguous_003",
        "prompt": "100について教えてください",
        "expected_functions": ["prime_factorization", "is_prime", "square_root"],
        "expected_description": "Should provide comprehensive analysis",
        "category": "open_ended_analysis"
    }
]

# 3. 文脈理解テスト
SEQUENTIAL_OPERATIONS = [
    {
        "id": "sequential_001",
        "prompt": "まず84を素因数分解してください。次に、得られた因数の合計を計算してください。最後に、その合計値の平方根を求めてください。",
        "expected_functions": ["prime_factorization", "sum", "square_root"],
        "expected_steps": [
            {"function": "prime_factorization", "input": 84, "output": [2, 2, 3, 7]},
            {"function": "sum", "input": [2, 2, 3, 7], "output": 14},
            {"function": "square_root", "input": 14, "output": 3.7416573867739413}
        ],
        "category": "explicit_sequence"
    },
    {
        "id": "sequential_002",
        "prompt": "72の約数の個数を求めたいです。そのために72を素因数分解し、各素因数の指数を使って約数の個数の公式を適用してください。",
        "expected_functions": ["prime_factorization"],
        "expected_description": "Prime factorization with divisor counting explanation",
        "category": "mathematical_reasoning"
    }
]

CONDITIONAL_OPERATIONS = [
    {
        "id": "conditional_001",
        "prompt": "数値Nを入力として、Nが素数なら1を返し、そうでなければNを素因数分解した結果を返してください。N=97で試してください。",
        "expected_functions": ["is_prime"],
        "expected_result": 1,
        "test_value": 97,
        "category": "conditional_logic"
    },
    {
        "id": "conditional_002",
        "prompt": "数値Mについて、Mが完全平方数なら平方根を返し、そうでなければMの絶対値を返してください。M=144で試してください。",
        "expected_functions": ["square_root"],
        "expected_result": 12.0,
        "test_value": 144,
        "category": "conditional_logic"
    }
]

# 4. エラーハンドリングテスト
INVALID_INPUT_TESTS = [
    {
        "id": "error_001",
        "prompt": "負の数 -5 の階乗を計算してください",
        "expected_error": "ArgumentException",
        "expected_message": "Factorial is not defined for negative numbers",
        "category": "negative_input_error"
    },
    {
        "id": "error_002",
        "prompt": "0で割り算をしてください: 10 ÷ 0",
        "expected_error": "ArgumentException", 
        "expected_message": "Cannot divide by zero",
        "category": "division_by_zero"
    },
    {
        "id": "error_003",
        "prompt": "負の数 -16 の平方根を計算してください",
        "expected_error": "ArgumentException",
        "expected_message": "Cannot calculate square root of negative number",
        "category": "invalid_sqrt"
    },
    {
        "id": "error_004",
        "prompt": "25の階乗を計算してください（オーバーフロー発生）",
        "expected_error": "ArgumentException",
        "expected_message": "Factorial calculation overflow for numbers greater than 20",
        "category": "overflow_error"
    }
]

EDGE_CASE_TESTS = [
    {
        "id": "edge_001",
        "prompt": "1を素因数分解してください",
        "expected_error": "ArgumentException",
        "expected_message": "Number must be greater than 1",
        "category": "boundary_condition"
    },
    {
        "id": "edge_002",
        "prompt": "空のリスト[]の合計を計算してください",
        "expected_result": 0,
        "expected_functions": ["sum"],
        "category": "empty_input"
    },
    {
        "id": "edge_003",
        "prompt": "0の階乗を計算してください",
        "expected_result": 1,
        "expected_functions": ["factorial"],
        "category": "special_case"
    }
]

# 5. スケーラビリティテスト
LARGE_NUMBER_TESTS = [
    {
        "id": "scale_001",
        "prompt": "1000000を素因数分解してください",
        "expected_functions": ["prime_factorization"],
        "expected_result": [2, 2, 2, 2, 2, 2, 5, 5, 5, 5, 5, 5],
        "category": "large_input"
    },
    {
        "id": "scale_002",
        "prompt": "1から1000までの数の合計を計算してください",
        "expected_functions": ["sum"],
        "expected_description": "Large range summation",
        "expected_result": 500500,
        "category": "large_range"
    },
    {
        "id": "scale_003",
        "prompt": "20の階乗（上限値）を計算してください",
        "expected_functions": ["factorial"],
        "expected_result": 2432902008176640000,
        "category": "boundary_performance"
    }
]

MULTIPLE_OPERATIONS_TESTS = [
    {
        "id": "multi_001",
        "prompt": "次の10個の数を同時に処理してください: [12, 15, 18, 20, 24, 30, 36, 40, 45, 60] - 各数を素因数分解し、それぞれの因数の合計を求め、全体の統計（最大、最小、平均）を出してください",
        "expected_functions": ["prime_factorization", "sum", "max", "min", "average"],
        "input_numbers": [12, 15, 18, 20, 24, 30, 36, 40, 45, 60],
        "category": "batch_processing"
    }
]

# 6. 多言語サポートテスト
JAPANESE_TESTS = [
    {
        "id": "jp_001",
        "prompt": "九十九を素因数分解してください",
        "expected_functions": ["prime_factorization"],
        "input_value": 99,
        "expected_result": [3, 3, 11],
        "category": "japanese_numbers"
    },
    {
        "id": "jp_002", 
        "prompt": "階乗の計算：六の階乗を求めてください",
        "expected_functions": ["factorial"],
        "input_value": 6,
        "expected_result": 720,
        "category": "japanese_numbers"
    }
]

ENGLISH_TESTS = [
    {
        "id": "en_001",
        "prompt": "Calculate the prime factorization of two hundred and fifty-six",
        "expected_functions": ["prime_factorization"],
        "input_value": 256,
        "expected_result": [2, 2, 2, 2, 2, 2, 2, 2],
        "category": "english_numbers"
    },
    {
        "id": "en_002",
        "prompt": "Find the greatest common divisor of forty-eight and sixty-four",
        "expected_functions": ["gcd"],
        "input_values": [48, 64],
        "expected_result": 16,
        "category": "english_numbers"
    }
]

MIXED_LANGUAGE_TESTS = [
    {
        "id": "mixed_001",
        "prompt": "Calculate 百二十八 (128) の prime factorization をしてください",
        "expected_functions": ["prime_factorization"],
        "input_value": 128,
        "expected_result": [2, 2, 2, 2, 2, 2, 2],
        "category": "mixed_language"
    }
]

# 7. 数学的精度テスト
PRECISION_TESTS = [
    {
        "id": "precision_001",
        "prompt": "2の平方根の精度を小数点以下10桁まで確認してください",
        "expected_functions": ["square_root"],
        "input_value": 2,
        "expected_precision": 10,
        "expected_result": 1.4142135623730951,
        "category": "floating_point_precision"
    },
    {
        "id": "precision_002",
        "prompt": "非常に大きな数での除算: 999999999 ÷ 3333333 の精度を確認してください",
        "expected_functions": ["divide"],
        "input_values": [999999999, 3333333],
        "expected_result": 300.0000003000001,
        "category": "large_number_division"
    }
]

VERIFICATION_TESTS = [
    {
        "id": "verify_001",
        "prompt": "ゴールドバッハ予想の検証：20を二つの素数の和で表してください（素数判定を使用）",
        "expected_functions": ["is_prime", "sum"],
        "target_number": 20,
        "expected_pairs": [(3, 17), (7, 13)],
        "category": "mathematical_conjecture"
    },
    {
        "id": "verify_002",
        "prompt": "ピタゴラス数の検証：3²+4²=5²を計算で確認してください",
        "expected_functions": ["power", "sum"],
        "expected_verification": True,
        "category": "theorem_verification"
    }
]

# 統合テストコレクション
ALL_TESTS = {
    "basic": BASIC_TESTS,
    "intermediate": INTERMEDIATE_TESTS, 
    "advanced": ADVANCED_TESTS,
    "expert": EXPERT_TESTS,
    "clear_prompts": CLEAR_PROMPTS,
    "ambiguous_prompts": AMBIGUOUS_PROMPTS,
    "sequential_operations": SEQUENTIAL_OPERATIONS,
    "conditional_operations": CONDITIONAL_OPERATIONS,
    "invalid_input_tests": INVALID_INPUT_TESTS,
    "edge_case_tests": EDGE_CASE_TESTS,
    "large_number_tests": LARGE_NUMBER_TESTS,
    "multiple_operations_tests": MULTIPLE_OPERATIONS_TESTS,
    "japanese_tests": JAPANESE_TESTS,
    "english_tests": ENGLISH_TESTS,
    "mixed_language_tests": MIXED_LANGUAGE_TESTS,
    "precision_tests": PRECISION_TESTS,
    "verification_tests": VERIFICATION_TESTS
}

# テスト統計
def get_test_statistics():
    """テストスイートに関する包括的な統計を返す"""
    total_tests = sum(len(test_group) for test_group in ALL_TESTS.values())
    
    stats = {
        "total_tests": total_tests,
        "by_category": {category: len(tests) for category, tests in ALL_TESTS.items()},
        "complexity_distribution": {
            "basic": len(BASIC_TESTS),
            "intermediate": len(INTERMEDIATE_TESTS),
            "advanced": len(ADVANCED_TESTS),
            "expert": len(EXPERT_TESTS)
        },
        "language_distribution": {
            "japanese": len(JAPANESE_TESTS),
            "english": len(ENGLISH_TESTS),
            "mixed": len(MIXED_LANGUAGE_TESTS)
        },
        "test_perspectives": [
            "Complexity Levels",
            "Ambiguity Resolution", 
            "Context Understanding",
            "Error Handling",
            "Scalability",
            "Multilingual Support",
            "Mathematical Accuracy"
        ]
    }
    
    return stats

if __name__ == "__main__":
    stats = get_test_statistics()
    print(f"Test Suite Statistics:")
    print(f"Total Tests: {stats['total_tests']}")
    print(f"Test Perspectives: {len(stats['test_perspectives'])}")
    for perspective in stats['test_perspectives']:
        print(f"  - {perspective}")