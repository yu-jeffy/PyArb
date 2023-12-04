from web3 import Web3
import json
from dotenv import load_dotenv
import os
from pricing import pool_data
from decimals import coins_decimals

# Load environment variables from .env file
load_dotenv()

# Set up your Web3 provider using the environment variable
web3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URL')))

# Check if connected to Web3
if web3.is_connected():
    print("We are connected to Web3!")

# some ERC-20s have different decimals, so this calculates dynamically
def calculate_price_with_decimals(sqrt_price_x96, token0_address, token1_address):
    token0_decimals = coins_decimals[token0_address]
    token1_decimals = coins_decimals[token1_address]
    # Convert sqrtPriceX96 to actual price
    price = (sqrt_price_x96 / (1 << 96)) ** 2
    # Adjust for token decimals
    price_adjusted = price * (10 ** token0_decimals) / (10 ** token1_decimals)
    return price_adjusted

def find_simple_arbitrage_opportunities(pool_data):
    prices = {}
    pool_addresses = {}

    for pool in pool_data:
        token0, token1, _, pool_address, _, sqrt_price_x96, token0_address, token1_address, _, _ = pool
        # Use the updated price calculation function with decimals
        price = calculate_price_with_decimals(sqrt_price_x96, token0_address, token1_address)
        token_pair = (token0[0], token1[0])
        
        if token_pair not in prices:
            prices[token_pair] = []
            pool_addresses[token_pair] = []
        prices[token_pair].append(price)
        pool_addresses[token_pair].append(pool_address)
    
    # Compare prices for simple arbitrage
    for token_pair, price_list in prices.items():
        if len(price_list) > 1 and max(price_list) != min(price_list):
            max_price = max(price_list)
            min_price = min(price_list)
            price_difference = max_price - min_price
            percentage_difference = (price_difference / min_price) * 100

            max_price_pool = pool_addresses[token_pair][price_list.index(max_price)]
            min_price_pool = pool_addresses[token_pair][price_list.index(min_price)]

            print(f"Arbitrage opportunity for {token_pair}: "
                  f"Buy at {min_price_pool} (Price: {min_price}), "
                  f"Sell at {max_price_pool} (Price: {max_price}). "
                  f"Price difference: {price_difference} ({percentage_difference:.2f}%)")

find_simple_arbitrage_opportunities(pool_data)