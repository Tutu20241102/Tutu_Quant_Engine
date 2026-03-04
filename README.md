# Tutu_Quant_Engine 🚀

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Quant](https://img.shields.io/badge/Quant-Risk%20Management-orange)
![License](https://img.shields.io/badge/License-MIT-green)

A professional quantitative trading engine and risk management framework designed for volatile crypto assets. This project focuses on tail-risk pricing, anti-fragile strategy backtesting, and systematic execution logic.

---

## 📌 Abstract
This repository contains a quantitative stress-test suite for Bitcoin (BTC). We utilize **10,000+ Monte Carlo paths** and **Merton Jump-Diffusion (MJD)** models to evaluate the mathematical floor of crypto assets during systemic "Black Swan" events (e.g., macro liquidity crunches or liquidation cascades).

## 🧮 Mathematical Foundations

### 1. Geometric Brownian Motion (GBM)
Standard model for continuous price action:
$$dS_t = \mu S_t dt + \sigma S_t dW_t$$

### 2. Merton Jump-Diffusion (MJD)
Injected with Poisson jump processes to simulate structural fragility:
$$dS_t = \mu S_t dt + \sigma S_t dW_t + S_t dJ_t$$
* **Jump Parameters:** $\lambda=5$ (shocks/year), $\mu_{jump}=-5\%$ (crash mean), $\sigma_{jump}=15\%$ (volatility).

---

## 📉 Tail-Risk Pricing Results (10,000 Monte Carlo Paths)

Before configuring any trading algorithms, we must mathematically locate the absolute floor of BTC during a systemic crash. We fed 1,000 days of historical volatility into 10,000 simulated 3-year paths, comparing the two models:

### Model 1: The Baseline (Geometric Brownian Motion)
Assuming a continuous and smooth market distribution:
* **Pessimistic Floor (Bottom 5% probability):** $34,729
* **Value Fair-Pricing (50% Median):** $128,995
* **Extreme Bubble Top (Top 5% probability):** $486,082
> **Conclusion:** Under normal conditions without systemic collapses, $34k acts as the iron-clad density floor.

### Model 2: The Stress Test (Merton Jump-Diffusion)
After absorbing extreme "volatility drag" (e.g., liquidity crunches, FTX-level liquidation cascades), the true probability distribution is severely reshaped:
* **Liquidation Dead Zone (Bottom 5% probability):** $11,121
* **Post-Disaster Median (50% Median):** $60,872
* **Extreme Mania Top (Top 5% probability):** $326,050
> **Conclusion:** Even under the most brutal volatility drag and repeated liquidation cascades, the mathematical floor sits robustly at $11k. The probability of BTC reaching an absorbing state of absolute zero is structurally invalid.

**The Quant Consensus:** The math exposes a massive fragility gap. A trading system anchored to the standard GBM floor ($34k) will be completely destroyed during a tail event. Therefore, our **Anti-fragile Grid** must be mathematically anchored to the MJD floor (**$11,000**).

---

## 📁 Research & Backtest Modules

The `research/` directory houses the core engines used to validate our trading logic:

* **`gbm_monte_carlo.py`**: Baseline market pricing and percentile distribution.
* **`mjd_stress_test.py`**: Extreme tail-risk pricing under black swan scenarios.
* **`btc_grid_backtest.py`**: A ruthless backtesting environment comparing standard grid trading vs. **Anti-fragile Wide-Grid** strategies.

### 📊 Stress-Test Visualization (The Proof)
The following chart demonstrates the survival rate and equity curve of our **Anti-fragile Grid ($11k - $100k)** during a 3-year simulated black swan event. Notice how the anti-fragile strategy (Green) outperforms by capturing bottom liquidity during crashes.

![BTC Grid Backtest Result](research/btc_grid_backtest_result.png)

---

## ⚙️ Installation & Usage

Ensure you have the required data science stack installed:

```bash
pip install numpy pandas matplotlib requests