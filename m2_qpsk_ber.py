# -*- coding: utf-8 -*-
"""QPSK 误码率（BER）曲线：加噪声 -> 解调 -> 统计误码。运行：python m2_qpsk_ber.py"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# 中文字体
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

def qpsk_mod(bits):
    symbols = np.zeros(len(bits) // 2, dtype=complex)
    for i in range(0, len(bits), 2):
        b0, b1 = bits[i], bits[i + 1]
        if b0 == 0 and b1 == 0:
            symbols[i // 2] = 1 + 1j
        elif b0 == 0 and b1 == 1:
            symbols[i // 2] = -1 + 1j
        elif b0 == 1 and b1 == 1:
            symbols[i // 2] = -1 - 1j
        else:
            symbols[i // 2] = 1 - 1j
    return symbols

def qpsk_demod(symbols):
    bits = np.zeros(2 * len(symbols), dtype=int)
    for i, s in enumerate(symbols):
        bits[2 * i]     = 0 if s.imag > 0 else 1
        bits[2 * i + 1] = 0 if s.real > 0 else 1
    return bits

num_bits = 100000
bits = np.random.randint(0, 2, num_bits)
symbols = qpsk_mod(bits)

EbN0_db = np.arange(0, 11, 1)
ber = []
for eb in EbN0_db:
    eb_linear = 10 ** (eb / 10)
    n0 = 1 / eb_linear                    # 符号在 ±1±1j，每比特能量 Eb = 1
    noise = np.sqrt(n0 / 2) * (np.random.randn(len(symbols))
                               + 1j * np.random.randn(len(symbols)))
    rx_bits = qpsk_demod(symbols + noise)
    errors = np.sum(rx_bits != bits)
    ber.append(errors / num_bits)
    print(f"Eb/N0 = {eb:2d} dB，误码率 = {errors / num_bits:.5f}")

plt.figure(figsize=(8, 5))
plt.semilogy(EbN0_db, ber, 'o-', label="仿真 QPSK")
plt.xlabel("Eb/N0 (dB)")
plt.ylabel("误码率 BER")
plt.title("QPSK 误码率曲线")
plt.grid(True, which='both')
plt.legend()
plt.show()
