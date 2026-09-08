# -*- coding: utf-8 -*-
"""OFDM 的 PAPR 统计与 CCDF 曲线。运行：python m5_papr.py"""
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
    return symbols / np.sqrt(2)

N = 64
n_syms = 10000

papr_ofdm = []
for _ in range(n_syms):
    bits = np.random.randint(0, 2, 2 * N)
    freq_sym = qpsk_mod(bits)
    time_sym = np.fft.ifft(freq_sym)
    peak = np.max(np.abs(time_sym) ** 2)
    avg = np.mean(np.abs(time_sym) ** 2)
    papr_ofdm.append(peak / avg)

papr_db = 10 * np.log10(papr_ofdm)

x = np.sort(papr_db)
ccdf = 1 - np.arange(1, len(x) + 1) / len(x)

print(f"OFDM 的 PAPR：最小 {papr_db.min():.1f} dB，最大 {papr_db.max():.1f} dB，"
      f"超过 10 dB 的比例 {np.mean(papr_db > 10) * 100:.1f}%")

plt.figure(figsize=(8, 5))
plt.semilogy(x, ccdf, label=f"OFDM（N={N} 子载波）")
plt.axvline(0, color='r', linestyle='--', label="单载波 QPSK（0 dB）")
plt.xlabel("PAPR 阈值 (dB)")
plt.ylabel("P(PAPR > 阈值)")
plt.title("OFDM 的 PAPR CCDF 曲线")
plt.grid(True, which='both')
plt.legend()
plt.show()
