#!/usr/bin/env python3
"""heliquad Stabilize 总距输入链交互图: RCIN.C3 -> IM_STB_COL 曲线 -> CTUN.ThI -> 混控平均通道 -> RCOU.

可视化 IM_STB_COL_1..4 三段总距成形曲线 (AC_InputManager_Heli.cpp:62-132,
拐点 control_in = 0/400/600/1000 即三段折线的四个端点值) 及其上下游全部可调环节:
  RC3_MIN/MAX/DZ 标定     RC_Channel::pwm_to_range_dz (RC_Channel.cpp:388-400)
  -> delta (= CTUN.ThI)   Stabilize 用 stab 分支: use_stab_col=true
                          (ModeStabilize_Heli::init, mode_stabilize_heli.cpp:15;
                           上电由 heli.cpp:17-19 预置; Acro 走 IM_ACRO_COL_EXP expo, 图中虚线对照)
  -> u 平均通道           move_actuators (AP_MotorsHeli_Quad.cpp:161-236, 无姿态/偏航项;
                          z / l / R_c 来自 H_COL_ANG_* 与 H_COL_MIN/MAX)
  -> PWM                  pwm_from_angle (SRV_Channel.cpp:199-213, 过 SERVOx_TRIM 分段)
参数前缀 IM_ = AC_InputManager_Heli 组 (Parameters.cpp:357); P0 默认值取自 mav.parm 实机 dump.
模式切换 0.5s 总距 ramp (AC_InputManager_Heli.cpp:111-116) 是时域行为, 图中不含.

用法:
    python3 heliquad_stbcol_chain_plot.py            # 交互窗口(拖滑条)
    python3 heliquad_stbcol_chain_plot.py --save out.png   # 无头渲染
"""
import argparse

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# P0 默认值 = mav.parm 实机值; IM_STB_COL_1..4 同时也是固件默认 (0/40/60/100)
P0 = dict(rc3_min=1000.0, rc3_max=2000.0, rc3_dz=10.0, stick=1600.0,
          stb1=0.0, stb2=40.0, stb3=60.0, stb4=100.0, acro_exp=0.0,
          th_min=-10.0, th_zero=0.0, th_land=-2.0, th_max=10.0,
          col_min=1250.0, col_max=1750.0,
          servo_min=1000.0, servo_trim=1500.0, servo_max=2000.0,
          col_hover=0.609)

SLIDERS = [  # (key, label, lo, hi, step) -- 分组: RC3 标定 / IM_STB_COL / 桨距角 / 总距范围 / SERVO / 悬停
    ("rc3_min", "RC3_MIN",       800.0, 1400.0, 5.0),
    ("rc3_max", "RC3_MAX",      1600.0, 2200.0, 5.0),
    ("rc3_dz",  "RC3_DZ",          0.0,  100.0, 1.0),
    ("stick",   "C3 stick (us)", 1000.0, 2000.0, 1.0),
    ("stb1", "IM_STB_COL_1 (@1000us)", 0.0, 100.0, 1.0),
    ("stb2", "IM_STB_COL_2 (@1400us)", 0.0, 100.0, 1.0),
    ("stb3", "IM_STB_COL_3 (@1600us)", 0.0, 100.0, 1.0),
    ("stb4", "IM_STB_COL_4 (@2000us)", 0.0, 100.0, 1.0),
    ("acro_exp", "IM_ACRO_COL_EXP (Acro ref)", 0.0, 1.0, 0.05),
    ("th_min",  "H_COL_ANG_MIN",     -20.0, 0.0, 0.5),
    ("th_max",  "H_COL_ANG_MAX",       5.0, 20.0, 0.5),
    ("th_zero", "H_COL_ZERO_THRST",   -5.0, 0.0, 0.1),
    ("th_land", "H_COL_LAND_MIN",     -5.0, 0.0, 0.1),
    ("col_min", "H_COL_MIN",        1000.0, 2000.0, 10.0),
    ("col_max", "H_COL_MAX",        1000.0, 2000.0, 10.0),
    ("servo_min",  "SERVOx_MIN",  800.0, 1500.0, 5.0),
    ("servo_trim", "SERVOx_TRIM", 800.0, 2200.0, 5.0),
    ("servo_max",  "SERVOx_MAX", 1500.0, 2200.0, 5.0),
    ("col_hover", "H_COL_HOVER (CTUN.ThI @ hover)", 0.0, 1.0, 0.005),
]

GROUPS = {0: "RC3 calibration (us)", 4: "IM_STB_COL curve (%, knots at control_in 0/400/600/1000)",
          9: "H_COL_ANG_* blade pitch (deg)", 13: "H_COL_MIN/MAX collective range (us)",
          15: "SERVOx_MIN/TRIM/MAX (us)", 18: "hover"}


def rc_to_control_in(rc, p):
    """RC_Channel::pwm_to_range_dz (RC_Channel.cpp:388-400), high_in=1000, 无 reverse."""
    lo, hi, dz = p["rc3_min"], p["rc3_max"], p["rc3_dz"]
    denom = hi - lo - dz
    r_in = np.clip(rc, lo, hi)
    low = lo + dz
    if denom <= 0.0:
        return np.zeros_like(r_in)
    return np.where(r_in > low, 1000.0 * (r_in - low) / denom, 0.0)


def stab_col(cin, p):
    """三段总距曲线, 拐点 control_in=0/400/600/1000 (AC_InputManager_Heli.cpp:70-89).

    分段线性且单调, 与 cpp 的三段斜率公式等价, np.interp 即逐点一致; 参数是百分比, cpp 里 *0.01f.
    """
    return np.clip(np.interp(cin, [0.0, 400.0, 600.0, 1000.0],
                             [p["stb1"], p["stb2"], p["stb3"], p["stb4"]]) * 0.01, 0.0, 1.0)


def acro_col(cin, p):
    """expo 路径 (AC_InputManager_Heli.cpp:92-108), Acro 模式对照 (use_stab_col=false)."""
    expo = min(p["acro_exp"], 1.0)
    if expo <= 0.0:
        return cin * 0.001
    x = (cin - 500.0) / 500.0
    return np.clip(0.5 + (expo * x**3 + (1.0 - expo) * x) * 0.5, 0.0, 1.0)


def calculate_scalars(p):
    """复现 AP_MotorsHeli_Quad::calculate_scalars (Quad cpp:67-98)."""
    warns = []
    col_min, col_max = p["col_min"], p["col_max"]
    if col_min >= col_max:  # cpp:70-73 静默重置
        col_min, col_max = 1250.0, 1750.0
        warns.append("COL_MIN>=COL_MAX: silently reset to 1250/1750 (cpp:70-73)")
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
        warns.append("R_c=1: no clamp headroom for attitude differential at delta=1")
    return z, l, r_c, warns


def u_mean(delta, z, r_c):
    """move_actuators 的平均通道(无姿态/偏航项), Quad cpp:192-236."""
    return 2.0 * (r_c * (delta - z) + z) - 1.0


def pwm_from_angle(u, p):
    """SRV_Channel::pwm_from_angle (SRV_Channel.cpp:199-213), 过 SERVOx_TRIM 分段线性.

    TRIM==MAX 时 u>=0 全段恒 TRIM (单边死区) -- 图中自动标红.
    """
    a = np.clip(u, -1.0, 1.0) * 4500.0
    return np.where(a >= 0,
                    p["servo_trim"] + a / 4500.0 * (p["servo_max"] - p["servo_trim"]),
                    p["servo_trim"] + a / 4500.0 * (p["servo_trim"] - p["servo_min"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", metavar="PNG", help="无头渲染到文件(不弹窗)")
    args = ap.parse_args()
    if args.save:
        matplotlib.use("Agg")

    plt.rcParams["axes.unicode_minus"] = False

    fig = plt.figure(figsize=(11, 12))
    fig.suptitle("heliquad Stabilize collective input chain:  "
                 "C3[us] →(RC3) control_in →(IM_STB_COL) δ=ThI →(move_actuators) "
                 r"$u=2[R_c(\delta-z)+z]-1$" + " →(pwm_from_angle) PWM",
                 fontsize=10, y=0.995)

    # 三个面板共享 x 轴 = RCIN.C3 (us), 一条杆位竖线贯穿全链
    ax1 = fig.add_axes([0.09, 0.80, 0.85, 0.125])   # ThI: IM_STB_COL 曲线
    ax2 = fig.add_axes([0.09, 0.635, 0.85, 0.125])  # 平均通道 u
    ax3 = fig.add_axes([0.09, 0.47, 0.85, 0.125])   # RCOU PWM
    for ax in (ax1, ax2, ax3):
        ax.set_xlim(1000, 2000)
        ax.grid(True, alpha=0.3)
    ax1.set_ylabel("CTUN.ThI (0-1)")
    ax1.set_ylim(-0.03, 1.06)
    ax2.set_ylabel("Mixer mean u")
    ax3.set_ylabel("RCOU mean PWM (us)")
    ax3.set_xlabel("RCIN.C3 (us)")
    ax2.set_yticks([-1, -0.5, 0, 0.5, 1])
    ax2.set_ylim(-1.05, 1.05)
    ax3.set_yticks([1000, 1250, 1500, 1750, 2000])

    info = fig.text(0.09, 0.955, "", fontsize=9, va="top")

    # 滑条
    sliders = {}
    bar_h, gap, group_gap = 0.0155, 0.0035, 0.011
    y = 0.415
    for i, (key, label, lo, hi, step) in enumerate(SLIDERS):
        if i in GROUPS:
            y -= group_gap
            fig.text(0.30, y + bar_h + 0.003, GROUPS[i], fontsize=8, color="gray", ha="left")
        ax_s = fig.add_axes([0.30, y, 0.50, bar_h])
        s = Slider(ax_s, label, lo, hi, valinit=P0[key], valstep=step)
        sliders[key] = s
        s.on_changed(lambda _k=key: redraw())
        y -= bar_h + gap

    rc = np.linspace(1000.0, 2000.0, 2001)

    def redraw():
        p = {k: s.val for k, s in sliders.items()}
        cin = rc_to_control_in(rc, p)
        delta = stab_col(cin, p)
        acro = acro_col(cin, p)
        z, l, r_c, warns = calculate_scalars(p)
        u = u_mean(delta, z, r_c)
        pwm = pwm_from_angle(u, p)
        # RCOU 面板纵轴: 贴合数据, 下沿不悬空 (自动定界会圆整到 0 导致 1000 刻度悬在中间)
        ax3.set_ylim(min(p["servo_min"], float(pwm.min())) - 50.0,
                     max(p["servo_max"], float(pwm.max())) + 50.0)

        # 杆位当前值
        cin_s = float(rc_to_control_in(np.array([p["stick"]]), p)[0])
        thI_s = float(stab_col(np.array([cin_s]), p)[0])
        u_s = float(u_mean(np.array([thI_s]), z, r_c)[0])
        pwm_s = float(pwm_from_angle(np.array([u_s]), p)[0])

        # 反解: ThI 目标值 -> 杆位 us (曲线单调, np.interp 反查)
        def rc_of_thi(t):
            return float(np.interp(t, delta, rc))

        rc_z = rc_of_thi(z)        # 零桨距杆位 (u_mean=0)
        rc_l = rc_of_thi(l)        # land min
        rc_h = rc_of_thi(p["col_hover"])   # 悬停杆位

        # 拐点位置随 RC3 标定移动 (control_in 400/600 -> us)
        rc_k400 = float(np.interp(400.0, cin, rc))
        rc_k600 = float(np.interp(600.0, cin, rc))

        # 曲线与两端点直线的偏离 (默认 0/40/60/100 时为 0 -> 拐点无效)
        lin = (p["stb1"] + (cin / 1000.0) * (p["stb4"] - p["stb1"])) * 0.01
        bend = float(np.max(np.abs(delta - lin)))

        lines["th"].set_data(rc, delta)
        lines["acro"].set_data(rc, acro)
        lines["u"].set_data(rc, u)
        lines["pwm"].set_data(rc, pwm)
        marks["pt1"].set_data([p["stick"]], [thI_s])
        marks["pt3"].set_data([p["stick"]], [pwm_s])
        for m in ("vs1", "vs2", "vs3"):
            marks[m].set_xdata([p["stick"], p["stick"]])
        for m in ("vz2", "vz3"):
            marks[m].set_xdata([rc_z, rc_z])
        marks["vl2"].set_xdata([rc_l, rc_l])
        for m in ("vh2", "vh3"):
            marks[m].set_xdata([rc_h, rc_h])
        for m, xk in (("k1", rc_k400), ("k2", rc_k600)):
            marks[m].set_xdata([xk, xk])

        # 单边死区: TRIM 撞 MIN/MAX (pwm_from_angle 两侧公式独立, SRV_Channel.cpp:208-212)
        if abs(p["servo_trim"] - p["servo_max"]) <= 1.0:
            warns.append("SERVOx_TRIM==MAX: u>=0 pinned at TRIM (channel sticks at 1500 once past zero-thrust stick!)")
        if abs(p["servo_trim"] - p["servo_min"]) <= 1.0:
            warns.append("SERVOx_TRIM==MIN: u<=0 pinned at TRIM (channel sticks at 1500 below zero-thrust stick!)")
        if p["rc3_max"] - p["rc3_min"] - p["rc3_dz"] <= 0:
            warns.append("RC3 range<=DZ: control_in stuck at 0, curve inactive")

        info.set_text(
            f"C3={p['stick']:.0f}us  ->  control_in={cin_s:.0f}  ->  ThI={thI_s:.3f}  ->  "
            f"u_mean={u_s:+.3f}  ->  PWM_mean={pwm_s:.0f}us\n"
            f"z={z:.3f}  l={l:.3f}  R_c={r_c:.3f}  |  zero-thrust stick C3={rc_z:.0f}us  "
            f"hover(COL_HOVER={p['col_hover']:.3f}) stick C3={rc_h:.0f}us  |  "
            f"knots at {rc_k400:.0f} / {rc_k600:.0f}us"
            + (f"  |  curve bend max|d-lin|={bend*100:.1f}%" if bend >= 0.001 else "  |  curve is a pure line (defaults 0/40/60/100, knots inactive)")
            + ("\n" + "  ".join(warns) if warns else ""))

        fig.canvas.draw_idle()

    lines = {
        "th": ax1.plot([], [], lw=2, color="tab:blue", label="IM_STB_COL (Stabilize = CTUN.ThI)")[0],
        "acro": ax1.plot([], [], lw=1.2, color="gray", ls="--", label="IM_ACRO_COL_EXP (Acro ref)")[0],
        "u": ax2.plot([], [], lw=2, color="tab:green")[0],
        "pwm": ax3.plot([], [], lw=2, color="tab:red")[0],
    }
    marks = {
        "vs1": ax1.axvline(np.nan, color="k", lw=1.2),
        "vs2": ax2.axvline(np.nan, color="k", lw=1.2),
        "vs3": ax3.axvline(np.nan, color="k", lw=1.2),
        "vz2": ax2.axvline(np.nan, color="k", ls="--", lw=1),
        "vz3": ax3.axvline(np.nan, color="k", ls="--", lw=1),
        "vl2": ax2.axvline(np.nan, color="tab:orange", ls=":", lw=1.2),
        "vh2": ax2.axvline(np.nan, color="tab:purple", ls="-.", lw=1.2),
        "vh3": ax3.axvline(np.nan, color="tab:purple", ls="-.", lw=1.2),
        "k1": ax1.axvline(np.nan, color="tab:cyan", lw=0.8, alpha=0.6),
        "k2": ax1.axvline(np.nan, color="tab:cyan", lw=0.8, alpha=0.6),
        "pt1": ax1.plot([], [], "ko", ms=5)[0],
        "pt3": ax3.plot([], [], "ko", ms=5)[0],
    }
    ax3.axhline(1500.0, color="gray", lw=0.8)
    ax3.text(1002, 1508, "TRIM=1500 (zero thrust / mean-channel zero)", fontsize=7, color="gray")
    ax1.legend(handles=[lines["th"], lines["acro"], marks["k1"]],
               labels=["IM_STB_COL (Stabilize)", "IM_ACRO_COL_EXP (Acro)", "knots 1400/1600us (move with RC3 cal)"],
               fontsize=8, loc="lower right")
    ax2.annotate("u=0 (zero thrust, black dashed): yaw crossover clamp pins one motor at 1500 most easily near here",
                 xy=(0.02, 0.06), xycoords="axes fraction", fontsize=7.5, color="gray")

    redraw()

    if args.save:
        fig.savefig(args.save, dpi=130)
        print(f"saved: {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
