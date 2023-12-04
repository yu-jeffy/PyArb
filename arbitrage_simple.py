from web3 import Web3
import json
from dotenv import load_dotenv
import os
from pricing import pool_data
from decimals import coins_decimals
from coins import coins

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

def find_simple_arbitrage_opportunities_high_low(pool_data):
    # Dictionary to store prices for each token pair
    prices = {}
    # Dictionary to store pool addresses for each token pair
    pool_addresses = {}

    # Iterate over the pool data to populate the prices and pool_addresses dictionaries
    for pool in pool_data:
        token0, token1, _, pool_address, _, sqrt_price_x96, token0_address, token1_address, _, _ = pool
        # Calculate the price of token1 in terms of token0
        price_token0_to_token1 = calculate_price_with_decimals(sqrt_price_x96, token0_address, token1_address)
        # Calculate the price of token0 in terms of token1 (inverse price)
        price_token1_to_token0 = 1 / price_token0_to_token1

        # Store the prices and pool addresses using a consistent token pair ordering
        token_pair = tuple(sorted([token0[0], token1[0]]))

        if token_pair not in prices:
            prices[token_pair] = {'token0_to_token1': [], 'token1_to_token0': []}
            pool_addresses[token_pair] = {'token0_to_token1': [], 'token1_to_token0': []}

        # Store the prices and corresponding pool addresses
        prices[token_pair]['token0_to_token1'].append(price_token0_to_token1)
        prices[token_pair]['token1_to_token0'].append(price_token1_to_token0)
        pool_addresses[token_pair]['token0_to_token1'].append(pool_address)
        pool_addresses[token_pair]['token1_to_token0'].append(pool_address)

    # Compare prices for simple arbitrage opportunities
    for token_pair, price_dict in prices.items():
        # Check if there are prices in both directions
        if price_dict['token0_to_token1'] and price_dict['token1_to_token0']:
            # Find the best (lowest) buy price for token0_to_token1 and the best (highest) sell price for token1_to_token0
            best_buy_price = min(price_dict['token0_to_token1'])
            best_sell_price = max(price_dict['token1_to_token0'])
            best_buy_pool = pool_addresses[token_pair]['token0_to_token1'][price_dict['token0_to_token1'].index(best_buy_price)]
            best_sell_pool = pool_addresses[token_pair]['token1_to_token0'][price_dict['token1_to_token0'].index(best_sell_price)]

            # Calculate the price difference and percentage difference
            price_difference = best_sell_price - best_buy_price
            percentage_difference = (price_difference / best_buy_price) * 100

            # Check if there is an arbitrage opportunity
            if price_difference > 0:
                print(f"Arbitrage opportunity for {token_pair}: "
                      f"Buy at {best_buy_pool} (Price: {best_buy_price}), "
                      f"Sell at {best_sell_pool} (Price: {best_sell_price}). "
                      f"Price difference: {price_difference} ({percentage_difference:.2f}%)")
            else:
                print(f"No arbitrage opportunity for {token_pair}.")


def find_simple_arbitrage_opportunities(pool_data):
    # Dictionary to store prices for each direction of each token pair
    prices = {}
    # Dictionary to store pool addresses for each direction of each token pair
    pool_addresses = {}

    for pool in pool_data:
        # Unpack the pool data
        token0, token1, _, pool_address, _, sqrt_price_x96, token0_address, token1_address, _, _ = pool
        
        # Calculate the price of token1 in terms of token0
        price_token0_to_token1 = calculate_price_with_decimals(sqrt_price_x96, token0_address, token1_address)
        # Calculate the price of token0 in terms of token1 (inverse price)
        price_token1_to_token0 = 1 / price_token0_to_token1

        # Store the prices and pool addresses for both directions
        token_pair_0_to_1 = (token0[0], token1[0])
        token_pair_1_to_0 = (token1[0], token0[0])

        if token_pair_0_to_1 not in prices:
            prices[token_pair_0_to_1] = []
            pool_addresses[token_pair_0_to_1] = []
        if token_pair_1_to_0 not in prices:
            prices[token_pair_1_to_0] = []
            pool_addresses[token_pair_1_to_0] = []

        prices[token_pair_0_to_1].append(price_token0_to_token1)
        prices[token_pair_1_to_0].append(price_token1_to_token0)
        pool_addresses[token_pair_0_to_1].append(pool_address)
        pool_addresses[token_pair_1_to_0].append(pool_address)

    # Compare prices for simple arbitrage opportunities
    for token_pair, price_list in prices.items():
        # Check if the reverse token pair also exists in the dictionary
        reverse_token_pair = (token_pair[1], token_pair[0])
        if reverse_token_pair in prices:
            # Find the best buy price for token_pair and the best sell price for reverse_token_pair
            best_buy_price = min(price_list)
            best_sell_price = max(prices[reverse_token_pair])
            best_buy_pool = pool_addresses[token_pair][price_list.index(best_buy_price)]
            best_sell_pool = pool_addresses[reverse_token_pair][prices[reverse_token_pair].index(best_sell_price)]

            # Calculate the price difference and percentage difference
            price_difference = best_sell_price - best_buy_price
            percentage_difference = (price_difference / best_buy_price) * 100

            # Check if there is an arbitrage opportunity
            if price_difference > 0:
                print(f"Arbitrage opportunity for {token_pair}: "
                      f"Buy at {best_buy_pool} (Price: {best_buy_price}), "
                      f"Sell at {best_sell_pool} (Price: {best_sell_price}). "
                      f"Price difference: {price_difference} ({percentage_difference:.2f}%)")

find_simple_arbitrage_opportunities(pool_data)
