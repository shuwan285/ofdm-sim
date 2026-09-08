# -*- coding: utf-8 -*-
"""
M2 数字调制 —— 第一步：QPSK 调制（比特 → 复数符号 → 星座图）

回顾理论：QPSK 用复平面上 4 个点代表 2 个比特（00/01/11/10）。
这个脚本就做一件事：把一串随机比特，映射成 4 个星座点之一。

运行方法：python m2_qpsk_modulation.py
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 1. 生成随机比特：16 个比特 = 8 个 QPSK 符号
num_bits = 16
bits = np.random.randint(0, 2, num_bits)
print("原始比特：", bits)

# 2. QPSK 映射：每 2 比特 → 1 个复数符号
#    映射规则（格雷码，相邻点只差 1 比特）：
#       00 → 1+1j   01 → -1+1j
#       11 → -1-1j  10 → 1-1j
symbols = np.zeros(num_bits // 2, dtype=complex)

for i in range(0, num_bits, 2):
    b0, b1 = bits[i], bits[i + 1]          # 取出这一组的 2 个比特
    if b0 == 0 and b1 == 0:                # 00
        symbols[i // 2] = 1 + 1j
    elif b0 == 0 and b1 == 1:              # 01
        symbols[i // 2] = -1 + 1j
    elif b0 == 1 and b1 == 1:              # 11
        symbols[i // 2] = -1 - 1j
    else:                                  # 10
        symbols[i // 2] = 1 - 1j

print("QPSK 符号：", symbols)

# 3. 画星座图
plt.figure(figsize=(6, 6))
plt.plot(symbols.real, symbols.imag, 'o', markersize=14)
plt.axhline(0, color='k', linewidth=0.5)
plt.axvline(0, color='k', linewidth=0.5)
plt.title("QPSK 星座图（16 比特 → 8 个符号）")
plt.xlabel("实部 I")
plt.ylabel("虚部 Q")
plt.xlim(-1.6, 1.6)
plt.ylim(-1.6, 1.6)
plt.grid(True)
plt.gca().set_aspect('equal')
plt.show()
