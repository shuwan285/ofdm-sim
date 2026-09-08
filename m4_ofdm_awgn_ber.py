# -*- coding: utf-8 -*-
"""OFDM + AWGN 的误码率，并与直传 QPSK 对比（两者应相同）。运行：python m4_ofdm_awgn_ber.py"""
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

N = 64    # 子载波数
cp = 16   # 循环前缀长度

def ofdm_tx(bits):
    freq_sym = qpsk_mod(bits)
    n_syms = len(freq_sym) // N
    freq_sym = freq_sym[:n_syms * N]
    freq_grid = freq_sym.reshape(n_syms, N)
    time_grid = np.fft.ifft(freq_grid, axis=1)
    with_cp = np.concatenate([time_grid[:, -cp:], time_grid], axis=1)
    return with_cp.flatten(), n_syms

def ofdm_rx(signal, n_syms):
    with_cp = signal.reshape(n_syms, N + cp)
    time_grid = with_cp[:, cp:]
    freq_grid = np.fft.fft(time_grid, axis=1)
    return qpsk_demod(freq_grid.flatten())

def qpsk_direct_ber(bits, EbN0_db):
    symbols = qpsk_mod(bits)
    ber = []
    for eb in EbN0_db:
        eb_lin = 10 ** (eb / 10)
        n0 = (1 / 2) / eb_lin
        noise = np.sqrt(n0 / 2) * (np.random.randn(len(symbols))
                                   + 1j * np.random.randn(len(symbols)))
        rx = qpsk_demod(symbols + noise)
        ber.append(np.sum(rx != bits) / len(bits))
    return ber

def ofdm_ber(bits, EbN0_db):
    tx, n_syms = ofdm_tx(bits)
    n_rx = n_syms * N * 2
    ber = []
    for eb in EbN0_db:
        eb_lin = 10 ** (eb / 10)
        sigma2 = 1 / (4 * N * eb_lin)          # 多出的 1/N 来自 IFFT 把能量摊到 N 个时域点
        noise = np.sqrt(sigma2) * (np.random.randn(len(tx))
                                   + 1j * np.random.randn(len(tx)))
        rx = ofdm_rx(tx + noise, n_syms)
        ber.append(np.sum(rx != bits[:n_rx]) / n_rx)
    return ber

num_bits = 100000
bits = np.random.randint(0, 2, num_bits)
EbN0_db = np.arange(0, 11, 1)

ber_qpsk = qpsk_direct_ber(bits, EbN0_db)
ber_ofdm = ofdm_ber(bits, EbN0_db)

print("Eb/N0 | QPSK 直接 | OFDM")
print("-" * 35)
for i, eb in enumerate(EbN0_db):
    print(f"{eb:4d}  | {ber_qpsk[i]:.2e} | {ber_ofdm[i]:.2e}")

plt.figure(figsize=(8, 5))
plt.semilogy(EbN0_db, ber_qpsk, 'o-', label="QPSK 直接传输")
plt.semilogy(EbN0_db, ber_ofdm, 's--', label="OFDM（QPSK 子载波）")
plt.xlabel("Eb/N0 (dB)")
plt.ylabel("误码率 BER")
plt.title("OFDM 在 AWGN 下与 QPSK 误码率相同")
plt.grid(True, which='both')
plt.legend()
plt.show()
