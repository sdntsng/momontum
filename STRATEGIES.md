# Algorithmic Trading Strategies & Research

This document outlines top-performing algorithmic trading strategies for cryptocurrency in 2024/2025, derived from current market research. It serves as a guide for selecting and implementing strategies within the Momontum framework.

## 1. Core Strategy Classes

### A. Momentum Trading
**Concept:** "The trend is your friend." Assets that have performed well in the past are likely to continue performing well in the short term.
-   **Logic:** Buy when price > N-period MA, or when RSI > 50 and rising. Sell when trend breaks.
-   **Best For:** Trending markets (Bull/Bear runs).
-   **Crypto Context:** crypto markets are notoriously trend-heavy due to retail sentiment and FOMO.
-   **Variations:**
    -   *Time-Series Momentum:* Focus on a single asset's past performance.
    -   *Cross-Sectional Momentum:* Buy the top N performing coins relative to the rest of the market (e.g., "Long Top 10 Alts vs BTC").

### B. Mean Reversion
**Concept:** "What goes up must come down." Prices eventually return to their historical average.
-   **Logic:** Short when price > Upper Bollinger Band (Overbought). Long when price < Lower Bollinger Band (Oversold).
-   **Best For:** Sideways/Ranging markets.
-   **Crypto Context:** Effective for stablecoins pairs or during consolidation phases. High risk during breakouts (price doesn't revert, it moons/crashes).
-   **Key Metric:** Z-Score of price relative to moving average.

### C. Statistical Arbitrage (Stat Arb)
**Concept:** Exploiting pricing inefficiencies between correlated assets.
-   **Pairs Trading:** Identify two coins that move together (e.g., BTC & ETH, or MATIC & ETH). If the spread diverges (one goes up, one stays flat), short the winner and long the loser, betting they will converge.
-   **Triangular Arbitrage:** Exploiting price differences between three currencies (e.g., BTC/USDT -> ETH/BTC -> ETH/USDT). Hard to execute without HFT infrastructure.
-   **Funding Rate Arbitrage:** Delta-neutral strategy. Buy spot, Short Futures. Collect the funding rate (usually positive in bull markets) while hedging price risk.

## 2. Advanced Combinations

| Combo | Logic | Why it works |
| :--- | :--- | :--- |
| **Momentum + Volatility Filter** | Only enter momentum trades when Volatility (ATR) is *expanding*. | Avoids "whipsaw" losses in low-volatility chop. |
| **Mean Reversion + Trend Filter** | Only Mean Revert *in direction of macro trend* (e.g. Buy dips in Uptrend). | Reduces risk of stepping in front of a steamroller. |
| **ML-Enhanced Signals** | Use Linear Regression/XGBoost to predict next-tick price (like current Momontum engine). Use this prediction as dynamic threshold for entry. | Adapts to changing market conditions faster than static rules. |

## 3. Asset Class Performance Matrix

| Asset Class | Momentum | Mean Reversion | Stat Arb |
| :--- | :--- | :--- | :--- |
| **Bitcoin (BTC)** | **High**. Institutional flows create sustained trends. | Medium. Harder to exploit, efficient market. | High (vs Futures/ETFs). |
| **Ethereum (ETH)** | **High**. Follows BTC but with higher beta. | Medium. | High (vs BTC). |
| **Top 10 Alts** (SOL, BNB) | **High**. Driven by ecosystem narratives. | Low. Prone to violent breakouts. | Medium. |
| **Mid Caps** (Top 100) | Medium. Trends can be pump-and-dump. | **High**. Inefficiencies exist. | **High**. Correlations often lag BTC. |
| **Shneaky Gems** (Low Cap) | **Extreme**. 10x or 0. | Dangerous. Assets may never revert (go to 0). | N/A (Liquidity risk). |

## 4. Testing Framework Requirements

To properly validate these strategies, our framework needs:

1.  **Multi-Asset Data Engine:**
    -   Ability to pull "baskets" (e.g., `get_top_10_market_cap()`).
    -   Store data in partitions: `data/btc`, `data/eth`, `data/top10`.

2.  **Backtesting Metrics:**
    -   **Sharpe Ratio**: Risk-adjusted return. (> 1.5 is good).
    -   **Max Drawdown**: Maximum peak-to-valley loss. (Must be < 20% for sanity).
    -   **Calmar Ratio**: Annual Return / Max Drawdown.

## 5. Recommended Next Steps

1.  **Dashboard**: Build a web UI to select strategies and asset lists visually.
2.  **Implementation**:
    -   Implement `PairsTradingStrategy` (Stat Arb).
    -   Implement `VolatilityFilter` for Momontum.
3.  **Data**: Expand Harvester to fetch data for Top 10 Alts automatically.
