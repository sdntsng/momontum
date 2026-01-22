# Momontum Dashboard Design Spec

## Executive Summary
This document outlines the architecture for the Momontum Trading Dashboard. The goal is to move from CLI-based interaction to a modern, interactive web interface for managing data, developing strategies, and visualizing backtest results across multiple asset classes.

## Tech Stack

### Frontend (The Logic)
-   **Framework**: **Vite + React**. (Chosen for speed and "Web App" complexity requirements).
-   **Language**: TypeScript.
-   **Styling**: **Vanilla CSS** / CSS Modules (Strict adherence to user preference).
-   **Visualization**: `Recharts` for interactive PnL curves and price charts.
-   **State Management**: React Context / Hooks.

### Backend (The Brain)
-   **Server**: **FastAPI** (Python).
-   **Role**: Exposes the existing Backtesting Engine and Data Lake to the frontend.
-   **Communication**: REST API.

---

## Features

### 1. Strategy Workbench
-   **List View**: See all strategies defined in `strategies/`.
-   **Config Editor**: Edit parameters (e.g., `momentum_window`, `z_score_threshold`) via a form UI.
-   **Code Viewer**: Read-only view of strategy logic.

### 2. Multi-Asset Lab
-   **Asset Selector**: Checkbox group to select test universe:
    -   [ ] BTC Only
    -   [ ] ETH Only
    -   [ ] Top 10 Alts
    -   [ ] "Shitcoin" Basket (High volatility, low cap)
-   **Date Range**: Date picker for backtest period.

### 3. Backtest Execution & Visualization
-   **Run Button**: Triggers async backtest on backend.
-   **Interactive Charts**:
    -   **PnL Curve**: Cumulative return over time.
    -   **Drawdown Chart**: Visualizing risk.
    -   **Price Overlay**: Entry/Exit markers on price chart.
-   **Comparison Table**: The "Leaderboard" showing Sharpe Ratio, Wins, and Total Return for selected strategies.

---

## Directory Structure

```
momontum/
├── dashboard/           # NEW: Frontend
│   ├── src/
│   ├── public/
│   ├── index.html
│   └── package.json
├── api/                 # NEW: Backend
│   ├── main.py          # FastAPI App
│   ├── routes/
│   └── service.py       # Bridges API to Backtester
├── strategies/          # Existing
├── backtesting/         # Existing
└── data_lake/           # Existing
```

## Implementation Phases

1.  **Backend API**: Wrap `bulk_runner` in FastAPI endpoints.
2.  **Frontend Setup**: Initialize Vite project with custom aesthetics.
3.  **Integration**: Connect Run button to Backend.
