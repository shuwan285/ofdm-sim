# -*- coding: utf-8 -*-
"""OFDM 的 PAPR 统计与 CCDF 曲线。

OFDM 的峰值可能落在 IFFT 采样点之间，所以要在频域补零再变换，
用更高的时域采样率去找真实峰值。这里同时画 1 倍和 4 倍的曲线作对比。
运行：python m5_papr.py
"""
import numpy as np
import matplotlib.pyplot as plt

from ofdm_sim import qpsk_mod, papr_ofdm, ccdf
from ofdm_sim.cli import base_parser, finish
from ofdm_sim.plotting import setup_chinese_font

setup_chinese_font()

N = 64

parser = base_parser(__doc__)
parser.add_argument("--symbols", type=int, default=10000, help="统计的 OFDM 符号数")
parser.add_argument("--oversample", type=int, default=4, help="频域补零倍数（默认 4）")
args = parser.parse_args()
rng = np.random.default_rng(args.seed)

papr_naive, papr_os = [], []
for _ in range(args.symbols):
    freq_sym = qpsk_mod(rng.integers(0, 2, 2 * N))
    papr_naive.append(papr_ofdm(freq_sym, oversample=1))
    papr_os.append(papr_ofdm(freq_sym, oversample=args.oversample))

papr_naive_db = 10 * np.log10(papr_naive)
papr_os_db = 10 * np.log10(papr_os)

for name, db in (("1 倍（只看 IFFT 采样点）", papr_naive_db),
                 (f"{args.oversample} 倍（补零过采样）", papr_os_db)):
    print(f"{name}：最大 {db.max():.2f} dB，平均 {db.mean():.2f} dB，"
          f"超过 10 dB 的比例 {np.mean(db > 10) * 100:.2f}%")

x_naive, y_naive = ccdf(papr_naive)
x_os, y_os = ccdf(papr_os)

fig = plt.figure(figsize=(8, 5))
plt.semilogy(x_naive, y_naive, drawstyle="steps-post", label="OFDM，1 倍采样")
plt.semilogy(x_os, y_os, drawstyle="steps-post",
             label=f"OFDM，{args.oversample} 倍过采样（N={N} 子载波）")
plt.axvline(0, color='r', linestyle='--', label="单载波 QPSK（0 dB）")
plt.xlabel("PAPR 阈值 (dB)")
plt.ylabel("P(PAPR > 阈值)")
plt.title("OFDM 的 PAPR CCDF 曲线")
plt.grid(True, which='both')
plt.legend()
finish(fig, args)
