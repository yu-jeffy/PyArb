from web3 import Web3
import json
from dotenv import load_dotenv
import os
from pricing import pool_data

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

# price is in sqrtPriceX96 from the pool smart contract, function to convert
def calculate_price_from_sqrt_price(sqrt_price_x96, token0_decimals, token1_decimals):
    # Convert sqrtPriceX96 to actual price
    price = (sqrt_price_x96 / (1 << 96)) ** 2
    # Adjust for token decimals
    price = price * (10 ** token0_decimals) / (10 ** token1_decimals)
    return price

# find arbitrage between two pools
def find_simple_arbitrage_opportunities(pool_data):
    prices = {}
    pool_addresses = {}

    for pool in pool_data:
        token0, token1, _, pool_address, _, sqrt_price_x96, _, _, _, _, _ = pool
        price = calculate_price_from_sqrt_price(sqrt_price_x96)
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

# find triangle arbitrage 
def find_triangle_arbitrage_opportunities(pool_data):
    # Create a graph where nodes are tokens and edges are pools with their respective prices
    graph = {}
    for pool in pool_data:
        token0, token1, _, _, _, sqrt_price_x96, _, _, _, _, _ = pool
        price = calculate_price_from_sqrt_price(sqrt_price_x96)
        token0_ticker, token0_address = token0
        token1_ticker, token1_address = token1
        
        if token0_ticker not in graph:
            graph[token0_ticker] = {}
        if token1_ticker not in graph:
            graph[token1_ticker] = {}
        
        # Add both directions to the graph with their respective prices
        graph[token0_ticker][token1_ticker] = {'price': 1 / price, 'pool': pool}
        graph[token1_ticker][token0_ticker] = {'price': price, 'pool': pool}
    
    # Find cycles of length 3 (triangle arbitrage)
    for start_token in graph:
        for second_token in graph[start_token]:
            for third_token in graph[second_token]:
                if third_token in graph and start_token in graph[third_token]:
                    # Calculate the product of the exchange rates
                    rate_product = (
                        graph[start_token][second_token]['price'] *
                        graph[second_token][third_token]['price'] *
                        graph[third_token][start_token]['price']
                    )
                    # If the product of rates is greater than 1, there is an arbitrage opportunity
                    if rate_product > 1:
                        print(f"Triangle arbitrage opportunity: {start_token} -> {second_token} -> {third_token} -> {start_token}")
                        print(f"Rates: {graph[start_token][second_token]['price']}, {graph[second_token][third_token]['price']}, {graph[third_token][start_token]['price']}")
                        print(f"Product of rates: {rate_product}")
                        print("-" * 40)

find_triangle_arbitrage_opportunities(pool_data)