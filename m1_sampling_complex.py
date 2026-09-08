# -*- coding: utf-8 -*-
"""
M1 信号基础 —— 实验二：采样定理 + 复数信号

两个知识点，是后面 OFDM 和 QPSK/QAM 调制的地基。
运行方法：在终端执行  python m1_sampling_complex.py
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# 解决中文乱码
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# ================= 实验1：采样定理（混叠现象） =================
f = 50          # 信号频率 50 Hz（余弦波）
# 采样定理要求 fs > 2*f = 100 Hz

# 情况A：采样率足够高（1000 Hz，远大于 100），信号被正确采样
fs_good = 1000
t_good = np.arange(0, 0.2, 1 / fs_good)
x_good = np.cos(2 * np.pi * f * t_good)

# 情况B：采样率太低（60 Hz < 100 Hz，违反采样定理）
fs_bad = 60
t_bad = np.arange(0, 0.2, 1 / fs_bad)
x_bad = np.cos(2 * np.pi * f * t_bad)

alias_freq = abs(fs_bad - f)    # 混叠后的"假"频率 = |60 - 50| = 10 Hz

plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(t_good, x_good, 'o-', markersize=3)
plt.title(f"采样率 {fs_good} Hz：正确还原 50 Hz 余弦波")
plt.xlabel("时间 (s)")
plt.ylabel("幅度")
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(t_bad, x_bad, 'o-', markersize=6, label="采样点（太少！）")
# 叠加一条 10 Hz 的余弦，看稀疏的采样点是不是"恰好"落在这条低频线上
t_cont = np.linspace(0, 0.2, 1000)
plt.plot(t_cont, np.cos(2 * np.pi * alias_freq * t_cont),
         'r--', label=f"看起来像 {alias_freq} Hz（假的！）")
plt.title(f"采样率 {fs_bad} Hz：50 Hz 被混叠成 {alias_freq} Hz")
plt.xlabel("时间 (s)")
plt.ylabel("幅度")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# ================= 实验2：复数信号 = 星座图（QPSK 雏形） =================
# 复平面上的 4 个点，就是 QPSK 的 4 个符号，每个点代表 2 个比特
symbols = [1 + 1j, -1 + 1j, -1 - 1j, 1 - 1j]
labels = ['00', '01', '11', '10']

plt.figure(figsize=(6, 6))
for s, lab in zip(symbols, labels):
    plt.plot(s.real, s.imag, 'o', markersize=14)
    plt.text(s.real + 0.08, s.imag + 0.08, lab, fontsize=14)

plt.axhline(0, color='k', linewidth=0.5)   # 横轴
plt.axvline(0, color='k', linewidth=0.5)   # 纵轴
plt.title("复平面 = 星座图（QPSK 的 4 个点，每个点=2 比特）")
plt.xlabel("实部 I")
plt.ylabel("虚部 Q")
plt.xlim(-1.6, 1.6)
plt.ylim(-1.6, 1.6)
plt.grid(True)
plt.gca().set_aspect('equal')   # 让横纵坐标等比例，点才对称
plt.show()
