# -*- coding: utf-8 -*-
"""QPSK 解调：复数符号 -> 比特，验证收发一致。运行：python m2_qpsk_demodulation.py"""
import numpy as np

num_bits = 16
bits = np.random.randint(0, 2, num_bits)

# 调制
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

# 解调：星座点在四个象限，只看实部虚部的正负
recovered_bits = np.zeros(num_bits, dtype=int)
for i, s in enumerate(symbols):
    recovered_bits[2 * i]     = 0 if s.imag > 0 else 1
    recovered_bits[2 * i + 1] = 0 if s.real > 0 else 1

print("原始比特：", bits)
print("恢复比特：", recovered_bits)
print("完全一致？", np.array_equal(bits, recovered_bits))
