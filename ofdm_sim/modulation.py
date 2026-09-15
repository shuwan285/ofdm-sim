# -*- coding: utf-8 -*-
"""数字调制 / 解调：QPSK、16-QAM（均归一化到平均符号能量 Es=1）。"""
import math

import numpy as np


def qpsk_mod(bits):
    """比特 -> QPSK 符号（格雷码：00→+1+1j, 01→-1+1j, 11→-1-1j, 10→+1-1j）。

    第一比特控制虚部、第二比特控制实部；除以 √2 使 Es=1。
    """
    bits = np.asarray(bits, dtype=int)
    b = bits[:2 * (len(bits) // 2)].reshape(-1, 2)
    I = 1 - 2 * b[:, 1]
    Q = 1 - 2 * b[:, 0]
    return (I + 1j * Q) / np.sqrt(2)


def qpsk_demod(symbols):
    """QPSK 符号 -> 比特（看实部、虚部正负，与 qpsk_mod 互逆）。"""
    s = np.asarray(symbols)
    b0 = (s.imag <= 0).astype(int)
    b1 = (s.real <= 0).astype(int)
    return np.column_stack([b0, b1]).ravel()


def qam16_mod(bits):
    """比特 -> 16-QAM 符号（格雷码 4-PAM 正交映射），除以 √10 使 Es=1。

    每 4 比特一组：前两比特映射实部，后两比特映射虚部，电平 {-3,-1,+1,+3}。
    """
    bits = np.asarray(bits, dtype=int)
    b = bits[:4 * (len(bits) // 4)].reshape(-1, 4)
    I = (2 * b[:, 0] - 1) * (3 - 2 * b[:, 1])
    Q = (2 * b[:, 2] - 1) * (3 - 2 * b[:, 3])
    return (I + 1j * Q) / np.sqrt(10)


def qam16_demod(symbols):
    """16-QAM 符号 -> 比特（先 ×√10 还原电平，再阈值判决）。"""
    s = np.asarray(symbols) * np.sqrt(10)
    I = np.where(s.real < -2, -3, np.where(s.real < 0, -1, np.where(s.real < 2, 1, 3)))
    Q = np.where(s.imag < -2, -3, np.where(s.imag < 0, -1, np.where(s.imag < 2, 1, 3)))
    b0 = (I > 0).astype(int)
    b1 = (np.abs(I) == 1).astype(int)
    b2 = (Q > 0).astype(int)
    b3 = (np.abs(Q) == 1).astype(int)
    return np.column_stack([b0, b1, b2, b3]).ravel()


def qpsk_ber_theory(eb_n0_db):
    """AWGN 下 QPSK 的理论误比特率：Pb = Q(√(2Eb/N0)) = ½·erfc(√(Eb/N0))。"""
    eb_n0 = 10 ** (np.asarray(eb_n0_db, dtype=float) / 10)
    return 0.5 * np.array([math.erfc(math.sqrt(v)) for v in np.atleast_1d(eb_n0)])
