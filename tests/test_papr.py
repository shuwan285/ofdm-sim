# -*- coding: utf-8 -*-
"""PAPR：过采样是否真的找到更高峰值；CCDF 能否直接画在对数轴上。"""
import numpy as np

from ofdm_sim.modulation import qpsk_mod
from ofdm_sim.papr import papr_ofdm, ccdf

N = 64


def _papr_samples(n_syms, oversample, seed=0):
    rng = np.random.default_rng(seed)
    return np.array([papr_ofdm(qpsk_mod(rng.integers(0, 2, 2 * N)), oversample=oversample)
                     for _ in range(n_syms)])


def test_oversampling_never_loses_peak():
    """N 点采样是过采样网格的子集，峰值只会更高或持平，不会更低。"""
    rng = np.random.default_rng(0)
    for _ in range(100):
        freq_sym = qpsk_mod(rng.integers(0, 2, 2 * N))
        naive = papr_ofdm(freq_sym, oversample=1)
        oversampled = papr_ofdm(freq_sym, oversample=4)
        assert oversampled >= naive * (1 - 1e-9)     # 相等时留出浮点余量


def test_oversampling_raises_average_papr():
    """1 倍采样系统性低估 PAPR，平均值应有可见差距。"""
    naive = _papr_samples(2000, oversample=1).mean()
    oversampled = _papr_samples(2000, oversample=4).mean()
    assert oversampled > naive * 1.02


def test_ccdf_never_zero_and_monotone():
    x, y = ccdf(_papr_samples(2000, oversample=4))
    assert len(x) == len(y) == 1999      # 丢掉最后一个概率为 0 的点
    assert np.all(y > 0)
    assert np.all(np.diff(y) <= 0)
    assert np.all(np.diff(x) >= 0)
