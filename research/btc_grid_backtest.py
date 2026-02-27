#btc_grid_backtest.py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ==========================================
# 🔧 核心参数与数学模型配置
# ==========================================
plt.style.use('dark_background') # 切换为专业的量化暗黑风格

def generate_btc_jump_diffusion(S0, mu, sigma, lambda_j, mu_j, sigma_j, days):
    """生成一条包含 BTC 连环爆仓插针的黑天鹅价格路径"""
    np.random.seed(42) # 固定随机种子以复现推演
    dt = 1.0 / 365.0
    path = np.zeros(days)
    path[0] = S0
    
    for t in range(1, days):
        Z = np.random.normal(0, 1)
        # 泊松过程：测算今天是否发生宏观黑天鹅或连环清算
        N = np.random.poisson(lambda_j * dt) 
        J = np.sum(np.random.normal(mu_j, sigma_j, N)) if N > 0 else 0
        
        drift = (mu - 0.5 * sigma**2) * dt
        diffusion = sigma * np.sqrt(dt) * Z
        path[t] = path[t-1] * np.exp(drift + diffusion + J)
        
    return path

def backtest_grid(price_path, lower_bound, upper_bound, grid_count, initial_capital=100000):
    """核心网格交易回测引擎"""
    grids = np.linspace(lower_bound, upper_bound, grid_count)
    grid_diff = grids[1] - grids[0]
    per_grid_capital = initial_capital / grid_count
    
    cash = initial_capital
    coin_qty = 0.0
    start_price = price_path[0]
    
    # 初始建仓逻辑
    for p in grids:
        if p < start_price:
            cash -= per_grid_capital
            coin_qty += per_grid_capital / p
            
    equity_curve = []
    current_grid_idx = np.searchsorted(grids, start_price) - 1
    
    for price in price_path:
        new_grid_idx = np.searchsorted(grids, price) - 1
        
        # 向上穿越（卖出平多，赚取利润）
        while current_grid_idx < new_grid_idx and current_grid_idx < grid_count - 1:
            current_grid_idx += 1
            sell_price = grids[current_grid_idx]
            if coin_qty >= per_grid_capital / sell_price:
                coin_qty -= per_grid_capital / sell_price
                cash += per_grid_capital + (per_grid_capital * grid_diff / sell_price)
                
        # 向下穿越（买入开多，分批抄底）
        while current_grid_idx > new_grid_idx and current_grid_idx >= 0:
            buy_price = grids[current_grid_idx]
            if cash >= per_grid_capital:
                cash -= per_grid_capital
                coin_qty += per_grid_capital / buy_price
            current_grid_idx -= 1
            
        equity = cash + coin_qty * price
        equity_curve.append(equity)
        
    return np.array(equity_curve)

# ==========================================
# 📊 运行回测与策略对抗
# ==========================================
days = 1095  # 测试未来 3 年 (与之前的推文模型保持一致)
S0 = 67220.0 # BTC 起始价格

# MJD 极端环境参数 (年化)
mu = 0.33             # 常规震荡上涨的漂移率
sigma = 0.47          # 常规年化波动率
lambda_j = 5.0        # 每年 5 次无征兆的闪崩
mu_j = -0.05          # 每次闪崩平均插针 -5%
sigma_j = 0.15        # 极端波动的方差

print("📡 正在生成 BTC 极限压力测试路径 (包含连环清算)...")
btc_path = generate_btc_jump_diffusion(S0, mu, sigma, lambda_j, mu_j, sigma_j, days)

print("⚔️ 正在运行三大策略对抗回测 (初始资金: $100,000)...")
# 策略A：常规价值区间网格 (34k 铁底 - 90k)
equity_normal = backtest_grid(btc_path, lower_bound=34000, upper_bound=90000, grid_count=50)

# 策略B：抗脆弱极端死区网格 (11k 灾难底 - 100k)
equity_antifragile = backtest_grid(btc_path, lower_bound=11000, upper_bound=100000, grid_count=50)

# 纯持有现货基准 (Hold)
equity_hold = (100000 / S0) * btc_path

# ==========================================
# 🎨 极客风可视化渲染
# ==========================================
fig = plt.figure(figsize=(16, 10), dpi=100)
gs = gridspec.GridSpec(2, 1, height_ratios=[1.2, 1])

# 上半部分：价格路径与防御阵地
ax1 = plt.subplot(gs[0])
ax1.plot(btc_path, color='#00ffff', alpha=0.8, label='BTC Simulated Price (MJD Black Swan)')
ax1.axhline(34000, color='#ff3333', linestyle='--', linewidth=2, label='Normal Grid Floor ($34k)')
ax1.axhline(11000, color='#00ff00', linestyle='--', linewidth=2, label='Anti-fragile Grid Floor ($11k)')
ax1.set_title("BTC 3-Year Stress Test: Price Path vs Grid Zones", fontsize=16, fontweight='bold', color='white', pad=15)
ax1.set_ylabel("BTC Price (USD)", fontsize=12)
ax1.legend(loc='upper right', facecolor='black', edgecolor='white')
ax1.grid(True, linestyle=':', color='#444444')

# 下半部分：资金净值生死战
ax2 = plt.subplot(gs[1], sharex=ax1)
ax2.plot(equity_hold, color='gray', linestyle=':', linewidth=2, label=f'Hold Spot: ${equity_hold[-1]:,.0f}')
ax2.plot(equity_normal, color='#ff3333', alpha=0.9, linewidth=2, label=f'Normal Grid (34k-90k): ${equity_normal[-1]:,.0f}')
ax2.plot(equity_antifragile, color='#00ff00', alpha=0.9, linewidth=2, label=f'Anti-fragile Grid (11k-100k): ${equity_antifragile[-1]:,.0f}')
ax2.set_title("Portfolio Equity Curve (Start: $100,000)", fontsize=16, fontweight='bold', color='white', pad=15)
ax2.set_ylabel("Total Equity (USD)", fontsize=12)
ax2.set_xlabel("Days Simulated", fontsize=12)
ax2.legend(loc='upper left', facecolor='black', edgecolor='white')
ax2.grid(True, linestyle=':', color='#444444')

plt.tight_layout()
plt.show()

# 核心风控数据计算与打印
def print_stats(name, equity):
    max_drawdown = np.min(equity / np.maximum.accumulate(equity)) - 1
    return_rate = (equity[-1] / 100000) - 1
    print(f"[{name}] 最终收益率: {return_rate*100:>6.2f}% | 极限最大回撤: {max_drawdown*100:>6.2f}%")

print("\n=== BTC 黑天鹅 3 年极限回测结果 (本金 $100,000) ===")
print_stats("纯持有现货 (Hold)", equity_hold)
print_stats("常规网格 (34k铁底)", equity_normal)
print_stats("抗脆弱网格 (11k灾难底)", equity_antifragile)