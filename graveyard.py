# Load the Uniswap V3 Pool contract ABI from the external JSON file
with open('uniswap_pool_abi.json', 'r') as abi_file:
    pool_abi = json.load(abi_file)

# price is in sqrtPriceX96 from the pool smart contract, function to convert
def calculate_price_from_sqrt_price(sqrt_price_x96):
    # Convert sqrtPriceX96 to actual price assuming both tokens have 18 decimals
    # ERC-20s usually have 18 decimals, because Ether has 18
    price = (sqrt_price_x96 / (1 << 96)) ** 2
    return price


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
        
        # Get historical data (observe function) for specified time intervals
        periods = [
            (5, 0),          # Last 5 seconds
            (30, 0),         # Last 30 seconds
            (60, 0),         # Last 1 minute
            (90, 0),         # Last 1 minute 30 seconds
            (120, 0),        # Last 2 minutes
            (180, 0),        # Last 3 minutes
            (240, 0),        # Last 4 minutes
            (300, 0),        # Last 5 minutes
            (600, 0),        # Last 10 minutes
            (900, 0),        # Last 15 minutes
            (1800, 0),       # Last 30 minutes
            (3600, 0)        # Last 1 hour
        ]

        historical_data = []
        try:
            for period in periods:
                # Call `observe` with the start and end of the period
                tick_cumulatives, seconds_per_liquidity_cumulative_x128s = pool_contract.functions.observe(period).call()
                
                # Calculate the time-weighted average tick from the cumulative values
                time_weighted_average_tick = (tick_cumulatives[1] - tick_cumulatives[0]) / (period[0])
                
                # Append the time-weighted average tick to the historical data list
                historical_data.append(time_weighted_average_tick)
        except Exception as e:
            print(f"An error occurred while fetching historical data for pool {pool_address}: {e}")
            historical_data = None

        # Append all the data into a tuple
        pool_data = (sqrt_price_x96, token0_address, token1_address, fee, tick_spacing, historical_data)
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
    print(f"Historical Data: {data[10]}")
    print("-" * 40)  # Line break for readability