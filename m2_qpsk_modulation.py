# -*- coding: utf-8 -*-
"""QPSK 调制：比特 -> 复数符号，画星座图。运行：python m2_qpsk_modulation.py"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# 中文字体
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

num_bits = 16
bits = np.random.randint(0, 2, num_bits)
print("原始比特：", bits)

# 格雷码 QPSK 映射：00->1+1j, 01->-1+1j, 11->-1-1j, 10->1-1j
symbols = np.zeros(num_bits // 2, dtype=complex)
for i in range(0, num_bits, 2):
    b0, b1 = bits[i], bits[i + 1]
    if b0 == 0 and b1 == 0:
        symbols[i // 2] = 1 + 1j
    elif b0 == 0 and b1 == 1:
        symbols[i // 2] = -1 + 1j
    elif b0 == 1 and b1 == 1:
        symbols[i // 2] = -1 - 1j
    else:
        symbols[i // 2] = 1 - 1j

print("QPSK 符号：", symbols)

plt.figure(figsize=(6, 6))
plt.plot(symbols.real, symbols.imag, 'o', markersize=14)
plt.axhline(0, color='k', linewidth=0.5)
plt.axvline(0, color='k', linewidth=0.5)
plt.title("QPSK 星座图")
plt.xlabel("实部 I")
plt.ylabel("虚部 Q")
plt.xlim(-1.6, 1.6)
plt.ylim(-1.6, 1.6)
plt.grid(True)
plt.gca().set_aspect('equal')
plt.show()
