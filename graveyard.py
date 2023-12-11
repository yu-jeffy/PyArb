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


# Helper function to calculate tick from the Uniswap price.
def calculate_tick_from_price(price: float) -> int:
    return math.floor(math.log(price) / math.log(1.0001))

# Fetch liquidity data for a range of ticks around start_tick_index within 
# the pool, checking up to num_ticks_to_check number of ticks.
def fetch_liquidity_data_for_ticks(pool_contract, start_tick_index, tick_spacing, num_ticks_to_check):
    ticks_data = []
    for i in range(num_ticks_to_check):
        tick_index = start_tick_index + i * tick_spacing
        ticks_data.append(
            pool_contract.functions.ticks(tick_index).call()
        )
    return ticks_data

# Estimate the number of ticks to check for liquidity based on the trade amount.
def calculate_number_of_ticks_to_check(trade_amount_eth, current_price, tick_spacing):
    """
    Note: This is a simplification for demonstration purposes.
    """
    # Assume a reasonable price impact per tick for large trades. You would need to calibrate this based on historical data.
    price_impact_per_tick = Decimal("0.0001")
    # Estimated number of ticks the price might move considering the trade amount
    estimated_ticks = int((Decimal(trade_amount_eth) * price_impact_per_tick) / current_price)
    # Return the number of ticks ensuring we check at least one tick
    return max(1, estimated_ticks // tick_spacing)

# Calculates the slippage for the trade across the ticks provided in ticks_data.
def calculate_trade_slippage(ticks_data, current_price, trade_amount_eth):
    """
    Note: This is a basic implementation and it assumes constant liquidity within the ticks.
    """
    trade_amount_remaining = Decimal(trade_amount_eth)
    total_output = Decimal(0)
    price_impact_per_liquidity = Decimal("0.0001")  # Arbitrary small value to simulate price impact per liquidity unit
    
    for tick in ticks_data:
        # Extract the gross liquidity from the tick data
        liquidity_gross = Decimal(tick[0])
        
        # Calculate the amount of output for this amount of liquidity
        # Adjust the output based on an estimated price impact per liquidity unit
        output = liquidity_gross * price_impact_per_liquidity
        total_output += output
        
        # Update the amount remaining for the trade
        trade_amount_remaining -= output
        
        # Stop if the trade amount has been fully processed
        if trade_amount_remaining <= 0:
            break
    
    # Calculate the average price, i.e., the amount of ETH traded per unit of output
    average_price = trade_amount_eth / total_output if total_output > 0 else 0
    
    # Slippage is the difference between the current price and the average traded price
    total_slippage_percent = (average_price - current_price) / current_price * 100
    total_slippage_eth = Decimal(trade_amount_eth) * total_slippage_percent / 100

    return float(total_slippage_eth), float(total_slippage_percent)

# Calculates the slippage for a trade amount in ETH across a Uniswap V3 pool.
def calculate_slippage(pool_address: str, trade_amount_eth: float) -> (float, float):
    """

    :param pool_address: The Uniswap V3 pool contract address.
    :param trade_amount_eth: The trade amount in ETH to calculate slippage for.
    :return: Tuple of total slippage amount and slippage percent.
    """

    pool_contract = web3.eth.contract(address=pool_address, abi=pool_abi)

    # Query the pool for current price and tickSpacing
    slot0 = pool_contract.functions.slot0().call()
    current_sqrt_price_x96 = Decimal(slot0[0])
    current_price = (current_sqrt_price_x96 / Decimal(2**96)) ** 2
    tick_spacing = pool_contract.functions.tickSpacing().call()

    # Find current tick index
    current_tick_index = calculate_tick_from_price(float(current_price))
    
    # Calculate ticks to check based on the size of the trade amount
    num_ticks_to_check = calculate_number_of_ticks_to_check(trade_amount_eth, current_price, tick_spacing)
    
    # Get tick data from pool contract
    ticks_data = fetch_liquidity_data_for_ticks(pool_contract, current_tick_index, tick_spacing, num_ticks_to_check)

    # Calculate slippage across all fetched ticks
    total_slippage_eth, slippage_percent = calculate_trade_slippage(ticks_data, current_price, trade_amount_eth)
    
    return total_slippage_eth, slippage_percent

# Calculate slippage for a trade amount of 1 ETH
total_slippage_eth, slippage_percent = calculate_slippage("0xCBCdF9626bC03E24f779434178A73a0B4bad62eD", .5)
print(f"Total Slippage in ETH: {total_slippage_eth}, Slippage Percentage: {slippage_percent:.2f}%")