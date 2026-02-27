#跳跃扩散模型（Jump-Diffusion）
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt

def get_binance_daily_close(symbol="BTCUSDT", limit=1000):
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": "1d", "limit": limit}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
    ])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close'] = df['close'].astype(float)
    df.set_index('open_time', inplace=True)
    return df['close']

def run_merton_jump_diffusion(ticker="BTCUSDT", days_to_simulate=1095, num_simulations=10000):
    print(f"📡 获取 {ticker} 历史数据并校准参数...")
    data = get_binance_daily_close(symbol=ticker)
    returns = np.log(1 + data.pct_change()).dropna()
    
    # 基础扩散参数
    mu = returns.mean()
    sigma = returns.std()
    last_price = data.iloc[-1]
    
    # ---------------- 引入跳跃扩散参数 (Merton Jump) ----------------
    # 假设每年发生 5 次极端行情，换算成日发生率 lambda
    lambda_jump = 5.0 / 365.0 
    # 假设跳跃发生时，平均带来 -5% 的跌幅 (向下跳跃为主)
    mu_jump = -0.05 
    # 跳跃幅度的标准差 (极度剧烈，甚至单日20%)
    sigma_jump = 0.15 
    # -------------------------------------------------------------

    print(f"✅ 当前价格: ${last_price:,.2f}")
    print(f"⚠️ 正在注入黑天鹅参数进行 {num_simulations} 次压力测试...")

    # 1. 生成标准的几何布朗运动增量
    Z = np.random.normal(0, 1, (days_to_simulate, num_simulations))
    
    # 2. 生成泊松分布的跳跃次数 (每天发生跳跃的次数，绝大多数为 0，少数为 1)
    jumps = np.random.poisson(lambda_jump, (days_to_simulate, num_simulations))
    
    # 3. 生成跳跃的幅度 (正态分布)
    jump_sizes = np.random.normal(mu_jump, sigma_jump, (days_to_simulate, num_simulations))
    
    # 4. 计算总收益乘数 (连续波动 + 突发跳跃)
    total_jump_impact = jumps * jump_sizes
    daily_returns = np.exp((mu - (sigma ** 2) / 2) + sigma * Z + total_jump_impact)
    
    # 5. 计算价格路径
    price_paths = np.zeros_like(daily_returns)
    price_paths[0] = last_price
    for t in range(1, days_to_simulate):
        price_paths[t] = price_paths[t-1] * daily_returns[t]

    final_prices = price_paths[-1]
    percentile_5 = np.percentile(final_prices, 5)
    percentile_50 = np.percentile(final_prices, 50)
    percentile_95 = np.percentile(final_prices, 95)
    
    print("\n=== 考虑黑天鹅后的压力测试概率分布 ===")
    print(f"📉 极端悲观 (5% 破产/清算防线): ${percentile_5:,.2f}")
    print(f"⚖️ 中性预期 (扛过震荡的合理估值): ${percentile_50:,.2f}")
    print(f"📈 极端乐观 (泡沫期顶点估值): ${percentile_95:,.2f}")

    plt.figure(figsize=(14, 7))
    plt.plot(price_paths[:, :200], color='purple', alpha=0.03)
    
    plt.axhline(percentile_95, color='green', linestyle='--', linewidth=2, label=f'95th: ${percentile_95:,.0f}')
    plt.axhline(percentile_50, color='red', linestyle='-', linewidth=2, label=f'50th: ${percentile_50:,.0f}')
    plt.axhline(percentile_5, color='orange', linestyle='--', linewidth=2, label=f'5th: ${percentile_5:,.0f}')
    
    plt.title(f"{ticker} Merton Jump-Diffusion Simulation (With Black Swans)", fontsize=14)
    plt.xlabel("Days", fontsize=12)
    plt.ylabel("Price (USD) - Log Scale", fontsize=12)
    plt.yscale('log') 
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_merton_jump_diffusion()