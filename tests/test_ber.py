# -*- coding: utf-8 -*-
"""误码率：与理论曲线、与直传 QPSK 的一致性。"""
import numpy as np

from ofdm_sim.modulation import qpsk_mod, qpsk_demod, qpsk_ber_theory
from ofdm_sim.channel import awgn
from ofdm_sim.ofdm import ofdm_tx, ofdm_rx, awgn_ofdm


def qpsk_ber(num_bits, eb_n0_db, seed):
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, num_bits)
    rx = qpsk_demod(awgn(qpsk_mod(bits), eb_n0_db, rng, es=1.0, bits_per_symbol=2))
    return np.mean(rx != bits)


def test_qpsk_ber_matches_theory():
    eb_db = 6.0
    theory = qpsk_ber_theory([eb_db])[0]
    assert abs(qpsk_ber(300000, eb_db, seed=0) - theory) / theory < 0.3


def test_ofdm_awgn_matches_qpsk():
    N, cp = 64, 16
    eb_db = 6.0
    num_bits = 2 * N * 1000

    rng = np.random.default_rng(0)
    bits = rng.integers(0, 2, num_bits)

    # 直传 QPSK
    ber_qpsk = np.mean(qpsk_demod(awgn(qpsk_mod(bits), eb_db,
                                       np.random.default_rng(0))) != bits)

    # OFDM + AWGN
    tx, n_syms = ofdm_tx(bits, N, cp)
    rx = ofdm_rx(awgn_ofdm(tx, N, eb_db, np.random.default_rng(0)), n_syms, N, cp)
    ber_ofdm = np.mean(rx != bits[:n_syms * N * 2])

    assert abs(ber_ofdm - ber_qpsk) / max(ber_qpsk, 1e-9) < 0.3
