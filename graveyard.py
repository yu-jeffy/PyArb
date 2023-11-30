# Load the Uniswap V3 Pool contract ABI from the external JSON file
with open('uniswap_pool_abi.json', 'r') as abi_file:
    pool_abi = json.load(abi_file)

# price is in sqrtPriceX96 from the pool smart contract, function to convert
def calculate_price_from_sqrt_price(sqrt_price_x96):
    # Convert sqrtPriceX96 to actual price assuming both tokens have 18 decimals
    # ERC-20s usually have 18 decimals, because Ether has 18
    price = (sqrt_price_x96 / (1 << 96)) ** 2
    return price


