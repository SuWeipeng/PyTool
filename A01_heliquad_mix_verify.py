#!/usr/bin/python3
# -*- coding:utf-8 -*-
import numpy as np
from matplotlib import pyplot as plt
import sys
import os
from utilities.LogDBParser import LogDBParser
import platform
import matplotlib

SAVE = "--save" in sys.argv
if SAVE:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
    db_name = "D:/Log/00000002.db"

# Cross-platform path handling
db_path = os.path.join('..', db_name)

# Check if file exists
if not os.path.exists(db_path):
    print(f"Error: Database file not found: {db_path}")
    sys.exit(1)

log = LogDBParser(db_path)

# ---- 参数: 从 PARM 表自动换算 z / R_c (calculate_scalars, Quad cpp:67-98) ----
parm = log.getData("PARM", "Name", "Value")
pvals = {}
for name, value in zip(parm[0], parm[1]):
    pvals[name] = float(value)          # 同名参数取最后一次

def pget(name, default):
    return pvals.get(name, default)

th_min = pget("H_COL_ANG_MIN", -10.0)
th_max = pget("H_COL_ANG_MAX", 10.0)
th_zero = min(max(pget("H_COL_ZERO_THRST", 0.0), th_min), th_max)
cmin, cmax = pget("H_COL_MIN", 1250.0), pget("H_COL_MAX", 1750.0)
if cmin >= cmax:
    cmin, cmax = 1250.0, 1750.0
z = (th_zero - th_min) / (th_max - th_min) if th_max != th_min else 0.0
r_c = (cmax - cmin) * 0.001
print(f"H_COL_ANG_MIN/MAX={th_min}/{th_max} ZERO={th_zero}  "
      f"H_COL_MIN/MAX={cmin}/{cmax}\n=> z={z:.3f}  R_c={r_c:.3f}  "
      f"(IM_STB_COL_2/3={pget('IM_STB_COL_2',40):.0f}/{pget('IM_STB_COL_3',60):.0f})")

# ---- 数据 ----
rcou = log.getData("RCOU", "TimeUS", "C1", "C2", "C3", "C4")
rate = log.getData("RATE", "TimeUS", "ROut", "POut", "YOut")
ctun = log.getData("CTUN", "TimeUS", "ThO")
if len(rate[0]) == 0:
    sys.exit("log 里没有 RATE 消息 (需要 LOG_BITMASK 姿态位)")

rt = np.asarray(rate[0], dtype=float)
rout = np.asarray(rate[1], dtype=float)
pout = np.asarray(rate[2], dtype=float)
yout = np.asarray(rate[3], dtype=float)
ct = np.asarray(ctun[0], dtype=float)
tho = np.asarray(ctun[1], dtype=float)

rc_t = np.asarray(rcou[0], dtype=float)
rc = np.vstack([np.asarray(rcou[i], dtype=float) for i in range(1, 5)])

# ---- 正向预测 ----
F_PHI = [-0.25, +0.25, +0.25, -0.25]    # Quad cpp:105-118, C1=FR(45) C2=RL(225) C3=FL(315) C4=RR(135)
F_THETA = [+0.25, -0.25, +0.25, -0.25]
F_PSI = [+0.25, +0.25, -0.25, -0.25]    # x_clockwise=false,false,true,true

ro = np.interp(rc_t, rt, rout)
po = np.interp(rc_t, rt, pout)
yo = np.interp(rc_t, rt, yout)
d = np.interp(rc_t, ct, tho)

pred = np.zeros_like(rc)
SERVO_MIN, SERVO_TRIM, SERVO_MAX = 1000.0, 1500.0, 2000.0
for ch in range(4):
    v = F_PHI[ch] * ro + F_THETA[ch] * po + F_PSI[ch] * yo + r_c * (d - z) + z
    u = 2.0 * v - 1.0
    a = np.clip(u, -1.0, 1.0) * 4500.0
    pred[ch] = np.where(a >= 0,
                        SERVO_TRIM + a / 4500.0 * (SERVO_MAX - SERVO_TRIM),
                        SERVO_TRIM + a / 4500.0 * (SERVO_TRIM - SERVO_MIN))

# ---- 正向预测 2: 含 yaw 过零钳位, 验证"单通道恒 1500"机制 (AP_MotorsHeli_Quad.cpp:204-229) ----
# 逐行复现 move_actuators: 缩放循环按 C1..C4 顺序连乘 yaw_out, 只有最后触发约束的电机
# 被精确钉零 (v=0 -> u=2z-1, z=0.5 时恰为 SERVOx_TRIM=1500)
smin  = np.array([[pget(f"SERVO{i}_MIN",  1000.0)] for i in range(1, 5)])
strim = np.array([[pget(f"SERVO{i}_TRIM", 1500.0)] for i in range(1, 5)])
smax  = np.array([[pget(f"SERVO{i}_MAX",  2000.0)] for i in range(1, 5)])
FP = np.array(F_PHI).reshape(-1, 1)
FT = np.array(F_THETA).reshape(-1, 1)
FPS = np.array(F_PSI).reshape(-1, 1)
print(f"SERVO1-4 MIN/TRIM/MAX={smin.ravel()[0]}/{strim.ravel()[0]}/{smax.ravel()[0]}"
      f"{'  (与硬编码基线一致)' if np.all(smin==1000) and np.all(strim==1500) and np.all(smax==2000) else '  WARN: 与基线 1000/1500/2000 不同!'}")

def pwm_from_angle(u):
    """SRV_Channel.cpp:199-213, 逐通道 SERVOx_MIN/TRIM/MAX."""
    a = np.clip(u, -1.0, 1.0) * 4500.0
    return np.where(a >= 0,
                    strim + a / 4500.0 * (smax - strim),
                    strim + a / 4500.0 * (strim - smin))

def quad_mixer(ro_, po_, yo_, d_):
    """逐行复现 AP_MotorsHeli_Quad::move_actuators (Quad cpp:161-236).

    返回 (pwm[4,N], pinned_ch[N]): pinned_ch = 缩放循环中最后触发钳位的电机序号
    (该电机 v 被精确钉零), -1 = 本采样未触发.
    """
    coll = r_c * (d_ - z)                                      # cpp:192,195
    out = FP * ro_ + FT * po_ + coll                           # cpp:197-201
    yaw = yo_.copy()
    pinned = np.full(out.shape[1], -1, dtype=int)
    for i in range(4):                                         # cpp:205-219 缩放循环
        y = FPS[i, 0] * yaw
        y = np.where(out[i] < 0.0, -y, y)                      # 零桨距以下 yaw 力矩反号
        trig = out[i] * (out[i] + y) < 0.0
        ys = np.where(trig & (y != 0.0), y, 1.0)
        yaw = np.where(trig, yaw * (-(out[i]) / ys), yaw)
        pinned = np.where(trig, i, pinned)
    for i in range(4):                                         # cpp:222-229 施加循环
        y = FPS[i, 0] * yaw
        y = np.where(out[i] < 0.0, -y, y)
        out[i] = out[i] + y
    u = (out + z) * 2.0 - 1.0                                  # cpp:232-236
    return pwm_from_angle(u), pinned

pred_cl, pinned_ch = quad_mixer(ro, po, yo, d)
clamp_active = pinned_ch >= 0

err = rc - pred
ok = np.abs(err) <= 1.5
print(f"\n|预测-实测|<=1.5us 占比: {ok.sum()}/{ok.size} = {100*ok.sum()/max(ok.size,1):.1f}%")
for ch in range(4):
    print(f"  C{ch+1}: bias均值={err[ch].mean():+7.1f}us  |err|<=1.5us 占比="
          f"{100*np.mean(np.abs(err[ch])<=1.5):5.1f}%")

# ---- 含钳位预测的吻合度 ----
err_cl = rc - pred_cl
print(f"\n含钳位预测 |预测-实测|<=1.5us 占比: {100*np.mean(np.abs(err_cl)<=1.5):.1f}%")
for ch in range(4):
    print(f"  C{ch+1}: bias均值={err_cl[ch].mean():+7.1f}us  |err|<=1.5us 占比="
          f"{100*np.mean(np.abs(err_cl[ch])<=1.5):5.1f}%")
print(f"yaw 钳位触发采样: {int(clamp_active.sum())}/{clamp_active.size} "
      f"= {100*np.mean(clamp_active):.1f}%")
for ch in range(4):
    m = pinned_ch == ch
    if m.any():
        print(f"  最后触发者(被钉零) C{ch+1}: {int(m.sum())} 采样 "
              f"({100*m.sum()/max(int(clamp_active.sum()),1):.0f}% of 触发)")

# ---- 精确 1500 平段: 实测≈1500 而线性预测偏离; 用含钳位预测判定机制① ----
mask_flat = (np.abs(rc - 1500.0) <= 1.0) & (np.abs(pred - 1500.0) > 3.0)
n_flat = int(mask_flat.sum())
print(f"\n实测≈1500 但线性预测偏离>3us 的采样: {n_flat} 个")
expl = mask_flat & (np.abs(pred_cl - 1500.0) <= 1.5)
print(f"其中含钳位预测同样≈1500 (机制①命中): {int(expl.sum())} 个 "
      f"({100*expl.sum()/max(n_flat,1):.0f}%)")
if n_flat:
    idx = np.where(mask_flat.any(axis=0))[0]
    splits = np.where(np.diff(idx) > 3)[0]
    for seg in np.split(idx, splits + 1):
        t0, t1 = rc_t[seg[0]], rc_t[seg[-1]]
        if t1 - t0 < 300_000:
            continue
        chs = [f"C{c+1}" for c in range(4) if mask_flat[c, seg].any()]
        pins = ", ".join(f"C{p+1}:{100*np.mean(pinned_ch[seg]==p):.0f}%"
                         for p in range(4) if np.any(pinned_ch[seg] == p))
        print(f"  {t0:.0f} ~ {t1:.0f}  ({(t1-t0)/1e6:.1f}s)  通道:{' '.join(chs)}  "
              f"ThO均值={d[seg].mean():.2f}  YOut均值={yo[seg].mean():+.2f}  "
              f"线性预测均值={pred[:, seg].mean():.0f}  "
              f"钳位预测均值={pred_cl[:, seg].mean():.0f}  钉零: {pins or '无'}")

# ---- 图: 每通道 实测 vs 两种预测 (绿底=该通道被钳位钉零的采样) ----
fig, axs = plt.subplots(4, 1, figsize=(14, 9), sharex=True)
lo = min(rc.min(), pred.min(), pred_cl.min()) - 50
hi = max(rc.max(), pred.max(), pred_cl.max()) + 50
for ch, ax in enumerate(axs):
    ax.fill_between(rc_t, lo, hi, where=(pinned_ch == ch),
                    color="green", alpha=0.10, label="yaw-clamp pinned")
    ax.plot(rc_t, rc[ch], lw=0.8, color="red", label="actual")
    ax.plot(rc_t, pred[ch], lw=0.8, color="tab:blue", ls="--", label="predicted (linear)")
    ax.plot(rc_t, pred_cl[ch], lw=2, color="green", ls=":", label="predicted (yaw clamp)")
    ax.axhline(1500, color="gray", lw=0.6)
    ax.set_ylim(lo, hi)
    ax.set_ylabel(f"C{ch+1} (us)")
    ax.grid(ls="--", lw=0.3)
    ax.legend(loc="upper right", fontsize=8)
axs[3].set_xlabel("TimeUS")
fig.suptitle("RCOU actual vs predicted (linear vs yaw-crossover clamp, Quad mixer)")
fig.tight_layout()
if SAVE:
    out_png = os.path.basename(db_name).rsplit(".", 1)[0] + "_mix_verify.png"
    fig.savefig(out_png, dpi=110)
    print(f"saved: {out_png}")
else:
    plt.show()
