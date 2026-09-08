# -*- coding: utf-8 -*-
"""导频信道估计（LS + 插值），并与完美 CSI 对比。运行：python m5_channel_estimation.py"""
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
cp = 16
pilot_spacing = 4
pilot_idx = np.arange(0, N, pilot_spacing)          # 导频位置 0,4,8,...,60
data_idx = np.array([i for i in range(N) if i not in pilot_idx])
pilot_val = (1 + 1j) / np.sqrt(2)

h = np.array([1.0, 0.5, 0.3, 0.2])
h = h / np.linalg.norm(h)
H = np.fft.fft(h, N)               # 真实信道（仅完美 CSI 用）

def ofdm_tx(bits):
    n_data = len(data_idx)
    n_syms = (len(bits) // 2) // n_data
    bits = bits[:2 * n_data * n_syms]
    data_sym = qpsk_mod(bits).reshape(n_syms, n_data)
    freq_grid = np.zeros((n_syms, N), dtype=complex)
    freq_grid[:, data_idx] = data_sym
    freq_grid[:, pilot_idx] = pilot_val
    time_grid = np.fft.ifft(freq_grid, axis=1)
    with_cp = np.concatenate([time_grid[:, -cp:], time_grid], axis=1)
    return with_cp.flatten(), n_syms, bits

def channel_estimate(freq_rx):
    H_at_pilot = freq_rx[:, pilot_idx] / pilot_val       # LS 估计
    H_est = np.zeros_like(freq_rx)
    for i in range(freq_rx.shape[0]):
        H_est[i] = (np.interp(np.arange(N), pilot_idx, H_at_pilot[i].real)
                    + 1j * np.interp(np.arange(N), pilot_idx, H_at_pilot[i].imag))
    return H_est

num_bits = 100000
bits = np.random.randint(0, 2, num_bits)
tx, n_syms, bits = ofdm_tx(bits)
n_rx = len(bits)

EbN0_db = np.arange(0, 21, 3)
ber_perfect = []
ber_est = []

for eb in EbN0_db:
    y = np.convolve(tx, h)[:len(tx)]
    sigma2 = 1 / (4 * N * 10 ** (eb / 10))
    y = y + np.sqrt(sigma2) * (np.random.randn(len(tx))
                               + 1j * np.random.randn(len(tx)))
    y_grid = y.reshape(n_syms, N + cp)[:, cp:]
    freq = np.fft.fft(y_grid, axis=1)

    eq_perfect = freq / H                                  # 完美 CSI
    rx_perfect = qpsk_demod(eq_perfect[:, data_idx].flatten())
    ber_perfect.append(np.sum(rx_perfect != bits) / n_rx)

    H_est = channel_estimate(freq)                         # 导频估计
    eq_est = freq / H_est
    rx_est = qpsk_demod(eq_est[:, data_idx].flatten())
    ber_est.append(np.sum(rx_est != bits) / n_rx)

print("Eb/N0 | 完美CSI  | 信道估计")
print("-" * 32)
for i, eb in enumerate(EbN0_db):
    print(f"{eb:4d}  | {ber_perfect[i]:.2e} | {ber_est[i]:.2e}")

plt.figure(figsize=(8, 5))
plt.semilogy(EbN0_db, ber_perfect, 'o-', label="完美信道已知 (CSI)")
plt.semilogy(EbN0_db, ber_est, 's--', label="导频信道估计")
plt.xlabel("Eb/N0 (dB)")
plt.ylabel("误码率 BER")
plt.title("信道估计性能（导频 + LS + 插值）")
plt.grid(True, which='both')
plt.legend()
plt.show()
