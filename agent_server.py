from openai import OpenAI
import os
from dotenv import load_dotenv
from quart import Quart, request, jsonify
from datetime import datetime
import argparse
from injective_functions.factory import InjectiveClientFactory
from injective_functions.utils.function_helper import (
    FunctionSchemaLoader,
    FunctionExecutor,
)
import json
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
import aiohttp

# Initialize Quart app (async version of Flask)
app = Quart(__name__)


class InjectiveChatAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Get API key from environment variable
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No OpenAI API key found. Please set the OPENAI_API_KEY environment variable."
            )

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # Initialize conversation histories
        self.conversations = {}
        # Initialize injective agents
        self.agents = {}
        schema_paths = [
            "./injective_functions/account/account_schema.json",
            "./injective_functions/auction/auction_schema.json",
            "./injective_functions/authz/authz_schema.json",
            "./injective_functions/bank/bank_schema.json",
            "./injective_functions/exchange/exchange_schema.json",
            "./injective_functions/staking/staking_schema.json",
            "./injective_functions/token_factory/token_factory_schema.json",
            "./injective_functions/wasm/wasm_schema.json",
            "./injective_functions/utils/mito_get_requests_schema.json"
        ]
        self.function_schemas = FunctionSchemaLoader.load_schemas(schema_paths)

    async def initialize_agent(
        self, agent_id: str, private_key: str, environment: str = "mainnet"
    ) -> None:
        """Initialize Injective clients if they don't exist"""
        if agent_id not in self.agents:
            clients = await InjectiveClientFactory.create_all(
                private_key=private_key, network_type=environment
            )
            self.agents[agent_id] = clients

    async def execute_function(
        self, function_name: str, arguments: dict, agent_id: str
    ) -> dict:
        """Execute the appropriate Injective function with error handling"""
        try:
            # Get the client dictionary for this agent
            clients = self.agents.get(agent_id)
            if not clients:
                return {
                    "error": "Agent not initialized. Please provide valid credentials."
                }

            return await FunctionExecutor.execute_function(
                clients=clients, function_name=function_name, arguments=arguments
            )

        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "details": {"function": function_name, "arguments": arguments},
            }

    async def get_response(
        self,
        message,
        session_id="default",
        private_key=None,
        agent_id=None,
        environment="mainnet",
    ):
        """Get response from OpenAI API."""
        await self.initialize_agent(
            agent_id=agent_id, private_key=private_key, environment=environment
        )
        print("initialized agents")
        try:
            # Initialize conversation history for new sessions
            if session_id not in self.conversations:
                self.conversations[session_id] = []

            # Add user message to conversation history
            self.conversations[session_id].append({"role": "user", "content": message})

            # Get response from OpenAI
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful AI assistant on Injective Chain. 
                    You will be answering all things related to injective chain, and help out with
                    on-chain functions.
                    
                    When handling market IDs, always use these standardized formats:
                    - For BTC perpetual: "BTC/USDT PERP" maps to "btcusdt-perp"
                    - For ETH perpetual: "ETH/USDT PERP" maps to "ethusdt-perp"
                    
                    When users mention markets:
                    1. If they use casual terms like "Bitcoin perpetual" or "BTC perp", interpret it as "BTC/USDT PERP"
                    2. If they mention "Ethereum futures" or "ETH perpetual", interpret it as "ETH/USDT PERP"
                    3. Always use the standardized format in your responses
                    
                    Before performing any action:
                    1. Describe what you're about to do
                    2. Ask for explicit confirmation
                    3. Only proceed after receiving a "yes"
                    
                    When making function calls:
                    1. Convert the standardized format (e.g., "BTC/USDT PERP") to the internal format (e.g., "btcusdt-perp")
                    2. When displaying results to users, convert back to the standard format
                    3. Always confirm before executing any functions
                    
                    For general questions, provide informative responses.
                    When users want to perform actions, describe the action and ask for confirmation but for fetching data you dont have to ask for confirmation.""",
                    }
                ]
                + self.conversations[session_id],
                functions=self.function_schemas,
                function_call="auto",
                max_tokens=2000,
                temperature=0.7,
            )

            response_message = response.choices[0].message
            print(response_message)
            # Handle function calling
            if (
                hasattr(response_message, "function_call")
                and response_message.function_call
            ):
                # Extract function details
                function_name = response_message.function_call.name
                function_args = json.loads(response_message.function_call.arguments)
                # Execute the function
                function_response = await self.execute_function(
                    function_name, function_args, agent_id
                )

                # Add function call and response to conversation
                self.conversations[session_id].append(
                    {
                        "role": "assistant",
                        "content": None,
                        "function_call": {
                            "name": function_name,
                            "arguments": json.dumps(function_args),
                        },
                    }
                )

                self.conversations[session_id].append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(function_response),
                    }
                )

                # Get final response
                second_response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model="gpt-4-turbo-preview",
                    messages=self.conversations[session_id],
                    max_tokens=2000,
                    temperature=0.7,
                )

                final_response = second_response.choices[0].message.content.strip()
                self.conversations[session_id].append(
                    {"role": "assistant", "content": final_response}
                )

                return {
                    "response": final_response,
                    "function_call": {
                        "name": function_name,
                        "result": function_response,
                    },
                    "session_id": session_id,
                }

            # Handle regular response
            bot_message = response_message.content
            if bot_message:
                self.conversations[session_id].append(
                    {"role": "assistant", "content": bot_message}
                )

                return {
                    "response": bot_message,
                    "function_call": None,
                    "session_id": session_id,
                }
            else:
                default_response = "I'm here to help you with trading on Injective Chain. You can ask me about trading, checking balances, making transfers, or staking. How can I assist you today?"
                self.conversations[session_id].append(
                    {"role": "assistant", "content": default_response}
                )

                return {
                    "response": default_response,
                    "function_call": None,
                    "session_id": session_id,
                }

        except Exception as e:
            error_response = f"I apologize, but I encountered an error: {str(e)}. How else can I help you?"
            return {
                "response": error_response,
                "function_call": None,
                "session_id": session_id,
            }

    def clear_history(self, session_id="default"):
        """Clear conversation history for a specific session."""
        if session_id in self.conversations:
            self.conversations[session_id].clear()

    def get_history(self, session_id="default"):
        """Get conversation history for a specific session."""
        return self.conversations.get(session_id, [])


# Initialize chat agent
agent = InjectiveChatAgent()


@app.route("/ping", methods=["GET"])
async def ping():
    """Health check endpoint"""
    return jsonify(
        {"status": "ok", "timestamp": datetime.now().isoformat(), "version": "1.0.0"}
    )


@app.route("/chat", methods=["POST"])
async def chat_endpoint():
    """Main chat endpoint"""
    data = await request.get_json()
    try:
        if not data or "message" not in data:
            return (
                jsonify(
                    {
                        "error": "No message provided",
                        "response": "Please provide a message to continue our conversation.",
                        "session_id": data.get("session_id", "default"),
                        "agent_id": data.get("agent_id", "default"),
                        "agent_key": data.get("agent_key", "default"),
                        "environment": data.get("environment", "testnet"),
                    }
                ),
                400,
            )

        session_id = data.get("session_id", "default")
        private_key = data.get("agent_key", "default")
        agent_id = data.get("agent_id", "default")
        response = await agent.get_response(
            data["message"], session_id, private_key, agent_id
        )

        return jsonify(response)
    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "response": "I apologize, but I encountered an error. Please try again.",
                    "session_id": data.get("session_id", "default"),
                }
            ),
            500,
        )


@app.route("/history", methods=["GET"])
async def history_endpoint():
    """Get chat history endpoint"""
    session_id = request.args.get("session_id", "default")
    return jsonify({"history": agent.get_history(session_id)})


@app.route("/clear", methods=["POST"])
async def clear_endpoint():
    """Clear chat history endpoint"""
    session_id = request.args.get("session_id", "default")
    agent.clear_history(session_id)
    return jsonify({"status": "success"})


def main():
    parser = argparse.ArgumentParser(description="Run the chatbot API server")
    parser.add_argument("--port", type=int, default=5000, help="Port for API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host for API server")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()

    config = Config()
    config.bind = [f"{args.host}:{args.port}"]
    config.debug = args.debug

    print(f"Starting API server on {args.host}:{args.port}")
    asyncio.run(serve(app, config))


if __name__ == "__main__":
    main()
