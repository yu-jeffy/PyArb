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


# Function to query additional pool data
def get_additional_pool_data(pool_address, pool_abi):
    pool_contract = web3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=pool_abi)
    try:
        # Get reserves of tokens (slot0)
        slot0 = pool_contract.functions.slot0().call()
        sqrt_price_x96 = slot0[0]
        
        # Get token addresses
        token0_address = pool_contract.functions.token0().call()
        token1_address = pool_contract.functions.token1().call()
        
        # Get fee information
        fee = pool_contract.functions.fee().call()
        
        # Get tick spacing
        tick_spacing = pool_contract.functions.tickSpacing().call()
        
        
        # Append all the data into a tuple
        pool_data = (sqrt_price_x96, token0_address, token1_address, fee, tick_spacing)
        return pool_data
    except Exception as e:
        print(f"An error occurred while fetching data for pool {pool_address}: {e}")
        return None


# Iterate over the pool_liquidities_valid list and query additional data for each pool
pool_data = []
for pool_info in pool_liquidities_valid:
    additional_data = get_additional_pool_data(pool_info[3], pool_abi)
    if additional_data:
        # Combine the existing pool info with the additional data
        full_pool_info = pool_info + additional_data
        pool_data.append(full_pool_info)

# Print the pool_data array with labels
for data in pool_data:
    print(f"Pair: {data[0][0]}-{data[1][0]}")
    print(f"Token 0 Address: {data[0][1]}")
    print(f"Token 1 Address: {data[1][1]}")
    print(f"Fee Tier: {data[2]}")
    print(f"Pool Address: {data[3]}")
    print(f"Liquidity: {data[4]}")
    print(f"Sqrt Price X96: {data[5]}")
    print(f"Token 0 Address (from pool): {data[6]}")
    print(f"Token 1 Address (from pool): {data[7]}")
    print(f"Pool Fee: {data[8]}")
    print(f"Tick Spacing: {data[9]}")
    print("-" * 40)  # Line break for readability