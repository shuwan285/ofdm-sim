# -*- coding: utf-8 -*-
"""调制 / 解调：收发互逆、能量归一化。"""
import numpy as np

from ofdm_sim.modulation import (qpsk_mod, qpsk_demod, qam16_mod, qam16_demod,
                                 qpsk_ber_theory)


def test_qpsk_roundtrip():
    rng = np.random.default_rng(0)
    bits = rng.integers(0, 2, 1000)
    assert np.array_equal(qpsk_demod(qpsk_mod(bits)), bits)


def test_qam16_roundtrip():
    rng = np.random.default_rng(0)
    bits = rng.integers(0, 2, 4000)
    assert np.array_equal(qam16_demod(qam16_mod(bits)), bits)


def test_qpsk_normalized_energy():
    """QPSK 是恒包络，任一符号的能量都是 1，不需要统计。"""
    rng = np.random.default_rng(0)
    symbols = qpsk_mod(rng.integers(0, 2, 2000))
    assert np.allclose(np.abs(symbols) ** 2, 1.0)


def test_qam16_normalized_energy():
    """遍历全部 16 个星座点求平均——随机抽样有涨落，卡不到 1e-12。"""
    all_bits = np.array([[int(b) for b in f"{i:04b}"] for i in range(16)]).ravel()
    symbols = qam16_mod(all_bits)
    assert np.isclose(np.mean(np.abs(symbols) ** 2), 1.0, atol=1e-12)


def test_qpsk_ber_theory():
    """理论曲线单调下降，且在 Eb/N0 = 6 dB 附近约 2.3e-3。"""
    theory = qpsk_ber_theory([0, 6, 10])
    assert np.all(np.diff(theory) < 0)
    assert np.isclose(theory[1], 2.3e-3, rtol=0.05)
