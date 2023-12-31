from web3 import Web3
from eth_abi import encode
from eth_abi.packed import encode_packed
from itertools import combinations
from coins import coins

# Uniswap V3 factory address
# https://docs.uniswap.org/contracts/v3/reference/deployments
factoryAddress = '0x1F98431c8aD98523631AE4a59f267346ea31F984'

# Fee tiers
# 1%, 0.3%, 0.05%, and 0.01%
fee_tiers = [10000, 3000, 500, 100]

# function to get pool address
def calculate_pool_address(factory, token_0, token_1, fee):
    POOL_INIT_CODE_HASH = '0xe34f199b19b2b4f47f68442619d555527d244f78a3297ea89325f843f87b8b54'

    # Sort tokens by address to conform to Uniswap's token0, token1 order
    [token_0, token_1] = sorted([token_0, token_1], key=lambda x: Web3.to_checksum_address(x))

    # Encode pool parameters
    abiEncoded = encode(['address', 'address', 'uint24'], (token_0, token_1, fee))

    salt = Web3.solidity_keccak(['bytes'], ['0x' +abiEncoded.hex()])
    abiEncoded_2 = encode_packed([ 'address', 'bytes32'], ( factory, salt))
    resPair = Web3.solidity_keccak(['bytes','bytes'], ['0xff' + abiEncoded_2.hex(), POOL_INIT_CODE_HASH])[12:]
    return(Web3.to_checksum_address(resPair.hex()))

# Calculate all unique combinations of two coin tickers
coin_pairs = combinations(coins.keys(), 2)

# Calculate the pool address for each pair and each fee tier
pool_addresses = []
for pair in coin_pairs:
    for fee in fee_tiers:
        # Look up the addresses for each ticker
        token_0_address = coins[pair[0]]
        token_1_address = coins[pair[1]]
        
        # Calculate the pool address using the addresses
        pool_address = calculate_pool_address(
            factory=factoryAddress,
            token_0=token_0_address,
            token_1=token_1_address,
            fee=fee
        )
        
        # Append the tickers, addresses, fee, and pool address to the list
        pool_addresses.append(((pair[0], token_0_address), (pair[1], token_1_address), fee, pool_address))

# Print the array of ((ticker_0, address_0), (ticker_1, address_1), fee, pool address) tuples
for item in pool_addresses:
    print(f"Pair: {item[0][0]}-{item[1][0]} ({item[0][1]}, {item[1][1]}), Fee: {item[2]}, Pool Address: {item[3]}")