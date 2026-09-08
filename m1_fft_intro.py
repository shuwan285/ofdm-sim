# -*- coding: utf-8 -*-
"""
M1 信号基础 —— 实验一：正弦波的时域与频域

OFDM 的根基是 FFT（快速傅里叶变换），它负责在"时域"和"频域"之间来回切换。
这个实验帮你建立最重要的直觉：一个正弦波在频域里就是一根"尖峰"。

运行方法：在终端执行  python m1_fft_intro.py
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# 解决中文乱码：指定中文字体 + 正常显示负号
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 1. 采样参数
fs = 1000                      # 采样率 1000 Hz（每秒采 1000 个点）
T = 1.0                        # 观察时长 1 秒
t = np.arange(0, T, 1 / fs)    # 时间轴：0, 1/fs, 2/fs, ... 共 1000 个点

# 2. 生成信号：两个不同频率的正弦波叠加（50 Hz 幅度1 + 150 Hz 幅度0.5）
x = np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 150 * t)

# 3. 计算 FFT，得到"频域信号"
N = len(x)                          # 采样点数
X = np.fft.fft(x)                   # 复数频谱（每个频点有实部和虚部）
freq = np.fft.fftfreq(N, 1 / fs)    # 对应的频率轴（含负频率）

# 4. 画图：左边时域，右边频域
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(t[:100], x[:100])           # 只看前 100 个点，否则线条太密
plt.title("时域：两个正弦波叠加（左图，x轴是时间）")
plt.xlabel("时间 (s)")
plt.ylabel("幅度")
plt.grid(True)

plt.subplot(1, 2, 2)
# 只看正频率部分；乘 2/N 是为了把幅度还原成真实振幅
mag = np.abs(X[:N // 2]) * 2 / N
plt.plot(freq[:N // 2], mag, 'o-', markersize=4)  # 加圆点，尖峰一眼可见
plt.xlim(0, 250)   # 放大 0~250 Hz，方便看清尖峰位置
plt.title("频域：幅度谱（右图，x轴是频率）")
plt.xlabel("频率 (Hz) —— 横轴数字就是频率")
plt.ylabel("幅度")
plt.grid(True)

plt.tight_layout()
plt.show()
