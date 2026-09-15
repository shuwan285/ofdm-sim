# -*- coding: utf-8 -*-
"""导频信道估计（LS + 插值），并与完美 CSI 对比。

接收端不知道信道，只能靠均匀插入的导频估计出 H 再均衡。这里比较两种插值：

- 循环线性插值：不依赖信道长度先验，首尾按频域周期性绕回；
- LS + 时域截断 + FFT 重构：把 IFFT 出来的噪声抽头截掉，误差更小，
  但需要知道信道冲激响应长度的上界。

后者截断长度选得太大（比如取到导频个数）就退化成不截断，反而不如前者。
用 --cir-length 可以自己试。运行：python m5_channel_estimation.py
"""
import numpy as np
import matplotlib.pyplot as plt

from ofdm_sim import qpsk_mod, qpsk_demod, awgn_ofdm
from ofdm_sim.channel import (apply_multipath, ls_channel_estimate,
                              ls_channel_estimate_dft)
from ofdm_sim.cli import add_bits_arg, add_ebn0_arg, base_parser, eb_n0_range, finish
from ofdm_sim.plotting import setup_chinese_font

setup_chinese_font()

N = 64
CP = 16
PILOT_SPACING = 4

pilot_idx = np.arange(0, N, PILOT_SPACING)      # 导频位置 0,4,8,...,60
data_idx = np.setdiff1d(np.arange(N), pilot_idx)
pilot_val = (1 + 1j) / np.sqrt(2)

h = np.array([1.0, 0.5, 0.3, 0.2])              # 多径：4 个抽头
h = h / np.linalg.norm(h)
H = np.fft.fft(h, N)                            # 真实信道响应

parser = add_bits_arg(add_ebn0_arg(base_parser(__doc__), default="0:20:3"))
parser.add_argument("--cir-length", type=int, default=len(h),
                    help=f"时域截断长度（默认 {len(h)}，即真实信道长度）")
args = parser.parse_args()
rng = np.random.default_rng(args.seed)

ebn0_db = eb_n0_range(args.ebn0)
n_syms = (args.bits // 2) // data_idx.size
bits = rng.integers(0, 2, 2 * data_idx.size * n_syms)


def ofdm_tx():
    """数据 + 导频 -> 加 CP 的时域信号。"""
    freq_grid = np.zeros((n_syms, N), dtype=complex)
    freq_grid[:, data_idx] = qpsk_mod(bits).reshape(n_syms, data_idx.size)
    freq_grid[:, pilot_idx] = pilot_val
    time_grid = np.fft.ifft(freq_grid, axis=1)
    return np.concatenate([time_grid[:, -CP:], time_grid], axis=1).flatten()


tx = ofdm_tx()

ber_perfect, ber_linear, ber_dft = [], [], []
for eb in ebn0_db:
    y = awgn_ofdm(apply_multipath(tx, h), N, eb, rng)
    freq = np.fft.fft(y.reshape(n_syms, N + CP)[:, CP:], axis=1)

    H_lin = ls_channel_estimate(freq, pilot_idx, pilot_val, N)
    H_dft = ls_channel_estimate_dft(freq, pilot_idx, pilot_val, N, args.cir_length)

    for H_use, out in ((H, ber_perfect), (H_lin, ber_linear), (H_dft, ber_dft)):
        rx = qpsk_demod((freq / H_use)[:, data_idx].flatten())
        out.append(np.mean(rx != bits))

print(f"子载波 {N}，导频每 {PILOT_SPACING} 个插一个，导频开销 "
      f"{pilot_idx.size / N:.1%}，截断长度 {args.cir_length}")
print("Eb/N0 | 完美CSI  | 循环线性插值 | 时域截断+FFT")
print("-" * 48)
for i, eb in enumerate(ebn0_db):
    print(f"{eb:4d}  | {ber_perfect[i]:.2e} | {ber_linear[i]:.2e}     "
          f"| {ber_dft[i]:.2e}")

fig = plt.figure(figsize=(8, 5))
plt.semilogy(ebn0_db, ber_perfect, 'o-', label="完美信道已知 (CSI)")
plt.semilogy(ebn0_db, ber_linear, 's--', label="导频 + 循环线性插值")
plt.semilogy(ebn0_db, ber_dft, '^:', label=f"导频 + 时域截断({args.cir_length}) + FFT")
plt.xlabel("Eb/N0 (dB)")
plt.ylabel("误码率 BER")
plt.title("信道估计性能对比")
plt.grid(True, which='both')
plt.legend()
finish(fig, args)
