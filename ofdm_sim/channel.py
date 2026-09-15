# -*- coding: utf-8 -*-
"""信道：AWGN、多径、导频信道估计。"""
import numpy as np


def awgn(symbols, eb_n0_db, rng, es=1.0, bits_per_symbol=2):
    """符号域加高斯白噪声。

    symbols 平均能量为 es，每符号 bits_per_symbol 个比特，
    则 Eb = es / bits_per_symbol，噪声单边功率谱密度 N0 = Eb / (Eb/N0)。
    """
    eb_n0 = 10 ** (eb_n0_db / 10)
    n0 = (es / bits_per_symbol) / eb_n0
    noise = np.sqrt(n0 / 2) * (rng.standard_normal(np.shape(symbols))
                               + 1j * rng.standard_normal(np.shape(symbols)))
    return symbols + noise


def apply_multipath(signal, h):
    """线性卷积模拟多径，截断回原长（末尾拖尾落在接收窗口之外，用不到）。"""
    return np.convolve(signal, h)[:len(signal)]


def ls_channel_estimate(freq_rx, pilot_idx, pilot_val, n_fft):
    """导频 LS 估计 + 循环线性插值，返回全部 n_fft 个子载波的信道响应。

    频域是循环的，所以最后一个导频到末子载波之间不能做常量外推，
    而是把第一个导频「绕回」到 n_fft 处，用它和最后一个导频插值。

    要求导频均匀分布；不依赖信道长度的先验。
    """
    H_pilot = freq_rx[:, pilot_idx] / pilot_val
    xp = np.append(pilot_idx, pilot_idx[0] + n_fft)          # 首导频绕回到末尾
    fp = np.concatenate([H_pilot, H_pilot[:, :1]], axis=1)
    grid = np.arange(n_fft)
    H_est = np.empty((freq_rx.shape[0], n_fft), dtype=complex)
    for i in range(freq_rx.shape[0]):
        H_est[i] = (np.interp(grid, xp, fp[i].real)
                    + 1j * np.interp(grid, xp, fp[i].imag))
    return H_est


def ls_channel_estimate_dft(freq_rx, pilot_idx, pilot_val, n_fft, cir_length):
    """导频 LS + 时域截断 + FFT 重构。

    导频处做 LS，IFFT 得到冲激响应，只保留前 cir_length 个抽头
    （更靠后的抽头全是噪声，留着只会抬高估计误差），
    再补零到 n_fft 做 FFT —— 时域补零等价于频域循环插值。

    信道冲激响应比导频个数短得多时，这个方法的估计误差明显低于线性插值；
    但截断长度必须选小：取到导频个数就等于不截断，反而不如线性插值。
    实践中 cir_length 取信道最大时延扩展（不超过 CP 长度）。
    """
    H_pilot = freq_rx[:, pilot_idx] / pilot_val
    h_time = np.fft.ifft(H_pilot, axis=1)
    h_pad = np.zeros((freq_rx.shape[0], n_fft), dtype=complex)
    h_pad[:, :cir_length] = h_time[:, :cir_length]
    return np.fft.fft(h_pad, axis=1)
