# -*- coding: utf-8 -*-
"""多径信道下循环前缀(CP)的作用：CP 够长 vs 不够长的误码率对比。运行：python m4_ofdm_multipath.py"""
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

def qpsk_demod(symbols):
    bits = np.zeros(2 * len(symbols), dtype=int)
    for i, s in enumerate(symbols):
        bits[2 * i]     = 0 if s.imag > 0 else 1
        bits[2 * i + 1] = 0 if s.real > 0 else 1
    return bits

N = 64

# 多径信道：直射 + 一个延迟 24 的强回波
delay = 24
strength = 0.9
h = np.zeros(delay + 1)
h[0] = 1.0
h[delay] = strength
h = h / np.linalg.norm(h)
H = np.fft.fft(h, N)

def multipath_ber(bits, cp_len, EbN0_db):
    freq_sym = qpsk_mod(bits)
    n_syms = len(freq_sym) // N
    freq_sym = freq_sym[:n_syms * N]
    freq_grid = freq_sym.reshape(n_syms, N)
    time_grid = np.fft.ifft(freq_grid, axis=1)

    if cp_len > 0:
        with_cp = np.concatenate([time_grid[:, -cp_len:], time_grid], axis=1)
    else:
        with_cp = time_grid
    tx = with_cp.flatten()
    sym_len = N + cp_len

    ber = []
    for eb in EbN0_db:
        y = np.convolve(tx, h)[:len(tx)]                 # 线性卷积模拟多径
        sigma2 = 1 / (4 * N * 10 ** (eb / 10))
        y = y + np.sqrt(sigma2) * (np.random.randn(len(tx))
                                   + 1j * np.random.randn(len(tx)))
        y_grid = y.reshape(n_syms, sym_len)[:, cp_len:]  # 去 CP
        freq = np.fft.fft(y_grid, axis=1) / H            # FFT + 均衡
        rx = qpsk_demod(freq.flatten())
        n_rx = len(rx)
        ber.append(np.sum(rx != bits[:n_rx]) / n_rx)
    return ber

num_bits = 200000
bits = np.random.randint(0, 2, num_bits)
EbN0_db = np.arange(0, 25, 3)

ber_cp32 = multipath_ber(bits, 32, EbN0_db)   # CP 够长（> 回波延迟 24）
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
