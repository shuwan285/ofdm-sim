# -*- coding: utf-8 -*-
"""信道估计：两种插值方式在无噪 / 有噪下的表现。"""
import numpy as np

from ofdm_sim.channel import ls_channel_estimate, ls_channel_estimate_dft

N = 64
PILOT_IDX = np.arange(0, N, 4)
PILOT_VAL = (1 + 1j) / np.sqrt(2)

H_TRUE = np.fft.fft(np.array([1.0, 0.5, 0.3, 0.2]) / np.linalg.norm([1.0, 0.5, 0.3, 0.2]), N)


def _pilot_rx(values):
    """接收端只在导频位置有值（估计用不到数据子载波）。"""
    freq_rx = np.zeros((1, N), dtype=complex)
    freq_rx[:, PILOT_IDX] = values
    return freq_rx


def test_dft_estimate_exact_for_short_channel():
    """无噪时，截断长度取到真实信道长度应完全还原 H。"""
    rx = _pilot_rx(H_TRUE[PILOT_IDX] * PILOT_VAL)
    H_est = ls_channel_estimate_dft(rx, PILOT_IDX, PILOT_VAL, N, cir_length=4)
    assert np.allclose(H_est[0], H_TRUE, atol=1e-9)


def test_linear_estimate_beats_constant_extrapolation():
    """循环插值把首尾绕回接上，末段误差应远小于 np.interp 的常量外推。"""
    rx = _pilot_rx(H_TRUE[PILOT_IDX] * PILOT_VAL)
    H_est = ls_channel_estimate(rx, PILOT_IDX, PILOT_VAL, N)[0]
    extrapolated = (np.interp(np.arange(N), PILOT_IDX, H_TRUE[PILOT_IDX].real)
                    + 1j * np.interp(np.arange(N), PILOT_IDX, H_TRUE[PILOT_IDX].imag))
    assert np.abs(H_est - H_TRUE).max() < np.abs(extrapolated - H_TRUE).max() / 5


def test_shorter_truncation_denoises():
    """有噪时，截到真实长度比截到导频个数（=不截断）误差小得多。"""
    rng = np.random.default_rng(0)
    noisy = H_TRUE[PILOT_IDX] * PILOT_VAL + 0.05 * (
        rng.standard_normal(PILOT_IDX.size) + 1j * rng.standard_normal(PILOT_IDX.size))
    rx = _pilot_rx(noisy)

    def mse(cir_length):
        H_est = ls_channel_estimate_dft(rx, PILOT_IDX, PILOT_VAL, N, cir_length)[0]
        return np.mean(np.abs(H_est - H_TRUE) ** 2)

    assert mse(4) < mse(PILOT_IDX.size) / 2
