# -*- coding: utf-8 -*-
"""16-QAM 调制，以及 QPSK vs 16-QAM 的误码率对比。运行：python m2_qam16_vs_qpsk.py"""
import numpy as np
import matplotlib.pyplot as plt

from ofdm_sim import qpsk_mod, qpsk_demod, qam16_mod, qam16_demod
from ofdm_sim.channel import awgn
from ofdm_sim.cli import add_bits_arg, add_ebn0_arg, base_parser, eb_n0_range, finish
from ofdm_sim.plotting import setup_chinese_font

setup_chinese_font()

parser = add_bits_arg(add_ebn0_arg(base_parser(__doc__), default="0:12:1"))
args = parser.parse_args()

ebn0_db = eb_n0_range(args.ebn0)


def ber_curve(mod_func, demod_func, bits_per_symbol, seed):
    """符号平均能量 Es=1 时，每比特能量 Eb = Es / bits_per_symbol。"""
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, args.bits)
    symbols = mod_func(bits)
    return [np.mean(demod_func(awgn(symbols, eb, rng, es=1.0,
                                    bits_per_symbol=bits_per_symbol)) != bits)
            for eb in ebn0_db]


ber_qpsk = ber_curve(qpsk_mod, qpsk_demod, 2, args.seed)
ber_qam16 = ber_curve(qam16_mod, qam16_demod, 4, args.seed)

print("Eb/N0(dB) | QPSK BER   | 16-QAM BER")
print("-" * 40)
for i, eb in enumerate(ebn0_db):
    print(f"{eb:5d}     | {ber_qpsk[i]:.2e} | {ber_qam16[i]:.2e}")

fig = plt.figure(figsize=(8, 5))
plt.semilogy(ebn0_db, ber_qpsk, 'o-', label="QPSK（2 bit/符号）")
plt.semilogy(ebn0_db, ber_qam16, 's-', label="16-QAM（4 bit/符号）")
plt.xlabel("Eb/N0 (dB)")
plt.ylabel("误码率 BER")
plt.title("QPSK vs 16-QAM 误码率对比")
plt.grid(True, which='both')
plt.legend()
finish(fig, args)
