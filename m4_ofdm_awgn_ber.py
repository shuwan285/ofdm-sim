# -*- coding: utf-8 -*-
"""OFDM + AWGN 的误码率，并与直传 QPSK 对比（两者应重合）。

注意：这里的 Eb/N0 按「有效子载波能量」归一化，CP 的发射能量开销未计入，
详见 README 的「建模假设」。运行：python m4_ofdm_awgn_ber.py
"""
import numpy as np
import matplotlib.pyplot as plt

from ofdm_sim import (qpsk_mod, qpsk_demod, qpsk_ber_theory,
                      ofdm_tx, ofdm_rx, awgn_ofdm)
from ofdm_sim.channel import awgn
from ofdm_sim.cli import add_bits_arg, add_ebn0_arg, base_parser, eb_n0_range, finish
from ofdm_sim.plotting import setup_chinese_font

setup_chinese_font()

N = 64    # 子载波数

parser = add_bits_arg(add_ebn0_arg(base_parser(__doc__)))
parser.add_argument("--cp", type=int, default=16, help="循环前缀长度（默认 16）")
args = parser.parse_args()
cp = args.cp
rng = np.random.default_rng(args.seed)

ebn0_db = eb_n0_range(args.ebn0)
bits = rng.integers(0, 2, args.bits)

# 直传 QPSK（无 OFDM，无 CP）
symbols = qpsk_mod(bits)
ber_qpsk = [np.mean(qpsk_demod(awgn(symbols, eb, rng)) != bits) for eb in ebn0_db]

# OFDM + AWGN
tx, n_syms = ofdm_tx(bits, N, cp)
n_rx = n_syms * N * 2
ber_ofdm = [np.mean(ofdm_rx(awgn_ofdm(tx, N, eb, rng), n_syms, N, cp) != bits[:n_rx])
            for eb in ebn0_db]

print(f"OFDM 参数：N={N}，CP={cp}（有效吞吐率 {N / (N + cp):.1%}）")
print("Eb/N0 | QPSK 直接 | OFDM")
print("-" * 35)
for i, eb in enumerate(ebn0_db):
    print(f"{eb:4d}  | {ber_qpsk[i]:.2e} | {ber_ofdm[i]:.2e}")

fig = plt.figure(figsize=(8, 5))
plt.semilogy(ebn0_db, ber_qpsk, 'o-', label="QPSK 直接传输")
plt.semilogy(ebn0_db, ber_ofdm, 's--', label="OFDM（QPSK 子载波）")
plt.semilogy(ebn0_db, qpsk_ber_theory(ebn0_db), 'k:', linewidth=1, label="QPSK 理论值")
plt.xlabel("Eb/N0 (dB)")
plt.ylabel("误码率 BER")
plt.title("AWGN 下 OFDM 与直传 QPSK 误码率相同")
plt.grid(True, which='both')
plt.legend()
finish(fig, args)
