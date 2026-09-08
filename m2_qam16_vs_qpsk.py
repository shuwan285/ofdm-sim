# -*- coding: utf-8 -*-
"""
M2 数字调制 —— 16-QAM + QPSK vs 16-QAM 的误码率对比

16-QAM = 4×4 网格，16 个点，每符号 4 比特（QPSK 是 4 个点、2 比特）。
对比要看的关键点：同样的 Eb/N0 下，QPSK 误码率更低（点疏、抗噪强），
但 16-QAM 每符号多传 2 倍比特（频谱效率高）——这就是调制阶数的权衡。
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# ---------- 格雷码：2 比特 ↔ 4-PAM 电平 ----------
def two_bits_to_level(b0, b1):
    # 00→-3, 01→-1, 11→+1, 10→+3
    if b0 == 0 and b1 == 0:      return -3
    elif b0 == 0 and b1 == 1:    return -1
    elif b0 == 1 and b1 == 1:    return 1
    else:                        return 3

def level_to_two_bits(level):
    if level == -3:    return 0, 0
    elif level == -1:  return 0, 1
    elif level == 1:   return 1, 1
    else:              return 1, 0

# ---------- QPSK ----------
def qpsk_mod(bits):
    symbols = np.zeros(len(bits) // 2, dtype=complex)
    for i in range(0, len(bits), 2):
        b0, b1 = bits[i], bits[i + 1]
        if b0 == 0 and b1 == 0:      symbols[i // 2] = 1 + 1j
        elif b0 == 0 and b1 == 1:    symbols[i // 2] = -1 + 1j
        elif b0 == 1 and b1 == 1:    symbols[i // 2] = -1 - 1j
        else:                        symbols[i // 2] = 1 - 1j
    return symbols / np.sqrt(2)      # 归一化：每符号能量 = 1

def qpsk_demod(symbols):
    bits = np.zeros(2 * len(symbols), dtype=int)
    for i, s in enumerate(symbols):
        bits[2 * i]     = 0 if s.imag > 0 else 1
        bits[2 * i + 1] = 0 if s.real > 0 else 1
    return bits

# ---------- 16-QAM ----------
def qam16_mod(bits):
    symbols = np.zeros(len(bits) // 4, dtype=complex)
    for i in range(0, len(bits), 4):
        I = two_bits_to_level(bits[i], bits[i + 1])      # 前 2 比特 → 实部
        Q = two_bits_to_level(bits[i + 2], bits[i + 3])  # 后 2 比特 → 虚部
        symbols[i // 4] = I + 1j * Q
    return symbols / np.sqrt(10)     # 归一化：16-QAM 平均每符号能量 = 10，除以 √10

def qam16_demod(symbols):
    symbols = symbols * np.sqrt(10)   # 先还原归一化，回到电平 {-3,-1,+1,+3}
    bits = np.zeros(4 * len(symbols), dtype=int)
    for i, s in enumerate(symbols):
        r, q = s.real, s.imag
        # 实部判断（判决边界在 -2、0、+2）
        if r < -2:    I = -3
        elif r < 0:   I = -1
        elif r < 2:   I = 1
        else:         I = 3
        # 虚部判断
        if q < -2:    Q = -3
        elif q < 0:   Q = -1
        elif q < 2:   Q = 1
        else:         Q = 3
        b0, b1 = level_to_two_bits(I)
        b2, b3 = level_to_two_bits(Q)
        bits[4 * i: 4 * i + 4] = [b0, b1, b2, b3]
    return bits

# ---------- 通用 BER 计算 ----------
def compute_ber(mod_func, demod_func, bits_per_symbol, num_bits, EbN0_db):
    num_bits = (num_bits // bits_per_symbol) * bits_per_symbol  # 对齐到整数个符号
    bits = np.random.randint(0, 2, num_bits)
    symbols = mod_func(bits)
    ber = []
    for eb in EbN0_db:
        eb_lin = 10 ** (eb / 10)
        # 归一化后每符号能量 Es=1，每比特能量 Eb = 1/bits_per_symbol
        n0 = (1 / bits_per_symbol) / eb_lin
        noise = np.sqrt(n0 / 2) * (np.random.randn(len(symbols))
                                   + 1j * np.random.randn(len(symbols)))
        rx_bits = demod_func(symbols + noise)
        errors = np.sum(rx_bits != bits)
        ber.append(errors / num_bits)
    return ber

# ---------- 主程序 ----------
EbN0_db = np.arange(0, 13, 1)     # 0 ~ 12 dB
num_bits = 200000

ber_qpsk = compute_ber(qpsk_mod, qpsk_demod, 2, num_bits, EbN0_db)
ber_qam16 = compute_ber(qam16_mod, qam16_demod, 4, num_bits, EbN0_db)

# 打印对比表
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
