# -*- coding: utf-8 -*-
"""各仿真脚本共用的命令行参数：随机种子、数据量、Eb/N0 范围、图片保存。"""
import argparse

import numpy as np


def base_parser(description):
    """基础解析器，带 --seed（保证可复现）和 --save（存图而不弹窗）。"""
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--seed", type=int, default=0,
                   help="随机种子，同种子结果可复现（默认 0）")
    p.add_argument("--save", metavar="PATH",
                   help="图片保存路径；不给则直接弹窗显示")
    return p


def add_bits_arg(parser, default=100000):
    parser.add_argument("--bits", type=int, default=default,
                        help=f"仿真比特数（默认 {default}）")
    return parser


def add_ebn0_arg(parser, default="0:10:1"):
    parser.add_argument("--ebn0", default=default, metavar="起点:终点:步长",
                        help=f"Eb/N0 扫描范围，单位 dB（默认 {default}）")
    return parser


def eb_n0_range(spec):
    """把 "0:10:1" 解析成 np.arange(0, 11, 1)。"""
    start, stop, step = (int(v) for v in spec.split(":"))
    return np.arange(start, stop + 1, step)


def finish(fig, args):
    """按 --save 决定存图还是显示。"""
    if args.save:
        fig.savefig(args.save, dpi=150, bbox_inches="tight")
        print(f"图片已保存到 {args.save}")
    else:
        import matplotlib.pyplot as plt
        plt.show()
