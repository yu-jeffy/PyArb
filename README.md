# PyArb

## Overview
This project aims to develop a Python-based arbitrage bot for Uniswap V3. The bot is designed to identify and potentially exploit price discrepancies across different Uniswap V3 pools for the same token pair. The project includes scripts for fetching pool data, calculating prices with proper token decimals, and identifying simple and triangular arbitrage opportunities.

## Project Structure
The project is divided into several Python files, each serving a specific purpose:

- `coins.py`: Contains a dictionary mapping token tickers to their respective Ethereum contract addresses.
- `decimals.py`: Fetches and stores the number of decimals for each token using the Web3 library and the ERC-20 `decimals` ABI.
- `pricing.py`: Queries Uniswap V3 pool contracts for liquidity and other pool-specific data.
- `arbitrage_simple.py`: Identifies simple arbitrage opportunities by comparing the prices of a token across different pools.
- `arbitrage_triangle.py`: Identifies triangular arbitrage opportunities by finding cycles of length three in a graph representation of token pools.

## Key Concepts

- **Pool Data**: Information about each pool, including token addresses, liquidity, `sqrt_price_x96`, and pool fees.
- **Price Calculation**: Conversion of `sqrt_price_x96` to actual token prices, adjusted for token decimals.
- **Graph Construction**: Representation of token pools as a graph where nodes are tokens and edges are pools with associated prices.
- **Arbitrage Identification**: Algorithms to detect price differences that can be exploited for profit, considering the direction of trades.

## Usage

1. **Environment Setup**: Install the required Python packages, such as `web3`, by running `pip install -r requirements.txt`.

2. **Ethereum Node Configuration**: Create a `.env` file in the root directory of the project with your Ethereum node HTTP provider URL. For example:
   ```
   WEB3_PROVIDER_URL="https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
   ```

3. **Token Configuration**: In `coins.py`, add the tokens you want the bot to monitor by specifying their ticker symbols and Ethereum contract addresses. For example:
   ```python
   # coins.py
   coins = {
       "WETH": '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
       "WBTC": '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
       "DAI": '0x6B175474E89094C44Da98b954EedeAC495271d0F',
       # Add more tokens as needed
   }
   ```

4. **Fetch Token Decimals**: Run `decimals.py` to fetch and store the number of decimals for each token in the `coins_decimals` dictionary. This information is crucial for accurate price calculations.

5. **Query Pool Data**: Use `pricing.py` to query Uniswap V3 pools for the latest data, including liquidity, prices, and fees.

6. **Identify Arbitrage Opportunities**: Execute `arbitrage_simple.py` to identify simple arbitrage opportunities across different pools for the same token pair. Alternatively, run `arbitrage_triangle.py` to identify triangular arbitrage opportunities by finding profitable cycles in the token graph.

7. **Review Results**: Analyze the output for potential arbitrage opportunities. The scripts will print information about profitable trades, including the tokens involved, the pools to execute the trades, and the expected profit margins.

## Considerations

- **Slippage**: The bot currently does not account for slippage, which can significantly impact the profitability of arbitrage trades, especially in pools with low liquidity.
- **Transaction Costs**: Ethereum gas fees are not considered in the current implementation and must be factored into the profitability calculation.
- **Execution Time**: Prices on decentralized exchanges can change rapidly, so the bot must execute trades quickly to capture the identified opportunities.
- **Smart Contract Interaction**: A production version of the bot would require smart contract integration to automate trade execution.

## Future Work

- Implement slippage estimation and include it in the profitability calculation.
- Integrate with Ethereum wallets and smart contracts to enable automated trade execution.
- Add real-time monitoring and alerting for arbitrage opportunities.
- Optimize the bot's performance and improve its resilience to changing market conditions.

## Disclaimer

This project is for educational purposes only. Arbitrage trading carries financial risks, and you should perform your own due diligence before running any trading bot on a live network. The developers of this project are not responsible for any financial losses incurred from using this bot.
