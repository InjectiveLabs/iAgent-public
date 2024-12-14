![Banner!](assets/logo.png)
# Injective Agent

Welcome to your OpenAI-powered trading agent, designed for seamless operation on the Injective Chain. This agent is built to help you make data-driven trading decisions with ease, thanks to its ability to analyze data, predict trends, and carry out trades based on your commands—all through natural, human-friendly interaction.

## Overview

This project uses OpenAI technology to bring a user-focused trading experience to the Injective Chain. The agent responds to commands in plain language, allowing you to manage trading tasks effortlessly. Whether you're monitoring the market, making predictions, or executing trades, the agent is ready to support your strategic decisions.  
  
## Key Features

* Real-time data analysis: Stay informed with immediate insights.  
* Predictive analytics: Tap into machine learning for accurate forecasting.  
* Automated trade execution: Act on decisions without delay on the Injective Chain.  
* Natural language commands: Use everyday language to guide the agent's actions.  
* Flexible configurations: Customize settings to suit various trading scenarios.  
* Simple setup: Minimal dependencies for a quick and hassle-free start.

## Requirements
All required packages are listed in requirements.txt. Ensure you have Python 3.12+ installed, then install the dependencies as shown in the Installation section.

## Installation

### Option 1: Local Installation

1. Clone this repository and navigate into it:
   ```bash
   git clone https://github.com/InjectiveLabs/iAgent.git
   cd iAgent  
   ```	
2. Install the required packages:
	```bash  
	pip install -r requirements.txt  
	```
3. Setup OpenAI api Key
	```bash
	export OPENAI_API_KEY="your_openai_api_key_here"
	```
4. Running the agent  
	To start the backend on a specified port (default is 5000), run:  
	```bash
	python agent_server.py --port 5000  
	```  
	Once the agent is running, you can use quickstart.py to connect to it and interact with it via URL:
	```bash
	python quickstart.py --url http://0.0.0.0:5000
	```

### Option 2: Docker Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/InjectiveLabs/iAgent.git
   cd iAgent
   ```

2. Build the Docker image:
   ```bash
   docker build -t injective-agent .
   ```

3. Run the container:
   ```bash
   docker run -d \
     -p 5000:5000 \
     -e OPENAI_API_KEY="<YOUR_OPENAI_API_KEY_GOES_HERE>" \
     --name injective-agent \
     injective-agent
   ```

4. Connect to the agent:
   ```bash
   python quickstart.py --url http://localhost:5000
   ```

To stop the container:
```bash
docker stop injective-agent
```

To restart the container:
```bash
docker start injective-agent
```

# AI Agent Usage Guide

This guide will help you get started with the AI Agent, including how to use commands, switch networks, and manage agents.
New agents can be saved and updated in the agents_config.yaml file,
the structure of the yaml file looks like 
```yaml
agent10:
  address: <YOUR_WALLET_ADDRESS>
  created_at: '2024-11-07'
  private_key: <YOUR_WALLET_PRIVATEKEY>
  network: <YOUR_DESIRED_NETWORK>
```

## Commands Overview

The AI Agent supports several commands categorized into general actions, network configurations, and agent management.

### General Commands
| Command   | Description                                |
|-----------|--------------------------------------------|
| `quit`    | Exit the agent session.                    |
| `clear`   | Clear the current session output.          |
| `help`    | Display help information.                  |
| `history` | Show command history in the session.       |
| `ping`    | Check the agent's status.                  |
| `debug`   | Toggle debugging mode.                     |
| `session` | Display current session details.           |

### Network Commands
| Command             | Description                                        |
|---------------------|----------------------------------------------------|
| `switch_network`    | Switch between `mainnet` and `testnet` environments.|

### Agent Management Commands
| Command              | Description                                   |
|----------------------|-----------------------------------------------|
| `create_agent`       | Create a new AI agent.                        |
| `delete_agent`       | Delete an existing AI agent.                  |
| `switch_agent`       | Switch to a different AI agent.               |
| `list_agents`        | Display a list of available agents.           
  
    
## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## Disclaimer

This repository and the information contained herein (collectively, this "Repository") has been provided for informational and discussion purposes only, and does not constitute nor shall it be construed as offering legal, financial, investment, or business advice. No warranties or guarantees are made about the accuracy of any information or code contained herein. The legal and regulatory risks inherent to digital assets are not the subject of this Repository, and no decision to buy, sell, exchange, or otherwise utilize any digital asset is recommended based on the content of this Repository. USE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS. For guidance regarding the possibility of said risks, one should consult with his or her own appropriate legal and/or regulatory counsel. One should consult one's own advisors for any and all matters related to finance, business, legal, regulatory, and technical knowledge or expertise. Use, fork or publication of this Repository represents an acknowledgment that Injective Labs Inc. is indemnified from any form of liability associated with actions taken by any other interested party. That explicit indemnification is acknowledged by the user or publisher to be legally binding and severable from all other portions of this document.