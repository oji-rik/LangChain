using Azure;
using Azure.AI.Inference;
using Azure.AI.OpenAI;
using AzureOpenAI_Net481_FunctionCalling;
using OpenAI.Chat;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;

class ProgramSample_net481
{
    static async Task Main()
    {
        Console.WriteLine("Azure OpenAI Function Calling with HTTP Server");
        Console.WriteLine("Choose mode:");
        Console.WriteLine("1. HTTP Server mode (for Python LangChain integration)");
        Console.WriteLine("2. Original chat mode");
        Console.Write("Enter choice (1 or 2): ");

        var choice = Console.ReadLine();

        if (choice == "1")
        {
            var server = new FunctionServer();
            await server.StartAsync();
            return;
        }

        // Original implementation
        var deploymentName = "gpt-4.1";
        var apiKey = Environment.GetEnvironmentVariable("AZURE_OPENAI_GPT4.1_API_KEY");
        var endpoint = new Uri("https://weida-mbw67lla-swedencentral.cognitiveservices.azure.com/");
        var client = new AzureOpenAIClient(endpoint, new AzureKeyCredential(apiKey));
        var chatClient = client.GetChatClient(deploymentName);

        // 🚀 Tool（関数）定義
        var factorTool = ChatTool.CreateFunctionTool(
            functionName: "prime_factorization",
            functionDescription: "整数を素因数分解する",
            functionParameters: BinaryData.FromObjectAsJson(new
            {
                type = "object",
                properties = new
                {
                    number = new { type = "integer", description = "対象の整数" }
                },
                required = new[] { "number" }
            })
        );

        var sumTool = ChatTool.CreateFunctionTool(
            functionName: "sum",
            functionDescription: "整数リストの合計を計算する",
            functionParameters: BinaryData.FromObjectAsJson(new
            {
                type = "object",
                properties = new
                {
                    list = new
                    {
                        type = "array",
                        items = new { type = "integer" }
                    }
                },
                required = new[] { "list" }
            })
        );

        var tools = new[] { factorTool, sumTool };
        var history = new List<ChatMessage>
        {
            new SystemChatMessage("あなたは優秀なアシスタントです。")
        };

        while (true)
        {
            Console.Write("入力> ");
            var input = Console.ReadLine();
            if (input?.Trim().ToLower() == "exit") break;

            history.Add(new UserChatMessage(input));

            var response = chatClient.CompleteChat(
                history,
                new ChatCompletionOptions()
                {
                    Tools = { factorTool, sumTool }
                }
            );

            var choices = response.Value;
            if (choices.ToolCalls != null && choices.ToolCalls.Count > 0)
            {
                var call = choices.ToolCalls[0];
                string funcName = call.FunctionName;
                var argsJson = call.FunctionArguments.ToString();
                var d = JsonDocument.Parse(argsJson).RootElement;

                // 関数実行
                string resultJson;
                switch (funcName)
                {
                    case "prime_factorization":
                        int n = d.GetProperty("number").GetInt32();
                        var factors = PrimeFactorization(n);
                        resultJson = JsonSerializer.Serialize(factors);
                        Console.WriteLine($"素因数分解の結果は、{string.Join(" × ", factors)}です。");
                        history.Add(new UserChatMessage($"素因数分解の結果は、{string.Join(" × ", factors)}です。"));
                        break;
                    case "sum":
                        var list = d.GetProperty("list").EnumerateArray()
                            .Select(x => x.GetInt32());
                        int sum = list.Sum();
                        resultJson = JsonSerializer.Serialize(sum);
                        Console.WriteLine($"リストの合計は、{sum} です");
                        history.Add(new UserChatMessage($"リストの合計は、{sum} です"));
                        break;
                    default:
                        resultJson = JsonSerializer.Serialize(new { error = "unknown" });
                        break;
                }

                // ツール結果を履歴に追加し、最終応答を取得
                //history.Add(new ToolChatMessage(funcName, resultJson));
            }
            else
            {
                string contentString = choices.Content + "";
                Console.WriteLine(contentString);
            }

            // choice を JSON 形式でファイルに保存
            //string filePath = "response.txt";
            //string jsonString = JsonSerializer.Serialize(choice, new JsonSerializerOptions { WriteIndented = true });
            //await WriteToFileAsync(filePath, jsonString);
            //Console.WriteLine($"応答が {filePath} に保存されました。");
        }
    }

    static List<int> PrimeFactorization(int n)
    {
        var list = new List<int>();
        for (int i = 2; i * i <= n; i++)
            while (n % i == 0) { list.Add(i); n /= i; }
        if (n > 1) list.Add(n);
        return list;
    }

    //static async Task WriteToFileAsync(string path, string content)
    //{
    //    byte[] encodedText = System.Text.Encoding.UTF8.GetBytes(content);

    //    using (var fs = new FileStream(path, FileMode.Create, FileAccess.Write, FileShare.None, bufferSize: 4096, useAsync: true))
    //    {
    //        await fs.WriteAsync(encodedText, 0, encodedText.Length);
    //    }
    //}
}

