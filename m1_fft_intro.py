# -*- coding: utf-8 -*-
"""正弦波的时域与频域：演示 FFT 把时域信号分解成频率分量。运行：python m1_fft_intro.py"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# 中文字体
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

fs = 1000                    # 采样率 (Hz)
T = 1.0                      # 观察时长 (s)
t = np.arange(0, T, 1 / fs)

# 两个正弦波叠加：50 Hz + 150 Hz
x = np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 150 * t)

N = len(x)
X = np.fft.fft(x)
freq = np.fft.fftfreq(N, 1 / fs)

plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(t[:100], x[:100])
plt.title("时域：两个正弦波叠加")
plt.xlabel("时间 (s)")
plt.ylabel("幅度")
plt.grid(True)

plt.subplot(1, 2, 2)
mag = np.abs(X[:N // 2]) * 2 / N   # 归一化，使峰值等于真实振幅
plt.plot(freq[:N // 2], mag, 'o-', markersize=4)
plt.xlim(0, 250)
plt.title("频域：幅度谱")
plt.xlabel("频率 (Hz)")
plt.ylabel("幅度")
plt.grid(True)

plt.tight_layout()
plt.show()
