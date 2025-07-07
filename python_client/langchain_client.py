import os
import sys
from typing import List
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from csharp_tools import create_tools_from_csharp_server, test_csharp_server_connection


def create_langchain_agent(
    azure_endpoint: str,
    azure_deployment: str,
    api_version: str = "2024-12-01-preview",
    csharp_server_url: str = "http://localhost:8080"
) -> AgentExecutor:
    """
    HTTP経由でC#関数を使用するLangChainエージェントを作成。
    
    Args:
        azure_endpoint: Azure OpenAI エンドポイントURL
        azure_deployment: Azure OpenAI デプロイメント名
        api_version: Azure OpenAI API バージョン
        csharp_server_url: C#関数サーバーのURL
        
    Returns:
        設定済みAgentExecutorインスタンス
    """
    
    # C#サーバー接続をテスト
    print(f"Testing connection to C# server at {csharp_server_url}...")
    if not test_csharp_server_connection(csharp_server_url):
        raise Exception(f"Cannot connect to C# server at {csharp_server_url}. Make sure the server is running.")
    print("✓ C# server connection successful")
    
    # Create Azure OpenAI client
    llm = AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        azure_deployment=azure_deployment,
        api_version=api_version,
        temperature=0.7
    )
    print("✓ Azure OpenAI client created")
    
    # Create tools from C# server
    print("Fetching tool definitions from C# server...")
    tools = create_tools_from_csharp_server(csharp_server_url)
    print(f"✓ Loaded {len(tools)} tools from C# server:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Create memory for conversation history
    memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history"
    )
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that can perform mathematical calculations using available tools. When asked to perform calculations, use the appropriate tools to get accurate results."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=100
    )
    
    print("✓ LangChain agent created successfully")
    return agent_executor


def create_agent():
    """
    デフォルト設定でLangChainエージェントを作成（テスト用）。
    
    Returns:
        設定済みAgentExecutorインスタンス
    """
    # デフォルト設定値
    AZURE_ENDPOINT = "https://weida-mbw67lla-swedencentral.cognitiveservices.azure.com/"
    AZURE_DEPLOYMENT = "gpt-4.1"
    CSHARP_SERVER_URL = "http://localhost:8080"
    
    # API キーの確認
    api_key = os.getenv("AZURE_OPENAI_GPT4.1_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        raise Exception("AZURE_OPENAI_API_KEY environment variable not set")
    
    return create_langchain_agent(
        azure_endpoint=AZURE_ENDPOINT,
        azure_deployment=AZURE_DEPLOYMENT,
        csharp_server_url=CSHARP_SERVER_URL
    )


def main():
    """インタラクティブチャットを実行するメイン関数。"""
    
    # 設定
    AZURE_ENDPOINT = "https://weida-mbw67lla-swedencentral.cognitiveservices.azure.com/"
    AZURE_DEPLOYMENT = "gpt-4.1"
    CSHARP_SERVER_URL = "http://localhost:8080"
    
    # Check for API key
    api_key = os.getenv("AZURE_OPENAI_GPT4.1_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        print("Error: AZURE_OPENAI_GPT4.1_API_KEY environment variable not set")
        print("Please set your Azure OpenAI API key:")
        print("  export AZURE_OPENAI_GPT4.1_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    try:
        # Create the agent
        print("Initializing LangChain agent with C# function integration...")
        agent_executor = create_langchain_agent(
            azure_endpoint=AZURE_ENDPOINT,
            azure_deployment=AZURE_DEPLOYMENT,
            csharp_server_url=CSHARP_SERVER_URL
        )
        
        print("\n" + "="*60)
        print("🚀 LangChain ↔ C# Function Integration Ready!")
        print("="*60)
        print("You can now ask questions that require mathematical calculations.")
        print("The agent will automatically use C# functions when needed.")
        print("\nExamples:")
        print("- '234を素因数分解し、その因数の総和を返してください'")
        print("- 'What are the prime factors of 60?'")
        print("- 'Find the sum of [1, 2, 3, 4, 5]'")
        print("\nType 'exit', 'quit', or '終了' to quit.")
        print("="*60)
        
        # Interactive chat loop
        while True:
            try:
                user_input = input("\n質問: ").strip()
                
                if user_input.lower() in ['exit', 'quit', '終了', '']:
                    print("終了します。")
                    break
                
                print("\n回答:")
                response = agent_executor.invoke({"input": user_input})
                print(f"\n{response['output']}")
                
            except KeyboardInterrupt:
                print("\n\n終了します。")
                break
            except Exception as e:
                print(f"\nエラーが発生しました: {str(e)}")
                
    except Exception as e:
        print(f"初期化エラー: {str(e)}")
        print("\nトラブルシューティング:")
        print("1. C#サーバーが起動していることを確認してください")
        print("2. Azure OpenAI API キーが正しく設定されていることを確認してください")
        print("3. ネットワーク接続を確認してください")
        sys.exit(1)


if __name__ == "__main__":
    main()