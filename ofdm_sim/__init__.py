# -*- coding: utf-8 -*-
"""OFDM 仿真公共库：调制解调、OFDM 收发、信道、PAPR、绘图。"""
from .modulation import (qpsk_mod, qpsk_demod, qam16_mod, qam16_demod,
                         qpsk_ber_theory)
from .ofdm import ofdm_tx, ofdm_rx, awgn_ofdm, add_cp, remove_cp
from .channel import (awgn, apply_multipath, ls_channel_estimate,
                      ls_channel_estimate_dft)
from .papr import papr_ofdm, ccdf
from .plotting import setup_chinese_font

__all__ = [
    "qpsk_mod", "qpsk_demod", "qam16_mod", "qam16_demod", "qpsk_ber_theory",
    "ofdm_tx", "ofdm_rx", "awgn_ofdm", "add_cp", "remove_cp",
    "awgn", "apply_multipath", "ls_channel_estimate", "ls_channel_estimate_dft",
    "papr_ofdm", "ccdf", "setup_chinese_font",
]
