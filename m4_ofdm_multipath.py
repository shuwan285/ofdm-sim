# -*- coding: utf-8 -*-
"""
M4 加信道 —— 第二步：多径信道下，循环前缀(CP)的作用

多径信道用一个"直射 + 强回波"模拟：回波延迟 24 个采样、强度 0.9。
关键对比三种 CP 长度：
  · CP=32（> 24，够长）：回波被 CP 吸收 → 误码率随 SNR 持续下降
  · CP=8 （< 24，不够）：回波造成码间串扰(ISI) → 误码率出现"地板"，SNR 再高也降不下
  · CP=0 （无 CP）     ：更严重的地板

（"均衡"先简化为 FFT 后除以信道频率响应 H[k]，完整信道估计在 M5。）
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# ---------- QPSK ----------
def qpsk_mod(bits):
    symbols = np.zeros(len(bits) // 2, dtype=complex)
    for i in range(0, len(bits), 2):
        b0, b1 = bits[i], bits[i + 1]
        if b0 == 0 and b1 == 0:      symbols[i // 2] = 1 + 1j
        elif b0 == 0 and b1 == 1:    symbols[i // 2] = -1 + 1j
        elif b0 == 1 and b1 == 1:    symbols[i // 2] = -1 - 1j
        else:                        symbols[i // 2] = 1 - 1j
    return symbols / np.sqrt(2)

def qpsk_demod(symbols):
    bits = np.zeros(2 * len(symbols), dtype=int)
    for i, s in enumerate(symbols):
        bits[2 * i]     = 0 if s.imag > 0 else 1
        bits[2 * i + 1] = 0 if s.real > 0 else 1
    return bits

# ---------- 参数 ----------
N = 64               # 子载波数

# 多径信道：直射(延迟0) + 一个强回波(延迟24)
delay = 24           # 回波延迟（采样数）
strength = 0.9       # 回波强度
h = np.zeros(delay + 1)
h[0] = 1.0
h[delay] = strength
h = h / np.linalg.norm(h)          # 归一化
H = np.fft.fft(h, N)               # 信道频率响应（均衡用）

# ---------- 多径 + 给定 CP 长度的误码率 ----------
def multipath_ber(bits, cp_len, EbN0_db):
    freq_sym = qpsk_mod(bits)
    n_syms = len(freq_sym) // N
    freq_sym = freq_sym[:n_syms * N]
    freq_grid = freq_sym.reshape(n_syms, N)
    time_grid = np.fft.ifft(freq_grid, axis=1)               # IFFT

    if cp_len > 0:                                            # 加 CP
        with_cp = np.concatenate([time_grid[:, -cp_len:], time_grid], axis=1)
    else:                                                     # 不加 CP
        with_cp = time_grid
    tx = with_cp.flatten()
    sym_len = N + cp_len

    ber = []
    for eb in EbN0_db:
        # 1) 过多径信道（线性卷积，截断到同样长度）
        y = np.convolve(tx, h)[:len(tx)]
        # 2) 加噪声
        sigma2 = 1 / (4 * N * 10 ** (eb / 10))
        y = y + np.sqrt(sigma2) * (np.random.randn(len(tx))
                                   + 1j * np.random.randn(len(tx)))
        # 3) 去 CP → FFT → 均衡（除以 H[k]）→ 解调
        y_grid = y.reshape(n_syms, sym_len)[:, cp_len:]
        freq = np.fft.fft(y_grid, axis=1) / H
        rx = qpsk_demod(freq.flatten())
        n_rx = len(rx)
        ber.append(np.sum(rx != bits[:n_rx]) / n_rx)
    return ber

# ---------- 主程序 ----------
num_bits = 200000
bits = np.random.randint(0, 2, num_bits)
EbN0_db = np.arange(0, 25, 3)      # 0 ~ 24 dB

ber_cp32 = multipath_ber(bits, 32, EbN0_db)   # CP 够长
ber_cp8  = multipath_ber(bits, 8,  EbN0_db)   # CP 不够
ber_cp0  = multipath_ber(bits, 0,  EbN0_db)   # 无 CP

print("Eb/N0 | CP=32(够) | CP=8(不够) | CP=0")
print("-" * 45)
for i, eb in enumerate(EbN0_db):
    print(f"{eb:4d}  | {ber_cp32[i]:.2e} | {ber_cp8[i]:.2e}  | {ber_cp0[i]:.2e}")

plt.figure(figsize=(8, 5))
plt.semilogy(EbN0_db, ber_cp32, 'o-', label="CP=32（够长）")
plt.semilogy(EbN0_db, ber_cp8,  's-', label="CP=8（不够）")
plt.semilogy(EbN0_db, ber_cp0,  '^-', label="CP=0（无）")
plt.xlabel("Eb/N0 (dB)")
plt.ylabel("误码率 BER")
plt.title("多径信道下，循环前缀长度的影响")
plt.grid(True, which='both')
plt.legend()
plt.show()
