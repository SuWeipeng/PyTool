#!/usr/bin/python3
# -*- coding:utf-8 -*-
# E02_PID_REVIEW.py - 移植 ArduPilot WebTools PIDReview 的 PID 分析功能到本地 matplotlib
# 参考实现: D:/github/WebTools/PIDReview/PIDReview.js 和 D:/github/WebTools/Libraries/fft.js
# 功能: 飞行总览 / 时域输入输出 / 平均FFT谱 / 频谱图(Spectrogram) / 阶跃响应(Wiener) / 参数组(Test)对比
# 运行方法:
#   python E02_PID_REVIEW.py                          # 全默认: 库 D:/Log/00000009.db, R 轴(Roll)
#   python E02_PID_REVIEW.py D:/Log/00000009.db       # 指定库文件, 轴默认 R
#   python E02_PID_REVIEW.py D:/Log/00000009.db P     # 指定库 + P 轴(Pitch)
#   python E02_PID_REVIEW.py D:/Log/00000009.db Y     # 指定库 + Y 轴(Yaw)
#   第1个参数 = 日志数据库文件(.db, 省略则用 D:/Log/00000009.db)
#   第2个参数 = 分析轴 R/P/Y(可省略, 默认 R), 其他值会报错退出
#   依赖: python3 + numpy + matplotlib(GUI 后端) + utilities/LogDBParser.py
#   提示: 脚本目录下的 utilities/ 会被自动找到, 但直接双击运行前请确认 python 在 PATH 里
#
# ==================== 图窗交互指南 ====================
# 程序打开两个窗口: 窗口1"Time"= 总览 / Inputs / Outputs, 窗口2"Freq"= 平均频谱 / 频谱图 / 阶跃响应。
# 其中 总览、Inputs、Outputs、频谱图 四条是"时间轴", 响应下面的鼠标操作;
# 平均频谱(横轴=频率)和阶跃响应(横轴固定0~0.5s)不响应鼠标, 只随右键重算而更新;
# 两个窗口的交互是打通的: 任一窗口里缩放/右键, 另一个窗口同步联动刷新。
#
# 【动作 1】左键框选缩放
#   动作: 在任一时间轴上按住左键拖出一个矩形后松开(或在工具栏平移模式下拖动)
#   目的: 粗选感兴趣的时间段(建议: 几次机动 + 一段悬停), 或放大看波形细节
#   影响: 四条时间轴(跨两个窗口)的 x 范围立即同步联动;
#         注意这只是"视图缩放", 频谱/频谱图/阶跃响应【不会】跟着变,
#         要让频域结果按新区间重算, 需接着做【动作 2】
#
# 【动作 2】右键点击时间轴(核心操作)
#   动作: 在任一窗口的时间轴上单击鼠标右键
#   目的: 把该轴当前的 x 显示范围定为新的分析区间, 重算全部频域结果
#   影响: 1) 区间按整秒取整; 若太短(数据点不足一个 FFT 窗)则控制台警告并保留原结果;
#         2) 重算平均频谱/频谱图/阶跃响应并刷新两个窗口, 控制台打印实际平均窗数和耗时;
#         3) 被点击的轴刻度变红、标题追加 "Analysis: 起始-结束 s"(本次重算所用区间);
#            总览图上出现红色阴影, 标出当前分析区间在全程中的位置;
#         4) 关闭了某个窗口不影响另一个窗口继续操作。
#
# 【动作 3】窗口底部 matplotlib 工具栏(自带功能)
#   Home=复位全部视图, 左/右箭头=撤销/恢复上一步视图, 十字=平移, 软盘=窗口存图。
#   其中平移松开左键时同样会触发时间轴联动。
#
# 【常量配置】不是交互动作, 在文件顶部修改后需重新运行:
#   FFT_WINDOW      FFT 窗长(2 的幂): 越大频率分辨率越高, 但时间定位越粗
#   AMP_MODE        幅度显示: 'linear' / 'dB' / 'PSD'
#   FREQ_LOG        频率轴是否对数显示
#   SPECTROGRAM_KEY 频谱图显示哪个信号: Tar/Act/Err/P/I/D/FF/DFF/Out
#
# 【推荐工作流】总览图找机动段 -> 左键缩放选中 -> 右键重算 -> 读频谱(交点/共振峰)
#   和阶跃响应(上升/过冲形态); 对比不同时段或不同参数时重复上述步骤。
# 【判读方法】每张图"看哪里、怎么评判"写在对应绘图函数(draw_*)的注释块里;
#   控制台会打印采样率、参数组(Test)表和每次重算的统计信息。
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
import sys
import os
import math
import time
from utilities.LogDBParser import LogDBParser
import platform
import matplotlib

# Check if running on Linux
if platform.system() == 'Linux':
    try:
        matplotlib.use('TkAgg')
    except ImportError:
        print("sudo apt-get install python3-tk")
        # Fallback to default backend
        pass

# Handle command line arguments
if len(sys.argv) > 1:
    db_name = sys.argv[1]
else:
    db_name = "D:/Log/00000009.db"

# 轴选择: R=Roll(PIDR), P=Pitch(PIDP), Y=Yaw(PIDY)
AXIS_DEF = {'R': ('PIDR', 'ATC_RAT_RLL_'),
            'P': ('PIDP', 'ATC_RAT_PIT_'),
            'Y': ('PIDY', 'ATC_RAT_YAW_')}
if len(sys.argv) > 2:
    axis_sel = sys.argv[2].upper()
else:
    axis_sel = 'R'
if axis_sel not in AXIS_DEF:
    print("Error: axis must be one of R / P / Y")
    sys.exit(1)
pid_table, parm_prefix = AXIS_DEF[axis_sel]

# Cross-platform path handling
db_path = os.path.join('..', db_name)

# Check if file exists
if not os.path.exists(db_path):
    print(f"Error: Database file not found: {db_path}")
    sys.exit(1)

log = LogDBParser(db_path)

try:
    data = log.getData("ANG","TimeUS","Roll","Pitch","Yaw")
    ang_timeus = data[0]
    ang_roll   = data[1]
    ang_pitch  = data[2]
    ang_yaw    = data[3]

    data = log.getData("POS","TimeUS","RelHomeAlt")
    pos_timeus = data[0]
    pos_alt    = data[1]

    data = log.getData("RATE","TimeUS","AOut")
    rate_timeus = data[0]
    rate_aout   = data[1]

    data = log.getData("PARM","TimeUS","Name","Value","Default")
    parm_timeus = data[0]
    parm_name   = data[1]
    parm_value  = data[2]
    parm_default = data[3]

    data = log.getData(pid_table,"TimeUS","Tar","Act","Err","P","I","D","FF","DFF","Dmod","SRate","Flags")
    pid_timeus = data[0]
    pid_tar = data[1]
    pid_act = data[2]
    pid_err = data[3]
    pid_p   = data[4]
    pid_i   = data[5]
    pid_d   = data[6]
    pid_ff  = data[7]
    pid_dff = data[8]

except Exception as e:
    print(f"Error: Problem reading data - {e}")
    sys.exit(1)

# 建立参数字典，字典形举例如下：
# {'Q_M_THST_HOVER'：[{3035145: 0.408207}, {51787417: 0.408207}, {271065946: 0.421976}]}
parms = {}
for i in range(len(parm_timeus)):
    if parms.get(parm_name[i]) == None:
        parms[parm_name[i]]=[{parm_timeus[i]:parm_value[i]}]
    else:
        parms.get(parm_name[i]).append({parm_timeus[i]:parm_value[i]})

# 查找一个参数
# 例：get_parm('ATC_RAT_RLL_P')
def get_parm(name):
    if parms.get(name) is not None:
        t = [] # 时间 TimeUS
        v = [] # 值
        for i in range(len(parms.get(name))):
            element = parms.get(name)[i]
            t.append(int(list(element.keys())[0]))
            v.append(float(list(element.values())[0]))
        return (t,v)

class PARM:
    def __init__(self,name):
        self.t,self.v = get_parm(name)

# ==================== 常量配置(对应网页上的控件) ====================
RAD2DEG = 180.0 / math.pi
US2S    = 1.0 / 1000000.0

FFT_WINDOW      = 512    # FFT 窗长, 必须是 2 的幂 (网页默认 512)
AMP_MODE        = 'dB'   # 幅度显示: 'linear' / 'dB' / 'PSD'
SPECTRUM_DB_SPAN = 90    # dB/PSD 模式纵轴显示跨度: 峰值以下多少 dB
                         # (全零信号如 DFF 在 -240dB, 不限制会把纵轴拉扁; 想看更深调大此值)
FREQ_LOG        = False  # 频率轴对数显示
SPECTROGRAM_KEY = 'Out'  # 频谱图显示的信号: Tar/Act/Err/P/I/D/FF/DFF/Out
ENSEMBLE_MAX    = 200    # 阶跃响应灰线最多画的条数(性能保护, 均值仍用全部窗计算)

FFT_KEYS = ['Tar','Act','Err','P','I','D','FF','DFF','Out']
# Plotly 默认 10 色, PIDReview 用它区分参数组
SET_COLORS = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd',
              '#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']
# 每个信号一种颜色, 时域/频域面板保持一致:
# 前 3 个与 Inputs 面板的 Tar/Act/Err 相同, 后 6 个与 Outputs 面板的 P/I/D/FF/DFF/Out 相同
KEY_COLORS = {'Tar':'#1f77b4', 'Act':'#ff7f0e', 'Err':'#2ca02c',
              'P'  :'#d62728', 'I'  :'#9467bd', 'D'  :'#8c564b',
              'FF' :'#e377c4', 'DFF':'#7f7f7f', 'Out':'#17becf'}
# 每个信号一种线型(时域面板用)
KEY_STYLE = {'Tar':'-', 'Act':'--', 'Err':':', 'P':'-', 'I':'--',
             'D':':', 'FF':'-.', 'DFF':(0,(1,1)), 'Out':'-'}
# 每个轴监控的 12 个参数: (表内键名, 参数后缀), 完整参数名 = 前缀 + 后缀
PARAM_KEYS = [('KP','P'),('KI','I'),('KD','D'),('KFF','FF'),('KDFF','D_FF'),('IMAX','IMAX'),
              ('FLTT','FLTT'),('NTF','NTF'),('FLTE','FLTE'),('NEF','NEF'),('FLTD','FLTD'),('SMAX','SMAX')]

# ==================== 数据转 numpy ====================
# 单位说明(已用 IMU0.GyrX 实测核对):
#   PID* 消息的 Tar/Act/Err 是 rad/s, 显示需换算成 deg/s;
#   P/I/D/FF/DFF 是控制器输出分量, 不换算; Out = P+I+D+FF+DFF
ang_t  = np.asarray(ang_timeus, dtype=float) * US2S
ang_r  = np.asarray(ang_roll,   dtype=float)
ang_p  = np.asarray(ang_pitch,  dtype=float)
ang_y  = np.asarray(ang_yaw,    dtype=float)
pos_t  = np.asarray(pos_timeus, dtype=float) * US2S
pos_a  = np.asarray(pos_alt,    dtype=float)
rate_t = np.asarray(rate_timeus, dtype=float) * US2S
rate_o = np.asarray(rate_aout,   dtype=float)

g_pid = {'Tar': np.asarray(pid_tar, dtype=float) * RAD2DEG,
         'Act': np.asarray(pid_act, dtype=float) * RAD2DEG,
         'Err': np.asarray(pid_err, dtype=float) * RAD2DEG,
         'P':   np.asarray(pid_p,   dtype=float),
         'I':   np.asarray(pid_i,   dtype=float),
         'D':   np.asarray(pid_d,   dtype=float),
         'FF':  np.asarray(pid_ff,  dtype=float),
         'DFF': np.asarray(pid_dff, dtype=float)}
g_pid['Out'] = g_pid['P'] + g_pid['I'] + g_pid['D'] + g_pid['FF'] + g_pid['DFF']
pid_t = np.asarray(pid_timeus, dtype=float) * US2S

# 全局分析状态
g_sets = []      # 参数组(Test)列表
g_batches = []   # 分批结果
g_pid_sets = {}  # 每个参数组包含的批
g_fft = None     # 选区内各组的逐窗 FFT
g_step = None    # 阶跃响应
g_t0 = 0.0       # 分析区间(秒)
g_t1 = 0.0

# ==================== 参数组(Test)划分 ====================
# 依 PIDReview.js:1510-1564 的状态机: 监控该轴 12 个参数,
# 任一参数变更时, 若距上次变更超过 1.0 秒则切出新组, 否则并入当前组
def build_param_sets(parm_t, parm_names, parm_vals, prefix):
    names = {prefix + suffix: key for key, suffix in PARAM_KEYS}
    # 日志顺序通常已按时间排列, 稳定排序只是保险
    order = np.argsort(parm_t, kind='stable')
    values = {'start_time': 0.0}
    for key, _ in PARAM_KEYS:
        values[key] = None
    sets = []
    last_set_end = None
    for idx in order:
        key = names.get(parm_names[idx])
        if key is None:
            continue
        t = parm_t[idx]
        v = parm_vals[idx]
        if values[key] is not None and values[key] != v:
            if last_set_end is None or (t - last_set_end) > 1.0:
                # 距上次参数变更超过 1 秒: 当前值到此为止, 记为一组
                last_set_end = t
                new_set = dict(values)
                new_set['end_time'] = last_set_end
                sets.append(new_set)
                values['start_time'] = t
            else:
                # 变更太近, 并入当前组
                values['start_time'] = t
        values[key] = v
    final = dict(values)
    final['end_time'] = math.inf
    sets.append(final)
    return sets

# 控制台打印 Test 表, 与上一组不同的值尾加 ' *'
def print_test_table(sets):
    print("%-4s %-9s %-9s" % ("Test","Start(s)","End(s)") +
          "".join("%8s" % (key) for key, _ in PARAM_KEYS))
    for i, s in enumerate(sets):
        end_str = 'end' if math.isinf(s['end_time']) else "%.2f" % s['end_time']
        print("%-4d %-9.2f %-9s" % (i+1, s['start_time'], end_str), end='')
        for key, _ in PARAM_KEYS:
            v = s[key]
            mark = ''
            if i > 0 and v is not None and sets[i-1][key] is not None and v != sets[i-1][key]:
                mark = ' *'
            print("%8s" % (('-' if v is None else "%.4g" % v) + mark), end='')
        print()

# ==================== 分批(断链检测) ====================
# 依 PIDReview.js:1378-1434: 间隔超过滑动平均 5 倍即断批(约等于丢两帧),
# 批内至少 64 个点, 批的边界同时按参数组切
def split_into_batches(t_s, sets):
    batches = []
    batch_start = 0
    count = 0
    param_set = 0
    set_start = sets[0]['start_time']
    set_end   = sets[0]['end_time']
    n = len(t_s)
    for j in range(1, n):
        if t_s[j] < set_start:
            continue
        count += 1
        past_set_end = t_s[j] > set_end
        if ((t_s[j]-t_s[j-1])*count > (t_s[j]-t_s[batch_start])*5) or (j == n-1) or past_set_end:
            if count >= 64:
                sample_rate = 1.0 / ((t_s[j-1]-t_s[batch_start]) / count)
                batches.append({'param_set': param_set, 'sample_rate': sample_rate,
                                'i0': batch_start, 'i1': j})
            if past_set_end:
                # 进入下一个参数组
                param_set += 1
                set_start = sets[param_set]['start_time']
                set_end   = sets[param_set]['end_time']
            batch_start = j
            count = 0
    return batches

# 批按参数组归堆, 并把信号切片挂到批上(切片是 numpy 视图, 不复制数据)
def build_pid_sets(batches):
    pid_sets = {}
    for b in batches:
        b['t'] = pid_t[b['i0']:b['i1']]
        for key in FFT_KEYS:
            b[key] = g_pid[key][b['i0']:b['i1']]
        pid_sets.setdefault(b['param_set'], []).append(b)
    return pid_sets

# ==================== FFT 引擎 ====================
def hanning(n):
    # 与 PIDReview Libraries/fft.js 的 hanning 完全相同: 0.5-0.5*cos(2*pi*i/(n-1))
    return np.hanning(n)

def window_correction_factors(w):
    # 线性幅值修正 1/mean(w), 能量修正 1/sqrt(mean(w^2))  (fft.js:17-22)
    return (1.0/w.mean(), 1.0/math.sqrt((w*w).mean()))

def fft_amplitude_ops(mode, fft_res):
    # 幅度显示模式, 依 fft.js:187-218
    corr_linear, corr_energy = window_correction_factors(hanning(FFT_WINDOW))
    if mode == 'PSD':
        # PSD: 先平方再平均, 10*log10, 修正 = (1/mean(w^2))*0.5/分辨率
        return {'fun': lambda x: x*x,
                'scale': lambda x: 10.0*np.log10(np.maximum(x, 1e-12)),
                'correction': corr_energy*corr_energy*0.5/fft_res,
                'label': 'PSD (dB/Hz)'}
    if mode == 'dB':
        return {'fun': lambda x: x,
                'scale': lambda x: 20.0*np.log10(np.maximum(x, 1e-12)),
                'correction': corr_linear,
                'label': 'Amplitude (dB)'}
    return {'fun': lambda x: x,
            'scale': lambda x: x,
            'correction': corr_linear,
            'label': 'Amplitude'}

def compute_range_fft():
    # 选区内滑窗 FFT: Hann 窗, 50% 重叠, 单边幅度谱
    # (依 PIDReview.js run_batch_fft:9-92 和 fft.js run_fft:40-106)
    global g_fft
    win = FFT_WINDOW
    spacing = round(win * 0.5)
    w = hanning(win)
    real_len = win//2 + 1
    # 单边谱缩放: 直流和奈奎斯特 1/N, 其余 2/N (补偿负频率丢弃的能量)
    scale = np.full(real_len, 2.0/win)
    scale[0]  = 1.0/win
    scale[-1] = 1.0/win

    # 平均采样率 = 各批采样率的算术平均 (JS: sample_time = count/sum)
    rate_sum = 0.0
    rate_cnt = 0
    for b in g_batches:
        if (b['i1']-b['i0']) < win:
            continue
        rate_sum += b['sample_rate']
        rate_cnt += 1
    if rate_cnt == 0:
        print("Error: not enough data for FFT window %d" % win)
        g_fft = None
        return
    sample_time = rate_cnt / rate_sum
    avg_rate = 1.0 / sample_time
    bins = np.arange(real_len) / (win * sample_time)

    fft_sets = []
    for si in range(len(g_sets)):
        bs = g_pid_sets.get(si)
        if bs is None:
            fft_sets.append(None)
            continue
        times = []
        specs = {k: [] for k in FFT_KEYS}
        have = False
        for b in bs:
            if len(b['Tar']) < win:
                continue
            # 9 个信号堆成矩阵一次滑窗, 比 JS 逐信号快
            mat  = np.stack([b[k] for k in FFT_KEYS])                       # (9, n)
            wins = np.lib.stride_tricks.sliding_window_view(mat, win, axis=1)[:, ::spacing, :]
            spec = np.fft.rfft(wins * w, axis=-1) * scale                   # (9, nwin, real_len)
            nwin = spec.shape[1]
            dt = 1.0 / b['sample_rate']
            # 窗中心时刻 = 批起点 + (窗起始样本 + 窗长一半) * 采样间隔
            times.append(b['t'][0] + (np.arange(nwin)*spacing + win*0.5) * dt)
            for ki, k in enumerate(FFT_KEYS):
                specs[k].append(spec[ki])
            have = True
        if not have:
            fft_sets.append(None)
            continue
        fft_sets.append({'time': np.concatenate(times),
                         'spec': {k: np.concatenate(specs[k]) for k in FFT_KEYS}})
    g_fft = {'bins': bins, 'sample_time': sample_time, 'avg_rate': avg_rate, 'sets': fft_sets}

# 选区内平均谱: 只平均窗中心落在 [g_t0,g_t1] 的窗 (PIDReview redraw:855-930)
def average_spectrum(set_fft, key, ops):
    t = set_fft['time']
    i0 = np.searchsorted(t, g_t0, side='left')
    i1 = np.searchsorted(t, g_t1, side='right')
    if i1 <= i0:
        return None, 0
    mean = ops['fun'](np.abs(set_fft['spec'][key][i0:i1])).mean(axis=0)
    y = ops['scale'](mean * ops['correction'])
    return y, i1 - i0

# 频谱图数据: 每窗一列; 空档(dt > 2.5 倍滑动平均)插 NaN 列留白 (PIDReview.js:980-1021)
def build_spectrogram(set_fft, key, ops):
    t = set_fft['time']
    spec = set_fft['spec'][key]
    xs = []
    zs = []
    count = 0
    last_time = t[0]
    section_start = t[0]
    for j in range(len(t)):
        count += 1
        this_time = t[j]
        this_dt = this_time - last_time
        average_dt = (this_time - section_start) / count
        if this_dt > average_dt * 2.5:
            # 断档: 在前后各自"本该有样本"的位置插两个空列
            count = 0
            xs.extend([last_time + average_dt, this_time - average_dt])
            zs.extend([None, None])
            section_start = this_time
        amp = np.abs(spec[j]) * ops['correction']
        xs.append(this_time)
        zs.append(ops['scale'](ops['fun'](amp)))
        last_time = this_time
    z = np.full((len(xs), len(g_fft['bins'])), np.nan)
    for i, zz in enumerate(zs):
        if zz is not None:
            z[i] = zz
    return np.array(xs), z

# ==================== 阶跃响应 ====================
# 单边复谱 -> N 点双边谱: 直流/奈奎斯特照抄, 内部 bin 减半并共轭镜像 (fft.js:109-135)
def to_double_sided(X):
    real_len = len(X)
    win = (real_len - 1) * 2
    full = np.empty(win, dtype=complex)
    full[0] = X[0]
    full[real_len-1] = X[-1]
    full[1:real_len-1] = X[1:real_len-1] * 0.5
    full[real_len:] = np.conj(X[1:real_len-1][::-1]) * 0.5
    return full

# 岭正则向量 sn: 25Hz 截止的累积高斯 -> 10/(1-S) 再取倒数 (PIDReview.js:1080-1106)
# 低频处 sn 极小(信任数据), 高频处极大(抑制噪声), 用于 Pxx 正则化
def make_sn(bins, win):
    real_len = win//2 + 1
    len_lpf = int(np.searchsorted(bins, 25.0, side='right'))
    len_lpf = max(min(len_lpf, real_len), 2)
    len_lpf += len_lpf - 2   # 双边谱修正(直流和奈奎斯特不复制)
    radius = int(math.ceil(len_lpf * 0.5))
    sigma = len_lpf / 6.0
    arr = np.ones(real_len)
    j = np.arange(len_lpf)
    ncg = np.cumsum(np.exp(-0.5/sigma**2 * (j - radius)**2.0))
    arr[:len_lpf] = ncg / ncg[-1]
    sn = np.concatenate([arr, arr[1:real_len-1][::-1]])
    return 1.0 / (10.0 * ((1.0 + 1e-9) - sn))

def compute_step_response():
    # 阶跃响应: 正则化 Wiener 传递函数估计 (PIDReview.js:1031-1209)
    # 方法源自 PID-Analyzer(Plasmatree) / PIDtoolbox:
    #   H = Pyx/Pxx = Y·conj(X) / (X·conj(X)+sn), 逆FFT后累加即阶跃
    global g_step
    if g_fft is None:
        g_step = None
        return
    win = FFT_WINDOW
    spacing = round(win / 16)   # 阶跃用更大的重叠(幅值不参与显示, 重叠多点无妨)
    w = hanning(win)
    real_len = win//2 + 1
    sn = make_sn(g_fft['bins'], win)
    scale = np.full(real_len, 2.0/win)
    scale[0]  = 1.0/win
    scale[-1] = 1.0/win
    avg_rate = g_fft['avg_rate']
    step_end = min(int(math.ceil(0.5*avg_rate)), win)   # 只取阶跃前 0.5 秒
    step_t = np.arange(step_end) / avg_rate
    gate = 20.0   # 窗内目标峰值低于 20 deg/s 的不参与(信噪比太差)
    sets_out = []
    gate_total = 0
    gate_pass = 0
    for si in range(len(g_sets)):
        bs = g_pid_sets.get(si)
        if bs is None:
            sets_out.append(None)
            continue
        steps = []
        for b in bs:
            if len(b['Tar']) < win:
                continue
            mat  = np.stack([b['Tar'], b['Act']])                            # (2, n)
            wins = np.lib.stride_tricks.sliding_window_view(mat, win, axis=1)[:, ::spacing, :]
            nwin = wins.shape[1]
            tar_max = np.abs(wins[0] * w).max(axis=-1) * RAD2DEG             # 每窗目标峰值(deg/s)
            spec = np.fft.rfft(wins * w, axis=-1) * scale
            for k in range(nwin):
                gate_total += 1
                if tar_max[k] < gate:
                    continue
                gate_pass += 1
                X = to_double_sided(spec[0, k])
                Y = to_double_sided(spec[1, k])
                Xc = np.conj(X)
                H = (Y * Xc) / (X * Xc + sn)
                imp = np.fft.ifft(H)
                steps.append(np.cumsum(imp.real)[:step_end])
        if len(steps) == 0:
            sets_out.append(None)
            continue
        sets_out.append({'t': step_t, 'steps': steps, 'mean': np.mean(steps, axis=0)})
    g_step = {'sets': sets_out, 'gate_total': gate_total, 'gate_pass': gate_pass}

# ==================== 绘图 ====================
def style_ax(ax, sci=True):
    # sci=False 用于 dB/频率轴: 科学计数偏移(如 1e2)会把刻度显示弄乱
    if sci:
        ax.ticklabel_format(style='sci', scilimits=(-1,2), axis='both')
    ax.grid(ls="--", lw=0.3)

def blend_to_white(hex_color, factor):
    # 把颜色向白色混合: factor=1 原色, 越小越浅(多组 Test 对比时区分组用)
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = int(r + (255 - r) * (1 - factor))
    g = int(g + (255 - g) * (1 - factor))
    b = int(b + (255 - b) * (1 - factor))
    return '#%02x%02x%02x' % (r, g, b)

def draw_set_rects(ax):
    # 参数组(Test)底色与标注, 多于 1 组时才画 (PIDReview.js:837-850)
    if len(g_sets) <= 1:
        return
    for si, s in enumerate(g_sets):
        ta = max(g_t0, s['start_time'])
        tb = min(g_t1, s['end_time'])
        if tb <= ta:
            continue
        c = SET_COLORS[si % len(SET_COLORS)]
        ax.axvspan(ta, tb, color=c, alpha=0.3, zorder=0)
        ax.axvline(ta, ls="--", lw=0.8, color=c)
        ax.annotate('Test%d' % (si+1), (ta, 0.98), xycoords=('data','axes fraction'),
                    color=c, fontsize=8, va='top')

def draw_overview():
    # 飞行总览: 姿态角 Roll/Pitch/Yaw(主轴, 来自 ANG, 与 PID 数据同速率) + 高度(twin1) + 油门输出(twin2)
    # ---------- 图面判读 ----------
    # 看哪里:
    #   - Roll/Pitch/Yaw 大幅变化的时段 = 机动动作, 与油门(AOut)的抬升相对应;
    #   - Yaw 曲线的竖直跳变 = 航向角 -180/180 度绕回, 不是数据错误;
    #   - 红色阴影 = 当前分析区间(右键重算的范围), 初始为全日志, 选了子区间才显示;
    #   - 高度曲线帮助确认飞行阶段(起飞/悬停/降落)。
    # 怎么用:
    #   - 先在这里拖动缩放挑一段"几次机动 + 悬停段"的时间, 再右键重算,
    #     频域结果的统计意义最好; 全程悬停(激励不足)或全程猛机动都会让判读失真。
    ax_ovr.clear()
    ax_ovr_t1.clear()
    ax_ovr_t2.clear()
    # clear() 会重置 twinx 的标签位置(左侧)和 t2 的 spine 外移, 每次重绘都要重新设置,
    # 否则 Alt(m)/AOut 与左侧 "Angle (deg)" 或彼此叠在一起
    for t in (ax_ovr_t1, ax_ovr_t2):
        t.yaxis.set_label_position('right')
        t.yaxis.set_ticks_position('right')
    ax_ovr_t2.spines['right'].set_position(('outward', 38))
    ax_ovr.plot(ang_t, ang_r, color=SET_COLORS[0], lw=0.6, label='ANG.Roll')
    ax_ovr.plot(ang_t, ang_p, color=SET_COLORS[1], lw=0.6, label='ANG.Pitch')
    ax_ovr.plot(ang_t, ang_y, color=SET_COLORS[2], lw=0.6, label='ANG.Yaw')
    ax_ovr.set_ylabel('Angle (deg)')
    ax_ovr_t1.plot(pos_t, pos_a, color=SET_COLORS[3], lw=0.8, label='POS.RelHomeAlt')
    ax_ovr_t1.set_ylabel('Alt (m)', color=SET_COLORS[3])
    ax_ovr_t1.tick_params(axis='y', colors=SET_COLORS[3])
    ax_ovr_t2.plot(rate_t, rate_o, color=SET_COLORS[4], lw=0.8, label='RATE.AOut')
    ax_ovr_t2.set_ylabel('AOut', color=SET_COLORS[4])
    ax_ovr_t2.tick_params(axis='y', colors=SET_COLORS[4])
    ax_ovr_t2.set_ylim(0, 1)
    # 只在选了子区间时画红影, 初始全范围时不画(否则整个面板泛红)
    if g_t0 > pid_t[0] or g_t1 < pid_t[-1]:
        ax_ovr.axvspan(g_t0, g_t1, color='r', alpha=0.08)
    ax_ovr.set_xlim(pid_t[0], pid_t[-1])
    style_ax(ax_ovr)
    h1,l1 = ax_ovr.get_legend_handles_labels()
    h2,l2 = ax_ovr_t1.get_legend_handles_labels()
    h3,l3 = ax_ovr_t2.get_legend_handles_labels()
    ax_ovr.legend(h1+h2+h3, l1+l2+l3, fontsize=7, loc='upper left')

def draw_time_inputs():
    # 时域输入: 目标/实际/误差 (deg/s)
    # ---------- 图面判读 ----------
    # 看哪里:
    #   - Tar(目标)与 Act(实际)的重合程度: 贴得越近跟踪越好;
    #   - Err(=Tar-Act)集中出现的时刻就是机动最剧烈的时刻;
    #   - Act 上的高频毛刺 = 机体振动直接传进了速率环。
    # 怎么评判:
    #   - 机动时 Act 能跟上 Tar 的形状、幅值略小 = 健康;
    #   - Act 明显滞后或削顶 = 增益偏低, 或输出饱和(配合下图查 SMAX/PDMX);
    #   - 悬停时 Tar 应该安静, Tar 自己抖动大说明角度环输出噪声大。
    ax_in.clear()
    draw_set_rects(ax_in)
    ax_in.plot(pid_t, g_pid['Tar'], color=SET_COLORS[0], lw=0.6, label='Tar')
    ax_in.plot(pid_t, g_pid['Act'], color=SET_COLORS[1], lw=0.6, label='Act')
    ax_in.plot(pid_t, g_pid['Err'], color=SET_COLORS[2], lw=0.6, label='Err')
    ax_in.set_xlim(g_t0, g_t1)
    ax_in.set_ylabel('deg/s')
    ax_in.set_title('Inputs')
    ax_in.legend(fontsize=8, ncols=3, loc='upper right')
    style_ax(ax_in)

def draw_time_outputs():
    # 时域输出: PID 各分量与合成输出
    # ---------- 图面判读 ----------
    # 看哪里:
    #   - FF(前馈)应承担快速机动的主要部分, P 跟随误差形状, I 缓慢抵消稳态误差;
    #   - D 项对振动最敏感: D 上毛刺多 = 振动没滤干净(查 FLTD/陷波器设置);
    #   - Out 出现平顶(削波)= 输出饱和, 说明触到了 SMAX/PDMX 限幅。
    # 怎么评判:
    #   - D 的幅值长期接近甚至超过 P = D 偏大或噪声太大, 容易引起震动和发热;
    #   - I 大幅缓慢摆动 = 重心变化或配平问题, 通常正常但会拖累响应一致性。
    ax_out.clear()
    draw_set_rects(ax_out)
    for key in ['P','I','D','FF','DFF','Out']:
        ax_out.plot(pid_t, g_pid[key], color=KEY_COLORS[key], lw=0.6, ls=KEY_STYLE[key], label=key)
    ax_out.set_xlim(g_t0, g_t1)
    ax_out.set_xlabel('Time (s)')
    ax_out.set_ylabel('Output')
    ax_out.set_title('Outputs')
    ax_out.legend(fontsize=7, ncols=6, loc='upper right')
    style_ax(ax_out)

def draw_fft():
    # 平均频谱: 颜色/线型=信号(与时域 Outputs 面板一致), 细线;
    # 多组 Test 对比时用颜色深浅区分组(单组为原色)
    # ---------- 图面判读 ----------
    # 看哪里:
    #   1. 低频段(约0.5~5Hz)的大峰 = 机动动作本身, 属正常信号;
    #   2. Act(实际)曲线从下方越过 Tar(目标)曲线的交点: 交点之后的频段里
    #      控制器在放大噪声而不是跟踪, 交点频率越低系统越"吵";
    #   3. Act/D 在 30~120Hz 出现隆起(驼峰) = 机体/桨叶共振,
    #      需要设陷波器(ATC_RAT_*_NTF/NEF)或降低 D 滤波频率(FLTD);
    #   4. 高频段的噪声地板高度 = 陀螺噪声水平, 越低越好。
    # 怎么评判:
    #   - 理想: Tar 与 Act 低频重合, 交点后 Act 平滑下降, 无共振驼峰;
    #   - DFF 全零列按 -240dB 地板显示, 是对数坐标的显示假象, 不是数据问题;
    #   - 多组参数(Test)对比时, 重点看交点频率和共振峰的变化。
    ax_fft.clear()
    plotted = []
    if g_fft is not None:
        ops = fft_amplitude_ops(AMP_MODE, g_fft['avg_rate']/FFT_WINDOW)
        xbins = g_fft['bins']
        if FREQ_LOG:
            xbins = xbins[1:]   # 0Hz 在对数轴上无法显示
        n_valid = len([s for s in g_fft['sets'] if s is not None])
        for si, sfft in enumerate(g_fft['sets']):
            if sfft is None:
                continue
            # 多组 Test 时颜色逐组变浅, 单组用原色
            shade = 1.0 if n_valid == 1 else (1.0, 0.65, 0.4, 0.25)[si % 4]
            for key in FFT_KEYS:
                y, n = average_spectrum(sfft, key, ops)
                if y is None:
                    continue
                yy = y[1:] if FREQ_LOG else y
                plotted.append(yy)
                label = ('Test%d ' % (si+1) if n_valid > 1 else '') + key
                ax_fft.plot(xbins, yy, color=blend_to_white(KEY_COLORS[key], shade),
                            ls=KEY_STYLE[key], lw=0.6, label=label)
        ax_fft.set_xlim(0, g_fft['avg_rate']/2)
        if FREQ_LOG:
            ax_fft.set_xscale('log')
        ax_fft.set_xlabel('Frequency (Hz)')
        ax_fft.set_ylabel(ops['label'])
        if AMP_MODE in ('dB','PSD') and len(plotted) > 0:
            # 全零信号的地板(-240dB)会把纵轴拉扁, 限制在峰值以下 SPECTRUM_DB_SPAN
            ymax = max(y.max() for y in plotted)
            ax_fft.set_ylim(ymax - SPECTRUM_DB_SPAN, ymax + 10)
    ax_fft.set_title('Averaged Spectrum (%s, win %d)' % (AMP_MODE, FFT_WINDOW))
    ax_fft.legend(fontsize=7, ncols=2)
    style_ax(ax_fft, sci=False)

def draw_spectrogram():
    # 频谱图: 信号分量随时间-频率的热图(多组日志取第一组)
    # ---------- 图面判读 ----------
    # 看哪里:
    #   - 水平亮带 = 固定频率的共振(桨叶/机架一阶模态), 若亮度随油门变化说明与转速相关;
    #   - 竖向亮带 = 机动动作的能量爆发, 应与总览图的机动时刻一一对应;
    #   - 空白竖条 = 日志断档(本日志无)。
    # 怎么评判:
    #   - 悬停段整体应偏暗(安静), 亮带集中出现在机动时段;
    #   - 若共振亮带的频率落在 D 滤波频率(FLTD)之上且幅值高, 就需要陷波器;
    #   - 色标已限制在峰值以下 90dB, 避免深色底部占满整图。
    ax_spc.clear()
    if g_fft is not None:
        ops = fft_amplitude_ops(AMP_MODE, g_fft['avg_rate']/FFT_WINDOW)
        for sfft in g_fft['sets']:
            if sfft is not None:
                xs, z = build_spectrogram(sfft, SPECTROGRAM_KEY, ops)
                break
        ybins = g_fft['bins']
        zz = z.T
        if FREQ_LOG:
            ybins = ybins[1:]
            zz = zz[1:]
        zmask = np.ma.masked_invalid(zz)
        vmin, vmax = None, None
        if AMP_MODE in ('dB','PSD') and zmask.count() > 0:
            vmax = float(zmask.max())
            vmin = vmax - SPECTRUM_DB_SPAN   # 同频谱图, 只显示峰值以下 SPECTRUM_DB_SPAN
        ax_spc.pcolormesh(xs, ybins, zmask, shading='nearest', cmap='jet',
                          vmin=vmin, vmax=vmax)
        ax_spc.set_xlim(g_t0, g_t1)
        if FREQ_LOG:
            ax_spc.set_yscale('log')
        ax_spc.set_ylabel('Frequency (Hz)')
        ax_spc.ticklabel_format(style='sci', scilimits=(-1,2), axis='x')
    ax_spc.set_xlabel('Time (s)')
    ax_spc.set_title('Spectrogram (%s)' % SPECTROGRAM_KEY)

def draw_step():
    # 阶跃响应: 灰线=各合格窗的独立估计, 彩线=组均值, 虚线 y=1 为理想跟踪
    # ---------- 图面判读 ----------
    # 看哪里:
    #   - 彩色均值线 = 系统对目标阶跃的平均闭环响应(0->1 的过程);
    #   - 灰线束 = 每个合格窗(目标峰值>20deg/s)的独立估计, 越集中越可信;
    #   - 虚线 y=1 = 完美跟踪, 横轴只看前 0.5 秒。
    # 怎么评判:
    #   - 快速升到 1、轻微过冲(<1.2)后回稳 = 阻尼良好, 调得不错;
    #   - 明显过冲(>1.4)再回落 = 阻尼不足, P/I 偏大或 D 不足;
    #   - 缓慢爬升到 1 = 响应迟钝, 增益偏低或滤波过重;
    #   - 灰线散乱互不一致 = 激励质量差, 此图仅供参考。
    # 方法: 正则化 Wiener 传递函数估计, 源自 PID-Analyzer(Plasmatree)/PIDtoolbox。
    ax_stp.clear()
    if g_step is not None:
        n_valid = len([s for s in g_step['sets'] if s is not None])
        for si, ss in enumerate(g_step['sets']):
            if ss is None:
                continue
            c = SET_COLORS[si % len(SET_COLORS)]
            if n_valid == 1:
                ens = ss['steps']
                if len(ens) > ENSEMBLE_MAX:
                    # 灰线太多影响刷新速度, 均匀抽稀显示(均值仍用全部窗)
                    idx = np.linspace(0, len(ens)-1, ENSEMBLE_MAX).astype(int)
                    ens = [ens[i] for i in idx]
                ens_mat = np.full((len(ens), len(ss['t'])), np.nan)
                for i, e in enumerate(ens):
                    ens_mat[i] = e
                ax_stp.plot(ss['t'], ens_mat.T, color=(0.4,0.4,0.4,0.2), lw=0.5)
            label = ('Test%d' % (si+1)) if n_valid > 1 else 'Mean'
            ax_stp.plot(ss['t'], ss['mean'], color=c, lw=2.2, label=label)
        ax_stp.axhline(1.0, ls=":", lw=0.8, color='k')
        ax_stp.set_xlim(0, 0.5)
        ax_stp.set_ylim(0, 2)
        ax_stp.set_xlabel('Time (s)')
        ax_stp.set_ylabel('Response')
    ax_stp.set_title('Step Response (Wiener, gate 20 deg/s)')
    ax_stp.legend(fontsize=8, loc='upper right')
    style_ax(ax_stp)

def draw_all():
    # 唯一重绘入口: 清空所有轴后整体重画, 避免线条泄漏
    draw_overview()
    draw_time_inputs()
    draw_time_outputs()
    draw_fft()
    draw_spectrogram()
    draw_step()

# ==================== 交互 ====================
def recalc_all():
    # 按当前 [g_t0,g_t1] 重算 FFT 与阶跃响应, 控制台打印耗时
    global g_fft, g_step
    t_start = time.time()
    compute_range_fft()
    compute_step_response()
    if g_fft is not None:
        # 只统计窗中心落在当前分析区间内的窗
        nwin = 0
        for s in g_fft['sets']:
            if s is not None:
                nwin += int(((s['time'] >= g_t0) & (s['time'] <= g_t1)).sum())
        print("FFT: window %d, avg rate %.2f Hz, res %.2f Hz, windows %d, recalc %.0f ms (range %d-%d s)"
              % (FFT_WINDOW, g_fft['avg_rate'], g_fft['avg_rate']/FFT_WINDOW, nwin,
                 (time.time()-t_start)*1000.0, g_t0, g_t1))
        if g_step is not None:
            print("step windows: %d/%d passed 20 deg/s gate"
                  % (g_step['gate_pass'], g_step['gate_total']))

def host_of(ax):
    # 总览的两个 twinx 归属到 ax_ovr 处理
    if ax is ax_ovr_t1 or ax is ax_ovr_t2:
        return ax_ovr
    return ax

def on_press(event):
    # 鼠标右键: 以当前缩放范围为分析区间, 重算频域并整体重绘 (E01 惯用法)
    global g_t0, g_t1
    if event.button != 3 or event.inaxes is None or event.xdata is None:
        return
    ax = host_of(event.inaxes)
    if ax not in g_time_axes:
        return
    xmin, xmax = sorted(ax.get_xlim())
    t0 = int(math.floor(xmin))
    t1 = int(math.ceil(xmax))
    avg_rate = g_fft['avg_rate'] if g_fft is not None else 0.0
    if (t1 - t0) * avg_rate < FFT_WINDOW:
        print("Warning: range %d-%d s too short for window %d at %.1f Hz, keep old range"
              % (t0, t1, FFT_WINDOW, avg_rate))
        return
    g_t0, g_t1 = t0, t1
    recalc_all()
    draw_all()
    # E01 式反馈: 红刻度 + 标题提示(标明本次重算所用的分析区间)
    ax.tick_params(axis='x', colors='red')
    ax.tick_params(axis='y', colors='red')
    ax.set_title(ax.get_title() + "   <- Analysis: %d-%d s" % (g_t0, g_t1))
    flush_all()

def button_release(event):
    # 鼠标左键: 任一时间轴缩放后, 其余时间轴联动 x 范围 (E01 惯用法)
    if event.button != 1 or event.inaxes is None:
        return
    ax = host_of(event.inaxes)
    if ax not in g_time_axes:
        return
    xmin, xmax = ax.get_xlim()
    for a in g_time_axes:
        if a is not ax:
            a.set_xlim(xmin, xmax)
    flush_all()

# ==================== 主流程 ====================
print("=== E02 PID Review ===")
print("axis: %s -> %s / %s*" % (axis_sel, pid_table, parm_prefix))
print("%s: %d rows, %.2f - %.2f s" % (pid_table, len(pid_t), pid_t[0], pid_t[-1]))

# 参数组与分批
parm_t_arr = np.asarray(parm_timeus, dtype=float) * US2S
g_sets    = build_param_sets(parm_t_arr, parm_name, np.asarray(parm_value, dtype=float), parm_prefix)
g_batches = split_into_batches(pid_t, g_sets)
g_pid_sets = build_pid_sets(g_batches)
avg_rate0 = np.mean([b['sample_rate'] for b in g_batches]) if len(g_batches) > 0 else 0.0
print("batches: %d, sample rate: %.2f Hz (avg)" % (len(g_batches), avg_rate0))
print("param sets: %d" % len(g_sets))
print_test_table(g_sets)

# 初始分析区间: 全日志
g_t0 = int(math.floor(pid_t[0]))
g_t1 = int(math.ceil(pid_t[-1]))

# ==================== 绘图布局: 两个窗口 ====================
# 窗口1 时域: 总览(通栏) + Inputs + Outputs;  窗口2 频域: 平均频谱 + 频谱图 + 阶跃响应
# 鼠标交互跨窗口: 任一窗口左键缩放四条时间轴联动, 右键均可触发重算并刷新两个窗口
fig_time = plt.figure("E02 Time", figsize=(16, 9), dpi=1920/16)
gs_t = gridspec.GridSpec(nrows=3, ncols=1, left=0.06, right=0.90, top=0.92, bottom=0.07,
                         hspace=0.42, height_ratios=[0.75, 1, 1])
ax_ovr = fig_time.add_subplot(gs_t[0])   # 飞行总览
ax_in  = fig_time.add_subplot(gs_t[1])   # 时域输入
ax_out = fig_time.add_subplot(gs_t[2])   # 时域输出
# 总览的两个副轴(高度/油门), 只创建一次; ax.clear() 不会清掉 twin, 重绘时需各自 clear
ax_ovr_t1 = ax_ovr.twinx()
ax_ovr_t2 = ax_ovr.twinx()
ax_ovr_t2.spines['right'].set_position(('outward', 38))
fig_time.suptitle("E02 PID Review  Time  -  %s / %s* (axis %s)" % (pid_table, parm_prefix, axis_sel))

fig_freq = plt.figure("E02 Freq", figsize=(16, 9), dpi=1920/16)
gs_f = gridspec.GridSpec(nrows=2, ncols=2, left=0.06, right=0.95, top=0.92, bottom=0.07,
                         wspace=0.18, hspace=0.35)
ax_fft = fig_freq.add_subplot(gs_f[0, 0])   # 平均频谱
ax_stp = fig_freq.add_subplot(gs_f[1, 0])   # 阶跃响应
ax_spc = fig_freq.add_subplot(gs_f[:, 1])   # 频谱图(右侧通栏, 热图更高)
fig_freq.suptitle("E02 PID Review  Freq  -  %s / %s* (axis %s)" % (pid_table, parm_prefix, axis_sel))

# 可右键重算/左键联动的时间轴(跨两个窗口)
g_time_axes = [ax_ovr, ax_in, ax_out, ax_spc]
g_figs = [fig_time, fig_freq]

def flush_all():
    # 刷新两个窗口; 某个窗口被关闭时跳过, 不影响另一个继续用
    for f in g_figs:
        try:
            f.canvas.draw_idle()
        except Exception:
            pass

# 初始计算与绘制
recalc_all()
draw_all()
flush_all()

# 两个窗口都挂上同一组鼠标事件处理
for f in g_figs:
    f.canvas.mpl_connect('button_press_event', on_press)
    f.canvas.mpl_connect('button_release_event', button_release)

plt.show()
