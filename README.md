# OFDM 简易仿真（Python）

用 Python + NumPy 从零实现的 OFDM 仿真，不依赖任何通信库。代码逐行对应《通信原理》里的 OFDM 原理，一边写一边理解。

## 项目内容

11 个脚本按学习顺序排列，每个是一个独立的里程碑：

| 文件 | 内容 |
|---|---|
| `m1_fft_intro.py` | 傅里叶变换入门：时域 / 频域 |
| `m1_sampling_complex.py` | 采样定理（混叠）+ 复数星座图 |
| `m2_qpsk_modulation.py` | QPSK 调制 + 星座图 |
| `m2_qpsk_demodulation.py` | QPSK 解调 + 收发一致性验证 |
| `m2_qpsk_ber.py` | QPSK 误码率（BER）曲线，与理论值对比 |
| `m2_qam16_vs_qpsk.py` | 16-QAM + 与 QPSK 的 BER 对比 |
| `m3_ofdm_basic.py` | 最简 OFDM 链路（IFFT/FFT + CP） |
| `m4_ofdm_awgn_ber.py` | OFDM + AWGN 误码率 |
| `m4_ofdm_multipath.py` | OFDM + 多径，循环前缀的作用 |
| `m5_channel_estimation.py` | 导频信道估计（LS + 插值） |
| `m5_papr.py` | PAPR（峰值平均功率比）分析 |

文档：

- `OFDM_notes.md` — OFDM 理论学习笔记
- `GLOSSARY.md` — 知识点清单与词汇表
- `PROJECT_LOG.md` — 开发日志

前几个脚本（`m1_*`、`m2_qpsk_modulation`、`m2_qpsk_demodulation`、`m3_ofdm_basic`）是讲原理的，调制解调都手写在文件里，方便单文件阅读。从 `m2_qpsk_ber` 开始的分析类脚本改成从 `ofdm_sim/` 导入，避免同一份调制代码散落多处、改一处漏一处。

## 快速开始

环境：Python 3.8+、NumPy、Matplotlib。安装：

```bash
pip install -r requirements.txt
```

运行任意脚本：

```bash
python m3_ofdm_basic.py          # 最简 OFDM 收发
python m4_ofdm_multipath.py      # 多径 + 循环前缀
python m5_channel_estimation.py  # 信道估计
```

画图的脚本都支持这几个参数：

```
--seed N      随机种子，同种子结果可复现（默认 0）
--bits N      仿真比特数
--ebn0 起:止:步  Eb/N0 扫描范围，单位 dB（如 0:12:2）
--save 路径   把图存成文件而不弹窗
```

例如 `python m5_papr.py --symbols 50000 --oversample 8 --save papr.png`。

## 公共模块与测试

`ofdm_sim/` 放各脚本共用的部分：`modulation.py`（QPSK / 16-QAM）、`ofdm.py`（IFFT、CP、AWGN）、`channel.py`（多径、导频信道估计）、`papr.py`、`plotting.py`（中文字体）、`cli.py`（命令行参数）。

测试用 pytest，覆盖调制解调互逆、能量归一化、无噪零误码、CP 够长时无 ISI、BER 与理论曲线的一致性等：

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## 建模假设

这是一个教学模型，为了把原理讲清楚做了不少简化。下面这些**没有**建模，所以不能拿这里的曲线当真实 Wi-Fi / 4G / 5G 的物理层性能看：

- **所有 N 个子载波都用来传数据**。真实的 OFDM 系统会留出 DC 子载波和保护子载波，也不会把导频铺成均匀梳状（`m5_channel_estimation.py` 里是均匀的）。
- **多径信道是固定不变的**。没有时变瑞利衰落，也没有多普勒。
- **接收端定时和载波频率完全对齐**。没有符号定时偏差、载波频偏、相位噪声。
- **没有信道编码**。真实系统会加卷积码 / LDPC / Turbo，编码增益有好几个 dB。
- **没有 PAPR 抑制**。削峰、预留子载波这些都没做。
- **PAPR 用 4 倍过采样逼近连续波形**。比只看 IFFT 采样点准得多，但严格来说仍略低于真正的连续时间 PAPR。

### 关于 Eb/N0 的口径

几个 BER 脚本里的 Eb/N0 是按**有效子载波能量**归一化的：噪声方差让每个数据子载波的 Eb/N0 等于设定值，CP 和导频占用的发射能量没有计入。

所以 `m4_ofdm_awgn_ber.py` 里 OFDM 和直传 QPSK 的曲线重合，是"能量归一化到有效符号"的理想情形。如果改成按总发射能量或有效吞吐率比较，开销是这样的（N=64、CP=16、导频每 4 个插一个）：

| 开销 | 损失 |
|---|---|
| CP 占 16/80 的发射能量 | 0.97 dB |
| 导频占 16/64 的子载波 | 1.25 dB |
| 合计 | 2.22 dB |

`m5_channel_estimation.py` 里 25% 的导频开销和 `m4_ofdm_multipath.py` 里 CP 的吞吐率损失是实打实的，脚本会把这些比例打印出来。

## 理论背景

OFDM 的核心思想：把一路高速数据拆成 N 路低速数据，放到 N 个正交子载波上并行传输。

```
比特 → 调制(QPSK/QAM) → 串并转换 → IFFT → 加循环前缀 → 发射
接收 → 去循环前缀 → FFT → 均衡 → 解调 → 比特
```

几个关键点：

- **正交**：子载波频率等间隔（Δf = 1/T），任意两个子载波相乘积分 = 0，可以无干扰分离。
- **IFFT/FFT**：用一次 IFFT 把 N 个子载波打包成时域波形，FFT 再拆包。
- **循环前缀**：把符号末尾复制到前面，长度大于最大多径延迟时可消除码间串扰（ISI）。代价是发射能量和吞吐率。
- **高 PAPR**：子载波同相相加会产生高峰值，是 OFDM 的著名缺点，`m5_papr.py` 用 CCDF 曲线量化它。

## 参考资料

- [PySDR: A Guide to SDR and DSP using Python](https://pysdr.org/content/ofdm.html)（Marc Lichtman，免费在线教材）
- 樊昌信、曹丽娜《通信原理（第 7 版）》，国防工业出版社（第 8 章 8.3 节 OFDM）
- [CommPy](https://github.com/veeresht/CommPy)（开源 Python 通信库，可作参考实现）
- Weinstein & Ebert, *Data Transmission by Frequency-Division Multiplexing Using the Discrete Fourier Transform*, IEEE Trans. Comm. Tech., 1971（OFDM 奠基论文）
- [3Blue1Brown 傅里叶变换（B 站官方中文）](https://www.bilibili.com/video/BV1pW411J7s8)

## 许可证

[MIT License](LICENSE)
