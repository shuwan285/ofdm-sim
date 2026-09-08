# -*- coding: utf-8 -*-
"""采样定理（混叠现象）与复数星座图。运行：python m1_sampling_complex.py"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# 中文字体
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 实验1：采样定理（混叠）
f = 50                       # 信号频率 (Hz)，采样定理要求 fs > 2f = 100 Hz

fs_good = 1000               # 采样率足够高
t_good = np.arange(0, 0.2, 1 / fs_good)
x_good = np.cos(2 * np.pi * f * t_good)

fs_bad = 60                  # 采样率过低，违反采样定理
t_bad = np.arange(0, 0.2, 1 / fs_bad)
x_bad = np.cos(2 * np.pi * f * t_bad)

alias_freq = abs(fs_bad - f)   # 混叠后的假频率 = 10 Hz

plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(t_good, x_good, 'o-', markersize=3)
plt.title(f"采样率 {fs_good} Hz：正确还原 50 Hz")
plt.xlabel("时间 (s)")
plt.ylabel("幅度")
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(t_bad, x_bad, 'o-', markersize=6, label="采样点（太少）")
t_cont = np.linspace(0, 0.2, 1000)
plt.plot(t_cont, np.cos(2 * np.pi * alias_freq * t_cont), 'r--',
         label=f"看起来像 {alias_freq} Hz（假的）")
plt.title(f"采样率 {fs_bad} Hz：50 Hz 混叠成 {alias_freq} Hz")
plt.xlabel("时间 (s)")
plt.ylabel("幅度")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# 实验2：复数信号 = 星座图（QPSK 雏形）
symbols = [1 + 1j, -1 + 1j, -1 - 1j, 1 - 1j]
labels = ['00', '01', '11', '10']

plt.figure(figsize=(6, 6))
for s, lab in zip(symbols, labels):
    plt.plot(s.real, s.imag, 'o', markersize=14)
    plt.text(s.real + 0.08, s.imag + 0.08, lab, fontsize=14)

plt.axhline(0, color='k', linewidth=0.5)
plt.axvline(0, color='k', linewidth=0.5)
plt.title("复平面 = 星座图（QPSK 的 4 个点，每个点 2 比特）")
plt.xlabel("实部 I")
plt.ylabel("虚部 Q")
plt.xlim(-1.6, 1.6)
plt.ylim(-1.6, 1.6)
plt.grid(True)
plt.gca().set_aspect('equal')
plt.show()
