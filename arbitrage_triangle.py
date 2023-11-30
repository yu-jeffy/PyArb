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
    # Fetch the decimals for each token
    token0_decimals = coins_decimals[token0_address]
    token1_decimals = coins_decimals[token1_address]
    # Convert sqrtPriceX96 to actual price
    price = (sqrt_price_x96 / (1 << 96)) ** 2
    # Adjust for token decimals
    price_adjusted = price * (10 ** token0_decimals) / (10 ** token1_decimals)
    return price_adjusted


# build graph of coins and pools
def build_arbitrage_graph(pool_data):
    graph = {}
    for pool in pool_data:
        token0, token1, _, _, _, sqrt_price_x96, token0_address, token1_address, _, _ = pool
        token0_ticker, _ = token0
        token1_ticker, _ = token1

        # Calculate the price from token0 to token1
        price_token0_to_token1 = calculate_price_with_decimals(sqrt_price_x96, token0_address, token1_address)
        # Calculate the price from token1 to token0 (inverse price)
        price_token1_to_token0 = 1 / price_token0_to_token1

        # Add the prices to the graph
        if token0_ticker not in graph:
            graph[token0_ticker] = {}
        if token1_ticker not in graph:
            graph[token1_ticker] = {}

        graph[token0_ticker][token1_ticker] = {
            'price': price_token0_to_token1,
            'pool_address': token1_address
        }
        graph[token1_ticker][token0_ticker] = {
            'price': price_token1_to_token0,
            'pool_address': token0_address
        }
    return graph

# find triangle arbitrage
def find_triangle_arbitrage_opportunities(graph):
    # Helper function to perform DFS and find cycles of length three
    def dfs(start_token, current_token, visited, path, depth):
        # Debugging: print the current path and depth
        print(f"Visiting: {current_token}, Path: {path}, Depth: {depth}")

        if depth == 3:
            # Check if there's a direct path back to the start_token
            if start_token in graph[current_token]:
                # Complete the cycle if it's a valid triangle
                path.append(start_token)
                print(f"Found cycle: {path}")  # Debugging: print the found cycle
                yield path
            return

        visited.add(current_token)
        for next_token in graph[current_token]:
            if next_token not in visited:
                yield from dfs(start_token, next_token, visited, path + [next_token], depth + 1)
        visited.remove(current_token)

    # Iterate over each token and perform DFS to find arbitrage opportunities
    for start_token in graph:
        found_opportunity = False
        for cycle in dfs(start_token, start_token, set(), [], 0):
            # Calculate the product of exchange rates along the cycle
            rate_product = 1
            for i in range(len(cycle) - 1):
                rate_product *= graph[cycle[i]][cycle[i + 1]]['price']

            if rate_product > 1:
                # Arbitrage opportunity found
                print(f"Arbitrage opportunity: {' -> '.join(cycle)}")
                print(f"Product of rates: {rate_product}")
                print(f"Pool Addresses: {[graph[cycle[i]][cycle[i + 1]]['pool'][3] for i in range(len(cycle) - 1)]}")
                print("-" * 40)
                found_opportunity = True

        if not found_opportunity:
            print(f"No arbitrage opportunity found for {start_token}.")

# READY, AIM, FIRE! 🏴‍☠️
arbitrage_graph = build_arbitrage_graph(pool_data)
print(arbitrage_graph)
find_triangle_arbitrage_opportunities(arbitrage_graph)