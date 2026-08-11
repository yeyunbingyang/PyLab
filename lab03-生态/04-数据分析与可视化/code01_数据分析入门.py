# 数据分析与可视化 — NumPy + Pandas + Matplotlib 入门

# pip install numpy pandas matplotlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# === NumPy ===
arr = np.array([1, 2, 3, 4, 5])
print(f'均值: {arr.mean()}, 标准差: {arr.std()}')

matrix = np.random.randn(3, 3)
print(f'矩阵:\n{matrix}')

# === Pandas ===
df = pd.DataFrame({
    '姓名': ['Alice', 'Bob', 'Charlie'],
    '年龄': [25, 30, 28],
    '薪资': [15000, 12000, 18000]
})
print(f'\nDataFrame:\n{df}')
print(f'\n描述统计:\n{df.describe()}')

# === Matplotlib ===
plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文显示
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]
plt.plot(x, y, marker='o')
plt.title('简单折线图')
plt.xlabel('X 轴')
plt.ylabel('Y 轴')
plt.savefig('plot.png')
print('\n图表已保存为 plot.png')
