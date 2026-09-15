# -*- coding: utf-8 -*-
"""QPSK 误码率（BER）曲线，并与理论值对比。运行：python m2_qpsk_ber.py"""
import numpy as np
import matplotlib.pyplot as plt

from ofdm_sim import qpsk_mod, qpsk_demod, qpsk_ber_theory
from ofdm_sim.channel import awgn
from ofdm_sim.cli import add_bits_arg, add_ebn0_arg, base_parser, eb_n0_range, finish
from ofdm_sim.plotting import setup_chinese_font

setup_chinese_font()

parser = add_bits_arg(add_ebn0_arg(base_parser(__doc__)))
args = parser.parse_args()
rng = np.random.default_rng(args.seed)

ebn0_db = eb_n0_range(args.ebn0)
bits = rng.integers(0, 2, args.bits)
symbols = qpsk_mod(bits)

ber = []
for eb in ebn0_db:
    rx = qpsk_demod(awgn(symbols, eb, rng))
    ber.append(np.mean(rx != bits))
    print(f"Eb/N0 = {eb:2d} dB，误码率 = {ber[-1]:.5f}")

fig = plt.figure(figsize=(8, 5))
plt.semilogy(ebn0_db, ber, 'o-', label="仿真 QPSK")
plt.semilogy(ebn0_db, qpsk_ber_theory(ebn0_db), 'k--', linewidth=1,
             label="理论值 ½erfc(√(Eb/N0))")
plt.xlabel("Eb/N0 (dB)")
plt.ylabel("误码率 BER")
plt.title("QPSK 误码率曲线")
plt.grid(True, which='both')
plt.legend()
finish(fig, args)
