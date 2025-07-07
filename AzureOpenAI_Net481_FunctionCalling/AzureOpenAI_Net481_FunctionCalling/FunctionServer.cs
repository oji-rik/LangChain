using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using AzureOpenAI_Net481_FunctionCalling.Models;

namespace AzureOpenAI_Net481_FunctionCalling
{
    public class FunctionServer
    {
        private HttpListener _listener;
        private readonly string _baseUrl = "http://localhost:8080/";
        private bool _isRunning = false;

        public async Task StartAsync()
        {
            try
            {
                _listener = new HttpListener();
                _listener.Prefixes.Add(_baseUrl);
                _listener.Start();
                _isRunning = true;

                Console.WriteLine($"Function Server started at {_baseUrl}");
                Console.WriteLine("Available endpoints:");
                Console.WriteLine("  GET /tools - Get available tool definitions");
                Console.WriteLine("  POST /execute - Execute a function");
                Console.WriteLine("Press 'q' to quit server...");

                var serverTask = Task.Run(async () =>
                {
                    while (_isRunning && _listener.IsListening)
                    {
                        try
                        {
                            var context = await _listener.GetContextAsync();
                            _ = Task.Run(() => ProcessRequestAsync(context));
                        }
                        catch (ObjectDisposedException)
                        {
                            // Expected when stopping the listener
                            break;
                        }
                        catch (HttpListenerException ex)
                        {
                            Console.WriteLine($"HTTP Listener error: {ex.Message}");
                            break;
                        }
                    }
                });

                // Wait for user input to quit
                while (_isRunning)
                {
                    var key = Console.ReadKey(true);
                    if (key.KeyChar == 'q' || key.KeyChar == 'Q')
                    {
                        break;
                    }
                }

                await StopAsync();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error starting server: {ex.Message}");
                throw;
            }
        }

        public async Task StopAsync()
        {
            _isRunning = false;
            if (_listener != null && _listener.IsListening)
            {
                _listener.Stop();
                _listener.Close();
                Console.WriteLine("Function Server stopped.");
            }
        }

        private async Task ProcessRequestAsync(HttpListenerContext context)
        {
            try
            {
                var request = context.Request;
                var response = context.Response;

                // Add CORS headers
                response.Headers.Add("Access-Control-Allow-Origin", "*");
                response.Headers.Add("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
                response.Headers.Add("Access-Control-Allow-Headers", "Content-Type");

                // Handle OPTIONS preflight request
                if (request.HttpMethod == "OPTIONS")
                {
                    response.StatusCode = 200;
                    response.Close();
                    return;
                }

                string responseString = "";
                response.ContentType = "application/json";

                try
                {
                    if (request.HttpMethod == "GET" && request.Url.AbsolutePath == "/tools")
                    {
                        responseString = GetToolDefinitions();
                        response.StatusCode = 200;
                    }
                    else if (request.HttpMethod == "POST" && request.Url.AbsolutePath == "/execute")
                    {
                        using (var reader = new StreamReader(request.InputStream, request.ContentEncoding))
                        {
                            var requestBody = await reader.ReadToEndAsync();
                            responseString = await ExecuteFunctionAsync(requestBody);
                            response.StatusCode = 200;
                        }
                    }
                    else
                    {
                        responseString = JsonConvert.SerializeObject(new { error = "Not Found" });
                        response.StatusCode = 404;
                    }
                }
                catch (Exception ex)
                {
                    responseString = JsonConvert.SerializeObject(new { error = ex.Message });
                    response.StatusCode = 500;
                    Console.WriteLine($"Request processing error: {ex.Message}");
                }

                var buffer = Encoding.UTF8.GetBytes(responseString);
                response.ContentLength64 = buffer.Length;
                await response.OutputStream.WriteAsync(buffer, 0, buffer.Length);
                response.Close();

                Console.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss} {request.HttpMethod} {request.Url.AbsolutePath} - {response.StatusCode}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing request: {ex.Message}");
                try
                {
                    context.Response.StatusCode = 500;
                    context.Response.Close();
                }
                catch { }
            }
        }

        private string GetToolDefinitions()
        {
            var tools = new List<ToolDefinition>
            {
                new ToolDefinition
                {
                    Name = "prime_factorization",
                    Description = @"単一の整数を素因数分解する。

重要な制約:
- 配列や複数の数値は同時処理できません
- 複数の数値の場合は、この関数を各数値に対して個別に呼び出してください
- 入力は1より大きい正の整数である必要があります
- 最大対応値: 1,000,000

使用例:
- 正しい: prime_factorization(12) → [2, 2, 3]
- 間違い: prime_factorization([12, 15, 18]) → エラー

複数の数値を処理する場合は、この関数を複数回呼び出してください。",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "number", new PropertySchema
                                {
                                    Type = "integer",
                                    Description = "素因数分解する単一の正の整数 (2以上1,000,000以下)"
                                }
                            }
                        },
                        Required = new[] { "number" }
                    }
                },
                new ToolDefinition
                {
                    Name = "sum",
                    Description = "整数リストの合計を計算する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "list", new PropertySchema
                                {
                                    Type = "array",
                                    Description = "合計を計算する整数のリスト",
                                    Items = new PropertySchema { Type = "integer" }
                                }
                            }
                        },
                        Required = new[] { "list" }
                    }
                },
                new ToolDefinition
                {
                    Name = "multiply",
                    Description = "整数リストの積を計算する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "list", new PropertySchema
                                {
                                    Type = "array",
                                    Description = "積を計算する整数のリスト",
                                    Items = new PropertySchema { Type = "integer" }
                                }
                            }
                        },
                        Required = new[] { "list" }
                    }
                },
                new ToolDefinition
                {
                    Name = "divide",
                    Description = "二つの数値を除算する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "dividend", new PropertySchema
                                {
                                    Type = "number",
                                    Description = "被除数"
                                }
                            },
                            {
                                "divisor", new PropertySchema
                                {
                                    Type = "number",
                                    Description = "除数"
                                }
                            }
                        },
                        Required = new[] { "dividend", "divisor" }
                    }
                },
                new ToolDefinition
                {
                    Name = "power",
                    Description = "べき乗を計算する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "base", new PropertySchema
                                {
                                    Type = "number",
                                    Description = "底"
                                }
                            },
                            {
                                "exponent", new PropertySchema
                                {
                                    Type = "number",
                                    Description = "指数"
                                }
                            }
                        },
                        Required = new[] { "base", "exponent" }
                    }
                },
                new ToolDefinition
                {
                    Name = "factorial",
                    Description = @"正の整数の階乗を計算する。

計算制限:
- 最大入力値: 1000 (BigInteger使用により大きな値も対応可能)
- 負の数には対応していません
- n = 0 の場合は 1 を返します (数学的定義)

結果の型:
- 戻り値は文字列形式 (非常に大きな数値のため)
- 100! は158桁の数値になります

使用例:
- factorial(5) → ""120""
- factorial(100) → ""93326215443944152681699...""

エラーハンドリング:
- n > 1000: 制限値超過エラー
- n < 0: 負の数エラー",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "n", new PropertySchema
                                {
                                    Type = "integer",
                                    Description = "階乗を計算する非負整数 (0以上1000以下)"
                                }
                            }
                        },
                        Required = new[] { "n" }
                    }
                },
                new ToolDefinition
                {
                    Name = "gcd",
                    Description = "最大公約数を計算する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "a", new PropertySchema
                                {
                                    Type = "integer",
                                    Description = "第一の整数"
                                }
                            },
                            {
                                "b", new PropertySchema
                                {
                                    Type = "integer",
                                    Description = "第二の整数"
                                }
                            }
                        },
                        Required = new[] { "a", "b" }
                    }
                },
                new ToolDefinition
                {
                    Name = "lcm",
                    Description = "最小公倍数を計算する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "a", new PropertySchema
                                {
                                    Type = "integer",
                                    Description = "第一の整数"
                                }
                            },
                            {
                                "b", new PropertySchema
                                {
                                    Type = "integer",
                                    Description = "第二の整数"
                                }
                            }
                        },
                        Required = new[] { "a", "b" }
                    }
                },
                new ToolDefinition
                {
                    Name = "is_prime",
                    Description = "数値が素数かどうかを判定する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "number", new PropertySchema
                                {
                                    Type = "integer",
                                    Description = "判定する整数"
                                }
                            }
                        },
                        Required = new[] { "number" }
                    }
                },
                new ToolDefinition
                {
                    Name = "square_root",
                    Description = "平方根を計算する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "number", new PropertySchema
                                {
                                    Type = "number",
                                    Description = "平方根を計算する非負数"
                                }
                            }
                        },
                        Required = new[] { "number" }
                    }
                },
                new ToolDefinition
                {
                    Name = "abs",
                    Description = "絶対値を計算する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "number", new PropertySchema
                                {
                                    Type = "number",
                                    Description = "絶対値を計算する数値"
                                }
                            }
                        },
                        Required = new[] { "number" }
                    }
                },
                new ToolDefinition
                {
                    Name = "modulo",
                    Description = "剰余を計算する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "dividend", new PropertySchema
                                {
                                    Type = "integer",
                                    Description = "被除数"
                                }
                            },
                            {
                                "divisor", new PropertySchema
                                {
                                    Type = "integer",
                                    Description = "除数"
                                }
                            }
                        },
                        Required = new[] { "dividend", "divisor" }
                    }
                },
                new ToolDefinition
                {
                    Name = "max",
                    Description = "整数リストの最大値を取得する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "list", new PropertySchema
                                {
                                    Type = "array",
                                    Description = "最大値を取得する整数のリスト",
                                    Items = new PropertySchema { Type = "integer" }
                                }
                            }
                        },
                        Required = new[] { "list" }
                    }
                },
                new ToolDefinition
                {
                    Name = "min",
                    Description = "整数リストの最小値を取得する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "list", new PropertySchema
                                {
                                    Type = "array",
                                    Description = "最小値を取得する整数のリスト",
                                    Items = new PropertySchema { Type = "integer" }
                                }
                            }
                        },
                        Required = new[] { "list" }
                    }
                },
                new ToolDefinition
                {
                    Name = "average",
                    Description = "整数リストの平均値を計算する",
                    Parameters = new ParametersSchema
                    {
                        Type = "object",
                        Properties = new Dictionary<string, PropertySchema>
                        {
                            {
                                "list", new PropertySchema
                                {
                                    Type = "array",
                                    Description = "平均値を計算する整数のリスト",
                                    Items = new PropertySchema { Type = "integer" }
                                }
                            }
                        },
                        Required = new[] { "list" }
                    }
                }
            };

            var toolsResponse = new ToolsResponse { Tools = tools };
            return JsonConvert.SerializeObject(toolsResponse, Formatting.Indented);
        }

        private async Task<string> ExecuteFunctionAsync(string requestBody)
        {
            try
            {
                var request = JsonConvert.DeserializeObject<FunctionRequest>(requestBody);
                
                if (request == null)
                {
                    return JsonConvert.SerializeObject(
                        FunctionResponse.CreateError("", "Invalid request format"));
                }

                Console.WriteLine($"Function call: {request.FunctionName} with arguments: {string.Join(", ", request.Arguments.Keys)}");

                object result = null;

                switch (request.FunctionName.ToLower())
                {
                    case "prime_factorization":
                        var numberObj = GetArgumentValue(request.Arguments, "number", "n", "num", "value", "integer");
                        if (numberObj != null)
                        {
                            var number = Convert.ToInt32(numberObj);
                            Console.WriteLine($"  → prime_factorization({number})");
                            result = MathFunctions.PrimeFactorization(number);
                        }
                        else
                        {
                            var availableArgs = string.Join(", ", request.Arguments.Keys);
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, 
                                    $"Missing number argument. Expected: 'number', 'n', 'num', 'value', or 'integer'. Received: {availableArgs}"));
                        }
                        break;

                    case "sum":
                        var listObj = GetArgumentValue(request.Arguments, "list", "numbers", "values", "arr", "data", "items");
                        if (listObj != null)
                        {
                            var numbers = ParseIntegerList(listObj, request.RequestId);
                            if (numbers == null) return JsonConvert.SerializeObject(FunctionResponse.CreateError(request.RequestId, "Invalid list format"));
                            
                            Console.WriteLine($"  → sum([{string.Join(", ", numbers)}])");
                            result = MathFunctions.Sum(numbers);
                        }
                        else
                        {
                            var availableArgs = string.Join(", ", request.Arguments.Keys);
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, 
                                    $"Missing list argument. Expected: 'list', 'numbers', 'values', 'arr', 'data', or 'items'. Received: {availableArgs}"));
                        }
                        break;

                    case "multiply":
                        var multiplyListObj = GetArgumentValue(request.Arguments, "list", "numbers", "values", "arr", "data", "items");
                        if (multiplyListObj != null)
                        {
                            var numbers = ParseIntegerList(multiplyListObj, request.RequestId);
                            if (numbers == null) return JsonConvert.SerializeObject(FunctionResponse.CreateError(request.RequestId, "Invalid list format"));
                            
                            Console.WriteLine($"  → multiply([{string.Join(", ", numbers)}])");
                            result = MathFunctions.Multiply(numbers);
                        }
                        else
                        {
                            var availableArgs = string.Join(", ", request.Arguments.Keys);
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, 
                                    $"Missing list argument. Expected: 'list', 'numbers', 'values', 'arr', 'data', or 'items'. Received: {availableArgs}"));
                        }
                        break;

                    case "divide":
                        var dividendObj = GetArgumentValue(request.Arguments, "dividend", "numerator", "a", "first");
                        var divisorObj = GetArgumentValue(request.Arguments, "divisor", "denominator", "b", "second");
                        if (dividendObj != null && divisorObj != null)
                        {
                            var dividend = Convert.ToDouble(dividendObj);
                            var divisor = Convert.ToDouble(divisorObj);
                            Console.WriteLine($"  → divide({dividend}, {divisor})");
                            result = MathFunctions.Divide(dividend, divisor);
                        }
                        else
                        {
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, "Missing dividend or divisor argument"));
                        }
                        break;

                    case "power":
                        var baseObj = GetArgumentValue(request.Arguments, "base", "number", "n", "x");
                        var exponentObj = GetArgumentValue(request.Arguments, "exponent", "exp", "power", "p");
                        if (baseObj != null && exponentObj != null)
                        {
                            var baseNum = Convert.ToDouble(baseObj);
                            var exponent = Convert.ToDouble(exponentObj);
                            Console.WriteLine($"  → power({baseNum}, {exponent})");
                            result = MathFunctions.Power(baseNum, exponent);
                        }
                        else
                        {
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, "Missing base or exponent argument"));
                        }
                        break;

                    case "factorial":
                        var factorialObj = GetArgumentValue(request.Arguments, "n", "number", "num", "value");
                        if (factorialObj != null)
                        {
                            var n = Convert.ToInt32(factorialObj);
                            Console.WriteLine($"  → factorial({n})");
                            result = MathFunctions.Factorial(n);
                        }
                        else
                        {
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, "Missing n argument"));
                        }
                        break;

                    case "gcd":
                        var gcdAObj = GetArgumentValue(request.Arguments, "a", "first", "x", "num1");
                        var gcdBObj = GetArgumentValue(request.Arguments, "b", "second", "y", "num2");
                        if (gcdAObj != null && gcdBObj != null)
                        {
                            var a = Convert.ToInt32(gcdAObj);
                            var b = Convert.ToInt32(gcdBObj);
                            Console.WriteLine($"  → gcd({a}, {b})");
                            result = MathFunctions.Gcd(a, b);
                        }
                        else
                        {
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, "Missing a or b argument"));
                        }
                        break;

                    case "lcm":
                        var lcmAObj = GetArgumentValue(request.Arguments, "a", "first", "x", "num1");
                        var lcmBObj = GetArgumentValue(request.Arguments, "b", "second", "y", "num2");
                        if (lcmAObj != null && lcmBObj != null)
                        {
                            var a = Convert.ToInt32(lcmAObj);
                            var b = Convert.ToInt32(lcmBObj);
                            Console.WriteLine($"  → lcm({a}, {b})");
                            result = MathFunctions.Lcm(a, b);
                        }
                        else
                        {
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, "Missing a or b argument"));
                        }
                        break;

                    case "is_prime":
                        var isPrimeObj = GetArgumentValue(request.Arguments, "number", "n", "num", "value");
                        if (isPrimeObj != null)
                        {
                            var number = Convert.ToInt32(isPrimeObj);
                            Console.WriteLine($"  → is_prime({number})");
                            result = MathFunctions.IsPrime(number);
                        }
                        else
                        {
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, "Missing number argument"));
                        }
                        break;

                    case "square_root":
                        var sqrtObj = GetArgumentValue(request.Arguments, "number", "n", "num", "value");
                        if (sqrtObj != null)
                        {
                            var number = Convert.ToDouble(sqrtObj);
                            Console.WriteLine($"  → square_root({number})");
                            result = MathFunctions.SquareRoot(number);
                        }
                        else
                        {
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, "Missing number argument"));
                        }
                        break;

                    case "abs":
                        var absObj = GetArgumentValue(request.Arguments, "number", "n", "num", "value");
                        if (absObj != null)
                        {
                            var number = Convert.ToDouble(absObj);
                            Console.WriteLine($"  → abs({number})");
                            result = MathFunctions.Absolute(number);
                        }
                        else
                        {
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, "Missing number argument"));
                        }
                        break;

                    case "modulo":
                        var modDividendObj = GetArgumentValue(request.Arguments, "dividend", "a", "first", "num1");
                        var modDivisorObj = GetArgumentValue(request.Arguments, "divisor", "b", "second", "num2");
                        if (modDividendObj != null && modDivisorObj != null)
                        {
                            var dividend = Convert.ToInt32(modDividendObj);
                            var divisor = Convert.ToInt32(modDivisorObj);
                            Console.WriteLine($"  → modulo({dividend}, {divisor})");
                            result = MathFunctions.Modulo(dividend, divisor);
                        }
                        else
                        {
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, "Missing dividend or divisor argument"));
                        }
                        break;

                    case "max":
                        var maxListObj = GetArgumentValue(request.Arguments, "list", "numbers", "values", "arr", "data", "items");
                        if (maxListObj != null)
                        {
                            var numbers = ParseIntegerList(maxListObj, request.RequestId);
                            if (numbers == null) return JsonConvert.SerializeObject(FunctionResponse.CreateError(request.RequestId, "Invalid list format"));
                            
                            Console.WriteLine($"  → max([{string.Join(", ", numbers)}])");
                            result = MathFunctions.Max(numbers);
                        }
                        else
                        {
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, "Missing list argument"));
                        }
                        break;

                    case "min":
                        var minListObj = GetArgumentValue(request.Arguments, "list", "numbers", "values", "arr", "data", "items");
                        if (minListObj != null)
                        {
                            var numbers = ParseIntegerList(minListObj, request.RequestId);
                            if (numbers == null) return JsonConvert.SerializeObject(FunctionResponse.CreateError(request.RequestId, "Invalid list format"));
                            
                            Console.WriteLine($"  → min([{string.Join(", ", numbers)}])");
                            result = MathFunctions.Min(numbers);
                        }
                        else
                        {
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, "Missing list argument"));
                        }
                        break;

                    case "average":
                        var avgListObj = GetArgumentValue(request.Arguments, "list", "numbers", "values", "arr", "data", "items");
                        if (avgListObj != null)
                        {
                            var numbers = ParseIntegerList(avgListObj, request.RequestId);
                            if (numbers == null) return JsonConvert.SerializeObject(FunctionResponse.CreateError(request.RequestId, "Invalid list format"));
                            
                            Console.WriteLine($"  → average([{string.Join(", ", numbers)}])");
                            result = MathFunctions.Average(numbers);
                        }
                        else
                        {
                            return JsonConvert.SerializeObject(
                                FunctionResponse.CreateError(request.RequestId, "Missing list argument"));
                        }
                        break;

                    default:
                        return JsonConvert.SerializeObject(
                            FunctionResponse.CreateError(request.RequestId, $"Unknown function: {request.FunctionName}"));
                }

                Console.WriteLine($"  → Result: {result}");
                return JsonConvert.SerializeObject(
                    FunctionResponse.CreateSuccess(request.RequestId, result));
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Function execution error: {ex.Message}");
                return JsonConvert.SerializeObject(
                    FunctionResponse.CreateError("", $"Function execution error: {ex.Message}"));
            }
        }

        /// <summary>
        /// 複数の可能なパラメータ名を試行して引数値を取得するヘルパーメソッド。
        /// LangChainがスキーマで定義されたものとは異なるパラメータ名を使用する傾向に対応。
        /// </summary>
        private static object GetArgumentValue(Dictionary<string, object> arguments, params string[] possibleNames)
        {
            foreach (string name in possibleNames)
            {
                if (arguments.ContainsKey(name))
                {
                    return arguments[name];
                }
            }
            return null;
        }

        /// <summary>
        /// 様々な入力形式から整数リストを解析するヘルパーメソッド
        /// </summary>
        private static List<int> ParseIntegerList(object listObj, string requestId)
        {
            try
            {
                if (listObj is Newtonsoft.Json.Linq.JArray jArray)
                {
                    return jArray.ToObject<List<int>>();
                }
                else if (listObj is List<object> objList)
                {
                    return objList.Select(Convert.ToInt32).ToList();
                }
                else if (listObj is object[] objArray)
                {
                    return objArray.Select(Convert.ToInt32).ToList();
                }
                return null;
            }
            catch
            {
                return null;
            }
        }
    }
}