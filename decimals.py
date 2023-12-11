from web3 import Web3
from dotenv import load_dotenv
import os
from coins import coins

# Load environment variables from .env file
load_dotenv()

# Set up your Web3 provider using the environment variable
web3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URL')))

# Check if connected to Web3
# if web3.is_connected():
    # print("We are connected to Web3!")

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
    # print(f"Token at address {token_address} has {decimals} decimals")  # Debugging output
    return decimals

# Dictionary to store coin addresses and their decimals
coins_decimals = {}

# Iterate over the coins dictionary and fetch decimals for each coin
for coin, address in coins.items():
    decimals = get_token_decimals(address)
    coins_decimals[address] = decimals
    # print(f"{coin} ({address}) has {decimals} decimals")

print("Coin decimal points:")
print(coins_decimals)
print()
