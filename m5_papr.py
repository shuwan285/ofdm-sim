# -*- coding: utf-8 -*-
"""
M5 进阶 —— PAPR（峰值平均功率比）

OFDM 的著名缺点：PAPR 高。因为 N 个子载波叠加时，某些时刻会"同相相加"，
产生很大峰值。PAPR = 峰值功率 / 平均功率。

用 CCDF 曲线刻画：横轴是 PAPR 阈值(dB)，纵轴是"PAPR 超过该阈值"的概率。
对比：单载波 QPSK 恒定包络（PAPR 恒 = 1，即 0 dB）。
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

def qpsk_mod(bits):
    symbols = np.zeros(len(bits) // 2, dtype=complex)
    for i in range(0, len(bits), 2):
        b0, b1 = bits[i], bits[i + 1]
        if b0 == 0 and b1 == 0:      symbols[i // 2] = 1 + 1j
        elif b0 == 0 and b1 == 1:    symbols[i // 2] = -1 + 1j
        elif b0 == 1 and b1 == 1:    symbols[i // 2] = -1 - 1j
        else:                        symbols[i // 2] = 1 - 1j
    return symbols / np.sqrt(2)

# ---------- 参数 ----------
N = 64                    # 子载波数
n_syms = 10000            # 生成很多 OFDM 符号来统计 PAPR

# ---------- 计算每个 OFDM 符号的 PAPR ----------
papr_ofdm = []
for _ in range(n_syms):
    bits = np.random.randint(0, 2, 2 * N)
    freq_sym = qpsk_mod(bits)
    time_sym = np.fft.ifft(freq_sym)         # 时域信号
    peak = np.max(np.abs(time_sym) ** 2)     # 峰值功率
    avg = np.mean(np.abs(time_sym) ** 2)     # 平均功率
    papr_ofdm.append(peak / avg)

papr_db = 10 * np.log10(papr_ofdm)           # 转成 dB

# ---------- CCDF 曲线：P(PAPR > 阈值) ----------
x = np.sort(papr_db)
ccdf = 1 - np.arange(1, len(x) + 1) / len(x)

print(f"OFDM 的 PAPR 统计：最小值 {papr_db.min():.1f} dB，"
      f"最大值 {papr_db.max():.1f} dB，超过 10 dB 的比例 "
      f"{np.mean(papr_db > 10) * 100:.1f}%")

plt.figure(figsize=(8, 5))
plt.semilogy(x, ccdf, label=f"OFDM（N={N} 子载波）")
plt.axvline(0, color='r', linestyle='--', label="单载波 QPSK（0 dB）")
plt.xlabel("PAPR 阈值 (dB)")
plt.ylabel("P(PAPR > 阈值)")
plt.title("OFDM 的 PAPR CCDF 曲线")
plt.grid(True, which='both')
plt.legend()
plt.show()
