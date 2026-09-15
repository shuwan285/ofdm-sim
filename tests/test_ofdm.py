# -*- coding: utf-8 -*-
"""OFDM 收发：无噪零误码、CP 够长时无码间串扰。"""
import numpy as np

from ofdm_sim.modulation import qpsk_mod, qpsk_demod
from ofdm_sim.ofdm import ofdm_tx, ofdm_rx
from ofdm_sim.channel import apply_multipath


def test_ofdm_noiseless_roundtrip():
    N, cp = 64, 16
    rng = np.random.default_rng(1)
    bits = rng.integers(0, 2, 2 * N * 10)
    tx, n_syms = ofdm_tx(bits, N, cp)
    rx = ofdm_rx(tx, n_syms, N, cp)
    assert np.array_equal(rx, bits[:len(rx)])


def test_cp_long_enough_no_isi():
    N, cp = 64, 32
    delay, strength = 24, 0.9
    h = np.zeros(delay + 1)
    h[0], h[delay] = 1.0, strength
    h = h / np.linalg.norm(h)
    H = np.fft.fft(h, N)

    rng = np.random.default_rng(0)
    bits = rng.integers(0, 2, 2 * N * 200)
    tx, n_syms = ofdm_tx(bits, N, cp)
    y = apply_multipath(tx, h)                       # 无噪声，仅多径
    freq = np.fft.fft(y.reshape(n_syms, N + cp)[:, cp:], axis=1) / H
    rx = qpsk_demod(freq.flatten())
    assert np.array_equal(rx, bits[:len(rx)])        # CP=32 > 延迟 24，完全无 ISI
