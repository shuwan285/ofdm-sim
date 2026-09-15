# -*- coding: utf-8 -*-
"""绘图通用配置。"""
import matplotlib


def setup_chinese_font():
    """配置 matplotlib 中文字体，避免中文乱码。"""
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
    matplotlib.rcParams['axes.unicode_minus'] = False
