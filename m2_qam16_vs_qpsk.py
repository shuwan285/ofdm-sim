# -*- coding: utf-8 -*-
"""16-QAM 调制，以及 QPSK vs 16-QAM 的误码率对比。运行：python m2_qam16_vs_qpsk.py"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# 中文字体
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 格雷码：2 比特 <-> 4-PAM 电平
def two_bits_to_level(b0, b1):
    # 00->-3, 01->-1, 11->+1, 10->+3
    if b0 == 0 and b1 == 0:
        return -3
    elif b0 == 0 and b1 == 1:
        return -1
    elif b0 == 1 and b1 == 1:
        return 1
    else:
        return 3

def level_to_two_bits(level):
    if level == -3:
        return 0, 0
    elif level == -1:
        return 0, 1
    elif level == 1:
        return 1, 1
    else:
        return 1, 0

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

def qam16_mod(bits):
    symbols = np.zeros(len(bits) // 4, dtype=complex)
    for i in range(0, len(bits), 4):
        I = two_bits_to_level(bits[i], bits[i + 1])
        Q = two_bits_to_level(bits[i + 2], bits[i + 3])
        symbols[i // 4] = I + 1j * Q
    return symbols / np.sqrt(10)          # 16-QAM 平均能量 = 10

def qam16_demod(symbols):
    symbols = symbols * np.sqrt(10)       # 还原归一化，回到电平 {-3,-1,+1,+3}
    bits = np.zeros(4 * len(symbols), dtype=int)
    for i, s in enumerate(symbols):
        r, q = s.real, s.imag
        I = -3 if r < -2 else (-1 if r < 0 else (1 if r < 2 else 3))
        Q = -3 if q < -2 else (-1 if q < 0 else (1 if q < 2 else 3))
        b0, b1 = level_to_two_bits(I)
        b2, b3 = level_to_two_bits(Q)
        bits[4 * i: 4 * i + 4] = [b0, b1, b2, b3]
    return bits

def compute_ber(mod_func, demod_func, bits_per_symbol, num_bits, EbN0_db):
    num_bits = (num_bits // bits_per_symbol) * bits_per_symbol
    bits = np.random.randint(0, 2, num_bits)
    symbols = mod_func(bits)
    ber = []
    for eb in EbN0_db:
        eb_lin = 10 ** (eb / 10)
        n0 = (1 / bits_per_symbol) / eb_lin   # 归一化后 Es=1，Eb = 1/bits_per_symbol
        noise = np.sqrt(n0 / 2) * (np.random.randn(len(symbols))
                                   + 1j * np.random.randn(len(symbols)))
        rx_bits = demod_func(symbols + noise)
        errors = np.sum(rx_bits != bits)
        ber.append(errors / num_bits)
    return ber

EbN0_db = np.arange(0, 13, 1)
num_bits = 200000

ber_qpsk = compute_ber(qpsk_mod, qpsk_demod, 2, num_bits, EbN0_db)
ber_qam16 = compute_ber(qam16_mod, qam16_demod, 4, num_bits, EbN0_db)

print("Eb/N0(dB) | QPSK BER   | 16-QAM BER")
print("-" * 40)
for i, eb in enumerate(EbN0_db):
    print(f"{eb:5d}     | {ber_qpsk[i]:.2e} | {ber_qam16[i]:.2e}")

plt.figure(figsize=(8, 5))
plt.semilogy(EbN0_db, ber_qpsk, 'o-', label="QPSK（2 bit/符号）")
plt.semilogy(EbN0_db, ber_qam16, 's-', label="16-QAM（4 bit/符号）")
plt.xlabel("Eb/N0 (dB)")
plt.ylabel("误码率 BER")
plt.title("QPSK vs 16-QAM 误码率对比")
plt.grid(True, which='both')
plt.legend()
plt.show()
