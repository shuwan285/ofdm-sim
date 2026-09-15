# -*- coding: utf-8 -*-
"""多径信道下循环前缀(CP)的作用：CP 够长 vs 不够长的误码率对比。

接收端已知信道（做迫零均衡），只看 CP 长度带来的 ISI 差异。
运行：python m4_ofdm_multipath.py
"""
import numpy as np
import matplotlib.pyplot as plt

from ofdm_sim import qpsk_demod, ofdm_tx, awgn_ofdm
from ofdm_sim.channel import apply_multipath
from ofdm_sim.cli import add_bits_arg, add_ebn0_arg, base_parser, eb_n0_range, finish
from ofdm_sim.plotting import setup_chinese_font

setup_chinese_font()

N = 64

# 多径信道：直射 + 一个延迟 24 的强回波
DELAY = 24
STRENGTH = 0.9
h = np.zeros(DELAY + 1)
h[0] = 1.0
h[DELAY] = STRENGTH
h = h / np.linalg.norm(h)
H = np.fft.fft(h, N)

parser = add_bits_arg(add_ebn0_arg(base_parser(__doc__), default="0:24:3"))
args = parser.parse_args()

ebn0_db = eb_n0_range(args.ebn0)
bits = np.random.default_rng(args.seed).integers(0, 2, args.bits)


def multipath_ber(cp_len):
    tx, n_syms = ofdm_tx(bits, N, cp_len)
    rng = np.random.default_rng(args.seed)
    ber = []
    for eb in ebn0_db:
        y = awgn_ofdm(apply_multipath(tx, h), N, eb, rng)
        freq = np.fft.fft(y.reshape(n_syms, N + cp_len)[:, cp_len:], axis=1) / H
        rx = qpsk_demod(freq.flatten())
        ber.append(np.mean(rx != bits[:len(rx)]))
    return ber


ber_cp32 = multipath_ber(32)   # CP 够长（> 回波延迟 24）
ber_cp8 = multipath_ber(8)     # CP 不够
ber_cp0 = multipath_ber(0)     # 无 CP

print("Eb/N0 | CP=32(够) | CP=8(不够) | CP=0")
print("-" * 45)
for i, eb in enumerate(ebn0_db):
    print(f"{eb:4d}  | {ber_cp32[i]:.2e} | {ber_cp8[i]:.2e}  | {ber_cp0[i]:.2e}")

fig = plt.figure(figsize=(8, 5))
plt.semilogy(ebn0_db, ber_cp32, 'o-', label="CP=32（够长）")
plt.semilogy(ebn0_db, ber_cp8, 's-', label="CP=8（不够）")
plt.semilogy(ebn0_db, ber_cp0, '^-', label="CP=0（无）")
plt.xlabel("Eb/N0 (dB)")
plt.ylabel("误码率 BER")
plt.title("多径信道下，循环前缀长度的影响")
plt.grid(True, which='both')
plt.legend()
finish(fig, args)
