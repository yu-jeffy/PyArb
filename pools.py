from web3 import Web3
from eth_abi import encode
from eth_abi.packed import encode_packed
from itertools import combinations

# Uniswap V3 factory address
# https://docs.uniswap.org/contracts/v3/reference/deployments
factoryAddress = '0x1F98431c8aD98523631AE4a59f267346ea31F984'

# coin dictionary, ticker : contract address
coins = {
  "WETH": '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
  "WBTC": '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
  "MKR" : '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',
  "LINK" : '0x514910771AF9Ca656af840dff83E8264EcF986CA'
}



# function to get pool address
def calculate_pool_address(factory = factoryAddress, token_0 = coins["WETH"], token_1 = coins["WBTC"], fee = 3000):
    POOL_INIT_CODE_HASH = '0xe34f199b19b2b4f47f68442619d555527d244f78a3297ea89325f843f87b8b54'
    abiEncoded_1 = encode(['address', 'address', 'uint24'], (token_0, token_1, fee )) if int(token_0,16)<int(token_1,16) else encode(['address', 'address', 'uint24'], (token_1, token_0, fee ))
    salt = Web3.solidity_keccak(['bytes'], ['0x' +abiEncoded_1.hex()])
    abiEncoded_2 = encode_packed([ 'address', 'bytes32'], ( factory, salt))
    resPair = Web3.solidity_keccak(['bytes','bytes'], ['0xff' + abiEncoded_2.hex(), POOL_INIT_CODE_HASH])[12:]
    return(resPair.hex())

# Calculate all unique combinations of two coins
coin_pairs = combinations(coins.values(), 2)

# Calculate the pool address for each pair and store them in an array
pool_addresses = [
    calculate_pool_address(
        factory=factoryAddress,
        token_0=pair[0],
        token_1=pair[1],
        fee=3000
    )
    for pair in coin_pairs
]

# Print the array of pool addresses
print(pool_addresses)