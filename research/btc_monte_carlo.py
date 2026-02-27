import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import ScalarFormatter
# ==========================================
# 🔧 解决中文显示和负号报错的补丁
# ==========================================
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']  # 优先使用微软雅黑，备用黑体
plt.rcParams['axes.unicode_minus'] = False  # 确保负号（-）能正常显示

# ==========================================
# 📊 第一步：量化参数配置 (基准：你跑出的实盘数据)
# ==========================================
np.random.seed(42) # 锁定随机种子，保证每次生成的图表一致，方便排版
ticker = "BTCUSDT"
days_to_simulate = 1095  # 3年
num_simulations = 10000 # 1万次
last_price = 67220.0     # 当前参考价格

# 模型核心参数 (均值与波动率)
mu_base = 0.000909
sigma_base = 0.024681

# 黑天鹅 parameters (Merton Jump-Diffusion)
lambda_jump = 5.0 / 365.0   # 每年5次
mu_jump = -0.05             # 平均跌幅
sigma_jump = 0.15           # 跳跃幅度标准差

print(f"📡 正在生成 10,000 次双轨压力测试图表 (风控视角)...")

# ==========================================
# 🧬 第二步：核心数学模型运算
# ==========================================

# 1. GBM (几何布朗运动)
Z_gbm = np.random.normal(0, 1, (days_to_simulate, num_simulations))
daily_returns_gbm = np.exp((mu_base - (sigma_base ** 2) / 2) + sigma_base * Z_gbm)
price_paths_gbm = np.zeros_like(daily_returns_gbm)
price_paths_gbm[0] = last_price
for t in range(1, days_to_simulate):
    price_paths_gbm[t] = price_paths_gbm[t-1] * daily_returns_gbm[t]

# 2. MJD (Merton 跳跃扩散模型)
Z_mjd = np.random.normal(0, 1, (days_to_simulate, num_simulations))
jumps = np.random.poisson(lambda_jump, (days_to_simulate, num_simulations))
jump_sizes = np.random.normal(mu_jump, sigma_jump, (days_to_simulate, num_simulations))
total_jump_impact = jumps * jump_sizes
daily_returns_mjd = np.exp((mu_base - (sigma_base ** 2) / 2) + sigma_base * Z_mjd + total_jump_impact)
price_paths_mjd = np.zeros_like(daily_returns_mjd)
price_paths_mjd[0] = last_price
for t in range(1, days_to_simulate):
    price_paths_mjd[t] = price_paths_mjd[t-1] * daily_returns_mjd[t]

# 计算三年后的概率分布
final_gbm = price_paths_gbm[-1]
perc_gbm = np.percentile(final_gbm, [5, 50, 95])

final_mjd = price_paths_mjd[-1]
perc_mjd = np.percentile(final_mjd, [5, 50, 95])

# ==========================================
# 🎨 第三步：顶级“暗黑科技风”Matplotlib 绘图
# ==========================================

# 设置暗黑背景
plt.style.use('dark_background')
fig = plt.figure(figsize=(20, 10), dpi=100) # 高分辨率用于 X 发布
gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])

# 定义荧光配色方案
color_paths = '#00ffff' # 荧光青 (冷酷的轨迹)
color_95th = '#00ff00'  # 荧光绿 (乐观)
color_50th = '#ff3333'  # 荧光红 (中枢)
color_5th = '#ffcc00'   # 荧光橙 (悲观防线)
color_text = '#ffffff'

def plot_paths(ax, paths, perc, title):
    # 绘制前 200 条路径作为荧光展示
    ax.plot(paths[:, :200], color=color_paths, alpha=0.015, linewidth=1)
    
    # 绘制分位数参考线
    ax.axhline(perc[2], color=color_95th, linestyle='--', linewidth=2.5, alpha=0.9)
    ax.axhline(perc[1], color=color_50th, linestyle='-', linewidth=3, alpha=1)
    ax.axhline(perc[0], color=color_5th, linestyle='--', linewidth=2.5, alpha=0.9)
    
    # 荧光文本标注
    # 标注 current price
    ax.text(days_to_simulate * 0.05, last_price * 1.1, f"Start: ${last_price:,.0f}", color=color_text, fontsize=14, fontweight='bold', bbox=dict(facecolor='black', alpha=0.5))
    
    # 标注 3年后 Percentiles
    right_x = days_to_simulate * 0.98
    ax.text(right_x, perc[2] * 1.1, f"95th: ${perc[2]:,.0f}", color=color_95th, fontsize=16, fontweight='bold', ha='right')
    ax.text(right_x, perc[1] * 1.1, f"50th: ${perc[1]:,.0f}", color=color_50th, fontsize=18, fontweight='bold', ha='right', bbox=dict(facecolor='black', alpha=0.6))
    ax.text(right_x, perc[0] * 0.7, f"5th: ${perc[0]:,.0f}", color=color_5th, fontsize=16, fontweight='bold', ha='right')
    
    # 坐标轴格式化
    ax.set_yscale('log') # 必须使用对数轴
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.grid(True, which='both', linestyle='-', color='#333333', alpha=0.5)
    ax.set_title(title, fontsize=20, fontweight='bold', pad=20, color=color_text)
    ax.set_xlabel("Days into Future", fontsize=14, color=color_text)
    ax.tick_params(axis='both', which='major', labelsize=12, labelcolor=color_text)
    
    # 去除边框
    for spine in ax.spines.values():
        spine.set_visible(False)

# 绘制 Subplot 1: 常规 GBM
ax1 = plt.subplot(gs[0])
plot_paths(ax1, price_paths_gbm, perc_gbm, f"{ticker} GBM: 温和周期模型")

# 绘制 Subplot 2: 黑天鹅 Jump-Diffusion
ax2 = plt.subplot(gs[1])
plot_paths(ax2, price_paths_mjd, perc_mjd, f"{ticker} MJD: 黑天鹅压力测试")

plt.tight_layout()

# 在 X 上发推建议使用 .png 格式保持清晰度
save_path = "BTC_Monte_Carlo_X_HighExposure.png"
plt.savefig(save_path, facecolor='#0a0a0a', edgecolor='none')
print(f"✅ 高曝光暗黑科技风配图已生成，保存为: {save_path}")
plt.show()