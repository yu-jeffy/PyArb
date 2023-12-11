from coins import coins
from pools import pool_addresses
from decimals import coins_decimals
from web3 import Web3;
from web3.exceptions import BadFunctionCallOutput
from dotenv import load_dotenv
import os
import json
from decimal import Decimal, getcontext
from web3 import Web3, middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy
import math

#Load environment variables from .env file
load_dotenv()

# Set up your Web3 provider using the environment variable
web3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URL')))

# Check if connected to Web3
if web3.is_connected():
    print("We are connected to Web3!")
else:
    raise Exception("Failed to connect to Web3, do you have your API key set?")


# gas price set speed to fast
web3.eth.set_gas_price_strategy(fast_gas_price_strategy)

# cache for gas price
web3.middleware_onion.add(middleware.time_based_cache_middleware)
web3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
web3.middleware_onion.add(middleware.simple_cache_middleware)

# print("fast gas price:")
# print(web3.eth.generate_gas_price())

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
def get_pool_liquidity_all(pool_addresses):
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
pool_liquidities = get_pool_liquidity_all(pool_addresses)

# Filter out pools with zero liquidity and create a new list.
# pools_valid is a list of tuples with the following structure:
# (token_0, token_1, fee, pool_address, liquidity)
pools_valid = [pool_info for pool_info in pool_liquidities if pool_info[4] > 0]

# Function to query price, sqrtpricex96, from a pool contract
def get_pool_price(pool_address):
    try:
        checksum_address = Web3.to_checksum_address(pool_address)  # Convert to checksum address
        pool_contract = web3.eth.contract(address=checksum_address, abi=pool_abi)
        slot0 = pool_contract.functions.slot0().call()
        sqrt_price_x96 = slot0[0]
        return sqrt_price_x96
    except Exception as e:
        print(f"An error occurred while fetching data for pool {pool_address}: {e}")
        return None

# Function to query prices for all pools
def get_pool_price_all(pool_addresses):
    pool_with_prices = []
    for item in pool_addresses:
        ticker_0, address_0 = item[0]
        ticker_1, address_1 = item[1]
        fee = item[2]
        pool_address = item[3]
        pool_liquidity = item[4]
        
        # Query the liquidity
        price = get_pool_price(pool_address)

        # Append the liquidity to the tuple
        item_with_price = item + (price,)
        
        # Append the result to the pool_liquidities array
        pool_with_prices.append(item_with_price)
    return pool_with_prices
    
# valid_pools_with_prices is a list of tuples with the following structure:
# (token_0, token_1, fee, pool_address, liquidity, sqrtpricex96)
valid_pools_with_prices = get_pool_price_all(pools_valid)

print("Valid pools:")
print(valid_pools_with_prices)
print()

# Function to calculate price from sqrtPriceX96 with decimal count of each token
getcontext().prec = 30 

# Function to calculate price from sqrtPriceX96 with decimal count of each token
def calculate_price(sqrt_price_x96, decimals0, decimals1):
    # Convert sqrtPriceX96 to the price (Token1/Token0)
    sqrt_price = Decimal(sqrt_price_x96) / Decimal(2**96)
    price_token0_token1 = sqrt_price**2
    price_adjustment_factor = Decimal(10)**(decimals1 - decimals0)
    
    return price_token0_token1 * price_adjustment_factor

# Empty dictionary to hold converted rates
pair_prices = {}

# Iterate over all pools in the data
for data in valid_pools_with_prices:
    token0 = data[0]
    token1 = data[1]
    pool_address = data[3]
    sqrtpricex96 = data[5]

    # Calculate the price for both directions
    price_t0_t1 = calculate_price(sqrtpricex96, coins_decimals[token0[1]], coins_decimals[token1[1]])
    price_t1_t0 = 1 / price_t0_t1

    # Define the dictionary key as 'TOKEN0_TICKER_to_TOKEN1_TICKER'
    key_t0_t1 = f"{token0[0].upper()}_TO_{token1[0].upper()}"
    key_t1_t0 = f"{token1[0].upper()}_TO_{token0[0].upper()}"

    # Initialize with empty list if key doesn't exist
    if key_t0_t1 not in pair_prices:
        pair_prices[key_t0_t1] = []
    if key_t1_t0 not in pair_prices:
        pair_prices[key_t1_t0] = []

    # Append new entry to the list associated with each key (tuple format for immutability)
    pair_prices[key_t0_t1].append((token0[1], token1[1], pool_address, price_t0_t1))
    pair_prices[key_t1_t0].append((token1[1], token0[1], pool_address, price_t1_t0))

# Print the prices for all pairs and directions
for key, entries in pair_prices.items():
    print()
    print(f"{key}:")
    for entry in entries:
        print(entry)
    print() 


# print("fast gas price:")
# print(web3.eth.generate_gas_price())

