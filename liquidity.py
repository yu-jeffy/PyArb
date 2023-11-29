from web3 import Web3
import json
from dotenv import load_dotenv
import os
from pools import pool_addresses  # Import pool_addresses from pools.py
from web3.exceptions import BadFunctionCallOutput

# Load environment variables from .env file
load_dotenv()

# Set up your Web3 provider using the environment variable
web3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URL')))

# Check if connected to Web3
if web3.is_connected():
    print("We are connected to Web3!")

# Load the Uniswap V3 Pool contract ABI from the external JSON file
with open('uniswap_pool_abi.json', 'r') as abi_file:
    pool_abi = json.load(abi_file)

# Function to query liquidity from a pool contract
def get_pool_liquidity(pool_address):
    try:
        checksum_address = Web3.to_checksum_address(pool_address)  # Convert to checksum address
        pool_contract = web3.eth.contract(address=checksum_address, abi=pool_abi)
        return pool_contract.functions.liquidity().call()
    except BadFunctionCallOutput:
        # If the contract call fails, return 0 liquidity
        return 0

# Function to get the liquidity for each pool and return an array of pool information with liquidity
def get_pool_liquidities(pool_addresses):
    pool_liquidities = []
    for item in pool_addresses:
        ticker_0, address_0 = item[0]
        ticker_1, address_1 = item[1]
        fee = item[2]
        pool_address = item[3]
        
        # Query the liquidity
        liquidity = get_pool_liquidity(pool_address)
        
        # Append the liquidity to the tuple
        item_with_liquidity = item + (liquidity,)
        
        # Append the result to the pool_liquidities array
        pool_liquidities.append(item_with_liquidity)
    return pool_liquidities

# Get the array of pool information with liquidity
pool_liquidities = get_pool_liquidities(pool_addresses)

# Filter out pools with zero liquidity and create a new list
pool_liquidities_valid = [pool_info for pool_info in pool_liquidities if pool_info[4] > 0]

# Print the array of pool information with non-zero liquidity
for pool_info in pool_liquidities_valid:
    print(f'Pair: {pool_info[0][0]}-{pool_info[1][0]} ({pool_info[0][1]}, {pool_info[1][1]}), Fee: {pool_info[2]}, Pool Address: {pool_info[3]}, Liquidity: {pool_info[4]}')