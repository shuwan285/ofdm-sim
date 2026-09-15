# -*- coding: utf-8 -*-
"""OFDM 收发：IFFT/FFT、循环前缀（CP）、时域加噪。"""
import numpy as np

from .modulation import qpsk_mod, qpsk_demod


def add_cp(time_grid, cp):
    """把符号末尾 cp 个点复制到前面（cp=0 时原样返回）。"""
    if cp == 0:
        return time_grid
    return np.concatenate([time_grid[..., -cp:], time_grid], axis=-1)


def remove_cp(with_cp, cp):
    """去掉循环前缀，恢复无 CP 的符号。"""
    return with_cp[..., cp:]


def ofdm_tx(bits, n_fft, cp, mod_func=qpsk_mod):
    """比特 -> 加 CP 的时域 OFDM 信号。返回 (一维发送信号, 符号数)。"""
    freq_sym = mod_func(bits)
    n_syms = len(freq_sym) // n_fft
    freq_grid = freq_sym[:n_syms * n_fft].reshape(n_syms, n_fft)
    time_grid = np.fft.ifft(freq_grid, axis=1)
    return add_cp(time_grid, cp).flatten(), n_syms


def ofdm_rx(signal, n_syms, n_fft, cp, demod_func=qpsk_demod):
    """去 CP -> FFT -> 解调，返回比特。"""
    with_cp = signal.reshape(n_syms, n_fft + cp)
    freq_grid = np.fft.fft(remove_cp(with_cp, cp), axis=1)
    return demod_func(freq_grid.flatten())


def awgn_ofdm(tx, n_fft, eb_n0_db, rng):
    """给 OFDM 时域信号加 AWGN，使解调后每个子载波的 Eb/N0 等于设定值。

    注意这里按「有效子载波能量」归一化：IFFT 把每符号能量摊到 n_fft 个
    时域点，FFT 再摊回 n_fft 个子载波，故噪声方差需乘 1/n_fft。
    CP 占用的是额外发射能量，未被计入 Eb/N0。
    """
    eb_n0 = 10 ** (eb_n0_db / 10)
    sigma2 = 1 / (4 * n_fft * eb_n0)
    noise = np.sqrt(sigma2) * (rng.standard_normal(tx.shape)
                               + 1j * rng.standard_normal(tx.shape))
    return tx + noise
