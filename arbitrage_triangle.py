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
# uses decimals from decimals.py
def calculate_price_with_decimals(sqrt_price_x96, token0_address, token1_address):
    token0_decimals = coins_decimals[token0_address]
    token1_decimals = coins_decimals[token1_address]
    price = (sqrt_price_x96 / (1 << 96)) ** 2
    # Adjust for token decimals
    price_adjusted = price * (10 ** token0_decimals) / (10 ** token1_decimals)
    return price_adjusted

# find triangle arbitrage
def find_triangle_arbitrage_opportunities(pool_data):
    # Create a graph where nodes are tokens and edges are pools with their respective prices
    graph = {}

    # Build the graph with correct prices
    for pool in pool_data:
        token0, token1, _, _, _, sqrt_price_x96, token0_address, token1_address, _, _, _ = pool
        token0_ticker, _ = token0
        token1_ticker, _ = token1

        # Ensure the correct order of decimals is used for the price calculation
        price = calculate_price_with_decimals(sqrt_price_x96, token0_address, token1_address)

        # Debug: Print the price and decimals for each pool
        print(f"Pool: {token0_ticker}-{token1_ticker}, Price: {price}, Decimals: {coins_decimals[token0_address]}, {coins_decimals[token1_address]}")

        if token0_ticker not in graph:
            graph[token0_ticker] = {}
        if token1_ticker not in graph:
            graph[token1_ticker] = {}

        # The price from token0 to token1
        graph[token0_ticker][token1_ticker] = {'price': price, 'pool': pool}
        # The price from token1 to token0 (inverse price)
        graph[token1_ticker][token0_ticker] = {'price': 1 / price, 'pool': pool}

    # Find cycles of length 3 (triangle arbitrage)
    for start_token in graph:
        for second_token in graph[start_token]:
            if start_token != second_token:  # Avoid self-loops
                for third_token in graph[second_token]:
                    if third_token != second_token and third_token != start_token:  # Avoid revisiting nodes
                        if start_token in graph[third_token]:  # Ensure the cycle is complete
                            # Calculate the product of the exchange rates
                            rate_product = (
                                graph[start_token][second_token]['price'] *
                                graph[second_token][third_token]['price'] *
                                graph[third_token][start_token]['price']
                            )
                            # If the product of rates is greater than 1, there is an arbitrage opportunity
                            if rate_product > 1:  # Using a threshold to account for fees and slippage
                                print(f"Triangle arbitrage opportunity: {start_token} -> {second_token} -> {third_token} -> {start_token}")
                                print(f"Rates: {graph[start_token][second_token]['price']}, {graph[second_token][third_token]['price']}, {graph[third_token][start_token]['price']}")
                                print(f"Product of rates: {rate_product}")
                                print(f"Pool Addresses: {graph[start_token][second_token]['pool'][3]}, {graph[second_token][third_token]['pool'][3]}, {graph[third_token][start_token]['pool'][3]}")
                                print("-" * 40)

# Call the function with the pool data
find_triangle_arbitrage_opportunities(pool_data)