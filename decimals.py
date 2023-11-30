from web3 import Web3
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set up your Web3 provider using the environment variable
web3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URL')))

# Check if connected to Web3
if web3.is_connected():
    print("We are connected to Web3!")

def get_token_decimals(token_address):
    # ERC-20 token standard 'decimals' function ABI
    decimals_abi = {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
    token_contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=[decimals_abi])
    decimals = token_contract.functions.decimals().call()
    print(f"Token at address {token_address} has {decimals} decimals")  # Debugging output
    return decimals



# Example token addresses
token_addresses = [
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
    "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",  # WBTC
    "0x514910771AF9Ca656af840dff83E8264EcF986CA",  # LINK
    # ... add other token addresses
]

# Fetch and print the decimals for each token
for address in token_addresses:
    get_token_decimals(address)