# -*- coding: utf-8 -*-
"""
M2 数字调制 —— 第二步：QPSK 解调（复数符号 → 比特）+ 收发一致性验证

回顾：调制是"比特 → 符号"，解调就是反过来"符号 → 比特"。
漂亮的地方：星座点就在四个象限，所以解调 = 看实部、虚部的正负号！

运行方法：python m2_qpsk_demodulation.py
"""
import numpy as np

# 1. 生成随机比特
num_bits = 16
bits = np.random.randint(0, 2, num_bits)

# 2. 调制：比特 → 符号（和上一步一样）
symbols = np.zeros(num_bits // 2, dtype=complex)
for i in range(0, num_bits, 2):
    b0, b1 = bits[i], bits[i + 1]
    if b0 == 0 and b1 == 0:      symbols[i // 2] = 1 + 1j
    elif b0 == 0 and b1 == 1:    symbols[i // 2] = -1 + 1j
    elif b0 == 1 and b1 == 1:    symbols[i // 2] = -1 - 1j
    else:                        symbols[i // 2] = 1 - 1j

# 3. 解调：符号 → 比特（关键！就看实部、虚部的正负）
recovered_bits = np.zeros(num_bits, dtype=int)
for i, s in enumerate(symbols):
    b0 = 0 if s.imag > 0 else 1   # 虚部 >0 → 第1个比特 = 0
    b1 = 0 if s.real > 0 else 1   # 实部 >0 → 第2个比特 = 0
    recovered_bits[2 * i] = b0
    recovered_bits[2 * i + 1] = b1

# 4. 验证：恢复的比特是否和原始比特完全一致（没有噪声时，必须一致）
print("原始比特：", bits)
print("恢复比特：", recovered_bits)
print("完全一致？", np.array_equal(bits, recovered_bits))
