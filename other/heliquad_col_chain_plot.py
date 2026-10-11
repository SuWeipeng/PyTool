#!/usr/bin/env python3
"""heliquad 总距参数换算链交互图.

可视化 H_COL_ANG_MIN/ZERO_THRST/LAND_MIN/MAX 与 H_COL_MIN/MAX 如何经过
calculate_scalars (AP_MotorsHeli_Quad.cpp:67-98)
  -> move_actuators (AP_MotorsHeli_Quad.cpp:161-237, 无姿态/偏航项的平均通道)
  -> pwm_from_angle (SRV_Channel.cpp:199-213)
变成 z / l / R_c 和 "总距指令 delta -> 舵机 PWM / 桨距角" 的映射曲线.

用法:
    python3 heliquad_col_chain_plot.py            # 交互窗口(拖滑条)
    python3 heliquad_col_chain_plot.py --save out.png   # 无头渲染
"""
import argparse
import os
import sys

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# SERVO1-4 默认标定(stingray.parm); pwm_from_angle 的三端点
SERVO_MIN, SERVO_TRIM, SERVO_MAX = 1000.0, 1500.0, 2000.0
ANGLE_MAX = 4500.0  # cdeg, QUAD_SERVO_MAX_ANGLE (AP_MotorsHeli_Quad.cpp:31)

P0 = dict(th_min=-10.0, th_zero=0.0, th_land=-2.0, th_max=10.0,
          col_min=1250.0, col_max=1750.0, u_hover=0.30)

SLIDERS = [  # (key, label, lo, hi, step) -- grouped: blade-pitch angles, collective range, hover
    ("th_min",  "H_COL_ANG_MIN",      -20.0, 0.0,  0.5),
    ("th_max",  "H_COL_ANG_MAX",         5.0, 20.0, 0.5),
    ("th_zero", "H_COL_ZERO_THRST",    -5.0, 0.0,  0.1),
    ("th_land", "H_COL_LAND_MIN",      -5.0, 0.0,  0.1),
    ("col_min", "H_COL_MIN",          1000.0, 2000.0, 10.0),
    ("col_max", "H_COL_MAX",          1000.0, 2000.0, 10.0),
    ("u_hover", "u_hover (hover mean motor u)", 0.05, 0.45, 0.01),
]


def calculate_scalars(p):
    """复现 AP_MotorsHeli_Quad::calculate_scalars (Quad cpp:67-98)."""
    warnings = []
    col_min, col_max = p["col_min"], p["col_max"]
    if col_min >= col_max:  # cpp:70-73 静默重置
        col_min, col_max = 1250.0, 1750.0
        warnings.append("COL_MIN>=COL_MAX: silently reset to 1250/1750 (cpp:70-73)")
    th_min, th_max = p["th_min"], p["th_max"]
    th_zero = np.clip(p["th_zero"], th_min, th_max)   # cpp:75
    th_land = np.clip(p["th_land"], th_min, th_max)   # cpp:77
    if not np.isclose(th_max, th_min):                # cpp:79-88
        z = (th_zero - th_min) / (th_max - th_min)
        l = (th_land - th_min) / (th_max - th_min)
    else:
        z = l = 0.0
    r_c = (col_max - col_min) * 0.001                 # cpp:186
    if r_c >= 0.999:
        warnings.append("R_c=1: zero clamp headroom for attitude at delta=1")
    return z, l, r_c, warnings


def u_mean(delta, z, r_c):
    """move_actuators 的平均通道(无姿态/偏航项), Quad cpp:192-236."""
    return 2.0 * (r_c * (delta - z) + z) - 1.0


def blade_pitch(delta, p, z):
    """桨距角模型: 标定意图的三点折线 (0,Thmin)-(z,Thzero)-(1,Thmax)."""
    return np.interp(delta, [0.0, z, 1.0],
                     [p["th_min"], np.clip(p["th_zero"], p["th_min"], p["th_max"]), p["th_max"]])


def pwm_from_angle(u):
    """SRV_Channel::pwm_from_angle (SRV_Channel.cpp:199-213), 过 TRIM 分段线性."""
    a = np.clip(u, -1.0, 1.0) * ANGLE_MAX
    return np.where(a >= 0,
                    SERVO_TRIM + a / ANGLE_MAX * (SERVO_MAX - SERVO_TRIM),
                    SERVO_TRIM + a / ANGLE_MAX * (SERVO_TRIM - SERVO_MIN))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", metavar="PNG", help="无头渲染到文件(不弹窗)")
    args = ap.parse_args()
    if args.save:
        matplotlib.use("Agg")

    plt.rcParams["axes.unicode_minus"] = False

    fig = plt.figure(figsize=(11, 7))
    fig.suptitle("heliquad collective conversion chain:  "
                 r"$u=2[R_c(\delta-z)+z]-1$,  $R_c=\frac{COL\_MAX-COL\_MIN}{1000}$,  "
                 r"$z=\frac{\Theta_{zero}-\Theta_{min}}{\Theta_{max}-\Theta_{min}}$",
                 fontsize=11, y=0.995)

    ax1 = fig.add_axes([0.09, 0.78, 0.85, 0.14])   # blade pitch
    ax2 = fig.add_axes([0.09, 0.60, 0.85, 0.14])   # mixer u
    ax3 = fig.add_axes([0.09, 0.42, 0.85, 0.14])   # servo pwm
    for ax in (ax1, ax2, ax3):
        ax.set_xlim(0, 1)
        ax.grid(True, alpha=0.3)
    ax1.set_ylabel("Blade pitch (deg)")
    ax2.set_ylabel("Mixer output u")
    ax3.set_ylabel("Servo PWM (us)")
    ax3.set_xlabel("Collective command delta (= CTUN.ThI, 0-1)")
    ax2.annotate("gray dashed = R_c=0.5 (defaults) reference", xy=(0.02, 0.04),
                 xycoords="axes fraction", fontsize=8, color="gray")
    ax2.set_yticks([-1, -0.5, 0, 0.5, 1])
    ax3.set_yticks([1000, 1250, 1500, 1750, 2000])

    info = fig.text(0.09, 0.955, "", fontsize=9, va="top")

    # 滑条
    sliders, s_objs = {}, []
    bar_h, gap, group_gap = 0.020, 0.006, 0.014
    groups = {0: "Blade pitch angles (deg)", 4: "Collective range (us)", 6: "Hover"}
    y = 0.31
    for i, (key, label, lo, hi, step) in enumerate(SLIDERS):
        if i in groups:
            y -= group_gap
            fig.text(0.30, y + bar_h + 0.004, groups[i], fontsize=8, color="gray", ha="left")
        ax_s = fig.add_axes([0.30, y, 0.50, bar_h])
        s = Slider(ax_s, label, lo, hi, valinit=P0[key], valstep=step)
        sliders[key] = s
        s_objs.append(s)
        s.on_changed(lambda _k=key: redraw())
        y -= bar_h + gap

    delta = np.linspace(0.0, 1.0, 401)
    lines = {
        "th": ax1.plot([], [], lw=2, color="tab:blue", label="Blade pitch model")[0],
        "u": ax2.plot([], [], lw=2, color="tab:green", label="u(δ)")[0],
        "pwm": ax3.plot([], [], lw=2, color="tab:red", label="PWM(δ)")[0],
        "u_ref": ax2.plot([], [], color="gray", ls="--", lw=1)[0],
        "pwm_ref": ax3.plot([], [], color="gray", ls="--", lw=1)[0],
        "th_span": ax1.fill_between([], [], [], color="tab:blue", alpha=0.08),
        "pwm_span": ax3.fill_between([], [], [], color="tab:red", alpha=0.08),
    }
    marks = {
        "vz1": ax1.axvline(np.nan, color="k", ls="--", lw=1),
        "vz2": ax2.axvline(np.nan, color="k", ls="--", lw=1),
        "vz3": ax3.axvline(np.nan, color="k", ls="--", lw=1),
        "vl1": ax1.axvline(np.nan, color="tab:orange", ls=":", lw=1.2),
        "vh1": ax1.axvline(np.nan, color="tab:purple", ls="-.", lw=1.2),
        "vh2": ax2.axvline(np.nan, color="tab:purple", ls="-.", lw=1.2),
        "vh3": ax3.axvline(np.nan, color="tab:purple", ls="-.", lw=1.2),
        "hzero": ax1.axhline(0.0, color="gray", lw=0.8),
        "htrim": ax3.axhline(SERVO_TRIM, color="gray", lw=0.8),
        "pt": ax1.plot([], [], "ko", ms=4)[0],
    }
    ax1.legend(handles=[lines["th"], marks["vz1"], marks["vl1"], marks["vh1"]],
               labels=["Blade pitch", "Zero thrust d=z", "Land min d=l", "Hover d_h"],
               fontsize=8, loc="upper left")

    def redraw():
        p = {k: s.val for k, s in sliders.items()}
        z, l, r_c, warns = calculate_scalars(p)
        u = u_mean(delta, z, r_c)
        th = blade_pitch(delta, p, z)
        pwm = pwm_from_angle(u)

        u_hover = sliders["u_hover"].val
        dh = z + u_hover / (2.0 * r_c) if r_c > 0 else np.nan

        lines["th"].set_data(delta, th)
        lines["u"].set_data(delta, u)
        lines["pwm"].set_data(delta, pwm)
        u_ref = u_mean(delta, z, 0.5)          # stingray default R_c=0.5 reference
        lines["u_ref"].set_data(delta, u_ref)
        lines["pwm_ref"].set_data(delta, pwm_from_angle(u_ref))
        lines["th_span"].remove()
        lines["pwm_span"].remove()
        lines["th_span"] = ax1.fill_between(delta, p["th_min"], th, color="tab:blue", alpha=0.08)
        lines["pwm_span"] = ax3.fill_between(delta, SERVO_MIN, pwm, color="tab:red", alpha=0.08)
        for m in ("vz1", "vz2", "vz3"):
            marks[m].set_xdata([z, z])
        marks["vl1"].set_xdata([l, l])
        for m in ("vh1", "vh2", "vh3"):
            marks[m].set_xdata([dh, dh])
        marks["pt"].set_data([0, z, 1], [p["th_min"], p["th_zero"], p["th_max"]])

        reach = "" if dh <= 1 else "  WARN d_h>1: hover unreachable!"
        info.set_text(
            f"z={z:.3f}  l={l:.3f}  R_c={r_c:.3f}  collective span={r_c*100:.0f}% of full (width 2R_c={2*r_c:.2f})  "
            f"δ_hover={dh:.3f}{reach}\n"
            f"pitch range [{p['th_min']:.1f}, {p['th_max']:.1f}] deg  "
            f"zero thrust at {z*100:.0f}% of command  "
            f"full-collective PWM={pwm_from_angle(np.array([u_mean(1.0, z, r_c)]))[0]:.0f}us (not 2000 => R_c<1)"
            + ("\n" + "  ".join(warns) if warns else ""))

        fig.canvas.draw_idle()

    redraw()

    if args.save:
        fig.savefig(args.save, dpi=130)
        print(f"saved: {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
