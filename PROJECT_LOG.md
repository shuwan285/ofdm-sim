# OFDM 仿真项目 · 开发日志

## 项目概述

- **目标**：用 Python 从零实现 OFDM 简易仿真，用于自学通信原理
- **仓库**：https://github.com/shuwan285/ofdm-sim
- **技术栈**：Python + NumPy + Matplotlib（无通信库依赖）
- **状态**：✅ 已完成（M0~M6 全部完成）

## 时间线（开始于 2026-09-08）

### M0 环境搭建 ✅
- Python 3.14.7 + VS Code
- 安装 numpy / matplotlib
- 配置 matplotlib 中文字体（全局 `matplotlibrc` 设为微软雅黑）

### M1 信号基础 ✅
- **产出**：`m1_fft_intro.py`、`m1_sampling_complex.py`
- **学习**：FFT（时域↔频域）、采样定理与混叠、复数与星座图

### M2 数字调制 ✅
- **产出**：`m2_qpsk_modulation.py`、`m2_qpsk_demodulation.py`、`m2_qpsk_ber.py`、`m2_qam16_vs_qpsk.py`
- **学习**：QPSK 调制解调、BER 曲线、16-QAM、高阶调制的"速率 vs 抗噪"权衡

### M3 OFDM 核心 ✅
- **产出**：`m3_ofdm_basic.py`
- **学习**：IFFT/FFT + 循环前缀，无噪声收发一致性验证

### M4 加信道 ✅
- **产出**：`m4_ofdm_awgn_ber.py`、`m4_ofdm_multipath.py`
- **学习**：AWGN 下 OFDM 透明（BER = QPSK）；多径 + CP 的误差地板现象

### M5 进阶 ✅
- **产出**：`m5_channel_estimation.py`、`m5_papr.py`
- **学习**：导频信道估计（LS + 插值）、PAPR / CCDF 分析

### M6 整理与发布 ✅
- **产出**：`README.md`、`requirements.txt`、`.gitignore`、`GLOSSARY.md`、`PROJECT_LOG.md`
- git 初始化、提交、推送到 GitHub

## 踩坑记录（重要，下次避免）

1. **matplotlib 中文乱码** → 设 `font.sans-serif = Microsoft YaHei`，并写全局 `matplotlibrc` 一劳永逸
2. **16-QAM 归一化后判决边界没缩放** → 星座点除以 √10 后，解调前要先 `×√10` 还原，否则判决边界 {-2,0,2} 全错
3. **多径信道太短看不出 CP 效果** → 3 抽头信道（延迟 2）串扰太小；改用"延迟 24 的强回波"并对比 CP=32/8/0，才出现明显的误差地板
4. **git push 在会话里超时** → 浏览器授权需要交互，需在 VS Code 自己的终端里 `git push`，不能用带超时的会话命令

### M7 复盘与修正 ✅（2026-09-15）

对外部 review 提出的问题逐条处理：

- **PAPR 统计**：原来只对 64 个 IFFT 采样点取峰值，会漏掉点与点之间的真实峰值。改成频域补零 4 倍过采样，`m5_papr.py` 里同时画 1 倍和 4 倍两条 CCDF 作对比（平均 PAPR 6.71 → 7.38 dB）。CCDF 改成阶梯曲线并去掉概率为 0 的最后一个点，对数纵轴画得出来了。
- **LICENSE**：README 声明了 MIT 但仓库里没有文件，补上。
- **信道估计**：原来的 `np.interp` 在最后一个导频(60)到子载波 63 之间做常量外推，无噪时最大误差 0.41。改成循环线性插值（首导频绕回），误差降到 0.056；另外补了「LS → 时域截断 → FFT 重构」的实现，截断长度取真实信道长度时完全精确。
- **公共模块与测试**：新建 `ofdm_sim/` 包收拢重复的调制、信道、绘图代码，分析类脚本改为导入；新增 `tests/`，15 个用例覆盖互逆性、能量归一化、无噪零误码、CP 无 ISI、BER 与理论曲线一致性。
- **可复现性**：所有脚本改用 `np.random.default_rng(seed)`，并加了 `--seed / --bits / --ebn0 / --save` 参数。
- **文档**：README 补「建模假设」章节，说明未建模的部分和 Eb/N0 的口径；删掉日志里的 SciPy（依赖里并没有用）；requirements 锁定最低版本。

## 下一步计划（可选增强）

- [ ] 16-QAM / 64-QAM 版本的 OFDM
- [ ] PAPR 抑制技术（削峰、预留子载波）
- [ ] 载波频偏 / 定时同步
- [ ] 时变瑞利衰落信道
- [ ] 信道编码（卷积码 / LDPC）带来的编码增益

## 下次继续时如何快速上手

1. `cd E:\githubxiangmu\ofdm-sim`
2. `git pull`（若在别的机器）
3. 从"下一步计划"挑一项，或直接跑 `python m3_ofdm_basic.py` 回顾核心链路
4. 参考 `GLOSSARY.md` 查概念，参考 `OFDM_notes.md` 回顾理论
