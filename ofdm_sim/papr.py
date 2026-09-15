# -*- coding: utf-8 -*-
"""PAPR（峰值平均功率比）计算与 CCDF 统计。"""
import numpy as np


def papr_ofdm(freq_sym, oversample=4):
    """单个 OFDM 符号的 PAPR（线性功率比 peak/mean）。

    oversample=1 只看 IFFT 的 n_fft 个离散点，会漏掉两点之间的真实峰值，
    低估 PAPR。oversample>1 时在频域补零再 IFFT，等效提高时域采样率，
    逼近连续波形的峰值。常用 4 倍，误差已可忽略。
    """
    n_fft = len(freq_sym)
    if oversample <= 1:
        time = np.fft.ifft(freq_sym)
    else:
        m = oversample * n_fft
        pad = np.zeros(m, dtype=complex)
        pad[:n_fft // 2] = freq_sym[:n_fft // 2]        # 正频率留在原位
        pad[-(n_fft // 2):] = freq_sym[n_fft // 2:]     # 负频率挪到末尾
        time = np.fft.ifft(pad) * oversample            # 补零使能量缩了 oversample 倍
    power = np.abs(time) ** 2
    return power.max() / power.mean()


def ccdf(papr_linear):
    """经验 CCDF：返回 (PAPR 阈值 dB, P(PAPR > 阈值))。

    按阶梯曲线取值，并丢掉最后那个概率为 0 的点——对数纵轴上画不出 0。
    """
    x = np.sort(10 * np.log10(np.asarray(papr_linear, dtype=float)))
    n = x.size
    y = (n - np.arange(1, n + 1)) / n
    return x[:-1], y[:-1]
