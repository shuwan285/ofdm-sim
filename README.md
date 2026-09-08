# OFDM 简易仿真（Python）

一个用 Python + NumPy **从零实现**的 OFDM（正交频分复用）仿真项目，不依赖任何通信库，代码逐行对应《通信原理》中的 OFDM 原理，适合学习和理解。

## ✨ 功能特性

- **数字调制**：QPSK / 16-QAM 调制解调、星座图、误码率（BER）曲线
- **OFDM 核心**：IFFT/FFT 调制解调、循环前缀（CP）
- **信道模型**：AWGN 加性噪声、多径衰落信道
- **信道估计**：导频 + 最小二乘（LS）估计 + 插值均衡
- **性能分析**：BER vs Eb/N0 曲线、PAPR CCDF 曲线

## 📂 目录结构

按学习/开发顺序排列，每个脚本是一个独立的里程碑：

| 文件 | 内容 |
|---|---|
| `m1_fft_intro.py` | 傅里叶变换入门：时域 / 频域 |
| `m1_sampling_complex.py` | 采样定理（混叠）+ 复数星座图 |
| `m2_qpsk_modulation.py` | QPSK 调制 + 星座图 |
| `m2_qpsk_demodulation.py` | QPSK 解调 + 收发一致性验证 |
| `m2_qpsk_ber.py` | QPSK 误码率（BER）曲线 |
| `m2_qam16_vs_qpsk.py` | 16-QAM + 与 QPSK 的 BER 对比 |
| `m3_ofdm_basic.py` | 最简 OFDM 链路（IFFT/FFT + CP） |
| `m4_ofdm_awgn_ber.py` | OFDM + AWGN 误码率 |
| `m4_ofdm_multipath.py` | OFDM + 多径，循环前缀的作用 |
| `m5_channel_estimation.py` | 导频信道估计（LS + 插值） |
| `m5_papr.py` | PAPR（峰值平均功率比）分析 |
| `OFDM_notes.md` | OFDM 理论学习笔记 |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- NumPy
- Matplotlib

### 安装依赖

```bash
pip install numpy matplotlib
```

### 运行

```bash
python m3_ofdm_basic.py        # 最简 OFDM 收发
python m4_ofdm_multipath.py    # 多径 + 循环前缀
python m5_channel_estimation.py # 信道估计
```

每个脚本运行后会打印结果并弹出图（星座图 / BER 曲线 / PAPR 曲线）。

## 📐 理论背景

OFDM 的核心思想：把一路高速数据拆成 N 路低速数据，放到 N 个**正交子载波**上并行传输：

```
比特 → 调制(QPSK/QAM) → 串并转换 → IFFT → 加循环前缀 → 发射
接收 → 去循环前缀 → FFT → 均衡 → 解调 → 比特
```

关键点：

- **正交**：子载波频率等间隔（Δf = 1/T），任意两个子载波相乘积分 = 0，可无干扰分离
- **IFFT/FFT**：用一次 IFFT 把 N 个子载波"打包"成时域波形，FFT 再"拆包"
- **循环前缀**：把符号末尾复制到前面，长度大于最大多径延迟时，可消除码间串扰（ISI）
- **高 PAPR**：子载波同相相加产生高峰值，是 OFDM 的著名缺点

## 📚 参考资料

- [PySDR: A Guide to SDR and DSP using Python](https://pysdr.org/content/ofdm.html)（Marc Lichtman，免费在线教材）
- 樊昌信、曹丽娜《通信原理（第 7 版）》，国防工业出版社（第 8 章 8.3 节 OFDM）
- [CommPy](https://github.com/veeresht/CommPy)（开源 Python 通信库，可作参考实现）
- Weinstein & Ebert, *Data Transmission by Frequency-Division Multiplexing Using the Discrete Fourier Transform*, IEEE Trans. Comm. Tech., 1971（OFDM 奠基论文）
- [3Blue1Brown 傅里叶变换（B 站官方中文）](https://www.bilibili.com/video/BV1pW411J7s8)

## 📄 许可证

MIT License
