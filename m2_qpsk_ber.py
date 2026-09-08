# -*- coding: utf-8 -*-
"""
M2 数字调制 —— 第三步：QPSK 误码率（BER）曲线

思路：加噪声 → 解调 → 数"错了多少比特" → 画 BER 随信噪比变化的曲线。

信噪比用 Eb/N0（每个比特的能量 ÷ 噪声强度），单位 dB，越大 = 噪声越小。
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# ========== 调制函数：比特 → QPSK 符号 ==========
def qpsk_mod(bits):
    symbols = np.zeros(len(bits) // 2, dtype=complex)
    for i in range(0, len(bits), 2):
        b0, b1 = bits[i], bits[i + 1]
        if b0 == 0 and b1 == 0:      symbols[i // 2] = 1 + 1j
        elif b0 == 0 and b1 == 1:    symbols[i // 2] = -1 + 1j
        elif b0 == 1 and b1 == 1:    symbols[i // 2] = -1 - 1j
        else:                        symbols[i // 2] = 1 - 1j
    return symbols

# ========== 解调函数：QPSK 符号 → 比特（看象限） ==========
def qpsk_demod(symbols):
    bits = np.zeros(2 * len(symbols), dtype=int)
    for i, s in enumerate(symbols):
        bits[2 * i]     = 0 if s.imag > 0 else 1   # 虚部 → 第1比特
        bits[2 * i + 1] = 0 if s.real > 0 else 1   # 实部 → 第2比特
    return bits

# ========== 主程序 ==========
num_bits = 100000                      # 比特数（越多，曲线越平滑，但跑得越慢）
bits = np.random.randint(0, 2, num_bits)
symbols = qpsk_mod(bits)

EbN0_db = np.arange(0, 11, 1)          # Eb/N0 从 0 到 10 dB，步长 1

ber = []                               # 存放每个信噪比下的误码率
for eb in EbN0_db:
    eb_linear = 10 ** (eb / 10)        # dB → 线性
    n0 = 1 / eb_linear                 # 噪声强度（符号归一化后 Eb=1）
    # 生成高斯白噪声（实部虚部各一半强度），加到符号上
    noise = np.sqrt(n0 / 2) * (np.random.randn(len(symbols))
                               + 1j * np.random.randn(len(symbols)))
    received = symbols + noise         # 接收信号 = 符号 + 噪声

    rx_bits = qpsk_demod(received)     # 解调
    errors = np.sum(rx_bits != bits)   # 数错了多少比特
    ber.append(errors / num_bits)      # 误码率 = 错比特数 / 总比特数
    print(f"Eb/N0 = {eb:2d} dB，错了 {errors} 个比特，误码率 = {errors / num_bits:.5f}")

# 画图（纵轴用对数刻度，因为 BER 变化范围极大）
plt.figure(figsize=(8, 5))
plt.semilogy(EbN0_db, ber, 'o-', label="仿真 QPSK")
plt.xlabel("Eb/N0 (dB)")
plt.ylabel("误码率 BER")
plt.title("QPSK 误码率曲线（信噪比越高，误码越少）")
plt.grid(True, which='both')
plt.legend()
plt.show()
