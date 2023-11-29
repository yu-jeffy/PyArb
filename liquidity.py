from web3 import Web3
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set up your Web3 provider using the environment variable
web3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URL')))

# Should return True if connected
print(web3.is_connected())  

# Load the Uniswap V3 Pool contract ABI from the external JSON file
with open('uniswap_pool_abi.json', 'r') as abi_file:
    pool_abi = json.load(abi_file)

# Function to query liquidity from a pool contract
def get_pool_liquidity(pool_address):
    checksum_address = Web3.to_checksum_address(pool_address)  # Convert to checksum address
    pool_contract = web3.eth.contract(address=checksum_address, abi=pool_abi)
    return pool_contract.functions.liquidity().call()

# Example usage:
# Suppose you have a pool address calculated from the previous steps
example_pool_address = '0xa6Cc3C2531FdaA6Ae1A3CA84c2855806728693e8'
liquidity = get_pool_liquidity(example_pool_address)
print(f'Liquidity in the pool: {liquidity}')