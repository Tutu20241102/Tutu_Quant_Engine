import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt

def get_binance_daily_close(symbol="BTCUSDT", limit=1000):
    """
    通过币安官方公开 API 获取历史日线收盘价
    """
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "1d",
        "limit": limit
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status() # 如果网络报错则抛出异常
    data = response.json()
    
    # 币安 K 线数据结构解析
    # [Open time, Open, High, Low, Close, Volume, Close time, ...]
    df = pd.DataFrame(data, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
    ])
    
    # 转换时间戳和数据类型
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close'] = df['close'].astype(float)
    df.set_index('open_time', inplace=True)
    
    return df['close']

def run_btc_monte_carlo(ticker="BTCUSDT", days_to_simulate=1095, num_simulations=10000):
    print(f"📡 正在通过 Binance API 拉取 {ticker} 最近 1000 天的数据...")
    
    try:
        # 1. 获取币安数据
        data = get_binance_daily_close(symbol=ticker)
        
        # 2. 计算日对数收益率
        returns = np.log(1 + data.pct_change()).dropna()
        mu = returns.mean()
        sigma = returns.std()
        last_price = data.iloc[-1]
        
        print(f"✅ 数据拉取成功！当前价格: ${last_price:,.2f}")
        print(f"📊 历史日均漂移率 (mu): {mu:.6f}, 日波动率 (sigma): {sigma:.6f}")
        print(f"🚀 开始进行 {num_simulations} 次蒙特卡洛随机游走模拟...\n")
        
    except Exception as e:
        print(f"❌ 数据获取失败: {e}")
        return

    # 3. 核心数学模型离散化运算 (几何布朗运动)
    Z = np.random.normal(0, 1, (days_to_simulate, num_simulations))
    daily_returns = np.exp((mu - (sigma ** 2) / 2) + sigma * Z)
    
    # 4. 生成价格路径矩阵
    price_paths = np.zeros_like(daily_returns)
    price_paths[0] = last_price
    
    # 累乘计算未来走势
    for t in range(1, days_to_simulate):
        price_paths[t] = price_paths[t-1] * daily_returns[t]

    # 5. 计算三年后的概率分布 (分位数)
    final_prices = price_paths[-1]
    percentile_5 = np.percentile(final_prices, 5)
    percentile_50 = np.percentile(final_prices, 50)  # 中位数
    percentile_95 = np.percentile(final_prices, 95)
    
    print("=== 未来3年 (1095天) 后的价格概率分布 ===")
    print(f"📉 悲观预期 (5% 概率低于此价格): ${percentile_5:,.2f}")
    print(f"⚖️ 中性预期 (中位数, 50/50胜率): ${percentile_50:,.2f}")
    print(f"📈 乐观预期 (5% 概率高于此价格): ${percentile_95:,.2f}")

    # 6. 可视化绘制
    plt.figure(figsize=(14, 7))
    plt.plot(price_paths[:, :200], color='blue', alpha=0.03) # 画前200条轨迹防卡顿
    
    plt.axhline(percentile_95, color='green', linestyle='--', linewidth=2, label=f'95th Percentile: ${percentile_95:,.0f}')
    plt.axhline(percentile_50, color='red', linestyle='-', linewidth=2, label=f'50th Percentile: ${percentile_50:,.0f}')
    plt.axhline(percentile_5, color='orange', linestyle='--', linewidth=2, label=f'5th Percentile: ${percentile_5:,.0f}')
    
    plt.title(f"Binance Data: {ticker} Monte Carlo Simulation ({num_simulations} paths, 3 Years)", fontsize=14)
    plt.xlabel("Days into the Future", fontsize=12)
    plt.ylabel("Price (USD) - Log Scale", fontsize=12)
    
    # 强制使用对数坐标轴
    plt.yscale('log') 
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_btc_monte_carlo()